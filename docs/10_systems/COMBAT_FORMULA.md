# COMBAT_FORMULA.md — Damage Pipeline, Combat Rules & Monster Stat Budget

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/LEVELING.md, 10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md,
10_systems/AI_BEHAVIOR.md, 10_systems/social/PARTY.md, 10_systems/social/RAID.md,
10_systems/PERSISTENCE.md,
20_schemas/monster.schema.md, 40_assets/ART_BIBLE.yaml, docs/WORLD_PLAN.md

Owner doc for the combat **math**: how the stat values from `10_systems/STATS.md` and a monster's
schema resolve into a damage number, a hit/miss, a crit, knockback, and death timing. Also owns
the **monster stat budget** (the numbers Phase D content copies) and the level-difference dampener
curve. Stat *definitions* are `10_systems/STATS.md`; element multiplier values are
`10_systems/ELEMENTS.md`; status magnitudes are `10_systems/STATUS_EFFECTS.md`. This doc consumes
those; it never restates them.

## 1. The `CombatMath` contract (pure, stateless)

All resolution is a single pure function of two already-computed stat blocks plus the incoming
skill descriptor — no world state, no side effects, server-authoritative
(`00_vision/PILLARS.md` P6; `10_systems/PERSISTENCE.md`). The future implementation is one
stateless class `CombatMath.resolve(attacker, defender, skill, rng) -> HitResult`. Attacker and
defender arrive as **final** stat blocks: every value has already passed the
`10_systems/STATS.md` §7 compute order, so transient `fortify`/`sunder`/`chill`/`empower` effects
are **already folded into** `armor`, `warding`, `haste`, and the offense rating before this
function runs. The pipeline reads final numbers and applies only the two damage-dealt multipliers
that are not stat folds (`empower`, `weaken`; §8).

## 2. Damage pipeline (canonical order)

```
resolve(A, D, skill, rng):
  # 1. HIT CHECK (§3)
  if not roll_hit(A, D, skill, rng):        return MISS (0 damage, floating "miss")
  # 2. IMMUNITY (element ×0, ELEMENTS §2)
  if skill.element in D.immune_to:          return IMMUNE (0 damage, floating "immune")
  # 3. BASE
  offense = D_is_magic(skill) ? A.spellpower : A.power     # skill declares; SKILL_SYSTEM
  raw     = offense * skill.coefficient                    # basic attack coefficient = 1.0
  # 4. MITIGATION (§5) — pick armor vs warding by element split (ELEMENTS §3)
  defstat = attuned(skill.element) ? D.warding : D.armor
  raw    *= K(D.level) / (K(D.level) + defstat)
  # 5. ELEMENT MULTIPLIER (ELEMENTS §2): ×0.5 / ×1.0 / ×1.5   (×0 handled at step 2)
  raw    *= element_mult(skill.element, D)
  # 6. CRIT (§4)
  crit    = rng.chance(A.crit_rate)
  if crit: raw *= A.crit_power
  # 7. VARIANCE (§7): uniform ±8%
  raw    *= rng.uniform(0.92, 1.08)
  # 8. DAMAGE-DEALT STATUS MULTIPLIERS (§8): empower / weaken on the ATTACKER
  raw    *= A.damage_dealt_mult
  # 9. LEVEL-DIFFERENCE DAMPENER (§9)
  raw    *= damage_diff_mult(A.level - D.level)
  return HIT(max(1, round(raw)), crit)      # a landed, non-immune hit always deals >= 1
```

Steps 4–9 are all multiplicative, so their commutation does not change the result before
rounding; the order above is the canonical one implementers and tests use.

## 3. Hit check (`precision` vs `evasion`)

`precision` is a rating (`10_systems/STATS.md` §2); `evasion` is a percentage (already soft-capped,
STATS §6). Hit chance, in percentage points:

```
PREC_TERM   = clamp((A.precision - 4 * D.level) * 0.05, -25, +25)   # at-level baseline = 4*level
hit_chance  = clamp(BASE_HIT + PREC_TERM - D.evasion - blind_pen, HIT_FLOOR, HIT_CEIL)
blind_pen   = 50 if A has `blind` else 0        # STATUS_EFFECTS §4.1 owns the magnitude
```

