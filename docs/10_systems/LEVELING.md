# LEVELING.md — Experience Curve, Kill Rewards & Level-Up

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/COMBAT_FORMULA.md, 10_systems/STATS.md, 10_systems/SKILL_SYSTEM.md,
10_systems/QUESTS.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/social/RAID.md, 10_systems/social/PARTY.md, 10_systems/PERSISTENCE.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the `exp`→`level` curve, the per-kill `exp` reward guideline, the `exp` source split
policy, and what a level-up grants. Combat math, monster stat budgets, and the **level-difference
dampener curve** live in `10_systems/COMBAT_FORMULA.md`; primary/derived stat growth lives in
`10_systems/STATS.md`; skill-point spending in `10_systems/SKILL_SYSTEM.md`; raid rules live in
`10_systems/social/RAID.md`. This doc consumes those and never restates them. The game `level` cap
is **300** (initial design, `00_vision/SCOPE.md`). This doc is **formula-first**: the closed-form
curve holds to 300, with detail tables for the **authored range** — Lv 1–80, spanning arc 1
(Lv 1–42) and arc 2 (Lv 40–80) — with the frozen curve extended to the owner-ratified Lv-100
`/played` anchor and a provisional softcap continuation only past Lv 100 (§1.2) until future arcs
author Lv 100+ content. The between-arcs plateau policy is §6.

## 1. The `exp` curve (Lv 1 → 80 authored; formula to 300)

Two coupled formulas define pacing. The first is the per-level requirement; the second (§3) is the
per-kill reward. They are bound so that **`exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L)`**
— i.e., the number of at-level `normal` kills to earn a level equals `kills_per_level(L)` exactly
(at 100% hunting), tying the curve directly to the time-to-kill contract
(`10_systems/COMBAT_FORMULA.md` §14).

```
exp_to_next(L)       = exp_per_kill_normal(L) · kills_per_level(L)      # exp to go L -> L+1
kills_per_level(L)   = round(20 + 6.6 · L + 0.20 · L²)   # at-level normal kills to level (100% hunting); L ≤ 100, see §1.2
exp_per_kill_normal(L) = round(4 · L^1.3)        # §3, base per-kill reward (all levels)
cumulative_total(L)  = Σ exp_to_next(i), i = 1..L-1
```

**Ratified pacing anchors (owner, 2026-07-24):** **Lv 40 ≈ 30 h · Lv 80 ≈ 166 h · Lv 100 ≈ 300 h**
of `/played`. The two coupled formulas keep their shape and coupling; only `kills_per_level` sets the
pace, and it is **frozen through Lv 100** (the Lv-100 anchor is owner-ratified; §1.2).

`kills_per_level` grows quadratically through the authored range, so **early levels are minutes and
the top of arc 2 (Lv 70–80) is multi-hour sessions per level** (P2); the quadratic is softened past
Lv 100 (§1.2). The `/played` estimate charges each level's **full** `kills_per_level` against an
effective **≈ 336 at-level-kill-equivalents/hour**: 480 raw kills/hour of peak hunting (one kill per
≈ 7.5 s, `10_systems/COMBAT_FORMULA.md` §14), discounted by the **0.70 hunting duty-cycle** — the
30% of a level that arrives from quests/first-clears (§4) plus travel, aggro, and turn-in downtime
clears at a slower blended rate. So `/played(L) = kills_per_level(L) / 336` (= `/ (480 · 0.70)`).

