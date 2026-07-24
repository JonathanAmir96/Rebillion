# BACKEND_PERFORMANCE.md — Server Scalability & Low Latency

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/PERSISTENCE.md, 10_systems/COMBAT_FORMULA.md, 10_systems/SKILL_SYSTEM.md,
10_systems/STATUS_EFFECTS.md, 10_systems/DROPS.md, 10_systems/SPAWN.md,
10_systems/AI_BEHAVIOR.md, 10_systems/INVENTORY.md, 10_systems/CONTROLS.md,
10_systems/social/MARKET.md, 10_systems/social/MAIL.md, 10_systems/social/PARTY.md,
10_systems/social/TRADING.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_TRAVERSAL.md,
15_maps_system/MAP_CONNECTIONS.md, 30_engineering/ENGINEERING_STANDARDS.md,
30_engineering/BACKEND_SECURITY.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the **live server's performance architecture**: tick model, wire format, room
topology, spatial partitioning, and database throughput. Authored per the **owner's backend
performance checklist (orchestrator instruction, 2026-07-24)**; `00_vision/SCOPE.md` still
excludes backend *implementation* from this run. Companion doc:
`30_engineering/BACKEND_SECURITY.md` (validation, transactions, transport security — its §0
reference stack applies here too). Design targets: **< 50 ms processing per tick** at the P99,
horizontal scale-out by room, no O(N²) entity loops.

## 1. Tick model

- **Server tick rate: 20 Hz first-pass** (50 ms budget per tick), the middle of the 15–30 Hz
  band appropriate for a 2D side-scroller — snappy enough for the P1 combat feel
  (`00_vision/PILLARS.md`) without doubling CPU for imperceptible gains. Not set higher
  without telemetry (§9) proving headroom; may drop toward 15 Hz for low-population field
  rooms if profiling justifies it (Open Questions).
- Each room tick runs: input intake → movement simulation + reconciliation
  (`30_engineering/BACKEND_SECURITY.md` §1) → AI/spawn/status timers
  (`10_systems/AI_BEHAVIOR.md`, `10_systems/SPAWN.md`, `10_systems/STATUS_EFFECTS.md`) →
  combat resolution (`10_systems/COMBAT_FORMULA.md`) → interest-scoped state broadcast (§3).
- Client-facing cadences stay decoupled from persistence: ledger writes (`exp`, drops,
  `shards`) batch asynchronously off the tick path — a tick never blocks on the database
  (§6–§8 make that budget hold).

## 2. Wire format — binary serialization

