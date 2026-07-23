# ENHANCEMENT.md — Emberstone Gear Enhancement (+1..+9)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ITEMS.md, 10_systems/SCROLLS.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/COMBAT_FORMULA.md, 10_systems/LEVELING.md, 10_systems/PERSISTENCE.md,
20_schemas/item.schema.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

Owner doc for **gear enhancement**: the `emberstone` material tiers, the `+1..+9` upgrade track,
the success/pity model, the stat gain per `+`, and where the fee and materials come from. The
stat *values* an item starts with are `10_systems/ITEMS.md` (§7–§9 base lines); this doc owns only
the **multiplier** enhancement layers on top, which STATS §2 then sums as part of `Σ*_gear`. The
`shards` fee schedule is `10_systems/ECONOMY.md`; emberstone drop rates are `10_systems/DROPS.md`.
Enhancement is cozy by design (`00_vision/PILLARS.md` P2): **no item is ever destroyed or
downgraded**, and worst-case cost is bounded by pity. **Affix-line modification is owned by
`10_systems/SCROLLS.md`; this doc's track scales base lines only (§4).**

## 1. Emberstone tiers → gear-band mapping

Five emberstone tiers (`item_etc_0193`–`0197`, `docs/ID_REGISTRY.md`), each covering two gear
tiers of the v3 twelve-tier ladder (`10_systems/ITEMS.md` §4). The stone tier must match the
item's tier band — you cannot enhance a T10 item with Emberstone I.

| Emberstone | ID | Enhances gear tiers | Item `req_level` range (`10_systems/ITEMS.md` §4) |
|---|---|---|---|
| Emberstone I | `item_etc_0193` | T1–T2 | 1–14 |
| Emberstone II | `item_etc_0194` | T3–T4 | 15–28 |
| Emberstone III | `item_etc_0195` | T5–T6 | 29–42 |
| Emberstone IV | `item_etc_0196` | T7–T8 | 43–56 |
| Emberstone V | `item_etc_0197` | T9–T10 | 57–70 |

T11–T12 (`req_level` 71–78, the Voidshore band) have **no matching stone yet** — coverage is an
open question (an Emberstone VI at the reserved `item_etc_0198` is proposed, not minted; see Open
Questions). One emberstone of the matching tier is consumed **per attempt** (success or fail). The visual
flavor of `emberstone` may be reskinned by an ART_BIBLE amendment (GLOSSARY note); the mechanic is
fixed here.

## 2. The enhancement track

Any single equip (every equip slot, `10_systems/ITEMS.md` §2) carries an `enhance_level` from `0`
(base) to `9`. The static `0`–`9` ceiling is the `enhance_max` field in `20_schemas/item.schema.md`;
the per-item runtime `enhance_level` is server-authoritative persisted state per §6 and
`10_systems/PERSISTENCE.md`. Each attempt targets the next `+`:

| Target `+` | Success | On failure |
|---|---|---|
| +1 … +5 | **100% (guaranteed)** | — (never fails) |
| +6 | 70% | no change to `+`, **no destruction, no downgrade** |
| +7 | 55% | no change to `+` |
| +8 | 40% | no change to `+` |
| +9 | 25% | no change to `+` |

Every attempt consumes one matching emberstone (§1) and the `shards` fee (§5), **whether it
succeeds or fails**. A failed attempt at +6..+9 leaves the item exactly where it was — the only
loss is the stone and the fee. This is the entire risk: `shards` and materials, never the item
(`00_vision/PILLARS.md` P2; contrast with the classic genre's destruction/downgrade loops, which
this deliberately rejects).

## 3. Pity model (bounds the risky band)

Applies only to the +6..+9 attempts (the +1..+5 band is already deterministic):

- **Soft pity.** Each consecutive **failure at the same target `+`** adds **+10 percentage
  points** to the next attempt's success chance at that `+`. The bonus resets to 0 the moment that
  `+` succeeds (and does not carry between different `+` levels).
- **Hard pity.** The **5th** attempt at any single `+` (i.e., after 4 failures) is a **guaranteed
  success**. This caps worst-case cost at 5 attempts per level.

Worked (+8 → +9, base 25%): attempts run 25% → 35% → 45% → 55% → 100%. Expected attempts ≈ **2.6**,
worst case **5**. A player can always look at the counter and know the maximum remaining cost — no
open-ended gambling (P1 readable, P2 cozy). The soft-pity counter is part of the item's persisted
state (§6), so it survives logout and is not farmable by re-equipping.

## 4. Stat gain per `+`

Each `+` adds a percentage of the item's **base lines** (`10_systems/ITEMS.md` §7–§9) — never of
its affix lines (§10 affixes stay fixed; only the base scales, keeping the math legible). The
guaranteed band adds +6% per level; the risky band adds +8% per level (bigger reward for the
gamble):

| `+` | per-level | cumulative base-line bonus |
|---|---|---|
| +1 | +6% | +6% |
| +2 | +6% | +12% |
| +3 | +6% | +18% |
| +4 | +6% | +24% |
| +5 | +6% | +30% |
| +6 | +8% | +38% |
| +7 | +8% | +46% |
| +8 | +8% | +54% |
| +9 | +8% | +62% |

