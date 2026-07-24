# MAP_CONNECTIONS.md — Portal Rules, Spawn Naming & the World Graph

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
docs/ID_REGISTRY.md, 10_systems/DEATH_PENALTY.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md,
10_systems/HUD.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md

Owner doc for the **rules** portals, spawns, and the Harthmoor Coachworks follow between maps.
`docs/WORLD_PLAN.md`'s "Cross-region walk edges" and "Harthmoor Coachworks" tables are the sole
authoritative source for *which* `map_NNN` pairs connect and *where* coach stations sit — they
are cited, never reproduced, here. This doc formalizes the spawn-naming convention
`docs/WORLD_PLAN.md` previews, the paid coach-travel rules, the Harborwind Ferry rules,
death-return routing, `dead_end` marking, and the region-progression gate policy. Portal object
params are `15_maps_system/MAP_INTERACTABLES.md` §2's; this doc owns only the rules governing them.

## 1. Portal kind semantics between regions

| Kind | Typical use | Region span |
|---|---|---|
| `edge` | Most field/dungeon chain links; the 8 cross-region walk edges (`docs/WORLD_PLAN.md`) | Usually intra-region; cross-region for the 8 listed walk edges |
| `door` | Town↔interior; every arena's entry gate (`15_maps_system/MAPS_SYSTEM.md` §8); both Harborwind Ferry ends | Same-region, except the two ferry doors that bridge Emberfoot↔Millbrook |
| `coach` | The paid Harthmoor Coachworks town-to-town network (`docs/WORLD_PLAN.md` "Harthmoor Coachworks") | Cross-region by design — that is its purpose |

The retired free-warp `waygate` kind (v1) no longer exists; `coach` is the only long-distance
transit kind, and it always charges a `shards` fare (§3). Per `00_vision/GLOSSARY.md`'s Transport
section, `waygate` / `waygate_console` are invalid tokens in all content.

## 2. Spawn-point naming law

