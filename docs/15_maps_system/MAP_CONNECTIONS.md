# MAP_CONNECTIONS.md — Portal Rules, Spawn Naming & the World Graph

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
docs/ID_REGISTRY.md, 10_systems/DEATH_PENALTY.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md,
10_systems/HUD.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md

Owner doc for the **rules** portals, spawns, and the coach service follow between maps.
`docs/WORLD_PLAN.md`'s "Cross-region walk edges" table and "Harthmoor Coachworks" section are the
sole authoritative source for *which* `map_NNN` pairs connect and where the coach stations sit —
they are cited, never reproduced, here. This doc formalizes the spawn-naming convention
`docs/WORLD_PLAN.md` previews, the paid coach fare rule, death-return routing, `dead_end`
marking, the region-progression gate policy, and the Sunken Depths terminus status. Portal object
params are `15_maps_system/MAP_INTERACTABLES.md` §2's; this doc owns only the rules governing
them.

## 1. Portal kind semantics between regions

| Kind | Typical use | Region span |
|---|---|---|
| `edge` | Most field/dungeon chain links; the cross-region walk edges of `docs/WORLD_PLAN.md`'s edge table | Usually intra-region; cross-region only for the listed edges (§7) |
| `door` | Town↔interior; every arena's entry gate (`15_maps_system/MAPS_SYSTEM.md` §8); the Harborwind Ferry crossings (`docs/WORLD_PLAN.md` edge table) | Same-region, except the ferry's island-crossing doors |
| `coach` | The paid Harthmoor Coachworks station-to-station transit (`docs/WORLD_PLAN.md` "Harthmoor Coachworks") | Cross-region by design — that is its purpose |

## 2. Spawn-point naming law

