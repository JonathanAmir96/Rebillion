# WORLD_PLAN.md — Authoritative Region / Map / Monster Allocation (v2)

Source of truth for world structure. **v2 (owner revision):** the world is **two islands,
8 bosses, 2 party quests**; the game's level cap is **300 (initial design)** and this run
authors the **first arc — Lv 1–42 content**. Every map and monster inherits its region's biome
identity (palette ramp + motif per `40_assets/ART_BIBLE.yaml` `environment.biome_identity`)
and level band. ID blocks are owned by `ID_REGISTRY.md`; this file allocates **what each ID
is**. Phase D region batches treat their region section here as their biome brief.

## The two islands

- **Emberfoot Isle** — the training island: one sheltered village, warm cinder fields, a
  first taste of every mechanic, one graduation boss. Lv 1–8. 16 maps.
- **Harthmoor Isle** — the main island (Victoria-style): the boat from Emberfoot lands at
  Rosen Harbor; Millbrook is the social hub city; six hunting regions ring it, ending in the
  Clockwork Ruins endgame. Lv 8–40. 184 maps.

Crossing: the **Harborwind Ferry** (`map_015`, combat-free `interior` map) connects
Emberfoot Village's dock (`map_001`) to Rosen Harbor (`map_017`) via `door` portals at each
end. Transit is instant at launch (scheduled sailings are flavor, see Open Questions).

## Region overview

| # | Region | Slug | Level | Biome key (ramp) | Maps | N | E | B |
|---|--------|------|-------|------------------|------|---|---|---|
| 1 | Emberfoot Isle | `emberfoot` | 1–8 | emberfoot (ember) | 16 | 10 | 1 | 1 |
| 2 | Millbrook & Rosen Harbor (hub) | `millbrook` | 8–14 | old_town (earth) | 26 | 12 | 2 | 1 |
| 3 | Verdant Hollow | `verdant` | 8–16 | verdant_hollow (verdant) | 28 | 16 | 3 | 1 |
| 4 | Tidewatch Coast | `tidewatch` | 14–22 | tidewatch (tide) | 27 | 16 | 3 | 1 |
| 5 | Gloomwood | `gloomwood` | 20–28 | gloomwood (verdant dark) | 27 | 16 | 3 | 1 |
| 6 | Ashfall Barrens | `ashfall` | 26–34 | ashfall (ember/ash) | 27 | 16 | 3 | 1 |
| 7 | Sunken Depths | `sunken` | 30–38 | tidewatch_dark (tide) | 25 | 16 | 4 | 1 |
| 8 | Clockwork Ruins (endgame) | `clockwork` | 34–40(+2) | clockwork (earth/stone) | 24 | 16 | 5 | 1 |
| — | **TOTAL** | | | | **200** | **118** | **24** | **8** |

Map-type totals: 4 towns · 16 interiors (incl. ferry) · 105 fields · 53 dungeons (incl. 6
party-quest maps) · 14 secrets · 8 arenas. Authored content spans Lv 1–42 (Clockwork elites
top out at 42); the game cap is 300 (initial design), so leveling past the arc is a slow
grind on endgame maps/PQs until future arcs land. ART_BIBLE biome keys frostpeak /
arcane_reach / voidshore / rift are **reserved for those future arcs** (as are the four 3rd
jobs); do not use them in this run's content.

## World-graph spine

```
EMBERFOOT ISLE (1–8)                HARTHMOOR ISLE (8–40)
Emberfoot Village ──ferry──> Rosen Harbor ─ Millbrook Central (hub)
                                              ├─ west ─> Verdant Hollow (8–16) ─> Gloomwood (20–28) ─> Ashfall (26–34) ─> Clockwork (34–40)
                                              └─ east ─> Tidewatch Coast (14–22) ─> Sunken Depths (30–38, terminus)
```

### Cross-region walk edges (both endpoint maps carry the portal; listed once)

| Edge | From map | To map |
|---|---|---|
| Emberfoot Village → Ferry | `map_001` (door) | `map_015` |
| Ferry → Rosen Harbor | `map_015` (door) | `map_017` |
| Rosen Harbor → Millbrook Central | `map_017` | `map_018` |
| Millbrook (west outskirts) → Verdant | `map_027` | `map_043` |
| Millbrook (east road) → Tidewatch | `map_028` | `map_076` |
| Verdant (deep hollow) → Gloomwood | `map_060` | `map_098` |
| Gloomwood (north fen) → Ashfall | `map_114` | `map_125` |
| Tidewatch (sea cave) → Sunken | `map_094` | `map_152` |
| Ashfall (char ridge) → Clockwork | `map_141` | `map_177` |

Sunken Depths and Clockwork Ruins are deliberate termini (their bosses are the payoff).

### Waygate network (Millbrook Central `map_018` is the hub)
Bidirectional warp pairs: `map_018` ↔ `map_001` (Emberfoot Village — unlocks after the first
ferry crossing), `map_071` (Tidewatch Port), `map_098` (Gloomwood entrance), `map_125`
(Ashfall entrance). Rules per 15_maps_system/MAP_CONNECTIONS.md.