| Lv→+1 | `exp_to_next` | `cumulative_total` @ Lv | kills/level | est. `/played` (level) | cum `/played` @ Lv |
|---|---|---|---|---|---|
| 1 | 108 | 0 | 27 | 0.08 h | 0.0 h |
| 2 | 340 | 108 | 34 | 0.10 h | 0.1 h |
| 3 | 714 | 448 | 42 | 0.12 h | 0.2 h |
| 4 | 1,200 | 1,162 | 50 | 0.15 h | 0.3 h |
| 5 | 1,856 | 2,362 | 58 | 0.17 h | 0.5 h |
| 6 | 2,747 | 4,218 | 67 | 0.20 h | 0.6 h |
| 7 | 3,800 | 6,965 | 76 | 0.23 h | 0.8 h |
| 8 | 5,160 | 10,765 | 86 | 0.26 h | 1.1 h |
| 9 | 6,720 | 15,925 | 96 | 0.29 h | 1.3 h |
| 10 | 8,480 | 22,645 | 106 | 0.32 h | 1.6 h |
| 15 | 22,140 | 89,111 | 164 | 0.49 h | 3.5 h |
| 20 | 45,704 | 242,476 | 232 | 0.69 h | 6.3 h |
| 25 | 81,530 | 536,781 | 310 | 0.92 h | 10.3 h |
| 30 | 132,534 | 1,039,591 | 398 | 1.18 h | 15.4 h |
| 35 | 201,872 | 1,833,160 | 496 | 1.48 h | 21.9 h |
| 40 | 292,336 | 3,014,368 | 604 | 1.80 h | 29.9 h |
| 45 | 407,208 | 4,696,676 | 722 | 2.15 h | 39.6 h |
| 50 | 549,950 | 7,006,322 | 850 | 2.53 h | 51.1 h |
| 55 | 723,216 | 10,091,160 | 988 | 2.94 h | 64.5 h |
| 60 | 931,520 | 14,108,987 | 1136 | 3.38 h | 80.1 h |
| 65 | 1,177,540 | 19,240,975 | 1294 | 3.85 h | 97.9 h |
| 70 | 1,464,924 | 25,685,465 | 1462 | 4.35 h | 118.2 h |
| 75 | 1,797,440 | 33,655,529 | 1640 | 4.88 h | 141.0 h |
| 80 | 2,177,148 | 43,384,436 | 1828 | 5.44 h | 166.5 h |

Rows Lv 1–80 are **frozen**: arc-1 (Lv 1–42) and arc-2 (Lv 40–80) content is balanced against these
exact values. **Authored total: ≈ 166 `/played` hours to reach Lv 80 (≈ 172 h to complete it);
authored total `exp` to reach Lv 80 = 43,384,436.** Intermediate levels: compute from the formula,
or linearly interpolate between rows. For Lv > 100 see the provisional continuation in §1.2.

### 1.1 Time distribution by band

The front ten levels are a single evening; each subsequent level is a smooth **≈ 1.04–1.07×** step
in `exp` over the previous (`exp_to_next(41)/(40) ≈ 1.07`, `(80)/(79) ≈ 1.04`) — a long steady ramp,
never a spike (P2). By arc:

**Arc 1 — Emberfoot + Harthmoor (Lv 1 → 42):** ≈ 33.6 `/played` hours to reach Lv 42.

| Band | Lv 1–10 | Lv 10–20 | Lv 20–30 | Lv 30–42 |
|---|---|---|---|---|
| `/played` | 1.6 h | 4.8 h | 9.0 h | 18.2 h |

**Arc 2 — Frostpeak → Arcane Reach → Voidshore (Lv 40 → 80):** ≈ 136.6 `/played` hours across the
contiguous band (per-level cost climbs from ≈ 1.80 h at Lv 40 to ≈ 5.44 h at Lv 79→80). The
per-island bands below are each measured over that island's **own** level range, so they **overlap
by design** (Frostpeak's 53–55 is also Arcane Reach's floor, etc.) and do not sum to the contiguous
total:

| Band (island) | Frostpeak 40–55 | Arcane Reach 53–68 | Voidshore 66–80 |
|---|---|---|---|
| `/played` | 34.6 h | 50.9 h | 64.7 h |

