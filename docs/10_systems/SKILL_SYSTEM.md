# SKILL_SYSTEM.md — Skill Acquisition, Loadout, Targeting & level_data

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/JOBS.md,
10_systems/LEVELING.md, 10_systems/STATS.md, 10_systems/SKILL_EFFECTS.md,
10_systems/STATUS_EFFECTS.md, 10_systems/ELEMENTS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/ECONOMY.md, 10_systems/social/PARTY.md, 10_systems/PERSISTENCE.md,
10_systems/CONTROLS.md, 10_systems/HUD.md, 40_assets/ART_BIBLE.yaml, docs/ID_REGISTRY.md

Owner doc for **how skills are learned, ranked, respec'd, slotted, cast, and targeted**, and for
the `level_data` interpolation convention every skill file relies on. It owns the six GLOSSARY
targeting tokens' geometry. It does **not** own the effect ops (`10_systems/SKILL_EFFECTS.md`),
the roster/rosters (`10_systems/JOBS.md`), stat formulas (`10_systems/STATS.md`), the damage
pipeline or cadence bases (`10_systems/COMBAT_FORMULA.md`), or status behavior
(`10_systems/STATUS_EFFECTS.md`). It consumes those and never restates them.

## 1. Skill points — acquisition

Level-up grants skill points; `10_systems/LEVELING.md` §5 delegates the **magnitude** here.

- **+1 skill point per level gained** (levels 2→cap 300 = **299 lifetime points**; none at Lv 1).
  The authored first arc reaches Lv 42 (41 points); the full cap-300 total is flagged below.
- Points are granted atomically with the level-up (server-authoritative,
  `10_systems/PERSISTENCE.md`; `10_systems/LEVELING.md` §5 owns the trigger).
- A job **advancement** (`10_systems/JOBS.md` §1) grants **no** extra points — the 1st unlocks the
  first-job skill **tier**, the 2nd unlocks the chosen **specialization**'s roster (§2). Keeping
  points on the flat +1/level curve makes total availability legible.
- By Lv 7 (end of `novice`) a character has 6 points for the four novice skills. Because the Lv 40
  advancement **branches** (`10_systems/JOBS.md` §1), a character accesses only its **6 first-job +
  one spec's 7 = 13 line skills** (+ 4 novice), i.e. 13 × `max_level` 10 = 130 line ranks — so **you
  specialize** and no character maxes everything (`00_vision/PILLARS.md` P4 depth). This is intended,
  not a shortfall; the exact cap-300 point budget vs the branched 13-skill kit is an Open Question.

## 2. Spending rules

- **`max_level` per skill = 10.** Each rank costs **1 point**. A skill's per-rank effect is defined
  by its `level_data` (§5).
