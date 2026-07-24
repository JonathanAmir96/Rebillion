# BACKEND_SECURITY.md — Server Anti-Cheat & Data Integrity

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/PERSISTENCE.md, 10_systems/STATS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/DROPS.md, 10_systems/INVENTORY.md, 10_systems/ENHANCEMENT.md, 10_systems/ECONOMY.md,
10_systems/QUESTS.md, 10_systems/SPAWN.md, 10_systems/AI_BEHAVIOR.md,
10_systems/social/TRADING.md, 10_systems/social/MARKET.md, 10_systems/social/MAIL.md,
10_systems/social/PARTY.md, 10_systems/social/GUILD.md, 10_systems/social/CHAT.md,
15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_TRAVERSAL.md,
15_maps_system/MAP_CONNECTIONS.md, 40_assets/ANIMATION_STATES.md,
30_engineering/ENGINEERING_STANDARDS.md,
30_engineering/BACKEND_PERFORMANCE.md, docs/VALIDATION.md, docs/ID_REGISTRY.md

Owner doc for the **live server's anti-cheat and data-integrity rules**: how the server
validates movement, authorizes combat, scopes visibility, and guarantees that no sequence of
client packets, crashes, or concurrent requests can mint, duplicate, or corrupt
`authority: server` state. Authored per the **owner's backend security checklist
(orchestrator instruction, 2026-07-24)**, which opens the backend *design* pass;
`00_vision/SCOPE.md` still excludes backend *implementation* from this run.

This doc owns the **enforcement architecture only**. What is server-owned is
`10_systems/PERSISTENCE.md` §1–§2 (the authority taxonomy — not restated here); each gameplay
rule stays in its owning system doc and is cited, never copied. Companion doc:
`30_engineering/BACKEND_PERFORMANCE.md` (tick, rooms, spatial grid, database throughput).

## 0. Doctrine — never trust the client

The client is a **rendering and input device**. Every byte it sends is treated as potentially
malicious until validated; the backend is the sole source of truth for every
`authority: server` field and the reconciler for every `authority: shared` field
(`10_systems/PERSISTENCE.md` §1). This is the live-server hardening of the boundary the solo
build already rehearses: the `10_systems/PERSISTENCE.md` §7 "never trusted from the client"
list is enforced by the `GameState` facade today and by this doc's server tomorrow — same
contract, same code path (`00_vision/PILLARS.md` P6).

**Reference stack (owner-directed, 2026-07-24; swappable without changing any rule here):**
a Node.js room-server layer (Colyseus-style, one room per `map_NNN` —
`30_engineering/BACKEND_PERFORMANCE.md` §4), PostgreSQL via Supabase as the persistent truth
ledger, Redis as the read cache (`30_engineering/BACKEND_PERFORMANCE.md` §8).

## 1. Movement validation & reconciliation (`authority: shared`)

Resolves the reconciliation algorithm `10_systems/PERSISTENCE.md` §4 deferred.

- **The server simulates movement itself.** It maintains the authoritative position, velocity,
  and locomotion state (`idle`/`walk`/`jump`/`fall`/`climb`, the movement subset of
  `40_assets/ANIMATION_STATES.md`) of every player and monster in the room. Clients send
  **inputs** (and their predicted position for reconciliation), never a bare "I am now here."
- **Simulation runs on the server-side collision map**: the same foothold graph, climbable
  volumes, one-way platforms, hazards, and movement constants that
  `15_maps_system/MAP_TRAVERSAL.md` fixes for the client. One movement model, two hosts —
  divergence between the two is a build error, not a tuning knob.
- **Tolerance + snap.** Each tick the server compares the client's predicted position with its
  own result. Within `reconcile_tolerance`, the client's value is accepted (lag/jitter grace);
  beyond it, the server **snaps** the client to the authoritative position in its next state
  packet, and the discrepancy is counted as a violation strike (§8). The concrete tolerance
  value is tile-scale-dependent and lands with the coding pass (Open Questions).
- **Velocity cap.** Independent of path validation, the server hard-rejects any per-tick
  displacement exceeding the fastest legal mover for the entity's state: `run_speed` /
  `climb_speed` and jump/gravity envelope (`15_maps_system/MAP_TRAVERSAL.md` §1), scaled by
  the entity's server-held `haste` (soft-capped per `10_systems/STATS.md` §6), plus the
  displacement ops a skill may legally grant (`dash`/`leap`/`knockback`/`pull`,
  `10_systems/SKILL_EFFECTS.md`) — times a small safety factor for tick aliasing. Teleport-type
  transitions exist only as server-initiated portal/`coach` moves
  (`15_maps_system/MAP_CONNECTIONS.md`); there is no client packet that names a destination
  position.

## 2. Combat & skill authorization (`authority: server`)

