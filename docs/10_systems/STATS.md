# STATS.md — Primary & Derived Stat Definitions

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/DROPS.md, 10_systems/PERSISTENCE.md, 10_systems/ITEMS.md, 10_systems/JOBS.md,
10_systems/LEVELING.md, 10_systems/ENHANCEMENT.md, 10_systems/SKILL_SYSTEM.md,
10_systems/STATUS_EFFECTS.md, 20_schemas/monster.schema.md

Owner doc for the 4 primary stats and 11 derived stats named in `00_vision/GLOSSARY.md`. Defines
their meaning, the formulas that map primaries + `level` + equipment to derived values, the
character growth/allocation model, soft caps, and the compute order. Every symbol here is a
GLOSSARY token; no new stat tokens are introduced. Damage/hit/mitigation *math* that consumes
these values is owned by `10_systems/COMBAT_FORMULA.md`; drop math by `10_systems/DROPS.md`.

## 1. Primary stats

Four primaries, one per job line (`10_systems/JOBS.md`). Each governs one weapon type and leans
into a distinct derived-stat identity.

| Primary | Gloss | Weapon line (GLOSSARY) | Identity lean |
|---|---|---|---|
| `might` | Melee/physical power | `blade` | `power`, plus minor `life` / `armor` (bruiser) |
| `finesse` | Ranged/precision | `bow` | `power`, plus `precision` (accurate striker) |
| `focus` | Spell/essence | `staff` | `spellpower`, plus `essence` / `warding` (caster) |
| `fortune` | Crit / evasion / drop-luck | `dirk` | `crit_rate`, `evasion`, drop-luck (rogue) |

## 2. Derived stats — meaning and formulas

`L` = `level`. `Σx_gear` = summed flat contribution from all equipped items and enhancement
(`10_systems/ITEMS.md`, `10_systems/ENHANCEMENT.md`). Coefficients are first-pass balance
values; the balance owner may retune, but the *shape* (which primary drives which derived) is
locked here.

| Derived | Meaning | Formula | Driver |
|---|---|---|---|
| `life` | Survival pool; 0 = defeat | `120 + 18*L + 3*might + Σlife_gear` | `L`, `might` (minor) |
| `essence` | Skill resource pool | `40 + 4*L + 3*focus + Σessence_gear` | `L`, `focus` |
| `power` | Weapon (physical) attack rating | `W + 2*G_phys + Σpower_gear` | weapon primary `G_phys` |
| `spellpower` | Magic attack rating | `W + 2*focus + Σspellpower_gear` | `focus` (staff) |
| `armor` | Physical defense rating | `Σarmor_gear + floor(might/4)` | gear (+`might` minor) |
| `warding` | Magic defense rating | `Σwarding_gear + floor(focus/4)` | gear (+`focus` minor) |
| `precision` | Accuracy rating (hit input) | `2*L + 2*finesse + Σprecision_gear` | `L`, `finesse` |
| `evasion` | Avoidance (% type) | `3 + 0.06*fortune + Σevasion_gear` | `fortune` |
| `crit_rate` | Critical chance (% type) | `5 + 0.10*fortune + Σcrit_rate_gear` | `fortune` |
| `crit_power` | Critical damage multiplier | `1.5 + 0.002*fortune + Σcrit_power_gear` | `fortune` |
| `haste` | Move + attack speed rating | `Σhaste_gear` | gear only |

Notes:
- `life` and `essence` are pools; every other derived is a rating or percentage.
- `armor`, `warding`, `haste` are primarily **gear** stats (the gear chase), with only a minor
  primary lean on `armor`/`warding` so `might`/`focus` retain a defensive identity.
- How `armor`/`warding` become a damage-reduction percentage is **not** defined here — it is
  `10_systems/COMBAT_FORMULA.md`. This doc defines only the rating value.
- `precision` is the attacker-side hit input; the head-to-head resolution of `precision` vs a
  defender's `evasion` (and level parity) is owned by `10_systems/COMBAT_FORMULA.md`.

### 2.1 `power` / `spellpower` weapon routing

`W` = the equipped weapon's attack value (authored in `10_systems/ITEMS.md`). It routes to
`power` for physical weapons and to `spellpower` for the `staff`. `G_phys` is the physical
weapon's governing primary:

