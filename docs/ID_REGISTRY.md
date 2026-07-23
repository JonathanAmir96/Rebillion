# ID_REGISTRY.md — Reserved ID Ranges (Immutable) — v3

IDs are semantic + zero-padded, immutable once assigned, and must fall inside their reserved
block. Collisions or out-of-range IDs fail VALIDATION.md §4. Region composition detail lives
in WORLD_PLAN.md; this file owns **who may mint which IDs**. **v2 note:** re-blocked for the
two-island / first-arc (Lv 1–42) / 8-boss world before any content IDs were minted (Phase D had not
started); this is the only permitted kind of re-blocking — never renumber minted IDs.
**v3 note (owner revision 2026-07-23):** extended for Arc 2 (Lv 40–80, regions R9–R11) and
re-blocked the never-minted growth reserves (arc-2 equips, branched-spec skill blocks) —
again before any Phase D minting, so the same legality applies.

## Maps — `map_001`–`map_324` (11 region blocks)

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
| 9 Frostpeak Isle (`frostpeak`) | `map_201`–`map_244` |
| 10 Arcane Reach (`arcane_reach`) | `map_245`–`map_284` |
| 11 Voidshore (`voidshore`) | `map_285`–`map_324` |

**Convention:** the last ID of each block is the region's boss arena. Raid stage maps are
`map_038`–`map_040` (`raid_undervault`), `map_195`–`map_197` (`raid_mainspring`),
`map_240`–`map_242` (`raid_deepfrost`), and `map_320`–`map_322` (`raid_voidtide`). The
Deepway passage dungeons are `map_201`–`map_203` (Frostpeak block).

## Monsters — `mob_001`–`mob_234` (normals first, then elites, boss last)

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
| 9 Frostpeak | `mob_151`–`mob_178` | 151–170 | 171–177 | 178 |
| 10 Arcane Reach | `mob_179`–`mob_206` | 179–198 | 199–205 | 206 |
| 11 Voidshore | `mob_207`–`mob_234` | 207–226 | 227–233 | 234 |

Totals: 178 normal, 45 elite, 11 boss = 234.

## Drop tables — `drop_mob_001`–`drop_mob_234`
Exactly one per monster, number matching its `mob_NNN`. Region equip pools:
`pool_equip_r01`–`pool_equip_r11` (semantics in 10_systems/DROPS.md; contents authored in
`50_content/drop_tables/pools.yaml`).

## Items — `item_equip_0001`–`0300`