**Spawn-point convention:** every map defines spawn `main`. Cross-region walk portals target
spawn `from_<origin_slug>` on the destination map; ferry doors target `from_ferry`; waygate
arrivals target `waygate`.

## Party quests (concept owner: 10_systems/social/PARTY_QUEST.md)
Two instanced co-op runs; each ends at an existing boss (no extra boss slots):
- **`pq_undervault` — Undervault Heist** (Lv 15–22, party 3–6): stages `map_038`–`map_040`
  → finale arena `map_042` (The Cellar King, party-instanced).
- **`pq_mainspring` — Mainspring Trial** (Lv 32–40, party 3–6): stages `map_195`–`map_197`
  → finale arena `map_200` (The Custodian, party-instanced).
Solo players still fight both bosses via the arena's open (non-PQ) entry at reduced reward.

---

## Region sections
Role coverage rule for monster batches: each region's normals must span ≥6 distinct role
archetypes (melee, ranged/caster, aerial, lurker/ambush, pack/swarm, tank/guard, support,
burster) — no stat-recolor rosters. Elites are flourished variants with stronger AI and
silhouettes. Boss uniques: boss #n owns `item_equip_{0199+2n}`/`{0200+2n}` (Cindermaw
0201–0202 … Custodian 0215–0216) per ID_REGISTRY.md.

