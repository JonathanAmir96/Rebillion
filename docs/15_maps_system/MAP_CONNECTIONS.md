# MAP_CONNECTIONS.md — Portal Rules, Spawn Naming & the World Graph

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
docs/ID_REGISTRY.md, 10_systems/DEATH_PENALTY.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md,
10_systems/HUD.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md

Owner doc for the **rules** portals, spawns, and waygates follow between maps.
`docs/WORLD_PLAN.md`'s "Cross-region walk edges" and "Waygate network" tables are the sole
authoritative source for *which* `map_NNN` pairs connect — they are cited, never reproduced, here.
This doc formalizes the spawn-naming convention `docs/WORLD_PLAN.md` previews, the waygate unlock
rule, death-return routing, `dead_end` marking, the region-progression gate policy, and resolves
`docs/WORLD_PLAN.md`'s terminus open question. Portal object params are
`15_maps_system/MAP_INTERACTABLES.md` §2's; this doc owns only the rules governing them.

## 1. Portal kind semantics between regions

| Kind | Typical use | Region span |
|---|---|---|
| `edge` | Most field/dungeon chain links; the 8 cross-region walk edges (`docs/WORLD_PLAN.md`) | Usually intra-region; cross-region for the 8 listed edges (+ §7's two additions) |
| `door` | Town↔interior; every arena's entry gate (`15_maps_system/MAPS_SYSTEM.md` §8) | Always same-region |
| `waygate` | The Millbrook-hub long-distance network (`docs/WORLD_PLAN.md` "Waygate network") | Cross-region by design — that is its purpose |

## 2. Spawn-point naming law

Formalizes the convention `docs/WORLD_PLAN.md`'s "Spawn-point convention" paragraph previews.
Three tokens are **reserved**; a map may also author additional freely-named spawns (e.g. a
multi-entrance dungeon's `upper_west`) as long as they never collide with the reserved set.

| Spawn name | Required on | Meaning |
|---|---|---|
| `main` | Every map, exactly one | Default arrival point — direct teleport, quest-start, and the fallback target for any portal that doesn't name another spawn |
| `from_<origin_slug>` | Every map that is the destination of an `edge` portal crossing a region boundary | `<origin_slug>` is the origin **region**'s GLOSSARY slug (not a per-map slug — maps have none). An intra-region `edge` targets plain `main` unless the destination map has multiple distinct entrances needing disambiguation |
| `waygate` | Every map with a `waygate_console` (`15_maps_system/MAP_INTERACTABLES.md` §9) | The fixed arrival point for all waygate-network transits; exactly one per waygate-bearing map |

Each of `docs/WORLD_PLAN.md`'s 8 bidirectional cross-region edges produces exactly two
`from_<origin_slug>` spawns (one per endpoint, each named for the *other* side's region) — e.g.
the Emberfoot↔Verdant edge gives Verdant's endpoint a `from_emberfoot` spawn and Emberfoot's
endpoint a `from_verdant` spawn.

## 3. Waygate unlock rule

**Touch the console once, then free travel forever — no cost, no cooldown** (P3: travel is a
low-friction loop, hunt outward, warp home).

- Unlock state is a per-character, server-authoritative, persistent set of unlocked waygate
  `map_id`s (`10_systems/PERSISTENCE.md`).
- **Millbrook Central's waygate is pre-unlocked for every character from creation** — it is already
  in a new character's unlocked set before the console is ever touched (touching it anyway is
  harmless/idempotent).
- Interacting with any `waygate_console` (`15_maps_system/MAP_INTERACTABLES.md` §9): if this
  waygate is not yet in the character's unlocked set, it is added (permanent, no re-lock); either
  way, a destination menu (`10_systems/HUD.md`) then opens listing every currently-unlocked
  waygate, and choosing one triggers the co-located `portal(kind: waygate)`
  (`15_maps_system/MAP_INTERACTABLES.md` §2) to that destination's `waygate` spawn.
- No `shards` cost, no cooldown, on any waygate transit.

## 4. Death-return routing

`10_systems/DEATH_PENALTY.md` §4 owns the bind mechanic and respawn destination (a bound town's
`main` spawn) — not restated here. This doc owns only *getting back out*: every valid bind town
(`docs/WORLD_PLAN.md`'s 4 towns) is also a waygate-network endpoint, so a respawned character
always has immediate access to its own town's `waygate_console`, already unlocked (it must have
rested there to be bound there), and can warp back to the frontier as ordinary travel (§3) — never
a special death-only routing path.

## 5. `dead_end` marking

Per `docs/VALIDATION.md` §5: any portal with **no matching reverse portal** on its destination map
must carry `dead_end: true`, authored on the portal that *leads into* the one-way transition (not
on the destination side). This is a validator-exemption flag only — it tells the world-graph
checker "do not require a reverse portal here" — not a required visible UI marker, though a map UI
may optionally surface it (`10_systems/HUD.md`'s call, not specified here). Ordinary `edge`/`door`/
`waygate` portals, which always pair with a reverse, are never marked `dead_end`.

## 6. Region-progression gate policy: none

**Decision: no authored region-to-region progression gate exists anywhere in the portal/waygate
system** — no level lock, quest-flag lock, or item-key lock on any region boundary (contrast with
an optional *per-arena* quest-flag gate, `15_maps_system/MAPS_SYSTEM.md` §8, a narrower, different
concern). A Lv 1 character can walk into a Lv 90 region; nothing here stops them. The only gate is
the emergent difficulty curve: `10_systems/COMBAT_FORMULA.md` §9's level-difference dampener makes
a badly under-level fight genuinely hard well before it's mechanically blocked, reinforced by
`10_systems/LEVELING.md`'s exp curve (which consumes that same §9 table) cratering reward for
over-level kills, and `docs/WORLD_PLAN.md`'s world-graph spine naturally lands a region-by-region
player roughly in-band anyway. This is deliberate (P2 — no trap walls, only a hard-but-not-
impossible curve) and matches §3's waygate unlock, which also never checks level.

## 7. Terminus decision — Frostpeak & Clockwork drop chutes

`docs/WORLD_PLAN.md` flags an open question, explicitly delegated to this doc: should Frostpeak
and Clockwork — both deliberate branch termini — get a late-game shortcut back toward Millbrook
besides the return scroll? **Decision: yes.** Both termini get a one-way drop chute from their
region's arena back down to the neighboring region's waygate-entrance field, so a player who has
just finished the terminus content isn't forced to walk the whole chain back or spend a return
scroll.

| Terminus | New portal on | Kind | `target_map` | `target_spawn` (new) | `dead_end` |
|---|---|---|---|---|---|
| Frostpeak (The Hornfall Summit) | `map_108` | `edge` | `map_073` (Ashfall's waygate-entrance field) | `from_frostpeak` | `true` |
| Clockwork (The Mainspring) | `map_144` | `edge` | `map_109` (Gloomwood's waygate-entrance field) | `from_clockwork` | `true` |

All four IDs already fall inside their region's reserved block (`docs/ID_REGISTRY.md`) — this
decision adds a portal between existing maps, it mints no new `map_NNN`.

Both new spawns follow this doc's own §2 naming law (`from_<origin_region_slug>`) and land on maps
that currently carry no `from_*` spawn (their existing cross-region edges use different map IDs
per `docs/WORLD_PLAN.md`'s edge table), so neither collides with an existing spawn. **No reverse
portal is authored** on either destination map back up to the arena — one-way is the point of a
terminus shortcut. `docs/WORLD_PLAN.md`'s edge table plus these two additions together form the
complete authorized cross-region walk-edge set (see Open Questions re: `docs/VALIDATION.md` §5's
wording). Phase D authors these two portals directly from this table.

## Map-level edge table

Authored by the Phase D world-graph reconciler after all 200 maps exist.

## Open Questions

- `docs/VALIDATION.md` §5 states cross-region edges "must match `docs/WORLD_PLAN.md`'s edge table
  exactly." `docs/WORLD_PLAN.md` itself delegates the §7 terminus decision to this doc, so that
  phrase should be read (or amended at a future pass) to include this doc's §7 additions as part of
  the authorized edge set. Flagged for `docs/VALIDATION.md`'s owner to confirm/reword — not
  resolved by editing that file here (out of scope for this doc).
- Whether waygate travel (§3) should ever carry a nominal `shards` sink is
  `10_systems/ECONOMY.md`'s call; default here is free, matching P3.
- Freely-authored extra spawn names on multi-entrance maps (§2) have no stricter naming
  convention yet; flag if Phase D authoring shows collisions or ambiguity in practice.
- Whether a map UI visually flags a `dead_end` portal before the player commits to it (§5) is
  `10_systems/HUD.md`'s design call, not decided here.
- The 1:1 mapping from each Rift raid arena to its staging-shard field
  (`10_systems/DEATH_PENALTY.md` §5.3's flagged open item) is still unresolved and is not settled
  by this doc either — it awaits Rift authoring.
- Whether the two new §7 drop-chutes need their own `docs/WORLD_PLAN.md` mention (beyond this
  doc) for discoverability is a light documentation question, not a design one; default is that
  this doc is the sole source for them.