- High-frequency state packets (positions, `life`/`essence` deltas, combat results, status
  ticks) use a **compact binary schema format** (Protobuf/MsgPack-class, or the room
  framework's native binary schema) — **never JSON**: JSON's size and encode/decode cost are
  spent thousands of times per second on the hot path.
- Field IDs/enums ride as integers mapped from GLOSSARY tokens at build time (the same
  token→`const`/`StringName` discipline `30_engineering/ENGINEERING_STANDARDS.md` fixes
  client-side); the wire schema is generated, not hand-maintained, so client and server cannot
  drift.
- JSON remains acceptable for low-frequency, non-tick traffic (auth handshakes, market/browse
  queries, mail bodies) where readability outweighs bytes.

## 3. Delta compression

- The server does **not** resend full room state every tick. Per connection, it tracks the
  last acknowledged state and sends only **changes since that ack**: entities that moved,
  stat values that changed, entities entering/leaving the client's area of interest
  (`30_engineering/BACKEND_SECURITY.md` §3).
- Full snapshots occur only on room join, area-of-interest cell entry, and desync recovery
  (including the §1-triggered snap of `30_engineering/BACKEND_SECURITY.md`).
- Idle entities cost zero bandwidth: an unchanged monster serializes to nothing.

## 4. Room topology — one room per map

- The world is **never one process**. Each `map_NNN` (200 maps, `docs/WORLD_PLAN.md` /
  `docs/ID_REGISTRY.md`) is a discrete **room**: its own tick loop, entity set, spawn zones
  (`10_systems/SPAWN.md` §1), and lifecycle. Portals/`coach`/ferry travel
  (`15_maps_system/MAP_CONNECTIONS.md`) are room hand-offs through the persistence layer, not
  in-process moves.
- Rooms are the **horizontal-scaling unit**: they distribute freely across processes and
  hosts; a hot hunting map never degrades a town on another core. Empty field/dungeon rooms
  hibernate (state parked, tick stopped) and wake on first entry.
- Instanced contexts — boss arenas (`15_maps_system/MAPS_SYSTEM.md` §8) and the two party
  quests (`pq_undervault`/`pq_mainspring`, `10_systems/social/PARTY.md`) — spawn as additional
  room instances of the same map, one per party, disposed on completion.

## 5. Spatial partitioning — per-room grid

- Within a room, entities index into a **uniform spatial grid**; the cell size is one render
  screen (≈ 40×22.5 tiles, `15_maps_system/MAPS_SYSTEM.md`), so a player's area of interest
  (`30_engineering/BACKEND_SECURITY.md` §3) is exactly the 3×3 cell neighborhood around them.
- All proximity queries run against the grid — interest replication (§3), skill target-shape
  checks (`10_systems/SKILL_SYSTEM.md` §6), aggro scans (`10_systems/AI_BEHAVIOR.md`), loot
  pickup radius (`10_systems/INVENTORY.md` §4) — turning per-player entity scans from
  O(entities-in-room) into O(entities-nearby). No system may iterate the full room entity list
  per player per tick.
- A uniform grid (not a quadtree) is the deliberate choice: side-scroller maps are shallow,
  wide, and foothold-banded (`15_maps_system/MAP_TRAVERSAL.md`), so fixed cells beat tree
  rebalancing. Revisit only with §9 evidence.

## 6. Database indexing

Every frequently queried column carries a PostgreSQL index, reviewed whenever a schema lands.
First-pass index set (concrete DDL is coding-pass work):

| Table (working shape) | Indexed columns | Serving |
|---|---|---|
| accounts | unique: account id, email, username (lookup at login) | auth (`30_engineering/BACKEND_SECURITY.md` §6) |
| characters | account id; unique: character name; current `map_NNN` (roster/handoff queries) | login roster, room hand-offs (§4) |
| inventory / bank rows | character id (+ tab), item ID | every §4-`30_engineering/BACKEND_SECURITY.md` transaction |
| market listings | status + item category/slot/`rarity`/price (browse filters, `10_systems/social/MARKET.md`); seller id | market search without full scans |
| mail | recipient id + unread flag | mailbox badge/fetch (`10_systems/social/MAIL.md`) |
| trade/audit logs | character id, timestamp | anti-fraud review (`30_engineering/BACKEND_SECURITY.md` §8) |
| quest progress | character id (+ quest ID) | login load, turn-in checks |

Static *content* (item/skill/monster definitions) is *not* served from these tables at
runtime — it ships with the server build or sits in cache (§8), so it needs no hot index.

## 7. Connection pooling

- The room layer talks to PostgreSQL through a **connection pool** (the Node.js driver's pool
  / Supabase's pooler) — never one connection per query, and never one per player. Pool size
  is bounded per server process; rooms share it.
- Transactions (`30_engineering/BACKEND_SECURITY.md` §4) hold a pooled connection only for
  their own duration; nothing holds a connection across a tick boundary or while awaiting
  client input (a trade session waiting on a Confirm holds **no** database resources — the
  transaction begins only at the swap).

## 8. Caching — static data never re-queried

- All design-time content — item/skill/monster/map/drop-table/spawn data compiled from
  `50_content/*` — is **immutable at runtime** (`30_engineering/ENGINEERING_STANDARDS.md`
  data layer). The server loads it once per process (in-memory, the server-side twin of the
  client's `Database` autoload) and/or serves it from **Redis** when many processes share a
  host tier; it is never fetched from PostgreSQL on a gameplay path.
- Redis additionally fronts read-heavy, slow-changing *live* data: market browse pages
  (short TTL), guild rosters/crests, presence. Anything transactional (§4 of
  `30_engineering/BACKEND_SECURITY.md`) reads its truth from PostgreSQL inside the
  transaction — the cache is never the ledger.
- Cache invalidation is event-driven off the owning mutation (listing sold → page dirty), not
  TTL-only, for anything a player would notice going stale.

## 9. Telemetry & APM — measure before optimizing

The backend ships with integrated application performance monitoring from the first
prototype; every target in this doc is a **measured** number, not an assumed one:

| Metric | Percentiles / form |
|---|---|
| Tick processing time, per room class (town/field/arena) | P50 / P95 / P99 vs the 50 ms budget |
| Database query + transaction latency | P95 / P99, per statement family |
| WebSocket message throughput + payload size | per connection and per room |
| Memory + entity counts | per room and per process |
| Concurrent connections (CCU), room counts, pool saturation | gauges + alert thresholds |
| Violation strikes / rate-limit drops | counters (feeds `30_engineering/BACKEND_SECURITY.md` §8) |

Alerting on P99 tick > budget and pool exhaustion; load tests replay recorded input traces
against target CCU before capacity decisions.

## 10. Requirement coverage (owner checklist, 2026-07-24)

| Checklist requirement | Owned by |
|---|---|
| Binary serialization (no JSON on hot path) | §2 |
| Delta compression | §3 |
| Tick rate balanced (15–30 Hz band) | §1 |
| Room instancing per map | §4 |
| Spatial partitioning (grid) | §5 |
| Indexing strategy | §6 |
| Connection pooling | §7 |
| Redis/in-memory caching of static data | §8 |
| Telemetry & APM percentiles | §9 |

## Open Questions

- 20 Hz (§1) is first-pass; confirm against §9 telemetry and the client's feel targets
  (`10_systems/COMBAT_FORMULA.md` cadence, `10_systems/CONTROLS.md` buffer windows) at the
  backend coding pass. Per-room-class variable tick (towns lower) is floated, not designed.
- Concrete wire-schema tooling (Protobuf vs MsgPack vs framework-native) is a coding-pass
  stack call under `30_engineering/BACKEND_SECURITY.md` §0's swappable-stack rule.
- Room capacity ceiling per map (max players before a field map needs parallel channel-split
  instances of the same map) is not designed — no CCU target exists yet; flag when live-ops
  sets one.
- The §6 table sketches working shapes only; real table/index DDL is Phase-later engineering
  work and must be re-derived from the landed `20_schemas/*` docs, not from this sketch.
- Whether persistence batching (§1) needs a write-ahead journal in Redis (crash window between
  ledger-relevant events and their PostgreSQL commit — e.g., a drop picked up moments before a
  room-process crash) — transactional events are safe (`30_engineering/BACKEND_SECURITY.md`
  §4), but tick-batched `exp` trickle could lose seconds; acceptable-loss window undecided.
- Cross-room global services (chat whisper routing, guild presence, market) are assumed to be
  ordinary services beside the room layer; their process topology is not designed here.
