# map.schema.md — YAML content schema for one authored map

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md,
docs/VALIDATION.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_CONNECTIONS.md,
15_maps_system/MAP_INTERACTABLES.md, 15_maps_system/MAP_LAYERS.md, 15_maps_system/MAP_TRAVERSAL.md,
10_systems/SPAWN.md, 10_systems/AI_BEHAVIOR.md, 10_systems/QUESTS.md, 40_assets/ART_BIBLE.yaml,
20_schemas/npc.schema.md, 20_schemas/monster.schema.md

## Purpose

The content schema for one map in the 200-map world (`docs/WORLD_PLAN.md`) — formalizing the exact
YAML typing for the map anatomy `15_maps_system/MAPS_SYSTEM.md` §1 describes conceptually, plus the
portal/spawn shapes `15_maps_system/MAP_CONNECTIONS.md` and `15_maps_system/MAP_INTERACTABLES.md`
leave to "the future map schema." This doc never restates those docs' rules (size guidance, portal
semantics, coach-travel fares, spawn-density budgets, traversal physics) — it only fixes field names,
types, and the schema-local checks a validator runs on top of them. Read by: Phase D region-batch
authors writing `map_NNN.yaml` files; the Phase D world-graph reconciler (`docs/VALIDATION.md` §5);
`20_schemas/npc.schema.md` (bidirectional `map`/`npcs` check); and the Phase E coding pass loading
map data into Godot scenes (`60_agents/`, not yet authored).

## File conventions

