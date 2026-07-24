# ID_REGISTRY.md — Reserved ID Ranges (Immutable)

IDs are semantic + zero-padded, immutable once assigned, and must fall inside their reserved
block. Collisions or out-of-range IDs fail VALIDATION.md §4. Region composition detail lives
in WORLD_PLAN.md; this file owns **who may mint which IDs**. The blocks below cover the
five-island / two-arc world (Lv 1–80, 11 bosses, regions R1–R11): all ID ranges were laid out
**before any content IDs were minted** (Phase D authored them afterward), which is the only
permitted kind of re-blocking — never renumber minted IDs.

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

## Items — `item_equip_0001`–`0340`

| Sub-block | Range | Authored (v3 plan) |
|---|---|---|
| Weapons, arc 1 (4 lines × T1–T6: Lv 1/8/15/22/29/36) | `0001`–`0040` | 24 |
| Armor, arc 1 (head/body/legs/boots/gloves × T1–T6) | `0041`–`0140` | 30 |
| Accessories, arc 1 (cape/ring/amulet) | `0141`–`0180` | 16 |
| Shield (`shield` slot, equipment-v2 wave; re-homed at the v3 merge) | `0181`–`0190` | 6 planned |
| Overall (`overall` slot, equipment-v2 wave; re-homed at the v3 merge) | `0191`–`0200` | 6 planned |
| Boss uniques (2 per boss, boss order #1–#11) | `0201`–`0222` | 22 |
| Raid-exclusive equipment (2 per raid, token-bought; undervault 0223–24 · mainspring 0225–26 · deepfrost 0227–28 · voidtide 0229–30) | `0223`–`0230` | 8 |
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
| 0021 | Capsule Ticket (10_systems/GACHAPON.md §3; vendor value 0; minted 2026-07-24) | | |

Tonic tiers bind to level bands per 10_systems/ITEMS.md (v3: seven tiers across the
authored Lv 1–80+ arcs).
`0022`–`0060` reserved for Phase D (region specialties, raid consumables, quest consumables).

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

**Raid tokens** (`10_systems/DROPS.md` §5.4, `10_systems/social/RAID.md`): `0177` Undervault
Seal · `0178` Mainspring Cog · `0179` Deepfrost Shard · `0180` Voidtide Pearl — one per raid,
guaranteed to each eligible member on a finale clear, spent at the Raid Quartermaster.
`0181`–`0192` reserved (future raid tokens / growth).
Enhancement materials: `item_etc_0193`–`0197` = Emberstone I–V (band mapping per
10_systems/ENHANCEMENT.md); `0198`–`0200` reserved (`0198` proposed as Emberstone VI for the
arc-2 bands — pending the ENHANCEMENT.md mapping decision, see Open Questions).

## Cosmetics — `item_cosmetic_0001`–`0064`
Cosmetic-only rewards (titles, dyes, crest flourishes, weapon/armor skins) per the
cosmetic-only charter (`10_systems/MONETIZATION.md`); they carry no stats (`00_vision/PILLARS.md`
anti-pay-to-win). **Owner of the cosmetic system + earn/equip rules: `10_systems/COSMETICS.md`**
(assigned 2026-07-24). Sub-blocks (carved before any cosmetic ID was minted — the permitted kind
of re-blocking):

| Sub-block | Range | Channel (`10_systems/COSMETICS.md` §4) |
|---|---|---|
| Raid-exclusive | `0001`–`0008` | One title + one cosmetic effect per raid, Quartermaster-bought with `raid_token`s |
| Guild | `0009`–`0032` | Guild-level unlocks + crest options (`10_systems/social/GUILD.md` §9) |
| Event / charter | `0033`–`0048` | Live-ops/seasonal — assigned 2026-07-24 to the Wayfarer's Charter season cosmetics (up to 6 per season; rule owner `10_systems/BATTLE_PASS.md` §5) |
| Capsule | `0049`–`0064` | Cogwork Capsule gacha exclusives (rule owner `10_systems/GACHAPON.md` §5; PA-001) — reassigned 2026-07-24 from unassigned growth, no IDs minted |

No cosmetic content is authored this run beyond these reservations; the 23 collection titles
(`10_systems/COLLECTIONS.md` §7) are server grant flags, not IDs, and deliberately sit outside
this block.

## Skills — `skill_<line>_001`–`060` per job line (blocks for branched 2nd jobs)
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

**Job-advancement, 3rd tier — `quest_121`–`quest_132` (reserved, unauthored; future arc).**
Range extension appended past the former `quest_120` cap in a new commit; `001`–`120` are
unmoved. Three quests per line, line order: `bulwark` `121`–`123` · `keeneye` `124`–`126` ·
`weaver` `127`–`129` · `flicker` `130`–`132` (quest-line anatomy: 10_systems/JOBS.md §1.1).
Mint only with the future 3rd-tier arc, alongside `skill_<line>_028`–`045`; nothing in this
run's content may reference these IDs.

## Raids — `raid_undervault` · `raid_mainspring` · `raid_deepfrost` · `raid_voidtide`
Owner: 10_systems/social/RAID.md. Future raids mint `raid_<name>` tokens here first (the
legacy `pq_<name>` family is retired and must not appear in content).

## Packet opcodes — `op_0001`–`op_9999` (13 domain blocks)

Engineering-side wire IDs for the client↔gateway protocol (the backend wave, not player content).
This block reserves the **domain ranges**; the individual opcodes are minted **only** in
`70_integrations/NETWORK_PROTOCOL.md`'s packet catalog, one per wire message, and are immutable once
minted (same law as every other ID here).

**Convention — unified `op_NNNN`, direction carried in the catalog + the wire envelope, not the ID.**
Chosen over a directional `op_c2s_NNN` / `op_s2c_NNN` split so the envelope's opcode field stays one
small unsigned integer over a single flat namespace and a request and its paired authoritative delta
sit adjacent inside the same domain block, rather than across two parallel namespaces. Each opcode is
**unidirectional** (one opcode = one message type = one direction); the direction (`c2s`/`s2c`) and
payload shape are declared per opcode in the catalog, not encoded in the number.

| # | Domain block | Range | Owner / semantics |
|---|---|---|---|
| 1 | System, keep-alive & transport control | `op_0001`–`op_0099` | NETWORK_PROTOCOL.md §9.1 (heartbeat, ack, error, disconnect, resume) |
| 2 | Auth, handshake & session | `op_0100`–`op_0199` | NETWORK_PROTOCOL.md §9.2 (protocol negotiation, session bind — ACCOUNTS_AUTH.md §3/§4) |
| 3 | Channel & instance management | `op_0200`–`op_0299` | NETWORK_PROTOCOL.md §9.3 (WORLD_CHANNELS.md §3/§6) |
| 4 | Movement & reconciliation | `op_0300`–`op_0399` | NETWORK_PROTOCOL.md §9.4 (GAMEPLAY_SIMULATION.md §2) |
| 5 | World snapshot & entity lifecycle | `op_0400`–`op_0499` | NETWORK_PROTOCOL.md §9.5 (GAMEPLAY_SIMULATION.md §1.1/§13) |
| 6 | Combat | `op_0500`–`op_0599` | NETWORK_PROTOCOL.md §9.6 (GAMEPLAY_SIMULATION.md §5) |
| 7 | Skill | `op_0600`–`op_0699` | NETWORK_PROTOCOL.md §9.7 (GAMEPLAY_SIMULATION.md §6/§9) |
| 8 | Loot & drop pickup | `op_0700`–`op_0799` | NETWORK_PROTOCOL.md §9.8 (GAMEPLAY_SIMULATION.md §11) |
| 9 | Inventory & equipment | `op_0800`–`op_0899` | NETWORK_PROTOCOL.md §9.9 (GAMEPLAY_SIMULATION.md §7) |
| 10 | Shards, acquisition & enhancement | `op_0900`–`op_0999` | NETWORK_PROTOCOL.md §9.10 (GAMEPLAY_SIMULATION.md §7/§10) |
| 11 | Quest | `op_1000`–`op_1099` | NETWORK_PROTOCOL.md §9.11 (GAMEPLAY_SIMULATION.md §8/§14) |
| 12 | Chat | `op_1100`–`op_1199` | NETWORK_PROTOCOL.md §9.12 (CHAT_SOCIAL_BACKEND.md) |
| 13 | Party & social | `op_1200`–`op_1299` | NETWORK_PROTOCOL.md §9.13 (CHAT_SOCIAL_BACKEND.md; GAMEPLAY_SIMULATION.md §8/§11) |

`op_1300`–`op_9999` are **reserved (future domains)** — a new domain claims the next free 100-wide
block in a new commit; existing blocks never move. **Within** a block the catalog conventionally lays
request (`c2s`) opcodes low and response/delta/event (`s2c`) opcodes high, leaving generous in-domain
growth (each domain expects roughly 5–20 opcodes against its 99-slot block); the registry owns the
block, the catalog owns the mint. Opcode IDs are minted only in NETWORK_PROTOCOL.md and are immutable
once minted — a retired packet's opcode is never re-used for a different message.

## Log event codes — `010`–`599` (6 channel blocks)

Engineering-side IDs for the server audit-log line format (the backend wave, not player content) —
same posture as the `op_NNNN` family above. This block reserves the **channel ranges**; the
individual codes (and their `log_*` event-type names) are minted **only** in
`70_integrations/SERVER_LOGGING_SPEC.md` §4, one per record shape, and are immutable once minted:
a retired code is never reused, and a new event takes the next free slot in its block in a new
commit — never a renumber. The code also fixes the record's verbosity level (level is
code-intrinsic, not stored per line — SERVER_LOGGING_SPEC.md §1/§3).

