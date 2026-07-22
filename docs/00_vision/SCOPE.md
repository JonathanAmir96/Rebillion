# SCOPE.md — What This Design Tree Delivers

This run produces the **design-documentation tree only**: prose system docs, schema docs, and
machine-loadable YAML content. No game code, no generated art, no backend. A later coding pass
(briefed in `60_agents/`) implements against these docs in Godot 4.3+.

## Content totals (authoritative counts — v2, owner revision 2026-07-21)

| Category | Count | Notes |
|---|---|---|
| Islands | 2 | Emberfoot Isle (training, Lv 1–8, 16 maps) → ferry → Harthmoor Isle (Lv 8–40, 184 maps) |
| Regions | 8 | Level-banded Lv 1 → 42 (authored arc); see WORLD_PLAN.md |
| Maps | 200 | 6 towns, 20 interiors (incl. ferry), 99 fields, 53 dungeons (incl. 6 PQ maps), 14 secrets, 8 boss arenas |
| Monsters | 150 | 118 normal + 24 elite + 8 boss |
| Party quests | 2 | `pq_undervault` (Lv 15–22), `pq_mainspring` (Lv 32–40); social/PARTY_QUEST.md |
| Drop tables | 150 + 8 pools | One per monster, plus one equip pool per region |
| Job lines | 4 | One per primary stat; novice → 1st (Lv 8) → 2nd (Lv 40); 3rd+ tiers deferred to future arcs |
| Skills | 56 | 13 per job line (6 first / 7 second, passives included) + 4 novice |
| Items — equip | ~86 | 24 weapons, 30 armor, 16 accessories, 16 boss uniques (batched tables) |
| Items — use | ~30 | Tonics, cleanses, scrolls, foods (batched table) |
| Items — etc | ~133 | 16 materials per region + 5 emberstone tiers (batched tables) |
| NPCs | 84 | Town-weighted; see ID_REGISTRY.md |
| Quests | 90 | Region-banded kill/collect/talk/reach chains, incl. 4 PQ handler quests |
| Elements | 6 | Owner: 10_systems/ELEMENTS.md (`arcane` mobs appear only in Clockwork) |
| Status effects | 16 | Owner: 10_systems/STATUS_EFFECTS.md |
| AI profiles | 12 | Owner: 10_systems/AI_BEHAVIOR.md |
| Skill effect ops | 14 | Owner: 10_systems/SKILL_EFFECTS.md |
| Animation states | 12 | Owner: 40_assets/ANIMATION_STATES.md |

The game's level cap is **300 (initial design, owner revision)**. This run authors the
**first arc**: maps and monsters span Lv 1–42, and leveling past the arc is a slow grind on
endgame maps and party quests until future arcs land. 10_systems/LEVELING.md designs the
full curve to 300 (formula-first) with detail tables for the authored range.

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
- Job advancement is linear (no branching); **3rd jobs are designed in name only**
  (JOBS.md future-expansion section) — their skills, quests, and regions ship with future
  arcs on the road to cap 300, and their skill IDs stay reserved in ID_REGISTRY.md.
- Four ART_BIBLE biomes (frostpeak, arcane_reach, voidshore, rift) are reserved for future
  islands/expansions and unused in this run's content.
- Palette-swap monster variants are permitted later but are **not** authored here and do not
  count toward the 150 designs.
- Map YAMLs describe structure (zones, spawns, portals, interactables) at design granularity,
  not geometry; exact foothold segments and terrain-chunk placement happen in the engine
  pass (v2.4: terrain is Maple-style footholds + painted chunks per ART_BIBLE amendment
  AB-001 — a deliberate art-scope increase over reusable tilesets, owner-approved).

## Phase deliverables (gates per GENERATE.md §5)
- **A** Vision & vocabulary: 00_vision/*, ID_REGISTRY.md, WORLD_PLAN.md, VALIDATION.md seed.
- **B** Systems: all 10_systems/* and 15_maps_system/*.
- **C** Schemas & asset specs: 20_schemas/*, 40_assets/*, Appendices A–C placed verbatim.
- **D** Content: all 50_content/* (region-batched, validated per batch).
- **E** Coding-pass briefs: 60_agents/*, VALIDATION.md finalized with Open Questions rollup.

## Open Questions
- Should secret maps count toward region completion metrics used by quests? Default: no.
- v2 revision arrived after Phase B: system docs written for the Lv 100 world are patched by
  the B-revision wave (tracked in docs/phase_reports/); flag any straggler references.
