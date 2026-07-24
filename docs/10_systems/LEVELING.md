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
pacing anchors, `memory.md` Decision Contract C3). The Lv 100–300 tail segment law is a future-arc
Open Question (§6).

## 1. The `exp` curve (arc Lv 1 → 42; published anchors through Lv 100)

Two coupled formulas define pacing. The first is the per-level requirement; the second (§3) is the
per-kill reward. They are bound so that **`exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L)`**
— i.e., the number of at-level `normal` kills to earn a level equals `kills_per_level(L)` exactly,
tying the curve directly to the time-to-kill contract (`10_systems/COMBAT_FORMULA.md` §14).

```
exp_to_next(L)         = exp_per_kill_normal(L) · kills_per_level(L)    # exp to go L -> L+1
kills_per_level(L)     = round(20 + 0.26 · L²)   # at-level normal kills to level
exp_per_kill_normal(L) = round(4 · L^1.3)        # §3, base per-kill reward
cumulative_total(L)    = Σ exp_to_next(i), i = 1..L-1
```

`kills_per_level` grows quadratically, so **early levels are minutes and the high levels are days of
sessions** (P2). The **canonical played-time model** (`memory.md` C3): a level's `/played` hours =
`kills_per_level(L) / (480 × 0.70)`, i.e. `kills_per_level(L) / 336`. This assumes ≈ 480 at-level
kills/hour (one kill per ≈ 7.5 s including travel/aggro, `10_systems/COMBAT_FORMULA.md` §14) and
that **hunting occupies ≈ 70% of playtime** (the other ≈ 30% is questing, shopping, travel, and
downtime — see §4). Cumulative `/played` to *reach* level `L` is the sum of the per-level hours over
levels `1..L−1`. Both the table below and the prose use this one model; there is no second reading.

| Lv→+1 | `exp_to_next` | kills/level | `/played` this lvl | cum `/played` @ Lv | `cumulative_total` @ Lv |
|---|---|---|---|---|---|
| 1 | 80 | 20 | 0.06 h | 0.0 h | 0 |
| 2 | 210 | 21 | 0.06 h | 0.1 h | 80 |
| 3 | 374 | 22 | 0.07 h | 0.1 h | 290 |
| 4 | 576 | 24 | 0.07 h | 0.2 h | 664 |
| 5 | 832 | 26 | 0.08 h | 0.3 h | 1,240 |
| 6 | 1,189 | 29 | 0.09 h | 0.3 h | 2,072 |
| 7 | 1,650 | 33 | 0.10 h | 0.4 h | 3,261 |
| 8 | 2,220 | 37 | 0.11 h | 0.5 h | 4,911 |
| 9 | 2,870 | 41 | 0.12 h | 0.6 h | 7,131 |
| 10 | 3,680 | 46 | 0.14 h | 0.8 h | 10,001 |
| 11 | 4,590 | 51 | 0.15 h | 0.9 h | 13,681 |
| 12 | 5,757 | 57 | 0.17 h | 1.0 h | 18,271 |
| 13 | 7,168 | 64 | 0.19 h | 1.2 h | 24,028 |
| 14 | 8,804 | 71 | 0.21 h | 1.4 h | 31,196 |
| 15 | 10,530 | 78 | 0.23 h | 1.6 h | 40,000 |
| 16 | 12,789 | 87 | 0.26 h | 1.8 h | 50,530 |
| 17 | 15,105 | 95 | 0.28 h | 2.1 h | 63,319 |
| 18 | 17,784 | 104 | 0.31 h | 2.4 h | 78,424 |
| 19 | 20,976 | 114 | 0.34 h | 2.7 h | 96,208 |
| 20 | 24,428 | 124 | 0.37 h | 3.0 h | 117,184 |
| 21 | 28,215 | 135 | 0.40 h | 3.4 h | 141,612 |
| 22 | 32,412 | 146 | 0.43 h | 3.8 h | 169,827 |
| 23 | 37,288 | 158 | 0.47 h | 4.2 h | 202,239 |
| 24 | 42,330 | 170 | 0.51 h | 4.7 h | 239,527 |
| 25 | 47,866 | 182 | 0.54 h | 5.2 h | 281,857 |
| 26 | 54,096 | 196 | 0.58 h | 5.8 h | 329,723 |
| 27 | 60,900 | 210 | 0.62 h | 6.3 h | 383,819 |
| 28 | 68,096 | 224 | 0.67 h | 7.0 h | 444,719 |
| 29 | 76,241 | 239 | 0.71 h | 7.6 h | 512,815 |
| 30 | 84,582 | 254 | 0.76 h | 8.3 h | 589,056 |
| 31 | 93,690 | 270 | 0.80 h | 9.1 h | 673,638 |
| 32 | 103,532 | 286 | 0.85 h | 9.9 h | 767,328 |
| 33 | 114,231 | 303 | 0.90 h | 10.8 h | 870,860 |
| 34 | 125,832 | 321 | 0.96 h | 11.7 h | 985,091 |
| 35 | 137,566 | 338 | 1.01 h | 12.6 h | 1,110,923 |
| 36 | 150,654 | 357 | 1.06 h | 13.6 h | 1,248,489 |
| 37 | 164,312 | 376 | 1.12 h | 14.7 h | 1,399,143 |
| 38 | 178,935 | 395 | 1.18 h | 15.8 h | 1,563,455 |
| 39 | 194,220 | 415 | 1.24 h | 17.0 h | 1,742,390 |
| **40** | **211,024** | **436** | **1.30 h** | **18.2 h** | **1,936,610** |
| 41 | 228,500 | 457 | 1.36 h | 19.5 h | 2,147,634 |
| **42** (arc end) | **247,164** | **479** | **1.43 h** | **20.9 h** | **2,376,134** |

