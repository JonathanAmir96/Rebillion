# MAP_INTERACTABLES.md — Interactable Object Registry

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/ID_REGISTRY.md, docs/VALIDATION.md,
docs/WORLD_PLAN.md, 10_systems/DEATH_PENALTY.md, 10_systems/HUD.md, 10_systems/PERSISTENCE.md,
10_systems/ECONOMY.md, 10_systems/SPAWN.md, 10_systems/STATS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/DROPS.md, 10_systems/QUESTS.md, 15_maps_system/MAPS_SYSTEM.md,
15_maps_system/MAP_TRAVERSAL.md, 15_maps_system/MAP_LAYERS.md, 15_maps_system/MAP_CONNECTIONS.md,
40_assets/ART_BIBLE.yaml, 20_schemas/map.schema.md

Owner doc for the 10 interactable object **types** a map YAML may place, and each type's param
shape. Portal *rules* (which kinds connect which maps, spawn-point targeting, coach rides) are
`15_maps_system/MAP_CONNECTIONS.md`'s; the climbing mechanic ropes/ladders invoke is
`15_maps_system/MAP_TRAVERSAL.md` §4; drop-table math and loot ownership windows are the future
`10_systems/DROPS.md`. This doc owns only the object shapes themselves.

## 1. Shared fields

Every interactable carries:

| Field | Meaning |
|---|---|
| `id` | Unique within the map, `snake_case` |
| `type` | One of the 10 types below |
| `rect` \| `position` | Tile-local placement (map schema, `20_schemas/map.schema.md`, Phase C, fixes the exact shape) |
| `interact_prompt` | UI text on approach (`10_systems/HUD.md`); omitted for auto-triggered types (`loot_drop`, an `edge` portal) |

Collision layer: all types below sit on layer **9 (`interactable`)** except `loot_drop`, which
sits on layer **7 (`pickups`)** — the canonical distinction is that layer 9 objects require a
deliberate "use" action (a prompt + input) while layer 7 objects auto-collect on touch
(`15_maps_system/MAP_LAYERS.md` §2.1 owns the enum itself).

## 2. `portal`

Kinds: `edge`, `door`, `coach` (v2.2 — the retired `waygate` kind is invalid in content,
`00_vision/GLOSSARY.md` "Transport"). Full connection semantics, spawn-point law, and the
coach/ferry ride rules are `15_maps_system/MAP_CONNECTIONS.md`'s; this doc owns only the object's
params.

| Param | Type | Notes |
|---|---|---|
| `kind` | enum | `edge` \| `door` \| `coach` |
| `target_map` | `map_NNN` | Fixed for `edge`/`door`; for `coach`, resolved at use-time from the destination the rider picks and pays for (§9) rather than a single fixed value |
| `target_spawn` | spawn name | Naming law in `15_maps_system/MAP_CONNECTIONS.md` §2 |
| `dead_end` | bool | `docs/VALIDATION.md` §5 — true if no reverse portal exists on the destination |

- `edge` — a screen-edge walk-off transition (most field/dungeon chain links and the cross-
  region walk edges, `docs/WORLD_PLAN.md`); visually seamless, no prompt.
