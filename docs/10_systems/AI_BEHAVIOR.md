# AI_BEHAVIOR.md — Monster AI Profiles

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md,
10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md, 10_systems/SKILL_EFFECTS.md,
10_systems/COMBAT_FORMULA.md, 10_systems/SPAWN.md, 10_systems/social/PARTY.md,
20_schemas/monster.schema.md, 40_assets/ANIMATION_STATES.md, 40_assets/ART_BIBLE.yaml,
15_maps_system/MAPS_SYSTEM.md, docs/VALIDATION.md, docs/ID_REGISTRY.md

Owner doc for the 12 AI profiles in `00_vision/GLOSSARY.md`. Defines, per profile, its state
machine, aggro/leash rules, platformer-aware movement, attack pattern, and the tunable parameters
a monster's data file may override. A monster file assigns exactly one `ai_profile`
(`20_schemas/monster.schema.md`) plus any tunable overrides; `boss_scripted` additionally declares
a `phases[]` list (§15). Damage numbers, status magnitudes, and element affinities are never
defined here — see `10_systems/COMBAT_FORMULA.md`, `10_systems/STATUS_EFFECTS.md`,
`10_systems/ELEMENTS.md`.

## 1. Shared state machine

Every profile is a path through 8 canonical states, chosen so the coding pass maps 1:1:

| State | Meaning | Typical animation state |
|---|---|---|
| `idle` | No target; minimal/no movement | `idle` |
| `patrol` | No target; moving a set path/territory | `walk` |
| `chase` | Target acquired; closing to attack range | `walk`/`jump`/`fall` as needed |
| `windup` | Committed to an attack; telegraph plays | `telegraph` (elite/boss) or a short `attack` lead-in |
| `attack` | Damage-dealing frame(s) fire | `attack`/`cast` |
| `recover` | Post-attack vulnerability window | `idle` or an `attack` tail |
| `flee` | Moving away from the target | `walk`/`jump` |
| `return` | Aggro broken; pathing home | `walk` |

`flee` covers two different motivations with the same mechanics: fear-based retreat (e.g.
`timid_grazer`) and tactical kiting/repositioning away from the target (e.g. `ranged_skirmisher`,
`support_caller`). Same state, different flavor — nothing mechanical distinguishes them. Not every
profile uses all 8 states; each profile's entry below lists its actual subset. Entering `die`
(`40_assets/ANIMATION_STATES.md`) exits this machine entirely from any state and clears all
statuses (`10_systems/STATUS_EFFECTS.md` §1), regardless of which state the monster was in.

## 2. Shared rules (defined once, not repeated per profile)

