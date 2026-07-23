# LEVELING.md — Experience Curve, Kill Rewards & Level-Up

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/COMBAT_FORMULA.md, 10_systems/STATS.md, 10_systems/SKILL_SYSTEM.md,
10_systems/QUESTS.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/social/PARTY.md, 10_systems/PERSISTENCE.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md

Owner doc for the `exp`→`level` curve, the per-kill `exp` reward guideline, the `exp` source split
policy, and what a level-up grants. Combat math, monster stat budgets, and the **level-difference
dampener curve** live in `10_systems/COMBAT_FORMULA.md`; primary/derived stat growth lives in
`10_systems/STATS.md`; skill-point spending in `10_systems/SKILL_SYSTEM.md`. This doc consumes
those and never restates them. Level cap is **300** (initial design, `00_vision/SCOPE.md`); this
run authors the **first arc**, Lv 1–42 (Clockwork elites top out at 42, `docs/WORLD_PLAN.md`).
The curve is designed formula-first to 300 with detail tables for the authored range; §6 covers
leveling past the arc.

## 1. The `exp` curve (Lv 1 → 300, formula-first)

Two coupled formulas define pacing. The first is the per-level requirement; the second (§3) is the
per-kill reward. They are bound so that **`exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L)`**
— i.e., the number of at-level `normal` kills to earn a level equals `kills_per_level(L)` exactly
(at 100% hunting), tying the curve directly to the time-to-kill contract
(`10_systems/COMBAT_FORMULA.md` §14).

```
exp_to_next(L)       = exp_per_kill_normal(L) · kills_per_level(L)      # exp to go L -> L+1
kills_per_level(L)   = round(20 + 0.20 · L²)     # at-level normal kills to level (100% hunting)
exp_per_kill_normal(L) = round(4 · L^1.3)        # §3, base per-kill reward
cumulative_total(L)  = Σ exp_to_next(i), i = 1..L-1
```

`kills_per_level` grows quadratically, so **early levels are minutes and the curve's deep end is
days of sessions** (P2). The `/played` estimate assumes ≈ 480 at-level kills/hour (one kill per ≈ 7.5 s
including travel/aggro, `10_systems/COMBAT_FORMULA.md` §14) and that **hunting supplies 70% of
`exp`** (§4), so pure-hunting kills = `0.70 · kills_per_level`.

| Lv→+1 | `exp_to_next` | `cumulative_total` @ Lv | kills/level | est. `/played` |
|---|---|---|---|---|
| 1 | 80 | 0 | 20 | 0.06 h |
| 2 | 210 | 80 | 21 | 0.06 h |
| 3 | 374 | 290 | 22 | 0.07 h |
| 4 | 552 | 664 | 23 | 0.07 h |
| 5 | 800 | 1,216 | 25 | 0.07 h |
| 6 | 1,107 | 2,016 | 27 | 0.08 h |
| 7 | 1,500 | 3,123 | 30 | 0.09 h |
| 8 | 1,980 | 4,623 | 33 | 0.10 h |
| 9 | 2,520 | 6,603 | 36 | 0.11 h |
| 10 | 3,200 | 9,123 | 40 | 0.12 h |
| 15 | 8,775 | 34,596 | 65 | 0.19 h |
| 20 | 19,700 | 97,673 | 100 | 0.30 h |
| 25 | 38,135 | 229,270 | 145 | 0.43 h |
| 30 | 66,600 | 472,105 | 200 | 0.60 h |
| 35 | 107,855 | 881,837 | 265 | 0.79 h |
| 40 | 164,560 | 1,527,517 | 340 | 1.01 h |
| 41 | 178,000 | 1,692,077 | 356 | 1.06 h |
| 42 | 192,468 | 1,870,077 | 373 | 1.11 h |

**Arc total (Lv 1 → 42): ≈ 1.87 M `exp`, ≈ 17 `/played` hours.** Detail rows stop at the arc's
end; beyond Lv 42 the same formulas run **formula-first to cap 300** with no authored rows —
Lv 42→300 is future-arc pacing, deliberately slow on current content (§6). Intermediate levels:
compute from the formula, or linearly interpolate between rows.

### 1.1 Time distribution by band (authored arc)

