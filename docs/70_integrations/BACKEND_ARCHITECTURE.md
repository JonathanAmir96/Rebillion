# BACKEND_ARCHITECTURE.md — Target Server Topology for the MMO Future

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 10_systems/PERSISTENCE.md,
30_engineering/ENGINEERING_STANDARDS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/SPAWN.md,
10_systems/ECONOMY.md, 10_systems/social/PARTY.md, 10_systems/social/CHAT.md,
10_systems/social/GUILD.md, 10_systems/social/MAIL.md, 10_systems/social/MARKET.md,
10_systems/social/TRADING.md, docs/WORLD_PLAN.md, docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

Design-only target topology for the live, networked build. **No implementation, no code** —
this run is design-documentation only (`00_vision/SCOPE.md` puts networking/backend out of
scope). This doc satisfies the contract in `10_systems/PERSISTENCE.md`: it maps that doc's
authority tags onto concrete server components, it does not re-derive them. It never restates a
system's values — combat math stays `10_systems/COMBAT_FORMULA.md`'s, spawn timing stays
`10_systems/SPAWN.md`'s, `shards` balance stays `10_systems/ECONOMY.md`'s. **Implemented when:**
the interim solo build has shipped and the owner greenlights a live server; nothing here blocks
or precedes the solo build.

## 1. Topology

**Channel model — chosen: single logical world + population channels + true instances.** One
authoritative economy/identity namespace (one `shards` wallet space, one `MARKET`/`MAIL`/`GUILD`
registry) with classic side-scroller **population channels** layered only over shared social
maps (towns, popular fields), plus **true instances** for arena and raid content.

Justification: `MARKET`, `MAIL`, and `TRADING` are account-to-account transfers of `server`-owned
items and `shards`; splitting the world into independent shards would fragment that ledger and
force cross-shard reconciliation the design never asks for. A single logical world keeps one
truth ledger (`10_systems/PERSISTENCE.md` §2). Population channels are a load/readability valve,
not a separate world: a crowded town map hosts N parallel copies sharing one character DB, so no
economy fork occurs. Boss arenas and raid finales are already instanced by
`10_systems/SPAWN.md` §3/§7 and `docs/WORLD_PLAN.md` (`raid_undervault` finale `map_042`,
`raid_mainspring` finale `map_200`), so instance workers are a requirement, not a choice.

```
        clients ── TLS ──┐
                         v
                  [ Edge / Gateway ]  session, rate-limit, fan-out, protocol
                    |          |
          [ Auth service ]   [ World routing ]
          accounts, login       |         |
                                v         v
                 [ World process(es) ]   [ Instance workers ]
                 per-map sim, channels    PQ + arena copies, per-party
                 combat/spawn/status      spun up on demand, torn down on exit
                    |        |                     |
                    v        v                     v
                 [ Social services ]  chat relay, party, guild, mail, market, trade
                    |        |                     |
                    +--------+----------+----------+
                                        v
                 [ Persistence stores ]  character DB · wallet/economy ledger ·
                 social/market DB · seeded-RNG audit log
```

- **Auth service** — owns account identity and the login handshake; the only holder of
  credentials (environment-managed, never committed; details in the sibling
  `70_integrations/ACCOUNTS_AUTH.md`). Issues a short-lived session token the gateway trusts.
- **Edge / gateway** — the single public endpoint. Terminates TLS, validates the session token,
  rate-limits, and routes each authenticated connection to the correct world process / channel /
  instance. Clients never address a world process directly.
- **World processes** — the unit of simulation is the **map** (`10_systems/SPAWN.md` §1). A
  world process hosts a set of maps, each map holding its spawn zones, live mobs, and active
  status timers. Population channels are additional map copies inside (or across) world processes.
- **Instance workers** — ephemeral map copies allocated to one party for raid stages/
  finales and boss arenas (`10_systems/SPAWN.md` §3/§7; `10_systems/social/PARTY.md` §6). `N`
  (party size, 3–6) is fixed at instance creation and never re-scaled mid-run.
- **Social services** — one relay/state tier hosting the server-deferred systems (§5).
- **Persistence stores** — the durable truth ledger. Separated by concern (character, wallet,
  social/market) so a market outage cannot corrupt character saves; vendor choice deferred (§6,
  Open Questions).

## 2. Tick model

- **Authoritative simulation tick: 20 Hz (50 ms), proposed.** Spawn maintenance
  (`10_systems/SPAWN.md` §3–§5 respawn/off-screen/hold logic), mob AI, and status-effect timers
  (`burn`/`poison`/`regen` ticks, buff/debuff expiry) advance on this per-map tick. Exact rate is
  a tuning parameter, not load-bearing here (Open Questions).