- **Rank 1 = "learn."** Spending the first point learns the skill (must meet its gates below).
- **Tier gate.** A skill's tier (`10_systems/JOBS.md` §1): **first-job** `001`–`006` unlocks at the
  1st advancement (**Lv 8**); a **specialization** roster (`007`–`013` spec #1 · `014`–`020` spec #2 ·
  `021`–`027` spec #3) unlocks at the 2nd advancement (**Lv 40**) — but only the **chosen** spec's
  block (see line/spec gate); the **3rd tier** (`028`–`045`) is reserved for a future arc (default
  gate Lv 80, `10_systems/JOBS.md` Open Questions). Novice skills (`skill_novice_*`) are learnable
  from Lv 1.
- **Line & spec gate.** You may only put points into (a) your own line's **first-job** skills
  (`001`–`006`, line chosen at the Lv 8 advancement), (b) your **chosen specialization**'s roster
  (spec chosen at the Lv 40 advancement — the sibling specs' rosters stay permanently locked,
  `10_systems/JOBS.md` §1), and (c) the shared novice kit. Equip/weapon proficiency is
  `10_systems/ITEMS.md`'s.
- **Prerequisite chains (policy).** A skill may declare a prerequisite: another **accessible** skill
  (first-job or same-specialization) at a minimum rank. Chains are **short and shallow**
  (`00_vision/PILLARS.md` P2, no trap builds) — typical patterns: a specialization capstone requiring
  its first-job feeder at rank ≥ 3–5, or a passive requiring the active it enhances at rank ≥ 1. The
  concrete prereq **edges** live in each skill's Phase D YAML (`prerequisites: [{skill, min_rank}]`);
  this doc owns only the rule that (a) prereqs reference **first-job or same-spec** skills — never a
  sibling spec (`10_systems/JOBS.md` §1 branch), (b) a skill is un-rankable until its prereqs are
  met, and (c) a respec that would break a prereq refunds the dependent ranks too (§4).

## 3. Respec — generous (`00_vision/PILLARS.md` P2)

- **Skill respec is free and unlimited at any town job-trainer NPC.** Reclaims all spent skill
  points to the pool for reassignment, subject to the §2 gates. No `shards` cost.
- **Only in a safe zone.** Respec is available in `town`/`interior` maps
  (`15_maps_system/MAPS_SYSTEM.md` map types), not mid-combat or in the field, so it is a planning
  action, not a per-pull swap.
- **Free-point (primary stat) respec is separate** and carries a `shards` fee owned by
  `10_systems/STATS.md` §4.3 / `10_systems/LEVELING.md` / `10_systems/ECONOMY.md`; this doc governs
  **skill** points only.
- Because respec is free, no skill investment is permanent and no build is a trap — the design can
  lean into strong, specialized kits (`00_vision/PILLARS.md` P4) without punishing experimentation.

## 4. `level_data` convention (define once; content never restates)

Every skill YAML expresses its per-rank scaling as a `level_data` map with rows at **skill levels
1, 4, 7, and 10 only**. Values at ranks 2, 3, 5, 6, 8, 9 are **linearly interpolated at load** from
the bracketing rows. This keeps skill files to four authored rows instead of ten.

```
# interpolation for any interpolatable field f at rank r (1..10):
#   pick the bracketing authored ranks lo,hi in {1,4,7,10} with lo <= r <= hi
#   f(r) = f(lo) + (f(hi) - f(lo)) * (r - lo) / (hi - lo)
#   integer fields: round half-up after interpolation; float fields: keep 2 decimals
```

- **Interpolatable fields** (numeric, may appear in `level_data`): `essence_cost`, `cooldown`, and
  every numeric op parameter — `deal_damage.mult`, `apply_status.chance`/`.dur`/`.magnitude`,
  `heal`/`grant_shield`/`restore_essence` amounts, `knockback`/`pull`/`dash`/`leap` distances,
  `taunt.dur`, `summon_entity.dur`, `passive_stat_bonus` values, `on_hit_proc.chance`.
- **Non-interpolatable fields** (declared once, outside `level_data`, constant across ranks): the
  op list and order, `element`, `status` token, `cleanse` `tag`, targeting shape and its geometry,
  `summon_entity.entity_ref`, `on_hit_proc.trigger`. A skill never changes its *shape* by rank,
  only its *numbers*.
- Rows must be **monotonic where it matters** (validator warn): `deal_damage.mult` and magnitudes
  non-decreasing with rank; `cooldown` non-increasing. `00_vision/PILLARS.md` P2 (ranking a skill
  never makes it worse).

## 5. Cost, cooldown & cast rules

- **Essence is the skill resource** (`10_systems/STATS.md`; pool = `essence`). Every active costs
  `essence`; passives cost nothing to sustain. Casting with insufficient `essence` fails (no
  `life` cost — no self-damage casting in scope).
- **Cost scales with tier and rank.** First-pass bands at skill rank 1 → rank 10 (per-skill values
  authored in `level_data`, §4):

  | Tier | `essence_cost` band (rank 1 → 10) | `cooldown` band |
  |---|---|---|
  | first-job (`001`–`006`) | 5 → 12 | 0–8 s (core attacks often 0–3 s, `essence`-gated) |
  | specialization (`007`–`027`, the chosen spec's block) | 12 → 28 | 4–20 s |
  | 3rd tier (`028`–`045`, future arc) | 25 → 55 | 8–120 s (ultimates high end) |
  | novice | 4 → 10 | 2–10 s |

  Utility skills may hold `essence_cost` flat across ranks; damage skills typically rise with rank
  as `mult` rises. `clarity` reduces `essence` cost at cast time (`10_systems/STATUS_EFFECTS.md`
  §4.2); this doc owns cost resolution, that buff is applied as a multiplier to the resolved cost.
- **No global cooldown (GCD).** For snappy, readable action combat (`00_vision/PILLARS.md` P1) each
  skill runs on its **own** cooldown; there is no shared lockout across the bar. Instead every skill
  has a brief **cast + recovery** window (an input lock) that overrides `base_attack_interval`
  during the skill (`10_systems/COMBAT_FORMULA.md` §10 owns the base cadence). Cast/recovery
  duration is per-skill (`level_data`-adjacent constant), short for spammables and longer for heavy
  hits; it exists so animations read honestly (hit-frame honesty, P1), not as a tax.
- **Cooldowns are per skill instance, real-time**, and pause with the game (solo) but run
  server-side authoritatively when live (`10_systems/PERSISTENCE.md`). Some passives/procs
  (`10_systems/SKILL_EFFECTS.md` `on_hit_proc`) carry an internal cooldown (`icd`) instead of a
  bar cooldown.

## 6. Targeting semantics — the six GLOSSARY shapes (owner)

A skill declares exactly one **targeting shape** (`00_vision/GLOSSARY.md`, owner = this doc). The
shape selects the candidate set; each effect op then applies to the candidates of its class
(offensive ops → hostiles, support ops → self/allies; `10_systems/SKILL_EFFECTS.md` composition).
Ranges are in **tiles** — 1 tile = the `40_assets/ART_BIBLE.yaml` grid unit; the pixel value is
pending the tile-scale lock (`10_systems/COMBAT_FORMULA.md` §10 Open Question), so all numbers here
are scale-free. Angles are degrees in the vertical facing plane (2D side-scroller).

| Shape | Geometry & parameters | Platformer notes |
|---|---|---|
| `melee_arc` | Wedge in front of the caster: `arc_degrees` (default 120, range 60–270), `radius` tiles (0.75–2.5). Hits all valid targets inside the wedge. | Facing-relative; a wide arc sweeps above/below on slopes and stairs. |
| `line` | Straight rectangle/ray in facing: `length` tiles (2–12), `width` tiles (0.5–2), `pierce` (int or `all`). Resolves near-instantly. | Ignores gravity; good for level shots and beams. Blocked by solid geometry unless `pierce_terrain:false` default. |
| `projectile` | Travelling body: `speed` tiles/s (6–24), `range` tiles (4–16), `pierce` (0–`all`), `gravity` (bool — arcs like a lobbed arrow/dirk vs flat), `impact_radius` tiles (0 = single target; >0 hands off to an `aoe_circle` on impact). | The one shape affected by drop; arcing shots clear cover, flat shots are point-and-click. |
| `aoe_circle` | Disc: `radius` tiles (1–6), `origin` (`self` \| `reticle` \| `impact`), `reticle_range` tiles (for ground-targeted casts), optional `telegraph` delay s. | Ground-target reticle is clamped to `reticle_range`; telegraphs show the disc before it lands (elite/boss and player skills alike, P1). |
| `self` | The caster only. No range. | Buffs, stances, dashes/leaps, self-`heal`/`shield`. |
| `party` | All party members (including caster) within `radius` tiles (default 8). Party membership and range are `10_systems/social/PARTY.md`'s; **solo, `party` resolves to `self` only**. | Support/aura shape; never hits hostiles. |

Facing, aim input, and reticle control are `10_systems/CONTROLS.md`'s; this doc owns only the
resolved geometry. A skill's effect ops read these targets (`10_systems/SKILL_EFFECTS.md`); the
damage/hit math per target is `10_systems/COMBAT_FORMULA.md`'s.

## 7. Skill bar & loadout policy

- **All learned actives are usable** — there is no "spellbook vs slotted" split that forgets what
  you know. What is limited is the **quick-cast bar**: the number of actives bound to inputs at
  once.
- **Bar size and input mapping are owned by `10_systems/CONTROLS.md` / `10_systems/HUD.md`**
  (forward). First-pass assumption for content sizing: **8 skill slots** plus dedicated inputs for
  basic attack, dodge, and jump; the exact count/layout is those docs' call (Open Question).
- **Re-slotting is free out of combat** (in any map), instant from the bar UI; it is not a respec
  (no points move). Encourages situational loadouts (a boss set vs a clear set) without cost.
- **Passives are never slotted.** Once learned they are always-on and fold into stats through
  `10_systems/STATS.md` §7 (`passive_stat_bonus`) or fire automatically (`on_hit_proc`); they do
  not occupy bar slots (`10_systems/SKILL_EFFECTS.md`).
- **Summons persist off-bar.** A `summon_entity` skill is cast from a slot, but the summoned
  entity then lives independently until it dies or expires (`10_systems/SKILL_EFFECTS.md` cap 1–2);
  the slot returns to cooldown and can be re-slotted without dismissing the summon.

## 8. Authority

Skill-point totals, gates, cooldowns, `essence` costs, `level_data` resolution, and targeting
resolution are **server-authoritative** in the live build (`00_vision/PILLARS.md` P6; contract in
`10_systems/PERSISTENCE.md`); the solo client simulates them and may be corrected on sync. No
content file recomputes interpolation or cost — it declares rows and constants, and the runtime
(client-advisory, server-truth) resolves them.

## Open Questions

- **Skill-bar slot count** (first-pass 8) and input layout are owned by `10_systems/CONTROLS.md` /
  `10_systems/HUD.md`; if the platform button budget forces fewer, content that assumes 8 usable
  actives at once may need review. Flagged for the B/C gate.
- **Skill-point total** (+1/level, 299 at cap 300) is first-pass; the v3 Lv 40 **branch**
  (`10_systems/JOBS.md` §1) means a character accesses 13 line skills (6 first-job + one spec's 7) +
  4 novice, so the point-vs-rank ratio shifted from the v2 21-skill assumption. If playtesting shows
  characters feel starved or over-flush against the branched 13-skill kit, `10_systems/LEVELING.md`
  (owner of the trigger) and this doc jointly retune (e.g., a small advancement lump or a per-arc
  point cap). Default holds at flat +1/level.
- **Tile → pixel scale** for all §6 ranges inherits `10_systems/COMBAT_FORMULA.md` §10's open scale
  lock (`40_assets/ART_BIBLE.yaml`); numbers here are tile-relative and unaffected by the eventual
  px value, but reticle/aim feel can't be tuned until it lands.
- **Free skill respec with no `shards` cost** (§3) is the generous default; if `10_systems/ECONOMY.md`
  needs a nominal sink, a small fee may be added there without changing this doc's mechanics.
- **Cast/recovery windows** per skill interact with `haste` attack-speed (`10_systems/STATS.md` §5);
  whether `haste` also shortens skill cast/recovery (vs only basic attacks and `cooldown`) is a
  `10_systems/COMBAT_FORMULA.md` cadence call. Default: `haste` speeds basic attacks and movement,
  not skill cast times; flagged.
