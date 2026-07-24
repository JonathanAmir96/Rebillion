# memory.md — State + Decisions Log

Written by the v2-reconciliation producer run (2026-07-24), per CLAUDE.md ("For future
Claude sessions"). Read this after README.md → GLOSSARY.md → WORLD_PLAN.md.

## Current state (2026-07-24)

- **Phases A–C complete; Phase D (content) not started — no content IDs minted.**
- The tree was split-brain after the v2 owner revision (2026-07-21): vision/world/registry
  docs were v2, but `10_systems/`, `15_maps_system/`, `20_schemas/`, and parts of the org
  charter were still v1 (cap 100, gates 8/30/60, Rift/raid content, free waygates).
- Audit: `docs/phase_reports/DESIGN_ORG_REVIEW_2026-07-24.md`. This run executes its §6
  dispatch plan; results in `docs/phase_reports/PHASE_B2_REPORT.md`.
- Branch note: the review's dispatch prompt named `claude/v2-reconciliation-fixes`; the
  work actually landed on `claude/game-design-org-review-dispatch-wq01tp` (the session's
  designated branch).

## Decision Contract (owner-ratified 2026-07-24; overrides any stale doc text)

Recorded verbatim from DESIGN_ORG_REVIEW_2026-07-24.md §6:

> C1. Level cap 300. Arc 1 authors Lv 1–42 only.
> C2. Job gates: 1st Lv 8 · 2nd Lv 40 · 3rd Lv 80. The Lv-80 gate is canonized NOW but
>     3rd-job content (skills 014–021, quests, instructors) stays reserved for future arcs.
> C3. Leveling curve: exp_per_kill_normal(L) = round(4·L^1.3) unchanged;
>     kills_per_level(L) = round(20 + 0.26·L²);
>     exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L).
>     Played-time model (canonical): /played per level = kills_per_level(L) / (480 × 0.70)
>     — hunting occupies ≈70% of playtime at ≈480 at-level kills/h. Anchors to publish:
>     Lv 40 ≈ 18 h · Lv 42 ≈ 21 h · Lv 60 ≈ 58 h · Lv 80 ≈ 134 h (≈1 month @ 4–5 h/day)
>     · Lv 100 ≈ 260 h. Lv 100–300 tail: leave as an explicit Open Question with these
>     anchors fixed (future-arc segment law), do not invent it.
> C4. Counts (canonical): 8 bosses / 16 boss uniques; 150 monsters = 118 normal / 24
>     elite / 8 boss; 200 maps = 6 towns / 20 interiors / 99 fields / 53 dungeons /
>     14 secrets / 8 arenas; skills authored this run = 13 per line + 4 novice = 56
>     (skill_<line>_014–021 reserved). Regions r01–r08 only; frostpeak / arcane_reach /
>     voidshore / rift are reserved future biomes and must not drive any active rule.
> C5. Travel: paid Harthmoor Coachworks (shards) + Harborwind Ferry. waygate /
>     waygate_console are retired tokens — replace with coach / coach_stop per GLOSSARY.
> C6. Bind/bank towns = the 6 v2 towns (Millbrook Central, Cindershelf, Mossmere,
>     Tidewatch Port, + the remaining ring towns per WORLD_PLAN). "Arcane Sanctum" is
>     invalid. Job trainers = each line's home-town instructor (Bulwark→Cindershelf,
>     Keeneye→Tidewatch Port, Weaver→Mossmere, Flicker→Millbrook), 2nd advancement via
>     the same instructor + Clockwork trial per WORLD_PLAN v2.3 — not Millbrook-only.
> C7. Gear band gap: extend weapon/armor tiers with one Lv-40 tier so the Lv 40–42 band
>     is covered (new ID range in a new commit — never renumber existing blocks).
> C8. Party quests: pq_undervault / pq_mainspring rules live in a new
>     docs/10_systems/social/PARTY_QUEST.md (GLOSSARY and SCOPE already point there);
>     PARTY.md drops its Rift-raid section and references it.
> C9. Rift / R12 / raid bosses (mob_147–150 as raid tier) / 150× raid exp / 12-region
>     pools (r09–r12) / Lv-105 monsters: all v1 content — delete or move to explicitly
>     marked "reserved for future arcs" notes. mob_145–150 are Clockwork elites + the
>     Custodian boss per ID_REGISTRY.