| # | Channel block | Range | Owner / semantics |
|---|---|---|---|
| 1 | Session & context | `010`–`099` | SERVER_LOGGING_SPEC.md §4.0 (session open/close, map-enter context) |
| 2 | `CHAT` | `100`–`199` | SERVER_LOGGING_SPEC.md §4.1 |
| 3 | `PLAYER_PROGRESSION` | `200`–`299` | SERVER_LOGGING_SPEC.md §4.2 |
| 4 | `ECONOMY` | `300`–`399` | SERVER_LOGGING_SPEC.md §4.3 |
| 5 | `COMBAT` | `400`–`499` | SERVER_LOGGING_SPEC.md §4.4 |
| 6 | `SECURITY_ALERTS` | `500`–`599` | SERVER_LOGGING_SPEC.md §4.5 (validation records, detector flags, GM audit) |

`600`–`999` are **reserved (future channels)** — a new channel claims the next free 100-wide block
in a new commit; existing blocks never move.

## Appearance styles — `style_<category>_NN`

Owner: 40_assets/CHARACTER_COMPOSITING.md (owner directive 2026-07-24). Character-creation
appearance parts and palette swatches only — a worn equip's sprite part reuses its own
`item_equip_NNNN`, cosmetic skins/dyes stay in the `item_cosmetic_NNNN` block above
(10_systems/COSMETICS.md), and player characters themselves are server-minted opaque ids,
never registry ids (70_integrations/ACCOUNTS_AUTH.md §2.1) — nothing here overlaps either.

