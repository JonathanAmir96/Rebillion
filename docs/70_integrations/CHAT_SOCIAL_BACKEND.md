# CHAT_SOCIAL_BACKEND.md — Chat & Social-Service Internals

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/VALIDATION.md §1,
10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md, 10_systems/social/CHAT.md,
10_systems/social/PARTY.md, 10_systems/social/GUILD.md, 10_systems/social/MARKET.md,
10_systems/social/MAIL.md, 10_systems/social/TRADING.md, 10_systems/social/RAID.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/DATABASE_PERSISTENCE.md,
70_integrations/WORLD_CHANNELS.md, 70_integrations/NETWORK_PROTOCOL.md,
70_integrations/ACCOUNTS_AUTH.md, docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

Owner doc for the **social-services tier's internals**: relay topology, roster/registry state,
escrow mechanics, rate limits, moderation hooks, and presence semantics for the six
server-deferred systems `70_integrations/BACKEND_ARCHITECTURE.md` §7 assigns here. That doc fixes
the topology contract (one social tier, scaling independently of world nodes) and where each
system lands; this doc is the sibling it delegates internals to (§9) and never re-derives its
topology, its database-technology choice (§3), or its failure-mode table (§8) — it cites them.
Game-design rules stay owned where they already are: exp/loot math is
`10_systems/social/PARTY.md`'s, guild fees are `10_systems/ECONOMY.md`'s, escrow *policy* (what
may trade, untradeable items) is `10_systems/social/TRADING.md`'s and `10_systems/social/MARKET.md`'s.
This doc restates none of it — it wires each system onto the social-services tier and fixes the
engineering calls (rate limits, moderation seams, presence fan-out) those docs explicitly leave
open. Storage schema is `70_integrations/DATABASE_PERSISTENCE.md`'s (authored in parallel this
wave); cross-channel/cross-map reach for chat and market conforms to
`70_integrations/WORLD_CHANNELS.md`'s cross-channel state section (authored in parallel); the wire
format for every packet named below is `70_integrations/NETWORK_PROTOCOL.md`'s (authored later,
cited by name wherever the wire begins). **Implemented when:** the interim solo build has shipped
and the owner greenlights a live server (`70_integrations/BACKEND_ARCHITECTURE.md` §10) — nothing
here blocks or precedes the solo build, matching every social/ stub's own "ships present but
dormant" stance.

## 1. Chat channels — roster and the world-channel gap

`10_systems/social/CHAT.md` is the **channel-roster owner**; its "Planned scope" fixes four
channels — `normal` (map-scoped broadcast), `party` (roster-scoped), `guild` (roster-scoped),
`whisper` (1:1, not map-scoped). **It does not define a `world` channel.** The task brief for this
doc asks for a world channel; per this doc's own instruction to check the rule owner first and
follow what it actually says, a `world` channel is **not assumed to exist** — it is proposed below
as an engineering addition, flagged to `10_systems/social/CHAT.md` for adoption, and never treated
as shipped GLOSSARY vocabulary until that doc (and `00_vision/GLOSSARY.md`'s Provisional section)
promotes it.

**Proposed addition: a `world` channel**, server-broadcast to every connected character regardless
of map or population channel (`70_integrations/WORLD_CHANNELS.md` cross-channel reach — a `world`
message must reach a player on any population copy of any map, unlike `normal`'s single-map-process
scope). Rationale for proposing it here rather than leaving chat at four channels: `MARKET` (§3)
is the one social system that is deliberately world-global and asynchronous, and a live game
without any world-wide text channel has no lightweight way to advertise a listing or call out a
world event — every other MMORPG-shaped social system in this tree (`GUILD` recruitment, `MARKET`
"selling X") wants a broadcast surface that `normal` (single map) and `whisper` (1:1) cannot serve.
**Cost, stated plainly:** a `world` channel fans out to the *entire* connected population from one
relay, not one map's occupants — it is the single most expensive chat channel to rate-limit and
moderate (§2), and it is the one channel that scales with total concurrency rather than per-map
occupancy. It is proposed as an opt-in, heavily-throttled channel for exactly that reason (§2).

| Channel | Scope | Roster/relay source | Reach |
|---|---|---|---|
| `normal` | Map-local broadcast | Sender's current `map_NNN` (`10_systems/social/CHAT.md`) | One map process only — never crosses population channels (`70_integrations/WORLD_CHANNELS.md` §5 cross-channel state) |
| `party` | Roster-scoped | `10_systems/social/PARTY.md` §1 roster | Crosses maps — a party member off-map still receives party chat (party membership, not location, gates it) |
| `guild` | Roster-scoped | `10_systems/social/GUILD.md` §3/§7 roster | Crosses maps — same reasoning as `party` |
| `whisper` | 1:1 | Recipient's live session (presence, §5) | Crosses maps; requires recipient online (no offline whisper — that gap is `MAIL`'s, §3.5) |
| `world` (proposed, engineering addition — not yet in `10_systems/social/CHAT.md`) | Global broadcast | Every connected session | Crosses every map, every population channel, every node |