| Constant | Value | Rationale |
|---|---|---|
| `BASE_HIT` | 95 | Attacks land by default; misses are readable events, not a math tax (P1). |
| `HIT_FLOOR` | 20 | You can always sometimes connect, even far under-level. |
| `HIT_CEIL` | 99 | A whiff is always possible; hit-frame honesty means a miss is a visible whiff. |
| `4 * level` | — | Expected at-level `precision`; surplus counters high `evasion`/level, deficit hurts. |

`blind` (`10_systems/STATUS_EFFECTS.md`) subtracts a flat 50 points from the blinded attacker's
`hit_chance` (this doc owns the roll; STATUS_EFFECTS owns the "+50% miss" magnitude). A `finesse`
build's surplus `precision` pushes toward `HIT_CEIL`; a `fortune` build's high `evasion` (STATS §6,
soft-cap 25%) is the only meaningful dodge source — monster `evasion` is kept low (§13) so combat
stays responsive.

## 4. Crit roll

`crit_rate` and `crit_power` arrive final and soft-capped from `10_systems/STATS.md` (§2, §6). One
Bernoulli roll at `A.crit_rate`; on success multiply by `A.crit_power` (step 6). Crit is rolled
**after** mitigation and element so it multiplies the real post-defense number. A crit is also a
knockback/hitstun trigger (§11). Snapshotted status DoTs carry the crit decision from their
application tick (`10_systems/STATUS_EFFECTS.md` §1); `CombatMath` is called per-DoT-tick with the
snapshot block.

## 5. Base damage & the mitigation curve

Offense is `power` (physical/`neutral` skills) or `spellpower` (magic skills); the skill declares
which (`10_systems/SKILL_SYSTEM.md`). `raw = offense * skill.coefficient`. Defense is a **curve**,
never flat subtraction, so a point of `armor` never fully cancels a point of `power` and low-damage
hits never floor to zero:

```
mitigation_multiplier = K(L) / (K(L) + defense)          # damage kept
K(L) = 50 + 20 * L        # L = the DEFENDER's level
```

`defense` = `warding` if the skill's element is attuned (`fire`/`frost`/`nature`/`arcane`/`shadow`),
else `armor`, per `10_systems/ELEMENTS.md` §3. Using the **defender's** level for `K` keeps a given
at-level defense rating at a stable damage-reduction band regardless of level: at-level monster
`armor` (`6*L`, §13) yields ≈ 8% reduction at Lv 1 rising to a stable ≈ 22% by Lv 20+. Players see
the same curve on incoming hits (their `armor`/`warding` from STATS vs `K(player.level)`).

## 6. Element multiplier hook

The element factor (×0 immune / ×0.5 resist / ×1.0 / ×1.5 weak) is owned entirely by
`10_systems/ELEMENTS.md` §2, read from the defender's `weak_to`/`resists`/`immune_to` lists
(`20_schemas/monster.schema.md`). ×0 short-circuits at pipeline step 2. **Players carry no affinity
lists** (ELEMENTS §3), so `element_mult` versus a player defender is always 1.0 — player elemental
defense is `warding` only.

## 7. Variance

Final multiply by `rng.uniform(0.92, 1.08)` (±8%). Variance is last among the damage multipliers
and before the level dampener so crits and non-crits share the same spread. It exists for texture,
not swing: ±8% never turns a 3-hit kill into a 4-hit kill at-level.

## 8. Status-modifier hooks

Only two statuses are damage-**dealt** multipliers and thus applied inside the pipeline (step 8),
because they are not stat folds: `empower` (+20% damage dealt) and `weaken` (−25% damage dealt),
both on the **attacker**, magnitudes owned by `10_systems/STATUS_EFFECTS.md` §4. Their product is
`A.damage_dealt_mult`. Every other status reaches `CombatMath` **through the stat block**, already
folded by STATS §7 step 4: `fortify`/`sunder` via `armor`/`warding`, `chill`/`swiftness` via
`haste`, `blind` via §3. DoT ticks (`burn`, `poison`) are ordinary `CombatMath` calls on the
attacker's application-time snapshot; mitigation and element apply to them exactly as to direct
hits (STATUS_EFFECTS §5).

## 9. Level-difference dampener (owner)

