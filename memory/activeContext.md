# activeContext.md — Current State, Priorities, Open Decisions

> Memory Bank file 4/5. Snapshot as of **2026-07-24** (`main` @ `1b28149` + owner
> rulings D1–D5, this session). Newest owner decisions live in root `memory.md`; this
> file distills what the *next* session must know before generating anything.

## Current repository state

- **Single canon** (owner-ruled 2026-07-24): the five-island / two-arc world — 11
  regions, 324 maps, 234 monsters, 11 bosses, 4 raids, branching 2nd jobs, authored
  content Lv 1–80 (elites to 82), game cap 300 reserved. A competing two-island
  reconciliation was reverted; version tags (v2/v3) were stripped — the tree reads as
  one design.
- **Phase D content is complete for the whole world** and the strict validator
  (`python3 tools/validate.py`, entry `map_001`, global reachability) passes
  **0 failures / 0 warnings**.
- **Phase I backend-design suite is landed and gated** (`docs/70_integrations/`), and
  audited against the owner's security/performance checklist
  (`BACKEND_CHECKLIST_AUDIT_2026-07-24.md`): 14 of 18 requirements fully covered by the
  suite; 4 flags filed (below). Stack decision owner-confirmed.
- **Newest design layer** (2026-07-24): the social package — raids as centerpiece
  (tokens `item_etc_0177`–`0180`, raid gear `item_equip_0223`–`0230`, daily
  first-clear 2×), `party_drop_bonus` ladder, widened party exp-share band,
  `social/PARTY_FINDER.md`, guild incentives (`guild_contribution`, weekly goals).
  **Balance pass done same day** — raid exp, drop-bonus ladder, exp-share band, guild
  curve/buffs, and Quartermaster prices are locked with arithmetic in the owning docs;
  plus a new cosmetics owner doc (`10_systems/COSMETICS.md`, `item_cosmetic_*` block
  owner-assigned in ID_REGISTRY).
- **Pacing retune** (owner-ratified): Lv 40 ≈ 30 h, Lv 80 ≈ 166 h, Lv 100 ≈ 300 h;
  `kills_per_level = round(20 + 6.6L + 0.20L²)` frozen through Lv 100.

## Owner rulings — 2026-07-24 (D1–D5, this session; logged in root `memory.md`)

- **D1 — hard Lv-80 world cap.** The Lv-300 reserve is retired. Patch queue: SCOPE /
  WORLD_PLAN / GLOSSARY cap lines; LEVELING §6 softcap-sketch removal; ACCOUNTS_AUTH
  §2.4 import clamp (82/300 → 80). **Open ruling:** fate of the Lv 81–82 elite
  overshoot (clamp to 80 vs keep as over-cap mobs) — filed, owner call.
- **D2 — 2nd-job advancement at Lv 30** (supersedes Lv 40). Patch queue: JOBS.md,
  LEVELING.md advancement references, GLOSSARY, `job.schema.md` advancement rows,
  trainer quest gates + Lv-40-gated skill rows; re-check FTUE/pacing notes that cite
  the advancement moment.
- **D3 — Supabase-managed PostgreSQL is the mandatory datastore**, under strict ACID
  with explicit `SELECT … FOR UPDATE` row locking on all two-sided swaps. Resolves
  flag **S6** as law (`systemPatterns.md`); DATABASE_PERSISTENCE.md next revision
  writes the full lock-order/retry spec (S9 rides along). Partially resolves the
  owner-priced hosting item (vendor chosen; region/failover still open).
- **D4 — server authority restated** (already canon, no doc change): physics, combat,
  damage, minting server-side; movement via the GAMEPLAY_SIMULATION §2 envelope;
  client input buffering advisory only; offline saves sanitized fail-closed.
- **D5 — token laws:** <250-line files, diff-only outputs, manifest-cached static
  reference data; **Fable = manual override only, never automated**. ORG.md amendment
  queued to record the Opus/Sonnet/Fable mapping.

## Immediate priorities (ordered)

1. **Owner-ruling patch wave (D1/D2/D3).** Apply the rulings above to their owning
   docs + affected content (cap lines, import clamp, 2nd-job gates), then re-validate
   0/0. Route: Opus brief → Sonnet diffs.
2. **Quest-exp regen (mechanical debt).** Every `50_content/quests/*.yaml` `exp` value
   is stale against the retuned LEVELING curve — regenerate (pct × exp_to_next), then
   re-validate. Owner doc: `LEVELING.md` §4 handoff.
3. **Phase E — coding-pass briefs.** The remaining generation phase: per-feature
   implementation briefs + the VALIDATION §7 Open-Questions rollup index. Route to
   Opus-tier per ORG.md.
