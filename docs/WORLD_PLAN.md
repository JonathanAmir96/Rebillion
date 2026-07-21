# WORLD_PLAN.md — Authoritative Region / Map / Monster Allocation

Source of truth for world structure. Every map and monster inherits its region's biome identity
(palette ramp + motif per `40_assets/ART_BIBLE.yaml` `environment.biome_identity`) and level
band. ID blocks are owned by `ID_REGISTRY.md`; this file allocates **what each ID is**.
Phase D region batches treat their region section here as their biome brief.

## Region overview

| # | Region | Slug | Level | Biome key (ramp) | Maps | N | E | B |
|---|--------|------|-------|------------------|------|---|---|---|
| 1 | Emberfoot Grounds | `emberfoot` | 1–10 | emberfoot (ember) | 12 | 9 | 1 | 1 |
| 2 | Verdant Hollow | `verdant` | 10–20 | verdant_hollow (verdant) | 16 | 9 | 2 | 1 |
| 3 | Millbrook Township (hub) | `millbrook` | ~15 | old_town (earth) | 12 | 7 | 1 | 1 |
| 4 | Tidewatch Coast | `tidewatch` | 20–30 | tidewatch (tide) | 16 | 9 | 2 | 1 |
| 5 | Sunken Depths | `sunken` | 30–40 | tidewatch_dark (tide) | 16 | 10 | 2 | 1 |
| 6 | Ashfall Wastes | `ashfall` | 40–50 | ashfall (ember/ash) | 18 | 10 | 2 | 1 |
| 7 | Frostpeak Ascent | `frostpeak` | 50–60 | frostpeak (tide/frost) | 18 | 10 | 2 | 1 |
| 8 | Gloomwood | `gloomwood` | 60–70 | gloomwood (verdant dark) | 18 | 10 | 2 | 1 |
| 9 | Clockwork Ruins | `clockwork` | 70–80 | clockwork (earth/stone) | 18 | 10 | 2 | 1 |
| 10 | Arcane Reach | `arcane_reach` | 80–90 | arcane_reach (arcane) | 18 | 10 | 2 | 1 |
| 11 | Voidshore | `voidshore` | 90–100 | voidshore (arcane void) | 20 | 10 | 3 | 1 |
| 12 | The Rift (endgame) | `rift` | 100+ | rift (arcane+mixed) | 18 | 8 | 2 | 4 |
| — | **TOTAL** | | | | **200** | **112** | **23** | **15** |

Map-type totals: 4 towns · 17 interiors · 94 fields · 54 dungeons · 16 secrets · 15 arenas.

## World-graph spine

```
Emberfoot → Verdant → MILLBROOK HUB → Tidewatch → Sunken
                        ├──────────→ Ashfall  → Frostpeak
                        ├──────────→ Gloomwood → Clockwork
                        └──────────→ Arcane Reach → Voidshore → The Rift
```

### Cross-region walk edges (both endpoint maps carry the portal; listed once)

| Edge | From map | To map |
|---|---|---|
| Emberfoot → Verdant | `map_009` | `map_013` |
| Verdant → Millbrook | `map_021` | `map_036` |
| Millbrook → Tidewatch | `map_037` | `map_046` |
| Tidewatch → Sunken | `map_054` | `map_057` |
| Ashfall → Frostpeak | `map_082` | `map_091` |
| Gloomwood → Clockwork | `map_119` | `map_127` |
| Arcane Reach → Voidshore | `map_156` | `map_163` |
| Voidshore → Rift | `map_173` | `map_183` |

### Waygate network (Millbrook Central `map_029` is the hub)
Bidirectional warp pairs: `map_029` ↔ `map_001` (Emberfoot Village), `map_041` (Tidewatch
Port), `map_145` (Arcane Sanctum), `map_073` (Ashfall entrance), `map_109` (Gloomwood
entrance). Waygates unlock per 15_maps_system/MAP_CONNECTIONS.md rules.

