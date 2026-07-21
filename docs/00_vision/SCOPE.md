# SCOPE.md — What This Design Tree Delivers

This run produces the **design-documentation tree only**: prose system docs, schema docs, and
machine-loadable YAML content. No game code, no generated art, no backend. A later coding pass
(briefed in `60_agents/`) implements against these docs in Godot 4.3+.

## Content totals (authoritative counts)

| Category | Count | Notes |
|---|---|---|
| Regions | 12 | Level-banded Lv 1 → 100+; see WORLD_PLAN.md |
| Maps | 200 | 4 towns, 17 interiors, 94 fields, 54 dungeons, 16 secrets, 15 boss arenas |
| Monsters | 150 | 112 normal + 23 elite + 15 boss (11 region bosses + 4 Rift raid bosses) |
| Drop tables | 150 + 12 pools | One per monster, plus one equip pool per region |
| Job lines | 4 | One per primary stat; novice → 1st (Lv 8) → 2nd (Lv 30) → 3rd (Lv 60) |
| Skills | 84 | 21 per job line (6 first / 7 second / 8 third, passives included) |
| Items — equip | ~144 | 40 weapons, ~80 armor, ~24 accessories, 30 boss uniques (batched tables) |
| Items — use | ~36 | Tonics, cleanses, scrolls, foods (batched table) |
| Items — etc | ~197 | 16 materials per region + 5 emberstone tiers (batched tables) |
| NPCs | 84 | Town-weighted; see ID_REGISTRY.md |
| Quests | 90 | Region-banded kill/collect/talk/reach chains |
| Elements | 6 | Owner: 10_systems/ELEMENTS.md |
| Status effects | 16 | Owner: 10_systems/STATUS_EFFECTS.md |
| AI profiles | 12 | Owner: 10_systems/AI_BEHAVIOR.md |
| Skill effect ops | 14 | Owner: 10_systems/SKILL_EFFECTS.md |
| Animation states | 12 | Owner: 40_assets/ANIMATION_STATES.md |

Level cap is **100**. Rift monsters may reach level 105; post-cap character progression is an
Open Question (below), not a promise.

## In scope (this run)
- All docs and content listed in GENERATE.md §2, including locked Appendices A–C verbatim.
- Social/economy systems (trading, party, guild, chat, mail, market): full design docs or
  honest stubs, all flagged server-dependent; **no implementation**.
- `VALIDATION.md` pass/fail rules, run against every content batch during generation.
- Coding-pass phase briefs in `60_agents/` (Phase E).

## Out of scope (this run)
- GDScript/scenes/engine work of any kind; art or audio asset generation (PixelLab briefs are
  templates only); networking/backend; balancing beyond first-pass budget tables; localization
  (US English only); monetization (none planned); character cosmetics beyond equipment.

## Deliberate scope limits
- One weapon type per job line (4 total). Armor is class-agnostic with stat leans.
- Job advancement is linear (no branching) to keep 84 skills coherent.
- Palette-swap monster variants are permitted later but are **not** authored here and do not
  count toward the 150 designs.
- Map YAMLs describe structure (zones, spawns, portals, interactables) at design granularity,
  not tile-exact geometry; tile work happens in the engine pass.

## Phase deliverables (gates per GENERATE.md §5)
- **A** Vision & vocabulary: 00_vision/*, ID_REGISTRY.md, WORLD_PLAN.md, VALIDATION.md seed.
- **B** Systems: all 10_systems/* and 15_maps_system/*.
- **C** Schemas & asset specs: 20_schemas/*, 40_assets/*, Appendices A–C placed verbatim.
- **D** Content: all 50_content/* (region-batched, validated per batch).
- **E** Coding-pass briefs: 60_agents/*, VALIDATION.md finalized with Open Questions rollup.

## Open Questions
- Post-cap (Lv 100) progression: paragon-style trickle, gear-only, or nothing at launch?
  Owner: LEVELING.md at Phase B; default assumption for now is gear-only.
- Should secret maps count toward region completion metrics used by quests? Default: no.