**Flag to `10_systems/social/CHAT.md` and `00_vision/GLOSSARY.md`:** adopt `world` as a fifth
channel token (its Open Questions already leaves "spam/rate limits... unset — owner
`10_systems/HUD.md` jointly with this doc," so this proposal and its rate limit, §2, are handed
back to that doc's owner for promotion, not silently assumed canon).

## 2. Rate limits and moderation hooks

Per this doc's mandate, these are **engineering calls**, not policy content — each gets a one-line
rationale. Moderation is **hooks/seams only** (filter pipeline, report flow, GM mute); the
wordlist, escalation policy, and staffing are live-ops decisions — `10_systems/social/GUILD.md` §2
flags its profanity rules as "applied server-side, not designed here," and
`70_integrations/ACCOUNTS_AUTH.md` §5 takes the same stance for name filtering ("applied
server-side, deliberately not authored in this tree") — this doc does not reopen that.

**Rate limits (messages per interval, per sending character), enforced at the gateway/relay
before a message reaches the social-services chat relay (`70_integrations/BACKEND_ARCHITECTURE.md`
§1 edge/gateway owns rate-limiting generally; this is chat's concrete instance of it):**

| Channel | Limit | Rationale |
|---|---|---|
| `normal` | 5 messages / 10 s | Map-local chat is low-stakes flavor traffic (`00_vision/PILLARS.md` P1 — a conversation should read without effort); generous enough for banter, tight enough that one process can't be flooded off a single map |
| `party` | 10 messages / 10 s | Small trusted roster (cap 6, `10_systems/social/PARTY.md` §1) coordinating combat needs faster turnaround than map chat |
| `guild` | 10 messages / 10 s | Same trust/coordination reasoning as `party`, at a larger roster (cap 60, `10_systems/social/GUILD.md` §4) |
| `whisper` | 5 messages / 10 s **to a single recipient**, 15 messages / 10 s aggregate across all recipients | The per-recipient cap stops one-target harassment; the aggregate cap stops a account from blasting the whole population 1:1 as a `world`-channel workaround |
| `world` (proposed, §1) | 1 message / 60 s | The most expensive channel to fan out (§1) and the highest-visibility spam vector; a full-minute cooldown keeps it a rare "advertise once" surface, not a live feed |

**Escalation ladder shape** (the shape is an engineering call; the trigger thresholds and durations
are live-ops-tunable configuration, not fixed here — matching `70_integrations/ACCOUNTS_AUTH.md`
§3's identical stance on sign-in lockout):

1. **Soft throttle** — a message that exceeds a channel's rate limit is dropped client-side-visibly
   (the sender sees "sending too fast," nothing reaches recipients); no record beyond a rolling
   counter in the presence/rate-limit cache (`70_integrations/BACKEND_ARCHITECTURE.md` §3's Redis +
   ETS/Presence tier). Self-clearing once the sender's rate window resets.
2. **Auto-mute** — repeated soft-throttle hits inside a short rolling window escalate to a
   short, automatic, channel-scoped mute (the offending channel only — a `world`-channel auto-mute
   never silences `party`, since a party still needs to coordinate through an incident). Duration
   is config, not fixed here.
3. **Report flow** — any player may report a chat message (message id, sender, channel, timestamp,
   and the message body as sent — captured verbatim so a GM reviews what was actually said, not a
   paraphrase); reports land in a moderation queue on the social-services tier. The queue should be
   durable — but `70_integrations/DATABASE_PERSISTENCE.md` §3.3's `social` schema does not yet
   define a report/moderation table, so its schema is pending (flagged in Open Questions to that
   doc). This is a seam (the queue and its eventual schema), not a triage policy.
4. **GM mute** — a human moderator issues an account-scoped, cross-channel mute (all of `normal`/
   `party`/`guild`/`whisper`/`world`) for a duration and reason the GM tool sets; enforced at the
   chat relay (§4) by checking mute state before accepting a message, the same choke-point pattern
   `70_integrations/ACCOUNTS_AUTH.md` §4.2 uses for "may this connection act as this
   character?" A GM mute outranks every per-channel state above.

**Filter pipeline (seam only).** Every outbound chat message passes through one filter stage before
relay fan-out: profanity/slur matching and the reserved/impersonation checks
`70_integrations/ACCOUNTS_AUTH.md` §5 already applies to character *names* are the same class of
check, reapplied to message *bodies* — this doc fixes that the seam exists at the relay (§4), not
the wordlist or match rules, which stay a live-ops policy per that doc's precedent.

## 3. Per-system attachment to the social-services tier

Each system lands on the **social services** component `70_integrations/BACKEND_ARCHITECTURE.md`
§1/§7 fixes (one relay/state tier scaling independently of world nodes); this section fixes each
system's **process/service shape**, **state store**, **cross-channel/cross-map reach**, and
**failure mode**, conforming to that doc's §7 table, §3 storage-technology table, and §8
degradation-stance table respectively.

### 3.1 CHAT — stateless relay

- **Process shape.** A stateless relay service on the social tier — it holds no durable state of
  its own beyond the rate-limit/mute cache (§2, §5's presence store). A message is: authenticate
  sender → resolve channel roster (party/guild membership come from those services' live state,
  §3.2/§3.3; `normal` roster is "everyone on this map process," sourced from the world node, not
  the social tier) → rate-limit/mute check (§2) → filter pipeline (§2) → fan-out to resolved
  recipients' gateway connections.
- **State store.** None durable by default — chat is fire-and-forget per
  `10_systems/social/CHAT.md`'s "client-side scrollback log" (client-held, not server-persisted).
  The one exception is the report-flow queue (§2), which should be durable on the social/market DB
  — schema pending in `70_integrations/DATABASE_PERSISTENCE.md` (Open Questions). Whether `party`/`guild`
  history persists across relogin is `10_systems/social/CHAT.md`'s own open question — this doc
  does not resolve it; if resolved yes, that history's store is `70_integrations/DATABASE_PERSISTENCE.md`'s
  to schema.
- **Cross-channel/cross-map reach.** `normal` never crosses a map process (§1); `party`/`guild`/
  `whisper`/`world` (proposed) all cross maps and population channels, resolved via presence (§5)
  and roster lookups against `PARTY`/`GUILD` service state, conforming to
  `70_integrations/WORLD_CHANNELS.md`'s cross-channel state section.
  `speech bubbles` render only on `normal`, entirely client-side once the message is delivered.
- **Failure mode.** Chat-relay outage degrades chat to unavailable; it never blocks combat,
  movement, or a wallet/inventory action — chat carries no `server`-truth game state
  (`10_systems/social/CHAT.md` — message content is `authority: server` only in the sense that the
  server is the sole *relay* authority, not because losing it corrupts anything durable), consistent
  with `70_integrations/BACKEND_ARCHITECTURE.md` §8's social/market DB stance ("core solo-style
  play... is unaffected"). A dropped relay reconnects the same way the gateway reconnect-grace
  window does (`70_integrations/ACCOUNTS_AUTH.md` §4) — in-flight messages during the gap are lost,
  never duplicated or replayed.

### 3.2 PARTY — roster + reward-arbitration service

- **Process shape.** A stateful service on the social tier holding one live roster process per
  active party (membership, join order, leader, loot mode — `10_systems/social/PARTY.md` §1–§2,
  §5) plus the reward-arbitration logic that computes exp/loot splits per that doc's §4–§5 formulas
  on each qualifying kill event (the world node emits the kill event; this service performs the
  arbitration — the math itself stays `10_systems/social/PARTY.md`'s, this doc only places where
  it executes). Party-instance bookkeeping (§6 of that doc — fallen-but-not-Released members,
  N-fixed-at-creation) is tracked by the same per-party process for the instance's lifetime.
- **State store.** Ephemeral, authoritative-but-not-durable: roster membership, loot mode, and
  rotation counters live in the social tier's ETS/Redis state and are **never written to Postgres**
  — `70_integrations/DATABASE_PERSISTENCE.md` §3.3 owns this classification (a party has no durable
  table; it is ephemeral by design, `10_systems/social/PARTY.md` §1 — a party of 1 auto-disbands).
  Only the wallet/item *results* of arbitration land durably, atomically in the character DB and
  wallet ledger (`70_integrations/BACKEND_ARCHITECTURE.md` §5 authority mapping). raid instance
  lifecycle itself is `10_systems/social/RAID.md` §5's and lands on instance workers, not
  this tier.
- **Cross-channel/cross-map reach.** Party chat (§3.1) and HUD-plate data
  (`10_systems/social/PARTY.md` §3) span every member's map regardless of location; exp/loot
  eligibility itself stays same-map-gated (that doc §4/§5) — the *service* reaches across maps to
  hold the roster, but the *reward rule* it evaluates is map-scoped, and this doc does not blur
  that distinction.
- **Failure mode.** Per `70_integrations/BACKEND_ARCHITECTURE.md` §8's social/market DB row: an
  unreachable party service degrades to read-only or unavailable — no new invites/kicks/loot-mode
  changes — while combat, movement, and quests on the world node continue unaffected. An
  in-flight kill's exp/loot arbitration that cannot reach the party service must **not** silently
  fall back to solo-style full-share (that would fabricate a `server` truth, `10_systems/PERSISTENCE.md`
  §7); it blocks the reward write and retries, matching the audit-log stance
  ("block... rather than roll unverifiably") for anything routed through the seeded RNG service
  (loot rolls, `10_systems/social/PARTY.md` §5).

### 3.3 GUILD — registry service

- **Process shape.** A registry service on the social tier: one durable record per guild (roster,
  ranks, crest data, MOTD — `10_systems/social/GUILD.md` §3, §5, §6), globally name-unique at
  creation (§2 of that doc, same global-namespace pattern as
  `70_integrations/ACCOUNTS_AUTH.md` §5's character names). Unlike `PARTY`, a guild is long-lived
  and its process/record persists whether members are online or not.
- **State store.** Social/market DB (Postgres — the `social` schema,
  `70_integrations/DATABASE_PERSISTENCE.md` §3.3), shared with `MARKET`/`MAIL` durable state and
  the `TRADING` trade log (party state is ephemeral, §3.2); the
  creation fee and roster-expansion/crest-edit fees (`10_systems/social/GUILD.md` §1, §4, §5) write
  through the wallet ledger (Postgres) in the same transaction as the registry write, since a paid
  guild action must never charge `shards` without the registry change landing (or vice versa).
  Concrete schema is `70_integrations/DATABASE_PERSISTENCE.md`'s.
- **Cross-channel/cross-map reach.** Guild chat (§3.1) and roster-derived presence (§5) reach every
  member regardless of map, matching `10_systems/social/GUILD.md` §7's "membership... grants access
  to the `guild` channel" with no location gate.
- **Failure mode.** Per `70_integrations/BACKEND_ARCHITECTURE.md` §8's "read-only or unavailable"
  social stance: registry *writes* (create, invite, rank change, crest edit, MOTD) degrade to
  unavailable, while roster *reads* may stay read-only from cache/replica where available; a
  guild's *existence* and roster are not lost (durable in Postgres, unlike a party's ephemeral
  process) — an outage pauses guild management, it does not corrupt or forget a guild.

### 3.4 TRADING — live two-party escrow session

- **Process shape.** A stateful, per-session escrow process on the social tier, one per active
  trade window (`10_systems/social/TRADING.md` §3's state machine: offer → lock → confirm → atomic
  swap → cancel). The process is the single transaction authority both clients trust (that doc's
  Server Dependency) — neither client executes its own half. Session exclusivity (§5, one active
  session per character) and the 120 s idle auto-cancel are enforced by this process's own timers.
- **State store.** The swap itself is an atomic multi-row Postgres transaction against the
  character DB (inventory) and wallet ledger (`70_integrations/BACKEND_ARCHITECTURE.md` §5 authority
  mapping, §3 "account-to-account transfers... must be atomic"); the trade log
  (`10_systems/social/TRADING.md` §5) persists to the social/market DB as an audit record, separate
  from the transactional swap itself.
- **Cross-channel/cross-map reach.** None by design — `10_systems/social/TRADING.md` §1 requires
  same-map, within-proximity, both characters present; this is the one social system that is
  deliberately **not** cross-map, and this doc does not extend it.
- **Failure mode.** If the escrow process or the wallet-ledger Postgres primary is unreachable at
  Swap, the transaction does not commit and both offers remain exactly where they were pre-swap
  (`10_systems/social/TRADING.md` §3 "nothing is transferred pre-swap" — this doc's failure mode
  is that the same invariant holds under an infrastructure fault, not just a player Cancel). This
  matches `70_integrations/BACKEND_ARCHITECTURE.md` §8's wallet-ledger row: freeze value transfer,
  never accept a half-completed swap.

### 3.5 MARKET — async listings board + escrow

- **Process shape.** An async, world-global listings service on the social tier — not per-session
  like `TRADING`; one shared board every character can browse/search regardless of map or
  population channel (`10_systems/social/MARKET.md`'s "purpose" — "without both being online
  together"). List/browse/buy/delist are independent requests against the shared board, not a
  live paired session.
- **State store.** Listings (`10_systems/social/MARKET.md`'s data sketch — `listing_id`, `seller`,
  `item_ref`, `ask_price`, `status`) persist to the social/market DB; escrowed items leave
  `10_systems/INVENTORY.md` on listing and are server-held (character DB item-ownership row
  transitions to the market escrow, not a separate inventory) until sold/delisted/expired. A buy
  transaction is the same atomic Postgres pattern as `TRADING` (§3.4) — item + `shards` (minus the
  listing fee, whose number's ownership is itself unsettled between `10_systems/ECONOMY.md` and
  `10_systems/social/MARKET.md` — each currently defers to the other; flagged in Open Questions)
  move in one transaction.
- **Cross-channel/cross-map reach.** World-global by definition — the one social system whose
  reach is not roster- or map-scoped at all, conforming to
  `70_integrations/WORLD_CHANNELS.md`'s cross-channel state section for a truly global read surface
  (every character, on any map, any population channel, sees the same board). This is the
  strongest justification for a `world` chat channel (§1) — `MARKET` already has world-global
  reach; a matching world-global *chat* surface is a natural companion, not a new reach model.
- **Failure mode.** Matches `TRADING`'s wallet-ledger stance: an unreachable market service freezes
  new listings/buys/delists; already-escrowed items stay server-held (never returned or duplicated
  speculatively) until the service recovers, per
  `70_integrations/BACKEND_ARCHITECTURE.md` §8's "freeze all `shards` faucets/sinks and
  `MARKET`/`MAIL`/`TRADING` value transfer; combat/movement continue."

### 3.6 MAIL — store-and-forward mailbox + COD

- **Process shape.** A store-and-forward service on the social tier: compose writes a durable mail
  record immediately (no live session with the recipient required, unlike `TRADING`); claim is a
  discrete recipient-initiated action (`10_systems/social/MAIL.md`'s "not proximity auto-loot").
  Unclaimed-mail expiry (returns any attachment to the sender) runs as a scheduled sweep on this
  service, not a per-message timer process — cheaper than `TRADING`'s per-session process shape
  since mail has no live counterpart to coordinate with.
- **State store.** Mail records (`10_systems/social/MAIL.md`'s data sketch — `mail_id`, `sender`,
  `recipient`, `attachment`, `shards_attached`, `cod_amount`) persist to the social/market DB;
  compose's flat send fee (`10_systems/ECONOMY.md` sink) and claim's item/`shards`/COD transfer are
  each an atomic Postgres transaction against the character DB and wallet ledger, same pattern as
  §3.4/§3.5. Whether `MARKET` proceeds route through `MAIL` is flagged unresolved by both stubs
  (`10_systems/social/MARKET.md`, `10_systems/social/MAIL.md`) — this doc supports either routing
  (both write through the same ledger transaction) without deciding it (Open Questions).
- **Cross-channel/cross-map reach.** World-global for delivery (a mailbox has no map scope — the
  recipient claims from anywhere), matching `MARKET`'s reach model (§3.5) more than `TRADING`'s
  proximity model (§3.4).
- **Failure mode.** Same wallet-ledger freeze stance as §3.4/§3.5 for compose/claim; an
  already-composed, already-escrowed mail item is never lost or duplicated by an outage — it stays
  server-held pending claim or expiry-return, matching `10_systems/social/MAIL.md`'s own "never
  destroyed" invariant (`00_vision/PILLARS.md` P2) under an infrastructure fault as well as the
  ordinary expiry path.

## 4. Chat relay topology (detail)

The chat relay (§3.1) sits on the social-services tier as a set of stateless, horizontally-scaled
relay processes behind the gateway (`70_integrations/BACKEND_ARCHITECTURE.md` §1's "social-service
replica... scales independently of world nodes" scaling unit). A message's path:

```
Client → Gateway (session-authenticated, §5 presence) → Chat relay
    → [mute check (§2)] → [rate-limit check (§2)] → [filter pipeline (§2)]
    → roster resolution (party/guild service lookup, §3.2/§3.3, or same-map world-node query for `normal`)
    → fan-out to each resolved recipient's live gateway connection
```

Every hop after "Gateway" runs on the social tier; the world node is consulted read-only for
`normal`'s map roster and is never blocked waiting on chat fan-out (chat fan-out failure never
backs up combat simulation — `70_integrations/BACKEND_ARCHITECTURE.md` §1's "a market surge never
starves combat sim" invariant applies identically to a chat surge). Packet shape for each hop
(client→gateway, gateway→relay, relay→recipient) is `70_integrations/NETWORK_PROTOCOL.md`'s to
define — this section fixes only the hop sequence and where each check runs.

## 5. Presence

`70_integrations/BACKEND_ARCHITECTURE.md` §3 fixes presence's storage technology (Redis for
cross-node coordination, BEAM-native ETS/Phoenix.Presence for in-node ephemeral state); this doc
owns the **semantics** — staleness and fan-out scope — layered on top.

- **Who sees online/offline.** This doc **proposes** a per-member online/offline indicator on the
  existing party roster surface (`10_systems/social/PARTY.md` §3's HUD-plate data contract) and
  guild panel (`10_systems/social/GUILD.md` §6/§7) — neither owner doc defines one today, so the
  field is flagged to their Open Questions for adoption (same pattern as the `world` channel
  proposal, §1). Whatever surfaces it, the source is this one presence layer, scoped by each
  service's roster (§3.2/§3.3), never a world-wide "who's online" list — no system in this tree
  asks for a global online roster, so none is built.
- **Where presence lives.** Phoenix.Presence, backed by BEAM-native ETS for in-node state and Redis
  for cross-node fan-out, per `70_integrations/BACKEND_ARCHITECTURE.md` §3 — this doc does not
  choose a different technology, only how it is read.
- **Staleness.** Presence is **eventually consistent, not instantaneous**: a disconnect is detected
  by the gateway's connection-drop signal and propagates to party/guild presence subscribers within
  a bounded window (target: sub-second in-node via ETS/Phoenix.Presence; cross-node fan-out via
  Redis trails slightly behind, consistent with
  `70_integrations/BACKEND_ARCHITECTURE.md` §8's "cross-node coordination... may lag until it
  recovers" Redis degradation stance). A dropped connection during the reconnect-grace window
  (`70_integrations/ACCOUNTS_AUTH.md` §4) shows as online-but-unreachable rather than flipping
  immediately to offline — this mirrors the grace window's own intent (a network blip is not a
  logout) and avoids a roster flapping online/offline on a transient hiccup. During that window a
  `whisper` to the character checks **reachability** (a live gateway connection), not roster
  presence: with no live connection to fan out to, the sender gets the same clear "recipient
  offline" result (§1) rather than a silent drop — the message is not queued (offline delivery is
  `MAIL`'s job, §3.6). Once the grace window
  lapses without reconnect, presence flips to offline and fan-out fires to every subscribed roster.
- **Fan-out scope.** A presence change fans out only to rosters the character is actually a member
  of at that instant (their current party, if any; their guild, if any) — never broadcast tier-wide.
  This bounds presence fan-out cost the same way `party`/`guild` chat channels are already
  roster-bounded (§1) rather than world-broadcast, and it is why a `world`-channel presence feed is
  explicitly **not** proposed alongside the `world` chat channel (§1) — no system in this tree needs
  it, and it would be the single most expensive fan-out this doc could add.
- **Whisper's presence use.** `whisper` (§1) requires the recipient to be online (no offline
  whisper path — `10_systems/social/MAIL.md` covers the offline case); the chat relay checks
  presence before attempting fan-out and returns a clear "recipient offline" result rather than
  silently dropping the message.

## Open Questions

- **`world` channel promotion.** §1 proposes a `world` chat channel as this doc's engineering
  addition because `10_systems/social/CHAT.md` currently defines only `normal`/`party`/`guild`/
  `whisper`; whether to adopt it (and its 1-msg/60s limit, §2) is that doc's and
  `00_vision/GLOSSARY.md`'s call, not decided here. If rejected, `MARKET`'s world-global reach (§3.5)
  stands without a matching chat surface.
- **Rate-limit and escalation-ladder thresholds (§2)** are first-pass engineering numbers, explicitly
  not balance content; retune once live-server telemetry exists, the same stance
  `10_systems/social/TRADING.md` §5 and `10_systems/social/CHAT.md`'s own Open Questions take on
  their first-pass numbers.
- **Whether `party`/`guild` chat history persists across relogin** is `10_systems/social/CHAT.md`'s
  open item (§3.1); if resolved yes, its store is `70_integrations/DATABASE_PERSISTENCE.md`'s to
  schema — flagged forward, not decided here.
- **`MARKET` proceeds: wallet credit vs. `MAIL` delivery** remains unresolved in both stubs
  (`10_systems/social/MARKET.md`, `10_systems/social/MAIL.md`); §3.6 confirms this doc's topology
  supports either routing without forcing the choice.
- **Report-queue triage/staffing** (§2's report flow) is a live-ops operational question — who
  reviews the queue, SLA, and tooling — not a backend-topology decision; flagged for an ops runbook
  this run does not produce. Separately, the queue's **durable schema is pending**:
  `70_integrations/DATABASE_PERSISTENCE.md` §3.3's `social` schema does not yet define a
  report/moderation table — flagged to that doc to add one on its next pass.
- **Market listing-fee ownership** (§3.5) is circular today: `10_systems/ECONOMY.md`'s sink table
  points at `10_systems/social/MARKET.md` as the number's future owner, while MARKET remains a stub
  deferring to the social-doc pass — the two docs must settle which one owns the fee number when
  MARKET promotes out of stub status; this doc only routes the fee through the wallet ledger.
- **Filter-pipeline wordlist and match rules (§2)** stay `70_integrations/ACCOUNTS_AUTH.md` §5's
  precedent: live-ops policy applied server-side, deliberately not authored in this design tree.
