# ID_REGISTRY.md — Reserved ID Ranges (Immutable) — v2

IDs are semantic + zero-padded, immutable once assigned, and must fall inside their reserved
block. Collisions or out-of-range IDs fail VALIDATION.md §4. Region composition detail lives
in WORLD_PLAN.md; this file owns **who may mint which IDs**. **v2 note:** re-blocked for the
two-island / first-arc (Lv 1–42) / 8-boss world before any content IDs were minted (Phase D had not
started); this is the only permitted kind of re-blocking — never renumber minted IDs.

## Maps — `map_001`–`map_200` (8 region blocks)

| Region (slug) | Block |
|---|---|
| 1 Emberfoot Isle (`emberfoot`) | `map_001`–`map_016` |
| 2 Millbrook & Rosen Harbor (`millbrook`) | `map_017`–`map_042` |
| 3 Verdant Hollow (`verdant`) | `map_043`–`map_070` |
| 4 Tidewatch Coast (`tidewatch`) | `map_071`–`map_097` |
| 5 Gloomwood (`gloomwood`) | `map_098`–`map_124` |
| 6 Ashfall Barrens (`ashfall`) | `map_125`–`map_151` |
| 7 Sunken Depths (`sunken`) | `map_152`–`map_176` |
| 8 Clockwork Ruins (`clockwork`) | `map_177`–`map_200` |

**Convention:** the last ID of each block is the region's boss arena. Party-quest stage maps
are `map_038`–`map_040` (`pq_undervault`) and `map_195`–`map_197` (`pq_mainspring`).

## Monsters — `mob_001`–`mob_150` (normals first, then elites, boss last)

| Region | Block | Normal | Elite | Boss |
|---|---|---|---|---|
| 1 Emberfoot | `mob_001`–`mob_012` | 001–010 | 011 | 012 |
| 2 Millbrook | `mob_013`–`mob_027` | 013–024 | 025–026 | 027 |
| 3 Verdant | `mob_028`–`mob_047` | 028–043 | 044–046 | 047 |
| 4 Tidewatch | `mob_048`–`mob_067` | 048–063 | 064–066 | 067 |
| 5 Gloomwood | `mob_068`–`mob_087` | 068–083 | 084–086 | 087 |
| 6 Ashfall | `mob_088`–`mob_107` | 088–103 | 104–106 | 107 |
| 7 Sunken | `mob_108`–`mob_128` | 108–123 | 124–127 | 128 |
| 8 Clockwork | `mob_129`–`mob_150` | 129–144 | 145–149 | 150 |

Totals: 118 normal, 24 elite, 8 boss = 150.

## Drop tables — `drop_mob_001`–`drop_mob_150`
Exactly one per monster, number matching its `mob_NNN`. Region equip pools:
`pool_equip_r01`–`pool_equip_r08` (semantics in 10_systems/DROPS.md; contents authored in
`50_content/drop_tables/pools.yaml`).

## Items — `item_equip_0001`–`0300`

