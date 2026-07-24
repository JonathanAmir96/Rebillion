# VALIDATION.md — Pass/Fail Rules (Run on Every Batch)

Defines what makes a file valid. A generation batch lands only after passing every check; the
coding pass later implements this same contract as a CI validator (see
30_engineering/ENGINEERING_STANDARDS.md). Seeded at Phase A; finalized at Phase E with the
Open Questions rollup.

## 1. No forbidden tokens
The legacy-genre terms below may appear **in this file only** (it is the canonical banned
list; the validator exempts `VALIDATION.md` and nothing else). Anywhere else — docs, schemas,
content, comments — their presence makes the file invalid. Matching is case-sensitive on
whole words:

`STR` · `DEX` · `INT` · `LUK` · `HP` · `MP` · `meso` · `mesos`

Use the GLOSSARY.md replacements (`might`/`finesse`/`focus`/`fortune`, `life`, `essence`,
`shards`).

## 2. Referential integrity
Every named reference must resolve to its owner registry: `element` →
10_systems/ELEMENTS.md · `status` → 10_systems/STATUS_EFFECTS.md · `ai_profile` →
10_systems/AI_BEHAVIOR.md · effect `op` → 10_systems/SKILL_EFFECTS.md · animation state →
40_assets/ANIMATION_STATES.md · `drop_table`/pool → an existing file/entry under
50_content/drop_tables/ · `schema` → an existing file under 20_schemas/ · item/mob/map/npc/
quest/skill IDs → existing content entries. Broken reference = fail.

## 3. Schema conformance
Content files carry front-matter (`id`, `schema`, `references`) and every field required by
their schema doc; no unknown fields; enum values only from the owning registry.

## 4. ID uniqueness and range
Every ID is globally unique, matches its prefix format, and falls inside its reserved block in
ID_REGISTRY.md (including tier layout for mobs — e.g., a boss ID slot may not hold a normal).

## 5. World-graph soundness
Every portal targets an existing map **and** an existing spawn point on that map; every map is
reachable from `map_001`; no dead-end portals. One-way or intentionally terminal exits must be
marked `dead_end: true` in the map file. Cross-region edges must match the **authorized edge
set** exactly: WORLD_PLAN.md's edge tables (arc 1 + arc 2).
**Warn-only:** spawn-zone monster levels rise monotonically along ascending field-map ID order
on a region's main path (WORLD_PLAN.md §"Map order & monster gradient law") — a violation
warns, never fails.

## 6. Asset contract
Animated entities declare `animation_states` using only ANIMATION_STATES.md tokens and include
every state required for their entity class (e.g., elites/bosses must include `telegraph`).
Skill `animation` IDs follow 40_assets/SKILL_ANIMATION.md naming (`<skill_id>_cast`, actives
only); icon **assets** are named by 1:1 derivation from the entity `id` — skill
`ui_icon_skill_<line>_<NNN>`, item `ui_icon_item_<id stem>` — and content files store **no**
`icon` field (owner ruling 2026-07-24; 20_schemas/skill.schema.md rule 10 /
20_schemas/item.schema.md rule 16; asset naming 40_assets/SKILL_ANIMATION.md §5 /
40_assets/UI_ART_SPEC.md).
Appearance-style references resolve to the ID_REGISTRY.md `style_<category>_NN` blocks
(40_assets/CHARACTER_COMPOSITING.md). When a monster file carries
`animation_notes`, every key must be a state token present in that same file's
`animation_states`, and every value a non-empty string (20_schemas/monster.schema.md rule 11).

## 7. Open Questions rollup
Every doc ends with `## Open Questions`. Phase E collects every entry into the index at the
bottom of this file; an entry may only be dropped by resolving it in the owning doc.

## Batch protocol
Each Phase D batch runs checks 1–6 before landing (orchestrator's validator script); check 5
runs region-locally per batch and globally after the world-graph reconciliation pass; check 7
runs at phase gates. Fix-or-flag: a failing file is corrected in-batch or reverted — never
landed "to fix later."

## Open Questions
- (Phase E) Should the CI validator also lint flavor-text length (≤2 sentences) mechanically?
  Default: yes, warn-only.
- tools/validate.py's `item_use` ID ceiling (0060) predates the scroll block
  `item_use_0061`–`0100` (ID_REGISTRY.md) — raise it when scroll content mints (owner:
  validator/tools).
- **Resolved (2026-07-24, owner ruling): the icon field is derived-implicit — option (b).**
  Content stores no `icon` field; the asset id derives 1:1 from the entity `id` (schemas'
  rules 10/16, §6 above). Minted content was already compliant (zero stored fields), and
  tools/validate.py's unknown-field gate now correctly *enforces* the ruling by rejecting any
  stored `icon:`. No backfill needed.
