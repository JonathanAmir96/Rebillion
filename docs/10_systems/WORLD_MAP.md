# WORLD_MAP.md — World Map & Island Map view (the zoom-out spatial UI)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md,
docs/VALIDATION.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_CONNECTIONS.md,
20_schemas/map.schema.md, 10_systems/HUD.md, 10_systems/ECONOMY.md, 10_systems/MONETIZATION.md,
10_systems/PERSISTENCE.md, 10_systems/social/RAID.md, 40_assets/UI_ART_SPEC.md

Owner doc for the **zoom-out spatial UI**: the full-screen **World Map** (all five islands, which
island you are on) and the **Island Map** (every non-hidden map of your current island, where you
are on it). It sits above the always-on in-map **minimap**, which stays owned by
`10_systems/HUD.md` §5. This doc owns *which maps appear* and *how the player's position is shown*;
it never restates map anatomy (`15_maps_system/MAPS_SYSTEM.md`), the world graph
(`15_maps_system/MAP_CONNECTIONS.md`), paid travel (`10_systems/ECONOMY.md`), or art
(`40_assets/UI_ART_SPEC.md`) — it links them.

## 1. The three spatial tiers

One hotkey opens the overlay; it zooms between two levels (Island ⇄ World). The minimap is always
on underneath. All three read the same live fact — the player's current `map_id` — and derive the
rest.

| Tier | Scope | "You are here" marker | Owner |
|---|---|---|---|
| **Minimap** | The current map only | Live dot at the player's position | `10_systems/HUD.md` §5 (always-on `frame_system` chrome) |
| **Island Map** | Every *shown* map of the current island (§2), as a node-link graph | The current map's node is highlighted | **this doc** |
| **World Map** | All five islands (`docs/WORLD_PLAN.md`) | The current island is highlighted | **this doc** |

The overlay is a modal screen (like the inventory/character windows), not draggable chrome; it
pauses nothing server-side (`10_systems/PERSISTENCE.md`) and is pure presentation.

## 2. Which maps show — derived from `map_type`, with an optional override

**Default rule (no authoring):** a map appears on the Island Map iff its `map_type`
(`15_maps_system/MAPS_SYSTEM.md` §2) is in the **shown set**; otherwise it is hidden.

| `map_type` | On Island Map? | Why |
|---|---|---|
| `field` | **Shown** | The walkable overworld — the island's connective tissue |
| `town` | **Shown** | Social hubs; the anchor landmarks a player navigates by |
| `arena` | **Shown** (as a boss landmark node) | The region's boss room, solo-reachable by its one `door` (`15_maps_system/MAPS_SYSTEM.md` §8) |
| `dungeon` | Hidden | Compact combat pockets, not overworld geography — includes every raid-stage map |
| `interior` | Hidden | Indoor rooms reached from a town ("home in the city") — inn/shop/hall/ferry/longship deck |
| `secret` | Hidden | Bonus/reward pockets off the main path — includes the 5 raid bonus rooms (`map_325`–`map_329`) |

This rule *is* the player's stated exclusion list — no raid maps, no hidden maps, no dungeons, no
interiors — expressed entirely through the existing `map_type` token, so it needs zero new
per-map authoring. **Raid content is already fully hidden** by type: the raid-stage maps are
`dungeon` (including `raid_orrery`'s `map_277`–`map_279`, shared with open-world dungeons,
`10_systems/social/RAID.md` §4) and the five bonus rooms `map_325`–`map_329` are `secret`. The
five raid **finale arenas** (`map_042`/`map_200`/`map_244`/`map_284`/`map_324`) are `arena` maps
and so appear once, as their region's ordinary solo-walkable boss landmark; the party-instanced
raid run through them (`10_systems/social/RAID.md` §4) is a separate instance, **not** a distinct
map node, so it never adds a second pin. A player who is *inside* an instanced raid stage or finale
resolves "you are here" (§4) against the static public portal graph, never the private instance;
this path is dormant in the interim solo build (`10_systems/social/RAID.md` §8).

**Optional per-map override** (`20_schemas/map.schema.md`, field `world_map`): the rare exception
the default gets wrong.

- `world_map: hide` — drop a normally-shown map (e.g. a spoiler field, or a `field`/`town` the
  designer wants off the printed map).
- `world_map: show` — surface a normally-hidden map (e.g. a signpost `dungeon` mouth the world
  map should acknowledge).

Absent = the §2 default. The override is a curation escape hatch, expected on a handful of maps at
most; it is **not** a per-map coordinate system (see §5). Two guards bound it:

- `world_map: show` forcing a `secret`/`interior` visible is discouraged (spoiler/clutter); a
  validator may warn (Open Questions).
- `world_map: hide` is **rejected** by the validator on any map carrying a travel or instructor
  landmark — a `coach_station`, a longship pier, a `from_ferry` dock, the Lv 40+ Deepway
  `level_gate` door, or a job-instructor NPC — because hiding it would delete an affordance §6
  requires the map to surface (e.g. `map_125` Cindershelf is at once a coach hub, the Deepway
  gateway, and the Bulwark instructor town). `hide` is permitted only on ordinary field/town maps
  with no such landmark.

