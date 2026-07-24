# SPAWN.md — Spawn Zones, Density, and Timers

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md,
docs/VALIDATION.md, 10_systems/AI_BEHAVIOR.md, 10_systems/DEATH_PENALTY.md,
10_systems/SKILL_EFFECTS.md, 10_systems/social/PARTY.md, 10_systems/social/RAID.md,
10_systems/STATUS_EFFECTS.md,
15_maps_system/MAPS_SYSTEM.md, 20_schemas/monster.schema.md, 40_assets/ANIMATION_STATES.md,
40_assets/UI_ART_SPEC.md, 30_engineering/ENGINEERING_STANDARDS.md

Owner doc for how monsters populate a map: spawn zone declaration, density budgets, respawn
timing, concurrency caps, off-screen spawning, and the elite/boss entrance flourish. Which
monster does what once spawned is `10_systems/AI_BEHAVIOR.md`'s; this doc governs only when,
where, and how many.

## 1. Spawn zones (declared per map)

Each map that permits combat declares zero or more named **spawn zones** in its content file.
Exact field typing is owned by the map schema (`20_schemas/`, filename not yet fixed — see Open
Questions); this doc specifies the required contents:

| Field | Meaning |
|---|---|
| `zone_id` | Unique within the map, `snake_case` (e.g. `field_west_upper`) |
| `rect` | `x, y, width, height` in tiles, map-local, top-left origin |
| `mob_pool` | List of `{mob, count}` entries — which `mob_NNN` (`docs/ID_REGISTRY.md`) lives here and its **absolute target population** (owner ruling 2026-07-24: the `20_schemas/map.schema.md` `spawn_zones` count model is adopted; the earlier `{mob_id, weight}` relative-odds sketch is retired) |
| `target_count` | How many concurrent mobs this zone tries to maintain — **derived as the sum of `mob_pool[].count`** (`20_schemas/map.schema.md`), never authored independently |
| `max_concurrent` | Hard ceiling this zone's spawner will never exceed (§4); `target_count ≤ max_concurrent` |

Shape matches the authoritative `20_schemas/map.schema.md` `spawn_zones`:
```yaml
spawn_zones:
  - zone_id: field_west_upper
    rect: { x: 12, y: 4, width: 18, height: 6 }
    mob_pool:
      - { mob: mob_005, count: 3 }
      - { mob: mob_006, count: 1 }
    target_count: 4        # = sum of counts
    max_concurrent: 6
```

Boss-tier `mob_NNN` IDs (`20_schemas/monster.schema.md` entity tiers) are never placed in a
regular `spawn_zones` entry — bosses spawn via arena-entry (§3), not the zone spawner. A single
zone may mix `normal` and `elite` entries in one `mob_pool`.

## 2. Density budgets by map type (tile-anchored)

Budgeted per **20 tiles of walkable extent** — a fixed world-space unit, deliberately **not**
"per screen": maps vary widely in size (a compact 60-tile connector up to a 400-tile-wide
crossing, and tall vertical shafts), and camera zoom is a presentation choice
(`10_systems/CAMERA.md` §5) that must never change how densely a map is populated. **Walkable
extent** = the summed horizontal length, in tiles, of a map's foothold-bearing play space across
all its platform tiers (`15_maps_system/MAP_TRAVERSAL.md` footholds) — so a two-story map counts
both stories, and a tall map with short floors is budgeted by what a player can actually stand on,
not by its bounding rect. (Reference: the locked render base is 640×360 = 40×22.5 tiles,
`15_maps_system/MAP_TRAVERSAL.md`; at a 2× default zoom one visible screen ≈ 20 tiles — the unit
below matches that feel target but no longer depends on the zoom decision.)

A map's total zone population, summed across its `target_count`s, should land near
`(walkable_extent_tiles / 20) × per-unit budget`, rounded, with a floor of 1 per declared zone.