Formalizes the convention `docs/WORLD_PLAN.md`'s "Spawn-point convention" paragraph previews.
Reserved spawn tokens are listed below; a map may also author additional freely-named spawns (e.g. a
multi-entrance dungeon's `upper_west`) as long as they never collide with the reserved set.

| Spawn name | Required on | Meaning |
|---|---|---|
| `main` | Every map, exactly one | Default arrival point — direct teleport, quest-start, and the fallback target for any portal that doesn't name another spawn |
| `from_<origin_slug>` | Every map that is the destination of an `edge` portal crossing a region boundary | `<origin_slug>` is the origin **region**'s GLOSSARY slug (not a per-map slug — maps have none). An intra-region `edge` targets plain `main` unless the destination map has multiple distinct entrances needing disambiguation |
| `from_ferry` | Both Harborwind Ferry endpoint maps (`map_001` dock, `map_017` Rosen Harbor) and the ferry interior (`map_015`) | The fixed arrival point for a Harborwind Ferry `door` crossing |
| `coach_stop` | Every town map that hosts a coach station (`15_maps_system/MAP_INTERACTABLES.md` §9) | The fixed arrival point for all Harthmoor Coachworks transits; exactly one per coach-bearing town |

Each of `docs/WORLD_PLAN.md`'s 8 bidirectional cross-region walk edges produces exactly two
`from_<origin_slug>` spawns (one per endpoint, each named for the *other* side's region) — e.g.
the Millbrook↔Verdant edge gives Verdant's endpoint a `from_millbrook` spawn and Millbrook's
endpoint a `from_verdant` spawn.

## 3. Harthmoor Coachworks — paid town transport

Replaces the retired free-warp network (v2.2). The Coachworks is a **paid** `shards` service, not a
free unlock-and-warp loop — travel is a deliberate sink, walked by default and short-cut by coach
(P3: a legible world you can traverse, not teleport across for free).

- **Coach stations** sit in the five Harthmoor ring towns per `docs/WORLD_PLAN.md`'s "Harthmoor
  Coachworks" table: **Rosen Harbor** (`map_017`), **Millbrook Central** (`map_018`), **Mossmere**
  (`map_043`), **Cindershelf** (`map_125`), and **Tidewatch Port** (`map_071`). Emberfoot Village
  (`map_001`, the training island) has no coach station; it connects to Harthmoor only by the ferry
  (§3.1). `docs/WORLD_PLAN.md` owns which towns carry a station — this doc never adds one.
- Each station places a `coach_stop` spawn (§2) and a `coach_station` interactable
  (`15_maps_system/MAP_INTERACTABLES.md` §9). Interacting opens a destination menu
  (`10_systems/HUD.md`) listing every *other* coach station; choosing one charges the fare (below)
  and lands the player on the destination's `coach_stop` spawn.
- **Fares cost `shards`, owned by `10_systems/ECONOMY.md`, scaling with ring distance.** This doc
  does **not** set fare numbers; it only asserts the pricing *model*: a ride's cost rises with how
  many ring hops separate the two stations along `docs/WORLD_PLAN.md`'s ring order
  (Millbrook ↔ Verdant ↔ Gloomwood ↔ Ashfall ↔ Tidewatch ↔ Millbrook), with **Millbrook Central as
  the hub** most rides route through conceptually. If `10_systems/ECONOMY.md` has not yet published
  a coach fare table, that is flagged in this doc's Open Questions and handed to ECONOMY's owner —
  no fare number is invented here.
- **No cooldown, no unlock gate.** Any character may ride between any two stations at any level; the
  fare is the only cost. There is no per-character "unlocked stations" set (that was the retired
  waygate mechanic) — every station is always available to anyone standing at another station.
- **One free novice pilgrimage ride.** The Rosen Harbor coachman gives each fresh novice **one free
  ride to their job instructor's town** — the advancement pilgrimage (`docs/WORLD_PLAN.md` "Job
  instructors"; instructor towns are Cindershelf / Tidewatch Port / Mossmere / Millbrook per line).
  This is a one-time, server-authoritative per-character grant (`10_systems/PERSISTENCE.md`); every
  ride thereafter is paid. Cindershelf (the Bulwark line) is deliberately the boldest first trip.
- **The Millbrook Return Scroll** (`item_use_0013`, `docs/ID_REGISTRY.md`) remains the only magic
  escape home and is a consumable item, not a coach — its rules are `10_systems/ITEMS.md`'s /
  `10_systems/ECONOMY.md`'s, not this doc's. There are **no free warps** otherwise.

### 3.1 Harborwind Ferry

The **Harborwind Ferry** (`map_015`, a combat-free `interior` map) connects Emberfoot Village's dock
(`map_001`) to Rosen Harbor (`map_017`) via a `door` portal at each end, targeting the `from_ferry`
spawn. It charges a **small `shards` fare per crossing** (fare owned by `10_systems/ECONOMY.md`);
transit is instant at launch (scheduled sailings are flavor — see `docs/WORLD_PLAN.md` Open
Questions). The ferry is the sole crossing between the two islands. Its fare and the coach fares are
separate line items in `10_systems/ECONOMY.md`.

## 4. Death-return routing

`10_systems/DEATH_PENALTY.md` §4 owns the bind mechanic and respawn destination (a bound town's
`main` spawn) — not restated here. This doc owns only *getting back out*: every valid bind town is
one of the six v2 towns (`docs/WORLD_PLAN.md`), five of which host a coach station, so a respawned
character can pay for a coach ride back toward the frontier as ordinary paid travel (§3) — never a
special death-only routing path, and never free. A character bound at Emberfoot Village (no station)
returns to Harthmoor via the ferry (§3.1). Coach travel does not check the player's state on death
any more than on any other turn: it is the same paid service either way.

## 5. `dead_end` marking

Per `docs/VALIDATION.md` §5: any portal with **no matching reverse portal** on its destination map
must carry `dead_end: true`, authored on the portal that *leads into* the one-way transition (not
on the destination side). This is a validator-exemption flag only — it tells the world-graph
checker "do not require a reverse portal here" — not a required visible UI marker, though a map UI
may optionally surface it (`10_systems/HUD.md`'s call, not specified here). Ordinary `edge` / `door`
portals, which always pair with a reverse, are never marked `dead_end`. Coach transits are not
graph edges in the reachability sense (they are a menu-driven service between fixed stations, not a
walk portal), so they are neither part of the cross-region walk-edge set nor subject to `dead_end`.

## 6. Region-progression gate policy: none

**Decision: no authored region-to-region progression gate exists anywhere in the portal system** —
no level lock, quest-flag lock, or item-key lock on any region boundary (contrast with an optional
*per-arena* quest-flag gate, `15_maps_system/MAPS_SYSTEM.md` §8, a narrower, different concern). A
Lv 1 character can walk into a Lv 40 region; nothing here stops them. The only gate is the emergent
difficulty curve: `10_systems/COMBAT_FORMULA.md` §9's level-difference dampener makes a badly
under-level fight genuinely hard well before it's mechanically blocked, reinforced by
`10_systems/LEVELING.md`'s exp curve (which consumes that same §9 table) cratering reward for
over-level kills, and `docs/WORLD_PLAN.md`'s ring-shaped world spine naturally lands a
region-by-region player roughly in-band anyway. This is deliberate (P2 — no trap walls, only a
hard-but-not-impossible curve). Coach travel (§3) likewise never checks level — the fare is the only
friction, and a player who pays to ride into a deadly region simply finds it deadly.

## 7. Termini — the ring, the spur, and the endgame heart

`docs/WORLD_PLAN.md`'s "Cross-region walk edges" table is the **complete, authoritative** set of
authorized cross-region walk edges — this doc adds none and invents no drop-chutes (the v1
Frostpeak/Clockwork chutes are retired along with the reserved biomes). The world graph is a
**ring**, not a tree, so it legitimately contains a cycle and two deliberate termini:

- **Ring closure.** The Tidewatch north strand → Ashfall east dunes edge (`map_088` → `map_140`)
  closes the Millbrook ↔ Verdant ↔ Gloomwood ↔ Ashfall ↔ Tidewatch ↔ Millbrook loop. This is a
  legitimate cycle-forming edge, not a duplicate or an error.
- **Clockwork Ruins (endgame heart).** The island's dead brass center is reached by **two** gates —
  Ashfall's char ridge → Clockwork east gate (`map_141` → `map_177`) and Gloomwood's web vaults →
  Clockwork west gate (`map_121` → `map_188`). Both are authorized edges; Clockwork is a Sleepywood-
  style deep center, not a dead end (it has two ways in and out).
- **Sunken Depths (deliberate depth spur terminus).** Reached from the Tidewatch sea cave
  (`map_094` → `map_152`). Sunken is a coastal spur with a single walk connection and no coach
  station; the intended exit is to walk back to Tidewatch or use the Millbrook Return Scroll. If
  Phase D authors the Sunken entrance as one-way, that portal carries `dead_end: true` (§5); if it
  authors a reverse walk edge, both endpoints pair normally. Either way this is the design intent,
  not a graph fault.

Return from any terminus is by walking back along the ring/spur, paying for a coach ride from the
nearest coach town (Tidewatch Port for the Sunken/Tidewatch side; Cindershelf for the Ashfall/
Clockwork side), or the Millbrook Return Scroll — never a free warp. Phase D authors every
cross-region portal directly from `docs/WORLD_PLAN.md`'s edge table; this section only classifies
the three cases so `docs/VALIDATION.md` §5 does not mistake a legitimate ring/terminus edge for a
fault (see Open Questions).

## Map-level edge table

Authored by the Phase D world-graph reconciler after all 200 maps exist, directly from
`docs/WORLD_PLAN.md`'s "Cross-region walk edges" table.

## Open Questions

- ~~`docs/VALIDATION.md` §5 could falsely fail the legitimate ring-closure edge
  (`map_088`→`map_140`), the second Clockwork gate (`map_121`→`map_188`), and the one-way Sunken
  spur terminus.~~ **Resolved 2026-07-24:** VALIDATION.md §5 now tests reachability (not
  acyclicity), carves out `dead_end: true` portals, and excludes `coach` portals from the
  walk-edge match — exactly the rewording this doc's §7 required.
- **Coach fare table.** `10_systems/ECONOMY.md` owns the `shards` fare per ride (scaling with ring
  distance) and the ferry fare. As of this revision ECONOMY has no published coach fare table
  (it is being retabled concurrently); this doc references the model only. Handed to ECONOMY's
  owner to publish the fare table; flag if the ring-distance/Millbrook-hub pricing model here needs
  adjustment once those numbers land.
- Whether the free novice pilgrimage ride (§3) should also cover the *return* trip, or only the
  outbound leg to the instructor's town, is a light design call — default here is outbound-only.
- Freely-authored extra spawn names on multi-entrance maps (§2) have no stricter naming convention
  yet; flag if Phase D authoring shows collisions or ambiguity in practice.
- Whether a map UI visually flags a `dead_end` portal before the player commits to it (§5) is
  `10_systems/HUD.md`'s design call, not decided here.