**Spawn-point convention:** every map defines spawn `main`. Cross-region walk portals target
spawn `from_<origin_slug>` on the destination map. Waygate arrivals target spawn `waygate`.
Frostpeak and Clockwork are deliberate branch termini (their arenas are the payoff).

---

## Region sections
Each lists: map allocation (types in ID order), monster slots, element mix, theme brief, boss
seed, and content blocks (NPC/quest/etc-material IDs per ID_REGISTRY.md). Role coverage rule
for monster batches: each region's normals must span ≥6 distinct role archetypes (melee,
ranged/caster, aerial, lurker/ambush, pack/swarm, tank/guard, support, burster) — no
stat-recolor rosters. Elites are flourished variants with stronger AI and silhouettes.

### R1 · Emberfoot Grounds (Lv 1–10) — `emberfoot`
Cinder-warmed training grounds around the starter town. Tone: warm, safe-feeling, first-steps.
- Maps: `001` town **Emberfoot Village** (start town, waygate) · `002`–`004` interiors
  (inn, outfitter, elder's hall) · `005`–`009` fields (ascending 1→10; `009` exits to Verdant)
  · `010` dungeon (Old Kiln Tunnels) · `011` secret · `012` arena (Kiln Heart).
- Mobs: `001`–`009` normal · `010` elite · `011` boss. Element mix: 6 `neutral`, 3 `fire`.
- Boss seed (`mob_011`, arena `map_012`): **Cindermaw** — an overgrown furnace-hound
  slumbering in the village's old kiln. Fire, `large`, single phase, generous telegraphs.
- Blocks: NPC `001`–`010` · quests `001`–`008` · etc `0001`–`0016`.

### R2 · Verdant Hollow (Lv 10–20) — `verdant`
Mossy sunken forest between Emberfoot and Millbrook. Tone: lush, dappled, first real danger.
- Maps: `013`–`021` fields (`013` entrance; `021` exits to Millbrook) · `022`–`025` dungeons
  (root warrens) · `026`–`027` secrets · `028` arena (Thornheart Grove).
- Mobs: `012`–`020` normal · `021`–`022` elite · `023` boss. Mix: 5 `nature`, 4 `neutral`.
- Boss seed (`mob_023`): **Thornback Sovereign** — a moss-armored beetle-stag older than the
  hollow. Nature, `large`, 2 phases (shell intact / shell cracked).
- Blocks: NPC `011`–`015` · quests `009`–`016` · etc `0017`–`0032`.

### R3 · Millbrook Township (hub, ~Lv 15) — `millbrook`
Timber-and-cobble market town; the social heart. Tone: cozy, lantern-lit, busy.
- Maps: `029` town **Millbrook Central** (hub, all waygates) · `030`–`035` interiors (inn,
  smithy, market hall, guild hall, tavern, mayor's house) · `036`–`037` fields (west/east
  outskirts; `036` from Verdant, `037` to Tidewatch) · `038`–`039` dungeons (Millbrook
  Catacombs) · `040` arena (The Cellar Deep).
- Mobs: `024`–`030` normal · `031` elite · `032` boss. Mix: 5 `neutral`, 2 `shadow`
  (catacomb vermin, outskirt pests; levels 12–17).
- Boss seed (`mob_032`): **The Cellar King** — a bloated rat-king throned on Millbrook's
  drowned grain stores. Shadow, `large`, summons vermin waves.
- Blocks: NPC `016`–`031` · quests `017`–`026` · etc `0033`–`0048`.

### R4 · Tidewatch Coast (Lv 20–30) — `tidewatch`
Wet cliffs, kelp shallows, a working port. Tone: bright brine, gulls, undertow menace.
- Maps: `041` town **Tidewatch Port** (waygate) · `042`–`045` interiors (harbormaster, inn,
  fishmonger, chandlery) · `046`–`051` fields (`046` from Millbrook) · `052`–`054` dungeons
  (sea caves; `054` descends to Sunken) · `055` secret · `056` arena (Siren Shoal).
- Mobs: `033`–`041` normal · `042`–`043` elite · `044` boss. Mix: 6 `frost`, 3 `neutral`.
- Boss seed (`mob_044`): **Tidecaller Morva** — a siren-priestess who sings ships onto the
  rocks. Frost, `large`, 2 phases (song / storm).
- Blocks: NPC `032`–`043` · quests `027`–`034` · etc `0049`–`0064`.

### R5 · Sunken Depths (Lv 30–40) — `sunken`
Drowned ruins below the coast; bioluminescent gloom. Tone: pressure, wonder, dread.
- Maps: `057`–`064` fields (`057` from Tidewatch) · `065`–`070` dungeons (ruin halls) ·
  `071` secret · `072` arena (The Warden's Vault).
- Mobs: `045`–`054` normal · `055`–`056` elite · `057` boss. Mix: 6 `frost`, 2 `shadow`,
  2 `neutral`.
- Boss seed (`mob_057`): **The Drowned Warden** — an armored husk still keeping a dead
  kingdom's last door. Frost/shadow theme (primary `frost`), `boss` size, 2 phases.
- Blocks: NPC `044`–`047` · quests `035`–`041` · etc `0065`–`0080`.

### R6 · Ashfall Wastes (Lv 40–50) — `ashfall`
Ash dunes and charred spires under a smoldering sky. Tone: oppressive heat, endurance.
- Maps: `073`–`082` fields (`073` waygate entrance; `082` climbs to Frostpeak) ·
  `083`–`087` dungeons (cinder vents) · `088`–`089` secrets · `090` arena (The Stoked Core).
- Mobs: `058`–`067` normal · `068`–`069` elite · `070` boss. Mix: 7 `fire`, 3 `neutral`.
- Boss seed (`mob_070`): **Karnothal, the Stoker** — a charred colossus feeding the wastes'
  eternal cinders. Fire, `boss` size, 2 phases (stoked / overburn).
- Blocks: NPC `048`–`051` · quests `042`–`048` · etc `0081`–`0096`.

### R7 · Frostpeak Ascent (Lv 50–60) — `frostpeak`
Vertical ice climbs above the ash line. Tone: thin air, silence, brittle light. Branch terminus.
- Maps: `091`–`100` fields (`091` from Ashfall; strongly vertical) · `101`–`105` dungeons
  (glacial caves) · `106`–`107` secrets · `108` arena (The Hornfall Summit).
- Mobs: `071`–`080` normal · `081`–`082` elite · `083` boss. Mix: 7 `frost`, 3 `neutral`.
- Boss seed (`mob_083`): **Rimehorn** — an avalanche-elk avatar of the summit. Frost,
  `boss` size, 2 phases (stampede / whiteout).
- Blocks: NPC `052`–`055` · quests `049`–`055` · etc `0097`–`0112`.

### R8 · Gloomwood (Lv 60–70) — `gloomwood`
Lightless canopy, fog, gnarled roots. Tone: hush, being watched.
- Maps: `109`–`119` fields (`109` waygate entrance; `119` to Clockwork) · `120`–`124`
  dungeons (hollow trunks, web vaults) · `125` secret · `126` arena (The Broodloom).
- Mobs: `084`–`093` normal · `094`–`095` elite · `096` boss. Mix: 4 `shadow`, 4 `nature`,
  2 `neutral`.
- Boss seed (`mob_096`): **Mother Gloam** — the spider-matron whose web *is* the wood's dark.
  Shadow, `boss` size, 2 phases (loom / frenzy).
- Blocks: NPC `056`–`059` · quests `056`–`062` · etc `0113`–`0128`.

### R9 · Clockwork Ruins (Lv 70–80) — `clockwork`
A dead brass city still ticking. Tone: awe, trespass, precision. Branch terminus.
- Maps: `127`–`135` fields (`127` from Gloomwood) · `136`–`142` dungeons (gearworks,
  vault lines) · `143` secret · `144` arena (The Mainspring).
- Mobs: `097`–`106` normal · `107`–`108` elite · `109` boss. Mix: 6 `neutral`, 4 `arcane`
  (constructs; sparks of the old power).
- Boss seed (`mob_109`): **The Custodian** — a haywire warden-engine guarding citizens who
  left centuries ago. Neutral/arcane (primary `arcane`), `boss` size, 3 phases.
- Blocks: NPC `060`–`063` · quests `063`–`069` · etc `0129`–`0144`.

### R10 · Arcane Reach (Lv 80–90) — `arcane_reach`
Floating shards and rune-lit sanctum of the magi. Tone: sublime, unstable footing.
- Maps: `145` town **Arcane Sanctum** (waygate) · `146`–`149` interiors (athenaeum, enchanter,
  inn, observatory) · `150`–`156` fields (`156` to Voidshore) · `157`–`160` dungeons
  (collapsed spires) · `161` secret · `162` arena (The Unbound Stacks).
- Mobs: `110`–`119` normal · `120`–`121` elite · `122` boss. Mix: 7 `arcane`, 3 `neutral`.
- Boss seed (`mob_122`): **The Unbound Archive** — a living spell-library that reads its
  visitors. Arcane, `boss` size, 3 phases (index / errata / burn the books).
- Blocks: NPC `064`–`075` · quests `070`–`077` · etc `0145`–`0160`.

### R11 · Voidshore (Lv 90–100) — `voidshore`
Where the sky tore and a black tide came in. Tone: last-lighthouse defiance.
- Maps: `163`–`173` fields (`163` from Arcane Reach; `173` to the Rift) · `174`–`179`
  dungeons (void-eaten cliffs) · `180`–`181` secrets · `182` arena (The Last Jetty).
- Mobs: `123`–`132` normal · `133`–`135` elite · `136` boss. Mix: 6 `shadow`, 4 `arcane`.
- Boss seed (`mob_136`): **Voidmaw Herald** — the hunger that walks ahead of the tide.
  Shadow, `boss` size, 3 phases.
- Blocks: NPC `076`–`079` · quests `078`–`084` · etc `0161`–`0176`.

### R12 · The Rift (Lv 100+) — `rift`
Reality fractured into mixed-motif shardscapes. Endgame; party content. Designed **last**.
- Maps: `183`–`188` fields (`183` from Voidshore; staging shards) · `189`–`194` dungeons
  (raid approaches) · `195`–`196` secrets · `197`–`200` raid arenas (one per raid boss).
- Mobs: `137`–`144` normal (Lv 100–104) · `145`–`146` elite (Lv 103–105) · `147`–`150`
  **raid bosses** (multi-phase, party-scaled; see PARTY.md + COMBAT_FORMULA.md).
- Raid boss seeds (aspects of the tear): `147` **The First Fracture** (arcane, arena
  `map_197`) · `148` **The Echo of Everything** (shadow, `map_198`) · `149` **The Borrowed
  Furnace** (fire, `map_199`) · `150` **The Still Abyss** (frost, `map_200`).
- Mix (normals/elites): 5 `arcane`, 4 `shadow`, 1 `neutral`.
- Blocks: NPC `080`–`084` (rift-camp vendors/handlers) · quests `085`–`090` · etc
  `0177`–`0192`.

## Element affinity summary
Region dominant elements for tuning and drops: R1 fire · R2 nature · R3 neutral/shadow ·
R4–R5 frost · R6 fire · R7 frost · R8 shadow/nature · R9 neutral/arcane · R10 arcane ·
R11 shadow/arcane · R12 arcane/mixed. Monsters use the matching palette ramp per ART_BIBLE.

## Open Questions
- Should Frostpeak/Clockwork termini get a late-game shortcut back to Millbrook besides the
  return scroll (e.g., a one-way drop chute)? Owner: MAP_CONNECTIONS.md, Phase B.
- Interior maps and combat: interiors are combat-free by default — confirm in MAPS_SYSTEM.md.