- **Aggro trigger types:** `sight` (target within `aggro_radius` tiles **and** within
  `aggro_vertical_band` tiles of vertical offset — the platformer verticality gate), `proximity`
  (radius only, no vertical/line-of-sight gate), `on_hit` (reacts only to incoming damage),
  `on_ally_call` (triggered by another monster's call, e.g. `pack_hunter`). Each profile below
  states which it uses.
- **Default `aggro_vertical_band`:** 3 tiles, overridable per monster. 1 tile = the map's grid
  unit (pixel size owned by `40_assets/ART_BIBLE.yaml`).
- **Leash:** every profile that can relocate has a `leash_radius` (tiles from its home/spawn
  point, `10_systems/SPAWN.md`). Exceeding it while in `chase`/`flee` forces an immediate
  `return`; the leash check is suspended for the duration of an already-committed
  `windup`/`attack` (a charger mid-dash does not snap home mid-swing). Reaching home during
  `return` fully restores `life` and re-enters `idle`/`patrol`. Profiles that never relocate
  (`stationary_turret`) have no leash; `boss_scripted` is bounded by its arena instead (§15).
- **Telegraph requirement:** any `windup` on an elite- or boss-tier monster must use the
  `telegraph` animation state (`40_assets/ANIMATION_STATES.md`; required by `docs/VALIDATION.md`
  §6). Normal-tier monsters may use a short, untelegraphed windup unless a profile states
  otherwise (`kamikaze_burster` is the one stated exception, §12).
- **Ground edge behavior (default):** ground profiles avoid walking off a platform edge or into a
  one-way-platform drop during `idle`/`patrol`/`chase`, unless their entry below explicitly says
  they drop-through or charge through edges.
- Elemental and status behavior (which damage/statuses a monster's attacks apply) is authored
  per-monster via `10_systems/SKILL_EFFECTS.md` ops and `10_systems/ELEMENTS.md` affinities — this
  doc defines only movement, targeting, and timing.

Every tunable below is a `snake_case` field a monster's YAML may override; values shown are
first-pass defaults. Units: radii/distances in tiles, durations/cooldowns in seconds, multipliers
against the monster's baseline move-speed (`10_systems/STATS.md` `haste`-derived speed).

## 3. `passive_wanderer`
**Intent:** ambient wildlife; ignores the player entirely unless struck.
**States:** `idle` → `patrol` → (`on_hit`) → `flee` → `return` → `patrol`. No `chase`/`windup` as
a rule.
**Aggro:** `on_hit` only; `aggro_radius` 0 (sight/proximity disabled by design).
**Leash:** `leash_radius` 5 — short, since it only ever flees a short distance from where it was
struck.
**Movement:** ground; standard edge-avoidance in `patrol`; never drops through platforms.
**Attack:** touch only. If cornered with no `flee` path for `corner_wait_s`, one touch-range tap
(no windup), then keeps trying to flee.
**Cooldown feel:** n/a — not a real combatant.
**Tunables:** `wander_radius` 6, `flee_duration_s` 4, `corner_wait_s` 2.

## 4. `timid_grazer`
**Intent:** notices the player from a distance and runs; fights only when it has no way out.
**States:** `idle`/`patrol` → `flee` → `return`. `windup`/`attack` occur only in the cornered edge
case.
**Aggro:** `proximity`, `aggro_radius` 5 — this radius triggers `flee`, never `chase`.
**Leash:** `leash_radius` 6.
**Movement:** ground; standard edge-avoidance while grazing, but while fleeing it will use a
one-way-platform drop-through if one lies on its escape path — the one profile that drop-throughs
while escaping, a visible "it got away" beat (P1).
**Attack:** touch only. If `flee` is blocked (wall/edge with no drop) for `corner_wait_s`, one weak
touch-range panic hit, then resumes fleeing.
**Cooldown feel:** n/a.
**Tunables:** `flee_radius` 5, `flee_speed_mult` 1.5, `corner_wait_s` 2.

## 5. `aggressive_charger`
**Intent:** commits hard and fast at anything it notices; punishable if sidestepped.
**States:** `idle`/`patrol` → `chase` → `windup` → `attack` → `recover` → `return`.
**Aggro:** `sight`, `aggro_radius` 7.
**Leash:** `leash_radius` 9.
**Movement:** ground; standard edge-avoidance in `idle`/`patrol`/`chase`, but the `attack` dash
explicitly ignores edge-avoidance — a committed charger runs off a ledge if that's where its line
took it (a readable, baitable tell, P1).
**Attack:** windup (telegraph required if elite) then a fast dash; contact during the dash deals
damage; a long `recover` afterward leaves it vulnerable.
**Cooldown feel:** slow and heavy — the payoff is punishing the recovery window.
**Tunables:** `aggro_radius` 7, `charge_speed_mult` 2.5, `charge_recover_s` 2.5.

## 6. `territorial_guard`
**Intent:** holds a specific spot or chokepoint; won't be pulled far from it.
**States:** `idle`/`patrol` (small loop) → `chase` → `windup` → `attack` → `recover` → `return`.
**Aggro:** `proximity`, `aggro_radius` 5.
**Leash:** `leash_radius` 4 — the tightest of any non-stationary profile; it gives up the instant
the target leaves its post.
**Movement:** ground; a small patrol loop (or fully stationary idle) within its territory;
standard edge-avoidance; never drops through.
**Attack:** windup melee swing (telegraph required if elite), moderate strength.
**Cooldown feel:** steady and predictable — a bread-and-butter mid-length swing cadence.
**Tunables:** `aggro_radius` 5, `leash_radius` 4, `patrol_radius` 3.

## 7. `ambush_lurker`
**Intent:** waits hidden and punishes anyone who walks on top of it.
**States:** `idle` (concealed, no `patrol`) → `attack` (surprise, no `windup`) → `recover` →
`chase`/`windup`/`attack` (revealed, normal cadence) → `return`.
**Aggro:** `proximity`, `aggro_radius` 2 — deliberately tiny; the hidden state itself is the
informed risk (any visual tell for the player is `40_assets/ART_BIBLE.yaml`'s concern, not this
doc's).
**Leash:** `leash_radius` 3 — barely leaves its hiding spot even once revealed.
**Movement:** ground; motionless while concealed; may cross one short gap to an adjacent platform
on its surprise strike, but does not use one-way drop-through.
**Attack:** first strike is instant/touch (no `windup` — concealment is the telegraph substitute);
once revealed, falls back to a normal windup melee pattern identical to `territorial_guard`'s.
**Cooldown feel:** one sharp opening hit, then steady like a guard.
**Tunables:** `ambush_radius` 2, `leash_radius` 3, `aggro_vertical_band` 1 (same-platform only).

## 8. `ranged_skirmisher`
**Intent:** keeps its distance and peppers the target; never wants to be touched.
**States:** `idle`/`patrol` → `chase`/`flee` (repositioning) → `windup` → `attack` → `recover` →
`return`.
**Aggro:** `sight`, `aggro_radius` 9 — the longest sight range, so it can open at range.
**Leash:** `leash_radius` 11.
**Movement:** ground; repositions along its current platform to hold between
`preferred_range_min` and `preferred_range_max`; standard edge-avoidance (backs up to an edge and
stops there, never falls off retreating).
**Attack:** windup projectile only (telegraph required if elite); never a touch attack, even if
cornered at melee range.
**Cooldown feel:** brisk and frequent — short enough that kiting stays threatening.
**Tunables:** `preferred_range_min` 4, `preferred_range_max` 8, `attack_cooldown_s` 1.5.

## 9. `aerial_swooper`
**Intent:** patrols the air lane above the fight and dives.
**States:** `idle`/`patrol` (airborne) → `chase` → `windup` → `attack` (dive) → `recover`
(climb back) → `return`.
**Aggro:** `sight`, `aggro_radius` 8.
**Leash:** `leash_radius` 10 (measured from its home patrol lane, not ground distance).
**Movement:** air; ignores ground/platform collision entirely at `patrol_altitude` — the dive
`attack` is the only phase where it approaches the platform layer. No drop-through concept; it
flies above platforms rather than through them.
**Attack:** windup hover-charge (telegraph required if elite) then a fast dive along a line toward
the target; contact during the dive deals damage; climbs back to `patrol_altitude` during
`recover`.
**Cooldown feel:** bursty — a visible charge-up, a fast strike, then a slower climb-back before it
can dive again.
**Tunables:** `patrol_altitude` 4, `swoop_speed_mult` 2.0, `climb_recover_s` 3.

## 10. `pack_hunter`
**Intent:** weak alone, dangerous in numbers; calls its pack in.
**States:** `idle`/`patrol` → `chase` → `windup` → `attack` → `recover` → `return`. Adds
`on_ally_call` as an alternate entry into `chase` (see below).
**Aggro:** `sight`, `aggro_radius` 5, **plus** it broadcasts a call on aggro: any other
`pack_hunter` within `pack_call_radius` tiles enters `chase` on the same target (`on_ally_call`
trigger) even if the target is outside *their own* `aggro_radius`. Each called member still
leashes from **its own** home point, never the caller's — a pack can only be pulled as far as its
individual members' leashes allow.
**Leash:** `leash_radius` 7 (per member, per above).
**Movement:** ground; standard edge-avoidance individually; converging pack members may use
drop-through platforms while in `chase` to reach the target faster — the other profile besides a
fleeing `timid_grazer` that drop-throughs, here to converge rather than escape.
**Attack:** touch melee, fast and individually weak; no windup — the threat is numbers, not a
telegraphed hit from any one member.
**Cooldown feel:** fast, low-cooldown per member.
**Tunables:** `aggro_radius` 5, `pack_call_radius` 8, `pack_max_size` 4.

## 11. `support_caller`
**Intent:** buffs and heals its allies rather than fighting the player directly.
**States:** `idle`/`patrol` → `flee`/`chase` (repositioning near allies, away from the player) →
`windup` → `attack` (cast on an ally) → `recover` → `return`.
**Aggro:** `sight`, `aggro_radius` 6 — notices the player in order to retreat toward allies, not
to engage them.
**Leash:** `leash_radius` 8.
**Movement:** ground; stays on platforms near the allies it supports; standard edge-avoidance;
does not drop through (prioritizes staying near its backline over escaping).
**Attack:** windup cast (telegraph if elite) applying a buff (`empower`/`fortify`/`regen`,
`10_systems/STATUS_EFFECTS.md`) to a nearby ally via `apply_status`
(`10_systems/SKILL_EFFECTS.md`) — not a direct player attack. If the player is adjacent with no
ally within `support_radius`, it falls back to one weak windup self-defense hit.
**Cooldown feel:** patient — long enough between casts that buffs never blanket the fight
permanently.
**Tunables:** `support_radius` 6, `cast_cooldown_s` 6, `retreat_range` 6.

## 12. `kamikaze_burster`
**Intent:** rushes the target and detonates; the attack is also its death.
**States:** `idle`/`patrol` → `chase` → (leash exceeded → `return`, same as any profile) →
`windup` (only once within `detonate_range`) → `attack` (detonate — the entity is removed; no
`recover`).
**Aggro:** `sight`, `aggro_radius` 6.
**Leash:** `leash_radius` 8; if the target escapes beyond it during `chase`, it gives up and
`return`s exactly like any other profile — only once `windup` begins is there no way back.
**Movement:** ground; rushes the most direct path to the target from the moment `chase` begins,
including off short edges/drops if that is the straight line — the one profile whose *entire*
committed phase (not just the final dash) ignores edge-avoidance.
**Attack:** single windup detonation at `detonate_range` (touch range). **Exception to the shared
telegraph rule (§2):** `kamikaze_burster` always plays `telegraph` before detonating, even at
`normal` tier — an untelegraphed self-destruct would violate `00_vision/PILLARS.md` P1 regardless
of monster tier. If killed before its windup completes, it simply dies without detonating; an
on-death-detonate variant is not defined here (see Open Questions).
**Cooldown feel:** one-shot — there is no repeat cooldown.
**Tunables:** `aggro_radius` 6, `detonate_range` 1, `rush_speed_mult` 1.8.

## 13. `stationary_turret`
**Intent:** a fixed-position threat that punishes staying in its line of fire.
**States:** `idle` → `windup` → `attack` → `recover` → `idle` (repeat while target in range). No
`patrol`/`chase`/`flee`/`return` — it never relocates, so it has no home point to leash from or
path back to.
**Aggro:** `sight`, `aggro_radius` 7. Losing sight/range simply returns it to `idle` in place.
**Leash:** n/a (immobile).
**Movement:** none. Ground/wall/ceiling-anchored placement is an art/level-layout concern, not an
AI one.
**Attack:** windup projectile (telegraph required if elite), repeating on cooldown while the
target remains in range.
**Cooldown feel:** metronomic — a fixed, fully learnable cadence.
**Tunables:** `aggro_radius` 7, `attack_cooldown_s` 2.5, `windup_s` 0.6.

## 14. `boss_scripted` — overview
**Intent:** an authored fight, not a reactive profile — combines other profiles' movement/attack
patterns per phase and adds boss-only abilities as it takes damage. Full phase contract in §15.
**States:** typically enters `chase`/`windup` immediately on arena-entry aggro (the trigger is
`15_maps_system/MAPS_SYSTEM.md`'s, not a `sight`/`proximity` roll), plus one boss-only state:
**`phase_shift`**, entered on a `life_threshold_pct` crossing. No `flee`/`return` — a boss does not
leash home; it is bounded by the arena itself, which is `15_maps_system/MAPS_SYSTEM.md`'s to
enforce, not this doc's.
**Attack:** always windup + `telegraph` — the `boss` entity tier (`20_schemas/monster.schema.md`)
falls under §2's telegraph requirement the same as `elite`, with no exceptions.
**Cooldown feel:** varies per phase; retuned via `param_overrides` (§15).

## 15. The `boss_scripted` phase contract

`10_systems/STATUS_EFFECTS.md` §1 already defines `phase_shift`'s behavior (no new status
applications; existing DoTs/CC suspended; invulnerable/untargetable by convention) — this doc only
triggers entry into it, never redefines what happens inside it. Bosses are immune to hard CC
(`10_systems/STATUS_EFFECTS.md` §3) — not restated here.

A boss monster file declares an ordered `phases[]` list (full field typing owned by
`20_schemas/monster.schema.md`; this doc specifies the AI-relevant contents that schema must
carry):

| Field | Meaning |
|---|---|
| `phase_id` | 1-based, ascending |
| `life_threshold_pct` | Enter this phase the instant boss `life` first drops ≤ this % of max; phase 1 is always 100 |
| `base_profile` | Which of the other 11 profiles this phase's movement/attack pattern borrows; omit to keep the previous phase's |
| `param_overrides` | Map of `snake_case` tunables (§3–13, e.g. `aggro_radius`, `attack_cooldown_s`) to new values for this phase |
| `added_abilities` | Ability references unlocked this phase — authored directly on the monster (`20_schemas/monster.schema.md`), **not** drawn from the player `skill_<line>_NNN` ID space (see Open Questions) |
| `enter_telegraph` | Bool; if true, entering this phase plays `phase_shift` before combat resumes |

**Transition rule:** a `life_threshold_pct` crossing interrupts immediately — even mid-`windup`/
`attack` — rather than waiting for `recover`. This is a deliberate exception to the normal state
machine: the life bar crossing the line **is** the telegraph (P1), so an instant cut to
`phase_shift` stays fair even though it interrupts. If a single hit crosses more than one
threshold at once, the boss enters only the lowest applicable phase directly; intermediate phases
are not played through.

**Ownership boundary:** the phase contract lives in the monster file. Arena-side scripting —
environmental hazards, add-wave placement, arena geometry changes, camera locks — is authored in
the map file and owned entirely by `15_maps_system/MAPS_SYSTEM.md`; it is not part of `phases[]`
and is not defined here. Add-wave *monsters themselves* spawn via the `summon_entity` effect op
(`10_systems/SKILL_EFFECTS.md`) as one of the boss's own `added_abilities`, not through
`10_systems/SPAWN.md`'s zone spawner.

**Tunables:** `phase_shift_duration_s` 1.5 (default transition window before the new phase's
combat resumes), `phase_transition_lock` true (life-threshold crossings always interrupt per
above; set false only if a specific boss needs a softer transition — flag it in that boss's data).

## Open Questions
- **Boss/monster ability ID prefix — resolved at the C gate:** the per-monster
  `mob_ability_<mob_NNN>_01`–`_08` namespace was adopted
  (`docs/phase_reports/PHASE_H_CONSISTENCY_REPORT.md`). Summon templates, by contrast, have
  **no minted `mob_NNN` block** — `mob_151`–`mob_178` belongs to the Frostpeak roster
  (`docs/ID_REGISTRY.md`, immutable) — so content references them via `summon_tmpl_*`
  placeholders (`docs/phase_reports/PHASE_D_ARC2_REPORT.md`), real IDs pending (next item).
- **Summon-template ID block — request to `docs/ID_REGISTRY.md`:** summon templates need a
  dedicated ID block outside the regional `mob_NNN` rosters; once ID_REGISTRY mints one (in
  its own commit — not minted here), the `summon_tmpl_*` placeholders re-point to real IDs.
- An on-death-detonate variant of `kamikaze_burster` (explodes even if killed before its windup
  completes) is not defined; if a later design wants it, it should be a monster-authored
  `on_hit_proc`/death effect (`10_systems/SKILL_EFFECTS.md`), not a change to this profile's base
  rule.
- `pack_max_size` (4) and `pack_call_radius` (8) are first-pass; may need per-region tuning once
  pack rosters are authored (Phase D).
- Whether a non-boss monster may ever combine two profiles (a "hybrid elite") outside the
  `boss_scripted` phase mechanism is out of scope here — default is exactly one profile per
  non-boss monster.
- Exact tile-to-pixel size for `aggro_radius`/`aggro_vertical_band` units is owned by
  `40_assets/ART_BIBLE.yaml`; not fixed here.
- `phase_shift_duration_s` and whether it should scale for raid finales
  (`10_systems/social/RAID.md`) is a first-pass default; owner
  `10_systems/COMBAT_FORMULA.md`/`10_systems/social/PARTY.md` may retune.
