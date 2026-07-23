# NETWORK_PROTOCOL.md — Wire Protocol: Transport, Envelope & Packet Catalog

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 10_systems/PERSISTENCE.md,
30_engineering/ENGINEERING_STANDARDS.md, docs/ID_REGISTRY.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/GAMEPLAY_SIMULATION.md,
70_integrations/ACCOUNTS_AUTH.md, 70_integrations/WORLD_CHANNELS.md,
70_integrations/CHAT_SOCIAL_BACKEND.md, 70_integrations/DATABASE_PERSISTENCE.md,
70_integrations/BUILD_DISTRIBUTION.md, docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

The **wire contract** between the Godot 4.3+ client and the Phoenix gateway
(`70_integrations/BACKEND_ARCHITECTURE.md` §1). `70_integrations/BACKEND_ARCHITECTURE.md` §9 delegates
**everything on the wire** here: transport, serialization, the message envelope, opcodes, versioning,
compression, keep-alive, and the packet catalog. This doc owns only the *bytes and their framing*. It
does **not** own — and never restates — the cadence and validation behind each packet
(`70_integrations/GAMEPLAY_SIMULATION.md` owns tick/snapshot/reconciliation numbers and the
per-domain server validation), the components that run the protocol
(`70_integrations/BACKEND_ARCHITECTURE.md`), the account/session lifecycle it carries
(`70_integrations/ACCOUNTS_AUTH.md`), channel selection and map-transition sequencing
(`70_integrations/WORLD_CHANNELS.md`), or the transaction boundaries a mutating packet commits to
(`70_integrations/DATABASE_PERSISTENCE.md`). Opcode **ranges** are `docs/ID_REGISTRY.md`'s; this doc
**mints** the individual opcodes inside them (§9).

**Decision posture.** Transport (§1), serialization (§2), envelope layout (§3), versioning (§4),
compression (§5), and keep-alive/timeout (§6) are engineering calls **made here** from best practice
for this genre — a 2D side-scrolling MMORPG, Godot 4.3+ client, Phoenix gateway,
hundreds-to-low-thousands concurrent — each with a one-paragraph rationale and named rejected
alternatives, per `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`'s decision authority. Nothing on
the wire is deferred to the owner; only vendor/hosting price tags live in
`70_integrations/BACKEND_ARCHITECTURE.md`'s Open Questions.

**Implemented when:** a live authoritative server / gateway exists
(`70_integrations/BACKEND_ARCHITECTURE.md` §6/§10). Until then there is no wire — the interim solo
build runs the same request→validate→delta shape (§7) in-process through the `GameState` facade
(`10_systems/PERSISTENCE.md` §5); the facade's backing store swaps to a gateway client speaking this
protocol at migration (`70_integrations/BACKEND_ARCHITECTURE.md` §6), and calling code does not change.

---

## 1. Transport — WebSocket over TLS (WSS), one long-lived connection

**Chosen: a single persistent WebSocket over TLS (WSS) per in-world session**, terminated at the
Phoenix gateway. Phoenix's socket tier is natively WebSocket, so WSS is exactly what the gateway
(`70_integrations/BACKEND_ARCHITECTURE.md` §1) is built to terminate; Godot 4.3 ships a first-class
`WebSocketPeer` with TLS in the client; and WSS gives framed, ordered, reliable, message-oriented
delivery over standard port 443, traversing the NATs, proxies, and firewalls a raw custom port would
snag on. One connection carries every domain (§9); routing to the correct world/channel/instance
process happens **behind** the gateway (`70_integrations/BACKEND_ARCHITECTURE.md` §1 "World routing"),
so the client never addresses a world process directly. TLS is mandatory and fail-closed (§10) — there
is no plaintext fallback.

Rejected alternatives:
- **Raw TCP + custom framing/TLS.** Throws away Phoenix's built-in socket/presence/channel machinery,
  forces a hand-rolled framing and handshake, and traverses hostile networks worse than WSS-on-443 —
  with no throughput upside at this genre's traffic.
- **QUIC / WebTransport.** Genuinely attractive (multiplexed streams, 0-RTT reconnect) but Godot 4.3's
  client has no first-class WebTransport support and Phoenix's WebTransport story is immature;
  head-of-line blocking on this game's single thin message stream is a non-issue at
  hundreds-to-low-thousands concurrent, so QUIC's main win buys nothing here yet. Kept in reserve for a
  later transport revision behind the `protocol_version` handshake (§4).
- **Raw UDP + a custom reliability/ordering layer.** The FPS/fighting-game choice. This genre's combat
  resolves as server-side **events** on the hit-frame signal, not position lockstep
  (`70_integrations/GAMEPLAY_SIMULATION.md` §1.2), and movement is reconciled forward with an
  accept-if-plausible envelope (`70_integrations/GAMEPLAY_SIMULATION.md` §2), so per-packet UDP
  reliability would reinvent TCP for latency wins the design never spends. WSS's reliable-ordered
  delivery is a fit, not a liability.

**Reliability consequence carried into the envelope (§3/§8):** because WSS is reliable and ordered
per connection, a dropped 10 Hz snapshot is *delayed*, not lost, and the client interpolates across the
gap (`70_integrations/GAMEPLAY_SIMULATION.md` §1.1); the protocol therefore implements **no**
retransmission of its own — `seq`/`ack` (§3) exist for correlation and idempotency, not reliability.

---

## 2. Serialization — MessagePack (binary), schema-light

**Chosen: MessagePack for every payload**, one codec both directions. It is compact binary (roughly
half of JSON on typical payloads) yet schemaless-tagged, so there is no `.proto`/codegen build step;
decisively, its type model maps 1:1 onto Godot's native `Dictionary`/`Array`/int/float/string, keeping
the GDScript-side codec cost low at 20 Hz client reports plus 10 Hz snapshots
(`70_integrations/GAMEPLAY_SIMULATION.md` §1.1), and Elixir has mature MessagePack libraries on the
gateway. Field naming in payloads uses `00_vision/GLOSSARY.md` tokens verbatim (`life`, `essence`,
`shards`, `enhance_level`, `rarity`, `exp`, `level`, …) so the wire never re-spells a canonical token.

Rejected alternatives:
- **JSON.** Trivially supported both sides and human-readable, but 2–3× the bytes and expensive
  GDScript string parsing at the snapshot/report cadence. Retained only as an **optional debug encoding**
  negotiable at the handshake (§4) for non-production builds.
- **Protobuf.** Best wire efficiency and a typed schema, but needs a compiled schema/codegen step and
  Godot 4.3 has no first-class GDScript protobuf runtime (third-party addons are heavy and slow); its
  schema-evolution rigidity buys little once the envelope already versions the contract (§4).
- **Custom hand-packed binary.** Smallest possible, but every field offset becomes hand-maintained on
  both client and server and brittle as the catalog (§9) grows; MessagePack captures ~90 % of the size
  win with self-describing safety.
- **CBOR.** Technically near-equivalent to MessagePack; rejected only for weaker turnkey GDScript
  tooling and familiarity, not on merit.

MessagePack **extension types** for hot compound values (e.g. a position/velocity vector pair) are a
coding-pass detail (Open Questions), not fixed here.

---

## 3. Message envelope — exact field layout

Every message on the wire is a single MessagePack **array** with a fixed positional header followed by
the opcode-specific body. Positional (array) rather than a named map for the header keeps the
per-message overhead to ~10–14 bytes:

```
[ op, seq, ack, t, flags, payload ]
```

