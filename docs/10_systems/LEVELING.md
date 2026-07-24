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
those and never restates them. The game's level cap is **300 (initial design, `00_vision/SCOPE.md`)**;
this run authors the **first arc, Lv 1–42**, and publishes the curve through Lv 100 (owner-ratified
pacing anchors, `memory.md` Decision Contract C3 as amended by the **C3′ pacing amendment** — the
owner ruled C3's pace too fast and re-tabled `kills_per_level`; C3′ is binding and supersedes C3's
anchors). The Lv 100–300 tail segment law is a future-arc Open Question (§6).

## 1. The `exp` curve (arc Lv 1 → 42; published anchors through Lv 100)

Two coupled formulas define pacing. The first is the per-level requirement; the second (§3) is the
per-kill reward. They are bound so that **`exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L)`**
— i.e., the number of at-level `normal` kills to earn a level equals `kills_per_level(L)` exactly,
tying the curve directly to the time-to-kill contract (`10_systems/COMBAT_FORMULA.md` §14).

```
exp_to_next(L)         = exp_per_kill_normal(L) · kills_per_level(L)    # exp to go L -> L+1
kills_per_level(L)     = round(20 + 6.6 · L + 0.2 · L²)   # at-level normal kills to level (C3′)
exp_per_kill_normal(L) = round(4 · L^1.3)        # §3, base per-kill reward
cumulative_total(L)    = Σ exp_to_next(i), i = 1..L-1
```

`kills_per_level` grows with a linear-plus-quadratic term (C3′), so **early levels are minutes and the
high levels are days of sessions** (P2). The **canonical played-time model** (`memory.md` C3, kills
coefficient amended by C3′): a level's `/played` hours =
`kills_per_level(L) / (480 × 0.70)`, i.e. `kills_per_level(L) / 336`. This assumes ≈ 480 at-level
kills/hour (one kill per ≈ 7.5 s including travel/aggro, `10_systems/COMBAT_FORMULA.md` §14) and
that **hunting occupies ≈ 70% of playtime** (the other ≈ 30% is questing, shopping, travel, and
downtime — see §4). Cumulative `/played` to *reach* level `L` is the sum of the per-level hours over
levels `1..L−1`. Both the table below and the prose use this one model; there is no second reading.

| Lv→+1 | `exp_to_next` | kills/level | `/played` this lvl | cum `/played` @ Lv | `cumulative_total` @ Lv |
|---|---|---|---|---|---|
| 1 | 108 | 27 | 0.08 h | 0.0 h | 0 |
| 2 | 340 | 34 | 0.10 h | 0.1 h | 108 |
| 3 | 714 | 42 | 0.12 h | 0.2 h | 448 |
| 4 | 1,200 | 50 | 0.15 h | 0.3 h | 1,162 |
| 5 | 1,856 | 58 | 0.17 h | 0.5 h | 2,362 |
| 6 | 2,747 | 67 | 0.20 h | 0.6 h | 4,218 |
| 7 | 3,800 | 76 | 0.23 h | 0.8 h | 6,965 |
| 8 | 5,160 | 86 | 0.26 h | 1.1 h | 10,765 |
| 9 | 6,720 | 96 | 0.29 h | 1.3 h | 15,925 |
| 10 | 8,480 | 106 | 0.32 h | 1.6 h | 22,645 |
| 11 | 10,530 | 117 | 0.35 h | 1.9 h | 31,125 |
| 12 | 12,928 | 128 | 0.38 h | 2.3 h | 41,655 |
| 13 | 15,680 | 140 | 0.42 h | 2.6 h | 54,583 |
| 14 | 18,848 | 152 | 0.45 h | 3.1 h | 70,263 |
| 15 | 22,140 | 164 | 0.49 h | 3.5 h | 89,111 |
| 16 | 26,019 | 177 | 0.53 h | 4.0 h | 111,251 |
| 17 | 30,210 | 190 | 0.57 h | 4.5 h | 137,270 |
| 18 | 34,884 | 204 | 0.61 h | 5.1 h | 167,480 |
| 19 | 40,112 | 218 | 0.65 h | 5.7 h | 202,364 |
| 20 | 45,704 | 232 | 0.69 h | 6.3 h | 242,476 |
| 21 | 51,623 | 247 | 0.74 h | 7.0 h | 288,180 |
| 22 | 58,164 | 262 | 0.78 h | 7.8 h | 339,803 |
| 23 | 65,608 | 278 | 0.83 h | 8.6 h | 397,967 |
| 24 | 73,206 | 294 | 0.88 h | 9.4 h | 463,575 |
| 25 | 81,530 | 310 | 0.92 h | 10.3 h | 536,781 |
| 26 | 90,252 | 327 | 0.97 h | 11.2 h | 618,311 |
| 27 | 99,760 | 344 | 1.02 h | 12.1 h | 708,563 |
| 28 | 110,048 | 362 | 1.08 h | 13.2 h | 808,323 |
| 29 | 121,220 | 380 | 1.13 h | 14.2 h | 918,371 |
| 30 | 132,534 | 398 | 1.18 h | 15.4 h | 1,039,591 |
| 31 | 144,699 | 417 | 1.24 h | 16.6 h | 1,172,125 |
| 32 | 157,832 | 436 | 1.30 h | 17.8 h | 1,316,824 |
| 33 | 171,912 | 456 | 1.36 h | 19.1 h | 1,474,656 |
| 34 | 186,592 | 476 | 1.42 h | 20.5 h | 1,646,568 |
| 35 | 201,872 | 496 | 1.48 h | 21.9 h | 1,833,160 |
| 36 | 218,174 | 517 | 1.54 h | 23.4 h | 2,035,032 |
| 37 | 235,106 | 538 | 1.60 h | 24.9 h | 2,253,206 |
| 38 | 253,680 | 560 | 1.67 h | 26.5 h | 2,488,312 |
| 39 | 272,376 | 582 | 1.73 h | 28.2 h | 2,741,992 |
| **40** | **292,336** | **604** | **1.80 h** | **29.9 h** | **3,014,368** |
| 41 | 313,500 | 627 | 1.87 h | 31.7 h | 3,306,704 |
| **42** (arc end) | **335,400** | **650** | **1.93 h** | **33.6 h** | **3,620,204** |

