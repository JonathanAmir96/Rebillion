# ANIMATION_TIMING.md — Playback-Rate & Hit-Frame Law

References: 00_vision/GLOSSARY.md, 40_assets/ANIMATION_STATES.md, 40_assets/ART_BIBLE.yaml,
40_assets/SPRITESHEET_SPEC.md, 30_engineering/ENGINEERING_STANDARDS.md,
10_systems/COMBAT_FORMULA.md, 10_systems/STATS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/AI_BEHAVIOR.md, 10_systems/SPAWN.md, 20_schemas/monster.schema.md,
20_schemas/skill.schema.md

Owner doc for the two things `40_assets/ANIMATION_STATES.md` explicitly deferred to it (its §4):
**exactly which frame** inside an `attack`/`cast` clip fires the combat damage signal (the
hit-frame), and the base playback speed every one of the 12 states runs at, including how `haste`
scales it. This doc owns **timing law only** — purpose, loop/one-shot behavior, interrupt priority,
and the required-state-per-class matrix stay `40_assets/ANIMATION_STATES.md`'s; frame-count ranges
and pixel dimensions stay `40_assets/ART_BIBLE.yaml`'s; the manifest **field** `hit_frame`/`fps_ref`
live in is `40_assets/SPRITESHEET_SPEC.md`'s (§7 there) — this doc fills that field with law, never
restates its shape. Damage math itself (`CombatMath`, mitigation, crit) stays entirely
`10_systems/COMBAT_FORMULA.md`'s; this doc only fixes **when** the signal that triggers it fires.

## 1. Base fps per state

