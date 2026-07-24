# ANIMATION_STATES.md — The 12-State Animation Registry

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 40_assets/ART_BIBLE.yaml,
40_assets/ANIMATION_TIMING.md, 40_assets/SKILL_ANIMATION.md,
10_systems/AI_BEHAVIOR.md, 15_maps_system/MAP_TRAVERSAL.md, 10_systems/COMBAT_FORMULA.md,
10_systems/STATUS_EFFECTS.md, 10_systems/SPAWN.md, 10_systems/DEATH_PENALTY.md, 10_systems/STATS.md,
20_schemas/monster.schema.md, 20_schemas/npc.schema.md, 20_schemas/skill.schema.md,
30_engineering/ENGINEERING_STANDARDS.md, docs/VALIDATION.md, docs/ID_REGISTRY.md

Owner doc for the 12 animation states in `00_vision/GLOSSARY.md` — the complete, closed set; no
entity of any kind uses a 13th token, and no doc may invent one
(`15_maps_system/MAP_TRAVERSAL.md` §7 already leans on this closure when it declines to add a
`swim` state). This doc fixes, per state: its purpose, whether it loops or plays once, its
frame-count budget, what cancels it and what it cancels, and — via the required-set matrix (§5) —
which of the 12 tokens each entity class must declare in its `animation_states` field
(`20_schemas/monster.schema.md`) for `docs/VALIDATION.md` check 6 to pass.

**What this doc does not own:** pixel/silhouette/palette treatment and the 9 locked frame-count
numbers themselves (`40_assets/ART_BIBLE.yaml`, cited in §2, never re-derived); *why* an
`ai_profile` enters `windup`/`chase`/`flee`/etc., or which profile does what
(`10_systems/AI_BEHAVIOR.md`, cited throughout); jump/fall/climb kinematics and platforming physics
(`15_maps_system/MAP_TRAVERSAL.md`, cited in §1/§3); exact per-frame hit-frame indices and
clip-length timing (owned by `40_assets/ANIMATION_TIMING.md`); and per-skill
animation clip **IDs** (owned by `40_assets/SKILL_ANIMATION.md`, cited by
`20_schemas/skill.schema.md` — a different namespace than the state tokens
this doc owns).

## 1. The 12-state registry

