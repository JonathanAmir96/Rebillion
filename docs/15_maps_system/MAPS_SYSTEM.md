# MAPS_SYSTEM.md — Map Anatomy & the 6 Map Types

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, docs/VALIDATION.md, 10_systems/SPAWN.md, 10_systems/DEATH_PENALTY.md,
10_systems/AI_BEHAVIOR.md, 10_systems/HUD.md, 10_systems/social/PARTY.md,
10_systems/social/RAID.md, 15_maps_system/MAP_TRAVERSAL.md, 15_maps_system/MAP_INTERACTABLES.md,
15_maps_system/MAP_LAYERS.md, 15_maps_system/MAP_CONNECTIONS.md, 40_assets/ART_BIBLE.yaml

Owner doc for a map's anatomy — the fields every map file carries — and for the 6 `map_type`
values in `00_vision/GLOSSARY.md`. Movement physics is `15_maps_system/MAP_TRAVERSAL.md`;
interactable object types are `15_maps_system/MAP_INTERACTABLES.md`; the depth/collision layer
stack is `15_maps_system/MAP_LAYERS.md`; portal, spawn-naming, and coach/longship transport rules
between maps are `15_maps_system/MAP_CONNECTIONS.md`. This doc consumes those and never restates them. Exact YAML
field typing/validation is the future `20_schemas/map.schema.md` (Phase C); this doc defines the
conceptual anatomy that schema will formalize. 1 screen = the locked render base 640×360 px ≈
40×22.5 tiles at the 16 px tile grid (`40_assets/ART_BIBLE.yaml`, Phase C) — used throughout §2's
size guidance.

## 1. Map anatomy

Every map file carries:

| Field | Meaning | Owner |
|---|---|---|
| `id` | `map_NNN`, immutable | `docs/ID_REGISTRY.md` |
| `display_name` | Player-facing name | §3 |
| `map_type` | One of the 6 GLOSSARY map types | §2 |
| `region` | GLOSSARY region slug | `docs/WORLD_PLAN.md` |
| `level_band` | `{min, max}` | §4 |
| `bgm` | Single music tag | §5 |
| `ambience` | List of 0+ ambience tags | §5 |
| `bounds` | `{width, height}` in tiles | §2 per-type guidance |
| `spawn_points` | Named entry points (`main`, `from_<slug>`, `coach_stop`, …) | `MAP_CONNECTIONS.md` |
| `portals` | Edge/door/coach/longship exits | `MAP_INTERACTABLES.md` (params) + `MAP_CONNECTIONS.md` (rules) |
| `spawn_zones` | Monster population zones | `10_systems/SPAWN.md` |
| `trigger_zones` | Optional named quest-`reach` zones — `{zone_id, rect}` list, rect shape as `10_systems/SPAWN.md` §1's zone rect (owner ruling 2026-07-24) | consumer `10_systems/QUESTS.md` §3 |
| `interactables` | Non-portal, non-mob objects | `MAP_INTERACTABLES.md` |
| `layers` | Depth/TileMapLayer/tileset declarations | `MAP_LAYERS.md` |
| `dead_end` | Per-portal flag (not map-level) | `docs/VALIDATION.md` §5, `MAP_CONNECTIONS.md` |

`combat_free` is never an authored field — it is fully determined by `map_type` (§6), never a
per-map toggle; there is no way to author a combat-enabled town or a combat-free field.

## 2. The 6 map types

Size guidance is authoring guidance for Phase D, not a `docs/VALIDATION.md` hard check.

| `map_type` | Purpose | Width guidance | Height guidance | Combat |
|---|---|---|---|---|
| `field` | Open overworld exploration/hunting; the world-graph's connective tissue | 3–6 screens (~120–240 tiles) | 1–3 screens (~23–68 tiles) | Yes — `10_systems/SPAWN.md` zone-spawned |
| `dungeon` | Compact-vertical combat gauntlet; corridor/room loops denser than a field | 1–2 screens (~40–80 tiles) | 2–5 screens (~45–113 tiles) | Yes — denser budget, `10_systems/SPAWN.md` §2 |
| `town` | Social hub: vendors, trainers, coach station, hosts interiors | 2–4 screens (~80–160 tiles) | 1 screen (~23 tiles) | No — combat-free (§6) |
| `interior` | Single indoor room (inn/shop/hall/etc.) reached via a `door` portal from a town | ≤1 screen (~≤40 tiles) | ≤1 screen (~≤23 tiles) | No — combat-free (§6) |
| `arena` | Gated boss encounter | 1–2 screens (~40–80 tiles) | 1 screen (~23 tiles), up to 2 for a vertical fight | Yes — boss-scripted only, no zone spawner (§7) |
| `secret` | Bonus/reward pocket off the main path | ≤2 screens any dimension (~≤80 tiles) | ≤2 screens (~≤45 tiles) | Optional, sparse — `10_systems/SPAWN.md` §2 |

