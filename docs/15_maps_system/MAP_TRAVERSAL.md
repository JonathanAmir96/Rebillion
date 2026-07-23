# MAP_TRAVERSAL.md — Player Movement Contract

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md,
10_systems/COMBAT_FORMULA.md, 10_systems/STATUS_EFFECTS.md, 10_systems/AI_BEHAVIOR.md,
10_systems/CONTROLS.md, 10_systems/SKILL_EFFECTS.md, docs/WORLD_PLAN.md,
15_maps_system/MAP_LAYERS.md, 15_maps_system/MAP_INTERACTABLES.md, 40_assets/ART_BIBLE.yaml,
40_assets/ANIMATION_STATES.md, 30_engineering/ENGINEERING_STANDARDS.md

Owner doc for the platforming movement contract: run speed, jump physics, one-way platforms,
climbing, moving platforms, environmental hazards, fall damage, and the Sunken Depths water-physics
flag — all expressed in **tiles**, so Phase D map authors and a future validator can check gap
distances by hand. Combat cadence (attack speed, `haste` conversion) is
`10_systems/COMBAT_FORMULA.md`/`10_systems/STATS.md`'s; this doc owns only traversal.

**Locked constants this doc builds on** (from the Phase C art/engineering bibles —
`40_assets/ART_BIBLE.yaml`, `30_engineering/ENGINEERING_STANDARDS.md`): tile grid **16 px**;
render base **640×360 px ≈ 40×22.5 tiles per screen**; entity pivot **feet-center** (every vertical
distance below — apex height, gap rise — is measured floor-to-floor from this pivot, not
bounding-box edges).

## 1. Run speed & jump physics

| Constant | Value | Notes |
|---|---|---|
| `run_speed` | **8 tiles/s** (128 px/s) | This doc's authoritative figure for platforming/level design (see Open Questions re: `10_systems/COMBAT_FORMULA.md` §10 reconciliation) |
| `jump_apex_height` | **3.5 tiles** | Max vertical rise reachable from a standing jump |
| `jump_distance` | **5 tiles** | Horizontal distance of a full running jump (takeoff at `run_speed`) at equal launch/landing height |

These three figures fix the jump arc's kinematics (standard projectile motion, pivot-to-pivot):

| Derived (reference for the coding pass) | Value |
|---|---|
| Total air time (`T`) | 0.625 s |
| Time to apex | 0.3125 s |
| Gravity (`g`) | ≈71.7 tiles/s² (≈1147 px/s²) |
| Initial jump velocity (`v0`) | ≈22.4 tiles/s (≈358 px/s) |

Final in-engine tuning (Godot gravity/jump-velocity project values) may deviate slightly from the
derived reference as long as it preserves the three headline figures above; those are the design
contract, the derived pair is a starting point, not a separate lock.

### 1.1 Validation rule (platform gaps)

A gap between two platforms intended to be crossable by a standard jump — no rope, ladder, or
moving platform — must satisfy, independently:

- **Horizontal** (equal or descending height): edge-to-edge distance ≤ **5 tiles**.
- **Vertical rise** (destination higher than origin): ≤ **3.5 tiles**, regardless of horizontal
  distance.

The two caps are each a single-axis maximum, **not additive corners** — a gap that is both
near-max horizontal *and* near-max vertical is not guaranteed jumpable; author conservatively
(recommend ≤70% of either cap when the other is also non-trivial) or bridge it with a rope,
ladder, or moving platform (§4–§5) instead. A descending gap has no horizontal ceiling beyond the
plain 5-tile cap — gravity always resolves a fall; a one-way-platform drop-through (§3) is the
deliberate tool for a *controlled* descent, not a distance to validate. Pixel-perfect jump-arc
validation is an engineering-pass tool (`30_engineering/ENGINEERING_STANDARDS.md`, Phase E); this
rule is the hand-checkable authoring budget for Phase D.

## 2. No fall damage

**Falling from any height never damages the player**, regardless of distance — there is no
fall-damage mechanic anywhere in this design. Contrast with hazards (§6), which damage on touch
regardless of how far the player fell to reach them.

## 3. One-way platforms

Collision layer **2 (`one_way`)** per the canonical enum (`15_maps_system/MAP_LAYERS.md` §2.1):
solid when approached/stood on from above, fully passable from below and the sides (a jump can
pass straight up through one).

