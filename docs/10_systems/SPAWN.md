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
| `mob_pool` | List of `{mob_id, weight}` pairs — which `mob_NNN` (`docs/ID_REGISTRY.md`) may spawn here, and their relative odds |
| `target_count` | How many concurrent mobs this zone tries to maintain |
| `max_concurrent` | Hard ceiling this zone's spawner will never exceed (§4); `target_count ≤ max_concurrent` |

Illustrative shape only — not the authoritative schema:
```yaml
spawn_zones:
  - zone_id: field_west_upper
    rect: { x: 12, y: 4, width: 18, height: 6 }
    mob_pool:
      - { mob_id: mob_005, weight: 3 }
      - { mob_id: mob_006, weight: 1 }
    target_count: 4
    max_concurrent: 6
```

Boss-tier `mob_NNN` IDs (`20_schemas/monster.schema.md` entity tiers) are never placed in a
regular `spawn_zones` entry — bosses spawn via arena-entry (§3), not the zone spawner. A single
zone may mix `normal` and `elite` entries in one `mob_pool`.

## 2. Density budgets by map type

Budgeted as **mobs per screen-width** rather than a fixed per-map total, so a longer map is denser
only in proportion to its length rather than needing a separate size tier. Working assumption:
**1 screen-width ≈ 20 tiles** at default camera zoom — provisional pending the real viewport spec
in `30_engineering/ENGINEERING_STANDARDS.md` (Open Questions). A map's total zone population,
summed across its `target_count`s, should land near `width_screens × per-screen budget` below.

| Map type | Normal / screen-width | Elite presence | Rationale |
|---|---|---|---|
| `field` | 3 | Rare — 1 elite per 3–4 screens, own small zone | Open exploration; the player chooses engagements (P1) |
| `dungeon` | 4 | Common — 1 elite zone per 2 screens | Corridor gauntlet; more committed combat |
| `secret` | 2 | Elevated `mob_pool` weight toward elite entries | Bonus content — sparser overall, but richer per encounter |
| `town` / `interior` | 0 | 0 | Combat-free (`docs/WORLD_PLAN.md` open item; assumed pending `15_maps_system/MAPS_SYSTEM.md` confirmation) |
| `arena` | n/a — exempt | n/a | Boss/wave-scripted, not zone-density-budgeted (`15_maps_system/MAPS_SYSTEM.md`) |

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

## 7. Raid finale arena spawn rules

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

A party's raid instance persists across individual member deaths/releases
(`10_systems/DEATH_PENALTY.md` §5.3) — it resets only on a full-party wipe or the party leaving
the instance, per the boss respawn decision in §3 and the re-entry model in
`10_systems/social/RAID.md` §5.

## Open Questions
- The `1 screen-width ≈ 20 tiles` assumption (§2) is provisional pending the real camera/viewport
  spec in `30_engineering/ENGINEERING_STANDARDS.md`; every density number in §2/§4 scales directly
  if that changes.
- The map schema's filename (§1) is assumed but not confirmed — likely
  `20_schemas/map.schema.md`, authored at Phase C.
- `target_count`/`max_concurrent` defaults (§2, §4) are first-pass and tunable per region once
  Phase D populates real zones.
- The town/interior combat-free assumption (§2) inherits `docs/WORLD_PLAN.md`'s open item; if
  `15_maps_system/MAPS_SYSTEM.md` later allows interior combat, this table needs a row.
- Whether the regional-boss "arena-entry instanced" mechanism (§3) is a true per-player instance
  or a shared arena that resets on empty is left to `15_maps_system/MAPS_SYSTEM.md`; both satisfy
  this doc's "no long timer" intent.
- Raid add-wave count/pacing is not budgeted here — it is authored per-boss in Phase D monster
  data, not a SPAWN.md rule.