One fixed frames-per-second value per state — the "snappy, readable, few frames done well"
principle (`40_assets/ART_BIBLE.yaml` `animation.principle`) applied to *time*, not frame count
(`ART_BIBLE.yaml`'s `frame_budgets` already fixes the latter). Loop states cite a **cycle length**
(no fixed duration — the loop just needs to read cleanly, `40_assets/ANIMATION_STATES.md` §1.1);
one-shot states cite a **playthrough length**, worked at the low/high end of each state's frame-count
budget (locked 9 states: `40_assets/ART_BIBLE.yaml animation.frame_budgets`; proposed 3 states:
`40_assets/ANIMATION_STATES.md` §2.2 — carrying that doc's own not-yet-blessed caveat, Open
Questions).

| State | Base fps | Loop/one-shot | Frame budget | Length at budget ends |
|---|---|---|---|---|
| `idle` | 5 | loop | [2,4] | 0.4 s – 0.8 s / cycle |
| `walk` | 9 | loop | [6,8] | 0.667 s – 0.889 s / cycle |
| `jump` | 10 | one-shot, holds (§2.2) | [1,2] | 0.1 s – 0.2 s |
| `fall` | 10 | one-shot, holds (§2.2) | [1,2] | 0.1 s – 0.2 s |
| `climb` | 8 | loop | [2,4] | 0.25 s – 0.5 s / cycle |
| `attack` | 11 | one-shot, haste-scaled (§3) | [4,6] | 0.364 s – 0.545 s (unhasted) |
| `cast` | 11 | one-shot, haste-scaled (§3) | [4,6] | 0.364 s – 0.545 s (unhasted) |
| `hit` | 12 | one-shot | [2,3] | 0.167 s – 0.25 s |
| `die` | 8 | one-shot | [4,6] | 0.5 s – 0.75 s |
| `telegraph` | 4 | one-shot, holds (§4) | [2,3]* | 0.5 s – 0.75 s |
| `phase_shift` | 6 | one-shot, holds/truncates (§6) | [4,6]* | 0.667 s – 1.0 s |
| `spawn` | 8 | one-shot, no external clock (§7) | [3,5]* | 0.375 s – 0.625 s |

`*` = proposed, not yet Agent-3-blessed budget (`40_assets/ANIMATION_STATES.md` §2.2). `jump`/`fall`
at 1 frame are a degenerate case: nothing "plays through," the single frame is the held pose from
the instant the state is entered (`40_assets/ANIMATION_STATES.md` §1.1).

**`telegraph`/`phase_shift` are never haste-scaled**, deliberately: `telegraph` is the fairness "tell"
that makes a hard-hitting attack dodgeable (`40_assets/ART_BIBLE.yaml` `animation.telegraphs`;
`10_systems/AI_BEHAVIOR.md` §2) — a hasted monster must never get to compress its own tell below the
tier floor (§4), which would defeat the entire reason the floor exists. `phase_shift`'s duration is
an externally-owned mechanical timer (§6), not a playback rate, so haste has no lever to pull there
either.

### 1.1 The general hold rule

Any one-shot clip whose on-screen **duration** is set by something other than its own frame
playback — a physics arc for `jump`/`fall` (`15_maps_system/MAP_TRAVERSAL.md`, cited by
`40_assets/ANIMATION_STATES.md` §1.1), a tier-minimum floor for `telegraph` (§4), or
`phase_shift_duration_s` for `phase_shift` (§6) — plays through its authored frames once at the §1
fps, then **holds its final frame** for whatever time remains (or, for `phase_shift` only, is cut
short in the rare case the external timer is shorter than the clip — §6). `attack`, `cast`, `hit`,
`die`, and `spawn` have no such external clock: their on-screen duration **is** their clip's own
playback length, full stop.

## 2. Duration formula & `haste` (player only)

```
effective_fps(state)          = base_fps(state)                                  # all states except attack/cast
effective_fps(attack | cast)  = base_fps(state) * (1 + attack_speed_pct)         # §3 below
clip_duration_s                = frame_count / effective_fps(state)
```

This mirrors `10_systems/COMBAT_FORMULA.md` §10's `effective = base_attack_interval /
(1 + attack_speed%)` shape (division rather than multiplication there because it frames the *interval
between* swings; the same `(1 + attack_speed%)` factor governs both, so the visible swing and the
attack cadence scale in lockstep and never drift apart relative to each other). **Whether the
`attack`/`cast` clip's own duration is meant to *equal* `10_systems/COMBAT_FORMULA.md`'s
`base_attack_interval`/a skill's cast+recovery window, or is shorter with the remainder covered by an
unanimated recovery lock, is `10_systems/SKILL_SYSTEM.md`'s still-open cast+recovery field to settle
(`20_schemas/skill.schema.md` Open Questions) — this doc fixes only the clip's own playback-rate
scaling, not that broader window.**

**Monsters do not carry a `haste` stat** (`20_schemas/monster.schema.md` Open Questions: "the §13
budget names no `crit_rate`/`crit_power`/`haste`/`essence` for monsters"). `attack_speed_pct` in the
formula above therefore means:
- **Player:** the final, soft/hard-capped, status-modified attack-speed percentage
  (`10_systems/STATS.md` §5–§7).
- **Monster:** `0%` baseline (no gear-driven haste to convert), modified **only** by a status effect
  that explicitly states an attack-speed-output change — today, `chill`'s `−15%` attack-speed output
  (`10_systems/STATUS_EFFECTS.md` §4.1). A monster's attack **cadence** (how often it swings at all)
  is a wholly separate number, owned by its `ai_profile`'s cooldown tunables
  (`10_systems/AI_BEHAVIOR.md`, e.g. `attack_cooldown_s`) or a boss ability's `cooldown`
  (`20_schemas/monster.schema.md`) — never this doc's formula.

### 2.1 Worked example (player, `attack`, `frame_count = 5`, `hit_frame = 2`, §3)

`10_systems/STATS.md` §6 soft-caps `attack_speed_pct` at `40%` (above-soft rate ×0.5) and hard-caps
it at `75%`:

| `attack_speed_pct` | `effective_fps` | `clip_duration_s` | `hit_time_s` (§3.2) |
|---|---|---|---|
| 0% (unhasted) | 11.00 | 0.455 | 0.182 |
| 40% (soft cap) | 15.40 | 0.325 | 0.130 |
| 75% (hard cap) | 19.25 | 0.260 | 0.104 |

## 3. THE HIT-FRAME CONTRACT (load-bearing)

Every `attack`/`cast` clip — and, because monster/boss `abilities[]` rows carry no clip of their own
(`20_schemas/monster.schema.md`; see `40_assets/SPRITESHEET_SPEC.md` Open Questions), every monster
**ability** that plays through one of those two states — declares exactly one `hit_frame` index in
the atlas manifest (`40_assets/SPRITESHEET_SPEC.md` §7.1, the `states.attack.hit_frame` /
`states.cast.hit_frame` field). That frame, and only that frame, emits the signal the combat system
listens for:

> "the animation's hit-frame (ANIMATION_TIMING) emits the signal combat listens for — damage never
> on a duplicate timer" (`30_engineering/ENGINEERING_STANDARDS.md`).

Concretely: the state-machine node requests the animation; when playback reaches `hit_frame`, it
fires one signal (EventBus, `30_engineering/ENGINEERING_STANDARDS.md` "signals up, calls down"); the
combat system (`CombatMath`, `10_systems/COMBAT_FORMULA.md` §1–§2) resolves damage in response. No
second, independent timer (a fixed-delay `Timer` node, a hardcoded seconds value) may **also** apply
damage for the same swing — the hit-frame is the *only* trigger, by construction, so the two can
never desync.

### 3.1 Default formula

```
hit_frame = ceil(0.6 * frame_count) - 1        # 0-indexed; overridable per asset in the manifest
```

| `frame_count` | `ceil(0.6*n)` | `hit_frame` (default) | Time through clip at that frame's start |
|---|---|---|---|
| 4 | 3 | 2 | 50% |
| 5 | 3 | 2 | 40% |
| 6 | 4 | 3 | 50% |

This is the value Phase D writes into the manifest absent a specific reason to differ — e.g. a slow
overhead swing that reads better with a later hit. The manifest's stored integer is always what
engineering reads (`40_assets/SPRITESHEET_SPEC.md` §7.1); this formula is an authoring aid, never a
runtime computation (`30_engineering/ENGINEERING_STANDARDS.md` prime directive 1, data-driven — the
number lives in data, not code).

### 3.2 Haste scales time, never the index

```
hit_time_s = hit_frame / effective_fps(attack | cast)
```

The **index** `hit_frame` (e.g., "frame 2 of 5") never changes with `attack_speed_pct` — haste never
adds or removes authored frames. Only the **wall-clock moment** that indexed frame arrives moves,
because `effective_fps` scales (§2). This is the literal meaning of "animation scales, hit-frame
index does not move": §2.1's worked table shows the same `hit_frame = 2` landing at `0.182 s`,
`0.130 s`, and `0.104 s` as `attack_speed_pct` rises — the swing gets faster, not differently shaped.

### 3.3 Projectile caveat

For a `projectile`-targeted attack/ability (`10_systems/SKILL_SYSTEM.md` §6 shape, not read against
this doc's task list), `hit_frame` most plausibly fires the projectile's **spawn/release** (matching
`30_engineering/ENGINEERING_STANDARDS.md`'s Hitbox/Area2D pattern), with actual damage applying later
on a travel-time collision — a second, later signal this doc does not name or define. **Since
confirmed:** `40_assets/SKILL_ANIMATION.md` §2 fixes exactly this reading (release at `hit_frame`,
damage on the projectile's own collision signal) as skill-visual law.

## 4. Telegraph minimum on-screen time by tier

A `telegraph` clip must remain visible at least this long regardless of its authored frame count —
the floor beneath which a "tell" stops being fair warning:

| Tier | Minimum on-screen time |
|---|---|
| `elite` | ≥ 0.4 s |
| `boss` | ≥ 0.6 s |

```
total_on_screen_s = max(clip_duration_s, tier_minimum_s)      # §1.1 hold rule
hold_s            = max(0, tier_minimum_s - clip_duration_s)
```

Worked against §1's `telegraph` fps (4) and proposed `[2,3]` budget:

| `frame_count` | `clip_duration_s` | vs `elite` (0.4 s) | vs `boss` (0.6 s) |
|---|---|---|---|
| 2 | 0.5 | clears — no hold | short by 0.1 s — holds to 0.6 s |
| 3 | 0.75 | clears — no hold | clears — no hold |

**`kamikaze_burster`'s normal-tier exception** (`10_systems/AI_BEHAVIOR.md` §12 — the one case where
a `normal`-tier monster is required to play `telegraph`, `40_assets/ANIMATION_STATES.md` §5.2): no
doc states a minimum on-screen time for it specifically, since the task/tier table above only names
`elite`/`boss`. This doc extends the `elite` floor (`≥ 0.4 s`) to it by identical fairness
reasoning — an untelegraphed-in-effect self-destruct is exactly the P1 problem the exception exists
to prevent — but this extension is **not** independently confirmed by `10_systems/AI_BEHAVIOR.md` or
any other doc; flagged in Open Questions rather than silently folded into the table above.

## 5. Hitstun / cancel windows (`hit` vs. `10_systems/COMBAT_FORMULA.md` §11)

`10_systems/COMBAT_FORMULA.md` §11 classes every landed hit `Light` (0.12 s hitstun) or `Heavy`
(0.35 s hitstun); this doc's job is only to line that lockout duration up against the `hit` clip's
own playback length (§1: fps 12, budget `[2,3]` → `0.167 s`–`0.25 s`):

| Hitstun class | Lockout | vs. `hit` clip (0.167–0.25 s) | Resolution |
|---|---|---|---|
| Light | 0.12 s | shorter than the clip, always | Clip keeps playing past hitstun's end; once the lockout expires, a new FSM transition (`40_assets/ANIMATION_STATES.md` §3, "ordinary transition") **may** cancel the remaining frames early — hitstun ending is not itself a forced cut. |
| Heavy | 0.35 s | longer than the clip, always | Clip finishes, then holds its final frame (§1.1) for the remainder — `0.183 s` (2-frame clip) or `0.10 s` (3-frame clip) of hold. |

**Re-entry mid-clip.** Per `40_assets/ANIMATION_STATES.md` §1.1, a second landed hit restarts `hit`
from frame 0; this doc adds that the **new** hit's class (Light/Heavy) establishes a fresh lockout
from that instant — hitstun does not stack additively across overlapping hits (monsters carry no
i-frames, `10_systems/COMBAT_FORMULA.md` §12, so this restart can happen repeatedly under a fast
combo).

**Whether `hit` is entered at all.** `40_assets/ANIMATION_STATES.md` §3 confirms a Heavy hit
interrupts a mid-`cast` (monster, unless super-armored; player, unless in i-frames/stability) and
treats a Light hit as a "non-canceling flinch" there — meaning, in a single-active-state machine, a
Light hit that does not cancel `cast` never actually enters `hit` at all (there is no second active
state to layer it into); only a Heavy hit interrupting `cast`, or **any** hit landing while the
entity is in a freely-cancelable state (`idle`/`walk`/`recover`), actually triggers `hit`. Whether the
same Light/Heavy split applies to a hit landing mid-`attack` or mid-`telegraph` is a gap
`40_assets/ANIMATION_STATES.md` itself already flags (its own Open Questions: "covers `cast` only")
— this doc's table above is written for the confirmed `cast` case and inherits that same gap for
`attack`/`telegraph` rather than resolving it (Open Questions).

## 6. `phase_shift` invulnerability sync

`10_systems/STATUS_EFFECTS.md` §1: while a boss is in `phase_shift`, "no new status applications" and
"all existing DoT timers and CC are suspended," and the boss is "invulnerable/untargetable by
convention" for the state's duration. `10_systems/AI_BEHAVIOR.md` §15 names that duration a real
field, `phase_shift_duration_s` (default `1.5 s`, overridable per boss like any other `ai_profile`
tunable, `20_schemas/monster.schema.md` `ai_params`). This doc's rule:

```
total_on_screen_s = phase_shift_duration_s        # ALWAYS — never the clip's own natural length
```

The clip plays through its authored frames at `6 fps` (§1); at the proposed `[4,6]` budget that is
`0.667 s`–`1.0 s`, always shorter than the `1.5 s` default, so in the default case the clip simply
holds its final frame for the `0.5 s`–`0.833 s` remainder (§1.1). **If a specific boss overrides
`phase_shift_duration_s` shorter than its clip's natural playthrough**, the mechanical timer still
wins — the clip is cut at expiry rather than allowed to run long — because invulnerability-drop and
combat-resume (`10_systems/AI_BEHAVIOR.md` §15: "combat resumes" once the phase transition ends) are
gated by `phase_shift_duration_s` itself, never by "however long the animation happens to take." This
generalizes `30_engineering/ENGINEERING_STANDARDS.md`'s no-duplicate-timer principle (§3 above) from
damage timing to invulnerability timing: there is exactly one clock, and the animation defers to it
in both directions (hold if short, truncate if long). Phase D should still pick `frame_count`/pick a
per-boss `phase_shift_duration_s` combination that avoids routine truncation in practice — this doc
states the correctness rule, not an authoring guarantee against it (Open Questions).

## 7. `spawn` — contrast with `phase_shift`

`10_systems/SPAWN.md` §6 ties an elite/boss `spawn`'s invulnerability to "the duration of its
`spawn` state" with **no separate numeric field** (unlike `phase_shift_duration_s`). So, unlike §6
above:

```
total_on_screen_s = clip_duration_s        # spawn has no external timer to hold against or truncate to
```

`spawn`'s invulnerability drop is gated by the same clock as its own playthrough — there is no second
duration anywhere in `10_systems/SPAWN.md` for it to drift against. At the proposed `[3,5]` budget
and `8 fps` (§1), that is `0.375 s`–`0.625 s`, entirely Phase D's choice within the budget; no floor
or ceiling beyond it is stated by any doc read for this task.

## Open Questions

- **Heavy-hit interrupt coverage (`attack`/`telegraph`) is unconfirmed.** `10_systems/COMBAT_FORMULA.md`
  §11 states the Heavy-hit-interrupts-mid-`cast` rule only; `40_assets/ANIMATION_STATES.md` already
  flags that `attack`/`telegraph` parity is assumed, not stated. §5's table here is written for the
  confirmed `cast` case only; inherits that gap rather than resolving it.
- ~~Projectile `hit_frame` semantics (§3.3).~~ **Resolved (C):** `40_assets/SKILL_ANIMATION.md` §2
  confirms release-at-`hit_frame` with damage on the projectile's own travel-time collision signal,
  consistent with `10_systems/SKILL_SYSTEM.md` §6's `projectile` shape. §3.3's reading stands as
  written.
- **`kamikaze_burster` normal-tier telegraph minimum (§4).** This doc extends the `elite` 0.4 s floor
  to that one normal-tier exception by fairness analogy; `10_systems/AI_BEHAVIOR.md` §12 states the
  exception itself but not a minimum on-screen time. Not independently confirmed.
- **Telegraph/`phase_shift`/`spawn` fps sit atop `40_assets/ANIMATION_STATES.md` §2.2's proposed, not
  yet Agent-3-blessed, frame budgets.** The fps *values* in §1 are this doc's own law regardless of
  the outcome, but every worked duration in §1/§4/§6/§7 using those three states' frame counts needs
  recomputing if the blessed numbers land differently.
- **Per-skill cast+recovery window (§2) remains `10_systems/SKILL_SYSTEM.md`'s open field**
  (`20_schemas/skill.schema.md` Open Questions). This doc fixes the clip's own haste-scaled playback
  and `hit_frame` timing only — not whether that clip's duration equals, or sits inside, the broader
  per-skill input-lock window.
- **Walk/climb/jump/fall are deliberately not `move-speed_pct`-scaled in this pass.** Only
  `attack`/`cast` scale, and only by `attack_speed_pct` (§2). Visually matching a hasted character's
  gait to its movement speed is a plausible future enhancement, not attempted here; also pending
  `10_systems/COMBAT_FORMULA.md` §10's own flagged placeholder on `base_move_speed`'s px/s value.
- **`phase_shift_duration_s` truncation (§6) is a correctness rule, not an authoring guarantee.**
  Nothing in this doc prevents Phase D from authoring a `frame_count`/per-boss-override combination
  that truncates routinely; flag if `docs/VALIDATION.md` should warn when a boss's
  `phase_shift_duration_s` override is shorter than its `phase_shift` clip's natural length at §1's
  fps.
- **Monster attack-speed-output modeling (§2) treats haste-less monsters as a `0%` baseline modifiable
  only by explicit status effects (e.g. `chill`).** `20_schemas/monster.schema.md` confirms monsters
  carry no `haste` stat, but no doc explicitly confirms this "0%-baseline-plus-status" reading is the
  intended one for animation playback specifically; flagged for `10_systems/STATUS_EFFECTS.md`'s
  owner to confirm.