### R1 · Emberfoot Isle (Lv 1–8) — `emberfoot`
Cinder-warmed training island around the starter village. Tone: warm, safe, first-steps.
- Maps `001`–`016`: `001` town **Emberfoot Village** (dock, waygate) · `002`–`004` interiors
  (inn, outfitter, elder's hall) · `005`–`011` fields (ascending 1→8) · `012`–`013` dungeons
  (Old Kiln Tunnels) · `014` secret · `015` interior **Harborwind Ferry** · `016` arena
  (Kiln Heart).
- Mobs `001`–`012`: normals `001`–`010` (7 `neutral`, 3 `fire`) · elite `011` · boss `012`.
- Boss #1 (`mob_012`, Lv 8, arena `map_016`): **Cindermaw** — an overgrown furnace-hound
  slumbering in the village kiln. Fire, `large`, single phase, generous telegraphs; the
  island's graduation fight before the ferry.
- Blocks: NPC `001`–`010` · quests `001`–`010` · etc `0001`–`0016`.

### R2 · Millbrook & Rosen Harbor (Lv 8–14, hub) — `millbrook`
Harbor district + timber-and-cobble market city; the social heart. Tone: cozy, lantern-lit.
- Maps `017`–`042`: `017` town **Rosen Harbor** (ferry dock) · `018` town **Millbrook
  Central** (hub, waygates) · `019`–`026` interiors (inn, smithy, market hall, guild hall,
  tavern, mayor's house, harbor office, bank) · `027`–`035` fields (west outskirts `027`,
  east road `028`, farmland, mill lanes) · `036`–`037` dungeons (Millbrook Catacombs) ·
  `038`–`040` dungeons (**PQ `pq_undervault` stages**, party-instanced) · `041` secret ·
  `042` arena (The Cellar Deep — also the PQ finale instance).
- Mobs `013`–`027`: normals `013`–`024` (8 `neutral`, 4 `shadow`; levels 8–14) · elites
  `025`–`026` · boss `027`.
- Boss #2 (`mob_027`, Lv 14, arena `map_042`): **The Cellar King** — a bloated rat-king
  throned on Millbrook's drowned grain stores. Shadow, `large`, summons vermin waves.
- Blocks: NPC `011`–`032` · quests `011`–`024` · etc `0017`–`0032`.

### R3 · Verdant Hollow (Lv 8–16) — `verdant`
Mossy sunken forest west of Millbrook. Tone: lush, dappled, first real danger.
- Maps `043`–`070`: `043`–`060` fields (`043` entrance from `027`; `060` deep hollow exits
  to Gloomwood) · `061`–`067` dungeons (root warrens) · `068`–`069` secrets · `070` arena
  (Thornheart Grove).
- Mobs `028`–`047`: normals `028`–`043` (10 `nature`, 6 `neutral`) · elites `044`–`046` ·
  boss `047`.
- Boss #3 (`mob_047`, Lv 16, arena `map_070`): **Thornback Sovereign** — a moss-armored
  beetle-stag older than the hollow. Nature, `large`, 2 phases (shell intact / cracked).
- Blocks: NPC `033`–`040` · quests `025`–`036` · etc `0033`–`0048`.

### R4 · Tidewatch Coast (Lv 14–22) — `tidewatch`
Wet cliffs, kelp shallows, a working port east of Millbrook. Tone: bright brine, undertow.
- Maps `071`–`097`: `071` town **Tidewatch Port** (waygate) · `072`–`075` interiors
  (harbormaster, inn, fishmonger, chandlery) · `076`–`088` fields (`076` entrance from
  `028`) · `089`–`094` dungeons (sea caves; `094` descends to Sunken) · `095`–`096` secrets
  · `097` arena (Siren Shoal).
- Mobs `048`–`067`: normals `048`–`063` (10 `frost`, 6 `neutral`) · elites `064`–`066` ·
  boss `067`.
- Boss #4 (`mob_067`, Lv 22, arena `map_097`): **Tidecaller Morva** — a siren-priestess who
  sings ships onto the rocks. Frost, `large`, 2 phases (song / storm).
- Blocks: NPC `041`–`054` · quests `037`–`048` · etc `0049`–`0064`.

### R5 · Gloomwood (Lv 20–28) — `gloomwood`
Lightless canopy and fog beyond the hollow. Tone: hush, being watched.
- Maps `098`–`124`: `098`–`114` fields (`098` entrance + waygate) · `115`–`121` dungeons
  (hollow trunks, web vaults) · `122`–`123` secrets · `124` arena (The Broodloom).
- Mobs `068`–`087`: normals `068`–`083` (8 `shadow`, 6 `nature`, 2 `neutral`) · elites
  `084`–`086` · boss `087`.
- Boss #5 (`mob_087`, Lv 28, arena `map_124`): **Mother Gloam** — the spider-matron whose
  web *is* the wood's dark. Shadow, `boss` size, 2 phases (loom / frenzy).
- Blocks: NPC `055`–`061` · quests `049`–`058` · etc `0065`–`0080`.

### R6 · Ashfall Barrens (Lv 26–34) — `ashfall`
Ash dunes and charred spires on the island's burnt north. Tone: oppressive heat, endurance.
- Maps `125`–`151`: `125`–`141` fields (`125` entrance + waygate; `141` char ridge exits to
  Clockwork) · `142`–`148` dungeons (cinder vents) · `149`–`150` secrets · `151` arena
  (The Stoked Core).
- Mobs `088`–`107`: normals `088`–`103` (10 `fire`, 6 `neutral`) · elites `104`–`106` ·
  boss `107`.
- Boss #6 (`mob_107`, Lv 34, arena `map_151`): **Karnothal, the Stoker** — a charred
  colossus feeding the barrens' eternal cinders. Fire, `boss` size, 2 phases.
- Blocks: NPC `062`–`068` · quests `059`–`068` · etc `0081`–`0096`.

### R7 · Sunken Depths (Lv 30–38) — `sunken`
Drowned ruins below the coast; bioluminescent gloom; `water_physics` fields. Terminus.
- Maps `152`–`176`: `152`–`163` fields (`152` entrance from `094`) · `164`–`173` dungeons
  (ruin halls) · `174`–`175` secrets · `176` arena (The Warden's Vault).
- Mobs `108`–`128`: normals `108`–`123` (10 `frost`, 4 `shadow`, 2 `neutral`) · elites
  `124`–`127` · boss `128`.
- Boss #7 (`mob_128`, Lv 38, arena `map_176`): **The Drowned Warden** — an armored husk
  still keeping a dead kingdom's last door. Frost, `boss` size, 2 phases.
- Blocks: NPC `069`–`075` · quests `069`–`078` · etc `0097`–`0112`.

### R8 · Clockwork Ruins (Lv 34–40, endgame) — `clockwork`
A dead brass city still ticking, past the char ridge. Tone: awe, trespass, precision.
- Maps `177`–`200`: `177`–`188` fields (`177` entrance from `141`) · `189`–`194` dungeons
  (gearworks) · `195`–`197` dungeons (**PQ `pq_mainspring` stages**, party-instanced) ·
  `198`–`199` secrets · `200` arena (The Mainspring — also the PQ finale instance).
- Mobs `129`–`150`: normals `129`–`144` (8 `neutral`, 8 `arcane`; Lv 34–40) · elites
  `145`–`149` (Lv 40–42) · boss `150`.
- Boss #8 (`mob_150`, Lv 40, arena `map_200`): **The Custodian** — a haywire warden-engine
  guarding citizens who left centuries ago. Arcane, `boss` size, 3 phases;
  party-recommended (PQ finale), soloable via open arena entry at reduced reward.
- Blocks: NPC `076`–`084` · quests `079`–`086` (+ PQ quests `087`–`090`) · etc
  `0113`–`0128`.

## Element affinity summary
R1 fire · R2 neutral/shadow · R3 nature · R4 frost · R5 shadow/nature · R6 fire ·
R7 frost/shadow · R8 neutral/arcane. `arcane` monsters appear only in Clockwork — arcane
stays special per ART_BIBLE usage rules. Monsters use the matching palette ramp.

## Open Questions
- Ferry: instant transit at launch; add scheduled sailings + an on-deck ambush event later?
  Owner: MAP_CONNECTIONS.md (flavor-only until then).
- Verdant (ends Lv 16) feeds Gloomwood (starts Lv 20); the intended path detours through
  Tidewatch first. Acceptable nonlinearity or add a Lv 16–20 bridge field to Verdant's deep
  end? Default: keep, signpost via quests.
- Future-expansion islands (frostpeak / arcane_reach / voidshore / rift biomes + 3rd jobs):
  out of scope this run; revisit after cap raise.
