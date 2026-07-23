# 50_content — Machine-Loadable Content (values + references only)

Phase D content. Every file here holds **values and references**, never rule text: it links to
the system doc that owns a number/rule, and to the schema that owns its shape. No rule is restated
(CLAUDE.md Law 2). US spelling everywhere; GLOSSARY tokens only (VALIDATION.md §1).

## Directory layout

| Path | Holds | Schema (`docs/20_schemas/`) |
|---|---|---|
| `maps/map_NNN.yaml` | one map | `map.schema.md` |
| `monsters/mob_NNN.yaml` | one monster | `monster.schema.md` |
| `drop_tables/drop_mob_NNN.yaml` | one per monster (number matches `mob_NNN`) | `drop_table.schema.md` |
| `drop_tables/pools.yaml` | the **single shared** region-pools file (`id: drop_pools`; all 12 `pool_equip_rNN`) | `drop_table.schema.md` |
| `items/equip/*.yaml` · `items/use/*.yaml` · `items/etc/*.yaml` | **batch tables** (many rows/file), not one-file-per-item | `item.schema.md` |
| `npcs/npc_NNN.yaml` | one NPC | `npc.schema.md` |
| `quests/quest_NNN.yaml` | one quest | `quest.schema.md` |
| `skills/<line>/skill_<line>_NNN.yaml` | one skill (`<line>` = `bulwark`/`keeneye`/`weaver`/`flicker`/`novice`) | `skill.schema.md` |

Items and skills are **subdivided by their own schema's File-conventions** (item.schema §File
conventions; skill.schema §File conventions) — they are not flat under `items/`/`skills/`.

## File naming

- One-entity files: filename stem **equals** the `id` (`map_204.yaml` → `id: map_204`). Zero-padded
  to the width its ID prefix uses (`map_NNN`, `mob_NNN`, `npc_NNN`, `quest_NNN`, `drop_mob_NNN`,
  `skill_<line>_NNN`; `item_*_NNNN` is 4-wide but items are batch-tabled, see below).
- Batch tables (`items/*`, `pools.yaml`): filename is the table stem; `id` is `item_table_<stem>`
  (or the fixed `drop_pools`). Row `id`s are the `item_*_NNNN` / `pool_equip_rNN` values.
- IDs are immutable and must sit inside their `docs/ID_REGISTRY.md` block (Law 3, VALIDATION §4).

## Front-matter contract (every file, VALIDATION §3)

```yaml
id:         <the entity id, or item_table_* / drop_pools for batch files>
schema:     20_schemas/<name>.schema.md      # literal path to the owning schema
references: [DOC, DOC, ...]                   # BARE system-doc names (no path, no .md)
```

`references` lists the docs whose values this file derives from; each schema fixes the baseline set
and the conditional adds (e.g. a map adds `SPAWN` when `spawn_zones` is non-empty). Names are bare
tokens (`COMBAT_FORMULA`, `WORLD_PLAN`), matching each schema's own template.

## Conventions fixed by the exemplars

- **Values only.** Copy stat/exp/price/reward numbers from the owning system doc (COMBAT_FORMULA
  §13, LEVELING §3, DROPS §3/§5, ITEMS §7–§10/§1.1, QUESTS §4–§5, ECONOMY §4/§7); never restate the
  formula. A `# comment` may show the worked source (e.g. `# §13 Lv40`) — flavor is the only prose.
- **Units.** tiles (distances/coords, top-left origin), seconds (durations/cooldowns), percent for
  `evasion`/`crit_rate` (float), `shards`/`exp`/`life` as integers.
- **Bidirectional links** (both sides must exist): a map's `npcs[]` ↔ each NPC's `map`; a monster's
  `drop_table` ↔ its `drop_mob_NNN` file; a quest's `giver_npc`/step targets ↔ those entities. A
  batch agent that adds an NPC to a town writes it on **both** the NPC file and the map's `npcs[]`.
- **Flag, don't guess** (Law 4): an unknown number/token goes to the owning doc's Open Questions,
  never invented here.

## Copy these exemplars (R9 · Frostpeak · Lv 40–55)

| Exemplar | Template for | Key model |
|---|---|---|
| `maps/map_204.yaml` | arc-2 port **town** | `town` type, `from_deepway`/`longship_dock` spawns, `longship` pier portal, coach-free, `npcs[]` bidirectional |
| `maps/map_208.yaml` | **field** | `spawn_zones` (SPAWN §1 count form), paired + forward `edge` portals, foothold `platform_brief` |
| `monsters/mob_151.yaml` | **normal** monster | §13 Lv-40 stat row, `ai_profile` + `ai_params`, normal animation set (no `telegraph`/`spawn`) |
| `drop_tables/drop_mob_151.yaml` | **normal** drop table | DROPS §5.1 shape, §3 `shards` band math |
| `drop_tables/pools.yaml` | region equip **pool** | `pool_equip_r09` seed; append other regions here (one shared file) |
| `items/etc/materials_r09.yaml` | region **materials** table | `etc` row: no `buy`, `source_hint`, `stack: 999` |
| `items/equip/weapons.yaml` | **weapon** rows | T7 base `W` (§7), 1 affix line (§10 budget), `enhance_max: 9` |
| `items/use/consumables.yaml` | **tonic** rows | `use` row: `effects[heal]`, `stack: 100`, tonic ladder (§1.1) |
| `npcs/npc_085.yaml` | arc-2 **pier NPC** | `pier_officer` role → `services: [longship]`, co-located with the pier portal |
| `quests/quest_091.yaml` | region **quest** | `side` reward budget (§4 exp band / §5 shards formula), kill + collect steps |
| `skills/bulwark/skill_bulwark_014.yaml` | **spec skill** | roster-exact identity, `level_data` rows at 1/4/7/10 |