| Map type | Normals / 20 walkable tiles | Elite presence | Rationale |
|---|---|---|---|
| `field` | 3 | Rare — 1 elite per 60–80 walkable tiles, own small zone | Open exploration; the player chooses engagements (P1) |
| `dungeon` | 4 | Common — 1 elite zone per 40 walkable tiles | Corridor gauntlet; more committed combat |
| `secret` | 2 | Elevated `mob_pool` weight toward elite entries | Bonus content — sparser overall, but richer per encounter |
| `town` / `interior` | 0 | 0 | Combat-free — confirmed rule, owned by `15_maps_system/MAPS_SYSTEM.md` §6 |
| `arena` | n/a — exempt | n/a | Boss/wave-scripted, not zone-density-budgeted (`15_maps_system/MAPS_SYSTEM.md`) |

Because the budget is linear in walkable extent, a 3-screen map and a 10-screen map need no
separate size tiers — they simply carry proportionally more zones (or larger `rect`s with higher
`target_count`s). Very small combat maps (< 20 walkable tiles) take the floor: one zone,
`target_count` 1–2. §4's `max_concurrent` defaults are per **zone** and unchanged by map size —
a big map gets more zones, never one giant unbounded zone.

## 3. Respawn timers by tier

| Tier | Respawn timer | Mechanism |
|---|---|---|
| `normal` | 10 s baseline | Zone spawner (§1); per-mob override via `respawn_timer_s` |
| `elite` | 90 s baseline | Zone spawner; same override field |
| `boss` (regional arena) | No real-time timer — **arena-entry instanced** | Resets when the arena is unoccupied and re-triggered |
| `boss` (raid finale) | No real-time timer — **party-instanced** | Scoped per party; §7 |

**Boss respawn decision.** Both regional and raid finale bosses use arena-entry instancing rather
than a long real-world timer: the boss is always available and resets to full life the next time
a player/party properly enters and triggers the arena, consistent with
`10_systems/DEATH_PENALTY.md` §5.2/§5.3's "walk back in, fresh attempt" model. This was chosen
over a long fixed timer to avoid a dead, waiting boss (`00_vision/PILLARS.md` P2) and because a
solo/small-party regional boss needs no server clock to stay fair. The literal mechanism — a true
per-party instance vs. a shared arena that resets on empty — is `15_maps_system/MAPS_SYSTEM.md`'s
to define; this doc fixes only the intent (no long timer).

## 4. Max concurrent per zone

`max_concurrent` (§1) is the hard ceiling the spawner will never exceed even if `target_count`
slots are open and timers have elapsed — a safety/perf/readability backstop distinct from the
authored `target_count`. Defaults by map type (overridable per zone):

| Map type | Default `max_concurrent` |
|---|---|
| `field` | 6 |
| `dungeon` | 8 |
| `secret` | 4 |

`town`/`interior`/`arena` have no zone spawner (§2), so no `max_concurrent` applies to them.

## 5. Off-screen spawn rule