One file per map at `50_content/maps/map_NNN.yaml` — `NNN` zero-padded to 3 digits, matching the
map's reserved slot in `docs/ID_REGISTRY.md`'s 8 region blocks (`map_001`–`map_200`). No batch
tables (contrast `10_systems/ITEMS.md` §12's category tables) — every map is distinct enough to
own its file. The file's `id` field and its filename's `NNN` must agree.

## Fields

All tile coordinates below are integers, map-local, top-left origin (consistent with
`10_systems/SPAWN.md` §1's `rect` convention). These are **static content-definition** files,
loaded identically by client and server; per `10_systems/PERSISTENCE.md` §1 every field carries
exactly one `authority` tag in its Notes — `server` (the value drives a server-adjudicated
mechanic; the client's copy is advisory), `client` (pure local presentation, never reconciled), or
`shared` (continuously predicted client-side and reconciled server-side, `10_systems/PERSISTENCE.md`
§4). Sub-table rows below inherit their parent field's tag and are not re-tagged individually.
Front-matter obeys `docs/VALIDATION.md` check 3.

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `map_NNN` | yes | `docs/ID_REGISTRY.md` | Immutable; `NNN` must fall inside this map's region block. `server` (identity). |
| `schema` | string | yes | this file | Literal `20_schemas/map.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list of string | yes | `docs/VALIDATION.md` §3 | Bare system-doc names (no path/extension) — baseline set in Validation rules. |
| `name` | string | yes | `15_maps_system/MAPS_SYSTEM.md` §1, §3 | Display name; §3 calls this concept `display_name` and owns its per-`map_type` naming pattern. `client`. |
| `region` | enum | yes | `docs/WORLD_PLAN.md` | GLOSSARY region slugs. `server`. |
| `map_type` | enum | yes | `15_maps_system/MAPS_SYSTEM.md` §2 | Fully determines combat eligibility (§6 there) — never a separate toggle. `server`. |
| `level_band` | `{min, max}` (int) | yes | `15_maps_system/MAPS_SYSTEM.md` §4; `docs/WORLD_PLAN.md` | Must fall within `region`'s overall band (Region overview table). `server` (feeds `10_systems/SPAWN.md` tuning). |
| `biome` | enum | yes | `40_assets/ART_BIBLE.yaml` `environment.biome_identity`; `15_maps_system/MAP_LAYERS.md` §4 | Fully determined by `region` — not freely authored. `client` (art/tileset selection only). |
| `tileset` | string `tileset_<biome_key>` | yes | `15_maps_system/MAP_LAYERS.md` §4 | Derived from `biome`. `client`. |
| `size_tiles` | `{w, h}` (int) | yes | `15_maps_system/MAPS_SYSTEM.md` §2 | §1 calls this `bounds`; per-`map_type` size guidance is authoring guidance, not a hard check. `server` (authoritative world bounds). |
| `water_physics` | bool | no, default `false` | `15_maps_system/MAP_TRAVERSAL.md` §7 | Intended for Sunken Depths (`sunken`) field/dungeon maps. `server` (jump/fall gravity modifier). |
| `bgm` | string, tag | yes | `15_maps_system/MAPS_SYSTEM.md` §5 | Freeform `snake_case`, no asset paths; shape pattern per `map_type`. `client`. |
| `ambience` | list of string, tag | no | `15_maps_system/MAPS_SYSTEM.md` §5 | 0+ independent looped-texture tags, same policy as `bgm`. `client`. |
| `layers_preset` | enum | yes | `15_maps_system/MAP_LAYERS.md` §1–§2 | One legal value exists today (Enums). `client`. |
| `spawn_points` | list of `{id, tile:[x,y]}`, ≥1 | yes | `15_maps_system/MAP_CONNECTIONS.md` §2 | Must include `main`; full naming law in Validation rules. `server` (world-graph fact; teleport-target correctness). |
| `portals` | list of object | no | `15_maps_system/MAP_CONNECTIONS.md`; `15_maps_system/MAP_INTERACTABLES.md` §2 | World-graph edges; empty only for a fully isolated map (none expected in the 200-map set). See §"portals" below. `server` (a `coach` portal resolves its destination dynamically from the coach menu and charges a `shards` fare — server-adjudicated economy, `15_maps_system/MAP_CONNECTIONS.md` §3). |
| `moving_platforms` | list of object | no | `15_maps_system/MAP_TRAVERSAL.md` §5 | See §"moving_platforms" below — that doc names this schema as pending owner of the param shape. `shared` (live position is client-predicted then server-reconciled, same shape as `10_systems/PERSISTENCE.md` §4's position/velocity case). |
| `spawn_zones` | list of object | no | `10_systems/SPAWN.md` | Must be empty/absent for `town`/`interior`/`arena`. See §"spawn_zones" below. `server` (zone population/timers). |
| `interactables` | list of object | no | `15_maps_system/MAP_INTERACTABLES.md` | Excludes `portal` (own field, above) and `loot_drop` (runtime-spawned only). See §"interactables" below. `server` (`sign`/`lore_marker` are presentation-only; the other 6 types drive a server-adjudicated mechanic — bind point, bank, coach ride, harvest/respawn, quest-flag gate). |
| `npcs` | list of string `npc_NNN` | no | `20_schemas/npc.schema.md` | Bidirectional with the NPC's own `map` field; region-local (Validation). `server` (world-population fact). |
| `platform_brief` | string, ≤6 lines | yes | `15_maps_system/MAP_TRAVERSAL.md` §1.1, §7; `00_vision/SCOPE.md` | The one descriptive/geometry-adjacent field (bands, verticality, gimmick) — not tile-exact; may assert traversal legality, engine-checked later. `client` (design-communication prose; see Open Questions on whether it even ships to the runtime client). |
| `arena_config` | object | required iff `map_type: arena`; must be absent otherwise | `15_maps_system/MAPS_SYSTEM.md` §8 | See §"arena_config" below. `server` (boss identity, gate rules). |
| `flavor` | string, ≤2 sentences | yes | `docs/VALIDATION.md` §7 | General player-facing blurb (proposed flavor-length lint). `client`. |

### `portals`

| Sub-field | Type | Required | Notes |
|---|---|---|---|
| `id` | string, `snake_case` | yes | Unique within the map (`15_maps_system/MAP_INTERACTABLES.md` §1 shared-field convention) |
| `kind` | enum: `edge`, `door`, `coach` | yes | Owner: `15_maps_system/MAP_INTERACTABLES.md` §2 / `15_maps_system/MAP_CONNECTIONS.md` §1 |
| `at` | `{tile:[x,y]}` **or** `{edge:<side>, tile_range:[min,max]?}` | yes | `tile` shape for `door`/`coach` (point placement); `edge` shape for `kind: edge` — `side` enum owned by this schema (Enums); `tile_range` optionally narrows the walk-off span along the edge, default full edge |
| `target_map` | string `map_NNN` | yes (`edge`/`door`); for `coach`, resolved dynamically at use-time from the coach menu (`15_maps_system/MAP_INTERACTABLES.md` §2) | Must resolve to an existing map file |
| `target_spawn` | string | yes | Must resolve to a `spawn_points[].id` on `target_map`; always authored explicitly, even when the value is `main` |
| `dead_end` | bool | no, default `false` | Authored only on the origin portal, never the destination (`15_maps_system/MAP_CONNECTIONS.md` §5). Ties to a world-graph check that runs globally, not per-file (`docs/VALIDATION.md` §5) |

A `coach`-kind portal resolves its destination dynamically from the coach menu at use-time and
charges a `shards` fare (`15_maps_system/MAP_CONNECTIONS.md` §3, `10_systems/ECONOMY.md`) — that
state is not stored in this file; this file only declares where the `coach_station`/portal object
sits. There is **no** per-character unlock set (the retired `waygate` mechanic is invalid,
`00_vision/GLOSSARY.md` Transport).

### `moving_platforms`

| Sub-field | Type | Required | Notes |
|---|---|---|---|
| `id` | string, `snake_case` | yes | Unique within the map |
| `path` | list of `[x, y]`, ≥2 points | yes | Map-local tile waypoints (`15_maps_system/MAP_TRAVERSAL.md` §5) |
| `speed` | float, tiles/s | yes | Constant between waypoints |
| `pause_s` | float | no | Dwell time at each waypoint |
| `loop_mode` | enum: `loop`, `ping_pong`, `once` | no, default `ping_pong` | |
| `one_way` | bool | no, default `false` | If true, platform also sits on collision layer 2 (`one_way`) rather than layer 1 (`world`) — `15_maps_system/MAP_LAYERS.md` §2.1 |

### `spawn_zones`

| Sub-field | Type | Required | Notes |
|---|---|---|---|
| `id` | string, `snake_case` | yes | Unique within the map; corresponds to `10_systems/SPAWN.md` §1's `zone_id` |
| `rect_tiles` | `{x, y, w, h}` (int) | yes | Corresponds to `10_systems/SPAWN.md` §1's `rect` |
| `mobs` | list of `{mob: mob_NNN, count: int ≥1}`, ≥1 entry | yes | `count` = this mob's target concurrent population in the zone; the zone's effective `target_count` (`10_systems/SPAWN.md` §1) = Σ `count`. This resolves `10_systems/SPAWN.md` §1's own illustrative `{mob_id, weight}` shape (explicitly flagged there as "not the authoritative schema") into an absolute-count authoring form — see Open Questions |
| `max_concurrent` | int | no | Hard ceiling, `10_systems/SPAWN.md` §1/§4; omit to use the `map_type` default from §4 |
| `respawn_override` | float, seconds | no | Overrides `10_systems/SPAWN.md` §3's tier baseline (10 s normal / 90 s elite) for every mob spawned from this zone |

A `boss`-tier `mob_NNN` may never appear in `mobs` (`10_systems/SPAWN.md` §1 — bosses spawn via
`arena_config`, not the zone spawner). A single zone may mix `normal` and `elite` entries.

### `interactables`

| Sub-field | Type | Required | Notes |
|---|---|---|---|
| `type` | enum, 8 values | yes | Owner: `15_maps_system/MAP_INTERACTABLES.md`; excludes `portal`/`loot_drop` (Enums) |
| `id` | string, `snake_case` | no | Unique within the map if present; some types are singleton-per-map by convention (e.g. `coach_station`) |
| `at_tile` | `[x, y]` (int) | yes | Anchor/placement point. `climbable`'s full vertical extent additionally uses `params.rect_tiles` below |
| `params` | object, shape by `type` | yes (`{}` legal only for types with no params) | See table below |

`params` shape by `type`:

| `type` | `params` fields | Owner |
|---|---|---|
| `climbable` | `rect_tiles:{x,y,w,h}` (full climb extent), `orientation: vertical`, `visual: rope\|ladder` | `15_maps_system/MAP_INTERACTABLES.md` §3 |
| `reactor` | `drop_table_ref` (id), `respawn_timer_s` (float, default 60), `harvest_prompt` (string) | §4 |
| `sign` | `text` (string, ≤2 sentences), `interact_prompt` (string) | §6 |
| `lore_marker` | `text` (string, ≤2 sentences), `interact_prompt` (string) | §6 |
| `inn_bed` | `{}` | §7 |
| `storage_chest` | `scope: character\|account` | §8 |
| `coach_station` | `{}` (must co-locate with exactly one `portals[]` entry of `kind: coach` and one `coach_stop` spawn; five coach towns only, `15_maps_system/MAP_CONNECTIONS.md` §3) | §9 |
| `quest_object` | `drop_table_ref` (id), `respawn_timer_s` (float, default 60), `required_quest_flag` (string — syntax unconfirmed, see Open Questions) | §10 |

### `arena_config`

| Sub-field | Type | Required | Notes |
|---|---|---|---|
| `boss_mob_id` | string `mob_NNN` | yes | Named field per `15_maps_system/MAPS_SYSTEM.md` §8 (`boss_mob_id`); must be `boss`-tier and match this region's `docs/WORLD_PLAN.md` boss seed |
| `gate` | `{type, required_flag?, party_min?}` | yes | `type: open\|quest_flag`, default `open` (`15_maps_system/MAPS_SYSTEM.md` §8); `required_flag` (quest-stage ref) required iff `type: quest_flag`; `party_min` (int) is meaningful only for the two raid **finale** arenas `map_042` / `map_200` when entered via their raid — its rule (party size 3–6, owned by `10_systems/social/RAID.md`). Every ordinary regional arena never requires a party, and both raid finales keep an open solo entry |
| `reset_grace_s` | float | no, default 30 | `15_maps_system/MAPS_SYSTEM.md` §8's `arena_reset_grace_s`; per-arena override hook |
| `hazards` | list of `{tier, at_tile\|rect_tiles}` | no | `tier` enum owned by `15_maps_system/MAP_TRAVERSAL.md` §6 (`minor`\|`standard`\|`severe`) |
| `camera_locks` | list of `{phase_id, params:{}}` | no | Phase-triggered per the boss's `phases[]` (`10_systems/AI_BEHAVIOR.md` §15); exact `params` shape is `10_systems/CAMERA.md`'s, not authored in this pass (Open Questions) |
| `geometry_changes` | list of `{phase_id, params:{}}` | no | Same phase-trigger pattern (`15_maps_system/MAPS_SYSTEM.md` §8); shape deferred |

Add-wave monsters are never map-authored here — they spawn via the boss's own `summon_entity`
ability (`15_maps_system/MAPS_SYSTEM.md` §8), authored on the boss's own monster file
(`20_schemas/monster.schema.md`).

## Enums

| Enum | Owner | Members (do not redefine — cite only) |
|---|---|---|
| `map_type` | `00_vision/GLOSSARY.md` / `15_maps_system/MAPS_SYSTEM.md` §2 | `field` · `dungeon` · `town` · `interior` · `arena` · `secret` |
| `region` | `docs/WORLD_PLAN.md` | The 8 active GLOSSARY region slugs (`frostpeak`/`arcane_reach`/`voidshore`/`rift` are reserved future biomes — invalid this run) |
| `biome` | `40_assets/ART_BIBLE.yaml` `environment.biome_identity` / `15_maps_system/MAP_LAYERS.md` §4 | The 8 biome-identity keys (one per active region; note Millbrook = `old_town`, Sunken = `tidewatch_dark`, not the region slug). The 4 reserved biomes are invalid here |
| `portals[].kind` | `15_maps_system/MAP_INTERACTABLES.md` §2 / `15_maps_system/MAP_CONNECTIONS.md` §1 | `edge` · `door` · `coach` (the retired `waygate` kind is invalid) |
| `interactables[].type` | `15_maps_system/MAP_INTERACTABLES.md` | `climbable` · `reactor` · `sign` · `lore_marker` · `inn_bed` · `storage_chest` · `coach_station` · `quest_object` (8 of its registry's types; `portal` and `loot_drop` are excluded here, see Fields) |
| `interactables[].params.scope` (`storage_chest`) | `15_maps_system/MAP_INTERACTABLES.md` §8 | `character` · `account` |
| `arena_config.hazards[].tier` | `15_maps_system/MAP_TRAVERSAL.md` §6 | `minor` · `standard` · `severe` |
| `portals[].at.edge` (screen side) | **this schema** (no other doc owns edge-side vocabulary) | `left` · `right` · `top` · `bottom` |
| `layers_preset` | **this schema**, reflecting `15_maps_system/MAP_LAYERS.md` §1–§2 | `standard` (the full 6-entry depth/`TileMapLayer` stack — only one value exists today, see Open Questions) |
| `arena_config.gate.type` | **this schema**, reflecting `15_maps_system/MAPS_SYSTEM.md` §8 | `open` · `quest_flag` |

## Example

Illustrative — real instances land in Phase D.

```yaml
id: map_005
schema: 20_schemas/map.schema.md
references: [MAPS_SYSTEM, MAP_CONNECTIONS, MAP_INTERACTABLES, MAP_LAYERS, MAP_TRAVERSAL, SPAWN, WORLD_PLAN]
name: Emberfoot Fields, Lower Reach
region: emberfoot
map_type: field
level_band: { min: 1, max: 3 }
biome: emberfoot
tileset: tileset_emberfoot
size_tiles: { w: 140, h: 28 }
water_physics: false
bgm: bgm_emberfoot
ambience: [amb_wind]
layers_preset: standard
spawn_points:
  - { id: main, tile: [14, 20] }
portals:
  - id: to_village
    kind: edge
    at: { edge: left }
    target_map: map_001
    target_spawn: main
    dead_end: false
  - id: to_fields_ii
    kind: edge
    at: { edge: right }
    target_map: map_006
    target_spawn: main
    dead_end: false
moving_platforms: []
spawn_zones:
  - id: field_lower_stretch
    rect_tiles: { x: 20, y: 18, w: 40, h: 8 }
    mobs:
      - { mob: mob_001, count: 3 }
      - { mob: mob_002, count: 1 }
    max_concurrent: 6
interactables:
  - type: sign
    id: sign_trailhead
    at_tile: [12, 19]
    params:
      text: "A weathered post points toward the deeper ash-warmed fields."
      interact_prompt: Read
npcs: []
platform_brief: |
  Two low terraces stepped by 2-tile rises, walkable in a single running jump.
  A one-way ledge mid-map offers a shortcut drop toward the lower spawn cluster.
  No verticality gimmick beyond the terraces — an easy, welcoming opener.
flavor: "The ash here is still warm underfoot, barely a season cooled since the kiln's last flare."
```

## Validation rules

Schema-specific checks beyond `docs/VALIDATION.md`'s globals (§1–§7 there):

1. **Portal targets exist.** Every `portals[].target_map` resolves to an existing `map_NNN` file;
   every `target_spawn` resolves to a `spawn_points[].id` on that `target_map`
   (`docs/VALIDATION.md` §2/§5).
2. **Spawn-point naming law.** Exactly one `main` (`15_maps_system/MAP_CONNECTIONS.md` §2). Every
   map that is the destination of a cross-region `edge` portal (`docs/WORLD_PLAN.md`'s edge table)
   carries the matching `from_<origin_slug>` (the origin's **region** slug). The two Harborwind Ferry
   endpoint maps (`map_001`, `map_017`) and the ferry interior (`map_015`) carry `from_ferry`. Every
   coach-town map with a `coach_station` interactable carries exactly one `coach_stop` spawn point.
3. **`dead_end` consistency.** A portal with no matching reverse portal on its destination map
   must set `dead_end: true`; ordinary paired `edge`/`door` portals never set it (a `coach` portal is a menu-driven service, not a walk edge, so it is not subject to `dead_end`, `15_maps_system/MAP_CONNECTIONS.md` §5). Checked
   globally at world-graph reconciliation, not per-file (`docs/VALIDATION.md` §5).
4. **Arena entrance rule.** An `arena` map's only entrance-capable portal is exactly one
   `door`-kind portal from its adjoining field/dungeon (`15_maps_system/MAPS_SYSTEM.md` §8). The v1
   Frostpeak/Clockwork egress "drop chute" is **retired** (`15_maps_system/MAP_CONNECTIONS.md` §7);
   no arena carries a second egress `edge` portal.
5. **Platform-gap promise.** `platform_brief` may assert gaps are crossable per
   `15_maps_system/MAP_TRAVERSAL.md` §1.1 (or §7's doubled figures under `water_physics: true`);
   this schema mechanically checks only the ≤6-line cap — exact tile-distance legality is an
   engine-pass concern (`00_vision/SCOPE.md`).
6. **Region-local mobs.** Every `spawn_zones[].mobs[].mob` and `arena_config.boss_mob_id` must fall
   inside this map's `region`'s mob block (`docs/ID_REGISTRY.md`). A `boss`-tier id may never
   appear in `spawn_zones` (`10_systems/SPAWN.md` §1).
7. **Arena boss match.** `arena_config.boss_mob_id` must be the boss `docs/WORLD_PLAN.md` names for
   this map's region. The two raid finale arenas reuse their region boss — `map_042` → The
   Cellar King (`mob_027`), `map_200` → The Custodian (`mob_150`) (`10_systems/social/RAID.md`).
8. **Combat-free map types.** `spawn_zones` must be empty/absent on `town` and `interior` maps
   (`15_maps_system/MAPS_SYSTEM.md` §6, `10_systems/SPAWN.md` §2). `spawn_zones` must also be
   empty/absent on `arena` maps (boss-scripted only, no zone spawner). `arena_config` must be
   absent on every non-`arena` map type.
9. **Derived-value consistency.** `biome` must equal `region`'s biome key
   (`15_maps_system/MAP_LAYERS.md` §4); `tileset` must equal `tileset_<biome>`; `level_band` must
   fall within `region`'s overall band (`docs/WORLD_PLAN.md`). This adopts
   `15_maps_system/MAP_LAYERS.md`'s own proposed tileset/biome check (flagged there as an open
   proposal) as a hard rule here.
10. **Interactable-type exclusions.** `interactables[].type` may not be `portal` (use `portals`) or
    `loot_drop` (runtime-spawned only, `15_maps_system/MAP_INTERACTABLES.md` §5).
11. **Bidirectional NPC listing.** Every id in `npcs` names a file whose own `map` field is this
    map's `id`, and vice versa (`20_schemas/npc.schema.md`).
12. **Front-matter `references` baseline.** Every map cites at least `MAPS_SYSTEM`,
    `MAP_CONNECTIONS`, `MAP_INTERACTABLES`, `MAP_LAYERS`, `MAP_TRAVERSAL`, and `WORLD_PLAN`; add
    `SPAWN` whenever `spawn_zones` is non-empty and `AI_BEHAVIOR` whenever `arena_config` declares
    `camera_locks`/`geometry_changes` keyed to boss phases.
13. **ID/file consistency.** `id`'s `NNN` matches the filename and falls inside this region's map
    block (`docs/ID_REGISTRY.md`).

## Template

```yaml
id: map_{NNN}
schema: 20_schemas/map.schema.md
references: [MAPS_SYSTEM, MAP_CONNECTIONS, MAP_INTERACTABLES, MAP_LAYERS, MAP_TRAVERSAL, WORLD_PLAN] # add SPAWN if spawn_zones non-empty; add AI_BEHAVIOR if arena_config uses phase-triggered camera_locks/geometry_changes
name: "{Display Name}"
region: { region_slug }
map_type: { field|dungeon|town|interior|arena|secret }
level_band: { min: { N }, max: { N } }
biome: { biome_key }
tileset: tileset_{biome_key}
size_tiles: { w: { N }, h: { N } }
# water_physics: true            # optional — omit unless this is a Sunken Depths field/dungeon map
bgm: bgm_{tag}
# ambience: [amb_{tag}]          # optional
layers_preset: standard
spawn_points:
  - { id: main, tile: [{x}, {y}] }
  # - { id: from_{origin_slug}, tile: [{x}, {y}] }   # required if this map is a cross-region edge destination
  # - { id: from_ferry, tile: [{x}, {y}] }           # required on the ferry endpoint maps (map_001/map_017) + ferry interior (map_015)
  # - { id: coach_stop, tile: [{x}, {y}] }           # required if this map has a coach_station (a coach town)
portals:
  - id: { portal_id }
    kind: { edge|door|coach }
    at: { tile: [{x}, {y}] }      # or: { edge: left|right|top|bottom }
    target_map: map_{NNN}
    target_spawn: { spawn_id }
    # dead_end: true              # optional — only if no reverse portal exists on target_map
# moving_platforms: []            # optional
# spawn_zones: []                 # optional — omit/empty for town, interior, and arena map_types
# interactables: []               # optional
# npcs: []                        # optional
platform_brief: |
  {≤6 lines: bands / verticality / gimmick}
# arena_config:                   # required only if map_type: arena
#   boss_mob_id: mob_{NNN}
#   gate: { type: open }
flavor: "{≤2 sentences}"
```

## Open Questions

- `15_maps_system/MAP_INTERACTABLES.md` frames itself as owning "the 10 interactable object
  types" while its per-section headers literally name 11 distinct nouns (`rope`/`ladder` as two,
  plus `sign`/`lore_marker` as two). This schema assumes `rope`/`ladder` collapse into one
  `climbable` type (distinguished only by the `visual` param), matching that doc's own count of
  10 — but that doc never states the unified token name; `climbable` is this schema's inference
  (borrowed from the `15_maps_system/MAP_LAYERS.md` §2.1 collision-layer name), not a confirmed
  one. Flag for `15_maps_system/MAP_INTERACTABLES.md`'s owner to confirm or correct.
- `spawn_zones[].mobs` uses an absolute `count` per mob (this schema's resolution) rather than
  `10_systems/SPAWN.md` §1's illustrative relative `weight` — that doc itself flags its shape as
  "illustrative only, not the authoritative schema," so this is this doc formalizing it, but the
  reinterpretation (target population per mob vs. weighted-random selection) changes the
  spawner's runtime algorithm and should be confirmed with `10_systems/SPAWN.md`'s owner.
- `respawn_override` is authored zone-wide (one value for every mob in the zone) rather than truly
  per-mob as `10_systems/SPAWN.md` §3's "per-mob override" wording suggests; flagged as a possible
  future refinement if a zone ever needs different overrides per mob within it.
- `interactables[].params.required_quest_flag` (`quest_object`) has no confirmed syntax even after
  `10_systems/QUESTS.md`'s authoring — that doc defines quest anatomy/steps but no concrete "flag"
  identifier grammar. This schema does not invent one; Phase D must coordinate a convention (e.g.
  `quest_NNN.step_<n>`) with `10_systems/QUESTS.md`'s owner before `quest_object` content lands.
- `arena_config.camera_locks`/`geometry_changes` `params` shape depends on `10_systems/CAMERA.md`,
  outside this task's required reading; left loosely typed (`{}`) pending that doc's review.
- Whether `hazards` should be authorable on non-arena map types is unresolved —
  `15_maps_system/MAP_TRAVERSAL.md` §6 describes hazards generically (not arena-scoped), but
  `15_maps_system/MAPS_SYSTEM.md` §8 only names a `hazards` list explicitly for arena maps. This
  schema currently exposes `hazards` only inside `arena_config`; flag if field/dungeon/secret maps
  need their own general-purpose hazard placements in a future revision.
- `layers_preset` has exactly one legal value (`standard`) because
  `15_maps_system/MAP_LAYERS.md` currently defines only one universal depth/`TileMapLayer` stack
  with no map-type variation. The field exists as a forward-compatible hook; flag whether a second
  preset is ever needed.
- Live zone-spawner state (current mob population, respawn timers in flight) has no explicit row
  in `10_systems/PERSISTENCE.md`'s save-model tables — flagged as a possible gap in that doc, not
  resolved here; this schema's `spawn_zones` field is static authoring config only, not runtime
  state.
- `platform_brief`'s ≤6-line cap and `flavor`'s ≤2-sentence cap have no mechanical lint yet,
  consistent with `docs/VALIDATION.md` §7's existing warn-only posture on flavor-length linting;
  this schema does not propose a stricter rule than that doc already carries.
- The front-matter `references` baseline (Validation rule 12) is this schema's own first-pass
  proposal, not yet exercised against a real Phase D batch; may need adjustment once region
  batches reveal which system docs a given map genuinely invokes.