| Sub-block | Range | Authored (v2 plan) |
|---|---|---|
| Weapons (4 lines × 6 tiers: Lv 1/8/15/22/29/36) | `0001`–`0040` | 24 |
| Armor (head/body/legs/boots/gloves × 6 tiers) | `0041`–`0140` | 30 |
| Accessories (cape/ring/amulet) | `0141`–`0180` | 16 |
| Reserved (growth) | `0181`–`0200` | — |
| Boss uniques (2 per boss, boss order #1–#8) | `0201`–`0216` | 16 |
| Reserved (uniques growth / future bosses) | `0217`–`0230` | — |
| Reserved (growth) | `0231`–`0300` | — |

Boss unique mapping: boss #n (region order) owns `item_equip_{0199+2n}` and `{0200+2n}`
(Cindermaw 0201–0202, Cellar King 0203–0204, Thornback 0205–0206, Morva 0207–0208, Gloam
0209–0210, Karnothal 0211–0212, Drowned Warden 0213–0214, Custodian 0215–0216).

## Items — `item_use_0001`–`0060`

Well-known IDs `0001`–`0016` are reserved with final names so drop tables and shops can
reference them before item files exist (stats authored in Phase D):

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

Tonic tiers bind to level bands per 10_systems/ITEMS.md (v2: five tiers across the
authored Lv 1–42 arc).
`0017`–`0060` reserved for Phase D (region specialties, PQ consumables, quest consumables).

## Items — `item_etc_0001`–`0200` (16 per region, monster materials)

| Region | Block | Region | Block |
|---|---|---|---|
| 1 Emberfoot | `0001`–`0016` | 5 Gloomwood | `0065`–`0080` |
| 2 Millbrook | `0017`–`0032` | 6 Ashfall | `0081`–`0096` |
| 3 Verdant | `0033`–`0048` | 7 Sunken | `0097`–`0112` |
| 4 Tidewatch | `0049`–`0064` | 8 Clockwork | `0113`–`0128` |

`0129`–`0192` reserved (future regions). Enhancement materials: `item_etc_0193`–`0197` =
Emberstone I–V (band mapping v2 per 10_systems/ENHANCEMENT.md); `0198`–`0200` reserved.

## Skills — `skill_<line>_001`–`030` per job line
Line tokens (owner 10_systems/JOBS.md): `bulwark` (might), `keeneye` (finesse), `weaver`
(focus), `flicker` (fortune). **v2 budget per line: 13 authored** (`001`–`006` first-job,
`007`–`013` second-job); `014`–`021` reserved for the deferred 3rd-job tier; `022`–`030`
reserved growth. `skill_novice_001`–`010` reserved for the novice kit (up to 4 authored).

## NPCs — `npc_001`–`npc_120`

| Region | Block | Count | Region | Block | Count |
|---|---|---|---|---|---|
| 1 Emberfoot | 001–010 | 10 | 5 Gloomwood | 055–061 | 7 |
| 2 Millbrook | 011–032 | 22 | 6 Ashfall | 062–068 | 7 |
| 3 Verdant | 033–040 | 8 | 7 Sunken | 069–075 | 7 |
| 4 Tidewatch | 041–054 | 14 | 8 Clockwork | 076–084 | 9 |

`npc_085`–`120` reserved. Total authored: 84.

## Quests — `quest_001`–`quest_120`

| Region | Block | Count | Region | Block | Count |
|---|---|---|---|---|---|
| 1 Emberfoot | 001–010 | 10 | 5 Gloomwood | 049–058 | 10 |
| 2 Millbrook | 011–024 | 14 | 6 Ashfall | 059–068 | 10 |
| 3 Verdant | 025–036 | 12 | 7 Sunken | 069–078 | 10 |
| 4 Tidewatch | 037–048 | 12 | 8 Clockwork | 079–086 | 8 |

Party-quest intro/handler quests: `quest_087`–`090` (2 per PQ; owner region R2/R8 casts).
`quest_091`–`120` reserved. Total authored: 90.

## Appearance styles — `style_<category>_NN`

Owner: 40_assets/CHARACTER_COMPOSITING.md (owner directive 2026-07-24). Character-creation
appearance parts and palette swatches only — a worn equip's sprite part reuses its own
`item_equip_NNNN` and mints nothing here.

| Category | Block | Authored (first-arc plan) |
|---|---|---|
| Base body | `style_base_00`–`style_base_04` | 1 (`style_base_00`, the canonical skeleton); rest reserved |
| Hair | `style_hair_01`–`style_hair_40` | 12; rest reserved |
| Face | `style_face_01`–`style_face_20` | 8; rest reserved |
| Skin swatches | `style_skin_00`–`style_skin_09` | 5 (palette-remap data only, no art); rest reserved |
| Hair-color swatches | `style_haircolor_00`–`style_haircolor_09` | 6 (palette-remap data only, no art); rest reserved |

Swatch color values are not canon until the ART_BIBLE skin/hair ramp amendment lands
(CHARACTER_COMPOSITING.md §5 / Open Questions).

## Party quests — `pq_undervault` · `pq_mainspring`
Owner: 10_systems/social/PARTY_QUEST.md. Future PQs mint `pq_<name>` tokens here first.

## Open Questions
- Reserved-growth blocks assume no category outgrows its range before the coding pass; if
  one does, extend the range here in a new commit — never renumber existing IDs.
