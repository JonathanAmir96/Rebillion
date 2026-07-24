# SCOPE.md — What This Design Tree Delivers

This run produces the **design-documentation tree only**: prose system docs, schema docs, and
machine-loadable YAML content. No game code, no generated art, no backend. A later coding pass
(briefed in `60_agents/`) implements against these docs in Godot 4.3+.

## Content totals (authoritative counts — v3, owner revision 2026-07-23)

| Category | Count | Notes |
|---|---|---|
| Islands | 5 | Emberfoot Isle (Lv 1–8) → ferry → Harthmoor Isle (Lv 8–40) → Deepway/longship → Frostpeak Isle (40–55), Arcane Reach (53–68), Voidshore (66–80) |
| Regions | 11 | Level-banded Lv 1 → 82 (authored arcs 1–2); see WORLD_PLAN.md |
| Maps | 324 | 12 towns, 30 interiors (incl. ferry + 3 longship decks), 153 fields, 95 dungeons (incl. 12 raid stage maps + 3 Deepway), 23 secrets, 11 boss arenas |
| Monsters | 234 | 178 normal + 45 elite + 11 boss |
| Raids | 4 | `raid_undervault` (15–22), `raid_mainspring` (32–40), `raid_deepfrost` (45–55), `raid_voidtide` (70–80); social/RAID.md |
| Drop tables | 234 + 11 pools | One per monster, plus one equip pool per region |
| Job lines | 4 | One per primary stat; novice → 1st (Lv 8) → 2nd (Lv 40, **branching: choose 1 of 2–3 specializations**, 10 specs total); 3rd tier deferred to future arcs |
| Skills | 98 | Per line: 6 first-job + 7 per specialization (bulwark/weaver ×3, keeneye/flicker ×2) + 4 novice |
| Items — equip | ~162 | 48 weapons, 60 armor, 32 accessories (T1–T12, Lv 1–78), 22 boss uniques (batched tables) |
| Items — use | ~34 | Tonics (7 tiers), cleanses, scrolls, foods (batched table) |
| Items — etc | ~181 | 16 materials per region (×11) + emberstone tiers (batched tables) |
| NPCs | 120 | Town-weighted; see ID_REGISTRY.md |
| Quests | 120 | Region-banded kill/collect/talk/reach chains, incl. 8 raid handler quests |
| Elements | 6 | Owner: 10_systems/ELEMENTS.md (`arcane` mobs appear only in Clockwork) |
| Status effects | 16 | Owner: 10_systems/STATUS_EFFECTS.md |
| AI profiles | 12 | Owner: 10_systems/AI_BEHAVIOR.md |
| Skill effect ops | 14 | Owner: 10_systems/SKILL_EFFECTS.md |
| Animation states | 12 | Owner: 40_assets/ANIMATION_STATES.md |

The game's level cap is **300 (initial design, owner revision)**. This run authors the
**first two arcs**: arc 1 spans Lv 1–42 on Emberfoot/Harthmoor; arc 2 (v3 revision) spans
Lv 40–82 across the three far isles, reached via the Lv-40 Deepway passage and the paid
longship network. Leveling past arc 2 is a slow grind on Voidshore endgame maps and raids
until future arcs land. 10_systems/LEVELING.md designs the full curve to 300
(formula-first) with detail tables for the authored range.

## In scope (this run)
- All docs and content listed in GENERATE.md §2, including locked Appendices A–C verbatim.
- Social/economy systems (trading, party, guild, chat, mail, market): full design docs or
  honest stubs, all flagged server-dependent; **no implementation**.
- `VALIDATION.md` pass/fail rules, run against every content batch during generation.
- Coding-pass phase briefs in `60_agents/` (Phase E).

## Out of scope (this run)
- GDScript/scenes/engine work of any kind; art or audio asset generation (PixelLab briefs are
  templates only); networking/backend; balancing beyond first-pass budget tables; localization
  (US English only); monetization implementation (direction fixed by owner amendment MON-001 in
  10_systems/MONETIZATION.md — cosmetic-only, no pay-to-win; no store content authored this
  run); character cosmetics beyond equipment (a zero-stat cosmetic layer is reserved by
  MONETIZATION.md §3.1 for a future arc).

## Deliberate scope limits
- One weapon type per job line (4 total). Armor is class-agnostic with stat leans.
- The 2nd advancement (Lv 40) **branches**: each line chooses one of 2–3 permanent
  specializations (v3 revision; rules and rosters in JOBS.md). **3rd-tier jobs are designed
  in name only** — their skills, quests, and regions ship with future arcs on the road to
  cap 300, and their skill IDs stay reserved in ID_REGISTRY.md.
- The ART_BIBLE `rift` biome is reserved for future islands/expansions and unused in this
  run's content (frostpeak / arcane_reach / voidshore entered use with arc 2).
- Palette-swap monster variants are permitted later but are **not** authored here and do not
  count toward the 234 designs.
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
- The v2 B-revision wave landed (docs/phase_reports/, phases F–H); the v3.1 straggler sync is
  tracked in docs/phase_reports/SYNC_AUDIT_v3_2026-07-23.md — flag any remaining straggler
  references there.