| Weapon line | Governing primary `G_phys` | Feeds |
|---|---|---|
| `blade` | `might` | `power` |
| `bow` | `finesse` | `power` |
| `dirk` | `fortune` | `power` |
| `staff` | — (uses `focus`) | `spellpower` |

The `dirk` line scales `power` off `fortune`, which also feeds `crit_rate`/`crit_power`. This
double-dip is the intended assassin fantasy; balancing it (weapon base `W`, coefficients) is a
`10_systems/COMBAT_FORMULA.md` / `10_systems/ITEMS.md` concern — see Open Questions.

## 3. `fortune` hooks: crit, evasion, drop-luck

`fortune` is the single luck stat. Its three hooks:
- **`crit_rate`**: `+0.10%` per point (see §2 formula), then soft-capped (§6).
- **`evasion`**: `+0.06%` per point (see §2 formula), then soft-capped (§6).
- **drop-luck**: exposes `fortune_drop_bonus% = 0.05 * fortune` (linear, uncapped here) to
  `10_systems/DROPS.md`. This doc defines only the **hook value**; whether/how DROPS applies it
  to rarity weights and whether DROPS caps it is owned entirely by `10_systems/DROPS.md`.

## 4. Base values, growth, and allocation

### 4.1 Level-1 base (`novice`, pre-gear, pre-free-points)

| `might` | `finesse` | `focus` | `fortune` |
|---|---|---|---|
| 5 | 5 | 5 | 5 |

### 4.2 Automatic per-level growth

Applied on each level-up. `novice` (Lv 1–7) grows evenly; from the 1st advancement (Lv 8,
`10_systems/JOBS.md`) the job's **main** primary grows fastest.

| Tier | Applies on reaching | Main primary | Each off-primary |
|---|---|---|---|
| `novice` | Lv 2–8 | +1 (all four equal) | +1 |
| advanced | Lv 9+ (to cap 300, formula-first) | +3 | +1 |

Cumulative auto-growth for a main primary at level `L≥9`: `5 + 7 + 3*(L-8)`. For an off-primary:
`5 + 7 + 1*(L-8)`. The formulas run to the level cap of 300 (`00_vision/SCOPE.md`) with no band
change; this run's authored content spans the Lv 1–42 arc, and future arcs inherit the same curve
(`10_systems/LEVELING.md` §6).

### 4.3 Free allocation pool (hybrid model)

In addition to auto-growth, each level-up grants **+2 free points** to spend across the four
primaries — formula-first, `2·(L−1)` lifetime points at level `L` (82 by the arc's end at Lv 42,
continuing to cap 300). Free points are **reallocatable** at a town NPC for a `shards`
fee (`10_systems/LEVELING.md` / `ECONOMY.md` own the fee).

**Model decision — hybrid (auto-growth + small reallocatable pool).** Auto-growth guarantees
every character a strong main primary and viable pools no matter how points are spent, so no
build is a trap (`00_vision/PILLARS.md` P2). The free pool is small enough that it never
dominates a derived stat yet large enough to express a build, and because it is reallocatable
for `shards` no choice is permanent. Manual-only would allow trap builds; auto-only would be
inert — hybrid avoids both.

### 4.4 Sample scaling (main = `might`, auto-growth only, no gear, no free points)

Illustrates the primary-driven portion; add `W`/`Σ*_gear` for real characters.

| Level | main `might` | off primaries | `life` | `essence` (off `focus`) | `power` (2×`might`) |
|---|---|---|---|---|---|
| 1 | 5 | 5 | 153 | 59 | 10 (+`W`) |
| 8 | 12 | 12 | 300 | 108 | 24 (+`W`) |
| 10 | 18 | 14 | 354 | 122 | 36 (+`W`) |
| 25 | 63 | 29 | 759 | 227 | 126 (+`W`) |
| 42 | 114 | 46 | 1218 | 346 | 228 (+`W`) |

Rows stop at the arc's end (Lv 42); beyond it the §4.2 formulas extrapolate unchanged toward
cap 300 (formula-only — no authored content or sample rows past the arc).

## 5. `haste` conversion (single combined rating)

