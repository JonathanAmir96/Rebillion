# MAP_CONNECTIONS.md — Portal Rules, Spawn Naming & the World Graph

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
docs/ID_REGISTRY.md, 10_systems/DEATH_PENALTY.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md,
10_systems/HUD.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md

Owner doc for the **rules** portals, spawns, and paid transport follow between maps (v2.2 — the
free waygate network is retired; `coach`/ferry are the paid transports, `00_vision/GLOSSARY.md`
"Transport"). `docs/WORLD_PLAN.md`'s "Cross-region walk edges" table and "Harthmoor Coachworks"
paragraph are the sole authoritative source for *which* `map_NNN` pairs and stations connect —
they are cited, never reproduced, here. This doc formalizes the spawn-naming convention
`docs/WORLD_PLAN.md` previews, the coach/ferry ride rules, death-return routing, `dead_end`
marking, the region-progression gate policy, and the terminus shortcut decision. Portal object
params are `15_maps_system/MAP_INTERACTABLES.md` §2's; fares are `10_systems/ECONOMY.md` §4.3's;
this doc owns only the rules governing them.

## 1. Portal kind semantics between regions

| Kind | Typical use | Region span |
|---|---|---|
| `edge` | Most field/dungeon chain links; the cross-region walk edges (`docs/WORLD_PLAN.md`) | Usually intra-region; cross-region for the listed edges (+ §7's addition) |
| `door` | Town↔interior; the ferry's two docks; every arena's entry gate (`15_maps_system/MAPS_SYSTEM.md` §8) | Same-region, except the ferry crossing |
| `coach` | The Harthmoor Coachworks paid station-to-station network (`docs/WORLD_PLAN.md` v2.2) | Cross-region by design — that is its purpose |

## 2. Spawn-point naming law

Formalizes the convention `docs/WORLD_PLAN.md`'s "Spawn-point convention" paragraph previews.
Three tokens are **reserved**; a map may also author additional freely-named spawns (e.g. a
multi-entrance dungeon's `upper_west`) as long as they never collide with the reserved set.

| Spawn name | Required on | Meaning |
|---|---|---|
| `main` | Every map, exactly one | Default arrival point — direct teleport, quest-start, and the fallback target for any portal that doesn't name another spawn |
| `from_<origin_slug>` | Every map that is the destination of an `edge` portal crossing a region boundary | `<origin_slug>` is the origin **region**'s GLOSSARY slug (not a per-map slug — maps have none). An intra-region `edge` targets plain `main` unless the destination map has multiple distinct entrances needing disambiguation |
| `coach_stop` | Every map with a `coach_station` (`15_maps_system/MAP_INTERACTABLES.md` §9) | The fixed arrival point for all coach transits; exactly one per station map (`docs/WORLD_PLAN.md` "Spawn-point convention"; `from_ferry` covers the ferry docks the same way) |

Each of `docs/WORLD_PLAN.md`'s bidirectional cross-region edges produces exactly two
`from_<origin_slug>` spawns (one per endpoint, each named for the *other* side's region) — e.g.
the Emberfoot↔Verdant edge gives Verdant's endpoint a `from_emberfoot` spawn and Emberfoot's
endpoint a `from_verdant` spawn.

## 3. Coach & ferry ride rules (v2.2 — paid transport, no free warps)

**Every ride costs `shards`; the ring is walked for free.** (P3 survives as hunt-outward,
ride-home-for-a-fee; the retired waygate network's touch-to-unlock state is gone entirely.)

- No unlock state exists: every station is usable by every character from the first visit; there
  is nothing persistent to track except the one-time free-pilgrimage flag
  (`10_systems/ECONOMY.md` §4.3, `10_systems/PERSISTENCE.md`).
- Interacting with a `coach_station` (`15_maps_system/MAP_INTERACTABLES.md` §9) opens a
  destination menu (`10_systems/HUD.md`) listing the other four stations with their fares
  (`10_systems/ECONOMY.md` §4.3); paying triggers the co-located `portal(kind: coach)`
  (`15_maps_system/MAP_INTERACTABLES.md` §2) to the destination's `coach_stop` spawn. A character
  who cannot pay simply cannot ride — no debt, no partial trips.
- The **Harborwind Ferry** is the same pattern with `door` portals at the two docks
  (`map_001` ↔ `map_015` ↔ `map_017`) and a flat per-crossing fare; transit is instant at launch
  (`docs/WORLD_PLAN.md` Open Questions keeps scheduled sailings as future flavor).
- No cooldown on any paid ride; the **Millbrook Return Scroll** (`item_use_0013`) remains the
  only magic escape home.

## 4. Death-return routing

`10_systems/DEATH_PENALTY.md` §4 owns the bind mechanic and respawn destination (a bound town's
`main` spawn) — not restated here. This doc owns only *getting back out*: a respawned character
returns to the frontier as **ordinary travel** — walking the ring, or a paid coach/ferry ride
where its bind town has a station (`10_systems/DEATH_PENALTY.md` §4's five bind towns all have
one, except Emberfoot Village, whose ferry dock serves the same role) — never a special
death-only routing path or discount.

## 5. `dead_end` marking

Per `docs/VALIDATION.md` §5: any portal with **no matching reverse portal** on its destination map
must carry `dead_end: true`, authored on the portal that *leads into* the one-way transition (not
on the destination side). This is a validator-exemption flag only — it tells the world-graph
checker "do not require a reverse portal here" — not a required visible UI marker, though a map UI
may optionally surface it (`10_systems/HUD.md`'s call, not specified here). Ordinary `edge`/`door`/
`coach` portals, which always pair with a reverse, are never marked `dead_end`.

## 6. Region-progression gate policy: none

**Decision: no authored region-to-region progression gate exists anywhere in the portal/coach
system** — no level lock, quest-flag lock, or item-key lock on any region boundary (contrast with
an optional *per-arena* quest-flag gate, `15_maps_system/MAPS_SYSTEM.md` §8, a narrower, different
concern). A Lv 8 character can walk into the Lv 34+ Clockwork gates; nothing here stops them. The
only gate is the emergent difficulty curve: `10_systems/COMBAT_FORMULA.md` §9's level-difference
dampener makes a badly under-level fight genuinely hard well before it's mechanically blocked,
reinforced by `10_systems/LEVELING.md`'s exp curve (which consumes that same §9 table) cratering
reward for over-level kills, and `docs/WORLD_PLAN.md`'s world-graph spine naturally lands a
region-by-region player roughly in-band anyway. This is deliberate (P2 — no trap walls, only a
hard-but-not-impossible curve) and matches §3's coach rules, which also never check level (only
the fare).

## 7. Terminus decision — the Sunken Depths drop chute (v2)

`docs/WORLD_PLAN.md` v2 makes **Sunken Depths** the world's one deliberate terminus spur (the v1
Frostpeak/Clockwork chutes died with the v1 world graph — Clockwork is now the ring's center with
two walk gates). The same player-respect question recurs: should a player who has just cleared
The Warden's Vault walk the whole 25-map spur back, or spend a return scroll? **Decision: one
one-way drop chute**, from the arena's approach back to the spur's mouth:

| Terminus | New portal on | Kind | `target_map` | `target_spawn` (new) | `dead_end` |
|---|---|---|---|---|---|
| Sunken Depths (The Warden's Vault) | `map_176` | `edge` | `map_094` (Tidewatch's sea-cave descent) | `from_sunken` | `true` |

Both IDs already fall inside their region's reserved block (`docs/ID_REGISTRY.md`) — this
decision adds a portal between existing maps, it mints no new `map_NNN`.

The new spawn follows this doc's own §2 naming law (`from_<origin_region_slug>`); `map_094`'s
existing cross-region edge (to `map_152`) is a different portal, so nothing collides. **No
reverse portal is authored** back up to the arena — one-way is the point of a terminus shortcut.
`docs/WORLD_PLAN.md`'s edge table plus this §7 addition together form the complete authorized
cross-region walk-edge set (`docs/VALIDATION.md` §5). Phase D authors this portal directly from
this table.

## Map-level edge table

Authored by the Phase D world-graph reconciler after all 200 maps exist.

## Open Questions

- ~~`docs/VALIDATION.md` §5's "must match WORLD_PLAN's edge table exactly" vs this doc's §7
  additions~~ **Resolved at the v2 straggler wave:** `docs/VALIDATION.md` §5 now names the
  authorized set as WORLD_PLAN's table **plus this doc's §7 row** (amended there, its owner's
  channel).
- Freely-authored extra spawn names on multi-entrance maps (§2) have no stricter naming
  convention yet; flag if Phase D authoring shows collisions or ambiguity in practice.
- Whether a map UI visually flags a `dead_end` portal before the player commits to it (§5) is
  `10_systems/HUD.md`'s design call, not decided here.
- Whether the §7 drop-chute needs its own `docs/WORLD_PLAN.md` mention (beyond this doc) for
  discoverability is a light documentation question, not a design one; default is that this doc
  is the sole source for it.
- Coach fares (`10_systems/ECONOMY.md` §4.3) assume five stations and ring-path hop counting; if
  Phase D map authoring shifts a station's map, only WORLD_PLAN/ECONOMY rows move — this doc's
  rules are station-agnostic.
