# PHASE_REPORT — Arc 2 Plan (v3 owner revision, 2026-07-23)

Status: **complete** (design-doc wave; Phase D content for R9–R11 not yet started).
Orchestrated per `docs/60_agents/roles/ORG.md`: producer + 8 role agents (all hard-tier
tasks routed to Opus-class agents), each owning disjoint files; producer performed the
gate reconciliation (GLOSSARY / ID_REGISTRY / SCOPE / CLAUDE.md) and all commits.

## The owner revision (summarized)

1. **Second arc, Lv 40–80**, with a significant per-level pace (session-scale levels).
2. **Branching 2nd jobs at Lv 40** — 2–3 specializations per line, each with its own
   identity (repeals the "linear, no branching" scope law).
3. Access to arc 2 **only** through a single main-island city via a 3-map **underground
   passage** that opens at Lv 40, surfacing on a new island; **three new islands** total,
   linked to the main island by a paid, MapleStory-style **scheduled ship** (2–3 min sail).
4. **Raids** replace "party quests" as the term; new raids at Lv 45–55 and Lv 70–80.
5. More obtainable items.

## Producer decisions (binding)

- Islands = the three reserved ART_BIBLE biomes: **Frostpeak Isle** (`frostpeak`, R9,
  Lv 40–55, maps 201–244), **Arcane Reach** (`arcane_reach`, R10, Lv 53–68, maps 245–284),
  **Voidshore** (`voidshore`, R11, Lv 66–80, maps 285–324). `rift` stays reserved.
- Passage city: **Cindershelf** (mining town, north Harthmoor) → **the Deepway**
  (`map_201`–`map_203`, `level_gate: 40`) → Frosthaven (`map_204`).
- Ship: the **Harthmoor Longship Line** from Tidewatch Port (`map_071`); full network to
  and among the far isles; new `longship` portal kind (paid + scheduled).
- Raids: `pq_*` → `raid_*` rename; new `raid_deepfrost` (45–55, stages 240–242, finale
  244) and `raid_voidtide` (70–80, stages 320–322, finale 324). Party size 3–6 everywhere.
- Specializations: bulwark 3 (Ironbrand/Stoneguard/Warcaller), keeneye 2
  (Pathstalker/Sureshot), weaver 3 (Runeweaver/Cindercall/Frostbind), flicker 2
  (Duskstep/Wildcard); existing v2 2nd-job rosters became spec-#1 rosters verbatim.
- Items: equip tiers T7–T12 (Lv 43–78) carved from the never-minted `0231`–`0300` reserve;
  Sovereign/Mythic tonic tiers at `item_use_0017`–`0020`; boss uniques 0217–0222.

## Files changed (by owner)

- **World:** WORLD_PLAN.md → v3 (R9–R11 sections, Deepway + longship edges, raids).
- **Systems:** JOBS.md → v3 branching (+SKILL_SYSTEM.md gate patches) · LEVELING.md → v3
  (cap 300, Lv>80 softcap continuation, arc-2 pacing ≈90 played hours) · ITEMS.md → v3
  (T1–T12 ladder; also reconciled leftover v1 tier tables) · new social/RAID.md (owner of
  raid rules) · MAP_CONNECTIONS.md + ECONOMY.md §7 (longship, level_gate, fares).
- **Debt reconciliation (flagged during the wave, fixed by two follow-up agents):**
  the stale v1 "Rift raid" model in PARTY/SPAWN/DROPS/COMBAT_FORMULA/QUESTS re-aimed at
  the four v3 raids; the retired `waygate` model purged from 15_maps_system/*,
  DEATH_PENALTY.md, map.schema.md, npc.schema.md in favor of coach + longship.
- **Producer gate:** GLOSSARY (slugs r09–r11, Raids family, longship tokens, spec names),
  ID_REGISTRY → v3 (all blocks above; skills re-blocked to `_060` per line), SCOPE → v3
  counts (324 maps / 234 monsters / 4 raids / 98 skills / 120 NPCs / 120 quests),
  CLAUDE.md current-state, this report.

## Known stragglers (flagged, not fixed here)

- STATS.md §4.2 growth table still framed for the Lv-100 world (cited by LEVELING v3 OQ).
- ENHANCEMENT.md: arc-2 emberstone band mapping + its §4 worked example cites the old T6
  values (ITEMS.md OQ; `item_etc_0198` proposed as Emberstone VI in ID_REGISTRY OQ).
- ECONOMY.md §4.1 tonic price bands predate v2 compression and lack Sovereign/Mythic rows
  (ITEMS.md OQ).
- Assorted Lv-100-era phrasing in DROPS/DEATH_PENALTY worked examples (harmless numbers,
  listed in the respective docs' Open Questions).
- MAP_INTERACTABLES/HUD hooks for the longship departure timer UI (MAP_CONNECTIONS OQ).

## Open Questions

- Phase D for R9–R11 (content YAML) follows the established region-batch pattern; the
  raid stage maps and 6 new spec skill YAMLs are the only new content shapes.
- 3rd-tier job mapping onto branched specs (one capstone per line vs per-spec) — JOBS.md.
- Longship mid-sail ambush event — MAP_CONNECTIONS.md (deferred, mirrors the ferry OQ).