| # | Token | Purpose | Loop / One-shot |
|---|---|---|---|
| 1 | `idle` | No target/no input; ambient minimal-motion pose. The default state — nothing else is claiming priority. | Loop |
| 2 | `walk` | Grounded horizontal locomotion: player run input, or a monster's `patrol`/`chase`/`flee`/`return` movement (`10_systems/AI_BEHAVIOR.md` §1 table). Doubles as the flight-loop for airborne AI profiles — no separate `fly` token (§5.3). | Loop |
| 3 | `jump` | Rising phase of a jump arc (player jump input, or a monster's `chase` crossing a gap, `10_systems/AI_BEHAVIOR.md` §1). Kinematics owned by `15_maps_system/MAP_TRAVERSAL.md` §1. | One-shot (§1.1) |
| 4 | `fall` | Descending phase — post-apex, an unjumped drop off an edge, or a `one_way` drop-through (`15_maps_system/MAP_TRAVERSAL.md` §3). Never itself a damage event (`15_maps_system/MAP_TRAVERSAL.md` §2 — no fall damage). | One-shot (§1.1) |
| 5 | `climb` | The single, first-class climbing state for both ropes and ladders (`15_maps_system/MAP_TRAVERSAL.md` §4) — no separate rope-swing state. Player-only (§5.2). | Loop |
| 6 | `attack` | Physical/weapon damage-dealing clip. Its damage-relevant hit-frame is `ANIMATION_TIMING`'s to fix, not this doc's (§4). | One-shot |
| 7 | `cast` | Magic/skill clip for damage, heal, or buff ops (`10_systems/SKILL_EFFECTS.md`, cast through `10_systems/SKILL_SYSTEM.md`). Same hit-frame note as `attack` (§4). | One-shot |
| 8 | `hit` | Damage-reaction/flinch clip; plays alongside the hitstun window every landed hit applies (`10_systems/COMBAT_FORMULA.md` §11). | One-shot |
| 9 | `die` | Defeat clip. Unconditional top-priority interrupt (§3) — clears every status the instant it is entered (`10_systems/STATUS_EFFECTS.md` §1) and, for the player, gates the `10_systems/DEATH_PENALTY.md` respawn flow. | One-shot |
| 10 | `telegraph` | The wind-up "tell" pose `10_systems/AI_BEHAVIOR.md` §2 requires before an elite/boss committed attack (`40_assets/ART_BIBLE.yaml` `animation.telegraphs`: "boss/elite attacks need a distinct wind-up pose frame") — the fairness read that makes a hard-hitting attack dodgeable. | One-shot |
| 11 | `phase_shift` | Boss-only transition clip entered the instant a `life_threshold_pct` crossing fires (`10_systems/AI_BEHAVIOR.md` §14–15); the boss is invulnerable/untargetable and all statuses/CC suspend for its duration (`10_systems/STATUS_EFFECTS.md` §1). | One-shot |
| 12 | `spawn` | Entrance flourish for an elite/boss zone-spawn or a mid-fight summon (`10_systems/SPAWN.md` §6) — invulnerable/untargetable throughout, so the entrance can't be punished before it's even seen. In addition to, never a replacement for, `telegraph`. | One-shot |

### 1.1 Loop vs. one-shot, precisely

- **Loop** (`idle`, `walk`, `climb`): the clip repeats for as long as the state is active; frame
  count is chosen for a clean repeat, not a fixed duration.
- **One-shot** (the other 9): the clip plays through its frames exactly once per entry and does not
  restart mid-playback; re-entering the state (a second swing, a second hit) restarts it from frame
  0. `jump`/`fall` are the one nuance: with only a 1–2 frame locked budget
  (`40_assets/ART_BIBLE.yaml`), "play through once" and "hold a pose" are functionally the same
  thing — the clip plays its 1–2 frames once, then holds the last frame for as long as the
  rise/descent lasts (a physics duration owned by `15_maps_system/MAP_TRAVERSAL.md` §1, not a
  clip-length one) rather than looping.

## 2. Frame budgets

### 2.1 Locked (9 states — `40_assets/ART_BIBLE.yaml` `animation.frame_budgets`; do not edit)

| Token | Budget | ART_BIBLE key |
|---|---|---|
| `idle` | 2–4 | `animation.frame_budgets.idle` |
| `walk` | 6–8 | `animation.frame_budgets.walk` |
| `jump` | 1–2 | `animation.frame_budgets.jump` |
| `fall` | 1–2 | `animation.frame_budgets.fall` |
| `climb` | 2–4 | `animation.frame_budgets.climb` |
| `attack` | 4–6 | `animation.frame_budgets.attack` |
| `cast` | 4–6 | `animation.frame_budgets.cast` |
| `hit` | 2–3 | `animation.frame_budgets.hit` |
| `die` | 4–6 | `animation.frame_budgets.die` |

These 9 numbers are `meta.status: locked` (owner Agent-3) in `40_assets/ART_BIBLE.yaml` — this doc
cites them and does not restate the reasoning behind any figure.

### 2.2 Proposed extensions (3 states — pending Agent-3 blessing, NOT locked)

`40_assets/ART_BIBLE.yaml` `animation.frame_budgets` predates 3 of this doc's 12 tokens. Since that
file is locked and outside this doc's file ownership, the following is a **proposal**, not a
ruling — flagged for Agent-3 to bless and land as an `40_assets/ART_BIBLE.yaml` `amendments[]`
entry (the file's `amendments[]` list already holds entry AB-001) before Phase D authors assets
against them:

| Token | Proposed budget | Rationale |
|---|---|---|
| `telegraph` | 2–3 | A wind-up "tell" is one held pose read at a glance — shorter than a full `attack`/`cast` (4–6) but needs at least 2 frames to read as a distinct pose rather than a single flash frame, consistent with `animation.telegraphs`'s "distinct wind-up pose" language. |
| `phase_shift` | 4–6 | An authored transition beat, not a hit reaction — budgeted like `attack`/`cast`/`die` rather than the terser `telegraph`/`hit`, long enough to read as a distinct event across an invulnerable window (`10_systems/STATUS_EFFECTS.md` §1). |
| `spawn` | 3–5 | Between `telegraph`'s terseness and `attack`/`cast`'s full budget — an entrance beat needs to read clearly (`10_systems/SPAWN.md` §6's "something dangerous just arrived") without the frame count of a full action clip. |

This is a first-pass proposal only; see Open Questions.

## 3. Interrupt rules

Priority ladder, highest first — a lower-priority state can never preempt a higher one already
playing:

1. **`die`** — unconditional. Entering `die` "exits this machine entirely from any state and clears
   all statuses" regardless of what was playing (`10_systems/AI_BEHAVIOR.md` §1, for monsters;
   `10_systems/DEATH_PENALTY.md` §1 for the player). Nothing below can prevent or outlast a `die`
   entry.
2. **Boss `phase_shift` entry** — a `life_threshold_pct` crossing "interrupts immediately — even
   mid-`windup`/`attack` — rather than waiting for `recover`" (`10_systems/AI_BEHAVIOR.md` §15);
   this cuts off an in-progress `telegraph`/`attack`/`cast` on a boss the instant the threshold is
   crossed. Boss-tier only.
3. **`hit` (heavy class only)** — a **heavy** hit (crit, a `knockback`-carrying skill, or damage
   ≥8% of target max `life`; exact thresholds `10_systems/COMBAT_FORMULA.md` §11, not restated)
   interrupts a `normal`/`elite` monster mid-`cast` unless it is flagged super-armored, and
   interrupts a player mid-`cast` unless the player is in i-frames or under a stability effect
   (`10_systems/COMBAT_FORMULA.md` §11–12). `boss` entities carry super-armor outside
   scripted-vulnerable windows, so `hit` typically layers as a flinch on a boss without canceling
   its `attack`/`cast`/`telegraph`. A **light** hit's shorter hitstun (0.12 s,
   `10_systems/COMBAT_FORMULA.md` §11) is not stated by that doc to force a full clip interrupt —
   treat it as a non-canceling flinch. See Open Questions for this rule's `attack`/`telegraph`
   coverage gap.
4. **Everything else** — ordinary FSM transitions (§3.1); `idle`/`walk` never preempt anything, they
   are simply superseded whenever any other state's entry condition is met.

### 3.1 Per-state cancel notes

- **`climb`**: entered on `climbable`-shape overlap plus held climb input; ends only via its own
  three dismount rules (auto at either end, manual hop, or side-step onto solid ground —
  `15_maps_system/MAP_TRAVERSAL.md` §4) or a higher-priority interrupt above. While active it blocks
  *entry into* `attack`/`cast` outright — "basic attack and the skill bar are disabled in `climb`"
  (`15_maps_system/MAP_TRAVERSAL.md` §4) — the player must dismount first; that is a gate, not a
  cancel. Whether a landed hit itself forcibly dismounts a climbing player is not addressed by any
  doc (Open Questions).
- **`telegraph`/`attack`/`cast`** (a monster's committed `windup`/`attack`): a leash-radius breach
  never interrupts these — "the leash check is suspended for the duration of an already-committed
  `windup`/`attack`" (`10_systems/AI_BEHAVIOR.md` §2) — `return` waits for the clip to finish (or
  for a higher-priority interrupt above).
- **`spawn`/`phase_shift`**: both run under invulnerability/untargetability for their full duration
  (`10_systems/SPAWN.md` §6; `10_systems/STATUS_EFFECTS.md` §1) — nothing damage-based can cut
  either short; they resolve on their own timer (`phase_shift`'s default `phase_shift_duration_s`
  1.5 s, `10_systems/AI_BEHAVIOR.md` §15).
- **`jump`/`fall`**: transition into each other automatically at the arc's apex
  (`15_maps_system/MAP_TRAVERSAL.md` §1); either is preempted by mounting a `climbable` shape
  mid-air, or ends on landing (→ `idle`/`walk`).

## 4. The hit-frame boundary (`attack`/`cast`)

This doc fixes only that `attack`/`cast` are one-shot clips inside the §2 frame budget. **Exactly
which frame** inside that clip fires the damage signal — the "hit-frame" — is `ANIMATION_TIMING`'s
contract, not this doc's: `30_engineering/ENGINEERING_STANDARDS.md` already anchors the coding-pass
convention that "the animation's hit-frame (ANIMATION_TIMING) emits the signal combat listens for —
damage never on a duplicate timer." This doc does not assign a frame index, does not derive one
from `haste` (attack-speed conversion is `10_systems/STATS.md` §5's, and it scales the whole clip's
*playback rate*, not this doc's frame *count* — no reason found here to reopen
`00_vision/GLOSSARY.md`'s closed haste-split question on that basis), and does not restate
`10_systems/SKILL_EFFECTS.md`'s damage-scaling math. Exact per-frame timing lives in
`40_assets/ANIMATION_TIMING.md` (now authored — see Open Questions).

## 5. Required-set matrix (per entity class)

Six entity classes. This is the set `docs/VALIDATION.md` check 6 ("include every state required
for their entity class") enforces. Every row is a **floor, not a ceiling** — an entity may declare
additional states its movement/kit calls for (e.g., `20_schemas/monster.schema.md`'s own worked
example gives an `aggressive_charger` elite both `jump` and `fall` beyond its required set, since
that profile's dash "explicitly ignores edge-avoidance," `10_systems/AI_BEHAVIOR.md` §5); the
validator only fails a *missing* required state, never an extra one.

| Entity class | Required `animation_states` |
|---|---|
| **player** | `idle`, `walk`, `jump`, `fall`, `climb`, `attack`, `cast`, `hit`, `die` — every state except `telegraph`/`phase_shift`/`spawn` (exactly the 9 `40_assets/ART_BIBLE.yaml`-locked states; see Open Questions on where this is validated). |
| **normal mob** | `idle`, `walk`, `attack`, `hit`, `die`, plus `cast` when §5.1 applies. **Exception:** `kamikaze_burster` additionally requires `telegraph` even at `normal` tier (§5.2). |
| **elite** | normal mob's set (§5.1/§5.2 exceptions included) + `telegraph` + `spawn`. |
| **boss** | elite's set + `phase_shift` (see Open Questions on the conflict with `20_schemas/monster.schema.md` rule 8's `enter_telegraph` gating). |
| **summon** | normal mob's set + `spawn` (no `telegraph` — see Open Questions on tier overlap). |
| **npc** | `idle` required; `walk` optional (ambient wander, not yet authored by any doc — see Open Questions). No other token applies: NPCs carry no `stats`/`life` (`20_schemas/npc.schema.md`), so `hit`/`die` never apply, and no NPC has an `ai_profile` or climbs. |

Never required for any monster class: `jump`/`fall`/`climb`. `jump`/`fall` are optional extras for
a ground `ai_profile` whose movement can leave standing ground (a charging dash overshooting an
edge, `10_systems/AI_BEHAVIOR.md` §5; a drop-through while fleeing/converging, §4/§10). `climb`
never applies to any monster — no `ai_profile` in `10_systems/AI_BEHAVIOR.md` §3–14 mounts a
`climbable` shape; climbing is player-only (`15_maps_system/MAP_TRAVERSAL.md` §4).

### 5.1 Cast requirement (all non-player classes)

`cast` is required, in addition to a class's baseline row above, when **either**:

- the entity's `ai_profile` is `ranged_skirmisher` or `support_caller` (`10_systems/AI_BEHAVIOR.md`
  §8/§11 — a projectile windup and a buff/heal cast on an ally, respectively), **or**
- the entity carries `stats.spellpower` (`20_schemas/monster.schema.md`) — i.e., any monster whose
  kit scales on magic, regardless of which of the 12 profiles it uses.

For **boss** (`ai_profile: boss_scripted`, §5.4), evaluate both clauses against every
`phases[].base_profile` in its `phases[]` list (`10_systems/AI_BEHAVIOR.md` §15) as well as the base
entity's own `stats.spellpower` — a boss that ever borrows `ranged_skirmisher`/`support_caller` for
one phase needs `cast` in its set even if its default phase does not.

### 5.2 `kamikaze_burster` telegraph exception

`10_systems/AI_BEHAVIOR.md` §12 states the shared telegraph rule (§2, elite/boss only) has one
named exception: "`kamikaze_burster` always plays `telegraph` before detonating, even at `normal`
tier — an untelegraphed self-destruct would violate [fairness] regardless of monster tier." A
`normal`-tier `kamikaze_burster` therefore requires `telegraph` despite being `normal` — the one way
a `normal`-tier monster is required to carry it. `20_schemas/monster.schema.md` rule 8's
"known-required" list does not currently mention this exception; flagged in Open Questions.

### 5.3 Aerial profiles: `walk` doubles as fly (no new token)

`aerial_swooper` is the only one of the 12 `ai_profile`s that is airborne — it "ignores
ground/platform collision entirely at `patrol_altitude`" (`10_systems/AI_BEHAVIOR.md` §9). Rather
than add a `fly` token, an aerial-profile monster's `walk` clip **doubles as its patrol/chase
flight-loop**. This mirrors the precedent `15_maps_system/MAP_TRAVERSAL.md` §7 already sets for
`water_physics` maps — underwater movement "plays ordinary `jump`/`fall`/`walk` at the modified
curve" rather than adding a `swim` token, because "the 12-state `00_vision/GLOSSARY.md` set is
fixed and final." An aerial-profile monster's required set is otherwise identical to its class row
above; it needs no `jump`/`fall` (its only ground-relative moment is the dive `attack`, and its
climb-back `10_systems/AI_BEHAVIOR.md` §9 `recover` reads through `walk`, not a platforming rise).

### 5.4 Boss class notes

This matrix assumes every `tier: boss` monster uses `ai_profile: boss_scripted` and therefore
carries a `phases[]` list to evaluate §5.1 against; `20_schemas/monster.schema.md` validates `tier`
and `ai_profile` independently and does not hard-link them (flagged in Open Questions). Separately,
this matrix requires `phase_shift` **unconditionally** for every `boss`, whereas
`20_schemas/monster.schema.md` rule 8 today only requires it "when any phase sets
`enter_telegraph: true`" — a narrower, per-phase gate. This doc treats `phase_shift` as a baseline
boss-class asset (every boss has at least one phase transition; the state should exist whether or
not a specific phase also flags the extra `enter_telegraph` flourish) rather than an opt-in; the
conflict with that schema's current wording is flagged in Open Questions, not resolved by editing
that file here.

## 6. Export naming

Every one of the 12 states follows `40_assets/ART_BIBLE.yaml`'s `export_contract.frame_naming`
pattern verbatim: `{entity_id}_{state}_{NN}` (`NN` = 2-digit, zero-based). `{state}` is always one
of the exact 12 GLOSSARY tokens (§1) — never an abbreviation or synonym. `{entity_id}` is the
owning content file's immutable `id`:

- Monster (any tier, including summon templates): `mob_NNN` (`docs/ID_REGISTRY.md`).
- NPC: `npc_NNN` (`docs/ID_REGISTRY.md`).
- Player: no `entity_id` token is registered anywhere in the tree today — see Open Questions.

`NN` indexes `0` .. `count-1` for whichever frame count the asset actually authors inside its
state's locked (§2.1) or proposed (§2.2) `[min, max]` budget — the budget is a range Phase D/asset
authors choose within, not a fixed count; e.g., an `attack` clip authored at 5 frames (inside the
locked `[4,6]`) exports `..._attack_00` through `..._attack_04`, never `_05`.

Examples: `mob_010_telegraph_00`, `mob_010_telegraph_01` (a 2-frame clip, within the §2.2 proposed
`[2,3]`); `npc_002_idle_00`, `npc_002_idle_01` (a 2-frame clip, the low end of the locked `[2,4]`).

## Open Questions

- **Extension budgets need Agent-3's blessing.** The proposed `telegraph` [2,3], `phase_shift`
  [4,6], and `spawn` [3,5] frame budgets (§2.2) are this doc's first-pass proposal only —
  `40_assets/ART_BIBLE.yaml` is locked and outside this doc's file ownership, so these three cannot
  be treated as canon until Agent-3 blesses them and lands them in that file's own `amendments[]`
  list (which already contains entry AB-001, for the terrain-model change — not these three). Phase
  D should not author `telegraph`/`phase_shift`/`spawn` frame counts against these numbers until
  that happens.
- **`20_schemas/monster.schema.md` rule 8 needs reconciling with this doc on three points**, now
  that `40_assets/ANIMATION_STATES.md` has landed as the "authority on the full per-class set" that
  rule 8 itself deferred to: (a) it gates `phase_shift`'s presence on
  `phases[].enter_telegraph: true` per-phase, while this doc requires it unconditionally for every
  `boss` (§5.4); (b) it does not hard-link `tier: boss` to `ai_profile: boss_scripted`, which this
  doc's boss row assumes (§5.4); (c) its "known-required" list omits the `kamikaze_burster`
  normal-tier `telegraph` exception (`10_systems/AI_BEHAVIOR.md` §12, this doc's §5.2). None of
  these are resolved here — flagged for that schema's owner.
- **Summon vs. tier overlap.** This doc's `summon` row is keyed off
  `20_schemas/monster.schema.md`'s `summon_owner` field, independent of `tier`. Whether an elite- or
  boss-caliber summon template (`tier: elite`/`boss` *and* `summon_owner` both set) must satisfy the
  union of its tier row and the summon row (e.g., still needing `telegraph`), or whether
  `summon_owner` presence caps it at the summon row regardless of tier, is not resolved by that
  schema's single-axis `tier` field. Not decided here.
- **Player has no registered `entity_id` or content schema.** `40_assets/ART_BIBLE.yaml`
  `export_contract.frame_naming` needs `{entity_id}_{state}_{NN}` for the player exactly as it does
  for `mob_NNN`/`npc_NNN`, but no ID prefix exists for the player character anywhere in the tree
  (`00_vision/GLOSSARY.md`'s ID-prefix list has none) and no `player.schema.md` exists.
  Consequently the player row in §5 is a spec for the Phase E coding pass
  (`30_engineering/ENGINEERING_STANDARDS.md`, `60_agents/`), not a Phase D `animation_states`-field
  check the way `docs/VALIDATION.md` check 6 currently runs for monsters — flag whether the player
  needs its own schema/ID block, or whether the job-line tokens
  (`bulwark`/`keeneye`/`weaver`/`flicker`) double as the export `entity_id`.
- **`20_schemas/npc.schema.md` has no `animation_states` field at all.** This doc's `idle`
  required/`walk` optional NPC row has nothing to attach to today — that schema defines no
  `animation_states`, `ai_profile`, or movement field, and (consistent with this doc's exemption) no
  `stats`/`life` field either. Recommend either an `npc.schema.md` revision adding the field so
  `docs/VALIDATION.md` check 6 can actually run against `npc_NNN.yaml` files, or an explicit
  decision that NPCs are exempt from check 6 by design. Not decided here.
- **Heavy-hit interrupt wording covers `cast` only.** `10_systems/COMBAT_FORMULA.md` §11 states a
  heavy hit interrupts a monster/player mid-`cast`; it does not say whether the same applies
  mid-`attack` or mid-`telegraph`. This doc's §3 interrupt ladder assumes parity across all three
  one-shot action clips but does not invent the rule where `COMBAT_FORMULA.md` is silent — confirm
  with that doc's owner.
- **Hit vs. climb is unaddressed.** Neither `15_maps_system/MAP_TRAVERSAL.md` §4 nor
  `10_systems/COMBAT_FORMULA.md` §11–12 states whether a landed hit forcibly dismounts a climbing
  player into `hit`/`fall`, or whether damage is simply absorbed without interrupting `climb`. Not
  assumed either way here.
- **`ANIMATION_TIMING` does not exist in the tree yet.** This doc's hit-frame boundary (§4) defers
  exact per-frame damage timing to `ANIMATION_TIMING`, per
  `30_engineering/ENGINEERING_STANDARDS.md`'s existing citation of it — **resolved:** both
  `40_assets/ANIMATION_TIMING.md` and `40_assets/SKILL_ANIMATION.md` now exist (Phase C
  checkpoint + the consistency wave); hit-frame-accurate combat has its contracts.
- **Monster tier-count discrepancy (112/23/15 vs 118/24/8) — resolved at the v2 straggler
  wave, and the counts have since moved again with v3:** `20_schemas/monster.schema.md`'s
  Purpose section matches `docs/ID_REGISTRY.md`; the current v3 split is **178/45/11**
  (normal/elite/boss), and Phase D budgets **11** `boss` asset sets.
- **No evade/dodge visual (owner request, 2026-07-24).** A monster's successful `evasion` roll
  (`10_systems/COMBAT_FORMULA.md` §13 stat; the owner's "monsters have a % to dodge") currently
  has **no dedicated clip** — the 12-state set is closed, so the miss is presentation-only
  (floating-text feedback is `10_systems/HUD.md`'s domain). If evasive monsters (e.g. high-`evasion`
  Flicker-flavored mobs) should visibly sidestep, that is a 13th state (`evade`) or a reuse rule
  (e.g. play `hit` mirrored without flinch frames) — either way it is this doc's closure to amend,
  with a frame budget needing Agent-3's ART_BIBLE blessing like the other extension states. Not
  decided here; `animation_notes` (`20_schemas/monster.schema.md` rule 11) must not describe an
  evade clip until it is.
