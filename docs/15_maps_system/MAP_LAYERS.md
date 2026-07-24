# MAP_LAYERS.md — Depth Layers, Collision Layers & Tileset Binding

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
15_maps_system/MAP_TRAVERSAL.md, 15_maps_system/MAP_INTERACTABLES.md, 40_assets/ART_BIBLE.yaml,
30_engineering/ENGINEERING_STANDARDS.md

Owner doc, within `15_maps_system/`, for the visual **depth-layer stack** every map renders,
how the playfield depth splits into `TileMapLayer`s, and the per-biome tileset binding convention.
The 9-value collision layer enum and the depth-layer list themselves are locked by the Phase C
art/engineering bibles (`40_assets/ART_BIBLE.yaml`, `30_engineering/ENGINEERING_STANDARDS.md`);
this doc is the first place in the tree that needs the full mapping, so it tabulates that lock for
the map-system docs' shared use rather than restating it per-doc. Two different things are both
colloquially "layers" below — **depth layers** (visual, parallax) and **collision layers**
(physics bitmask); §3 disambiguates.

## 1. The 4 depth layers

Draw/parallax order, back to front:

| Depth layer | Parallax factor | Content | Collision |
|---|---|---|---|
| Sky / far-parallax | ~0.1× camera speed (near-static) | Sky, clouds, distant silhouettes | None |
| Mid-parallax | ~0.4–0.6× camera speed | Mid-ground scenery: distant hills, structures | None |
| Playfield | 1.0× (moves exactly with the world) | All gameplay — terrain, entities, interactables | Full (§2) |
| Foreground occluders | ~1.1–1.3× camera speed (slightly faster — standard near-camera parallax pop) | Decorative foreground dressing the player passes behind (foliage, pillars) | None, visual-only |

Only the **playfield** carries collision; the other three are pure parallax dressing.

## 2. Playfield → `TileMapLayer`s

| `TileMapLayer` | Purpose | Collision layer | Notes |
|---|---|---|---|
| `decor_back` | Playfield-depth decor drawn behind terrain | None | Same 1.0× parallax as the rest of the playfield — a draw-order choice, not a separate depth layer |
| `terrain` | Solid ground/walls | 1 `world` | Solid collision; organic ground is AB-001 terrain chunks snapped to arbitrary-angle footholds (`15_maps_system/MAP_TRAVERSAL.md` §1), not axis-aligned tiles — the 16 px grid still governs built structures |
| `one_way` | Drop-through platforms | 2 `one_way` | Mechanic owned by `15_maps_system/MAP_TRAVERSAL.md` §3 |
| `climbable` | Ropes/ladders | 8 `climbable` | Mechanic owned by `15_maps_system/MAP_TRAVERSAL.md` §4 |
| *(entities)* | Player, monsters, hitboxes, pickups, interactables | 3–7, 9 (below) | Not `TileMapLayer`s — see §3 |
| `decor_front` | Playfield-depth decor drawn in front of terrain/entities | None | Distinct from the *foreground occluders* depth layer (§1), which is a separate, further-forward parallax layer entirely |

Full playfield draw order: `decor_back` → `terrain`/`one_way`/`climbable` → entities (player,
monsters) → `decor_front`.

### 2.1 The canonical collision layer enum

| # | Layer | Kind |
|---|---|---|
| 1 | `world` | Tile (`terrain`) |
| 2 | `one_way` | Tile (`one_way`) |
| 3 | `player_body` | Entity |
| 4 | `monster_body` | Entity |
| 5 | `player_hit` | Entity (hitbox) |
| 6 | `monster_hit` | Entity (hitbox) |
| 7 | `pickups` | Entity (`loot_drop`, `15_maps_system/MAP_INTERACTABLES.md` §5) |
| 8 | `climbable` | Tile (`climbable`) |
| 9 | `interactable` | Entity (every other `15_maps_system/MAP_INTERACTABLES.md` type) |

## 3. Depth layers vs. collision layers — disambiguation

**Depth layers** (§1) are parallax/render-order bands a camera renders at different speeds; only
one of the four (playfield) has physics at all. **Collision layers** (§2.1) are the Godot physics
bitmask every solid body or trigger declares; layers 3–7 and 9 belong to *entity* nodes (player,
monsters, hitboxes, pickups, interactables), not to any `TileMapLayer` — they all conceptually live
at playfield depth, since gameplay entities only ever exist there. Only layers 1, 2, and 8 are
`TileMapLayer`s. Do not conflate the two vocabularies when authoring or reviewing a map file.

## 4. Per-biome tileset binding

Every map's `tileset_id` = `tileset_<biome_key>`, where `biome_key` is looked up from its region's
`docs/WORLD_PLAN.md` "Biome key (ramp)" column — **never** authored freely per map, and **not**
the same as the region slug for Millbrook and Sunken (below). A map's biome (and therefore
tileset) is fully determined by its region; there is no second map-level art token.

| Region (v3, `docs/WORLD_PLAN.md`) | Biome key | Tileset token |
|---|---|---|
| Emberfoot Isle | `emberfoot` | `tileset_emberfoot` |
| Millbrook & Rosen Harbor | `old_town` | `tileset_old_town` |
| Verdant Hollow | `verdant_hollow` | `tileset_verdant_hollow` |
| Tidewatch Coast | `tidewatch` | `tileset_tidewatch` |
| Gloomwood | `gloomwood` | `tileset_gloomwood` |
| Ashfall Barrens | `ashfall` | `tileset_ashfall` |
| Sunken Depths | `tidewatch_dark` | `tileset_tidewatch_dark` |
| Clockwork Ruins | `clockwork` | `tileset_clockwork` |
| Frostpeak Isle | `frostpeak` | `tileset_frostpeak` |
| Arcane Reach | `arcane_reach` | `tileset_arcane_reach` |
| Voidshore | `voidshore` | `tileset_voidshore` |

One tileset id per biome (11 total across the two authored arcs); only the `rift` biome key is
**reserved for a future arc** (`00_vision/SCOPE.md`, `docs/WORLD_PLAN.md`) and mints its tileset
token when that arc lands. Internal variants for a region's distinct sub-areas (e.g., a
cave versus an open field in the same region) are an atlas-organization concern inside that one
tileset, owned by `40_assets/ART_BIBLE.yaml`, not a second token here.

## 5. Lighting/ambience overlay policy

**Simple modulate tints only — no dynamic lighting**, per `40_assets/ART_BIBLE.yaml`'s anti-goals
(consistent with `00_vision/PILLARS.md`'s anti-pillar against photoreal/HD-2D rendering). A map may
declare one `ambient_tint: {color, strength}` applied via a single scene-wide modulate affecting
all four depth layers uniformly — no per-layer separate tints, no per-tile lightmaps, no dynamic
light/shadow nodes. Time-of-day and light-flicker effects are out of scope; a "flickering torch"
look, if wanted, is a simple sprite animation on a `decor_front`/`decor_back` asset, not a real
light source (stays inside the anti-goal).

## Open Questions

- Whether one tileset per biome is visually sufficient for a region's more different sub-areas
  (e.g., Sunken Depths' ruin-halls vs. open trenches) is `40_assets/ART_BIBLE.yaml`'s call, not
  resolved here.
- `ambient_tint` values themselves (which color/strength per map) are Phase D content, not
  specified in this systems doc.
- Parallax factor ranges (§1) are first-pass guidance; exact per-map values are an authoring
  choice within the stated bands, not individually validated here.
- Whether `docs/VALIDATION.md` should mechanically check that every map's `tileset_id` matches its
  region's biome key (§4) is a proposal for that doc's owner, not decided here.
