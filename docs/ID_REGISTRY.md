# ID_REGISTRY.md — Reserved ID Ranges (Immutable)

IDs are semantic + zero-padded, immutable once assigned, and must fall inside their reserved
block. Collisions or out-of-range IDs fail VALIDATION.md §4. Region composition detail (map
types, edges, themes) lives in WORLD_PLAN.md; this file owns **who may mint which IDs**.

## Maps — `map_001`–`map_200` (12 region blocks)

| Region (slug) | Block |
|---|---|
| 1 Emberfoot Grounds (`emberfoot`) | `map_001`–`map_012` |
| 2 Verdant Hollow (`verdant`) | `map_013`–`map_028` |
| 3 Millbrook Township (`millbrook`) | `map_029`–`map_040` |
| 4 Tidewatch Coast (`tidewatch`) | `map_041`–`map_056` |
| 5 Sunken Depths (`sunken`) | `map_057`–`map_072` |
| 6 Ashfall Wastes (`ashfall`) | `map_073`–`map_090` |
| 7 Frostpeak Ascent (`frostpeak`) | `map_091`–`map_108` |
| 8 Gloomwood (`gloomwood`) | `map_109`–`map_126` |
| 9 Clockwork Ruins (`clockwork`) | `map_127`–`map_144` |
| 10 Arcane Reach (`arcane_reach`) | `map_145`–`map_162` |
| 11 Voidshore (`voidshore`) | `map_163`–`map_182` |
| 12 The Rift (`rift`) | `map_183`–`map_200` |

**Convention:** the last ID(s) of each block are the region's boss arena(s) — one arena per
region, except Rift where `map_197`–`map_200` are the four raid arenas.

## Monsters — `mob_001`–`mob_150` (normals first, then elites, boss last)

| Region | Block | Normal | Elite | Boss |
|---|---|---|---|---|
| 1 Emberfoot | `mob_001`–`mob_011` | 001–009 | 010 | 011 |
| 2 Verdant | `mob_012`–`mob_023` | 012–020 | 021–022 | 023 |
| 3 Millbrook | `mob_024`–`mob_032` | 024–030 | 031 | 032 |
| 4 Tidewatch | `mob_033`–`mob_044` | 033–041 | 042–043 | 044 |
| 5 Sunken | `mob_045`–`mob_057` | 045–054 | 055–056 | 057 |
| 6 Ashfall | `mob_058`–`mob_070` | 058–067 | 068–069 | 070 |
| 7 Frostpeak | `mob_071`–`mob_083` | 071–080 | 081–082 | 083 |
| 8 Gloomwood | `mob_084`–`mob_096` | 084–093 | 094–095 | 096 |
| 9 Clockwork | `mob_097`–`mob_109` | 097–106 | 107–108 | 109 |
| 10 Arcane Reach | `mob_110`–`mob_122` | 110–119 | 120–121 | 122 |
| 11 Voidshore | `mob_123`–`mob_136` | 123–132 | 133–135 | 136 |
| 12 The Rift | `mob_137`–`mob_150` | 137–144 | 145–146 | 147–150 (4 raid bosses) |

Totals: 112 normal, 23 elite, 15 boss = 150.

## Drop tables — `drop_mob_001`–`drop_mob_150`
Exactly one per monster, number matching its `mob_NNN`. Region equip pools:
`pool_equip_r01`–`pool_equip_r12` (semantics in 10_systems/DROPS.md; pool contents authored in
`50_content/drop_tables/pools.yaml`).

## Items — `item_equip_0001`–`0300`

| Sub-block | Range |
|---|---|
| Weapons (4 lines × 10 tiers) | `item_equip_0001`–`0040` |
| Armor (head/body/legs/boots/gloves × tiers) | `item_equip_0041`–`0140` |
| Accessories (cape/ring/amulet) | `item_equip_0141`–`0180` |
| Reserved (growth) | `item_equip_0181`–`0200` |
| Boss uniques (2 per boss, boss order) | `item_equip_0201`–`0230` |
| Reserved (growth) | `item_equip_0231`–`0300` |