- **Clients declare intent, never outcome**: the only legal combat packet is "use skill S with
  aim/target T." The server validates, in order: the character actually owns S at a rank ≥ 1
  (`10_systems/SKILL_SYSTEM.md` §2), cooldown elapsed and `essence_cost` payable (§5),
  cast/recovery window respected (§5), and the target lies inside S's declared targeting shape
  and range (§6) *as measured against server-held positions* (§1) — not client-reported ones.
  A target outside the attacker's area of interest (§3) is invalid by construction.
- **All resolution math runs server-side**: hit check, crit, variance, mitigation, element and
  status multipliers — the `CombatMath` contract of `10_systems/COMBAT_FORMULA.md` §1–§2,
  fed by **authoritative stat blocks recomputed from the database-held base values**
  (`10_systems/STATS.md` §7–§8), never by client-submitted stats.
- **All randomness is server randomness**: the single seeded RNG service
  (`30_engineering/ENGINEERING_STANDARDS.md`) lives server-side once live — combat rolls, drop
  rolls (`10_systems/DROPS.md` §9), and enhancement attempts (`10_systems/ENHANCEMENT.md` §6)
  cannot be re-rolled by replaying packets (§5 idempotency).
- The server applies the resulting `life`/status changes to its own state
  (`10_systems/STATUS_EFFECTS.md` §5), then **broadcasts the outcome** to every client whose
  area of interest (§3) contains the participants.

## 3. Visibility — area-of-interest replication

The server sends a client position/combat/entity data **only for entities inside that
player's area of interest**: the viewport (render base ≈ 40×22.5 tiles,
`15_maps_system/MAPS_SYSTEM.md`) plus one buffer screen, resolved via the room's spatial grid
(`30_engineering/BACKEND_PERFORMANCE.md` §5). Entities outside it are simply never serialized
to that connection — a modified client cannot render what it was never sent. This is the
defense against map-hack/radar tooling, and it doubles as the §2 range gate and a bandwidth
bound. Loot visibility additionally respects drop tagging/ownership windows
(`10_systems/DROPS.md` §7): an unowned-phase check happens server-side before a drop is
replicated as interactable.

## 4. Transactional integrity — ACID for every ledger mutation

Every mutation of `authority: server` persistent state (the `10_systems/PERSISTENCE.md` §2
table: inventory tabs, bank, equipment, `enhance_level`, `shards` wallet, quest flags, skill
ranks, `exp`/`level`, market/mail/trade/guild records) executes inside a **single database
transaction** (`BEGIN … COMMIT`) with rollback on any failure — crash, disconnect, or logic
error mid-operation leaves the ledger exactly as it was.

Multi-party operations are **one atomic transaction, never a choreography of halves**:

| Operation | Atomic unit | Rule owner |
|---|---|---|
| Direct trade swap | both offers (items + `shards`) change hands together or not at all | `10_systems/social/TRADING.md` §3 |
| Market list / buy / delist | escrow out of seller inventory · price+fee out of buyer, item in, proceeds credited | `10_systems/social/MARKET.md` |
| Mail with attachment | attachment escrow on send; item+message delivered or neither | `10_systems/social/MAIL.md` |
| Enhancement attempt | fee + emberstone consumed ⟷ result applied, one unit | `10_systems/ENHANCEMENT.md` §5–§6 |
| Vendor buy/sell, coach fare, guild fees | wallet delta + item/state delta together | `10_systems/ECONOMY.md` §2/§4 |
| Loot pickup | ownership check + inventory insert + world-drop removal | `10_systems/DROPS.md` §7, `10_systems/INVENTORY.md` §4–§5 |

The "no partial state is ever visible" promise `10_systems/social/TRADING.md` §3 already makes
is *implemented* by this rule; that doc keeps owning the escrow UX and limits.

## 5. Concurrency — row-level locking & idempotency (anti-dupe)

- Inside a §4 transaction, the server acquires **row-level locks** (`SELECT … FOR UPDATE`) on
  every character/inventory/wallet row it will modify **before** reading the values it
  validates against — no check-then-act windows. Two simultaneous attempts to move the same
  item (double-click, two devices, trade racing a market listing) serialize; the second sees
  the item already gone and fails cleanly. This is the structural defense against duplication
  exploits.
- **Deterministic lock ordering** (e.g., ascending character row key, then item row key)
  across all code paths, so cross-locking transactions cannot deadlock.
- **Idempotency**: every state-mutating client packet carries a client-generated request ID;
  the server stores the outcome and replays it (rather than re-executing) on retransmit.
  A dropped ACK can therefore never double-apply a purchase, pickup, or enhancement attempt.
- One in-flight session rule per exclusive context — one trade session per character
  (`10_systems/social/TRADING.md` §1/§5), one active enhancement dialog, etc. — enforced
  server-side, not by UI state.

## 6. Transport security

- All realtime client↔server traffic runs over **encrypted WebSocket (WSS/TLS)**; there is no
  plaintext listener in any environment, including dev (fail loud —
  `30_engineering/ENGINEERING_STANDARDS.md` directive 7).