**Pacing (owner directive, v3):** every arc-2 level is a **full session or more** — a significant,
session-scale climb per level in the classic-MMO tradition, yet each level is only a few percent
heavier than the last (no spikes) and the level-up refill (§5) plus the Lv-40 job-advancement beat
(Open Questions) keep it fair, not cruel (P2). The reachable authored climb is ≈ 166 `/played` hours
to reach the top of arc 2 (≈ 172 h to complete Lv 80); the full curve to cap 300 is formula-driven
and provisional past Lv 100 (§1.2, §6).

### 1.2 Past the ratified anchors (Lv > 100) — provisional softcap continuation

**Why the boundary is Lv 100.** Lv 100 is now an owner-ratified `/played` anchor (≈ 300 h), so the
real quadratic is **kept and frozen all the way through Lv 100** — Lv 81–100 are the ratified
extension to that anchor (still pre-content: arc-2 authors only to ≈ Lv 82). Only **past** Lv 100 is
the curve provisional. Continued unbroken, the §1 quadratic reaches `kills_per_level ≈ 20,000` at
Lv 300 — a single level of ≈ 60 `/played` hours and a punishing multi-thousand-hour tail, the wall
the "cozy, not cruel" pillar forbids (P2). No Lv 100+ content is authored yet, so the true > 100
curve is **future-arc design**; as a placeholder that keeps the formula from emitting absurd values,
`kills_per_level` continues **linearly** past Lv 100 — value and slope matched at the boundary
(`kills_per_level(100) = 2,680`, slope `6.6 + 0.4·100 = 46.6`):

```
kills_per_level(L) = round(20 + 6.6 · L + 0.20 · L²)   for L ≤ 100     # frozen (Lv 81–100 = ratified extension to the Lv-100 anchor)
                   = round(2680 + 46.6 · (L − 100))     for L > 100     # provisional linear softcap
exp_per_kill_normal(L) = round(4 · L^1.3)          # unchanged, all levels (stays bound to COMBAT_FORMULA TTK/reward)
```

This is C1-continuous (no kink at Lv 100), preserves every Lv 1–100 value exactly, and bounds a
near-cap level to ≈ 36 `/played` hours with ≈ 4,690 h to cap 300 — still a heavy classic-MMO tail,
not a wall, and explicitly **provisional/future-arc** (content authored only through ≈ Lv 82).
Checksums (all **provisional** past Lv 100; future arcs will re-tune with content-balanced pacing):

| Lv | `kills_per_level` | `exp_to_next` | est. `/played` per level | cum `/played` @ Lv |
|---|---|---|---|---|
| 100 (boundary) | 2,680 | 4,266,560 | 8.0 h | ≈ 299 h |
| 150 | 5,010 | 13,516,980 | 14.9 h | ≈ 867 h |
| 200 | 7,340 | 28,780,140 | 21.8 h | ≈ 1,783 h |
| 300 (cap) | 12,000 | 79,704,000 | 35.7 h | ≈ 4,690 h |

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
`exp/hour ≈ 480 · exp_per_kill_normal(L)`, rising steadily (≈ 1.9 K/h at Lv 1 → ≈ 572 K/h at Lv 80,
the top of arc 2) with no region-boundary jumps.

| `tier` | multiplier | Notes |
|---|---|---|
| `normal` | ×1 | The pacing anchor. |
| `elite` | ×5 | ×6 `life` (COMBAT_FORMULA §13.2) for ×5 `exp` → marginally less `exp/hour` than normals; elites are speed-bumps and drop-density, not `exp` farms. |
| `boss` | ×25 | ×35 `life`; a region `boss` is a progression/loot event, not an `exp/hour` play. |
| raid boss | raid-shared, **150× base total** | Total = `150 · exp_per_kill_normal(boss.level)`, split among the raid party per `10_systems/social/RAID.md` (exp-share mechanics in `10_systems/social/PARTY.md` §4). This is only the finale **kill**; a raid also pays per-stage and completion grants (§3.1) that make a full clear a strong `exp` event, not just a loot run. |