A mob never spawns where the player can see it happen. Concretely: a zone's respawn timer
elapsing does not spawn a mob if the chosen spawn point falls within the active camera viewport
plus a buffer margin (2 tiles beyond the visible edge, so pop-in isn't visible even at the edge).
If the point is on-screen when the timer completes, the spawn is **held** — not lost, not
re-timed from zero — and resolves on the next tick the point is found clear. The specific point
chosen within a zone's `rect` is picked at random among points currently off-screen and
traversable; if none currently qualify, the zone simply waits.

At map load, initial zone population spawns during the load/transition (before the camera settles
on the player), so this rule's practical effect is on respawns during play, not initial
population.

## 6. Elite spawn flourish

Normal-tier mobs spawn silently — no flourish; they simply appear (off-screen, per §5) and
walk/idle in. **Elite- and boss-tier spawns play the `spawn` animation state**
(`40_assets/ANIMATION_STATES.md`) as a deliberate "something dangerous just arrived" beat (P1
readability) — this is in addition to, not a replacement for, their required `telegraph` state on
their first attack (`docs/VALIDATION.md` §6). Following the same convention already established
for `phase_shift` (`10_systems/STATUS_EFFECTS.md` §1), an elite/boss is **invulnerable and
untargetable for the duration of its `spawn` state**, so its entrance can't be punished before the
player has even seen it. Any accompanying screen or audio cue is `40_assets/UI_ART_SPEC.md`'s to
define, not this doc's.

## 7. Raid spawn rules — finale arena, stage maps, bonus room

The four raid finale arenas (`map_042`/`map_200`/`map_244`/`map_324`, `10_systems/social/RAID.md`
§2, `docs/WORLD_PLAN.md`) do not use the zone spawner (§1–§4) at all — they are single-boss scripted
encounters, exempt exactly like regular arenas (§2). Entry is through the raid herald and stage
chain, not an open portal (`10_systems/social/RAID.md` §3–§4). Spawning here is **party-instanced**:
entering the finale arena allocates that encounter to the entering party alone (party
size/membership rules owned by `10_systems/social/PARTY.md`), and the finale boss
(`mob_027`/`mob_150`/`mob_178`/`mob_234`, `10_systems/social/RAID.md` §2) spawns fresh for that
instance at full life. Mid-fight adds/waves are not a `SPAWN.md` concept — they are the boss's own
`phases[].added_abilities` (`10_systems/AI_BEHAVIOR.md` §15) executed through the `summon_entity`
effect op (`10_systems/SKILL_EFFECTS.md`), scoped to the same party instance.

A raid's **stage maps** (`10_systems/social/RAID.md` §4) are ordinary combat dungeons and **do** run
the zone spawner (§1–§4) — the spawner's rules are unchanged; only the map copy is party-scoped to
the instance.

A raid's **bonus room** (`10_systems/social/RAID.md` §6.E, `map_325`–`map_328`) runs **no spawner
at all** — no zone, no mobs, no boss. Its only contents are `reactor` interactables
(`15_maps_system/MAP_INTERACTABLES.md` §4), whose one-shot behavior is that doc's `respawn_timer_s`
and not a `SPAWN.md` concept. It is named here only so the exemption is explicit alongside the
other two above.

A party's raid instance persists across individual member deaths/releases
(`10_systems/DEATH_PENALTY.md` §5.3) — it resets only on a full-party wipe or the party leaving
the instance, per the boss respawn decision in §3 and the re-entry model in
`10_systems/social/RAID.md` §5.

## Open Questions
- **Resolved (2026-07-24 contradiction fix):** §2 is re-anchored to a fixed world-space unit
  (per 20 tiles of walkable extent) instead of "per screen-width," removing the dependency on the
  undecided default camera zoom (`10_systems/CAMERA.md` §5 Open Question) and covering the full
  dynamic range of map sizes. If CAMERA later locks a zoom whose visible width differs sharply
  from ≈20 tiles, revisit the *feel* of the per-unit numbers — the unit itself no longer moves.
- How the validator computes `walkable_extent_tiles` from a map file (sum of foothold segment
  lengths at design granularity) is a `20_schemas/map.schema.md` / `tools/` implementation detail;
  flagged for the validator owner.
- `target_count`/`max_concurrent` defaults (§2, §4) are first-pass and tunable per region once
  Phase D populates real zones.
- **Resolved (2026-07-24, owner ruling): the absolute-count spawn model is adopted.** §1 now
  carries the `20_schemas/map.schema.md` `{mob, count}` shape (target-population maintenance;
  `target_count` = sum) — the model all minted Phase D maps already use. The old weighted-random
  sketch is retired.
- **Resolved:** the town/interior combat-free rule (§2) is confirmed and owned by
  `15_maps_system/MAPS_SYSTEM.md` §6; if that doc ever allows interior combat, §2's table needs
  a row.
- Whether the regional-boss "arena-entry instanced" mechanism (§3) is a true per-player instance
  or a shared arena that resets on empty is left to `15_maps_system/MAPS_SYSTEM.md`; both satisfy
  this doc's "no long timer" intent.
- Raid add-wave count/pacing is not budgeted here — it is authored per-boss in Phase D monster
  data, not a SPAWN.md rule.
