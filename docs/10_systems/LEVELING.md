# LEVELING.md — Experience Curve, Kill Rewards & Level-Up

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/COMBAT_FORMULA.md, 10_systems/STATS.md, 10_systems/SKILL_SYSTEM.md,
10_systems/QUESTS.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/social/PARTY.md, 10_systems/social/PARTY_QUEST.md, 10_systems/ITEMS.md,
10_systems/ENHANCEMENT.md, 10_systems/SCROLLS.md, 10_systems/PERSISTENCE.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the `exp`→`level` curve, the per-kill `exp` reward guideline, the `exp` source split
policy, and what a level-up grants. Combat math, monster stat budgets, and the **level-difference
dampener curve** live in `10_systems/COMBAT_FORMULA.md`; primary/derived stat growth lives in
`10_systems/STATS.md`; skill-point spending in `10_systems/SKILL_SYSTEM.md`. This doc consumes
those and never restates them. The game cap is **300 (initial design, `00_vision/SCOPE.md`)**;
the curve is formula-first and extends to any level. This run authors content to **Lv 42**
(`docs/WORLD_PLAN.md`) — no monster in this arc exceeds `level` 42, and leveling past the arc is
a deliberately slow grind (§6).

## 1. The `exp` curve (formula-first; detail table for Lv 1–100)

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

`kills_per_level` grows quadratically, so **early levels are minutes and the 90s are days of
sessions** (P2). The `/played` estimate assumes ≈ 480 at-level kills/hour (one kill per ≈ 7.5 s
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
| 45 | 239,700 | 2,493,061 | 425 | 1.26 h |
| 50 | 336,440 | 3,875,368 | 520 | 1.55 h |
| 55 | 457,500 | 5,789,790 | 625 | 1.86 h |
| 60 | 606,800 | 8,363,327 | 740 | 2.20 h |
| 65 | 787,150 | 11,743,125 | 865 | 2.57 h |
| 70 | 1,002,000 | 16,092,952 | 1,000 | 2.98 h |
| 75 | 1,254,920 | 21,591,578 | 1,145 | 3.41 h |
| 80 | 1,548,300 | 28,436,584 | 1,300 | 3.87 h |
| 85 | 1,888,385 | 36,840,325 | 1,465 | 4.36 h |
| 90 | 2,277,960 | 47,042,044 | 1,640 | 4.88 h |
| 95 | 2,719,250 | 59,290,218 | 1,825 | 5.43 h |
| 99 | 3,112,560 | 70,745,051 | 1,980 | 5.89 h |
| 100 | — (cap) | 73,857,611 | — | — |

**Total to Lv 100: ≈ 73.86 M `exp`, ≈ 201 `/played` hours** — a reference milestone; the curve
continues past 100 by formula toward the 300 cap (future arcs own any retune of that stretch,
see Open Questions). The authored arc's top (Lv 42) sits at ≈ 1.75 M cumulative `exp`.
Intermediate levels: compute from the formula, or linearly interpolate between rows.

### 1.1 Time distribution by band

| Band | Lv 1–10 | Lv 10–30 | Lv 30–60 | Lv 60–90 | Lv 90–100 |
|---|---|---|---|---|---|
| `/played` | 0.7 h | 6.1 h | 38.5 h | 102.2 h | 53.8 h |

The front ten levels are a single evening; the last ten are ≈ 54 hours — the intended long-tail
climb, not a wall (each level stays a legible multiple of the previous, no spikes).

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
Lv 42, the arc top) with no region-boundary jumps.

| `tier` | multiplier | Notes |
|---|---|---|
| `normal` | ×1 | The pacing anchor. |
| `elite` | ×5 | ×6 `life` (COMBAT_FORMULA §13.2) for ×5 `exp` → marginally less `exp/hour` than normals; elites are speed-bumps and drop-density, not `exp` farms. |
| `boss` | ×25 | ×35 `life`; a region `boss` is a progression/loot event, not an `exp/hour` play. |

A **PQ-instanced finale boss** (`10_systems/social/PARTY_QUEST.md` §4) pays this same `boss` ×25
row, split among the party per `10_systems/social/PARTY.md` §4 — party quests reward loot and
story, `exp` is secondary. A future-arc raid tier may mint its own party-shared multiplier; none
exists in this arc.