### C3′ — pacing amendment (owner directive, 2026-07-24, later same day)

The owner reviewed the C3 anchors mid-run and ruled the pace too fast: **"is too quick to
level 40 I think need 30hours... lvl 100 for now 300hours."** Amended curve (same
exp-per-kill formula, same ÷(480 × 0.70) played-time model):

> kills_per_level(L) = round(20 + 6.6·L + 0.2·L²)

Ratified anchors (supersede C3's): **Lv 40 ≈ 30 h · Lv 100 ≈ 300 h** ("for now").
Derived anchors: Lv 8 ≈ 1 h · Lv 42 ≈ 33.5 h · Lv 60 ≈ 80 h · **Lv 80 ≈ 166 h** — the
3rd-job gate moves from ≈1 month to ≈5–6 weeks at 4–5 h/day; flagged to the owner at
amendment time, not objected to. The Lv 100–300 tail stays an Open Question per C3.

C7 implementation note: the six v2 towns are Emberfoot Village, Rosen Harbor, Millbrook
Central, Mossmere, Tidewatch Port, Cindershelf (WORLD_PLAN v2.3). The Lv-40 gear tier
minted inside existing `item_equip` sub-block slack (28 weapons / 35 armor authored) —
see ID_REGISTRY.md tier-7 note.

## Run outcome (2026-07-24, end of reconciliation run)

All waves complete; QA verdict PASS-WITH-FLAGS and every flag resolved in-run except the
locked-file item (ART_BIBLE reserved-biome annotation — routed to the art director's
amendments channel). Full record: `docs/phase_reports/PHASE_B2_REPORT.md` (§4 has the
open-questions rollup). Travel economy now published in ECONOMY §7 (coach 300/1,000/1,800
by ring hop · ferry 150 · Return Scroll 2,500 as a paid recall).

## Decisions log

- 2026-07-21 (owner) — v2 world revision: cap 300, two islands, 8 regions/bosses, paid
  coach travel, 3rd jobs reserved. Recorded in CLAUDE.md, GLOSSARY, WORLD_PLAN, SCOPE.
- 2026-07-24 (owner, via DESIGN_ORG_REVIEW) — Decision Contract C1–C9 above: 3rd-job gate
  Lv 80; leveling coefficient 0.26; canonical ÷0.70 played-time table model; tier-7 gear;
  PARTY_QUEST.md created; Rift/raid v1 content deleted or explicitly reserved.
- 2026-07-24 (org) — `docs/15_maps_system/` ownership assigned to ROLE_SYSTEMS_ARCHITECT;
  ROLE_MONSTER_DESIGNER added before Phase D; ART_GENERATION_RUNBOOK ownership resolved
  (integration engineer owns, art director holds QA veto).
- 2026-07-24 (owner, mid-run) — **C3′ pacing amendment** (section above): Lv 40 ≈ 30 h,
  Lv 100 ≈ 300 h; curve `20 + 6.6·L + 0.2·L²`; Lv 80 lands ≈ 166 h (supersedes the
  "1 month to 3rd job" target).
- 2026-07-24 (producer) — Millbrook Return Scroll kept as `item_use_0013` but ruled a
  shard-priced vendor consumable (2,500) — no free warps of any kind (C5); coach/ferry
  fares published in ECONOMY §7.

## Open questions rollup (live copies live in each doc's own section)

- Lv 100–300 curve tail segment law — future-arc owner call (C3 fixes anchors ≤100 only).
- 480 kills/h and 70%-hunting constants are unmeasured; Phase D spawn/TTK data re-verifies.
- run_speed 128 px/s (MAP_TRAVERSAL) vs base_move_speed 200 px/s (COMBAT_FORMULA) — see
  the owning docs' Open Questions if not resolved by this run.

## For the next session

Phase D (content generation) is next: region-scoped sub-agents, exemplar-first,
validator-gated, staffed per `docs/60_agents/roles/ORG.md` (including the new
ROLE_MONSTER_DESIGNER). The `tools/` validator still does not exist — VALIDATION.md checks
are manual until it lands.