Formalizes the convention `docs/WORLD_PLAN.md`'s "Spawn-point convention" paragraph previews.
Three tokens are **reserved**; a map may also author additional freely-named spawns (e.g. a
multi-entrance dungeon's `upper_west`) as long as they never collide with the reserved set.

| Spawn name | Required on | Meaning |
|---|---|---|
| `main` | Every map, exactly one | Default arrival point — direct teleport, quest-start, and the fallback target for any portal that doesn't name another spawn |
| `from_<origin_slug>` | Every map that is the destination of an `edge` portal crossing a region boundary | `<origin_slug>` is the origin **region**'s GLOSSARY slug (not a per-map slug — maps have none). An intra-region `edge` targets plain `main` unless the destination map has multiple distinct entrances needing disambiguation |
| `coach_stop` | Every coach-station town (the 5 Harthmoor stations, §3) | The fixed arrival point for all coach transits; exactly one per station map |

Each of `docs/WORLD_PLAN.md`'s bidirectional cross-region walk edges produces exactly two
`from_<origin_slug>` spawns (one per endpoint, each named for the *other* side's region) — e.g.
the Millbrook↔Verdant edge gives Verdant's endpoint (`map_043`) a `from_millbrook` spawn and
Millbrook's endpoint (`map_027`) a `from_verdant` spawn. The Harborwind Ferry's `door` portals
are the one special case: per `docs/WORLD_PLAN.md`'s spawn-point convention, docking doors
target the destination's `from_ferry` spawn (a fourth reserved token, same collision rules).

## 3. Coach fare rule (Harthmoor Coachworks)

**Every ride is paid in `shards` — there are no free warps anywhere in the world** (v2.2: the
earlier free-warp mechanism is retired; its token is invalid per `00_vision/GLOSSARY.md`). The
ring is walked; the coach is the paid shortcut.

- **Stations:** the 5 Harthmoor towns — Rosen Harbor (`map_017`), Millbrook Central (`map_018`),
  Mossmere (`map_043`), Cindershelf (`map_125`), Tidewatch Port (`map_071`) — per
  `docs/WORLD_PLAN.md` "Harthmoor Coachworks"; that section, not this doc, owns the station list.
- **Boarding:** the player talks to the station's coachman NPC
  (`15_maps_system/MAP_INTERACTABLES.md` §9), picks a destination station from the fare dialogue
  (`10_systems/HUD.md` renders it), and pays; the co-located `portal(kind: coach)` then delivers
  them to the destination's `coach_stop` spawn (§2).
- **Fares scale with ring distance** between the two stations; the fare table is
  `10_systems/ECONOMY.md`'s, cited, never restated, here. The Harborwind Ferry's per-crossing
  shard fare is likewise `10_systems/ECONOMY.md`'s.
- **No unlock state:** stations are never discovered, unlocked, or bound — any character with the
  fare may ride between any two stations from their first visit
  (`10_systems/PERSISTENCE.md` stores nothing for the coach).
- **One exception:** the Rosen Harbor coachman grants each fresh novice **one free ride to their
  job instructor's town** (the advancement pilgrimage, `docs/WORLD_PLAN.md`).
- The **Millbrook Return Scroll** (`item_use_0013`) remains the sole magic escape home; it is an
  item, not a portal rule (owner: the use-item tables), noted here only as the coach's
  complement.

## 4. Death-return routing

`10_systems/DEATH_PENALTY.md` §4 owns the bind mechanic and respawn destination (a bound town's
`main` spawn) — not restated here. This doc owns only *getting back out*: every valid bind town
(`docs/WORLD_PLAN.md`'s 6 towns) is also a transport endpoint — the 5 Harthmoor towns are coach
stations (§3) and Emberfoot Village has the ferry dock — so a respawned character always steps
straight back into ordinary travel (walk the ring, or pay the coach/ferry fare) — never a
special death-only routing path.

## 5. `dead_end` marking

Per `docs/VALIDATION.md` §5: any portal with **no matching reverse portal** on its destination map
must carry `dead_end: true`, authored on the portal that *leads into* the one-way transition (not
on the destination side). This is a validator-exemption flag only — it tells the world-graph
checker "do not require a reverse portal here" — not a required visible UI marker, though a map UI
may optionally surface it (`10_systems/HUD.md`'s call, not specified here). Ordinary `edge`/`door`
portals, which always pair with a reverse, are never marked `dead_end`; a `coach` portal is never
marked either — every transit runs between two stations that each carry a coach portal (§3).

## 6. Region-progression gate policy: none

**Decision: no authored region-to-region progression gate exists anywhere in the portal/coach
system** — no level lock, quest-flag lock, or item-key lock on any region boundary (contrast with
an optional *per-arena* quest-flag gate, `15_maps_system/MAPS_SYSTEM.md` §8, a narrower, different
concern). A Lv 8 fresh graduate can walk the ring straight into the Clockwork Ruins (Lv 34–40);
nothing here stops them. The only gate is
the emergent difficulty curve: `10_systems/COMBAT_FORMULA.md` §9's level-difference dampener makes
a badly under-level fight genuinely hard well before it's mechanically blocked, reinforced by
`10_systems/LEVELING.md`'s exp curve (which consumes that same §9 table) cratering reward for
over-level kills, and `docs/WORLD_PLAN.md`'s world-graph spine naturally lands a region-by-region
player roughly in-band anyway. This is deliberate (P2 — no trap walls, only a hard-but-not-
impossible curve) and matches §3's coach fare, which checks `shards`, never level.

## 7. Extra ring edges & the Sunken Depths terminus

`docs/WORLD_PLAN.md`'s cross-region edge table already carries two edges beyond the region-chain
spine — both ordinary bidirectional `edge` portals under §2's naming law, listed here only so map
authors don't mistake them for omissions:

- **Tidewatch → Ashfall ring closure**: `map_088` (north strand) ↔ `map_140` (east dunes) —
  closes the Harthmoor ring.
- **Gloomwood → Clockwork west gate**: `map_121` (web vaults) ↔ `map_188` — the Ruins' second
  gate, alongside the Ashfall char-ridge gate (`map_141` ↔ `map_177`).

**This doc adds no edges of its own**: `docs/WORLD_PLAN.md`'s edge table is the complete
authorized cross-region set. **Sunken Depths is a deliberate terminus** — entered only from
Tidewatch's sea cave (`map_094` → `map_152`), with no far exit. The trip home from its deep end
is the walk back up, or the Millbrook Return Scroll (`item_use_0013`) followed by a coach ride
back out (§3). Whether the terminus ever earns a late-arc shortcut stays open (Open Questions),
consistent with `docs/WORLD_PLAN.md` calling the spur "a deliberate terminus."

## Map-level edge table

Authored by the Phase D world-graph reconciler after all 200 maps exist.

## Open Questions

- `docs/VALIDATION.md` §5 states cross-region edges "must match `docs/WORLD_PLAN.md`'s edge table
  exactly." Under the v2.2 revision that wording is now literally correct — this doc authors no
  edges of its own (§7), so `docs/WORLD_PLAN.md`'s 11-row edge table is the complete authorized
  set. An earlier draft of this doc proposed extra §7 edges; `docs/VALIDATION.md`'s owner should
  simply confirm the wording stands unamended.
- Sunken Depths terminus shortcut (§7): does the deep end ever earn a one-way late-arc exit back
  toward the coast, or does Return Scroll + coach stay the intended loop? Default: no shortcut,
  matching `docs/WORLD_PLAN.md`'s "deliberate terminus."
- Ferry cadence (delegated here by `docs/WORLD_PLAN.md`'s open question): transit is instant at
  launch; scheduled sailings and an on-deck ambush event remain flavor-only ideas for a later
  pass — nothing in this doc's rules depends on the choice.
- Freely-authored extra spawn names on multi-entrance maps (§2) have no stricter naming
  convention yet; flag if Phase D authoring shows collisions or ambiguity in practice.
- Whether a map UI visually flags a `dead_end` portal before the player commits to it (§5) is
  `10_systems/HUD.md`'s design call, not decided here.