Counts per type are fixed by `docs/WORLD_PLAN.md`/`00_vision/SCOPE.md` (153 field · 95 dungeon ·
12 town · 30 interior · 11 arena · 23 secret = 324); this doc governs shape, not allocation.

## 3. Naming conventions (`display_name`)

Patterns below are authoring law for the *shape* of a name; the specific name for any given
`map_NNN` is Phase D content, not fixed here.

| `map_type` | Pattern | Rationale |
|---|---|---|
| `town` | `<Place name> <Settlement noun>` (Village/Township/Port/Sanctum) | Matches the 12 towns already named in `docs/WORLD_PLAN.md` |
| `field` | `<Region descriptor>` + a directional/progression qualifier, never a new place-name | A field chain must read as one place, not a new zone (P3 — world map drawable from memory) |
| `dungeon` | `<Place> <Tunnels\|Warrens\|Caves\|Vault(s)\|Spires\|…>` or `The <Adjective> <Noun>` | Evokes the crawl itself |
| `interior` | `<Function>` (Inn, Smithy, Market Hall, …), optionally `<Town> <Function>` when cross-region UI needs disambiguation | Matches the building's purpose |
| `arena` | A unique proper noun, frequently `The <Noun>` | Never reused — it *is* the encounter's identity (matches existing WORLD_PLAN arena names) |
| `secret` | Evocative, reward-hinting, no fixed template | Small bonus content, deliberately un-patterned |

## 4. `level_band` metadata

`level_band: {min, max}` is required on every map and must fall within (or equal) its region's
overall band in `docs/WORLD_PLAN.md`'s Region overview table. A region's maps commonly narrow the
band along a chain (e.g., an ascending field sequence starts near the region floor and ends near
its ceiling) rather than every map spanning the full region range. Millbrook's hub maps (region
band 8–14, `docs/WORLD_PLAN.md`) use a tight band near the region floor (8–9 in authored
content) rather than a wide range. `level_band`
feeds `10_systems/SPAWN.md`'s `mob_pool` tuning and a future recommended-level display
(`10_systems/HUD.md`, not specified here).

## 5. `bgm` / `ambience` tag policy — names only, assets later

Tags are freeform `snake_case` identifiers with no file paths, IDs, or asset references; the
concrete audio catalog is authored at Phase C/D by `40_assets/`. `bgm` is a single required tag
per map; `ambience` is an optional list of independent looped-texture tags layered under it.

| Field | Convention | Example shape |
|---|---|---|
| `bgm` (field/dungeon/secret) | `bgm_<biome_key>` — shared across a region's non-town, non-arena maps (biome identity, P3) | `bgm_emberfoot` |
| `bgm` (town) | `bgm_town_<region_slug>` | `bgm_town_millbrook` |
| `bgm` (interior) | Inherits its town's tag, or `bgm_interior_<mood>` for a hushed variant | `bgm_town_emberfoot` |
| `bgm` (arena) | `bgm_boss_<region_slug>` — bespoke boss theme | `bgm_boss_emberfoot` |
| `ambience` (any) | `amb_<texture>`, reused verbatim wherever the same texture applies | `amb_wind`, `amb_drip`, `amb_crowd` |

Biome keys are `docs/WORLD_PLAN.md`'s "Biome key (ramp)" column values (not the region slug — they
differ for Millbrook `old_town` and Sunken `tidewatch_dark`); see `MAP_LAYERS.md` §4 for the full
per-region table shared with tileset binding.

## 6. Combat-free confirmation — resolves an open item

**Decision: `town` and `interior` maps are combat-free** — no `spawn_zones`, no hostile
`monster_body` presence, no arena boss. This section owns the rule as **confirmed**: it settles
the interiors question `docs/WORLD_PLAN.md` formerly carried as an open item (since cleared
there) and answers `10_systems/SPAWN.md` §2's pending assumption: **yes**, for both map types.

## 7. Zone state on player death — resolves DEATH_PENALTY.md §5.1

**Decision: player death never resets zone/trash content.** Cleared `normal`/`elite` mobs stay
cleared; `10_systems/SPAWN.md`'s ordinary respawn timers (§3 there) keep governing repopulation
exactly as if no death occurred. Only a regional **arena** encounter resets on death/exit (§8) —
that is a property of the boss instance, not the surrounding zone. This resolves
`10_systems/DEATH_PENALTY.md` §5.1's flagged open item: field/dungeon zone state is untouched by a
player's own defeat (P2 — death stings but never deletes an evening; re-clearing a corridor you
already cleared would be exactly that kind of sting).