| Category | Block | Authored (arc-1 plan) |
|---|---|---|
| Base body | `style_base_00`–`style_base_04` | 1 (`style_base_00`, the canonical skeleton); rest reserved |
| Hair | `style_hair_01`–`style_hair_40` | 12; rest reserved |
| Face | `style_face_01`–`style_face_20` | 8; rest reserved |
| Skin swatches | `style_skin_00`–`style_skin_09` | 5 (palette-remap data only, no art); rest reserved |
| Hair-color swatches | `style_haircolor_00`–`style_haircolor_09` | 6 (palette-remap data only, no art); rest reserved |

Swatch color values are canon per ART_BIBLE.yaml amendment AB-002 (`skin_NN` / `hair_*`
ramp keys; binding in CHARACTER_COMPOSITING.md §5).

## Seasons — `season_001`–`season_050`
Owner: 10_systems/BATTLE_PASS.md (the Wayfarer's Charter). One ID per 30-day season, minted in
chronological order; season content files land under `50_content/seasons/` (schema
`20_schemas/season.schema.md`, Phase C). `season_001` is the launch season (authored at Phase D);
`002`–`050` reserved. Charter tasks carry no global IDs — they are per-season keys inside the
season file. (Block added 2026-07-24, before any season IDs were minted.)

## Open Questions
- Reserved-growth blocks assume no category outgrows its range before the coding pass; if
  one does, extend the range here in a new commit — never renumber existing IDs.
- The `op_NNNN` opcode family is an **engineering-side** ID (wire protocol), deliberately registry-owned
  but not enumerated in `docs/00_vision/GLOSSARY.md`'s `## ID prefixes` list, which tracks player-content
  prefixes only. Confirm at reconciliation whether GLOSSARY should note the opcode family for completeness,
  or whether engineering IDs stay out of the content-token glossary by design (this file remains their owner
  either way).
- The Event/charter cosmetic sub-block (`item_cosmetic_0033`–`0048`, 16 IDs) covers ≈ 2.5
  seasons at the charter's up-to-6-per-season budget; extend the cosmetic block past `0064`
  in a new commit before `season_003` content is authored.
- `item_etc_0198` is proposed as Emberstone VI for the arc-2 enhancement bands; the band
  mapping decision belongs to 10_systems/ENHANCEMENT.md (see ITEMS.md Open Questions). Mint
  only once that doc lands the mapping.
- Equipment-v2 integration (v3 merge debt): shield/overall content (`0181`–`0200`) and
  scroll content (`item_use_0061`–`0078`) are registered but unauthored; ITEMS.md §2's v3
  slot roster and the schemas/validator must adopt `shield`/`overall`/`req_line` and the
  scroll vocabulary before that Phase D batch runs. Owner: ITEMS.md + SCROLLS.md wave.