| Field | Type | Meaning |
|---|---|---|
| `op` | uint16 | The opcode from the `op_NNNN` family (`docs/ID_REGISTRY.md`); the **sole switch key** for dispatch. One opcode = one message type = one direction (§9). |
| `seq` | uint32 (wrapping) | The sender's monotonic per-connection sequence number. Client and server each maintain their own outbound `seq`. Used for ordering diagnostics, `ack` correlation, and **request idempotency** (§8) — a request keeps its `seq` when replayed after a reconnect. |
| `ack` | uint32 | The highest contiguous peer `seq` the sender has processed. Piggybacked so either side detects loss/lag over the reliable transport, and so the server can tie a reconciliation correction back to the exact client input `seq` it was computed against (`70_integrations/GAMEPLAY_SIMULATION.md` §2). |
| `t` | uint32 | The sender's monotonic clock in ms (low 32 bits), sampled at send. Carries client input time (reconciliation) and the server snapshot stamp (interpolation). The envelope only **carries** the stamp — the 20 Hz report / 10 Hz snapshot / 50 ms tick cadences are `70_integrations/GAMEPLAY_SIMULATION.md` §1's, not re-decided here. |
| `flags` | uint8 bitfield | `bit0 COMPRESSED` — payload is compressed (§5). `bit1 RESUMED` — set on the first packet after a reconnect resume (§6). `bit2`–`bit7` reserved-zero (fragment/continuation and future non-WSS-transport reliability markers). |
| `payload` | MessagePack map | The opcode-specific body: named fields per the §9 catalog row. An empty map for bodyless control packets (e.g. heartbeat). |

The header fields are the same in both directions; only `payload` shape and the legal set of `op`
values differ by direction. The envelope is transport-agnostic above WSS — if a future transport
revision (§1) lands, only `flags`' reserved reliability bits change meaning, not the header shape.

---

## 4. Versioning — `protocol_version` negotiated at handshake

The wire introduces a **fourth** version number beyond `70_integrations/BUILD_DISTRIBUTION.md` §2's
three: **`protocol_version`** (monotonic integer) — the version of *this contract*: the §3 envelope
layout plus the §9 opcode-catalog semantics. It is owned here and changes only on a
non-back-compatible wire change, a slower axis than either `client_version` or `content_version`.

**Handshake (first exchange after the socket opens, before session auth completes).** The client's
first `c2s` packet (§9.2) carries `protocol_version`, `client_version`, and `content_version`
(`70_integrations/BUILD_DISTRIBUTION.md` §2). The gateway replies **accept** (agreeing a
`protocol_version` from the window it supports) or **reject** with the minimum required. Only after a
protocol accept does the session-auth exchange (`70_integrations/ACCOUNTS_AUTH.md` §3/§4, carried by
§9.2 packets) proceed.

- **`protocol_version` vs `client_version`** — kept separate for exactly
  `70_integrations/BUILD_DISTRIBUTION.md` §2's reason (the numbers change at different rates): an old
  client that still speaks the current `protocol_version` should connect after a content-only patch
  without a wire bump. Baking the wire version into `client_version` (a bump on every executable
  release) is **rejected** on that ground.
- **`client_version`** is carried so the server's deprecated-client gate
  (`70_integrations/BUILD_DISTRIBUTION.md` §3 "server-driven version gate") can refuse an outdated build
  and force a storefront update; that refusal is a §9.2 reject with an "update required" reason.
- **`content_version`** is carried for diagnostics and content-mismatch detection, but per
  `70_integrations/BUILD_DISTRIBUTION.md` §2 it does **not** itself gate the wire — a referenced-ID
  mismatch is a content/migration concern, not a protocol one.

**Posture (decided):** the gateway supports a small window of recent `protocol_version`s; below the
floor is a **hard reject** routed to the storefront update gate above. This is set here, not owner-deferred.

---

## 5. Compression — per-message DEFLATE, threshold-gated

**Chosen: per-message compression with DEFLATE (zlib), applied only above a size threshold
(~512 bytes), signaled by the envelope `flags` `COMPRESSED` bit (§3).** WSS can negotiate the standard
`permessage-deflate` extension both Phoenix and Godot's `WebSocketPeer` support; but blanket
compression wastes CPU and can *grow* the many tiny control/movement packets, so the protocol compresses
only messages over the threshold — the crowded-channel 10 Hz snapshot
(`70_integrations/GAMEPLAY_SIMULATION.md` §1.1) and bulk transfers (character load, inventory/bank dump,
market-listing pages) benefit, small packets skip it. DEFLATE because Godot has native zlib
(`Compression`) and Elixir has `:zlib` — universally available, cheap, good ratio on structured data.
Per-message opt-in keeps the decoder simple: check one flag bit, inflate or not.

Rejected alternatives:
- **Stream-level compression** (compress the whole socket with a shared dictionary) — a better ratio,
  but couples every message's decode to accumulated stream state, defeats the per-message threshold, and
  complicates the fragment story; not worth it at this scale.
- **Brotli / zstd** — better ratios, but weaker turnkey availability in Godot 4.3 GDScript; zlib is the
  safe universal choice, revisitable behind the `protocol_version` handshake (§4).
- **No compression** — fine for tiny packets, wasteful for the snapshot and bulk cases.

Threshold (~512 bytes) and DEFLATE level are **ops-tunable** values with a **fixed shape**
(compress-above-threshold, per-message flag, DEFLATE); the shape is law here, the exact numbers are
operational.

---

## 6. Keep-alive & timeout — 15 s heartbeat, 30 s socket-dead, inside the 90 s session grace

Two distinct clocks, and the design keeps them ordered so a reconnect always has time to fire:

- **Heartbeat — 15 s.** A `c2s` ping (§9.1) with a `s2c` pong; either side may also use WebSocket
  native ping/pong control frames, with the application heartbeat as the session-liveness signal Phoenix
  models. Negligible bandwidth.
- **Socket-dead detection — 30 s.** The gateway treats a connection with no traffic for 30 s (two
  missed heartbeats plus margin) as dead and tears down the **transport**.
- **Session grace — 90 s (owned by `70_integrations/ACCOUNTS_AUTH.md` §4.3, not re-decided here).** A
  torn-down transport does **not** end the in-world session: the character stays live and bound for the
  90 s reconnect-grace window, during which the client re-opens the socket and re-runs the §4 handshake
  with the `70_integrations/ACCOUNTS_AUTH.md` §3.4 signed **resume ticket** instead of a full login
  (§9.1/§9.2), and the gateway rebinds it to the same character (`RESUMED` flag, §3). If the grace has
  expired, the resume is rejected and a full login (`70_integrations/ACCOUNTS_AUTH.md` §3) is required.

Rationale: 15 s heartbeat detects a drop within ~30 s — comfortably inside the 90 s grace, so a
transient blip never costs the session — at trivial cost; the socket-liveness clock (30 s) and the
session clock (90 s) are deliberately different, and the invariant is **socket-dead < session-grace** so
the reconnect path (§9.1/§9.2) always has runway. Rejected: a **60 s heartbeat** (a drop could burn most
of the 90 s grace before detection); **OS-level TCP keepalive only** (minutes-long defaults, useless
against a 90 s window); **no heartbeat / detect-on-next-send** (an idle client in a quiet town looks
dead, and a dead socket looks alive until the next action).

---

## 7. The acquisition rule — normative envelope-level contract (binds the whole catalog)

**This is the law every packet in §9 must satisfy, stated once here so no catalog row restates it.**

Every `c2s` packet is a **REQUEST — a statement of intent** ("I cast X", "I attacked Y", "I picked up
Z", "I bought W", "I attempted +7", "I allocated a point"), **never a statement of outcome**. The server
validates each request against its owning `70_integrations/GAMEPLAY_SIMULATION.md` domain section
(§5–§13 there) and the `10_systems/PERSISTENCE.md` §7 never-trust list, then returns every server-owned
result as an authoritative `s2c` **delta/event**. The uniform acquisition rule and its per-item
request→validate→delta mapping are `70_integrations/GAMEPLAY_SIMULATION.md` §14's and
`10_systems/PERSISTENCE.md` §7's — cited, not restated here.

Consequences that constrain the §9 catalog (a Sonnet author must honor these when filling it):

1. **No outcome field may appear in a `c2s` payload.** A client packet never carries a gained item, a
   resulting `shards` amount, a rolled `rarity`/`qty`, a post-hit `life`/`essence` value, a
   client-recomputed derived stat, or an enhancement result. Those fields are **`s2c`-only**. A
   `server`-authority (`10_systems/PERSISTENCE.md` §1) field inside a `c2s` payload is a modeling error.
2. **`c2s` payloads carry intent fields only** — target ids, a skill id + chosen rank + aim, slot
   indices, an item id + *requested* qty, a shop sku, the target equip for an enhance attempt. Their
   annotation is `shared` (position/velocity, `10_systems/PERSISTENCE.md` §4) or **`intent`** —
   client-submitted request input the server always re-checks; never `server`-truth. `intent` is a
   **wire-role annotation of this catalog, not a `10_systems/PERSISTENCE.md` §1 authority tag**:
   that taxonomy's three tags classify *state* and are complete (§1's "no fourth tag" law stands —
   its `client` tag means never-synced local preference state, which by definition never appears on
   the wire, PERSISTENCE §3). A request field is not state; it is input to a validation, so it
   carries the catalog's own `intent` marker instead of borrowing a state tag it would contradict.