**Drop-through.** While standing on a `one_way` platform, the drop-through input (exact chord owned
by `10_systems/CONTROLS.md`, not fixed here) suspends the player's `player_body` (layer 3)
collision against layer 2 for a short window (**0.3 s**), then restores it once clear — long enough
to fall clear of the platform, short enough that it cannot be held indefinitely as a stealth mode.
Monster drop-through is a per-AI-profile choice, not a blanket rule (`10_systems/AI_BEHAVIOR.md`
§2's default edge-avoidance, with `timid_grazer` explicitly drop-through-while-fleeing) — this doc
owns only the mechanic monsters invoke, not which profiles use it.

## 4. Ropes and ladders (climbing)

Collision layer **8 (`climbable`)** (`15_maps_system/MAP_LAYERS.md` §2.1). **Climbing is a single,
first-class state implemented once** — ropes and ladders are the *same* mechanic with a different
visual dressing (`15_maps_system/MAP_INTERACTABLES.md` §3); there is no separate rope-swing
physics or ladder-specific code path.

| Rule | Value |
|---|---|
| Mount | Player's `player_body` overlaps a `climbable` shape **and** the climb input is held (`10_systems/CONTROLS.md`) → enters `climb` (`40_assets/ANIMATION_STATES.md`); horizontal run velocity zeroes, gravity suspends |
| `climb_speed` | **4 tiles/s** (half `run_speed`) — vertical-only movement while climbing |
| Auto-dismount | Reaching either end of the climbable shape's vertical extent returns to `idle`/`fall` |
| Manual dismount | Jump input while climbing performs a fixed **1.5-tile** horizontal hop off in the facing direction, then resumes normal jump/fall physics |
| Side dismount | Moving horizontally off the climbable shape onto adjacent solid ground steps off normally (standard ladder-exit convention) |
| Attack while climbing | **No.** Basic attack and the skill bar are disabled in `climb`; the player must dismount to fight |

## 5. Moving platforms

Allowed. A moving platform is authored as ordinary terrain (layer **1 `world`**, or layer **2
`one_way`** if it should also be droppable-through) plus a motion behavior layered on top — motion
is orthogonal to the layer choice, not a new collision layer.

| Param | Type | Notes |
|---|---|---|
| `path` | list of `{x, y}` tile-local waypoints | Map-local coordinates |
| `speed` | tiles/s | Constant between waypoints |
| `pause_s` | float, optional | Dwell time at each waypoint before continuing |
| `loop_mode` | `loop` \| `ping_pong` \| `once` | Default `ping_pong` |

A player standing on a moving platform is carried with it (parented motion); the §1.1 validation
rule does not apply to a moving-platform-bridged gap — the platform itself is the crossing.

## 6. Hazards (spikes, lava)

A hazard deals **touch damage as a fixed percentage of the touching player's max `life`** — not
mitigated by `armor`/`warding`, not element-multiplied (deliberately simple and legible, P1: a
player who dies to a hazard should always know why, regardless of gear). This is a different
damage instance shape than the `10_systems/COMBAT_FORMULA.md` §2 pipeline; the two hooks it *does*
reuse are the standard **0.40 s player i-frame window** and the **hitstun/knockback** convention
(`10_systems/COMBAT_FORMULA.md` §11–§12):

| Hazard tier | Touch damage (% max `life`) | Example |
|---|---|---|
| Minor | 5% | Shallow spikes, thorns |
| Standard | 10% | Pit spikes, hot coals |
| Severe | 20% | Lava, deep chasms with active hazards |

Reapplication is gated by the player's i-frames — a hazard cannot deal damage faster than roughly
**once per 0.40 s** of continuous contact (`10_systems/COMBAT_FORMULA.md` §12), the same throttle
that already prevents monster-touch stun-lock. A hazard hit is never classed **heavy** — it applies
no knockback and no extra hitstun beyond the i-frame window; it is a punishing floor/wall, not an
attack that could fling the player into more danger.

## 7. Swim: `water_physics` map flag

Sunken Depths (`docs/WORLD_PLAN.md` R7) uses a **modified-jump flag**, not a separate stat or a new
movement mode: a boolean `water_physics: true` authored per map (Sunken Depths' field/dungeon
maps; false/omitted everywhere else). It applies one scalar to the §1 jump/fall gravity and
nothing else:

| Field | Value | Effect |
|---|---|---|
| `water_gravity_mult` | **0.5** (half gravity) | Doubles time-to-apex, total air time, apex height, and jump distance (at the unchanged 8 tiles/s `run_speed`) |

| | Normal | `water_physics: true` |
|---|---|---|
| Apex height | 3.5 tiles | **7.0 tiles** |
| Jump distance (at `run_speed`) | 5 tiles | **10 tiles** |
| Total air time | 0.625 s | 1.25 s |

Map authors validating gaps on a `water_physics` map use these doubled figures in place of §1.1's
caps. The flag touches **only** jump/fall gravity — one-way platforms (§3), climbing (§4), moving
platforms (§5), and hazards (§6) behave identically regardless of the flag. No new `swim`
animation state exists (the 12-state `00_vision/GLOSSARY.md` set is fixed and final); underwater
movement plays ordinary `jump`/`fall`/`walk` at the modified curve — the physics itself should read
as floaty, not a new animation vocabulary.

## Open Questions

- ~~`run_speed` (128 px/s) vs `10_systems/COMBAT_FORMULA.md` §10's 200 px/s placeholder~~
  **Resolved at the C gate:** COMBAT_FORMULA §10 adopted this doc's 8 tiles/s (= 128 px/s at the
  AB-001 16 px grid) as `base_move_speed`; every authored gap figure in this doc stands
  unchanged.
- Derived gravity/`v0` (§1) are a mathematical reference, not an independently tuned feel; the
  coding pass (`30_engineering/ENGINEERING_STANDARDS.md`) may retune within the constraint that
  apex/distance/run-speed stay locked.
- `climb_speed` (4 tiles/s) and the manual-dismount hop (1.5 tiles) are first-pass; no other doc
  references them yet.
- Optional status-effect tagging on a hazard (e.g., lava applying `burn`,
  `10_systems/STATUS_EFFECTS.md`) is not specified here — left as a per-hazard-instance Phase D
  authoring choice using `apply_status`'s existing flat-magnitude option
  (`10_systems/SKILL_EFFECTS.md` §14), not a new mechanic.
- Moving-platform param shape (§5) is first-pass pending the real map schema
  (`20_schemas/map.schema.md`, Phase C).
- Whether aquatic/flying monsters ignore `water_gravity_mult` entirely (as `aerial_swooper`
  already ignores platform collision, `10_systems/AI_BEHAVIOR.md` §9) is unresolved; flag for
  `10_systems/AI_BEHAVIOR.md`.
- The drop-through input chord (§3) and climb input (§4) are `10_systems/CONTROLS.md`'s to name;
  not assumed here beyond "an input exists."
