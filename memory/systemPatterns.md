# systemPatterns.md — Architecture & Non-Negotiable Laws

> Memory Bank file 2/5. Backend decisions here were gated in Phase I
> (`docs/phase_reports/PHASE_I_BACKEND_REPORT.md`) and audited against the owner's
> security/performance checklist (`docs/phase_reports/BACKEND_CHECKLIST_AUDIT_2026-07-24.md`).
> Owning docs win on detail; this file is the map.

## System architecture overview

**Topology** (`docs/70_integrations/BACKEND_ARCHITECTURE.md` §1): single logical world →
Godot clients → TLS → Edge/Gateway (Phoenix: TLS termination, token validation,
rate-limiting, presence, routing) → Auth service + World nodes (Elixir/OTP) + ephemeral
Instance workers + Social services + Persistence tier. Clients never reach the database.

- **Unit of simulation = the map.** One OTP-supervised process per live map/channel/
  instance; owns spawn zones, live mobs, status timers. Empty maps park their tick loop
  (~zero cost). A map crash loses only that map; OTP restarts it and players re-route to
  their last persisted point.
- **Room instancing** (owner requirement P4 — never one world loop): population
  *channels* are extra supervised processes of the same map (cap 5/map; occupancy 150
  town / 60 field); **raid gates are the only true instances** — one ephemeral worker
  per party, torn down on exit. Open-entry boss arenas are shared reset-when-empty maps
  (30 s grace), never per-party.
- **Tick model** (`GAMEPLAY_SIMULATION.md` §1): **20 Hz simulation / 10 Hz snapshot**;
  client physics 60 Hz. Timers are absolute-expiry timestamps checked per tick;
  cooldowns lazily checked at cast time.

**Server-authoritative physics/movement** (`GAMEPLAY_SIMULATION.md` §2): client
predicts at 60 Hz and reports position+velocity at 20 Hz; server runs one
accept-if-plausible reconciliation check per occupant per tick — ±½-tile slack +
displacement margin at the stat-capped speed + velocity-direction sanity. Small error
blends over 2–3 frames; gross divergence hard-snaps out-of-band. No world rollback.

**Server-authoritative damage** (`GAMEPLAY_SIMULATION.md` §5–§6): "I used Skill X" is a
*request*; the server checks cooldown, `essence_cost`, and targeting, then resolves via
the pure, stateless `CombatMath.resolve()` — hit events are queued and drained once per
tick in deterministic order through one seeded RNG service, written to the append-only
audit log, and pushed as events. `CombatMath` has bit-for-bit parity fixtures in both
GDScript (GUT) and Elixir (ExUnit).

**Mob AI** (`GAMEPLAY_SIMULATION.md` §13, `docs/10_systems/AI_BEHAVIOR.md`): the map
process owns every live mob's AI (8 states + 12 profiles + scripted boss phases), spawn
upkeep, respawn timers, and the off-screen spawn rule. The client only animates mobs.

**Database strategy** (`docs/70_integrations/DATABASE_PERSISTENCE.md`): **one
Supabase-managed PostgreSQL database** (datastore vendor owner-ratified 2026-07-24),
three schemas — `char` / `wallet` / `social` — each with a least-privilege role. Chosen
over separate databases precisely so value transfers (trades, market buys, mail COD,
enhance fees) commit as ordinary single-DB multi-schema **ACID transactions — no 2PC**.
Append-only `wallet_ledger` (balance = same-transaction sum of deltas); append-only
off-Postgres RNG audit log, written *before* the applying transaction. Redis/ETS are
cache tiers, **never truth**. The Elixir/OTP + Phoenix game-server decision stands
unchanged — Supabase supplies the database tier only; clients never reach it.

**Transaction semantics — two-sided swaps (owner law 2026-07-24; resolves flag S6):**
every multi-row value transfer (trade swap, market escrow purchase, mail COD
payment-vs-claim, wallet mutation) runs as one ACID transaction that takes explicit
row-level locks up front: `SELECT … FOR UPDATE` on *all* participating rows — both
wallets, the moving `item_instance`/`inventory_slot` rows, and the `market_listing` /
`mail` / trade rows — acquired in one deterministic global lock order (ascending table,
then primary key; lower character id first) so concurrent swaps can never deadlock.
Preconditions re-validate *under lock* (listing still active, item still owned, wallet
within cap); deltas + `wallet_ledger` rows apply; then commit — or the whole
transaction is refused. Two buyers racing one listing: first locker wins, second fails
closed on re-validation; duplication is impossible because the item row itself is
locked and moved in the same transaction. Default isolation READ COMMITTED + explicit
locks; paths that cannot pre-enumerate their rows (offline-import merge) escalate to
SERIALIZABLE with bounded retry. Full spec lands in `DATABASE_PERSISTENCE.md`'s next
revision (queued — `activeContext.md`).