**By slot** the cumulative % scales that slot's base line(s):

| Slot | Scaled base line(s) |
|---|---|
| `weapon` | `W` (`power` or `spellpower`) |
| `head`/`body`/`legs`/`boots`/`gloves` | `armor` **and** `warding` |
| `shield` | `armor` **and** `warding` |
| `overall` | `armor` **and** `warding` |
| `cape` | `warding` and `evasion` |
| `ring` | primary and `crit_rate` |
| `amulet` | primary and `crit_power` |

Worked: a T6 `blade` (base `W` 151, `10_systems/ITEMS.md` §7) at +9 adds +62% = +94 `power`
(total 245), exceeding a +0 T7 `blade` (196) — the enhancement chase leapfrogs one tier at the
top end. T6 is arc 1's top tier and T12 (Voidshore) the authored top of the ladder — T7–T12 are
arc 2, built (`10_systems/ITEMS.md` §4) — so **T12 +9 + boss uniques is the between-arcs endgame**
(`10_systems/LEVELING.md` §6); the leapfrog principle holds at every tier seam.
The added value enters `power`/`armor`/… as `Σ*_gear` per `10_systems/STATS.md` §2 and is subject
to that doc's soft caps (§6) for the percentage lines. This enhancement headroom is part of the
at-level `power_ref` assumption in `10_systems/COMBAT_FORMULA.md` §15.

## 5. Shard fee per attempt

Every attempt costs `shards`, paid to the enhancement NPC (a town smith interior,
`docs/WORLD_PLAN.md`). The **fee schedule is owned by `10_systems/ECONOMY.md` §3** — it rises with
both the gear tier and the target `+` (so the risky high-`+` band at high tiers is the economy's
main `shards` sink). This doc does not restate the numbers; it asserts only that: one fee is paid
per attempt (success or fail), the fee is a pure `shards` sink (no material refund on fail), and
the fee scales up-tier/up-`+` so enhancement remains a meaningful sink at cap without ever gating
progression behind luck (pity, §3, bounds the material and fee cost).

## 6. Emberstone acquisition & authority

- **Drops.** Emberstones drop from `elite` and `boss` monsters; the drop rates
  and which tier drops in which region are owned by `10_systems/DROPS.md` (§5 elite/boss table
  shapes) and keyed to the region's level band (`docs/WORLD_PLAN.md`). Emberstones are **not**
  vendor-purchasable at launch (they are a hunt reward, keeping the enhancement loop tied to play
  — `00_vision/PILLARS.md` P2/P3); see Open Questions.
- **Authority.** All rolls (success/fail), soft-pity counters, `enhance_level`, and fee/material
  consumption are **server-authoritative** in the live build (`00_vision/PILLARS.md` P6; contract
  `10_systems/PERSISTENCE.md`). The solo client may preview the odds and simulate an attempt, but
  the server is the source of truth on sync — no client-side "reroll until success."

## Open Questions

- Success rates (§2) and per-level stat gains (§4) are first-pass balance. If the +6..+9 band
  proves too swingy or too safe against the §5 fee, tune the odds and the soft-pity step (§3)
  before touching the stat-gain %s. Owner: this doc with `10_systems/ECONOMY.md`.
- Should a **transfer** exist to move an `enhance_level` (or its cost) from an outgrown item to its
  tier-up replacement, so the enhancement grind is not fully repeated each tier? Default: no
  transfer at launch (each item enhanced from +0). Flag as a possible cozy addition; would need an
  op in the enhancement NPC UI and a rule here.
- **T11–T12 emberstone coverage (§1).** The five stones map to T1–T10; the Voidshore tiers
  T11–T12 (`req_level` 71–78) are uncovered. `10_systems/ITEMS.md`'s Open Questions propose an
  **Emberstone VI** at the reserved `item_etc_0198` (VI → T11–T12, Lv 71–80) — not minted here;
  adopting it needs an `docs/ID_REGISTRY.md` commit. Owner: this doc with `10_systems/ITEMS.md`.
- §4's by-slot table still lists `shield` and `overall` rows — slots outside
  `10_systems/ITEMS.md` §2's nine (accepted debt, tracked in `docs/ID_REGISTRY.md`'s Open
  Questions); reconcile if the slot set is ever revisited.
- Emberstone vendor purchase / crafting from region materials (`item_etc` per region) is deferred;
  if added it belongs to `10_systems/ECONOMY.md` (a `shards`/material sink) referencing this doc's
  tier mapping (§1), not a new drop rule.
- Whether the arc-2 raids (`raid_deepfrost`/`raid_voidtide`, `10_systems/social/RAID.md`) drop a
  distinct high-tier emberstone or reuse Emberstone V is deferred (`10_systems/DROPS.md`);
  default reuses V (and VI if adopted).
- Enhancement above +9 (e.g., a +10..+12 "starforce" extension) is explicitly **not** in scope this
  pass; if ever added it must not break the `10_systems/COMBAT_FORMULA.md` §13/§15 balance surface
  (the anti-power-creep concern of `00_vision/PILLARS.md`).