| Sub-block | Range | Authored (v3 plan) |
|---|---|---|
| Weapons, arc 1 (4 lines × T1–T6: Lv 1/8/15/22/29/36) | `0001`–`0040` | 24 |
| Armor, arc 1 (head/body/legs/boots/gloves × T1–T6) | `0041`–`0140` | 30 |
| Accessories, arc 1 (cape/ring/amulet) | `0141`–`0180` | 16 |
| Shield (`shield` slot, equipment-v2 wave; re-homed at the v3 merge) | `0181`–`0190` | 6 planned |
| Overall (`overall` slot, equipment-v2 wave; re-homed at the v3 merge) | `0191`–`0200` | 6 planned |
| Boss uniques (2 per boss, boss order #1–#11) | `0201`–`0222` | 22 |
| Reserved (uniques growth / future bosses) | `0223`–`0230` | — |
| Weapons, arc 2 (4 lines × T7–T12: Lv 43/50/57/64/71/78) | `0231`–`0254` | 24 |
| Armor, arc 2 (5 slots × T7–T12) | `0255`–`0284` | 30 |
| Accessories, arc 2 | `0285`–`0300` | 16 |

Boss unique mapping: boss #n (region order) owns `item_equip_{0199+2n}` and `{0200+2n}`
(Cindermaw 0201–0202, Cellar King 0203–0204, Thornback 0205–0206, Morva 0207–0208, Gloam
0209–0210, Karnothal 0211–0212, Drowned Warden 0213–0214, Custodian 0215–0216, Skoldir
0217–0218, Aetheron 0219–0220, Nyxaris 0221–0222).

**Equipment-v2 re-homing note (v3 merge):** the equipment-v2 wave originally carved
shield/overall from `0231`–`0250`, but the v3 arc-2 batch had already **minted**
`0231`–`0300` as arc-2 weapons/armor/accessories content. Minted IDs never move, so
shield/overall re-homed into the never-minted `0181`–`0200` growth reserve (10 + 10 slots).
Their content and the ITEMS §2 slot-roster integration with the v3 T1–T12 ladder are a
follow-up wave (see Open Questions).

## Items — `item_use_0001`–`0100`

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
| 0017 | Sovereign Life Tonic | 0019 | Mythic Life Tonic |
| 0018 | Sovereign Essence Tonic | 0020 | Mythic Essence Tonic |

Tonic tiers bind to level bands per 10_systems/ITEMS.md (v3: seven tiers across the
authored Lv 1–80+ arcs).
`0021`–`0060` reserved for Phase D (region specialties, raid consumables, quest consumables).

**Gear-modification scrolls (equipment-v2 wave; semantics 10_systems/SCROLLS.md):**
`0061`–`0078` = 18 SKUs, 3 slot families × 2 kinds × 3 tiers, laid out `0061`–`0066`
weapon_family, `0067`–`0072` armor_family, `0073`–`0078` accessory_family (each family in
order aspect steady/bold/perilous, then temper steady/bold/perilous). `0079`–`0090`
reserved scroll growth; `0091`–`0100` reserved. The range extension `0061`–`0100` was
appended past the former `0060` cap in a new commit; `0001`–`0060` are unmoved.

## Items — `item_etc_0001`–`0200` (16 per region, monster materials)

| Region | Block | Region | Block |
|---|---|---|---|
| 1 Emberfoot | `0001`–`0016` | 5 Gloomwood | `0065`–`0080` |
| 2 Millbrook | `0017`–`0032` | 6 Ashfall | `0081`–`0096` |
| 3 Verdant | `0033`–`0048` | 7 Sunken | `0097`–`0112` |
| 4 Tidewatch | `0049`–`0064` | 8 Clockwork | `0113`–`0128` |
| 9 Frostpeak | `0129`–`0144` | 10 Arcane Reach | `0145`–`0160` |
| 11 Voidshore | `0161`–`0176` | | |

`0177`–`0192` reserved (raid tokens per 10_systems/DROPS.md §5.4 / future growth).
Enhancement materials: `item_etc_0193`–`0197` = Emberstone I–V (band mapping per
10_systems/ENHANCEMENT.md); `0198`–`0200` reserved (`0198` proposed as Emberstone VI for the
arc-2 bands — pending the ENHANCEMENT.md mapping decision, see Open Questions).

## Skills — `skill_<line>_001`–`060` per job line (v3 re-block for branched 2nd jobs)
Line tokens (owner 10_systems/JOBS.md): `bulwark` (might), `keeneye` (finesse), `weaver`
(focus), `flicker` (fortune). Per-line layout: `001`–`006` first-job (shared by the line's
specs) · `007`–`013` specialization #1 · `014`–`020` specialization #2 · `021`–`027`
specialization #3 (`bulwark`/`weaver` only; reserved for `keeneye`/`flicker`) · `028`–`045`
reserved 3rd tier · `046`–`060` reserved growth. **v3 authored budget:** `bulwark`/`weaver`
27 each, `keeneye`/`flicker` 20 each (spec rosters in 10_systems/JOBS.md).
`skill_novice_001`–`010` reserved for the novice kit (up to 4 authored).

## NPCs — `npc_001`–`npc_120`

| Region | Block | Count | Region | Block | Count |
|---|---|---|---|---|---|
| 1 Emberfoot | 001–010 | 10 | 5 Gloomwood | 055–061 | 7 |
| 2 Millbrook | 011–032 | 22 | 6 Ashfall | 062–068 | 7 |
| 3 Verdant | 033–040 | 8 | 7 Sunken | 069–075 | 7 |
| 4 Tidewatch | 041–054 | 14 | 8 Clockwork | 076–084 | 9 |
| 9 Frostpeak | 085–096 | 12 | 10 Arcane Reach | 097–108 | 12 |
| 11 Voidshore | 109–120 | 12 | | | |

Total authored: 120.

## Quests — `quest_001`–`quest_120`

| Region | Block | Count | Region | Block | Count |
|---|---|---|---|---|---|
| 1 Emberfoot | 001–010 | 10 | 5 Gloomwood | 049–058 | 10 |
| 2 Millbrook | 011–024 | 14 | 6 Ashfall | 059–068 | 10 |
| 3 Verdant | 025–036 | 12 | 7 Sunken | 069–078 | 10 |
| 4 Tidewatch | 037–048 | 12 | 8 Clockwork | 079–086 | 8 |
| 9 Frostpeak | 091–100 | 10 | 10 Arcane Reach | 101–110 | 10 |
| 11 Voidshore | 111–120 | 10 | | | |

Raid intro/handler quests: `quest_087`–`090` (arc 1, 2 per raid; owner region R2/R8 casts),
`quest_099`–`100` (`raid_deepfrost`), `quest_119`–`120` (`raid_voidtide`).
Total authored: 120.

## Raids — `raid_undervault` · `raid_mainspring` · `raid_deepfrost` · `raid_voidtide`
Owner: 10_systems/social/RAID.md. Future raids mint `raid_<name>` tokens here first (the
legacy `pq_<name>` family is retired and must not appear in content).

## Open Questions
- Reserved-growth blocks assume no category outgrows its range before the coding pass; if
  one does, extend the range here in a new commit — never renumber existing IDs.
- `item_etc_0198` is proposed as Emberstone VI for the arc-2 enhancement bands; the band
  mapping decision belongs to 10_systems/ENHANCEMENT.md (see ITEMS.md Open Questions). Mint
  only once that doc lands the mapping.
- Equipment-v2 integration (v3 merge debt): shield/overall content (`0181`–`0200`) and
  scroll content (`item_use_0061`–`0078`) are registered but unauthored; ITEMS.md §2's v3
  slot roster and the schemas/validator must adopt `shield`/`overall`/`req_line` and the
  scroll vocabulary before that Phase D batch runs. Owner: ITEMS.md + SCROLLS.md wave.