## 3. Islands are derived from `region`

A map carries `region`, not `island` (`20_schemas/map.schema.md`). The five-island grouping is
`docs/WORLD_PLAN.md`'s (mirrored in `00_vision/GLOSSARY.md` "Region slugs") — **owner: WORLD_PLAN**;
reproduced here only as the lookup this UI performs:

| Island | Regions (slugs) |
|---|---|
| Emberfoot Isle | `emberfoot` |
| Harthmoor Isle | `millbrook` · `verdant` · `tidewatch` · `gloomwood` · `ashfall` · `sunken` · `clockwork` |
| Frostpeak Isle | `frostpeak` |
| Arcane Reach | `arcane_reach` |
| Voidshore | `voidshore` |

The Island Map clusters its shown nodes by `region` within the island (Harthmoor's seven regions
read as one island but group visibly — the Victoria-ring layout of `docs/WORLD_PLAN.md`). Emberfoot
and each far isle are a single region, so island and region coincide there.

A **bridging map's island is its authored `region`'s island**, even while the map physically spans
two: the Harborwind Ferry (`map_015` → Emberfoot), the Deepway (`map_201`–`map_203` → Frostpeak),
and the longship decks (`map_207`/`map_247`/`map_287` → their moored far isle). The World Map snaps
to that island the instant the player enters, not to the origin; any distinct "in transit / at sea"
treatment is an authored art exception raised to `40_assets/UI_ART_SPEC.md`, never emergent.

**World-Map island adjacency** (which islands connect to which) is **not** derived from the
visibility graph — every cross-island connector is a hidden `interior`/`dungeon` (the ferry, the
Deepway, the longship decks), so the shown graph has zero cross-island links. Island adjacency is
sourced from `docs/WORLD_PLAN.md`'s transit edge tables (ferry, Deepway, and the arc-2 longship
network), independent of §2's map-visibility rule.

## 4. "You are here"

All position readouts derive from the player's current `map_id` — live session state, never a saved
or authored field (`10_systems/PERSISTENCE.md`):

- **World Map** highlights `island_of(region_of(map_id))` — including for bridging maps, whose
  island is their authored `region`'s (§3).
