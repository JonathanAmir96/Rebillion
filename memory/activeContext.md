# activeContext.md — Current State, Priorities, Open Decisions

> Memory Bank file 4/5. Snapshot as of **2026-07-24, post md-audit** (audit wave merged
> to `main`; the six audit calls owner-ruled the same day). Newest owner decisions
> live in root `memory.md`; this file distills what the *next* session must know
> before generating anything.

## Current repository state

- **Single canon** (owner-ruled 2026-07-24): the five-island / two-arc world — 11
  regions, 324 maps, 234 monsters, 11 bosses, 5 raids, branching 2nd jobs, authored
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
- **2026-07-24 design layers** (newest last; details in root `memory.md`): social
  package + balance pass + `COSMETICS.md` → full-tree contradiction sweep (27 findings,
  all resolved; UA-001/ES-001) → gameplay-loop review (`UI_WINDOWS.md`, HUD decisions,
  mockup) → combo layer (`COMBO_SYSTEM.md`, advancement quest lines) → composited
  character sprites + entry flow + display (`CHARACTER_COMPOSITING.md`, `ACCOUNT.md`,
  `DISPLAY.md`, 4-slot roster, AB-002) → wiki generator + per-monster animation notes
  (all 234 authored) → **repo-wide md audit** (this branch: ~27 contradiction rulings,
  connectivity 117/117, quest-exp regen landed, 6 mock-ups, UA-002/ES-002;
  `docs/phase_reports/MD_AUDIT_REPORT_2026-07-24.md`) → **live-ops layer**
  (`BATTLE_PASS.md` Wayfarer's Charter + `GACHAPON.md` Cogwork Capsule, MON-001/PA-001)
  → **design-critic pass 01** (`docs/phase_reports/design_reviews/REVIEW_2026-07-24_01.md`):
  fifth raid `raid_orrery` (56–69, no new map/mob IDs) closing the Lv 56–69 raid drought,
  capsule amendment **PA-002** (10 tickets/week **per account**; prizes and tickets
  bind-on-dispense — no vendor, no trade, no market listing), and the Gilded Charter fee
  made **progressive by `level` band** (`ECONOMY.md` §4.4, 2,500 → 60,000, was flat 6,000).
- **Pacing retune** (owner-ratified): Lv 40 ≈ 30 h, Lv 80 ≈ 166 h, Lv 100 ≈ 300 h;
  `kills_per_level = round(20 + 6.6L + 0.20L²)` frozen through Lv 100. Quest `exp`
  content is now **regenerated** against it (`tools/regen_quest_exp.py`, 120/120).

## Immediate priorities (ordered)

1. **Phase E — coding-pass briefs.** The remaining generation phase: per-feature
   implementation briefs + the VALIDATION §7 Open-Questions rollup index. Route to
   Opus-tier per ORG.md.
2. **Balance pass (D-gate retune).** ECONOMY prices/fees, tonic bite (overshoots
   ~20–30% target past Superior), DROPS anchors, WORLD_CHANNELS capacity targets
   (sized against the old two-island world), raid band vs Millbrook ceiling; input:
   the regenerated quest-exp table (MD_AUDIT_REPORT Appendix A).
3. **Art pass.** PixelLab briefs per `ART_GENERATION_RUNBOOK.md` — no longer blocked:
   the 16 px tile-scale lock and the DISPLAY.md resolution law are resolved; the
   compositing spike gate (base body + 1 outfit + 2 hairs, COMPOSITING §9) runs first.
4. **Backend coding pass** (post-briefs): Elixir/OTP skeleton per the Phase I suite;
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
- COLLECTIONS set-completion `shards` grant needs a 4th-faucet ECONOMY amendment.
- Resolved & removed from this list 2026-07-24: the FTUE Lv-8 gate (front-loaded grants
  verified — quest sum 3,804 ≥ 3,800, `ONBOARDING_FTUE.md` §2), the ITEMS/JOBS registry
  re-blocks (landed long since; stale OQs closed), and **all six md-audit calls**
  (owner-ruled same day — icon derived-implicit · SPAWN count model · trigger_zones ·
  shield/overall stays tracked debt · Agent-3 runs AB-/UA-/ES- · coach 3+-tier =
  future headroom; see `memory.md`).

**Known design debts (non-blocking, tracked in owning docs):** shields/overalls/
scrolls content integration (blocks 0181–0200, `item_use_0061`–`0100` reserved;
validator `item_use` ceiling needs raising when scrolls mint; now discoverable from
ITEMS.md's own OQ) · COLLECTIONS/AUDIO deep hooks · `map_109` `from_clockwork` chute
residue · wiki_gen.py generates no job pages yet (WIKI_EXPORT lists 7 page types).

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