3. **`s2c` delta payloads carry the authoritative result**, tagged `server` or `shared`
   (`10_systems/PERSISTENCE.md` §1); the client's optimistic prediction reconciles to it
   (`70_integrations/GAMEPLAY_SIMULATION.md` §3 explains why prediction + authority coexist safely).
4. **Every state-mutating `c2s` opcode MUST name its validating `70_integrations/GAMEPLAY_SIMULATION.md`
   section** in its catalog row (the "Server validation" column, §9) — that is the bridge the kickoff
   requires between this wire doc and the simulation layer.
5. **Idempotency (§8) is mandatory for acquisition packets** — a buy/enhance/allocate replayed after a
   reconnect must not double-apply.

---

## 8. Sequencing, ordering & idempotency (wire-side guarantees)

Reliability and in-order delivery come from WSS (§1), so the protocol adds none of its own; `seq`/`ack`
(§3) serve three ends:

- **Reconciliation correlation.** The server stamps a movement correction with the client input `seq`
  it reconciled against (`70_integrations/GAMEPLAY_SIMULATION.md` §2 owns the cadence and the
  accept-if-plausible envelope; this doc only carries the numbers).
- **Idempotency.** A `c2s` request carries its `seq`; on a reconnect replay (§6) the server dedups by
  `(session, seq)` so a resend after a blip does not double-apply — the wire-side guarantee behind
  `70_integrations/GAMEPLAY_SIMULATION.md` §10's "no reroll" and §14's request→delta. This is what makes
  the §7 acquisition packets safe to retry.
- **Diagnostics.** Gaps between `seq` and the peer's `ack` surface loss/lag for telemetry
  (`70_integrations/TELEMETRY_ANALYTICS.md`).

Ordering is per-connection and total (one WSS stream); the server processes a session's requests in
arrival order, which is also the order the combat-event queue drains them in
(`70_integrations/GAMEPLAY_SIMULATION.md` §1.2 owns the drain).

---

## 9. Packet catalog — domain-ordered, filled

> **STAGE STATUS.** §9.0's structure, opcode sub-blocks, validating sections, and per-packet template
> were fixed in stage 1; the individual packet rows below were authored in **stage 2** against that
> fixed contract. Every row satisfies §7 (the acquisition rule) and cites its
> `70_integrations/GAMEPLAY_SIMULATION.md` (or domain-owning doc) validating section. Every opcode below
> is minted and **immutable** (`docs/ID_REGISTRY.md`); a retired packet's opcode is never reused. Gaps
> inside each block are explicitly reaffirmed **reserved** at the end of that domain's table — a future
> addition mints the next free slot in a new commit, never renumbers a row above it.

### 9.0 Per-packet template (fill one row per packet)