Boss unique mapping: boss #n (region order; Rift bosses are #12–#15) owns
`item_equip_{0199+2n}` and `{0200+2n}` (e.g., region 1 boss → 0201–0202; Rift's four →
0223–0230).

## Items — `item_use_0001`–`0060`

Well-known IDs `0001`–`0016` are reserved **now** so drop tables and shops can reference them
before item files exist (names final; stats authored in Phase D):

| ID | Name | ID | Name |
|---|---|---|---|
| 0001 | Lesser Life Tonic | 0009 | Superior Essence Tonic |
| 0002 | Life Tonic | 0010 | Prime Essence Tonic |
| 0003 | Greater Life Tonic | 0011 | Antidote |
| 0004 | Superior Life Tonic | 0012 | Thaw Salve |
| 0005 | Prime Life Tonic | 0013 | Millbrook Return Scroll |
| 0006 | Lesser Essence Tonic | 0014 | Hearth Bread |
| 0007 | Essence Tonic | 0015 | Sharpening Oil |
| 0008 | Greater Essence Tonic | 0016 | Ironhide Draught |

`0017`–`0060` reserved for Phase D (region specialties, quest consumables).

## Items — `item_etc_0001`–`0200` (16 per region, monster materials)

| Region | Block | Region | Block |
|---|---|---|---|
| 1 Emberfoot | `0001`–`0016` | 7 Frostpeak | `0097`–`0112` |
| 2 Verdant | `0017`–`0032` | 8 Gloomwood | `0113`–`0128` |
| 3 Millbrook | `0033`–`0048` | 9 Clockwork | `0129`–`0144` |
| 4 Tidewatch | `0049`–`0064` | 10 Arcane Reach | `0145`–`0160` |
| 5 Sunken | `0065`–`0080` | 11 Voidshore | `0161`–`0176` |
| 6 Ashfall | `0081`–`0096` | 12 The Rift | `0177`–`0192` |

Enhancement materials: `item_etc_0193`–`0197` = Emberstone I–V; `0198`–`0200` reserved.

## Skills — `skill_<line>_001`–`030` per job line
Line tokens (promoted at B gate; owner 10_systems/JOBS.md): `bulwark` (might), `keeneye`
(finesse), `weaver` (focus), `flicker` (fortune). Budget per line: 21 authored skills
(001–021 in tier order: 6 first-job, 7 second-job, 8 third-job); 022–030 reserved.
`skill_novice_001`–`010` reserved for the novice kit (up to 4 authored).

## NPCs — `npc_001`–`npc_120`

| Region | Block | Count | Region | Block | Count |
|---|---|---|---|---|---|
| 1 Emberfoot | 001–010 | 10 | 7 Frostpeak | 052–055 | 4 |
| 2 Verdant | 011–015 | 5 | 8 Gloomwood | 056–059 | 4 |
| 3 Millbrook | 016–031 | 16 | 9 Clockwork | 060–063 | 4 |
| 4 Tidewatch | 032–043 | 12 | 10 Arcane Reach | 064–075 | 12 |
| 5 Sunken | 044–047 | 4 | 11 Voidshore | 076–079 | 4 |
| 6 Ashfall | 048–051 | 4 | 12 The Rift | 080–084 | 5 |

`npc_085`–`120` reserved. Total authored: 84.

## Quests — `quest_001`–`quest_120`

| Region | Block | Count | Region | Block | Count |
|---|---|---|---|---|---|
| 1 Emberfoot | 001–008 | 8 | 7 Frostpeak | 049–055 | 7 |
| 2 Verdant | 009–016 | 8 | 8 Gloomwood | 056–062 | 7 |
| 3 Millbrook | 017–026 | 10 | 9 Clockwork | 063–069 | 7 |
| 4 Tidewatch | 027–034 | 8 | 10 Arcane Reach | 070–077 | 8 |
| 5 Sunken | 035–041 | 7 | 11 Voidshore | 078–084 | 7 |
| 6 Ashfall | 042–048 | 7 | 12 The Rift | 085–090 | 6 |

`quest_091`–`120` reserved. Total authored: 90.

## Open Questions
- Reserved-growth blocks assume no category outgrows its range before the coding pass; if one
  does, extend the range here in a new commit — never renumber existing IDs.
