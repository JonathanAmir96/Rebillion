# BACKEND_CHECKLIST_AUDIT_2026-07-24.md — Owner Security/Performance Checklist vs the Phase I Suite

References: docs/phase_reports/PHASE_I_BACKEND_REPORT.md, 70_integrations/BACKEND_ARCHITECTURE.md,
70_integrations/GAMEPLAY_SIMULATION.md, 70_integrations/NETWORK_PROTOCOL.md,
70_integrations/DATABASE_PERSISTENCE.md, 70_integrations/WORLD_CHANNELS.md,
70_integrations/ACCOUNTS_AUTH.md, 70_integrations/CHAT_SOCIAL_BACKEND.md,
70_integrations/TELEMETRY_ANALYTICS.md, 10_systems/PERSISTENCE.md, 10_systems/social/TRADING.md,
docs/VALIDATION.md

On **2026-07-24** the owner issued a backend **security** (anti-cheat / data-integrity) and
**performance** (scalability / low-latency) requirements checklist. The Phase I backend wave
(`docs/phase_reports/PHASE_I_BACKEND_REPORT.md`, run 2026-07-23) had landed one day earlier and
already decides most of the same ground. This report audits every checklist requirement against
the landed suite: **verdict, owning doc/section, and the gaps flagged** (as Open Questions in the
owning docs, per the tree's flag-don't-guess law). It states no new rules itself.

**Branch disposition.** The checklist branch first authored two standalone owner docs
(`30_engineering/BACKEND_SECURITY.md`, `30_engineering/BACKEND_PERFORMANCE.md`) against a pre-v3,
pre-Phase-I base. On merge they were **retired unlanded** — the gated suite owns every rule they
would have duplicated (single-source-of-truth law) — and replaced by this audit plus three
surgical Open-Question flags. `10_systems/PERSISTENCE.md` §4's stale "out of scope" deferral was
repointed to `70_integrations/GAMEPLAY_SIMULATION.md` §2 in the same merge.

## 1. Security checklist — verdicts

| # | Owner requirement | Verdict | Where it is satisfied |
|---|---|---|---|
| S1 | Server-side movement validation (authoritative position/velocity/state; simulate inputs; snap beyond threshold) | **Covered** | `70_integrations/GAMEPLAY_SIMULATION.md` §2: server-held `shared` position/velocity, 20 Hz accept-if-plausible check, error-blend inside the envelope, out-of-band hard-snap correction on gross divergence |
| S2 | Velocity capping per tick | **Covered** | Same §2 envelope: per-interval displacement margin = max plausible travel at the occupant's speed cap (base × capped `haste`/`swiftness`, `10_systems/STATS.md` §6) + velocity-direction sanity check |
| S3 | Server-side damage calculation ("I used Skill X" → server checks cooldown/resource/target, rolls from DB-authoritative stats, applies, broadcasts) | **Covered** | `70_integrations/GAMEPLAY_SIMULATION.md` §5 (deterministic per-tick combat queue, server-side `CombatMath`), §6 (skill-use validation: cooldown timers, `essence_cost`, targeting), §14 (acquisition rule: every mutating packet cites its validating section); results pushed event-driven via `70_integrations/NETWORK_PROTOCOL.md` §13 |
| S4 | Visibility / area-of-interest checks (no map-radar) | **Partial — flagged** | Exposure is bounded today by per-map/channel scope + occupancy caps (`70_integrations/WORLD_CHANNELS.md`: 150 town / 60 field), but the 10 Hz snapshot is whole-visible-state per broadcast; per-client interest filtering was already an open item in `70_integrations/NETWORK_PROTOCOL.md` — its Open Question now carries the anti-cheat rationale (this audit), not capacity alone |
| S5 | ACID transactions for every inventory change; trades atomic | **Covered** | `70_integrations/DATABASE_PERSISTENCE.md` §4: one-transaction table for every ledger mutation — the two-party swap commits both offers across `char`+`wallet`+`social` schemas or not at all (the schemas-in-one-database decision exists precisely for this) |
| S6 | Row-level locking against duplication races | **Partial — flagged** | Structural guards exist (slot-uniqueness PK, append-only wallet ledger, audit-before-commit, `70_integrations/NETWORK_PROTOCOL.md` §8 idempotent replay dedup); the explicit lock/isolation discipline for multi-row swap paths is now a `70_integrations/DATABASE_PERSISTENCE.md` Open Question (this audit) |
| S7 | WSS + TLS everywhere | **Covered** | `70_integrations/NETWORK_PROTOCOL.md` §1 (WSS transport); `70_integrations/BACKEND_ARCHITECTURE.md` §1 (TLS-terminating gateway is the only public endpoint; clients never reach the database) |
| S8 | Rate limiting & flood-drop on packets and endpoints | **Covered** | Gateway rate-limit tier (`70_integrations/BACKEND_ARCHITECTURE.md` §1); concrete per-channel chat limits + throttle→auto-mute ladder (`70_integrations/CHAT_SOCIAL_BACKEND.md`); login lockout ladder (`70_integrations/ACCOUNTS_AUTH.md`); gameplay ceilings stack on top (`10_systems/social/TRADING.md` §5) |
| S9 | Strict input validation; prepared statements | **Mostly covered — SQL rule flagged** | Wire-side: fixed envelope, opcode catalog, per-field types and authority annotations (`70_integrations/NETWORK_PROTOCOL.md` §3/§9); semantic: every mutating packet routes through its `70_integrations/GAMEPLAY_SIMULATION.md` §5–§14 validating section. The parameterized-SQL-only rule was nowhere written — folded into the new `70_integrations/DATABASE_PERSISTENCE.md` Open Question |