Keyed on `d`. This doc owns **both** the damage curve and the exp curve; `10_systems/LEVELING.md`
cites the exp column, never restates it.

**Damage** — `d = attacker.level − defender.level`, multiplies outgoing damage (step 9). Over-level
attackers deal full damage (they should stomp); under-level attackers are throttled versus higher
targets so you can fight up but it is genuinely hard:

| `d` | ≥0 | −1 | −2 | −3 | −4 | −5 | −6 | −7 | −8 | −9 | ≤−10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dmg × | 1.00 | 1.00 | 0.95 | 0.90 | 0.82 | 0.74 | 0.64 | 0.54 | 0.44 | 0.34 | max(0.20, 0.34 − 0.07·(−d−9)) |

**Exp** — `d = player.level − monster.level`, multiplies the base exp reward
(`10_systems/LEVELING.md` §2 applies it). Near-level kills pay full; over-leveling craters exp
(anti-boost); killing up pays a small capped bonus:

| `d` | ≤−6 | −5…−1 | 0 | +1…+5 | +6…+9 | +10…+14 | ≥+15 |
|---|---|---|---|---|---|---|---|
| exp × | 1.10 | 1.00 + 0.02·(−d) | 1.00 | 1.00 − 0.06·d | 0.70 − 0.10·(d−5) | 0.30 − 0.05·(d−9) | 0.05 |

The same monster hitting a low player uses the damage table with `d = monster.level − player.level`
≥ 0 → ×1.00 (full, dangerous). Fighting +10 mobs stacks the 20% hit floor (§3) with ≤0.27 damage —
a deliberate wall, not a lock.

## 10. Attack cadence & `haste` base (delegated from STATS)

`10_systems/STATS.md` §5 owns the `haste` → percentage conversion; the **base cadences** it applies
to are owned here:

| Base | Value | Applied |
|---|---|---|
| `base_attack_interval` | 0.90 s (≈1.11 basic attacks/s) | `effective = 0.90 / (1 + attack_speed%)` |
| `base_move_speed` | 200 px/s (reference) | `effective = 200 · (1 + move_speed%)` |

Skill cast/recovery times override `base_attack_interval` per skill (`10_systems/SKILL_SYSTEM.md`).
`base_move_speed` in px/s is a placeholder pending the tile scale locked by `40_assets/ART_BIBLE.yaml`
(Open Question).

## 11. Knockback & hitstun

Every landed hit applies **hitstun** (a brief action lockout on the target). Hits are classed:

| Class | Trigger | Hitstun | Knockback |
|---|---|---|---|
| Light | default | 0.12 s | none |
| Heavy | crit **or** skill carries `knockback` op (`10_systems/SKILL_EFFECTS.md`) **or** damage ≥ 8% of target max `life` | 0.35 s | impulse (below) |

Heavy knockback base impulse = **(140 px horizontal, 60 px vertical)**, along the attack vector,
scaled by the target's size class (`40_assets/ART_BIBLE.yaml sizing.size_classes`):

| Size | `tiny` | `small` | `medium` | `large` | `boss` |
|---|---|---|---|---|---|
| knockback × | 1.5 | 1.2 | 1.0 | 0.5 | 0.0 (immune) |

A heavy hit **interrupts** a `normal`/`elite` monster mid-`cast` unless it is flagged super-armored;
`boss`/raid entities have super-armor except in scripted-vulnerable windows owned by
`10_systems/AI_BEHAVIOR.md`. `boss`-size knockback ×0 aligns with their CC immunity
(`10_systems/STATUS_EFFECTS.md` §3). Player casts are interrupted by heavy hits unless the player is
in i-frames (§12) or a stability effect applies.

## 12. Player invulnerability frames