- All server↔database (Supabase/PostgreSQL) and server↔cache connections use **TLS**.
- Clients hold **no database credentials of any kind**: the game client never talks to the
  database directly — only to the room server, which holds the service credential. Any
  client-exposed database path (e.g., Supabase row-level-security anon access) is disabled
  for gameplay tables.
- Session authentication: a connection is bound to one authenticated account before any
  gameplay packet is accepted; the account/auth system itself is still the open item
  `10_systems/PERSISTENCE.md` §2 marks "(future account system)" (Open Questions).

## 7. Rate limiting & input validation

- **Per-connection packet budgets**, enforced per channel class (movement input, action
  intents, social/chat, meta/queries) per second, with a small burst allowance. Exceeding a
  budget drops packets; sustained flooding **drops the connection** and counts a strike (§8).
  HTTP endpoints (auth, account) carry equivalent per-IP/per-account limits. Concrete budget
  numbers are tick-rate-coupled and land with the coding pass (Open Questions).
- Gameplay-level ceilings already owned elsewhere stay there and stack on top: trade cooldown
  and hourly volume ceiling (`10_systems/social/TRADING.md` §5), chat spam limits
  (`10_systems/social/CHAT.md`, open), invite-decline timeouts
  (`10_systems/social/PARTY.md` §2).
- **Every packet is schema-validated before any handler runs**: expected message type, field
  presence, data types, lengths (strings/arrays), numeric ranges, and enum membership against
  the owning registries (`00_vision/GLOSSARY.md` tokens; IDs must parse and fall inside their
  `docs/ID_REGISTRY.md` blocks). Malformed input is rejected and logged, never coerced — the
  runtime mirror of `docs/VALIDATION.md`'s build-time checks.
- **Parameterized statements only** for every database query (prepared statements /
  parameterized query API); string-concatenated SQL is forbidden repo-wide. Free-text fields
  (chat bodies, guild names/MOTD per `10_systems/social/GUILD.md` §2/§6) are length-bounded,
  encoding-validated, and stored inert — rendered as text, never interpreted.

## 8. Audit trail & sanctions

- Server-side append-only logs for anti-fraud review: completed trades (owned by
  `10_systems/social/TRADING.md` §5), market transactions, mail attachments, enhancement
  attempts, and violation strikes (§1 movement snaps beyond tolerance, §5 idempotency
  replays, §7 flood/malformed-packet rejections).
- Strikes escalate: silent correction → disconnect → account flagged for human review.
  Automated permanent sanctions are **not** designed here; thresholds and policy are a
  live-ops decision (Open Questions).

## 9. Requirement coverage (owner checklist, 2026-07-24)

| Checklist requirement | Owned by |
|---|---|
| Server-side movement validation; snap on discrepancy | §1 |
| Velocity capping per tick | §1 |
| Server-side damage calculation; cooldown/resource/target checks | §2 |
| Visibility / area-of-interest checks | §3 (+ `30_engineering/BACKEND_PERFORMANCE.md` §5) |
| Database transactional safety (ACID, atomic trades) | §4 |
| Atomic row-level locking (anti-dupe) | §5 |
| Encrypted WebSocket (WSS) and TLS | §6 |
| Rate limiting & throttling | §7 |
| Strict input validation; prepared statements | §7 |

## Open Questions

- Concrete numbers — `reconcile_tolerance`, per-state velocity-cap table (with the tick-alias
  safety factor), per-channel packet budgets, and idempotency-record retention — are
  coding-pass values, dependent on the tile-scale lock (`40_assets/ART_BIBLE.yaml`) and the
  tick rate (`30_engineering/BACKEND_PERFORMANCE.md` §1). First-pass values land with the
  server prototype, owner this doc.
- Sanctions policy (§8): strike thresholds, review tooling, and appeal flow are live-ops
  design, not authored here.
- Account/auth design (§6) is still unowned — `10_systems/PERSISTENCE.md` §2's "(future
  account system)"; whether Supabase Auth is the provider is a stack call for the coding pass.
- The offline→online import validation pass (`10_systems/PERSISTENCE.md` §9 + its Open
  Questions) should reuse this doc's §7 validation machinery (range/ID/enum checks) — joint
  owner with `10_systems/PERSISTENCE.md`, still undecided there.
- Whether the interim solo build's `GameState` facade should also emulate §5 idempotency and
  §7 budgets locally (beyond the `10_systems/PERSISTENCE.md` §7 list it already enforces) —
  default **no**, they are transport-layer concerns with no local attacker.
- Monster/AI authority is assumed fully server-side once live (`10_systems/AI_BEHAVIOR.md`
  profiles run in the room process; `10_systems/SPAWN.md` timers server-held) — stated here as
  the default, but those docs were written host-agnostic and should be confirmed at the
  backend coding pass.