- **Per-map vs per-process.** The **map** is the tick unit: each map (or channel copy) owns its
  spawner, its live-mob set, and its status timers, so an empty map costs nothing and a busy map
  is isolated. Cross-map concerns (routing, presence, the tick scheduler) are **per-process**.
  Instances tick as their own maps on an instance worker.
- **Combat is event-driven, not polled.** `CombatMath.resolve(...)` is a pure, stateless,
  server-authoritative function (`10_systems/COMBAT_FORMULA.md` §1); it runs on the hit-frame
  signal the animation emits (`30_engineering/ENGINEERING_STANDARDS.md`, "damage never on a
  duplicate timer"), not on a fixed combat poll. All rolls flow through the one seeded RNG service
  so a result is server-verifiable later.
- **Client prediction / reconciliation boundary.** Only `authority: shared` fields cross this
  boundary — position/velocity (`10_systems/PERSISTENCE.md` §4): the client predicts locally for
  snappy input and the server reconciles. **The concrete reconciliation algorithm is explicitly
  out of scope** per `10_systems/PERSISTENCE.md` §4 and `00_vision/SCOPE.md`; this doc only fixes
  *where* it runs (world process, against that map's own simulation) and does not re-derive it.
  `server` fields are never predicted as truth; `client` fields never leave the client.

## 3. Authority mapping

`10_systems/PERSISTENCE.md` is the **owner** of every tag and every truth-ledger row below; this
table only maps its §1 tags and §2 rows onto the §1 components. It restates no rule or value.

| Truth-ledger row (PERSISTENCE §2/§3/§4) | Tag | Owning component | Durable store |
|---|---|---|---|
| Character identity | `server` | Auth service | character DB |
| `level` / `exp` / `exp_into_level` | `server` | World process (leveling) | character DB |
| Primary stats, free-point allocation, derived recompute | `server` | World process (stats) | character DB |
| Inventory (3 tabs) + bank | `server` | Inventory logic in world process | character DB |
| Equipment worn, `enhance_level`, soft-pity counters | `server` | Enhancement resolver (via RNG service) | character DB |
| `shards` wallet | `server` | Wallet / economy service | wallet ledger |
| Quest flags / step progress / completed set | `server` | Quest logic in world process | character DB |
| Skill ranks, respec state, cooldown timers | `server` | World process (skills); cooldowns in-memory | character DB |
| Active status effects (timers, stacks) | `server` | Per-map simulation (world process) | character DB (on save) |
| Drop rolls, loot tag/ownership timers | `server` | Loot roller (seeded RNG service) | RNG audit log |
| Combat resolution (hit/crit/damage/mitigation) | `server` | `CombatMath` in world process | RNG audit log |
| Bind point | `server` | World process | character DB |
| Guild / party / trade / mail / market state | `server` | Social services (§5) | social/market DB |
| Raw input, keybinds, camera, UI prefs | `client` | Client only — never synced (PERSISTENCE §3) | local config |
| Position / velocity | `shared` | World process reconciler (§2) | not persisted mid-run |

## 4. Migration path

**The solo build ships first.** `00_vision/SCOPE.md` excludes backend from this run;
`10_systems/PERSISTENCE.md` §5 requires the solo client to be written against a
server-authoritative *boundary* — one **`GameState` facade** over a local save — even with no
server. That facade is the migration seam.

- **Stays unchanged.** The `GameState` facade interface; the pure `CombatMath` class; the single
  seeded RNG service; the never-trust-the-client enforcement (`10_systems/PERSISTENCE.md` §7 — no
  self-minted `shards`/items, no re-rolled drops, no client-recomputed derived stat treated as
  truth). These were built to move server-side untouched (`30_engineering/ENGINEERING_STANDARDS.md`
  prime directive 5).
- **Replaced.** The facade's **backing store** swaps from a local file to a gateway network
  client; the in-process "simulated boundary" becomes real world processes; the local RNG becomes
  the server RNG service with an audit log. Calling code does not change — that is the point of
  the facade.
- **One-way import.** A solo character imports **once** into the live world, never the reverse
  (`10_systems/PERSISTENCE.md` §9); the import's validation/sanitization pass is that doc's open
  item, not re-decided here.
- **Implemented when.** After the solo build ships and the owner greenlights a live server. Until
  then this whole topology is dormant design, exactly as the social systems below.

## 5. Social-deferred systems

All six are designed but server-deferred (their stubs ship "present but dormant" in the solo
build). When un-deferred they land on the **social services** tier (§1); each remains
`authority: server` (`10_systems/PERSISTENCE.md` §2).

| System | Lands as | Notes |
|---|---|---|
| `CHAT` | Stateless relay off the gateway/social tier | Map-scoped `normal`, roster `party`/`guild`, `whisper` (`10_systems/social/CHAT.md`); speech bubbles are a `normal`-channel client render |
| `PARTY` | Roster + reward-arbitration service | Owns exp/loot arbitration and instance allocation for PQs (`10_systems/social/PARTY.md` §4–§6) |
| `GUILD` | Guild registry service | Rosters, crest data (`10_systems/social/GUILD.md`); creation fee is an `10_systems/ECONOMY.md` sink |
| `TRADING` | Live two-party escrow session | Both online; server-held escrow swap (`10_systems/social/TRADING.md`) |
| `MARKET` | Async listings board + escrow | Server-held listing escrow; shared board = `server` state (`10_systems/social/MARKET.md`) |
| `MAIL` | Store-and-forward mailbox + COD | Attachment/`shards`/COD escrow; may deliver `MARKET` proceeds (`10_systems/social/MAIL.md`) |

`TRADING`/`MARKET`/`MAIL` all move `server`-owned items and `shards`, so they write through the
wallet ledger and character DB (§3), never a client copy — the single-world choice (§1) is what
keeps that ledger coherent.

## 6. Failure modes & degradation

Per `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`, every external dependency lists a failure
mode and a degradation stance. Fail-loud in dev, fail-safe in prod
(`30_engineering/ENGINEERING_STANDARDS.md` directive 7): a component that cannot prove a `server`
truth must refuse the action, never fabricate it.

| Dependency | Failure mode | Degradation / stance |
|---|---|---|
| Auth service | Down → no new logins | Existing sessions run on cached tokens until expiry; new logins queue, never bypass auth |
| Edge / gateway | Down → total outage (single entry point) | Horizontal replicas behind a balancer; a dropped connection reconnects to the same character, no state minted client-side |
| World process | Crash → its maps drop | Players re-routed to a fresh copy at their last **persisted** point (autosave cadence, `10_systems/PERSISTENCE.md` §6); unsaved position (`shared`, §2) is disposable by design |
| Instance worker | Crash mid-PQ/arena | Instance is lost; party returns to the staging map and re-enters fresh (matches `10_systems/SPAWN.md` §3 "walk back in" reset) — no partial-credit fabrication |
| Character DB | Unreachable → saves fail | Block state-mutating actions (level-up, turn-in, loot commit) rather than accept unsaved progress; read-only play may continue briefly |
| Wallet / economy ledger | Unreachable | Freeze all `shards` faucets/sinks and `MARKET`/`MAIL`/`TRADING` value transfer; combat/movement continue |
| Social/market DB | Unreachable | Social systems degrade to read-only or unavailable; core solo-style play (combat, quests, movement) is unaffected |
| Seeded RNG service | Unreachable | Block every roll it gates — drops, crits, enhancement — rather than roll unverifiably (`10_systems/PERSISTENCE.md` §7) |

**Scaling.** Maps are the shard-able unit: hot maps split into more population channels; PQ/arena
load scales by spinning up instance workers on demand and tearing them down on exit. Social
services scale independently of world processes (a market surge never starves combat sim). The
one hard single-namespace constraint is the wallet/market ledger — kept as one authority on
purpose (§1); its write throughput is the scaling ceiling to watch.

## Open Questions

- **Hosting, cloud vendor, database engine, and instance-orchestration platform are owner-priced
  and deliberately unchosen here** (per role charter: open questions for anything owner-priced).
  No vendor, region, or managed-service commitment is made in this doc; secrets stay
  environment-managed and uncommitted.
- Authoritative tick rate (§2, proposed 20 Hz) is a tuning parameter pending real load and the
  camera/viewport spec that `10_systems/SPAWN.md` §2 also depends on.
- Population-channel switching UX (manual vs automatic, whether a party auto-co-locates to one
  channel) is undesigned; flagged for the future live-build UX pass, not this doc.
- Whether `MARKET` proceeds deliver via wallet credit or `MAIL` is unresolved in both stubs
  (`10_systems/social/MARKET.md`, `10_systems/social/MAIL.md`) — a routing choice this topology
  supports either way, not decided here.
- The `shared` position/velocity reconciliation algorithm is out of scope (`10_systems/PERSISTENCE.md`
  §4); this doc places *where* it runs but does not design it.
- Cross-region/DB failover and replication topology for the character and wallet stores is
  deferred to the vendor decision above.