**Arc 1 (Lv 1 → 42): ≈ 2.38 M `exp`, ≈ 21 `/played` hours.** Intermediate values come from the
formula; the table is a checksum.

### 1.1 Published anchors beyond the arc (reference only — not authored this run)

The curve is defined for the full cap-300 game, but only these anchors are owner-ratified (C3); the
Lv 100–300 tail is a future-arc segment law (§6). Rows below are reference, not arc-1 content:

| Lv→+1 | `exp_to_next` | kills/level | `/played` this lvl | cum `/played` @ Lv | `cumulative_total` @ Lv |
|---|---|---|---|---|---|
| 50 | 433,490 | 670 | 1.99 h | 34 h | 4,954,763 |
| 60 | 783,920 | 956 | 2.85 h | **58 h** | 10,744,922 |
| 70 | 1,296,588 | 1,294 | 3.85 h | 91 h | 20,739,344 |
| 80 (3rd-job gate) | 2,005,644 | 1,684 | 5.01 h | **134 h** | 36,722,952 |
| 90 | 2,953,014 | 2,126 | 6.33 h | 190 h | 60,833,085 |
| 100 | 4,171,040 | 2,620 | 7.80 h | **260 h** | 95,602,828 |

Anchors: **Lv 40 ≈ 18 h · Lv 42 ≈ 21 h · Lv 60 ≈ 58 h · Lv 80 ≈ 134 h (≈ 1 month at 4–5 h/day) ·
Lv 100 ≈ 260 h.** These are the pacing contract every economy/quest/TTK table cites.

### 1.2 Time distribution by band (cumulative `/played`)

| Band | Lv 1–8 | Lv 8–20 | Lv 20–30 | Lv 30–40 | Lv 40–42 | Lv 42–60 | Lv 60–80 | Lv 80–100 |
|---|---|---|---|---|---|---|---|---|
| `/played` | 0.5 h | 2.5 h | 5.3 h | 9.9 h | 2.7 h | 37 h | 77 h | 126 h |

The whole authored arc (Lv 1–42) is a legible ≈ 21 h — about 4–5 play-days — front-loaded so the
first job (Lv 8) is a single evening. The steep back half (Lv 42→100) is the intended long-tail
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
  (`10_systems/social/PARTY_QUEST.md`) until future arcs add content. The §1 anchors (Lv 60 ≈ 58 h,
  Lv 80 ≈ 134 h, Lv 100 ≈ 260 h) are the ratified pacing target for that tail.

**The Lv 100–300 tail segment law is an explicit Open Question, deferred to a future arc.** The
owner ratified the ≤ 100 anchors only (`memory.md` C3); a steeper piecewise segment or exponent
change past Lv 100 is a future-arc decision. This run does **not** invent it — every economy/quest/
TTK table in this arc cites only the Lv 1–100 curve above. SCOPE's earlier "post-cap gear-only /
paragon" question is moot under cap 300: there is no launch cap to be post of; the question reopens
only when a future arc approaches Lv 300.

## Open Questions

- **Lv 100–300 curve tail (segment law):** deferred to a future arc (§6). Only the Lv ≤ 100 anchors
  are ratified (Lv 40 ≈ 18 h · Lv 42 ≈ 21 h · Lv 60 ≈ 58 h · Lv 80 ≈ 134 h · Lv 100 ≈ 260 h). A
  future owner sets the tail; it must keep those anchors and not touch the §1 arc curve. Owner:
  LEVELING.md, future arc.
- The ≈ 480 kills/hour pacing assumption folds in travel/aggro downtime that has not been measured;
  if real spawn density (`docs/WORLD_PLAN.md`, map spawn data) diverges, the `/played` estimates
  shift while the `exp_to_next` curve stays fixed. Flagged for the Phase D content pass.
- Quest `exp` totalling exactly 25% per region depends on `10_systems/QUESTS.md` honoring this
  budget; if quest counts per region (`docs/ID_REGISTRY.md`) can't hit 25% cleanly at a given band,
  the residual shifts to hunting (higher `kills_per_level` in practice). Owner: QUESTS.md.
- No `exp` is discarded in this arc (cap 300 is far above the Lv 1–42 range; §6). A Lv-300 cap-edge
  `exp`-overflow policy (e.g. a "mastery `exp` → `shards`/material" soft sink) is a future-arc
  question that would belong to `10_systems/ECONOMY.md`, not here. Not in scope this run.