## 8. Arena rules

**Entry gate.** An arena's *only* ingress is one dedicated `door`-kind portal
(`15_maps_system/MAP_INTERACTABLES.md` §2) from its adjoining field/dungeon map — arenas never
have a second walkable entrance, satisfying `docs/VALIDATION.md` §5 reachability with exactly one
edge. Default gate = open (no level lock, no quest lock — P1, the player chooses engagements). A
per-arena quest-flag override is an optional Phase D authoring choice, not a rule here. The four
raid finale arenas (`map_042`/`map_200`/`map_244`/`map_324`) double as their raids' finale
instances: the raid entry — party 3–6, through the raid herald and the party-instanced stage chain
(`10_systems/social/RAID.md` §3–§4, `10_systems/SPAWN.md` §7) — is a separate path that never
touches the arena's own `door`, which stays the ungated open solo entry (`RAID.md` §7). Regional
arenas never require a party.

**`boss_bar` hookup.** An arena map declares `boss_mob_id: mob_NNN` identifying its boss. The
client shows `10_systems/HUD.md`'s `boss_bar` element bound to that mob's `life` the moment its AI
leaves `idle` (`10_systems/AI_BEHAVIOR.md` §1 state machine) and hides it on that mob's `die` state
or the player leaving the arena map; the bar's rendering/animation is entirely `HUD.md`'s.

**Lockout/respawn.** No lockout exists — regional arena bosses are freely repeatable with no
cooldown, key, or weekly limit (P2, ordinary farming). **Decision (this doc, per
`10_systems/SPAWN.md` §3's delegation):** a regional arena is a single **shared** map instance, not
per-party-instanced. It resets to phase 1 at full life once it has been empty of players for
`arena_reset_grace_s` = **30 s** — long enough that a same-party wipe-and-retry doesn't reset
mid-corpse-run, short enough that a later group never inherits a stale fight. This satisfies
`10_systems/SPAWN.md` §3's "no long timer" intent while keeping regional bosses simple, single-
instance content (P3, one connected world); raid instances — each raid's stage maps **and** its
finale arena copy (`10_systems/social/RAID.md` §4) — remain the sole party-instanced
exception (`10_systems/SPAWN.md` §7). `10_systems/DEATH_PENALTY.md` §5.2's "re-entering starts a
fresh attempt" is the solo-player special case of this same rule (an empty arena after one
player's death/respawn).

**Hazard/add-wave authoring.** `10_systems/AI_BEHAVIOR.md` §15 assigns arena-side scripting
(environmental hazards, add-wave placement, arena geometry changes, camera locks) to this doc. An
arena map file may declare a `hazards` list (placed instances of the touch-damage hazard types
owned by `15_maps_system/MAP_TRAVERSAL.md` §6) and phase-triggered `camera_locks`/
`geometry_changes` keyed to the boss's `phases[]` (`10_systems/AI_BEHAVIOR.md` §15); add-wave
*monsters* themselves spawn via the boss's own `summon_entity` ability, not a `spawn_zones` entry.

## Open Questions

- `arena_reset_grace_s` (30 s) is a first-pass default; may need per-boss tuning once Phase D
  content exists (e.g., a longer grace for encounters with a long walk-in).
- The render-base lock (screen ≈ 40×22.5 tiles, cited above) resolves `10_systems/SPAWN.md` §2's
  provisional "1 screen-width ≈ 20 tiles" assumption — the real figure is double. SPAWN.md's
  density numbers are authored per-screen (not per-tile) so they do not need renumbering, but its
  owner should update that citation once this doc lands.
- Per-arena quest-flag gates (§8) are left fully to Phase D map authoring; no catalog of which
  arenas use one is proposed here.
- `bgm`/`ambience` tag catalog governance (who prevents duplicate near-synonym tags, e.g.
  `amb_wind` vs. `amb_windy`) is unowned; flag for `40_assets/` at the C gate.
- Whether `interior` should ever allow a scripted, non-zone-spawned combat beat (a forced NPC
  fight) is out of scope here; default holds strictly combat-free per §6.
- **Resolved (2026-07-24, owner ruling): `reach`-step trigger zones declared.** §1 now carries
  the optional `trigger_zones` field (named `{zone_id, rect}` list, SPAWN-style rect — exactly
  what `10_systems/QUESTS.md` §3 assumed). Still deferred to Phase E: wiring validator
  resolution of quest `reach` targets against declared zones, and backfilling `trigger_zones`
  onto the minted maps whose quests reference named zones. Owner: this doc + validator/tools at
  Phase E.
- Secret-map size guidance (§2) has no WORLD_PLAN precedent to anchor against; first-pass only.
