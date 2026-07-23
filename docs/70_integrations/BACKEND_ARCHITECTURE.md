# BACKEND_ARCHITECTURE.md — Live-Server Topology Contract

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 10_systems/PERSISTENCE.md,
30_engineering/ENGINEERING_STANDARDS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/SPAWN.md,
10_systems/ECONOMY.md, 10_systems/social/PARTY.md, 10_systems/social/CHAT.md,
10_systems/social/GUILD.md, 10_systems/social/MAIL.md, 10_systems/social/MARKET.md,
10_systems/social/TRADING.md, 10_systems/social/PARTY_QUEST.md, 15_maps_system/MAPS_SYSTEM.md,
docs/WORLD_PLAN.md,
70_integrations/ACCOUNTS_AUTH.md, 70_integrations/GAMEPLAY_SIMULATION.md,
70_integrations/NETWORK_PROTOCOL.md, 70_integrations/WORLD_CHANNELS.md,
70_integrations/CHAT_SOCIAL_BACKEND.md, 70_integrations/DATABASE_PERSISTENCE.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

The **authoritative topology contract** for the live, networked build. This doc is written first
in the backend wave and gated before its six siblings (§9) fan out. It commits to the concrete
server stack (§2), the concrete database technology at the component level (§3), and the topology
(§1) — those are engineering calls made here from best practice, not deferred to the owner. It
satisfies the contract in `10_systems/PERSISTENCE.md`: it maps that doc's authority tags onto
concrete components (§5), it does not re-derive them. It never restates a system's values — combat
math stays `10_systems/COMBAT_FORMULA.md`'s, spawn timing stays `10_systems/SPAWN.md`'s, `shards`
balance stays `10_systems/ECONOMY.md`'s. Schema detail, tick rates, wire protocol, channel capacity,
auth flows, and chat internals are each a named sibling's (§9). **Implemented when:** the interim
solo build has shipped and the owner greenlights a live server; nothing here blocks or precedes the
solo build (`00_vision/SCOPE.md` puts networking/backend out of this run's scope).

## 1. Topology

**Channel model — chosen: single logical world + population channels + true instances.** One
authoritative economy/identity namespace (one `shards` wallet space, one `MARKET`/`MAIL`/`GUILD`
registry) with classic side-scroller **population channels** layered only over shared social maps
(towns, popular fields), plus **true instances** for arena and party-quest content.

Justification: `MARKET`, `MAIL`, and `TRADING` are account-to-account transfers of `server`-owned
items and `shards`; splitting the world into independent parallel worlds would fragment that ledger
and force cross-world reconciliation the design never asks for. A single logical world keeps one truth
ledger (`10_systems/PERSISTENCE.md` §2). Population channels are a load/readability valve, not a
separate world: a crowded town map hosts N parallel copies sharing one character DB, so no economy
fork occurs. Party-quest stages/finales are per-party instanced by `10_systems/SPAWN.md` §7 and
`10_systems/social/PARTY_QUEST.md` (`pq_undervault` finale `map_042`, `pq_mainspring` finale
`map_200`), so instance workers are a requirement, not a choice. Open-entry boss arenas are **not**
per-party: `10_systems/SPAWN.md` §3 runs a regional arena as one shared map that resets once empty
(`15_maps_system/MAPS_SYSTEM.md` §8 shared-arena rules), so arenas live as ordinary supervised map
processes on world nodes — only entry through a PQ gate allocates a true instance. This doc fixes the channel-model
**shape**; capacity targets and the per-map channel-count math are `70_integrations/WORLD_CHANNELS.md`'s (§9).

```
        Godot 4.3+ clients ── TLS ──┐
                                    v
                        [ Edge / Gateway ]   Phoenix socket tier: session bind,
                        rate-limit, presence, fan-out  (protocol → NETWORK_PROTOCOL.md)
                          |            |
              [ Auth service ]     [ World routing ]
              accounts, login        |          |
              (ACCOUNTS_AUTH.md)     v          v
                        [ World node(s) ]     [ Instance workers ]
                        BEAM/OTP; one supervised   PQ stage/finale copies, one
                        process per live map/       ephemeral map process per
                        channel: spawner, mob set,  party, spun up on demand and
                        status timers, shared arenas torn down on exit
                          |         |                       |
                          v         v                       v
                        [ Social services ]  chat relay, party, guild, mail, market, trade
                        (CHAT_SOCIAL_BACKEND.md)            |
                          |         |                       |
                          +---------+-----------+-----------+
                                                v
              [ Persistence tier ]  (DATABASE_PERSISTENCE.md maps schema onto this)
              PostgreSQL: character DB · wallet/economy ledger · social/market DB
              append-only log store: seeded-RNG audit log
              Redis + BEAM-native ETS/Presence: session/presence/cooldown/escrow cache
```

- **Auth service** — owns account identity and the login handshake; the only holder of
  credentials (environment-managed, never committed; §10). Issues a short-lived session token the
  gateway trusts. Account/character split, session lifecycle, and name policy are
  `70_integrations/ACCOUNTS_AUTH.md`'s; this doc owns only the component it runs on.
- **Edge / gateway** — the single public endpoint. Terminates TLS, validates the session token,
  rate-limits, holds presence, and routes each authenticated connection to the correct world
  process / channel / instance. Clients never address a world process directly. Transport,
  serialization, and the packet catalog are `70_integrations/NETWORK_PROTOCOL.md`'s (§9).
- **World nodes** — the unit of simulation is the **map** (`10_systems/SPAWN.md` §1). A world node
  hosts a set of maps, each map an independently-supervised process holding its spawn zones, live
  mobs, and active status timers. Population channels are additional map processes inside (or
  across) world nodes.
- **Instance workers** — ephemeral map processes allocated to one party for party-quest stages/
  finales (`10_systems/SPAWN.md` §7). Open-entry boss arenas are not instance-worker content: they
  run as single shared map processes on world nodes under `10_systems/SPAWN.md` §3's
  reset-when-empty rule (`15_maps_system/MAPS_SYSTEM.md` §8). Party size `N` is fixed at instance
  creation — rule owned by `10_systems/SPAWN.md` §7, party bookkeeping by
  `10_systems/social/PARTY.md` §6.
- **Social services** — one relay/state tier hosting the server-deferred systems (§7); internals
  are `70_integrations/CHAT_SOCIAL_BACKEND.md`'s.
- **Persistence tier** — the durable truth ledger, separated by concern so a market outage cannot
  corrupt character saves (§3). Storage schema, transaction boundaries, and write cadence are
  `70_integrations/DATABASE_PERSISTENCE.md`'s.

**Scaling units — what you add one more of, and when:**

| Unit added | Trigger to add | Bound / ceiling |
|---|---|---|
| **World node** (BEAM node) | Aggregate map-process CPU/memory on existing nodes crosses the node budget | Horizontal; maps route across nodes via the router. Practically unbounded at this game's scale |
| **Population channel** (extra map process) | A shared map's occupancy crosses the readability/perf cap | Cap owned by `70_integrations/WORLD_CHANNELS.md`; a channel is cheap (an empty map process is near-free) |
| **Instance worker** (ephemeral map process) | A party enters a PQ gate (`10_systems/SPAWN.md` §7) | One per party; torn down on exit — self-scaling with demand. Open-entry arenas are shared map processes (§1), not instances |
| **Social-service replica** | Chat/party/guild/market throughput rises | Scales independently of world nodes — a market surge never starves combat sim |
| **Read replica** of a Postgres store | Read load (rosters, market browse) grows | The wallet/market **write** primary is the one hard single-writer ceiling (§8), kept single by the single-world choice on purpose |

## 2. Server stack

**Chosen: an engine-independent authoritative server on Elixir/OTP (BEAM), with Phoenix for the
socket, presence, and channel tiers. The Godot 4.3+ engine is the client only; the server does not
embed Godot.**

Rationale: the whole topology is an actor system in disguise. "The map is the unit of simulation —
each map owns its spawner, its live-mob set, and its status timers, so an empty map costs nothing
and a busy map is isolated" (§4, `10_systems/SPAWN.md` §1) maps one-to-one onto an OTP
supervised-process-per-map model, and the failure-mode table (§8) — a map crash drops only its
maps and re-routes players, an instance crash loses only that instance — *is* an OTP supervision
tree rather than error-handling bolted on afterward. The single logical world's heavy load is
account-to-account social traffic (chat, party, guild, mail, market, trade, presence for
hundreds-to-low-thousands concurrent), which is BEAM's proven sweet spot. Combat is
hit-event-triggered rather than a heavy fixed-rate numeric sim (§4), and a side-scroller's position reconciliation is light, so
the BEAM's soft-realtime profile is a fit rather than a liability. Fault isolation, per-process
supervised restart, and live presence come from the platform instead of being hand-built.

Rejected alternatives:
- **Headless Godot as the server** (share GDScript physics/scenes with the client). Rejected:
  GDScript is too slow for thousands of concurrent authoritative sessions, Godot's threading and
  socket model is not built for a long-lived authoritative fleet, and it couples the server
  lifecycle to the game-engine release cadence. It offers no supervision/fault-isolation model,
  so the §8 degradation guarantees would be hand-rolled.
- **Go.** A viable middle ground (goroutines, simple ops, static typing) and the closest runner-up,
  but the per-map supervision, restart, and presence machinery this topology leans on would be
  built and maintained by hand — exactly what OTP provides natively.
- **Rust / C++ / C#.** More raw throughput than hundreds-to-low-thousands concurrent 2D warrants;
  authoring cost and (for Rust/C++) memory-model overhead buy performance headroom this genre does
  not need. Kept in reserve as a NIF/port escape hatch (below), not as the primary stack.

**The pure combat formula still moves server-side "untouched" — as a spec, not a shipped file.**
`30_engineering/ENGINEERING_STANDARDS.md` (prime directive 5) and `10_systems/PERSISTENCE.md` §2
require `CombatMath`, the drop roller, and the seeded RNG service to move to the server unchanged.
Because the server is engine-independent, "unchanged" is honored at the level of the algorithm:
`10_systems/COMBAT_FORMULA.md` remains the single source of truth, and the server's Elixir port is
validated against the **same** test vectors the client's GDScript `CombatMath` is tested against
(`30_engineering/ENGINEERING_STANDARDS.md` GUT tests) so client prediction and server authority can
never diverge. Any CPU-hot numeric path a specific map ever needs is an OTP NIF/port (Rust) — a
coding-pass optimization, not an architecture change. The cross-implementation test-vector
requirement is flagged to `70_integrations/GAMEPLAY_SIMULATION.md` (§9).

## 3. Database technology

One transactional engine backs the three account-to-account stores; the audit stream and the cache
tier use fit-for-purpose technologies off that engine so neither steals its write budget. Schema,
transaction boundaries, and write cadence are `70_integrations/DATABASE_PERSISTENCE.md`'s (§9) — this
doc fixes only the **technology** each component runs on and why.

| Component (from §5) | Technology | Why |
|---|---|---|
| Character DB | **PostgreSQL** (own logical database/schema) | Relational, ACID; a character save is a set of related rows that must commit together |
| Wallet / economy ledger | **PostgreSQL** (own logical database/schema) | Account-to-account `shards`/item transfers (`MARKET`/`MAIL`/`TRADING`) must be **atomic** — no minting, no loss; multi-row transactions are the whole point of the single-world ledger (§1) |
| Social / market DB | **PostgreSQL** (own logical database/schema) | Guild/party/trade/mail/market state; relational, and shares transactions with the wallet on value transfer |
| Seeded-RNG audit log | **Append-only log store** (partitioned object storage / log-structured stream), off Postgres | High-write, write-once, read-rarely (forensic/replay). Keeping it off the transactional DB protects the ledger's write budget (§8) |
| Session / presence / cooldown / escrow-in-flight cache | **Redis** for cross-node coordination + **BEAM-native ETS / Phoenix.Presence** for in-node ephemeral state | Fast, TTL-native, not a source of truth — Postgres stays truth. BEAM holds in-node ephemeral state itself, so Redis is a smaller dependency than in a stateless-server design |

**Chosen: PostgreSQL for all three transactional stores, one engine, separated by logical
database.** Rationale: the wallet/market ledger is a money ledger — the single-world choice (§1)
exists precisely to keep it one coherent, transactionally-consistent authority, and Postgres's
ACID multi-row transactions are what make an account-to-account transfer atomic. Character and
social DBs share the same engine (operational simplicity, one backup/replication story) but sit in
separate logical databases so a market-DB outage cannot corrupt character saves (the §1 "separated
by concern" invariant). Rejected: a document/NoSQL store (MongoDB/DynamoDB) for the wallet or
character data — its eventual consistency and weak cross-row transactions are wrong for a ledger
that must never mint or lose value; the RNG audit log's write-once stream is the only place that
access pattern fits, and it goes to the append-only store, not Postgres. Rejected: a
distributed/horizontally-partitioned SQL engine (CockroachDB/Vitess) — premature for a single-region,
hundreds-to-low-thousands-concurrent world; it trades latency and operational weight for scale this
game does not reach, and cross-region topology is an owner-priced vendor decision (Open Questions),
not a launch requirement.

## 4. Simulation placement (tick model is a sibling's)

This doc fixes only **where** simulation runs; the concrete tick rates, per-tick vs event-driven
budgets, timer resolution, and reconciliation cadence are `70_integrations/GAMEPLAY_SIMULATION.md`'s
(§9) — do not read numbers into this section.

- **Per-map, on world nodes.** Spawn maintenance (`10_systems/SPAWN.md` §3–§5 respawn/off-screen/
  hold logic), mob AI, and status-effect timers (`burn`/`poison`/`regen` ticks, buff/debuff expiry)
  advance on a per-map simulation loop owned by that map's process. An empty map costs nothing; a
  busy map is isolated. Cross-map concerns (routing, presence, the scheduler) are per-node.
  Instances tick as their own maps on an instance worker.
- **Combat resolution is triggered by the hit-frame signal** — the convention
  `30_engineering/ENGINEERING_STANDARDS.md` already fixes ("damage never on a duplicate timer"),
  extended here only as placement: `CombatMath.resolve(...)` is a pure, stateless,
  server-authoritative function (`10_systems/COMBAT_FORMULA.md` §1) invoked per hit event on the
  map's world process. Whether the server handles those events inline or via a per-tick queue is
  `70_integrations/GAMEPLAY_SIMULATION.md`'s call (§9). All rolls flow through the one seeded RNG
  service so a result is server-verifiable later against the audit log (§3).
- **Client prediction / reconciliation boundary — placement only.** Only `authority: shared`
  fields cross this boundary — position/velocity (`10_systems/PERSISTENCE.md` §4): the client
  predicts locally for snappy input and the server reconciles. The reconciliation **algorithm**
  and **cadence** are `70_integrations/GAMEPLAY_SIMULATION.md`'s and out of scope for
  `10_systems/PERSISTENCE.md` §4; this doc fixes only that it runs on the map's own world process,
  against that map's own simulation. `server` fields are never predicted as truth; `client` fields
  never leave the client.

## 5. Authority mapping

`10_systems/PERSISTENCE.md` is the **owner** of every tag and every truth-ledger row below; this
table only maps its §1 tags and §2 rows onto the §1 components and the §3 stores. It restates no
rule or value.

| Truth-ledger row (PERSISTENCE §2/§3/§4) | Tag | Owning component | Durable store (§3) |
|---|---|---|---|
| Character identity | `server` | Auth service (`ACCOUNTS_AUTH.md`) | character DB (Postgres) |
| `level` / `exp` / `exp_into_level` | `server` | World process (leveling) | character DB (Postgres) |
| Primary stats, free-point allocation, derived recompute | `server` | World process (stats) | character DB (Postgres) |
| Inventory (3 tabs) + bank | `server` | Inventory logic in world process | character DB (Postgres) |
| Equipment worn, `enhance_level`, soft-pity counters | `server` | Enhancement resolver (via RNG service) | character DB (Postgres) |
| `shards` wallet | `server` | Wallet / economy service | wallet ledger (Postgres) |
| Quest flags / step progress / completed set | `server` | Quest logic in world process | character DB (Postgres) |
| Skill ranks, respec state, cooldown timers | `server` | World process (skills); cooldowns in-memory (ETS/Redis) | character DB (Postgres) |
| Active status effects (timers, stacks) | `server` | Per-map simulation (world process) | character DB on save (Postgres) |
| Drop rolls, loot tag/ownership timers | `server` | Loot roller (seeded RNG service) | RNG audit log (append-only) |
| Combat resolution (hit/crit/damage/mitigation) | `server` | `CombatMath` in world process | RNG audit log (append-only) |
| Bind point | `server` | World process | character DB (Postgres) |
| Guild / party / trade / mail / market state | `server` | Social services (§7) | social/market DB (Postgres) |
| Raw input, keybinds, camera, UI prefs | `client` | Client only — never synced (PERSISTENCE §3) | local config (client) |
| Position / velocity | `shared` | World process reconciler (§4) | not persisted mid-run |

## 6. Migration path

**The solo build ships first.** `00_vision/SCOPE.md` excludes backend from this run;
`10_systems/PERSISTENCE.md` §5 requires the solo client to be written against a server-authoritative
*boundary* — one **`GameState` facade** over a local save — even with no server. That facade is the
migration seam.

- **Stays unchanged.** The `GameState` facade interface; the pure `CombatMath` class (as a spec,
  §2); the single seeded RNG service; the never-trust-the-client enforcement
  (`10_systems/PERSISTENCE.md` §7 — no self-minted `shards`/items, no re-rolled drops, no
  client-recomputed derived stat treated as truth). These were built to move server-side untouched
  (`30_engineering/ENGINEERING_STANDARDS.md` prime directive 5).
- **Replaced.** The facade's **backing store** swaps from a local file to a gateway network client
  speaking `70_integrations/NETWORK_PROTOCOL.md`'s protocol; the in-process "simulated boundary"
  becomes real Elixir/OTP world processes (§2); the local RNG becomes the server RNG service writing
  the append-only audit log (§3). Calling code does not change — that is the point of the facade.
- **One-way import.** A solo character imports **once** into the live world, never the reverse
  (`10_systems/PERSISTENCE.md` §9; `70_integrations/ACCOUNTS_AUTH.md` §2 binds it to an account on
  import); the import's validation/sanitization pass is those docs' open item, not re-decided here.
- **Implemented when.** After the solo build ships and the owner greenlights a live server. Until
  then this whole topology is dormant design, exactly as the social systems below.

## 7. Social-deferred systems

All six are designed but server-deferred (their stubs ship "present but dormant" in the solo
build). When un-deferred they land on the **social services** tier (§1); each remains
`authority: server` (`10_systems/PERSISTENCE.md` §2). Service internals — relay topology, roster
state, escrow mechanics — are `70_integrations/CHAT_SOCIAL_BACKEND.md`'s (§9); this table fixes only
where each lands.

| System | Lands as | Notes |
|---|---|---|
| `CHAT` | Stateless relay off the gateway/social tier | Map-scoped `normal`, roster `party`/`guild`, `whisper` (`10_systems/social/CHAT.md`); speech bubbles are a `normal`-channel client render |
| `PARTY` | Roster + reward-arbitration service | Owns exp/loot arbitration and party bookkeeping for PQ instances (`10_systems/social/PARTY.md` §4–§6); the allocation mechanism itself is `10_systems/SPAWN.md` §7's |
| `GUILD` | Guild registry service | Rosters, crest data (`10_systems/social/GUILD.md`); creation fee is an `10_systems/ECONOMY.md` sink |
| `TRADING` | Live two-party escrow session | Both online; server-held escrow swap (`10_systems/social/TRADING.md`) |
| `MARKET` | Async listings board + escrow | Server-held listing escrow; shared board = `server` state (`10_systems/social/MARKET.md`) |
| `MAIL` | Store-and-forward mailbox + COD | Attachment/`shards`/COD escrow; may deliver `MARKET` proceeds (`10_systems/social/MAIL.md`) |

`TRADING`/`MARKET`/`MAIL` all move `server`-owned items and `shards`, so they write through the
wallet ledger and character DB (§5) inside one Postgres transaction (§3), never a client copy — the
single-world choice (§1) is what keeps that ledger coherent.

## 8. Failure modes & degradation

Per `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`, every component and external dependency
lists a failure mode and a degradation stance. Fail-loud in dev, fail-safe in prod
(`30_engineering/ENGINEERING_STANDARDS.md` directive 7): a component that cannot prove a `server`
truth must refuse the action, never fabricate it.

| Dependency | Failure mode | Degradation / stance |
|---|---|---|
| Auth service | Down → no new logins | Existing sessions run on cached tokens until expiry; new logins queue, never bypass auth (`70_integrations/ACCOUNTS_AUTH.md` §3) |
| Edge / gateway | Down → total outage (single entry point) | Horizontal replicas behind a balancer; a dropped connection reconnects to the same character within the reconnect-grace window (`70_integrations/ACCOUNTS_AUTH.md` §4), no state minted client-side |
| World node / map process | Crash → its maps drop | OTP supervisor restarts the map fresh; players re-routed to a fresh copy at their last **persisted** point (autosave cadence, `10_systems/PERSISTENCE.md` §6); unsaved position (`shared`, §5) is disposable by design |
| Instance worker | Crash mid-PQ/arena | Instance is lost; party returns to the staging map and re-enters fresh (matches `10_systems/SPAWN.md` §3 "walk back in" reset) — no partial-credit fabrication |
| PostgreSQL — character DB | Unreachable → saves fail | Block state-mutating actions (level-up, turn-in, loot commit) rather than accept unsaved progress; read-only play may continue briefly |
| PostgreSQL — wallet / economy ledger | Unreachable | Freeze all `shards` faucets/sinks and `MARKET`/`MAIL`/`TRADING` value transfer; combat/movement continue |
| PostgreSQL — social/market DB | Unreachable | Social systems degrade to read-only or unavailable; core solo-style play (combat, quests, movement) is unaffected |
| Append-only RNG audit log | Unwritable | Block every roll it gates — drops, crits, enhancement — rather than roll unverifiably (`10_systems/PERSISTENCE.md` §7); an ungated roll is worse than a paused one |
| Redis / cache tier | Unreachable | BEAM-native ETS/Presence covers in-node ephemeral state; cross-node coordination (presence fan-out, distributed rate-limit) degrades — sessions stay bound, but multi-node social presence may lag until it recovers |
| Seeded RNG service | Unreachable | Block every roll it gates (same stance as the audit log above) |

**Scaling.** Maps are the horizontally-splittable unit: hot maps split into more population channels (§1,
`70_integrations/WORLD_CHANNELS.md`); PQ/arena load scales by spinning up instance workers on demand
and tearing them down on exit. Social services scale independently of world nodes (a market surge
never starves combat sim). The one hard single-writer constraint is the wallet/market Postgres
primary — kept as one authority on purpose (§1); its write throughput is the scaling ceiling to
watch, mitigated by read replicas for browse/roster reads (§1 table) but never by partitioning the
`shards` namespace.

## 9. Sibling-doc boundaries (single source of truth)

This doc is gated first; the following six siblings are authored later this run and own the detail
this doc deliberately does not decide. Each is cited above where its boundary is crossed.

| Sibling | Owns (this doc does not decide it) |
|---|---|
| `70_integrations/GAMEPLAY_SIMULATION.md` | Concrete tick model: rates, per-tick vs event-driven split, timer resolution, reconciliation cadence, and the client/server `CombatMath` test-vector parity requirement flagged in §2 |
| `70_integrations/NETWORK_PROTOCOL.md` | Transport, serialization, envelope, opcodes, the packet catalog — everything on the wire between client and gateway |
| `70_integrations/WORLD_CHANNELS.md` | Channel-model detail and capacity targets (per-map occupancy cap, channel-count math); this doc fixes only the channel-model shape (§1) |
| `70_integrations/ACCOUNTS_AUTH.md` | Account/character split, credential and session lifecycle, name policy, reconnect-grace and session-lifetime numbers (exists; its revision this run SETS those numbers, removing the earlier version's deferrals back to this doc) |
| `70_integrations/CHAT_SOCIAL_BACKEND.md` | Chat/social service internals: relay topology, roster state, escrow mechanics for the §7 systems |
| `70_integrations/DATABASE_PERSISTENCE.md` | Storage schema, transaction boundaries, and write cadence mapped onto the §3 technologies |

## 10. Secrets & implemented-when

- **Secrets are environment-managed, never committed** (`docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`;
  matches `70_integrations/ACCOUNTS_AUTH.md` §3's password-hashing-parameter stance and the
  `PIXELLAB_SECRET` precedent). Database credentials, the Redis auth, session-signing keys, and any
  storefront/SSO secrets live in environment-managed configuration and are set/rotated in ops, never
  in this tree.
- **Implemented when:** a live authoritative server exists — i.e. after the interim solo build
  ships and the owner greenlights it (§6). Until then this topology is a forward contract, dormant
  by design, and blocks nothing in the solo build.

## Open Questions

Only game-design unknowns and owner-priced items live here; the concrete stack (§2), database
technology (§3), and topology (§1) are decided in this doc and are **not** open questions.

- **Hosting, cloud vendor, region(s), and managed-service selection are owner-priced.** This doc
  commits to PostgreSQL, an append-only log store, and Redis as **technologies** (§3); which managed
  offering hosts them, in which region(s), and any support/contract tier carry a real price tag and
  stay the owner's call. No vendor or region commitment is made here; secrets stay
  environment-managed and uncommitted (§10).
- **RNG audit-log retention window and storage tier** (§3) are owner-priced — how long forensic/
  replay data is kept, and on what storage class, is a cost decision, not an architecture one.
- **Cross-region / DB failover and replication topology** for the character and wallet stores is
  deferred to the vendor decision above; single-region is assumed at launch (§3), and a
  multi-region posture would reopen the name-uniqueness namespace granularity noted in
  `70_integrations/ACCOUNTS_AUTH.md`.
- Whether `MARKET` proceeds deliver via wallet credit or `MAIL` is unresolved in both stubs
  (`10_systems/social/MARKET.md`, `10_systems/social/MAIL.md`) — a routing choice this topology
  supports either way (both write through the same Postgres ledger transaction, §7), not decided here.