Each domain sub-section carries one table of this exact shape:

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_NNNN` | `snake_case_name` | `c2s` \| `s2c` | intent-only for `c2s`; authoritative for `s2c` (§7) | the validating §; `—` for transport/social-tier packets that no simulation section gates | the `op_NNNN`(s) the server returns, or `—` for fire-and-forget `s2c` |

Fill rules (from §7, restated as a checklist for the stage-2 author — these are constraints, not new rules):
- **Direction is fixed per opcode.** Lay `c2s` request opcodes low in the block, `s2c` delta/event
  opcodes high (`docs/ID_REGISTRY.md` within-block convention).
- **Authority tags** come from `10_systems/PERSISTENCE.md` §1 (`server`/`client`/`shared`) — never a new
  tag. No `server` field in a `c2s` payload (§7.1).
- **Every state-mutating `c2s` row names its validating section** in column 5 (§7.4). A pure query or a
  transport/social-tier packet may use `—` and cite its owner in a note instead.
- **Payload fields name `00_vision/GLOSSARY.md` tokens verbatim** where they carry stats/resources/
  currency (`life`, `essence`, `shards`, `enhance_level`, `rarity`, `exp`, `level`, primary-stat tokens).
- Add a short note under a row only for a genuinely non-obvious field or a multi-packet exchange; do not
  restate a rule the cited section owns.

### 9.1 System, keep-alive & transport control — `op_0001`–`op_0099`
Validating layer: transport-level (heartbeat, ack, error/disconnect reason, reconnect **resume** —
resume validity is `70_integrations/ACCOUNTS_AUTH.md` §4.3's; §6 here fixes the timing). Column 5 is
mostly `—` for this block.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0001` | `heartbeat_ping` | `c2s` | `client_time: uint32 — intent` | `—` (liveness signal, §6) | `op_0090` |
| `op_0002` | `resume_request` | `c2s` | `resume_ticket: bytes — intent` (bearer copy of the `70_integrations/ACCOUNTS_AUTH.md` §3.4 signed ticket), `last_ack_seq: uint32 — intent` | `—` (ticket signature + 90 s grace validity is `70_integrations/ACCOUNTS_AUTH.md` §4.3's; §6 here fixes the timing) | `op_0091` or `op_0092` |
| `op_0090` | `heartbeat_pong` | `s2c` | `server_time: uint32 — server` | `—` | `—` |
| `op_0091` | `resume_accept` | `s2c` | `character_id: string — server`, `map_id: string — server`, `channel_index: uint8 — server` | `—` (`70_integrations/ACCOUNTS_AUTH.md` §4.3; sets envelope `flags.RESUMED`, §3) | `—` |
| `op_0092` | `resume_reject` | `s2c` | `reason: enum{grace_expired, ticket_invalid} — server` | `—` (`70_integrations/ACCOUNTS_AUTH.md` §4.3) | client falls back to `op_0101` full login (§9.2) |
| `op_0093` | `disconnect_notify` | `s2c` | `reason: enum{idle_timeout, kicked_duplicate_login, malformed_threshold, server_shutdown} — server` | `—` (§6 socket-dead 30 s; `70_integrations/ACCOUNTS_AUTH.md` §4.4 kick-on-second-login) | `—` |

Note: `disconnect_notify` is the one generic transport-level disconnect event, reused by every domain
that needs to end a connection (e.g. auth's kick-on-second-login, §9.2) rather than each domain minting
its own duplicate shape.

`op_0003`–`op_0089` and `op_0094`–`op_0099` remain **unminted/reserved** in this block.

### 9.2 Auth, handshake & session — `op_0100`–`op_0199`
Validating layer: `70_integrations/ACCOUNTS_AUTH.md` §3 (login, token) and §4 (gateway bind,
character-select, resume); the §4 `protocol_version`/`client_version`/`content_version` negotiation is
this doc's. Not gated by a `70_integrations/GAMEPLAY_SIMULATION.md` section — cite ACCOUNTS_AUTH in
notes.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0100` | `client_hello` | `c2s` | `protocol_version: uint32 — intent`, `client_version: string — intent`, `content_version: string — intent` | `—` (§4 negotiation window; `70_integrations/BUILD_DISTRIBUTION.md` §2/§3 version gate) | `op_0190` |
| `op_0101` | `login_request` | `c2s` | `handle: string — intent`, `password: string — intent` (submitted over TLS, never persisted verbatim, `70_integrations/ACCOUNTS_AUTH.md` §3.2) | `—` (`70_integrations/ACCOUNTS_AUTH.md` §3.2–§3.5: rate-limit/lockout gate before hash compare, Argon2id verify, uniform failure message) | `op_0191` |
| `op_0102` | `character_select_request` | `c2s` | `slot_index: uint8 — intent` | `—` (`70_integrations/ACCOUNTS_AUTH.md` §4.1/§4.2 gateway bind) | `op_0192` |
| `op_0103` | `character_create_request` | `c2s` | `slot_index: uint8 — intent`, `name: string — intent` | `—` (`70_integrations/ACCOUNTS_AUTH.md` §5 name-policy gate: allowed set/length, reserved+profanity filter, global uniqueness) | `op_0193` |
| `op_0104` | `logout_request` | `c2s` | (empty map) | `—` (`70_integrations/ACCOUNTS_AUTH.md` §3.6 revocation — invalidates refresh-token family) | `op_0093` (§9.1) |
| `op_0190` | `server_hello` | `s2c` | `accepted: bool — server`, `agreed_protocol_version: uint32 — server`, `min_required_client_version: string — server`, `reject_reason: enum{version_too_old, none} — server` | `—` (§4) | `—` |
| `op_0191` | `login_result` | `s2c` | `success: bool — server`, `character_roster: array — server` (up to 3 slots, `70_integrations/ACCOUNTS_AUTH.md` §2.2), `fail_reason: enum{invalid_credentials, account_locked} — server` | `—` (`70_integrations/ACCOUNTS_AUTH.md` §3.3–§3.5) | `—` |
| `op_0192` | `character_select_result` | `s2c` | `character_id: string — server`, `level: uint16 — server`, `map_id: string — server`, `position: vec2 — shared`, `life: uint32 — server`, `essence: uint32 — server`, `shards: uint32 — server` (initial `GameState` pointer, `10_systems/PERSISTENCE.md` §1) | `—` (`70_integrations/ACCOUNTS_AUTH.md` §4.1/§4.2) | `—` |
| `op_0193` | `character_create_result` | `s2c` | `success: bool — server`, `character_id: string — server`, `fail_reason: enum{name_taken, invalid_name, slot_occupied} — server` | `—` (`70_integrations/ACCOUNTS_AUTH.md` §5) | `—` |

`op_0105`–`op_0189` and `op_0194`–`op_0199` remain **unminted/reserved** in this block.

### 9.3 Channel & instance management — `op_0200`–`op_0299`
Validating layer: `70_integrations/WORLD_CHANNELS.md` §3 (channel select/switch) and §6 (map-transition
handoff sequencing / what blocks); raid-instance allocation is `10_systems/SPAWN.md` §7 as scoped by
`70_integrations/GAMEPLAY_SIMULATION.md` §13.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0200` | `channel_switch_request` | `c2s` | `target_channel_index: uint8 — intent` | `—` (`70_integrations/WORLD_CHANNELS.md` §3 fill-lowest-first/party-aware assignment overrides a full target; §4 30 s cooldown + 5 s combat lock) | `op_0290` |
| `op_0201` | `portal_transition_request` | `c2s` | `portal_id: string — intent`, `claimed_destination_map_id: string — intent` (advisory only — the server re-derives the real destination from the map's authored portal graph, never trusts this field, `docs/VALIDATION.md` §5) | `—` (`70_integrations/WORLD_CHANNELS.md` §6 blocking sequence: portal-target validation, §3 channel assignment) | `op_0291` |
| `op_0202` | `coach_travel_request` | `c2s` | `destination_town_map_id: string — intent` | `—` (`70_integrations/WORLD_CHANNELS.md` §6 handoff; the fare charge itself is `10_systems/ECONOMY.md`'s — no `70_integrations/GAMEPLAY_SIMULATION.md` section owns fare validation, flagged) | `op_0291`, `op_0990` (§9.10, `reason: coach_fare`) |
| `op_0203` | `raid_enter_request` | `c2s` | `raid_token: string — intent` (any `docs/ID_REGISTRY.md` "Raids" token — `raid_undervault` \| `raid_mainspring` \| `raid_deepfrost` \| `raid_voidtide`; acting party read server-side, not client-asserted) | `—` (`10_systems/SPAWN.md` §7 as scoped by `70_integrations/GAMEPLAY_SIMULATION.md` §13; party-size floor `10_systems/social/RAID.md` §2/§3, cap `10_systems/social/PARTY.md` §1) | `op_0292` |
| `op_0204` | `raid_leave_request` | `c2s` | (empty map) | `—` (`10_systems/social/RAID.md` §5 fallen/Release/re-enter, fed by `70_integrations/GAMEPLAY_SIMULATION.md` §12) | `op_0292` |
| `op_0290` | `channel_switch_result` | `s2c` | `accepted: bool — server`, `channel_index: uint8 — server`, `spawn_point: string — server`, `reject_reason: enum{cooldown, combat_lock, channel_full, all_channels_full} — server` | `—` (`70_integrations/WORLD_CHANNELS.md` §3/§4) | `—` |
| `op_0291` | `transition_result` | `s2c` | `destination_map_id: string — server`, `channel_index: uint8 — server`, `spawn_point: string — server`, `accepted: bool — server`, `reject_reason: enum{invalid_portal, spinup_failed, held_queued} — server` | `—` (`70_integrations/WORLD_CHANNELS.md` §6) | `—` |
| `op_0292` | `raid_instance_result` | `s2c` | `accepted: bool — server`, `instance_id: string — server`, `stage_map_id: string — server`, `reject_reason: enum{party_too_small, party_too_large, headroom} — server` | `—` (`10_systems/SPAWN.md` §7, `10_systems/social/RAID.md` §2/§5) | `—` |

Note: `op_0291` is the single `transition_result` shape returned for both `op_0201` (portal) and `op_0202`
(coach); a coach transition additionally emits `op_0990` for the fare debit. Manual switch (`op_0200`)
severs the character's live mob engagement and resumes at the destination channel's `main` spawn per
`70_integrations/WORLD_CHANNELS.md` §4 — no field carries "where I stood," matching that section's rule
that `authority: shared` position does not carry across a channel/process boundary.

`op_0205`–`op_0289` and `op_0293`–`op_0299` remain **unminted/reserved** in this block.

### 9.4 Movement & reconciliation — `op_0300`–`op_0399`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §2 (the 20 Hz client report, the per-tick
reconciliation, the accept-if-plausible envelope, forward soft-correct vs hard-snap). Payload is the one
`authority: shared` pairing — position/velocity (`10_systems/PERSISTENCE.md` §4).

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0300` | `movement_input_report` | `c2s` | `position: vec2 — shared`, `velocity: vec2 — shared`, `client_time: uint32 — shared` (reported at the client's 20 Hz cadence, `10_systems/PERSISTENCE.md` §4) | `§2` (accept-if-plausible envelope: ± ½-tile slack + per-interval displacement margin + velocity-direction sanity check) | `op_0390` on rejection only |
| `op_0390` | `movement_hard_snap` | `s2c` | `position: vec2 — shared`, `velocity: vec2 — shared`, `corrected_seq: uint32 — server` (correlates to the rejected client `seq`, §8) | `§2` (gross-divergence / teleport-scale hard-snap path) | `—` |

Note: an in-envelope report gets **no reply** — the server silently adopts it (§2, "no correction
sent"). A small overshoot (soft-correct) carries **no dedicated opcode**: it rides the next `op_0400`
`entity_snapshot` (§9.5) as that occupant's own authoritative position/velocity, which the client
error-blends over 2–3 frames; only the gross-divergence case gets the immediate `op_0390` out-of-band
event. This is why the domain is intentionally narrow — one `authority: shared` pairing, one report
shape, one correction shape.

`op_0301`–`op_0389` and `op_0391`–`op_0399` remain **unminted/reserved** in this block.

### 9.5 World snapshot & entity lifecycle — `op_0400`–`op_0499`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §1.1 (the 10 Hz continuous-state snapshot
of visible entities' position/velocity/animation-state/status-icon set) and §13 (authoritative
spawn/despawn, death, `phase_shift`, boss-phase events — intent only animates these). All `s2c`.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0400` | `entity_snapshot` | `s2c` | `entities: array<{entity_id: string, position: vec2 — shared, velocity: vec2 — shared, animation_state: enum — server, status_icons: array — server}>` | `§1.1` (10 Hz broadcast, visible-entity set) | `—` |
| `op_0401` | `entity_spawn` | `s2c` | `entity_id: string — server`, `entity_kind: enum{mob, player, summon} — server`, `mob_id: string — server` (when a mob), `position: vec2 — shared` (same §4 pairing as `op_0400`; the spawn coordinate seeds the client's tracked copy), `tier: enum{normal, elite, boss} — server` | `§13` (spawn maintenance; elite/boss `spawn`-flourish invulnerability window, `10_systems/SPAWN.md` §6) | `—` |
| `op_0402` | `entity_despawn` | `s2c` | `entity_id: string — server`, `reason: enum{out_of_range, leash_return, expired} — server` | `§13` | `—` |
| `op_0403` | `entity_death` | `s2c` | `entity_id: string — server`, `killer_character_id: string — server` | `§5.2`/`§13` (death pushed as an immediate event) | credited kill triggers `op_0792` `kill_reward_delta` (§9.8) |
| `op_0404` | `boss_phase_shift` | `s2c` | `entity_id: string — server`, `phase_index: uint8 — server`, `invulnerable: bool — server` | `§13` (`life_threshold_pct` crossing, `boss_scripted` AI, `10_systems/AI_BEHAVIOR.md` §15) | `—` |
| `op_0405` | `death_penalty_delta` | `s2c` | `exp_lost: uint32 — server`, `exp_into_level: uint32 — server` (post-penalty), `respawn_map_id: string — server` (the stored bind point, `10_systems/DEATH_PENALTY.md` §4), `raid_override: bool — server` (party-instance fallen/Release flow instead of respawn, `10_systems/DEATH_PENALTY.md` §5.3) | `§12` (server-computed exp cost + bind-point respawn; follows the character's own `op_0403`) | `—` |

Note: this domain is deliberately `s2c`-only (§9.0's direction rule still holds — every opcode is
unidirectional) because the client requests nothing here; it only ever animates what the server pushes
(`§13`'s "client only animates, never authoritative" stance). An entering character's initial full state
is the first `entity_snapshot`/`entity_spawn` set pushed right after `op_0291`/`op_0192` (§9.3/§9.2)
completes the handoff — no separate "give me the snapshot" request exists.

`op_0406`–`op_0499` remain **unminted/reserved** in this block.

### 9.6 Combat — `op_0500`–`op_0599`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §5 (the `hit_event` on the hit-frame
signal, the §5.1 validation gate, the queued per-tick resolve, the resolved `HitResult`/death pushed as
immediate events). `c2s` = the hit-frame request; `s2c` = the authoritative result.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0500` | `hit_event_request` | `c2s` | `attacker_entity_id: string — intent`, `candidate_target_ids: array — intent`, `skill_id: string — intent` (basic-attack sentinel or `skill_<line>_NNN`), `client_hit_frame_time: uint32 — intent` | `§5.1` (actor/authenticity, range/geometry against server-side position, legality — learned/cooldown/`essence_cost` or basic-attack cadence, final stat blocks) | `op_0590` |
| `op_0590` | `hit_result` | `s2c` | `attacker_entity_id: string — server`, `results: array<{target_entity_id: string, outcome: enum{hit, miss, immune}, damage: uint32, is_crit: bool, element: enum — server, knockback_impulse: vec2 — server, hitstun_ms: uint16 — server, interrupted: bool — server}>` | `§5.2` (full `10_systems/COMBAT_FORMULA.md` §2 pipeline — hit/miss, immunity short-circuit, mitigation, element, crit, ±8 % variance, `empower`/`weaken`, level-diff dampener, floor; hit classing/knockback/hitstun/interrupt per §11) | `op_0403` `entity_death` (§9.5) follows if a target's `life` reaches 0 |

`op_0501`–`op_0589` and `op_0591`–`op_0599` remain **unminted/reserved** in this block.

### 9.7 Skill — `op_0600`–`op_0699`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §6 (cast request → the learned/rank/
cooldown/`essence_cost`/targeting gate → effect-op application) with §9 for any `apply_status` result.
`c2s` = cast request (skill id, rank, aim); `s2c` = the authoritative effect deltas.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0600` | `skill_cast_request` | `c2s` | `skill_id: string — intent`, `rank: uint8 — intent`, `aim: vec2 — intent` (or `target_entity_id: string — intent` per targeting shape) | `§6.1` (learned & ranked, prereq chain, `cooldown` elapsed, `essence_cost` payable, targeting shape resolved server-side) | `op_0690` |
| `op_0690` | `skill_cast_result` | `s2c` | `accepted: bool — server`, `skill_id: string — server`, `essence_spent: uint16 — server`, `cooldown_expires_at: uint32 — server`, `reject_reason: enum{not_learned, on_cooldown, insufficient_essence, prereq_unmet, out_of_range} — server` | `§6.1` | on accept, followed by `op_0590` (§9.6, for `deal_damage` effects) and/or `op_0691`/`op_0692`/`op_0693` per the skill's effect list |
| `op_0691` | `status_applied` | `s2c` | `target_entity_id: string — server`, `status: enum — server` (GLOSSARY status-effect token), `stacks: uint8 — server`, `expires_at: uint32 — server`, `source_power_snapshot: uint32 — server` | `§6.2` (`apply_status` op) and `§9` (application rules, `unique`/`stack`/`refresh` stacking, 12-status ceiling with least-remaining-duration displacement) | `—` |
| `op_0692` | `status_cleared` | `s2c` | `target_entity_id: string — server`, `status: enum — server`, `reason: enum{expired, cleansed, death_clear} — server` | `§9` (expiry/cleanse; `die` clears all statuses with no post-mortem tick) | `—` |
| `op_0693` | `skill_effect_delta` | `s2c` | `target_entity_id: string — server`, `op: enum{heal, restore_essence, grant_shield, knockback, pull, dash, leap, summon_entity, taunt} — server`, `amount: uint32 — server` (pool ops, capped per §7), `displacement: vec2 — server` (movement ops), `summoned_entity_id: string — server` (for `summon_entity`, ticks under `§13`) | `§6.2` (non-damage effect-op application) | `—` |

`op_0601`–`op_0689` and `op_0694`–`op_0699` remain **unminted/reserved** in this block.

### 9.8 Loot & drop pickup — `op_0700`–`op_0799`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §11 (drop rolls on monster death, loot
ownership tags/timers, the `shards` faucet). `c2s` = a pickup *request*; the server assigns per tag,
never the client (§7).

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0700` | `loot_pickup_request` | `c2s` | `drop_instance_id: string — intent` (a ground drop the client is in the platformer-friendly vacuum range of, `10_systems/INVENTORY.md` §4) | `§11` (ownership-tag/timer check — exclusive 60 s, free 60–120 s, despawn 120 s) | `op_0791` |
| `op_0790` | `loot_drop_spawn` | `s2c` | `drop_instance_id: string — server`, `position: vec2 — server`, `owner_tag_character_ids: array — server`, `exclusive_expires_at: uint32 — server`, `free_expires_at: uint32 — server` | `§11` (drop rolled per that mob's `drop_mob_NNN` table, tagged to whoever dealt/took damage) | `—` |
| `op_0791` | `loot_pickup_result` | `s2c` | `accepted: bool — server`, `item_id: string — server`, `qty: uint16 — server`, `rarity: enum — server`, `reject_reason: enum{not_tagged, expired, inventory_full} — server` | `§11` (no self-assigned `rarity`/`qty`/pool result) | on accept, followed by `op_0890` `inventory_delta` (§9.9) |
| `op_0792` | `kill_reward_delta` | `s2c` | `killed_entity_id: string — server`, `shards: uint32 — server` (guaranteed faucet per kill, level-scaled, **not** `fortune`-affected), `exp: uint32 — server`, `level_up: bool — server` | `§11` (`shards` faucet) and `§8` (`exp_awarded = round(base_exp(mob) · exp_diff_mult(...))`, level-up transaction — a kill's `shards` and `exp` are computed together and delivered on one packet) | if `level_up`, followed by `op_0891` `stat_block_delta` (§9.9); the **party split** of both fields is `70_integrations/CHAT_SOCIAL_BACKEND.md`'s reward arbitration (§9.13), not this packet |

Note: `shards` and quest items auto-route to the tagger and never lie on the ground (`10_systems/DROPS.md`
§7), so only tagged, non-currency items go through `op_0700`/`op_0791`; `op_0792` fires unconditionally
on an eligible kill with no client request. The exact world-process↔party-service request/response
boundary for reward arbitration is `70_integrations/GAMEPLAY_SIMULATION.md`'s own flagged Open Question
(not this doc's to resolve) — `op_0792` covers the solo/soloed-kill wire shape; the party-split delivery
mechanism is `70_integrations/CHAT_SOCIAL_BACKEND.md`'s to finalize.

`op_0701`–`op_0789` and `op_0793`–`op_0799` remain **unminted/reserved** in this block.

### 9.9 Inventory & equipment — `op_0800`–`op_0899`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §7 (equip → derived-stat recompute as sole
truth); inventory/bank moves are `server` truth (`10_systems/PERSISTENCE.md` §2) committed atomically
per `70_integrations/DATABASE_PERSISTENCE.md`. `c2s` = move/equip/use *request*; `s2c` = the
authoritative inventory + recomputed-stat delta.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0800` | `item_move_request` | `c2s` | `tab: enum{use, etc, equip} — intent`, `from_slot: uint8 — intent`, `to_slot: uint8 — intent`, `qty: uint16 — intent` | `§11` (inventory & bank addendum → `10_systems/INVENTORY.md` §1–§2 slot/stack ceilings) | `op_0890` |
| `op_0801` | `item_equip_request` | `c2s` | `item_id: string — intent`, `from_slot: uint8 — intent`, `equip_slot: enum — intent` (GLOSSARY equipment-slot token) | `§7` (derived-stat recompute as the sole truth; the server's stored equip-set is never overridden by a client claim) | `op_0890`, `op_0891` |
| `op_0802` | `item_unequip_request` | `c2s` | `equip_slot: enum — intent` | `§7` | `op_0890`, `op_0891` |
| `op_0803` | `item_use_request` | `c2s` | `item_id: string — intent`, `from_slot: uint8 — intent`, `target_entity_id: string — intent` (optional, self-target default) | `§11` (inventory & bank addendum; consumable pool restore recomputes through §6.2's `heal`/`restore_essence` caps) | `op_0890`, `op_0693` (§9.7, pool-restore delta) |
| `op_0804` | `bank_deposit_request` | `c2s` | `tab: enum{use, etc, equip} — intent`, `from_slot: uint8 — intent`, `qty: uint16 — intent` | `§11` (inventory & bank addendum → `10_systems/INVENTORY.md` §7 bank ceilings; committed per `70_integrations/DATABASE_PERSISTENCE.md`) | `op_0890` |
| `op_0805` | `bank_withdraw_request` | `c2s` | `bank_tab: enum{use, etc, equip} — intent`, `bank_slot: uint8 — intent`, `qty: uint16 — intent` | `§11` (inventory & bank addendum → `10_systems/INVENTORY.md` §7) | `op_0890` |
| `op_0890` | `inventory_delta` | `s2c` | `tab: enum — server`, `slots: array<{slot_index: uint8, item_id: string, qty: uint16}> — server`, `bank_slots: array — server` (present on a bank op) | `—` (`10_systems/PERSISTENCE.md` §2 inventory truth) | `—` |
| `op_0891` | `stat_block_delta` | `s2c` | `primaries: {might: uint16, finesse: uint16, focus: uint16, fortune: uint16} — server`, `derived: {life: uint32, essence: uint32, power: uint32, spellpower: uint32, armor: uint32, warding: uint32, precision: uint32, evasion: uint32, crit_rate: uint16, crit_power: uint16, haste: uint16} — server` | `§7` (compute order primaries → derived → soft/hard caps §6 → transient status fold; the sole recompute truth) | `—` |
| `op_0892` | `inventory_action_rejected` | `s2c` | `request_seq: uint32 — server`, `reason: enum{slot_full, wrong_tab, level_gate, stack_cap, invalid_item, bank_full} — server` | `§7` / `10_systems/INVENTORY.md` ceilings | `—` |

Note: `op_0891` is the **one canonical stat-recompute push**, minted once here and reused as the response
for every trigger that forces a `§7` recompute — equip/unequip (this domain), free-point
allocation/respec (`op_0900`/`op_0901`, §9.10), level-up (`op_0792`/`op_1092`, §9.8/§9.11), and a
transient status fold (§9.7) — rather than each domain minting a duplicate shape for the same
server-truth push.

`op_0806`–`op_0889` and `op_0893`–`op_0899` remain **unminted/reserved** in this block.

### 9.10 Shards, acquisition & enhancement — `op_0900`–`op_0999`
Validating sections: `70_integrations/GAMEPLAY_SIMULATION.md` §10 (enhancement attempt → server-held
soft-pity roll, no reroll) and §7 (free-point allocation fee, wallet); shop buy/sell are
`10_systems/ECONOMY.md` sinks/faucets executed server-side. This block is the sharp end of §7 — the
`shards` amount, the enhance result, and the rolled outcome are **`s2c`-only**.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_0900` | `stat_allocate_request` | `c2s` | `points: {might: uint8, finesse: uint8, focus: uint8, fortune: uint8} — intent` (requested distribution, intent only) | `§7` (checked against the available +2/level pool; applied only if it covers) | `op_0891` (§9.9) |
| `op_0901` | `stat_reallocate_request` | `c2s` | `points: {might: uint8, finesse: uint8, focus: uint8, fortune: uint8} — intent` (full redistribution intent) | `§7` (reallocation `shards` fee charged via wallet, `10_systems/LEVELING.md`/`10_systems/ECONOMY.md`) | `op_0891` (§9.9), `op_0990` |
| `op_0902` | `enhancement_attempt_request` | `c2s` | `item_id: string — intent`, `from_slot: uint8 — intent` (the target equip; no outcome field, §7.1) | `§10` (matching-tier `emberstone` held + `shards` fee payable; consumed regardless of roll outcome) | `op_0991` |
| `op_0903` | `shop_buy_request` | `c2s` | `vendor_npc_id: string — intent`, `sku: string — intent`, `qty: uint16 — intent` | `—` (`10_systems/ECONOMY.md` §4 vendor price bands; no `70_integrations/GAMEPLAY_SIMULATION.md` section owns shop pricing — flagged) | `op_0992` |
| `op_0904` | `shop_sell_request` | `c2s` | `item_id: string — intent`, `from_slot: uint8 — intent`, `qty: uint16 — intent` | `—` (`10_systems/ECONOMY.md` §4 — vendor buys at 25 % of buy value) | `op_0992` |
| `op_0990` | `wallet_delta` | `s2c` | `shards: uint32 — server`, `reason: enum{shop_buy, shop_sell, respec_fee, enhancement_fee, coach_fare} — server` | `—` (`10_systems/ECONOMY.md` sinks/faucets; `coach_fare` per `70_integrations/WORLD_CHANNELS.md` §6) | `—` |
| `op_0991` | `enhancement_result` | `s2c` | `item_id: string — server`, `success: bool — server`, `enhance_level: uint8 — server` (never destroys/downgrades, `10_systems/ENHANCEMENT.md` §2), `pity_counter: uint8 — server` (server-held persisted state, §3/§6) | `§10` | `—` |
| `op_0992` | `shop_transaction_result` | `s2c` | `accepted: bool — server`, `item_id: string — server`, `qty: uint16 — server`, `reject_reason: enum{insufficient_shards, out_of_stock, inventory_full} — server` | `—` (`10_systems/ECONOMY.md` §4) | `op_0890` (§9.9), `op_0990` |

`op_0905`–`op_0989` and `op_0993`–`op_0999` remain **unminted/reserved** in this block.

### 9.11 Quest — `op_1000`–`op_1099`
Validating sections: `70_integrations/GAMEPLAY_SIMULATION.md` §14 (quest never-trust gate, same
request→validate→delta shape) and §8 (turn-in `exp`/level-up). `c2s` = accept/progress/turn-in
*request*; `s2c` = the authoritative quest-flag + reward delta.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_1000` | `quest_accept_request` | `c2s` | `quest_id: string — intent`, `giver_npc_id: string — intent` | `§14`; `10_systems/QUESTS.md` §2/§6 (`level_requirement` hard gate, `prereqs`) | `op_1090` |
| `op_1001` | `quest_progress_request` | `c2s` | `quest_id: string — intent`, `step_id: string — intent`, `progress_ref: string — intent` (a kill/collect/reach/interact reference — never an asserted completion) | `§14` (same request→validate→delta shape as the never-trust list) | `op_1091` |
| `op_1002` | `quest_turn_in_request` | `c2s` | `quest_id: string — intent`, `turn_in_npc_id: string — intent` | `§8` (`exp`/`shards`/item reward, level-up transaction) and `§14` | `op_1092` |
| `op_1003` | `quest_abandon_request` | `c2s` | `quest_id: string — intent` | `—` (`10_systems/QUESTS.md` §7 — no pre-turn-in reward to revoke; `collect`-step items already picked up are kept) | `op_1093` |
| `op_1090` | `quest_accept_result` | `s2c` | `accepted: bool — server`, `quest_id: string — server`, `step_states: array — server`, `reject_reason: enum{level_gate, prereq_unmet, concurrency_cap} — server` (cap 20 active, `10_systems/QUESTS.md` §8) | `§14` | `—` |
| `op_1091` | `quest_progress_delta` | `s2c` | `quest_id: string — server`, `step_id: string — server`, `progress: uint16 — server`, `target: uint16 — server` | `§14` | `—` |
| `op_1092` | `quest_turn_in_result` | `s2c` | `quest_id: string — server`, `exp: uint32 — server`, `shards: uint32 — server`, `items_granted: array — server`, `level_up: bool — server` | `§8` | if `level_up`, followed by `op_0891` `stat_block_delta` (§9.9) |
| `op_1093` | `quest_abandon_result` | `s2c` | `quest_id: string — server`, `accepted: bool — server` | `—` (`10_systems/QUESTS.md` §7) | `—` |

`op_1004`–`op_1089` and `op_1094`–`op_1099` remain **unminted/reserved** in this block.

### 9.12 Chat — `op_1100`–`op_1199`
Validating layer: `70_integrations/CHAT_SOCIAL_BACKEND.md` (map-scoped `normal`, roster `party`/`guild`,
`whisper`, rate limits, moderation hooks). Not gated by a `70_integrations/GAMEPLAY_SIMULATION.md`
section — social-tier relay; cite CHAT_SOCIAL_BACKEND in notes.

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_1100` | `chat_send_request` | `c2s` | `channel: enum{normal, party, guild, whisper} — intent`, `body: string — intent`, `whisper_recipient: string — intent` (whisper only) | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §2 mute/rate-limit/filter gates, §4 relay hop sequence) | `op_1190` or `op_1191` |
| `op_1101` | `chat_report_request` | `c2s` | `message_id: string — intent`, `reason: string — intent` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §2 report flow — captured verbatim into the moderation queue) | `op_1192` |
| `op_1190` | `chat_message` | `s2c` | `channel: enum — server`, `sender_character_id: string — server`, `body: string — server`, `sent_at: uint32 — server` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §4 relay) | `—` |
| `op_1191` | `chat_send_rejected` | `s2c` | `request_seq: uint32 — server`, `reason: enum{rate_limited, channel_muted, gm_muted, recipient_offline} — server` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §2 escalation ladder; §5 whisper-offline result) | `—` |
| `op_1192` | `chat_report_ack` | `s2c` | `message_id: string — server`, `queued: bool — server` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §2 report flow) | `—` |

Note: the `channel` enum ships four values (`normal`/`party`/`guild`/`whisper`) per
`10_systems/social/CHAT.md`'s "Planned scope." A fifth value, `world`, is proposed but **not yet
adopted** (`70_integrations/CHAT_SOCIAL_BACKEND.md` §1 Open Question, pending `10_systems/social/CHAT.md`
and `00_vision/GLOSSARY.md` promotion) — it is **not** a legal wire value until that promotion lands;
flagged, not minted as a live enum member, per the "flag, don't guess" law.

`op_1102`–`op_1189` and `op_1193`–`op_1199` remain **unminted/reserved** in this block.

### 9.13 Party & social — `op_1200`–`op_1299`
Validating layer: `70_integrations/CHAT_SOCIAL_BACKEND.md` (party roster, guild, live `TRADING` escrow,
async `MARKET`, `MAIL`); the party exp/loot **arbitration** handoff is that doc's, fed by
`70_integrations/GAMEPLAY_SIMULATION.md` §8/§11 (which compute the total and roll, then hand off the
split). All value transfer is `server` truth committed through the Postgres ledger
(`70_integrations/DATABASE_PERSISTENCE.md`), never a client copy (§7).

| Opcode | Name | Dir | Payload fields (`field: type` — wire annotation, §7.2) | Server validation | Response / delta packet(s) |
|---|---|---|---|---|---|
| `op_1200` | `party_invite_request` | `c2s` | `target_character_id: string — intent` | `—` (`10_systems/social/PARTY.md` §1 roster cap 6; `70_integrations/CHAT_SOCIAL_BACKEND.md` §3.2 roster service) | `op_1270` or `op_1271` |
| `op_1201` | `party_join_request` | `c2s` | `invite_id: string — intent` | `—` (§3.2) | `op_1270` |
| `op_1202` | `party_leave_request` | `c2s` | (empty map) | `—` (§3.2; a party of 1 auto-disbands, `10_systems/social/PARTY.md` §1) | `op_1270` |
| `op_1203` | `party_kick_request` | `c2s` | `target_character_id: string — intent` (leader-only, checked server-side) | `—` (§3.2) | `op_1270` or `op_1271` |
| `op_1204` | `party_loot_mode_request` | `c2s` | `mode: enum — intent` (`10_systems/social/PARTY.md` §5 loot-mode enum) | `—` (§3.2) | `op_1270` |
| `op_1205` | `guild_create_request` | `c2s` | `name: string — intent` | `—` (`10_systems/social/GUILD.md` §2 global-uniqueness/name policy; creation fee `10_systems/ECONOMY.md`) | `op_1272` or `op_1273` |
| `op_1206` | `guild_invite_request` | `c2s` | `target_character_id: string — intent` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §3.3) | `op_1272` or `op_1273` |
| `op_1207` | `guild_join_request` | `c2s` | `invite_id: string — intent` | `—` (§3.3) | `op_1272` |
| `op_1208` | `guild_leave_request` | `c2s` | (empty map) | `—` (§3.3) | `op_1272` |
| `op_1209` | `guild_rank_change_request` | `c2s` | `target_character_id: string — intent`, `new_rank: string — intent` (officer-only, checked server-side) | `—` (`10_systems/social/GUILD.md` §3 rank policy) | `op_1272` or `op_1273` |
| `op_1210` | `trade_invite_request` | `c2s` | `target_character_id: string — intent` | `—` (`10_systems/social/TRADING.md` §1 same-map proximity gate) | `op_1274` |
| `op_1211` | `trade_offer_update_request` | `c2s` | `items: array — intent` (item refs/qty, intent only), `shards: uint32 — intent` (offered amount, intent only) | `—` (`10_systems/social/TRADING.md` §3 offer/lock state machine) | `op_1274` |
| `op_1212` | `trade_confirm_request` | `c2s` | (empty map) | `—` (`10_systems/social/TRADING.md` §3 confirm → atomic swap) | `op_1274` or `op_1275` |
| `op_1213` | `trade_cancel_request` | `c2s` | (empty map) | `—` (`10_systems/social/TRADING.md` §3 — nothing transferred pre-swap) | `op_1274` |
| `op_1214` | `market_list_request` | `c2s` | `item_id: string — intent`, `from_slot: uint8 — intent`, `ask_price: uint32 — intent` | `—` (`10_systems/social/MARKET.md` data sketch; listing-fee ownership unsettled, `70_integrations/CHAT_SOCIAL_BACKEND.md` §3.5 Open Question) | `op_1276` or `op_1277` |
| `op_1215` | `market_buy_request` | `c2s` | `listing_id: string — intent` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §3.5 atomic buy transaction) | `op_1276` or `op_1277` |
| `op_1216` | `market_delist_request` | `c2s` | `listing_id: string — intent` | `—` (§3.5) | `op_1276` |
| `op_1217` | `mail_compose_request` | `c2s` | `recipient_character_id: string — intent`, `item_id: string — intent` (optional), `shards_attached: uint32 — intent`, `cod_amount: uint32 — intent` | `—` (`10_systems/social/MAIL.md` data sketch; send fee `10_systems/ECONOMY.md`) | `op_1278` or `op_1281` |
| `op_1218` | `mail_claim_request` | `c2s` | `mail_id: string — intent` | `—` (`70_integrations/CHAT_SOCIAL_BACKEND.md` §3.6 claim transaction) | `op_1279` or `op_1281` |
| `op_1270` | `party_roster_update` | `s2c` | `party_id: string — server`, `members: array — server`, `leader_character_id: string — server`, `loot_mode: enum — server` | `—` (§3.2) | `—` |
| `op_1271` | `party_action_rejected` | `s2c` | `request_seq: uint32 — server`, `reason: enum{invite_declined, party_full, not_leader, target_unreachable} — server` | `—` (§3.2) | `—` |
| `op_1272` | `guild_roster_update` | `s2c` | `guild_id: string — server`, `members: array — server`, `ranks: array — server`, `motd: string — server` | `—` (§3.3) | `—` |
| `op_1273` | `guild_action_rejected` | `s2c` | `request_seq: uint32 — server`, `reason: enum{name_taken, insufficient_rank, roster_cap, invite_declined} — server` | `—` (§3.3) | `—` |
| `op_1274` | `trade_state_update` | `s2c` | `session_id: string — server`, `offers: {a: array, b: array} — server`, `locked: {a: bool, b: bool} — server` | `—` (`10_systems/social/TRADING.md` §3) | `—` |
| `op_1275` | `trade_result` | `s2c` | `session_id: string — server`, `committed: bool — server`, `items_received: array — server`, `shards_received: uint32 — server` | `—` (`10_systems/social/TRADING.md` §3 atomic swap) | `—` |
| `op_1276` | `market_listing_update` | `s2c` | `listing_id: string — server`, `status: enum{active, sold, delisted, expired} — server` | `—` (§3.5) | `—` |
| `op_1277` | `market_action_rejected` | `s2c` | `request_seq: uint32 — server`, `reason: enum{fee_unpayable, item_untradeable, listing_not_found} — server` | `—` (§3.5) | `—` |
| `op_1278` | `mail_delivered` | `s2c` | `mail_id: string — server`, `sender_character_id: string — server`, `has_attachment: bool — server` | `—` (§3.6) | `—` |
| `op_1279` | `mail_claim_result` | `s2c` | `mail_id: string — server`, `item_id: string — server`, `shards_received: uint32 — server`, `cod_paid: uint32 — server` | `—` (§3.6) | `—` |
| `op_1280` | `presence_update` | `s2c` | `character_id: string — server`, `online: bool — server`, `roster_scope: enum{party, guild} — server` | `—` (§5 — proposed presence indicator, **not yet adopted** by `10_systems/social/PARTY.md`/`10_systems/social/GUILD.md`, flagged in their Open Questions) | `—` |
| `op_1281` | `mail_action_rejected` | `s2c` | `request_seq: uint32 — server`, `reason: enum{recipient_not_found, insufficient_shards, item_untradeable} — server` | `—` (§3.6) | `—` |

Note: `party`/`guild` reward *math* stays `10_systems/social/PARTY.md`'s and `10_systems/DROPS.md`'s;
this table only wires the roster/escrow/listing *requests*. The exp/loot **split** that
`op_0792`/`op_0791` (§9.8) hand off to this tier has no dedicated opcode of its own here — that
world-process↔party-service boundary is `70_integrations/GAMEPLAY_SIMULATION.md`'s own flagged Open
Question, not resolved by this catalog. `op_1280` mirrors the `world`-channel flag (§9.12): a proposed
addition, not a shipped one, per the "flag, don't guess" law.

`op_1219`–`op_1269` and `op_1282`–`op_1299` remain **unminted/reserved** in this block.

---

## 10. Failure modes & degradation (external wire dependencies)

Per `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`, every external dependency lists a failure mode;
fail-loud in dev, fail-safe in prod (`30_engineering/ENGINEERING_STANDARDS.md` directive 7). A component
that cannot prove a `server` truth refuses the action, never fabricates it.

| Dependency / condition | Failure mode | Stance |
|---|---|---|
| TLS handshake | Cannot establish a secure socket → no connection | Fail-closed: **no plaintext fallback** (§1); the client retries WSS, surfacing a connection error, never downgrading. |
| WSS transport dropped mid-session | Socket dies | Detected within ~30 s (§6); the in-world session survives in the 90 s grace (`70_integrations/ACCOUNTS_AUTH.md` §4.3) and the client resumes with the signed ticket; no state minted client-side (`70_integrations/BACKEND_ARCHITECTURE.md` §8). |
| Malformed / undecodable envelope | A message fails MessagePack decode or violates §3 | The receiver **drops** the message and never guesses fields; the gateway may close a connection that exceeds a malformed-message threshold (DoS/abuse guard). Fail-loud in dev. |
| Unknown `op` | An opcode the receiver does not know (older client, newer server) | Ignore + log; the §4 `protocol_version` gate is the primary defense, so this is the belt-and-suspenders path, never a crash. |
| `permessage-deflate` negotiation fails | The extension is unavailable | Fall back to uncompressed — both sides MUST accept an uncompressed payload; compression (§5) is opportunistic, never required for correctness. |
| Oversized message | A payload exceeds the max-message-size cap | Reject (a DoS guard); the cap is an ops-tunable value with a fixed shape (Open Questions). |
| Idempotency store unavailable (reconnect dedup, §8) | The `(session, seq)` dedup cannot be checked | Fail-closed for acquisition packets: **refuse** the replayed mutating request rather than risk a double-apply (`70_integrations/GAMEPLAY_SIMULATION.md` §10/§14), matching the roll-blocked-not-fabricated stance. |

---

## Open Questions

- **Snapshot encoding & interest management.** Whether the 10 Hz snapshot (§9.5) is full visible-state
  keyframes or delta-encoded against the last acknowledged snapshot, and whether a crowded population
  channel needs per-client area-of-interest filtering, is a capacity question owned by
  `70_integrations/WORLD_CHANNELS.md` (its own Open Question) and `70_integrations/GAMEPLAY_SIMULATION.md`
  §1.1; the envelope (§3) and the reliable-ordered transport (§1) support either encoding. §9.5's
  `entity_snapshot` (`op_0400`) is authored as whole-visible-state per broadcast; revisit that row (not
  its opcode — minted opcodes are immutable) if delta-encoding or area-of-interest filtering is adopted
  at those docs' next revision.
- **Max-message-size and compression tuning.** The max payload cap (§10), the ~512-byte compression
  threshold, and the DEFLATE level (§5) are ops-tunable numbers with a fixed shape; exact values want a
  coding-pass bandwidth/CPU measurement against real Godot 4.3 client packing, not a design guess.
- **MessagePack extension-type assignments** for hot compound values (position/velocity vectors, packed
  status-icon sets) are a coding-pass detail (§2); none are reserved here.
- **Debug JSON encoding** (§2) — whether non-production builds may negotiate a JSON payload encoding at
  the handshake (§4) for inspectability is a minor coding-pass convenience, not fixed here.
- **QUIC/WebTransport transport revision** (§1) is kept in reserve behind the `protocol_version`
  handshake; if Godot's and Phoenix's support matures, revisiting the transport is a `protocol_version`
  bump, not a redesign — flagged, not scheduled.
- **Stage-2 catalog authoring** (§9) is **complete** — 103 opcodes minted across the 13 domain blocks
  against the §9.0 template, each citing its `70_integrations/GAMEPLAY_SIMULATION.md` (or domain-owning
  doc) validating section. Residue surfaced during the fill, now flagged at its own domain row rather
  than here: no `70_integrations/GAMEPLAY_SIMULATION.md` section owns shop pricing or coach-fare
  validation (§9.3/§9.10 cite `10_systems/ECONOMY.md` instead); the `world` chat channel (§9.12) and the
  party/guild `presence_update` (§9.13) are proposed additions awaiting promotion by their owning docs,
  not shipped enum/opcode members; and the world-process↔party-service reward-arbitration wire boundary
  (§9.8/§9.13) stays `70_integrations/GAMEPLAY_SIMULATION.md`'s own open item, not resolved by this
  catalog.