| Mob Lv | `normal` ×1 | `elite` ×5 | `boss` ×25 |
|---|---|---|---|
| 1 | 4 | 20 | 100 |
| 5 | 32 | 160 | 800 |
| 10 | 80 | 400 | 2,000 |
| 20 | 197 | 985 | 4,925 |
| 30 | 333 | 1,665 | 8,325 |
| 40 | 484 | 2,420 | 12,100 |
| 50 | 647 | 3,235 | 16,175 |
| 60 | 820 | 4,100 | 20,500 |
| 70 | 1,002 | 5,010 | 25,050 |
| 80 | 1,191 | 5,955 | 29,775 |
| 90 | 1,389 | 6,945 | 34,725 |
| 100 | 1,592 | 7,960 | 39,800 |
| 105 | 1,697 | 8,485 | 42,425 |

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

## 6. Beyond the arc — Lv 42 toward the 300 cap (v2)

The game cap is **300 (initial design)**; this arc's authored content tops at Lv 42
(`docs/WORLD_PLAN.md` — Clockwork elites). Between the two there is **no wall**, only a soft
asymptote:

- **The §1 curve keeps applying by formula past the authored range** — nothing special happens at
  Lv 42; there is no arc-level cap flag anywhere in the data.
- **Out-leveling the arc is deliberately slow.** Past ≈ 42 the player out-levels every authored
  monster, so the level-difference dampener (`10_systems/COMBAT_FORMULA.md` §9, applied in §2)
  progressively craters per-kill `exp`. Leveling continues as a slow grind on the Clockwork
  endgame maps and party quests (`10_systems/social/PARTY_QUEST.md`) until future arcs add higher
  bands — the v2 replacement for v1's hard-cap "gear-only" wall.
- **Arc endgame is the gear chase**: T6 weapons at +9 (`10_systems/ENHANCEMENT.md`), boss uniques
  (`10_systems/ITEMS.md` §11), scroll lines (`10_systems/SCROLLS.md`), and the Mainspring Trial.
  You out-gear the arc's endgame; out-leveling it is possible but never the efficient path.
- **Growth systems are specified through Lv 100 today** (`10_systems/STATS.md` §4.2 auto-growth,
  `10_systems/SKILL_SYSTEM.md` point accrual); their extension toward 300 is future-arc design,
  flagged in those docs' Open Questions. At `level` 300 itself `exp` gain simply stops.

Argument against a paragon trickle (unchanged from v1): a paragon stat drip would inflate
primaries past the `10_systems/STATS.md` §4 model that every monster budget
(`10_systems/COMBAT_FORMULA.md` §13) and the authored skill roster are balanced against, forcing
perpetual re-tuning and the exact power-creep economy `00_vision/PILLARS.md` anti-pillars forbid.
Gear-plus-slow-levels keeps the balance surface fixed, routes endgame ambition into the loot loop,
and matches "the grind is cozy, not cruel" (P2). A paragon-style system is explicitly **deferred
to post-launch and is not a launch promise** (tracked in Open Questions as a future
consideration, not an in-scope item).

## Open Questions

- **Post-launch** paragon/prestige track (deferred, §6): if ever pursued, it must not touch the
  §1 base curve or the primary model; a bounded, mostly-horizontal system (cosmetic/`shards`/
  account-wide unlocks) is the only shape compatible with the fixed balance surface. Owner:
  LEVELING.md, post-launch — **not** an in-scope launch item.
- The §1 curve past Lv 100 is a pure formula extension today; when future arcs approach higher
  bands (toward cap 300), this doc owns any retune of that stretch — the authored-arc rows
  (Lv 1–42) stay fixed.
- The ≈ 480 kills/hour pacing assumption folds in travel/aggro downtime that has not been measured;
  if real spawn density (`docs/WORLD_PLAN.md`, map spawn data) diverges, the `/played` estimates
  shift while the `exp_to_next` curve stays fixed. Flagged for the Phase D content pass.
- Quest `exp` totaling exactly 25% per region depends on `10_systems/QUESTS.md` honoring this
  budget; if quest counts per region (`docs/ID_REGISTRY.md`) can't hit 25% cleanly at a given band,
  the residual shifts to hunting (higher `kills_per_level` in practice). Owner: QUESTS.md.
- `exp` at the true cap (Lv 300) is currently discarded (§6); if a "mastery `exp` →
  `shards`/material" conversion is ever wanted as a soft sink, it belongs to
  `10_systems/ECONOMY.md`, not here. Default: discarded (moot until future arcs near the cap).