- `door` — an explicit approach-and-interact threshold (town↔interior, the ferry's docks, every
  arena's entry gate, `15_maps_system/MAPS_SYSTEM.md` §8).
- `coach` — the paid station-to-station transit itself, always paired with a `coach_station` (§9)
  on the same map; visual identity for all three kinds is `40_assets/ART_BIBLE.yaml`'s.

## 3. `rope` / `ladder`

Mechanically identical placements of the single climbing state
(`15_maps_system/MAP_TRAVERSAL.md` §4) — the only difference is which visual asset renders on the
`climbable` (layer 8) shape.

| Param | Type | Notes |
|---|---|---|
| `rect` | tiles | Defines the climbable region's extent |
| `orientation` | enum | `vertical` (both types are vertical-only; no horizontal climbable shape) |
| `visual` | `rope` \| `ladder` | Selects the art asset only — no mechanical difference |

## 4. `reactor`

A breakable/harvest node (ore vein, crystal cluster, herb patch) distinct from a monster — it has
no `mob_NNN` ID and does not use `10_systems/SPAWN.md`'s zone spawner.

| Param | Type | Notes |
|---|---|---|
| `drop_table_ref` | id | References an entry under `50_content/drop_tables/` (`docs/VALIDATION.md` §2), same mechanism monster drops use |
| `respawn_timer_s` | float | Default **60 s**; independent per-instance timer, not `10_systems/SPAWN.md`'s mob timers |
| `harvest_prompt` | string | e.g. "Mine," "Gather" — flavor for the interact prompt |

On harvest, the reactor becomes depleted (non-interactable, visually changed) and spawns a
`loot_drop` (§5) at its position; it re-arms after `respawn_timer_s`.

## 5. `loot_drop`

The physical item entity spawned by a monster death or a `reactor` harvest. Layer **7
(`pickups`)** — auto-collected on `player_body` overlap, no interact prompt.

| Param | Type | Notes |
|---|---|---|
| `item_ref` | `item_equip_*` \| `item_use_*` \| `item_etc_*` | `docs/ID_REGISTRY.md` |
| `rarity` | GLOSSARY rarity token | Drives the tint ramp, `40_assets/ART_BIBLE.yaml` `rarity_code` |
| `owner_window` | — | Temporary kill/harvest-credit ownership before it becomes free-for-all; exact duration and party-sharing rule is the future `10_systems/DROPS.md`'s, not fixed here |

**Bounce-settle behavior** (this doc's own mechanic): on spawn, the drop pops with a small random
impulse — **0.5–1.5 tiles** horizontal (random direction) and a **0.5-tile** upward hop — falls
under `15_maps_system/MAP_TRAVERSAL.md` §1's standard gravity, lands on the nearest solid surface
below (layer 1/2 collision), and settles motionless, ready to collect.

## 6. `sign` / `lore_marker`

Pure flavor, no gameplay effect.

| Param | Type | Notes |
|---|---|---|
| `text` | string | ≤2 sentences (matches `docs/VALIDATION.md`'s proposed flavor-text lint, its Open Questions) |
| `interact_prompt` | string | e.g. "Read" |

## 7. `inn_bed`

Sets the character's bind point and rests.

| Param | Type | Notes |
|---|---|---|
| `id` | — | One per inn interior |

On interact: (a) sets the character's bind point to this map's town
(`10_systems/DEATH_PENALTY.md` §4 — rebind cost/cooldown is that doc's open question, not this
one's); (b) fully restores `life` and `essence` to max, instantly. (b) is this doc's own definition
of the bed's "rest" action — it does **not** resolve `10_systems/STATS.md`/
`10_systems/COMBAT_FORMULA.md`'s broader open question about ambient out-of-combat regeneration
elsewhere on the map, which remains separately unowned.

## 8. `storage_chest`

The account/character bank UI hook. Server-flagged: contents are persistent, account-critical
state, so all reads/writes are server-authoritative (`10_systems/PERSISTENCE.md`, P6) even though
the solo client may cache a local advisory copy — the client only opens the UI
(`10_systems/HUD.md`); it never resolves storage state itself.

| Param | Type | Notes |
|---|---|---|
| `scope` | enum | `character` \| `account` — which storage pool it opens; owner call is `10_systems/ECONOMY.md`/`10_systems/PERSISTENCE.md`, not fixed here |

## 9. `coach_station`

The physical object a player interacts with to ride the Harthmoor Coachworks (v2.2). Full ride
rules, fares, and network semantics are `15_maps_system/MAP_CONNECTIONS.md` §3 /
`10_systems/ECONOMY.md` §4.3; this doc defines only the object. A `coach_station` is always
co-located with exactly one `portal(kind: coach)` (§2) on the same map — interacting with the
station opens the destination/fare menu, and paying triggers that portal toward the chosen
station's `coach_stop` spawn.

| Param | Type | Notes |
|---|---|---|
| `id` | — | One per station map (the five towns, `docs/WORLD_PLAN.md`) |

## 10. `quest_object`

A quest-flag-gated variant of `reactor` (§4) — same harvest/respawn shape, plus a visibility/
interactability gate.

| Param | Type | Notes |
|---|---|---|
| `drop_table_ref` | id | As §4 |
| `respawn_timer_s` | float | As §4 |
| `required_quest_flag` | quest stage ref | Object is invisible/non-interactable unless the owning character's quest state satisfies this; exact quest-state vocabulary is the future `10_systems/QUESTS.md`'s, not fixed here |

## Open Questions

- Whether `reactor`/`quest_object` drop references need their own `docs/ID_REGISTRY.md` prefix
  (e.g. a `reactor_drop_NNN` block) or reuse the existing `drop_mob_NNN`/pool space is unresolved —
  flagged for `docs/ID_REGISTRY.md` at the C gate, not decided here.
- `owner_window` (§5) duration and party-sharing rules are entirely `10_systems/DROPS.md`'s once
  authored; this doc only asserts the concept exists.
- `required_quest_flag`'s exact syntax (§10) depends on `10_systems/QUESTS.md`, not yet authored.
- `storage_chest` `scope` (§8) — per-character or account-wide banks — is an open design call for
  `10_systems/ECONOMY.md`/`10_systems/PERSISTENCE.md`.
- `reactor`/`quest_object` default `respawn_timer_s` (60 s) is a first-pass number; may need per-
  region tuning once Phase D populates real material nodes.
- Exact tile-local placement typing (`rect` vs `position` per type) is deferred to
  `20_schemas/map.schema.md` (Phase C); this doc only names which shape each type conceptually
  needs.
