# VALIDATION.md — Pass/Fail Rules (Run on Every Batch)

Defines what makes a file valid. A generation batch lands only after passing every check; the
coding pass later implements this same contract as a CI validator (see
30_engineering/ENGINEERING_STANDARDS.md). Seeded at Phase A; finalized at Phase E with the
Open Questions rollup.

**Ownership:** this file is **producer-owned**. Any role that needs a check added or reworded
(most often ROLE_SYSTEMS_ARCHITECT, whose Definition-of-Done implies validation rules)
**proposes the wording to the producer for sign-off** — the producer is the only role that
edits VALIDATION.md. This resolves the earlier producer-vs-architect ownership tangle.

## 1. No forbidden tokens
The legacy-genre terms below may appear **in this file only** (it is the canonical banned
list; the validator exempts `VALIDATION.md` and nothing else). Anywhere else — docs, schemas,
content, comments — their presence makes the file invalid. Matching is case-sensitive on
whole words:

`STR` · `DEX` · `INT` · `LUK` · `HP` · `MP` · `meso` · `mesos` · `PQ` · `party quest` ·
`pq_` (as an ID prefix)

Use the GLOSSARY.md replacements (`might`/`finesse`/`focus`/`fortune`, `life`, `essence`,
`shards`), and **raid** / `raid_<name>` for the instanced co-op runs (owner ruling
2026-07-24; owner doc `10_systems/social/RAID.md`). `party quest` matches
case-insensitively and hyphenated (`party-quest`); `PQ` matches case-sensitive whole-word.

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
Every portal targets an existing map **and** an existing spawn point on that map. Every map is
reachable from `map_001` via walk portals (`edge`/`door`); the test is **reachability, not
acyclicity** — the world is the Harthmoor **ring**, so cycle-forming edges are expected, not
faults, in particular the Tidewatch→Ashfall ring closure (`map_088`→`map_140`) and the two
Clockwork gates (`map_141`→`map_177` and `map_121`→`map_188`). Every walk portal must have a
matching reverse portal on its destination map **unless** it is a one-way or intentionally
terminal exit (e.g. the Sunken Depths spur), which must be marked `dead_end: true` in the map
file; a `dead_end: true` portal is exempt from the reverse-portal requirement, and **no
unmarked** one-way portal may exist. The set of cross-region walk edges must be **exactly**
`WORLD_PLAN.md`'s "Cross-region walk edges" table — every table row present, and no
cross-region walk edge beyond that table. `coach`-kind portals are a menu-driven paid service
between fixed coach stations, **not** walk edges: they are excluded from the
cross-region-edge match and from the reverse-portal / `dead_end` checks.
**Warn-only:** spawn-zone monster levels rise monotonically along ascending field-map ID
order on a region's main path (WORLD_PLAN.md §"Map order & monster gradient law") — a
violation warns, never fails.

## 6. Asset contract
Animated entities declare `animation_states` using only ANIMATION_STATES.md tokens and include
every state required for their entity class (e.g., elites/bosses must include `telegraph`).
Skill `animation` IDs follow 40_assets/SKILL_ANIMATION.md naming.

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
- `tools/validate.py` was authored against the v3-lineage counts (11 regions, 324 maps,
  T1–T12) and predates both the v2 reconciliation merge and the `item_use_0061`–`0100`
  scroll block — its configuration must be re-aimed at the v2 canon (ID_REGISTRY.md) before
  it gates any batch (owner: producer/tools).