**Arc 1 (Lv 1 → 42): ≈ 3.62 M `exp`, ≈ 34 `/played` hours.** Intermediate values come from the
formula; the table is a checksum.

### 1.1 Published anchors beyond the arc (reference only — not authored this run)

The curve is defined for the full cap-300 game, but only these anchors are owner-ratified (C3); the
Lv 100–300 tail is a future-arc segment law (§6). Rows below are reference, not arc-1 content:

| Lv→+1 | `exp_to_next` | kills/level | `/played` this lvl | cum `/played` @ Lv | `cumulative_total` @ Lv |
|---|---|---|---|---|---|
| 50 | 549,950 | 850 | 2.53 h | 51.1 h | 7,006,322 |
| 60 | 931,520 | 1,136 | 3.38 h | **80.1 h** | 14,108,987 |
| 70 | 1,464,924 | 1,462 | 4.35 h | 118.2 h | 25,685,465 |
| 80 (3rd-job gate) | 2,177,148 | 1,828 | 5.44 h | **166.5 h** | 43,384,436 |
| 90 | 3,103,026 | 2,234 | 6.65 h | 226.3 h | 69,139,582 |
| 100 | 4,266,560 | 2,680 | 7.98 h | **298.6 h** | 105,199,357 |

Anchors (C3′ ratified): **Lv 8 ≈ 1 h · Lv 40 ≈ 30 h · Lv 42 ≈ 33.5 h · Lv 60 ≈ 80 h · Lv 80 ≈ 166 h
(≈ 5–6 weeks at 4–5 h/day) · Lv 100 ≈ 300 h.** These are the pacing contract every economy/quest/TTK
table cites. (C3′ superseded the earlier, faster C3 anchors — Lv 80 moved from ≈ 1 month to ≈ 5–6
weeks; the change was flagged to the owner at amendment time and not objected to.)

### 1.2 Time distribution by band (cumulative `/played`)

| Band | Lv 1–8 | Lv 8–20 | Lv 20–30 | Lv 30–40 | Lv 40–42 | Lv 42–60 | Lv 60–80 | Lv 80–100 |
|---|---|---|---|---|---|---|---|---|
| `/played` | 1.1 h | 5.3 h | 9.0 h | 14.5 h | 3.7 h | 47 h | 86 h | 132 h |

The whole authored arc (Lv 1–42) is a legible ≈ 34 h — about a week of evenings — front-loaded so the
first job (Lv 8) is ≈ 1 h, a single evening. The steep back half (Lv 42→100) is the intended long-tail
climb to the 3rd-job gate, not a wall (each level stays a legible multiple of the previous).

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
`exp/hour ≈ 480 · exp_per_kill_normal(L)`, rising steadily (≈ 1.9 K/h at Lv 1 → ≈ 248 K/h at the Lv
42 arc end) with no region-boundary jumps.

| `tier` | multiplier | Notes |
|---|---|---|
| `normal` | ×1 | The pacing anchor. |
| `elite` | ×5 | ×6 `life` (COMBAT_FORMULA §13.2) for ×5 `exp` → marginally less `exp/hour` than normals; elites are speed-bumps and drop-density, not `exp` farms. |
| `boss` | ×25 | ×35 `life`; a region `boss` is a progression/loot event, not an `exp/hour` play. The 8 arc bosses (`docs/WORLD_PLAN.md`) all pay `boss` reward; party quests (`10_systems/social/PARTY_QUEST.md`) end at an existing boss and share this reward per `10_systems/social/PARTY.md`. |

There is no raid tier (Decision Contract C9): `mob_145`–`150` are Clockwork elites and the Custodian
boss, not raid bosses. Arc monster levels top out at 42 (Clockwork elites, `docs/WORLD_PLAN.md`).