`haste` stays **one rating** per GLOSSARY default; it converts to two percentages applied to
base move and attack cadence (base cadences owned by `10_systems/COMBAT_FORMULA.md`):

| Output | Pre-cap conversion |
|---|---|
| move-speed bonus % | `0.10 * haste` |
| attack-speed bonus % | `0.15 * haste` |

Both outputs are then soft-capped (§6). No strong reason was found to split `haste` into
separate tokens (see Open Questions) — kept combined.

## 6. Soft caps / diminishing returns (percentage-type stats)

Applied to `crit_rate`, `evasion`, and both `haste` outputs after the §2/§5 raw value is
computed. For raw value `R`, soft cap `S`, hard cap `H`:

```
effective = R                          if R <= S
effective = min(H, S + (R - S) * 0.5)  if R >  S
```

| Output | Base | Soft cap `S` | Above-soft rate | Hard cap `H` |
|---|---|---|---|---|
| `crit_rate` | 5% | 50% | ×0.5 | 75% |
| `evasion` | 3% | 25% | ×0.5 | 50% |
| `haste` → move-speed % | 0% | 30% | ×0.5 | 50% |
| `haste` → attack-speed % | 0% | 40% | ×0.5 | 75% |

`crit_power` is a **multiplier**, not a percentage: it has no soft cap and is bounded only by the
per-slot `crit_power` gear budget in `10_systems/ITEMS.md`. `precision` is a rating (no cap
here; `10_systems/COMBAT_FORMULA.md` governs its effect). Rationale (P1, readable): soft caps
bite only when stacking gear past the intended band, keeping percentages legible and preventing
`crit_rate`/`evasion`/`haste` from trivializing content.

## 7. Compute order and status interaction

A character's stats resolve in this order (server-authoritative, §8):
1. **Primaries** = base (§4.1) + auto-growth (§4.2) + free pool (§4.3) + equipment flat primary
   bonuses + enhancement (`10_systems/ENHANCEMENT.md`).
2. **Derived** = §2 formulas on the final primaries + `level` + equipment flat derived bonuses.
3. **Soft/hard caps** (§6) applied to `crit_rate`, `evasion`, `haste` outputs.
4. **Transient status modifiers** from `10_systems/STATUS_EFFECTS.md` (`empower`, `fortify`,
   `swiftness`, `weaken`, `sunder`, `chill`, …) applied last. Percentage hard caps in §6 are
   **re-clamped** after this step, so a `swiftness` buff cannot exceed the attack-speed hard cap.

## 8. Stat authority (server-authoritative)

All of §7 is recomputed **server-side** in the eventual live build; the solo client's values are
advisory and may be overridden by the server on sync. No system may treat client-computed derived
stats as truth (`00_vision/PILLARS.md` P6). The authoritative recompute contract and the
client/server boundary are owned by `10_systems/PERSISTENCE.md`.

## Open Questions

- `haste` split into separate move-speed and attack-speed tokens: **resolved — kept combined**
  (GLOSSARY default; no balance reason found). Reopen only if attack-speed animation breakpoints
  later require independent control; owner STATS.md.
- `dirk`/`fortune` double-dip (`power` + `crit_rate` + `crit_power` from one primary) may need a
  lower `power` coefficient or lower weapon base `W`. Owner: `10_systems/COMBAT_FORMULA.md` +
  `10_systems/ITEMS.md`; default keeps the uniform `2*G_phys` coefficient.
- Free-pool size (+2/level) and the reallocation `shards` fee are first-pass; owners
  `10_systems/LEVELING.md` / `ECONOMY.md` may tune.
- Passive out-of-combat `life`/`essence` regeneration (resting) is not defined here; propose
  ownership by `10_systems/COMBAT_FORMULA.md` or a dedicated rest rule. Flagged.
- Exact `armor`/`warding` → damage-reduction curve and `precision`-vs-`evasion` hit resolution
  are `10_systems/COMBAT_FORMULA.md`'s; confirm the boundary at the B gate.
- Post-arc growth (Lv 42+ on current content): auto-growth runs formula-first to cap 300 (§4.2),
  but whether future arcs adjust the +3/+1 deltas or add new bands is a future-arc decision.
  Owner: `10_systems/LEVELING.md` (§6 past-arc pacing).
