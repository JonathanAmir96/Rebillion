# activeContext.md — Current State, Priorities, Open Decisions

> Memory Bank file 4/5. Snapshot as of **2026-07-24** (branch synced to `main`
> @ `d400bcf`). Newest owner decisions live in root `memory.md`; this file distills
> what the *next* session must know before generating anything.

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
  All first-pass numbers, flagged tunable.
- **Pacing retune** (owner-ratified): Lv 40 ≈ 30 h, Lv 80 ≈ 166 h, Lv 100 ≈ 300 h;
  `kills_per_level = round(20 + 6.6L + 0.20L²)` frozen through Lv 100.

## Immediate priorities (ordered)

1. **Quest-exp regen (mechanical debt).** Every `50_content/quests/*.yaml` `exp` value
   is stale against the retuned LEVELING curve — regenerate (pct × exp_to_next), then
   re-validate. Owner doc: `LEVELING.md` §4 handoff.
2. **Phase E — coding-pass briefs.** The remaining generation phase: per-feature
   implementation briefs + the VALIDATION §7 Open-Questions rollup index. Route to
   Opus-tier per ORG.md.
3. **Balance pass (D-gate retune).** ECONOMY prices/fees, tonic bite (overshoots
   ~20–30% target past Superior), DROPS anchors, WORLD_CHANNELS capacity targets
   (sized against the old two-island world), raid band vs Millbrook ceiling.
4. **Art pass.** PixelLab briefs per `ART_GENERATION_RUNBOOK.md`; blocked first on the
   ART_BIBLE tile-scale lock (owner/Agent-3 channel), which also unblocks CAMERA/HUD/
   COMBAT_FORMULA movement placeholders.
5. **Backend coding pass** (post-briefs): Elixir/OTP skeleton per the Phase I suite;
   resolve the four audit flags before the affected subsystems are written.

## Active architectural gaps (filed flags — resolve before coding that area)

- **S4 / P2 — snapshot interest filtering + delta encoding**: 10 Hz snapshot is
  whole-visible-state; per-client area-of-interest filtering carries the anti-map-radar
  rationale. Owner: `NETWORK_PROTOCOL.md` / `WORLD_CHANNELS.md` OQs.
- **S6 / S9 — DB concurrency discipline**: explicit row-lock/lock-order/serializable-
  retry rules for multi-row swaps + the parameterized-SQL-only rule. Owner:
  `DATABASE_PERSISTENCE.md` OQ (next revision of that doc).
- **P9 — operational APM unowned**: P95/P99 tick latency, query time, throughput, CCU,
  alerting have no owning doc (`TELEMETRY_ANALYTICS.md` is balance-only). Proposed for
  the backend coding pass as an ops runbook.
- **Report/moderation durable schema** missing from `social` schema
  (`DATABASE_PERSISTENCE.md` §3.3).

## Open technical decisions (by decider)

**Owner-priced (money/vendor calls — cannot be decided by agents):**
hosting vendor/region/managed-Postgres vs self-run · RNG-audit retention window ·
failover/replication topology · storefront + CI + code-signing vendors · SSO and email
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
- Memory Bank governance: Fable = specs/gates, Opus = logic/audit, Sonnet = execution,
  Haiku = mechanical fill (`memory/systemPatterns.md` §2; `docs/60_agents/roles/ORG.md`).
- Keep files < 250 lines, diff-only edits, one concern per commit, validator-gated.
- After any merge, re-run `tools/md_graph.py` (connectivity) and `tools/validate.py`.

## Open Questions

- Should `memory/` be added to the validator's default scan scope (token/link checks
  currently cover `docs/` + root docs only)? Default: yes, at the next tools revision.
