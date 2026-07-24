# PHASE_REPORT — Phase A (Vision & Vocabulary)

Status: **complete**. Written by the orchestrator (top tier, per §7: foundations).

## Files created
- `README.md` (orchestrator addition: repo entry point)
- `docs/00_vision/PILLARS.md` — 7 pillars + anti-pillars
- `docs/00_vision/SCOPE.md` — authoritative content counts and phase deliverables
- `docs/00_vision/GLOSSARY.md` — canonical tokens: 4 primary stats, 11 derived, meta,
  6 elements, 16 statuses, 12 AI profiles, 14 effect ops, 6 targeting modes, 12 animation
  states, 6 map types, 9 equip slots, 4 weapon types, tiers/rarities/sizes, ID prefixes,
  region slugs
- `docs/ID_REGISTRY.md` — reserved blocks: maps 001–200, mobs 001–150 (tier slots), items
  (equip 0001–0300 incl. boss uniques 0201–0216; use 0001–0060 with 16 well-known IDs; etc
  0001–0200 incl. Emberstone I–V at 0193–0197), skills (per-line 001–030 + novice), NPCs
  001–120 (84 authored), quests 001–120 (90 authored), drop tables + region equip pools
- `docs/WORLD_PLAN.md` — 8 region sections: map-type allocation per ID, cross-region edges,
  coach/ferry transport network, spawn-point conventions, monster slot layouts, element mixes,
  boss seeds, NPC/quest/etc blocks
- `docs/VALIDATION.md` (seed) — 7 checks + batch protocol; sole holder of the banned-token
  list

## Tokens / IDs reserved
All enum families above are **canonical**; owner docs (Phase B/C) define semantics but may not
rename or extend without a GLOSSARY Provisional entry. Job line tokens are the one deliberate
Provisional (JOBS.md proposes at Phase B; promoted at the B gate).

## Deviations from GENERATE.md
- Added `README.md` and `docs/phase_reports/` (not in the §2 tree) for repo usability and
  durable phase reports. No other structural changes.

## Open Questions (rolled up)
- **Post-cap progression model (SCOPE.md → LEVELING.md at B) — resolved:**
  no hard wall — the exp curve keeps applying by formula past Lv 42, but the level-difference
  dampener makes out-leveling the arc a slow grind; endgame progression is primarily the gear
  chase (T6 +9, boss uniques, scrolls). Paragon/prestige is deferred post-launch. See
  `docs/10_systems/LEVELING.md` §6.
- Secret maps in completion metrics (SCOPE.md; default no).
- **`haste` split into move/attack components (GLOSSARY.md → STATS.md at B) — resolved at the
  B gate:** kept combined; conversion percentages owned by
  `docs/10_systems/STATS.md` §5. See `docs/00_vision/GLOSSARY.md` Open Questions.
- Reserved-growth block overflow procedure (ID_REGISTRY.md; extend-never-renumber).
- Terminus regions' return shortcut (WORLD_PLAN.md → MAP_CONNECTIONS.md at B).
- **Interiors combat-free confirmation (WORLD_PLAN.md → MAPS_SYSTEM.md at B) — resolved:**
  `town` and `interior` maps are combat-free (no `spawn_zones`, no hostile monster_body, no
  arena boss); see `docs/15_maps_system/MAPS_SYSTEM.md` §6.
- Flavor-length lint mechanical? (VALIDATION.md → Phase E; default warn-only).
- Inherited from locked appendices (log only): bitmap font license; boss >96px policy;
  UI window drag policy; guild crest shape/symbol count lock.