## Non-negotiable laws

### 1. Never Trust the Client
Every client→server packet is a statement of *intent*, never an outcome
(`NETWORK_PROTOCOL.md` §7). The `docs/10_systems/PERSISTENCE.md` §1 tag taxonomy is
complete and closed: `server` (sole truth: identity, exp, stats, inventory, wallet,
quests, skills, drops, combat results, cooldowns, social state) / `client` (never
synced: input, keybinds, camera, UI prefs) / `shared` (position+velocity only —
client predicts, server reconciles). The never-trust list (`PERSISTENCE.md` §7,
`GAMEPLAY_SIMULATION.md` §14): the client never mints items or `shards`, never
self-assigns drop results, never supplies derived stats as truth, never rerolls
enhancement, never skips a cost/cooldown/prerequisite gate. Every mutating packet must
cite its validating `GAMEPLAY_SIMULATION.md` section. Offline→online import is
fail-closed: re-derive level from raw exp + bounds-check everything; reject, don't
repair (`ACCOUNTS_AUTH.md` §2.4).

### 2. Multi-agent governance
Memory-bank workflow tiers, mapped onto the repo's routing law
(`docs/60_agents/roles/ORG.md` — route by **blast radius**, not volume):

- **Fable — MANUAL OVERRIDE ONLY** (owner-ratified 2026-07-24; supersedes the earlier
  "Fable = specs seat" mapping). Fable is never assigned automated pipeline roles — it
  is invoked exclusively on manual developer trigger for high-level producer decisions,
  phase-gate rulings, and manual overrides.
- **Opus — Architecture/Logic/Audit.** The primary automated reasoning engine:
  cross-system architecture, complex game logic, database schemas, network protocols,
  math formulas and curves, boss/arena design, coding-pass briefs, adversarial deep
  audits and QA gates.
- **Sonnet — Execution.** Task-bounded implementation inside a fixed contract:
  map/quest/NPC batches, schema docs, doc reviews, file generation, and diff
  application within pre-computed manifests.
- **Haiku — mechanical fill** (template YAML, token scans, stubs), per ORG.md.

`docs/60_agents/roles/ORG.md` amendment queued: the producer seat's *automated* duties
route to Opus; manual gates and overrides are the developer-triggered Fable seat.

Escalation: unresolved ambiguity → file in the owning doc's `## Open Questions` and
escalate one tier via the producer — **never guess** (repo Law 4). Leads pre-compute
manifests so the tier below executes mechanically. Only the producer commits/pushes.

### 3. Token preservation
- **< 250 lines per file.** Memory files and new docs stay under 250 lines; split by
  concern rather than growing monoliths. (Repo convention: content files hold values +
  references only; link, never restate — Law 2.)
- **Diff-only output.** Agents editing existing files emit targeted diffs/edits, never
  full-file rewrites; one concern per commit; content commits separate from doc/rule
  commits.
- **Cached static reference data** (owner-ratified 2026-07-24 — formalizes the ORG.md
  demotion rule): leads bake GLOSSARY tokens, ID blocks, enum lists, and exemplar
  shapes into the batch manifest; executors never re-read owner docs mid-batch.
- Exemplar-first batching: one real file per schema, then region-scoped parallel
  agents, each batch validator-gated (`python3 tools/validate.py`) before landing.

### 4. Standing repo laws (bind every agent — see `projectbrief.md`)
GLOSSARY tokens only · single source of truth · immutable IDs in `ID_REGISTRY.md`
blocks · locked files untouched (`ART_BIBLE.yaml`, `UI_ART_SPEC.md`,
`ENGINEERING_STANDARDS.md`) · every doc ends with `## Open Questions` · validate before
landing · US spelling.

## Client engineering patterns (locked — `docs/30_engineering/ENGINEERING_STANDARDS.md`)

- Godot 4.3+, statically-typed GDScript; data-driven always (new monster = zero code);
  composition over inheritance; signals up / calls down via EventBus.
- YAML → `.tres` Resources at **build time**; content Resources immutable at runtime;
  `Database` autoload hard-errors on broken refs at load.
- All damage math lives only in pure stateless `CombatMath`; all randomness through one
  seeded RNG service — both movable server-side unchanged.
- Solo build writes all state through the `GameState` facade so the backing store swaps
  from local file to gateway client at migration with calling code unchanged
  (`PERSISTENCE.md` §5).
- Object-pool hot paths; hierarchical state machines; canonical collision-layer enum;
  GUT tests + CI validator block merges.

## Open Questions

- None owned here. Live architectural flags (interest filtering S4, row-lock discipline
  S6/S9, APM ownership P9, snapshot delta-encoding) are indexed in `activeContext.md`
  and owned by their `70_integrations/` docs.