| Band | Lv 1–10 | Lv 10–20 | Lv 20–30 | Lv 30–42 |
|---|---|---|---|---|
| `/played` | 0.7 h | 1.9 h | 4.2 h | 9.8 h |

The front ten levels are a single evening; the arc's final band (Lv 30–42) is ≈ 10 hours — the
long-tail climb begins inside the arc and continues past it (§6), with each level a legible
multiple of the previous, no spikes.

## 2. Applying rewards: base × dampener

```
exp_awarded = round( base_exp(mob) · exp_diff_mult(player.level − mob.level) )
base_exp(mob) = exp_per_kill_normal(mob.level) · tier_mult(mob.tier)
```

`exp_diff_mult` is the **exp column of the level-difference dampener owned by
`10_systems/COMBAT_FORMULA.md` §9** — full near-level, a small capped bonus (≤ ×1.10) for killing
up, and a crater toward ×0.05 for over-leveled ("gray") kills (anti-boost). It is keyed on
`player.level − mob.level`. This doc does **not** restate that curve; it only names where it applies.

## 3. Per-kill `exp` rewards & tier multipliers

Base reward is by **monster** `level`, `exp_per_kill_normal(L) = round(4·L^1.3)`, scaled by tier.
Because reward and the §1 curve share this term, `exp/hour` stays smooth across regions: at-level
`exp/hour ≈ 480 · exp_per_kill_normal(L)`, rising steadily (≈ 1.9 K/h at Lv 1 → ≈ 248 K/h at
Lv 42, the arc's end) with no region-boundary jumps.

| `tier` | multiplier | Notes |
|---|---|---|
| `normal` | ×1 | The pacing anchor. |
| `elite` | ×5 | ×6 `life` (COMBAT_FORMULA §13.2) for ×5 `exp` → marginally less `exp/hour` than normals; elites are speed-bumps and drop-density, not `exp` farms. |
| `boss` | ×25 | ×35 `life`; a region `boss` is a progression/loot event, not an `exp/hour` play. Boss `exp` earned in a party splits per `10_systems/social/PARTY.md`. |

| Mob Lv | `normal` ×1 | `elite` ×5 | `boss` ×25 |
|---|---|---|---|
| 1 | 4 | 20 | 100 |
| 5 | 32 | 160 | 800 |
| 10 | 80 | 400 | 2,000 |
| 20 | 197 | 985 | 4,925 |
| 30 | 333 | 1,665 | 8,325 |
| 40 | 484 | 2,420 | 12,100 |
| 42 | 516 | 2,580 | 12,900 |

The table stops at Lv 42 — the highest authored monsters are the Clockwork elites (Lv 40–42,
`docs/WORLD_PLAN.md`); higher rows are formula-only until future arcs author them.

## 4. `exp` source split policy

Target mix of where a level's `exp` comes from, so no single activity is mandatory (P2) and the
world stays a hunt-and-hangout loop (P3):

| Source | Target share | Owner of the budget |
|---|---|---|
| Hunting (monster kills) | ≈ 70% | This doc (§1–§3). |
| Quests | ≈ 25% | `10_systems/QUESTS.md` (per-quest `exp` budgets **cite this doc**; a region's quest `exp` should total ≈ 25% of the `exp` to clear that region's level band). |
| Other (first-clear, bestiary, exploration) | ≈ 5% | Small one-time grants; owners `10_systems/DROPS.md` / map & bestiary systems. |

The 70% hunting share is what the §1 `/played` estimate is built on (pure-hunting kills =
`0.70 · kills_per_level`). If a region's quests over- or under-shoot 25%, its effective pace drifts
from the table — `10_systems/QUESTS.md` is responsible for staying in budget, citing these numbers.

## 5. Level-up rewards

On reaching a new `level`, atomically (server-authoritative, `10_systems/PERSISTENCE.md`):

| Reward | Value | Owner |
|---|---|---|
| `life` / `essence` refill | both pools set to full (a level-up is also a heal) | pools defined `10_systems/STATS.md` §2 |
| Primary auto-growth | main +3 / off +1 (advanced), or +1 all (novice) | `10_systems/STATS.md` §4.2 — cited, not restated |
| Free allocation points | +2, reallocatable for `shards` | `10_systems/STATS.md` §4.3 |
| Skill points | granted per the job progression | `10_systems/SKILL_SYSTEM.md` — cited, not restated |

This doc owns only the **refill-on-level** rule and the trigger; the magnitudes of growth, free
points, and skill points are owned by STATS and SKILL_SYSTEM. The level-difference **exp** dampener
that gates how much a kill contributes toward the next level is `10_systems/COMBAT_FORMULA.md` §9
(§2 above).

## 6. Past-arc leveling (Lv 42+) — slow grind by design (SCOPE Open Question, RESOLVED)

`00_vision/SCOPE.md`'s open question ("post-cap progression: paragon trickle, gear-only, or nothing
at launch? — owner LEVELING.md") is **resolved here: no paragon/overflow track.** The `level`
curve runs formula-first to cap **300**, but this run authors content only to Lv 42, so past the
arc:

- **Leveling continues on the §1 formulas, deliberately slowly.** The highest authored monsters
  are the Clockwork elites (Lv 40–42) and the deep Sunken/Clockwork maps; a character past Lv 42
  earns increasingly dampened `exp` on them (`10_systems/COMBAT_FORMULA.md` §9, over-leveled
  direction) while `exp_to_next` keeps growing. Grinding toward 300 on current content is
  possible but intentionally not the point — future arcs raise the authored band.
- **Endgame is the gear chase + party quests.** The loop past the arc is gear and enhancement
  (`10_systems/ITEMS.md`, `10_systems/ENHANCEMENT.md`), the two party quests (`pq_undervault`,
  `pq_mainspring` — owner `10_systems/social/PARTY_QUEST.md`), and the 8 regional bosses; `exp`
  is secondary there. Kill rewards stay meaningful for drops and `shards`
  (`10_systems/DROPS.md`, `10_systems/ECONOMY.md`).
- **Primary auto-growth continues** (+3 main / +1 off per level, `10_systems/STATS.md` §4.2,
  formula-first to cap). At `level` 300 (cap), `exp` gain stops applying to `level`.

Argument against a paragon trickle: a paragon stat drip would inflate primaries past the
`10_systems/STATS.md` §4 model that every monster budget (`10_systems/COMBAT_FORMULA.md` §13) and
all 56 skills are balanced against, forcing perpetual re-tuning and the exact power-creep economy
`00_vision/PILLARS.md` anti-pillars forbid. The formula-first curve keeps the balance surface
fixed, routes past-arc ambition into the loot loop and party quests, and matches "the grind is
cozy, not cruel" (P2). A paragon-style system is explicitly **deferred to post-launch and is not
a launch promise** (tracked in Open Questions as a future consideration, not an in-scope item).

## Open Questions

- **Post-launch** paragon/prestige track (deferred, §6): if ever pursued on the road to cap 300,
  it must not touch the §1 base curve or the primary model; a bounded, mostly-horizontal system
  (cosmetic/`shards`/account-wide unlocks) is the only shape compatible with the fixed balance
  surface. Owner: LEVELING.md, post-launch — **not** an in-scope launch item.
- Party `exp` split mechanics (even vs contribution-weighted) and the party `exp`-share radius are
  owned by `10_systems/social/PARTY.md`; party-quest reward handling is
  `10_systems/social/PARTY_QUEST.md`'s. Confirm at the B gate.
- The ≈ 480 kills/hour pacing assumption folds in travel/aggro downtime that has not been measured;
  if real spawn density (`docs/WORLD_PLAN.md`, map spawn data) diverges, the `/played` estimates
  shift while the `exp_to_next` curve stays fixed. Flagged for the Phase D content pass.
- Quest `exp` totalling exactly 25% per region depends on `10_systems/QUESTS.md` honoring this
  budget; if quest counts per region (`docs/ID_REGISTRY.md`) can't hit 25% cleanly at a given band,
  the residual shifts to hunting (higher `kills_per_level` in practice). Owner: QUESTS.md.
- `exp` at cap is currently discarded (§6); if a "mastery `exp` → `shards`/material" conversion is
  ever wanted as a soft sink, it belongs to `10_systems/ECONOMY.md`, not here. Default: discarded.
