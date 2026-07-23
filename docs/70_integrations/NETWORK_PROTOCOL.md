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
   authority tags are `shared` (position/velocity, `10_systems/PERSISTENCE.md` §4) or `client`-advisory
   input the server re-checks; never `server`-truth.
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

## 9. Packet catalog — domain-ordered skeleton (**catalog filled in stage 2**)

> **STAGE STATUS.** This section fixes the **structure, opcode sub-blocks, validating sections, and the
> per-packet template**. The individual packet rows are authored in **stage 2** by a Sonnet sub-agent
> filling the template below inside this fixed contract; every row it adds must satisfy §7 (the
> acquisition rule) and cite its `70_integrations/GAMEPLAY_SIMULATION.md` validating section. No opcode
> is minted until it is written into a row here; minted opcodes are immutable (`docs/ID_REGISTRY.md`).

### 9.0 Per-packet template (fill one row per packet)

Each domain sub-section carries one table of this exact shape:

| Opcode | Name | Dir | Payload fields (`field: type` — authority tag) | Server validation (`GAMEPLAY_SIMULATION.md §N`) | Response / delta packet(s) |
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
mostly `—` for this block. **Catalog filled in stage 2.**

### 9.2 Auth, handshake & session — `op_0100`–`op_0199`
Validating layer: `70_integrations/ACCOUNTS_AUTH.md` §3 (login, token) and §4 (gateway bind,
character-select, resume); the §4 `protocol_version`/`client_version`/`content_version` negotiation is
this doc's. Not gated by a `70_integrations/GAMEPLAY_SIMULATION.md` section — cite ACCOUNTS_AUTH in
notes. **Catalog filled in stage 2.**

### 9.3 Channel & instance management — `op_0200`–`op_0299`
Validating layer: `70_integrations/WORLD_CHANNELS.md` §3 (channel select/switch) and §6 (map-transition
handoff sequencing / what blocks); PQ-instance allocation is `10_systems/SPAWN.md` §7 as scoped by
`70_integrations/GAMEPLAY_SIMULATION.md` §13. **Catalog filled in stage 2.**

### 9.4 Movement & reconciliation — `op_0300`–`op_0399`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §2 (the 20 Hz client report, the per-tick
reconciliation, the accept-if-plausible envelope, forward soft-correct vs hard-snap). Payload is the one
`authority: shared` pairing — position/velocity (`10_systems/PERSISTENCE.md` §4). **Catalog filled in
stage 2.**

### 9.5 World snapshot & entity lifecycle — `op_0400`–`op_0499`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §1.1 (the 10 Hz continuous-state snapshot
of visible entities' position/velocity/animation-state/status-icon set) and §13 (authoritative
spawn/despawn, death, `phase_shift`, boss-phase events — client only animates these). All `s2c`.
**Catalog filled in stage 2.**

### 9.6 Combat — `op_0500`–`op_0599`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §5 (the `hit_event` on the hit-frame
signal, the §5.1 validation gate, the queued per-tick resolve, the resolved `HitResult`/death pushed as
immediate events). `c2s` = the hit-frame request; `s2c` = the authoritative result. **Catalog filled in
stage 2.**

### 9.7 Skill — `op_0600`–`op_0699`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §6 (cast request → the learned/rank/
cooldown/`essence_cost`/targeting gate → effect-op application) with §9 for any `apply_status` result.
`c2s` = cast request (skill id, rank, aim); `s2c` = the authoritative effect deltas. **Catalog filled in
stage 2.**

### 9.8 Loot & drop pickup — `op_0700`–`op_0799`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §11 (drop rolls on monster death, loot
ownership tags/timers, the `shards` faucet). `c2s` = a pickup *request*; the server assigns per tag,
never the client (§7). **Catalog filled in stage 2.**

### 9.9 Inventory & equipment — `op_0800`–`op_0899`
Validating section: `70_integrations/GAMEPLAY_SIMULATION.md` §7 (equip → derived-stat recompute as sole
truth); inventory/bank moves are `server` truth (`10_systems/PERSISTENCE.md` §2) committed atomically
per `70_integrations/DATABASE_PERSISTENCE.md`. `c2s` = move/equip/use *request*; `s2c` = the
authoritative inventory + recomputed-stat delta. **Catalog filled in stage 2.**

### 9.10 Shards, acquisition & enhancement — `op_0900`–`op_0999`
Validating sections: `70_integrations/GAMEPLAY_SIMULATION.md` §10 (enhancement attempt → server-held
soft-pity roll, no reroll) and §7 (free-point allocation fee, wallet); shop buy/sell are
`10_systems/ECONOMY.md` sinks/faucets executed server-side. This block is the sharp end of §7 — the
`shards` amount, the enhance result, and the rolled outcome are **`s2c`-only**. **Catalog filled in
stage 2.**

### 9.11 Quest — `op_1000`–`op_1099`
Validating sections: `70_integrations/GAMEPLAY_SIMULATION.md` §14 (quest never-trust gate, same
request→validate→delta shape) and §8 (turn-in `exp`/level-up). `c2s` = accept/progress/turn-in
*request*; `s2c` = the authoritative quest-flag + reward delta. **Catalog filled in stage 2.**

### 9.12 Chat — `op_1100`–`op_1199`
Validating layer: `70_integrations/CHAT_SOCIAL_BACKEND.md` (map-scoped `normal`, roster `party`/`guild`,
`whisper`, rate limits, moderation hooks). Not gated by a `70_integrations/GAMEPLAY_SIMULATION.md`
section — social-tier relay; cite CHAT_SOCIAL_BACKEND in notes. **Catalog filled in stage 2.**

### 9.13 Party & social — `op_1200`–`op_1299`
Validating layer: `70_integrations/CHAT_SOCIAL_BACKEND.md` (party roster, guild, live `TRADING` escrow,
async `MARKET`, `MAIL`); the party exp/loot **arbitration** handoff is that doc's, fed by
`70_integrations/GAMEPLAY_SIMULATION.md` §8/§11 (which compute the total and roll, then hand off the
split). All value transfer is `server` truth committed through the Postgres ledger
(`70_integrations/DATABASE_PERSISTENCE.md`), never a client copy (§7). **Catalog filled in stage 2.**

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
  §1.1; the envelope (§3) and the reliable-ordered transport (§1) support either encoding. Confirm at
  their authoring and before the stage-2 §9.5 rows are minted.
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
- **Stage-2 catalog authoring** (§9) is the remaining deliverable: a Sonnet sub-agent fills every
  domain table against the §9.0 template, minting opcodes into `docs/ID_REGISTRY.md`'s blocks and citing
  each mutating packet's `70_integrations/GAMEPLAY_SIMULATION.md` validating section. This is a fixed-scope
  fill inside this contract, not an open design question.