| Mob Lv | `normal` ×1 | `elite` ×5 | `boss` ×25 |
|---|---|---|---|
| 1 | 4 | 20 | 100 |
| 5 | 32 | 160 | 800 |
| 10 | 80 | 400 | 2,000 |
| 20 | 197 | 985 | 4,925 |
| 30 | 333 | 1,665 | 8,325 |
| 40 | 484 | 2,420 | 12,100 |
| 50 | 647 | 3,235 | 16,175 |
| 55 | 732 | 3,660 | 18,300 |
| 60 | 820 | 4,100 | 20,500 |
| 70 | 1,002 | 5,010 | 25,050 |
| 80 | 1,191 | 5,955 | 29,775 |

Mob Lv > 80 (future-arc content): compute from `exp_per_kill_normal(L) = round(4·L^1.3)`.

Raid-boss total `exp` scales with the raid's boss `level`. The two arc-2 raids
(`10_systems/social/RAID.md`): **`raid_deepfrost`** (boss Lv 55) totals `150 · 732 ≈ 109,800`;
**`raid_voidtide`** (boss Lv 80) totals `150 · 1,191 ≈ 178,650` — split among the raid party
(≈ 21,960 and ≈ 35,730 per member at `N` = 5). That finale-**kill** share alone is worth only ≈ 30
at-level `normal` kills, so the kill by itself is not the draw — the **per-stage and completion
grants in §3.1** are what make a full raid clear a strong `exp` event (and the loot is
`10_systems/DROPS.md`'s).

### 3.1 Raid stage & completion `exp` (MapleStory-inspired)

Raids (`10_systems/social/RAID.md`) pay `exp` in the classic co-op-run tradition: a grant on **each
stage cleared** plus a headline **completion bonus** on the finale-boss kill, on top of the ordinary
stage mobs and the §3 raid-boss row. Both grants are **fixed authored `exp` amounts** — a flat
number per raid, **not** a formula and **not** a fraction of a level — paid **flat to every eligible
member** (not a pool to split, so the whole party is rewarded for finishing). Each raid's values:

| Raid (band) | `raid_stage_exp` (each stage cleared) | `raid_clear_exp` (finale completion) |
|---|---|---|
| `raid_undervault` (Lv 15–22) | 3,000 | 20,000 |
| `raid_mainspring` (Lv 32–40) | 6,000 | 40,000 |
| `raid_deepfrost` (Lv 45–55) | 10,000 | 60,000 |
| `raid_voidtide` (Lv 70–80) | 16,000 | 100,000 |

Values are **fixed and predictable**: a `raid_voidtide` stage always pays 16,000 on clear, every run,
to each member; its finale always pays the 100,000 completion bonus — the run's **best single `exp`
reward**. A full clear (all stages + finale) is worth roughly **10–15% of a band-level to each
member** — a genuinely great grouped session, deliberately more rewarding than the same wall-clock
spent hunting solo, so raids are something a group *wants* to run (`00_vision/PILLARS.md` P3), while
solo leveling stays fully viable (P2, encourage-not-mandate). Each stage grants its
`raid_stage_exp` the moment that stage's objective (`10_systems/social/RAID.md` §4) completes. The
numbers rise across the bands only because each raid is authored with its own fixed values — there
is no per-level scaling formula.

**First-clear-of-the-day bonus.** The first successful clear of a given raid, per character, per day
(day boundary per `10_systems/PERSISTENCE.md`), pays **2× that raid's `raid_clear_exp`** plus one
bonus `raid_token` (`10_systems/social/RAID.md`). Later same-day clears pay the normal grants. This
daily beat — not a cap — is the "log in and raid with the guild" social rhythm; there is **no weekly
lockout**, and the 15-minute per-character clear cooldown (`10_systems/social/RAID.md` §5) only stops
back-to-back clear-chaining from replacing field play as the `/played` pacing anchor. The boss's own
kill `exp` (§3's 150× row, split per `10_systems/social/PARTY.md` §4) is separate and on top. All raid
grants sit **outside** the §4 mandatory source-split.

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

**Raids sit outside this mandatory mix.** The §3.1 raid grants are an **elective accelerator**, not
part of the 70/25/5 budget: the §1 curve and its `/played` estimates assume a player who never raids
(hunting + quests only), so raids can pay strong `exp` (§3.1) without any activity becoming mandatory
(P2). A grouped player who also raids simply travels the same curve faster; the party exp bonus
(`10_systems/social/PARTY.md` §4) works the same way. Neither touches the §1 curve.

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

## 6. Past the authored arcs — the Lv 80+ plateau (gear-first)

The game `level` cap is **300** (`00_vision/SCOPE.md`), so `exp` never stops mattering and there is
**no post-cap state to design here yet** — the authored world simply **runs out** at the top of
arc 2. Voidshore endgame maps top out at Lv 80 and `raid_voidtide`'s boss is Lv 80
(`docs/WORLD_PLAN.md`, `10_systems/social/RAID.md`); the highest authored elites reach ≈ Lv 82. Past
≈ Lv 82 a character keeps leveling on the §1 curve (frozen through the ratified Lv-100 anchor, then
the §1.2 softcap), but with no higher-band content the pace is a deliberate **slow grind** on the top
Voidshore maps and the two arc-2 raids until arc 3 authors Lv 80+ regions.

- **The plateau chase is gear, not levels.** Between arcs, the meaningful power gains come from
  **gear and enhancement** (`10_systems/ITEMS.md`, `10_systems/ENHANCEMENT.md`) — chasing raid
  uniques and enhancement tiers on the Voidshore maps and the arc-2 raids — not from the slow trickle
  of plateau levels. Level-up primary auto-growth continues per `10_systems/STATS.md` §4.2 (that doc
  owns its range); at the plateau it is a minor drip next to the gear loop.
- **No paragon/overflow track at launch.** A paragon stat drip would inflate primaries past the
  `10_systems/STATS.md` §4 model that every monster budget (`10_systems/COMBAT_FORMULA.md` §13) and
  all authored skills are balanced against, forcing perpetual re-tuning and the exact power-creep
  economy `00_vision/PILLARS.md` anti-pillars forbid. The plateau keeps the balance surface fixed and
  routes endgame ambition into the loot loop and the raids, matching "the grind is cozy, not cruel"
  (P2). A paragon-style system stays **deferred to post-launch and is not a launch promise** (Open
  Questions).
- **The true cap-300 endgame is future-arc design.** The frozen curve now reaches the owner-ratified
  Lv-100 anchor; the Lv 100–300 curve is provisional (§1.2); the
  high-level regions, any late-cap or post-cap progression policy, and the endgame gear-check that
  the level-difference dampener (`10_systems/COMBAT_FORMULA.md` §9) is meant to gate all ship with
  future arcs and are **out of scope for this run** (`00_vision/SCOPE.md`).

## Open Questions

- **Lv > 100 softcap is provisional (§1.2).** The frozen quadratic now holds through the
  owner-ratified Lv-100 `/played` anchor; the linear continuation past Lv 100 is a placeholder to stop
  the quadratic from emitting absurd near-cap values. The real Lv 100–300 pacing is future-arc design
  and must be re-tabled per arc against that arc's content, quests, and any rested-`exp` system,
  without touching the frozen Lv 1–100 curve. Owner: LEVELING.md, future arcs.
- **Authored quest-content `exp` rewards are now stale against this curve (regen handoff).** The
  `docs/50_content/quests/*.yaml` files store computed `exp` reward integers (= `pct · exp_to_next`,
  §4 / `10_systems/QUESTS.md` §4). Because `exp_to_next` changed, those integers must be
  mechanically regenerated in a **Phase-D content pass** against the new curve — do **not** hand-edit
  them here. Monster `stats.exp` (per-kill `exp_per_kill_normal`, §3) is **unchanged** and not stale.
  Owner: Phase-D content / producer.
- **`10_systems/ONBOARDING_FTUE.md` Lv 1→8 plausibility check is stale against the new curve**
  (out-of-scope doc, flag-only). That doc restates §1's old per-level `/played` rows to argue Lv 8 is
  reachable in ≈ 0.50 h of at-level exp, inside its 60-minute FTUE budget. Under the ratified curve
  the cumulative `/played` to **reach** Lv 8 is ≈ 1.1 h (per-level rows 0.08 … 0.23), which now
  **overshoots** that 60-minute budget on pure at-level pacing — so the FTUE either leans harder on
  scripted first-clear/quest grants (§4 "other") in the intro or its "Lv 8 by end of first hour"
  target needs revisiting. Reconcile with the FTUE owner. Owner: ONBOARDING_FTUE.md + this doc.
- **Branching 2nd-job advancement at Lv 40** (owner `10_systems/JOBS.md`, patched in parallel): the
  advancement lands at the arc-1→arc-2 seam (Lv 40), exactly where per-level cost first exceeds an
  hour. If pacing wants a **beat** there — an advancement quest granting a one-time `exp` bump or
  skill-point spike to reward the choice and cushion the ramp into arc 2 — the grant is budgeted here
  (§4 "other" one-time grants), but the branch structure, quest, and any gate are JOBS.md's. Confirm
  whether advancement should carry a pacing grant, and how a branch choice (if it changes hunting
  efficiency) interacts with the §1 `/played` assumption. Owner: JOBS.md + this doc.
- **`10_systems/STATS.md` §4.2 growth range** was authored for the retired Lv-100 world; §5/§6 cite
  it for level-up primary auto-growth, which must now extend across the new cap-300 range (or state
  its own cap). Reconcile at the next gate. Owner: STATS.md.
- **Post-launch** paragon/prestige track (deferred, §6): if ever pursued, it must not touch the
  §1 base curve or the primary model; a bounded, mostly-horizontal system (cosmetic/`shards`/
  account-wide unlocks) is the only shape compatible with the fixed balance surface. Owner:
  LEVELING.md, post-launch — **not** an in-scope launch item.
- Raid `exp` split (the §3 150× total) is arbitrated by `10_systems/social/RAID.md` with the
  contribution-weighted base + presence-bonus mechanics in `10_systems/social/PARTY.md` §4; the
  ≈ 21,960 / ≈ 35,730 per-member figures here assume the even-split degenerate case at `N` = 5.
  Reconcile the exact per-member share with PARTY §4 at the next gate.
- **Raid stage/completion `exp` values (§3.1) are first-pass fixed numbers.** Authored per raid as
  flat amounts (not a formula, not a fraction of a level), so a clear's reward is fully predictable;
  retune the numbers themselves with telemetry against the `10_systems/social/RAID.md` §5 clear
  cooldown so raiding never beats hunting as the pacing anchor. Owner: this doc with
  `10_systems/social/RAID.md` / `10_systems/ECONOMY.md`.
- **The party exp bonus (`10_systems/social/PARTY.md` §4) accelerates grouped pacing.** The §1
  `/played` estimates are solo (pure hunting); a full party earns `party_bonus`-boosted `exp` (up to
  a **doubled** pool at `N` = 6) and clears faster, so grouped `/played` is shorter than the table.
  Reconciling the grouped pace against the solo curve is flagged. Owner: this doc with
  `10_systems/social/PARTY.md`.
- The ≈ 480 kills/hour pacing assumption (and the 0.70 duty-cycle behind the ≈ 336 effective rate)
  folds in travel/aggro/turn-in downtime that has not been measured; if real spawn density
  (`docs/WORLD_PLAN.md`, map spawn data) diverges, the `/played` estimates shift while the
  `exp_to_next` curve stays fixed. Flagged for the Phase D content pass.
- Quest `exp` totalling exactly 25% per region depends on `10_systems/QUESTS.md` honoring this
  budget; if quest counts per region (`docs/ID_REGISTRY.md`) can't hit 25% cleanly at a given band,
  the residual shifts to hunting (higher `kills_per_level` in practice). Owner: QUESTS.md.