| Mob Lv | `normal` ×1 | `elite` ×5 | `boss` ×25 |
|---|---|---|---|
| 1 | 4 | 20 | 100 |
| 5 | 32 | 160 | 800 |
| 8 (boss #1) | 60 | 300 | 1,500 |
| 14 (boss #2) | 124 | 620 | 3,100 |
| 22 (boss #4) | 222 | 1,110 | 5,550 |
| 30 | 333 | 1,665 | 8,325 |
| 38 (boss #7) | 453 | 2,265 | 11,325 |
| 40 (boss #8) | 484 | 2,420 | 12,100 |
| 42 (elite cap) | 516 | 2,580 | 12,900 |

Reference rows beyond the arc (not authored this run): Lv 60 → 820 · Lv 80 → 1,191 · Lv 100 → 1,592
`normal` base.

## 4. `exp` source split policy

Target mix of where a level's `exp` comes from, so no single activity is mandatory (P2) and the
world stays a hunt-and-hangout loop (P3):

| Source | Target share | Owner of the budget |
|---|---|---|
| Hunting (monster kills) | ≈ 70% | This doc (§1–§3). |
| Quests | ≈ 25% | `10_systems/QUESTS.md` (per-quest `exp` budgets **cite this doc**; a region's quest `exp` should total ≈ 25% of the `exp` to clear that region's level band). |
| Other (first-clear, bestiary, exploration) | ≈ 5% | Small one-time grants; owners `10_systems/DROPS.md` / map & bestiary systems. |

The 70% hunting share is the same figure the §1 `/played` model is built on: hunting occupies ≈ 70%
of playtime, so a level's wall-clock hours = `kills_per_level(L) / (480 × 0.70)`. Killing exactly
`kills_per_level(L)` at-level normals *does* earn the level (the §1 coupling), and that hunting is
≈ 70% of the hours spent reaching it — the remaining ≈ 30% (quests, shopping, travel, downtime) is
already folded into the `/played` figure. If a region's quests over- or under-shoot the 25% `exp`
share, its effective pace drifts from the table — `10_systems/QUESTS.md` is responsible for staying
in budget, citing these numbers.

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

## 6. Arc-1 scope and the post-arc tail (SCOPE Open Question)

This run authors the **first arc, Lv 1–42** (`00_vision/SCOPE.md`). The game cap is **300 (initial
design)**. Within the arc:

- **Character growth is fully specified Lv 1–42**: the §1 curve, primary auto-growth
  (`10_systems/STATS.md` §4.2), skill points (`10_systems/SKILL_SYSTEM.md`), and gear tiers through
  the Lv-40 band (`10_systems/ITEMS.md`, C7) all cover the arc.
- **Past Lv 42**, arc-1 content runs out: leveling toward the Lv 80 3rd-job gate and beyond is a
  slow grind on the endgame Clockwork maps and the two party quests
  (`10_systems/social/PARTY_QUEST.md`) until future arcs add content. The §1 anchors (Lv 60 ≈ 80 h,
  Lv 80 ≈ 166 h, Lv 100 ≈ 300 h) are the ratified pacing target for that tail.

**The Lv 100–300 tail segment law is an explicit Open Question, deferred to a future arc.** The
owner ratified the ≤ 100 anchors only (`memory.md` C3); a steeper piecewise segment or exponent
change past Lv 100 is a future-arc decision. This run does **not** invent it — every economy/quest/
TTK table in this arc cites only the Lv 1–100 curve above. SCOPE's earlier "post-cap gear-only /
paragon" question is moot under cap 300: there is no launch cap to be post of; the question reopens
only when a future arc approaches Lv 300.

## Open Questions

- **Lv 100–300 curve tail (segment law):** deferred to a future arc (§6). Only the Lv ≤ 100 anchors
  are ratified (C3′: Lv 8 ≈ 1 h · Lv 40 ≈ 30 h · Lv 42 ≈ 33.5 h · Lv 60 ≈ 80 h · Lv 80 ≈ 166 h ·
  Lv 100 ≈ 300 h). A future owner sets the tail; it must keep those anchors and not touch the §1 arc
  curve. Owner: LEVELING.md, future arc.
- The ≈ 480 kills/hour pacing assumption folds in travel/aggro downtime that has not been measured;
  if real spawn density (`docs/WORLD_PLAN.md`, map spawn data) diverges, the `/played` estimates
  shift while the `exp_to_next` curve stays fixed. Flagged for the Phase D content pass.
- Quest `exp` totalling exactly 25% per region depends on `10_systems/QUESTS.md` honoring this
  budget; if quest counts per region (`docs/ID_REGISTRY.md`) can't hit 25% cleanly at a given band,
  the residual shifts to hunting (higher `kills_per_level` in practice). Owner: QUESTS.md.
- No `exp` is discarded in this arc (cap 300 is far above the Lv 1–42 range; §6). A Lv-300 cap-edge
  `exp`-overflow policy (e.g. a "mastery `exp` → `shards`/material" soft sink) is a future-arc
  question that would belong to `10_systems/ECONOMY.md`, not here. Not in scope this run.