## 2. Performance checklist — verdicts

| # | Owner requirement | Verdict | Where it is satisfied |
|---|---|---|---|
| P1 | Binary serialization, no JSON on hot paths | **Covered** | `70_integrations/NETWORK_PROTOCOL.md` §2: MessagePack envelope/payloads, DEFLATE above ~512 B; JSON at most as a debug-build negotiation (its own OQ) |
| P2 | Delta compression | **Open by decision — bounded** | Snapshot is whole-visible-state at 10 Hz, deliberately, with client interpolation; delta-encoding is an explicit `70_integrations/NETWORK_PROTOCOL.md` Open Question tied to the same revisit as S4, and occupancy caps bound worst-case payload meanwhile |
| P3 | Tick rate tuned to the genre (15–30 Hz band, not needlessly high) | **Covered** | `70_integrations/GAMEPLAY_SIMULATION.md` §1.1: 20 Hz simulation / 10 Hz snapshot, with the 20 Hz-snapshot option explicitly rejected as bandwidth waste |
| P4 | Room instancing — never one world loop | **Covered** | `70_integrations/BACKEND_ARCHITECTURE.md` §1: one supervised process per live map/channel; population channels for crowded maps; ephemeral instance workers per party for raid content |
| P5 | Spatial partitioning (grid/quadtree) to avoid O(N²) | **Satisfied by architecture** | The unit of simulation is already the map process, and `70_integrations/WORLD_CHANNELS.md` occupancy caps (≤150 town / ≤60 field per channel) bound N to side-scroller scale — no in-map grid is warranted at those caps; revisit only if caps rise materially (no flag filed) |
| P6 | Index all frequently queried columns | **Covered at design granularity** | `70_integrations/DATABASE_PERSISTENCE.md` §3 schema sketches carry the load-bearing keys (unique account/character name, composite inventory PKs, listing/mail status keys); column-level index *tuning* is explicitly coding-pass work per that doc |
| P7 | Connection pooling | **Covered — sizing owner-priced** | `70_integrations/DATABASE_PERSISTENCE.md`: pooled access assumed throughout; per-role pool caps (e.g. per-role PgBouncer) already an owner-priced Open Question there |
| P8 | Redis/in-memory caching of static data | **Covered** | `70_integrations/BACKEND_ARCHITECTURE.md` §3: Redis + BEAM-native ETS/Presence cache tier, Postgres never the source for hot ephemera; authored content (items/skills/mobs/maps) is not in the runtime DB at all — it ships with the build (`70_integrations/DATABASE_PERSISTENCE.md` §2 runtime-keys-vs-authored-IDs rule) |
| P9 | APM: P95/P99 tick latency, query time, throughput, memory, CCU | **Gap — flagged** | No suite doc owns operational/perf telemetry; `70_integrations/TELEMETRY_ANALYTICS.md` is deliberately balance-only. Its Open Questions now carry the APM gap with the checklist's required metric set, proposed for the backend coding pass (this audit) |

## 3. Actions taken by this audit

1. **Retired** the checklist branch's two would-be owner docs in the merge (see Branch
   disposition above) — no duplicate rule text landed.
2. **Repointed** `10_systems/PERSISTENCE.md` §4 (+ its Open Question) from the stale
   "out of scope this run" deferral to `70_integrations/GAMEPLAY_SIMULATION.md` §2, which
   resolves it.
3. **Flagged S4** — added the anti-cheat (map-radar) rationale to
   `70_integrations/NETWORK_PROTOCOL.md`'s existing snapshot-encoding/interest-management Open
   Question.
4. **Flagged S6/S9** — added the concurrency-control-discipline + parameterized-SQL Open
   Question to `70_integrations/DATABASE_PERSISTENCE.md`.
5. **Flagged P9** — added the operational-APM ownership gap to
   `70_integrations/TELEMETRY_ANALYTICS.md`'s Open Questions.

## Open Questions

- ~~**Stack naming discrepancy (owner to confirm).** The 2026-07-24 checklist names
  Supabase/PostgreSQL, a Colyseus-style room server, and Redis as its reference technologies. The
  gated suite decides PostgreSQL and Redis (matching) but **Elixir/OTP + Phoenix** rather than a
  Node/Colyseus room layer (`70_integrations/BACKEND_ARCHITECTURE.md` §2, with Node-adjacent
  alternatives rejected on supervision/fault-isolation grounds), and no Supabase commitment
  (hosting/managed-service selection is owner-priced in that doc's Open Questions). Every
  checklist *requirement* is satisfied technology-agnostically. If Supabase or Colyseus is a hard
  owner constraint rather than an illustrative reference, that reopens
  `70_integrations/BACKEND_ARCHITECTURE.md` §2/§3 through its amendment channel — the default
  assumption here is that the suite's gated decision stands.~~ **Resolved 2026-07-24 (owner):**
  the suite's Elixir/OTP + Phoenix decision **stands**, owner-confirmed. The owner prioritizes
  reliability over build speed ("develop will take time but use the more reliable method even if
  a little more complex") and set the end-state as an **autonomously maintained** live game —
  incidents trigger agents that diagnose and fix (`docs/60_agents/AUTONOMOUS_MAINTENANCE.md`).
  OTP's supervision/crash-report model doubles as that loop's structured trigger source, which
  strengthens the original rationale. The checklist's Colyseus/Supabase names are confirmed as
  illustrative references only.
- The three flags filed above (S4 interest filtering, S6/S9 concurrency + SQL discipline, P9
  APM ownership) resolve in their owning docs, not here; this report only tracks that they were
  filed.