On taking any monster damage instance, the player gains **0.40 s of i-frames**: incoming monster
contact, attacks, and status applications deal 0 and apply nothing for the window. i-frames also
attach to `dash`/`leap` and dodge skills (`10_systems/SKILL_EFFECTS.md`). i-frames do **not** cleanse
DoTs already on the player (existing `burn`/`poison` keep ticking) and do **not** apply between ticks
of a single multi-hit player skill against a monster — **monsters do not get i-frames**, so player
combos land fully (P1). The 0.40 s window bounds monster touch/attack stacking (§13) at roughly one
instance per 0.8 s of overlap, preventing stun-lock deaths (P2, "death stings, never deletes an
evening").

## 13. Monster stat budget (LOAD-BEARING — Phase D copies these)

Baseline **normal, at-level** monster stats. Formulas are authoritative; the table is the checksum.
For any level not listed, compute from the formula (preferred) or linearly interpolate between
adjacent rows (≤1% error).

| Column | Formula | Notes |
|---|---|---|
| `life` | `4 · (level + 3)²` | Sets time-to-kill against the §15 DPS curve. |
| `power` / `spellpower` | `6 + 3·level` | Given at parity; a mob attack declares one. Drives touch dmg (§13.1). |
| `armor` / `warding` | `6·level` each (defense budget `12·level`) | Author may reallocate between the two, keeping the **sum** ≈ `12·level`. |
| `precision` | `4·level` | The §3 at-level baseline; a mob at baseline neither over- nor under-hits. |
| `evasion` | `3 + 0.03·level` (%) | Kept low so players rarely miss; dodge is a player-`fortune` fantasy, not a monster one. |

| Lv | `life` | `power`/`spellpower` | `armor` | `warding` | `precision` | `evasion` % |
|---|---|---|---|---|---|---|
| 1 | 65 | 9 | 6 | 6 | 4 | 3.0 |
| 2 | 100 | 12 | 12 | 12 | 8 | 3.1 |
| 3 | 145 | 15 | 18 | 18 | 12 | 3.1 |
| 4 | 195 | 18 | 24 | 24 | 16 | 3.1 |
| 5 | 255 | 21 | 30 | 30 | 20 | 3.2 |
| 6 | 325 | 24 | 36 | 36 | 24 | 3.2 |
| 7 | 400 | 27 | 42 | 42 | 28 | 3.2 |
| 8 | 485 | 30 | 48 | 48 | 32 | 3.2 |
| 9 | 575 | 33 | 54 | 54 | 36 | 3.3 |
| 10 | 675 | 36 | 60 | 60 | 40 | 3.3 |
| 15 | 1295 | 51 | 90 | 90 | 60 | 3.5 |
| 20 | 2115 | 66 | 120 | 120 | 80 | 3.6 |
| 25 | 3135 | 81 | 150 | 150 | 100 | 3.8 |
| 30 | 4355 | 96 | 180 | 180 | 120 | 3.9 |
| 35 | 5775 | 111 | 210 | 210 | 140 | 4.1 |
| 40 | 7395 | 126 | 240 | 240 | 160 | 4.2 |
| 45 | 9215 | 141 | 270 | 270 | 180 | 4.4 |
| 50 | 11235 | 156 | 300 | 300 | 200 | 4.5 |
| 55 | 13455 | 171 | 330 | 330 | 220 | 4.7 |
| 60 | 15875 | 186 | 360 | 360 | 240 | 4.8 |
| 65 | 18495 | 201 | 390 | 390 | 260 | 5.0 |
| 70 | 21315 | 216 | 420 | 420 | 280 | 5.1 |
| 75 | 24335 | 231 | 450 | 450 | 300 | 5.3 |
| 80 | 27555 | 246 | 480 | 480 | 320 | 5.4 |
| 85 | 30975 | 261 | 510 | 510 | 340 | 5.6 |
| 90 | 34595 | 276 | 540 | 540 | 360 | 5.7 |
| 95 | 38415 | 291 | 570 | 570 | 380 | 5.9 |
| 100 | 42435 | 306 | 600 | 600 | 400 | 6.0 |
| 105 | 46655 | 321 | 630 | 630 | 420 | 6.2 |

### 13.1 Touch (body-contact) damage

A monster whose AI permits body contact deals **touch damage = round(0.5 · power)**, element
`neutral` (unless the schema flags an elemental body), on an **0.8 s per-target cadence**, run through
the full §2 pipeline and gated by player i-frames (§12) — so overlap costs the player roughly one
touch instance per 0.8 s. Passive profiles (`passive_wanderer`, `timid_grazer`,
`10_systems/AI_BEHAVIOR.md`) deal **no** touch damage; `boss` bodies deal touch damage only in phases
their script marks contact-hot.

### 13.2 Tier multipliers (applied to the normal baseline of the same level)

| Tier | `life` | `power`/`spellpower` | `armor`/`warding` | `precision` | `evasion` | CC / knockback |
|---|---|---|---|---|---|---|
| `elite` | ×6 | ×1.5 | ×1.3 | ×1.1 | +2% | STATUS_EFFECTS §3 elite row |
| `boss` | ×35 | ×2.0 | ×1.6 | ×1.2 | +0 (bosses don't dodge) | boss row; knockback-immune (§11) |
| raid boss | §13.3 | ×2.5 (fixed) | ×1.8 | ×1.2 | +0 | CC-immune (STATUS_EFFECTS §3) |

Worked checks: elite Lv 30 `life` = 4355×6 ≈ 26 150; boss Lv 60 `life` = 15 875×35 ≈ 555 700; boss
Lv 80 `power` = 246×2 = 492. Region and raid finale bosses (`docs/WORLD_PLAN.md`,
`10_systems/social/RAID.md`) copy the row for their level and phase-tune within it.

### 13.3 Raid-boss party scaling (owner)

The four raid finale bosses (`mob_027`/`mob_150`/`mob_178`/`mob_234`, `10_systems/social/RAID.md`
§2, `docs/WORLD_PLAN.md`) scale `life` with party size `N` **when fought via raid entry**
(`10_systems/social/RAID.md` §3). The same boss soloed through the arena's open (non-raid) entry is
an ordinary region `boss` (§13.2, no `N`-scaling). `10_systems/social/PARTY.md` §6 owns the legal
party range (`3–6`) and how `N` is counted; this doc owns the math:

```
raid_life(N, L) = normal_life(L) · 90 · N          # per-member linear
raid_damage      = normal_power(L) · 2.5           # FIXED — never scaled by N
enrage_timer     = 12 min                           # boss wipes the party on expiry
```

Because both `raid_life` and total party DPS scale linearly in `N`, time-to-kill is essentially
`N`-independent and holds at the §14 midpoint across the whole legal `3–6` range (worked below).
Raid boss `damage` is **not** `N`-scaled — more players means more bodies to cover mechanics, not a
bigger tank check. `N` is **fixed at instance creation** (`10_systems/SPAWN.md` §7,
`10_systems/social/PARTY.md` §6) and never re-scales: if members fall or leave, the survivors face
the full `N`-scaled `life` with reduced live DPS and hit enrage first — which, together with the
3-member entry gate (`10_systems/social/PARTY.md` §6) and boss mechanics, is what enforces the party
requirement, **not** `life` alone. Reference table at Lv 80 (`raid_voidtide` boss `mob_234`, the
highest authored raid boss):

| `N` | `raid_life` | party effective DPS (§15 × `N` × 0.85) | TTK |
|---|---|---|---|
| 3 | 7.44 M | ≈ 15 600 | ≈ 7.9 min |
| 4 | 9.92 M | ≈ 20 800 | ≈ 7.9 min |
| 5 | 12.40 M | ≈ 26 000 | ≈ 7.9 min |
| 6 | 14.88 M | ≈ 31 200 | ≈ 7.9 min |

`N` = 3 (the entry floor) clears in ≈ 7.9 min — inside the §14 6–10 min band with margin under the
12-minute enrage — so the floor needs no retune. Because TTK is `N`-independent at the fixed 0.85
coordination factor, larger parties do **not** clear faster; any real large-party coordination
falloff (Open Questions) only pushes `N` = 6 toward the slow end of the band, never outside it.

## 14. Time-to-kill targets (design contract)

At-level, appropriately geared, solo unless noted. These are the acceptance band for the §13 budget
and the §15 DPS curve; balance retunes toward the **midpoint**, never outside the band.

| Target | TTK band | Midpoint model | Source |
|---|---|---|---|
| normal mob | 3–6 s | 4.5 s (`life` / effective DPS) | §13, §15 |
| `elite` | 20–40 s | ≈ 30 s (×6 `life`, +mitigation/dodging) | §13.2 |
| region `boss` | 2–4 min | ≈ 2.5 min base + phase/mechanic downtime | §13.2 |
| raid finale boss | 6–10 min | ≈ 8 min, any legal party (3–6) | §13.3 |

## 15. Player DPS assumption table (backs §14)

"Effective DPS" = the sustained, post-mitigation single-target damage a correctly-geared at-level
player must output to hit the §14 midpoint; it equals `normal_life(L) / 4.5`. `power_ref` is an
**illustrative** reference offense (`power` or `spellpower`) for an at-level geared player
(`10_systems/STATS.md` formulas + typical gear); `mult m` = effective DPS ÷ `power_ref` is the
combined rotation × `haste` × `crit` × mitigation factor that `10_systems/SKILL_SYSTEM.md` +
`10_systems/ITEMS.md` must collectively deliver (it matures from basic-attack ≈1.0 early to a full
geared rotation ≈5.2 at cap). Load-bearing artifact is `normal_life`; `power_ref`/`m` are the
balance target, not a formula this doc owns.

| Lv | `normal_life` | effective DPS | `power_ref` | `mult m` | TTK |
|---|---|---|---|---|---|
| 1 | 65 | 14 | 15 | 0.94 | 4.5 s |
| 5 | 255 | 57 | 38 | 1.49 | 4.5 s |
| 10 | 675 | 150 | 73 | 2.06 | 4.5 s |
| 20 | 2115 | 470 | 162 | 2.90 | 4.5 s |
| 30 | 4355 | 968 | 277 | 3.49 | 4.5 s |
| 40 | 7395 | 1644 | 418 | 3.93 | 4.5 s |
| 50 | 11235 | 2497 | 585 | 4.27 | 4.5 s |
| 60 | 15875 | 3528 | 778 | 4.53 | 4.5 s |
| 70 | 21315 | 4737 | 997 | 4.75 | 4.5 s |
| 80 | 27555 | 6124 | 1242 | 4.93 | 4.5 s |
| 90 | 34595 | 7688 | 1513 | 5.08 | 4.5 s |
| 100 | 42435 | 9430 | 1810 | 5.21 | 4.5 s |
| 105 | 46655 | 10368 | 1968 | 5.27 | 4.5 s |

Very early mobs (Lv 1–4) may die below 3 s once a player has any active skill; that fast end is
intended tutorial pacing (P2) and stays inside the "snappy" spirit of the band.

## Open Questions

- `base_move_speed` (200 px/s) and `base_attack_interval` (0.90 s) are placeholders until the tile
  scale is locked in `40_assets/ART_BIBLE.yaml`; the `haste` percentages (STATS §5) are scale-free,
  but the px value is not. Owner: COMBAT_FORMULA at the C gate.
- The legal raid party range is confirmed `3–6` (`10_systems/social/PARTY.md` §6,
  `10_systems/social/RAID.md` §3); the §13.3 `raid_life`/DPS model is linear in `N`, so TTK is
  ≈`N`-independent and holds at the §14 midpoint (≈8 min) across the whole 3–6 range (worked in
  §13.3, incl. the `N` = 3 floor). Remaining flag: the fixed **0.85 coordination-efficiency** factor
  is a first-pass assumption; if real large-party coordination falls faster than that, `N` = 6
  drifts toward the slow end of the §14 band. Owner: balance pass with `10_systems/social/PARTY.md`.
- `power_ref`/`mult m` (§15) assume typical gear budgets from `10_systems/ITEMS.md` and skill
  coefficients from `10_systems/SKILL_SYSTEM.md` that are not yet authored; if those land far from
  the reference, retune `mult m` (never `normal_life`). Owner: balance pass, C/D gates.
- Whether the `dirk`/`fortune` double-dip (`10_systems/STATS.md` OQ) needs a `power`-coefficient
  cut is a joint ITEMS/COMBAT_FORMULA call; default keeps STATS's uniform `2·G_phys`.
- Heavy-hit cast interruption versus `normal`/`elite` super-armor flags needs the flag vocabulary
  from `10_systems/AI_BEHAVIOR.md`; default is "interruptible unless flagged."
- Out-of-combat `life`/`essence` regen (resting) inherited from `10_systems/STATS.md` OQ is still
  unowned; propose a short rest rule here or in a dedicated doc. Flagged, not resolved.