4. **Balance pass (D-gate retune) — remaining slice.** The social-package slice locked
   2026-07-24; still owed: ECONOMY prices/fees, tonic bite (overshoots ~20–30% target
   past Superior), DROPS anchors, WORLD_CHANNELS capacity targets (sized against the
   old two-island world), raid band vs Millbrook ceiling.
5. **Art pass.** PixelLab briefs per `ART_GENERATION_RUNBOOK.md`; blocked first on the
   ART_BIBLE tile-scale lock (owner/Agent-3 channel), which also unblocks CAMERA/HUD/
   COMBAT_FORMULA movement placeholders.
6. **Backend coding pass** (post-briefs): Elixir/OTP skeleton per the Phase I suite;
   resolve the remaining audit flags before the affected subsystems are written.

## Active architectural gaps (filed flags — resolve before coding that area)

- **S4 / P2 — snapshot interest filtering + delta encoding**: 10 Hz snapshot is
  whole-visible-state; per-client area-of-interest filtering carries the anti-map-radar
  rationale. Owner: `NETWORK_PROTOCOL.md` / `WORLD_CHANNELS.md` OQs.
- **S6 — resolved by owner law (2026-07-24)**: explicit `FOR UPDATE` row-lock +
  lock-order + serializable-retry discipline is now mandated (`systemPatterns.md`);
  `DATABASE_PERSISTENCE.md` next revision writes the full spec. **S9**
  (parameterized-SQL-only rule) still owed in that same revision.
- **P9 — operational APM unowned**: P95/P99 tick latency, query time, throughput, CCU,
  alerting have no owning doc (`TELEMETRY_ANALYTICS.md` is balance-only). Proposed for
  the backend coding pass as an ops runbook.
- **Report/moderation durable schema** missing from `social` schema
  (`DATABASE_PERSISTENCE.md` §3.3).

## Open technical decisions (by decider)

**Owner-priced (money/vendor calls — cannot be decided by agents):**
hosting region for BEAM nodes (datastore vendor = Supabase, ratified 2026-07-24) ·
RNG-audit retention window · failover/replication topology · storefront + CI +
code-signing vendors · SSO and email
providers · character-slot expansion pricing · platform priority sign-off
(Windows→macOS→Linux proposed).

**Design calls needed before/at the relevant coding step:**
- MARKET proceeds: wallet credit vs MAIL delivery (blocks market + mail code).
- Account/credential store placement: `char` schema vs dedicated `account` schema
  (default: separate).
- Out-of-combat life/essence rest-regen: unowned rule (STATS/COMBAT shared OQ).
- `round(raw)` rounding convention: pinned round-half-up in fixtures; COMBAT_FORMULA
  owner to confirm.
- Shop-pricing / coach-fare server-validation ownership (no sim section owns it).
- `world` chat channel promotion (proposed 1 msg/60 s) — CHAT.md + GLOSSARY call.
- Emberstone coverage gap: T11–T12 gear has no enhancement stone (Emberstone VI
  `item_etc_0198` reserved, unminted).
- FTUE: Lv-8 ferry gate now lands ≈1.1 h vs the 60-min intro budget — front-load
  scripted exp or relax the gate (intro owner).
- COLLECTIONS set-completion `shards` grant needs a 4th-faucet ECONOMY amendment.
- ID_REGISTRY re-blocks flagged in ITEMS/JOBS OQs (arc-2 mints, skill-line 001–060
  layout) — land registry commits before minting content against them.

**Known design debts (non-blocking, tracked in owning docs):** shields/overalls/
scrolls content integration (blocks 0181–0200, `item_use_0061`–`0100` reserved;
validator `item_use` ceiling needs raising when scrolls mint) · COLLECTIONS/AUDIO/FTUE
deep hooks · stale Lv-100-era phrasing in a few examples · `map_109` `from_clockwork`
chute residue.

## Ground rules for this workflow (owner-directed)

- Reliability over build speed; end-state is an **autonomously maintained** live game
  (`docs/60_agents/AUTONOMOUS_MAINTENANCE.md`).
- Memory Bank governance: **Fable = manual override only** (producer decisions on
  manual developer trigger, never automated); Opus = architecture/logic/audit;
  Sonnet = execution; Haiku = mechanical fill (`memory/systemPatterns.md` §2; ORG.md).
- Keep files < 250 lines, diff-only edits, one concern per commit, validator-gated.
- After any merge, re-run `tools/md_graph.py` (connectivity) and `tools/validate.py`.

## Open Questions

- Should `memory/` be added to the validator's default scan scope (token/link checks
  currently cover `docs/` + root docs only)? Default: yes, at the next tools revision.