- **Island Map** highlights the current `map_id`'s node. If the current map is hidden (`world_map:
  hide` or a hidden `map_type` — e.g. the player is inside a dungeon, or on the ferry), resolve the
  marker by **breadth-first search over the full `portals[]` graph** (all portal kinds, following
  one-way `dead_end` portals forward), **restricted to maps whose `region` is on the same island**
  as the current map, and highlight the nearest reachable *shown* map; break ties by lowest
  `map_id`. If no shown map on the current island is reachable, fall back to the lowest shown
  `map_id` in the current `region`, then the island's lowest shown `map_id` — the marker is never
  blank, and the fallback is `map_id`-based because Gloomwood, Sunken, and Clockwork have no `town`
  map to anchor on. This BFS traverses **all** portal kinds to *locate* the player; the drawn
  *links* of §5 use only walk portals — the two are deliberately different.
- **Minimap** shows the in-map position (`10_systems/HUD.md` §5).

## 5. Node layout comes from the world graph, not authored coordinates

The Island Map is a **node-link graph**: one node per shown map. Links come from the
**hidden-contracted** portal graph, **not** the raw shown-only subgraph: two shown maps are linked
when a walk path (`edge`/`door` portals) connects them through **zero or more hidden maps**. This
contraction is **required, not cosmetic** — in the authored content 10 of the 11 boss `arena`s
reach the overworld only through a hidden approach `dungeon`, and the entire 12-map Sunken Depths
field spur (`map_152`–`map_163`) reaches the rest of Harthmoor only through the hidden sea-cave
`dungeon` chain; on the raw shown-only graph they would be unplaceable floating nodes and a whole
disconnected region. An `arena` node attaches to the shown map at the far end of its approach chain.
Adjacency is data we already have (`15_maps_system/MAP_CONNECTIONS.md`; the portal set in every
`map_NNN.yaml`); this doc adds no coordinate fields.

**Connectivity is a content invariant** (proposed `docs/VALIDATION.md` §5 addition): every shown map
must link, in the hidden-contracted graph, to at least one other shown map on its island — a shown
map that does not is a content error. (Edge case: `map_324`'s only walk link runs through the
`secret` `map_328`, so contraction crosses a `secret` there; if that ever matters, `map_324` takes
an explicit `world_map` handle.)

Region **cluster order and the ring/center/spur topology are not derivable from the portal graph** —
the graph yields adjacency only, not the Victoria-ring's angular order, Clockwork-as-center, or
Sunken-as-spur. The canonical order is `docs/WORLD_PLAN.md`'s ring sequence (Millbrook → Verdant →
Gloomwood → Ashfall → Tidewatch, Clockwork center, Sunken spur); §3's "cluster by region" consumes
that named order, while the hidden-contracted graph governs only intra-cluster node placement.

Concrete pixel placement — island backdrop, node icons, region biome halos, edge styling, the
"you are here" pin — is **art**, owned by `40_assets/UI_ART_SPEC.md` (the change-controlled
"world map/travel" screen family, UA-003; wireframe `docs/mockups/world_travel_mockup.html`) and
finalized in the coding pass. Auto-layout from the portal graph vs. hand-placed coordinates is an
engine/art choice deferred there (Open Questions). The design law this doc fixes is only P3 — *the
world map must be drawable from memory* (`00_vision/PILLARS.md`), which the naming conventions
(`15_maps_system/MAPS_SYSTEM.md` §3) already serve.

## 6. View-only — the map never teleports

The World/Island Map is **informational**. Selecting a node does **not** travel there — Rebillion
has **no free warps** (`docs/WORLD_PLAN.md`; "Backtracking law"), and travel is never sold as power
(`10_systems/MONETIZATION.md`). All travel stays the authored paid/gated flows: the Harthmoor
Coachworks (`15_maps_system/MAP_CONNECTIONS.md` §3; fares `10_systems/ECONOMY.md` §7.1), the
longship line (`15_maps_system/MAP_CONNECTIONS.md` §8; fares `10_systems/ECONOMY.md` §7.2), the
Harborwind Ferry (fare `10_systems/ECONOMY.md` §7.1), and the free Lv 40+ Deepway
(`15_maps_system/MAP_CONNECTIONS.md` §9.1). The map may *surface* those affordances (e.g. mark coach
stations and piers, as `docs/mockups/world_travel_mockup.html` already does) and hand off to their
existing UI, but it originates no route of its own.

## 7. No fog-of-war — the whole island is shown at once

Every map in the shown set (§2) for the current island is drawn immediately, whether or not the
player has visited it — matching the request to "see all the maps in the island." There is no
visited-unlock/discovery gate and therefore **no new persistence** (`10_systems/PERSISTENCE.md`):
the view is fully derived from static map data plus the live `map_id`. The Island Map always shows
the **current island only** — a player cannot open the Island Map of an island they are not on — so
far-isle spoilers are bounded to the World Map's five island silhouettes. Whether *not-yet-reached
islands* on the World Map (the Arc-2 far isles before Lv 40) are shown dimmed or in full is an art
detail (Open Questions); the default is to show all five, since the world never closes.

Because visibility is *derived* from the mutable `map_type` (`20_schemas/map.schema.md`), retyping a
map silently reshapes the screen; the §5 hidden-contracted connectivity invariant re-runs on every
content batch and fails if any region or `arena` becomes unreachable in the shown graph, catching
such a change as a content error rather than a silent hole.

## Open Questions

- **Is the World Map tier the same screen as the existing "world map/travel" mock-up?** This doc
  assumes one overlay with an Island⇄World zoom, merging the travel-network view
  (`docs/mockups/world_travel_mockup.html`, UA-003) with the you-are-here island view. Confirm with
  `40_assets/UI_ART_SPEC.md`'s owner; that mock-up may also be independently refreshed (owner note,
  2026-07-24) — this doc references its *role*, not its current pixels.
- **`island` as a first-class token/field?** Islands are derived from `region` (§3). If content or
  the runtime ever needs island as an authored value, it belongs in `00_vision/GLOSSARY.md` /
  `docs/WORLD_PLAN.md`, not invented here (Law 1/2). Flagged, not resolved. Related: a
  `docs/VALIDATION.md` check should assert §3's region→island table covers every
  `00_vision/GLOSSARY.md` region slug, so no region can leave `island_of()` undefined.
- **Node layout algorithm** — auto-layout from the `portals[]` graph vs. hand-authored coordinates
  in the art/engine pass (§5). Deferred to the coding pass; if coordinates are chosen, they are art
  data (`40_assets/UI_ART_SPEC.md`), not a `map.schema.md` field.
- **`arena` as its own node** — *resolved:* each of the eleven arenas shows as a boss-landmark node,
  attached to the overworld via the §5 hidden-contracted chain (this is what makes the 10 dungeon-
  gated arenas placeable at all). Revisit only if the landmarks read as clutter.
- **Override reach** — `world_map: show` surfacing a `secret`/`interior` is permitted but discouraged
  (spoiler/clutter); a validator could warn. The opposite, `world_map: hide` on a travel/instructor
  hub, is a **hard validator reject**, not a warning (§2).
- **Art contract** — island backdrop, region halos, node/edge/"you are here" styling, and the
  not-yet-reached-island treatment (§5–§7) are `40_assets/UI_ART_SPEC.md`'s (change-controlled);
  raised here for that doc's owner, authored nowhere in this pass.
- **Hotkey binding** for the overlay is a controls concern (`10_systems/DISPLAY.md` / input map),
  not fixed here.
