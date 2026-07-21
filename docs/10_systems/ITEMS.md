# ITEMS.md — Item Categories, Equipment, Rarity & the Stat-Line Budget

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/ELEMENTS.md,
10_systems/JOBS.md, 10_systems/ENHANCEMENT.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/INVENTORY.md, 10_systems/STATUS_EFFECTS.md, 10_systems/SKILL_EFFECTS.md,
20_schemas/item.schema.md, 40_assets/ART_BIBLE.yaml, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

Owner doc for **items**: the three categories, the nine equipment slots and four weapon types
(semantics for the GLOSSARY tokens whose owner is this doc), the `rarity` ladder, and — the
load-bearing part — the **equip stat-line budget** every equip is built from and that Phase D
copies verbatim. Stat *definitions* and the formulas that sum gear into derived values are
`10_systems/STATS.md` (this doc supplies the `W` and `Σ*_gear` numbers STATS §2 consumes, never
the combination rule); damage *math* is `10_systems/COMBAT_FORMULA.md`; enhancement is
`10_systems/ENHANCEMENT.md`; drop rates `10_systems/DROPS.md`; prices `10_systems/ECONOMY.md`;
carry/stack rules `10_systems/INVENTORY.md`. This doc never restates those.

## 1. Categories (three)

| Category | ID prefix (`docs/ID_REGISTRY.md`) | Contents | Owner of behavior |
|---|---|---|---|
| `equip` | `item_equip_NNNN` | Worn gear (§2). Unstacked. | This doc + `10_systems/ENHANCEMENT.md` |
| `use` | `item_use_NNNN` | Consumables: tonics (restore `life`/`essence`), cleanses (remove a `10_systems/STATUS_EFFECTS.md` cleanse tag), scrolls (utility/return), foods (temporary buffs). The 16 well-known IDs `0001`–`0016` are reserved in `docs/ID_REGISTRY.md`. | Effect ops `10_systems/SKILL_EFFECTS.md`; restore/buff magnitudes authored Phase D; prices `10_systems/ECONOMY.md` |
| `etc` | `item_etc_NNNN` | Non-worn: monster materials (16/region), quest items, and enhancement materials Emberstone I–V (`item_etc_0193`–`0197`, `10_systems/ENHANCEMENT.md`). Mostly vendor/trade value. | This doc (category); materials themed by `docs/WORLD_PLAN.md` region |

`equip` is fully specified here. `use`/`etc` items carry no stat-line budget; their functional
values (restore amounts, buff magnitudes, material vendor price) are authored in Phase D against
`20_schemas/item.schema.md` and priced by `10_systems/ECONOMY.md`.

## 2. Equipment slots (nine)

Nine worn slots; one item each. Each slot carries a fixed **base line** set (§6). Ordering used
for the armor budget is `body > legs > head > boots = gloves` (torso protects most).

| Slot | Worn | Base line(s) | Equip restriction |
|---|---|---|---|
| `weapon` | main hand | `power` or `spellpower` = `W` (§7) | weapon **type** gates by job line (§3) + `req_level` |
| `head` | head | `armor` + `warding` | `req_level` only (class-agnostic, `00_vision/SCOPE.md`) |
| `body` | torso | `armor` + `warding` | `req_level` |
| `legs` | legs | `armor` + `warding` | `req_level` |
| `boots` | feet | `armor` + `warding` | `req_level` |
| `gloves` | hands | `armor` + `warding` | `req_level` |
| `cape` | back | `warding` + `evasion` | `req_level` |
| `ring` | finger (×1) | one primary + `crit_rate` | `req_level` |
| `amulet` | neck | one primary + `crit_power` | `req_level` |

Armor and accessory slots are **class-agnostic** (`00_vision/SCOPE.md`): any line may wear any
piece that meets `req_level`. Build identity on armor comes from **which primary** its affixes
roll (the "stat lean," §10), not from a class lock.

## 3. Weapon types (four)

One weapon type per job line (`10_systems/JOBS.md` §0). A weapon of a given type is equippable
only by its line; before the 1st advancement (Lv 8) a `novice` wields a **granted starter weapon**
(`power` `W`≈4, `neutral`; not one of the 40 line weapons — see `10_systems/JOBS.md` §6).

| Type | Line (`10_systems/JOBS.md`) | Governing primary | Feeds |
|---|---|---|---|
| `blade` | `bulwark` | `might` | `power` |
| `bow` | `keeneye` | `finesse` | `power` |
| `dirk` | `flicker` | `fortune` | `power` (the double-dip) |
| `staff` | `weaver` | `focus` | `spellpower` |

How a weapon's `W` and its governing primary combine into `power`/`spellpower` — including the
`dirk`/`fortune` double-dip — is owned by `10_systems/STATS.md` §2.1 (not restated here). The
type→line pairing is fixed by GLOSSARY/`10_systems/JOBS.md`; this doc owns its **enforcement**
(equip restriction). `W` is the weapon's authored attack value (§7).

## 4. Tier bands and level requirements

Ten gear tiers **T1–T10**, each keyed to a required level aligned to region entry
(`docs/WORLD_PLAN.md`). Weapons and armor share the tier grid; accessories use the same grid
(Phase D may author accessories at fewer bands, §12). The **Lv 8 first advancement**
(`10_systems/JOBS.md`) is the gate at which a character can first equip a line weapon (it will be
past T1's `req_level` 1 by then). There is **no T11**: at Lv 100 the endgame power source is
**T10 + enhancement (`10_systems/ENHANCEMENT.md`) + boss uniques (§11)**, matching the gear-only
post-cap policy (`10_systems/LEVELING.md` §6).

| Tier | `req_level` | Region context (`docs/WORLD_PLAN.md`) |
|---|---|---|
| T1 | 1 | Emberfoot (starter) |
| T2 | 10 | Verdant |
| T3 | 20 | Tidewatch |
| T4 | 30 | Sunken |
| T5 | 40 | Ashfall |
| T6 | 50 | Frostpeak |
| T7 | 60 | Gloomwood |
| T8 | 70 | Clockwork |
| T9 | 80 | Arcane Reach |
| T10 | 90 | Voidshore / Rift-ready |

**ID-block layout** within `item_equip` (`docs/ID_REGISTRY.md` owns the ranges; this is the
intra-block convention): weapons `0001`–`0040` = 10 tiers × 4 types in line order
(`blade 0001`–`0010`, `bow 0011`–`0020`, `staff 0021`–`0030`, `dirk 0031`–`0040`); armor
`0041`–`0140` = 5 slots × tiers (`head 0041`–, `body`, `legs`, `boots`, `gloves`, then reserved
growth for intermediate/region-variant pieces); accessories `0141`–`0180` = `cape`/`ring`/`amulet`
× tiers; boss uniques `0201`–`0230` (§11).

## 5. Rarity ladder

Five rarities (GLOSSARY; owner this doc). Rarity does **not** change a weapon's base `W` or a
piece's base defense — it adds **affix lines** (§10). Colors are locked in
`40_assets/ART_BIBLE.yaml` `rarity_code` (referenced, not restated).

| `rarity` | Affix lines (§10) | Typical source (`10_systems/DROPS.md`) |
|---|---|---|
| `common` | 0 | vendor stock, `normal` drops |
| `uncommon` | 1 | `normal`/`elite` drops, region pools |
| `rare` | 2 | `elite`/`boss` pools |
| `epic` | 3 | `boss` pools, boss uniques (§11) |
| `legendary` | 4 (+1 flourish on uniques) | `boss`/raid pools, boss uniques (§11) |

## 6. Stat model: base lines + affix lines

Every equip = **base lines** (rarity-independent, fixed by slot × tier; §7–§9) **plus** **affix
lines** (rarity-driven count and magnitude; §10). A `common` item is base-only. All lines are flat
values summed by `10_systems/STATS.md` §2 as `W` / `Σ*_gear` — this doc owns the numbers, STATS
owns the combination and any soft caps (`10_systems/STATS.md` §6).

**Primary-equivalent (pe) weights** normalize heterogeneous lines to one budget unit (1 pe ≈ the
value of +1 primary), used only as the balance/validation checksum (§10, `docs/VALIDATION.md`):

| Line | pe per unit | Line | pe per unit |
|---|---|---|---|
| +1 primary | 1.00 | +1 `precision` | 0.20 |
| +1 `power`/`spellpower` | 0.50 | +1% `crit_rate` | 3.00 |
| +1 `armor` | 0.10 | +0.01 `crit_power` | 0.30 |
| +1 `warding` | 0.10 | +1% `evasion` | 2.50 |
| +1 `life` | 0.03 | +1 `haste` | 1.50 |
| +1 `essence` | 0.06 | | |

## 7. Weapon `power` / staff `spellpower` by tier (base `W`)

`W` is tier-driven and rarity-independent (P1 legibility: a `legendary` and a `common` T6 `blade`
share `W`; the `legendary` differs by affixes). Physical types (`blade`/`bow`/`dirk`) feed
`power`; `staff` feeds `spellpower`, set ~10% higher as a first-pass ranged-caster/`essence`-cost
lever. These values, plus gear affix `power` and the primary contribution, are tuned so an
at-level geared character reaches the `power_ref` offense of `10_systems/COMBAT_FORMULA.md` §15
(that doc's OQ owns retuning `mult m` if they drift; `W` is never retuned to break the band).

| Tier | `req_level` | `W` (`blade`/`bow`/`dirk` → `power`) | `W` (`staff` → `spellpower`) |
|---|---|---|---|
| T1 | 1 | 8 | 9 |
| T2 | 10 | 30 | 33 |
| T3 | 20 | 68 | 74 |
| T4 | 30 | 116 | 127 |
| T5 | 40 | 176 | 193 |
| T6 | 50 | 246 | 270 |
| T7 | 60 | 327 | 359 |
| T8 | 70 | 418 | 460 |
| T9 | 80 | 522 | 574 |
| T10 | 90 | 636 | 700 |

## 8. Armor / warding base by slot × tier

Formula is authoritative; the checksum table samples it. `K(L)` is the mitigation denominator
owned by `10_systems/COMBAT_FORMULA.md` §5 (defined there, not restated) — a full at-level 5-piece
set targets `Σarmor ≈ K(L)/3` (≈ 25% physical reduction in that doc's band). Pieces lean physical
(`warding` = 70% of `armor`); a caster tops up `warding` via `focus` and `cape` (§9).

```
armor_base(slot, L)   = round( w[slot] · K(L) / 3 )        # K(L) per COMBAT_FORMULA §5
warding_base(slot, L) = round( 0.70 · armor_base(slot, L) )
w[slot]: body 0.28 · legs 0.24 · head 0.18 · boots 0.15 · gloves 0.15   (Σ = 1.0)
```

| Slot | Lv 1 | Lv 10 | Lv 30 | Lv 50 | Lv 70 | Lv 90 |
|---|---|---|---|---|---|---|
| body `armor`/`warding` | 7 / 5 | 23 / 16 | 61 / 43 | 98 / 69 | 135 / 95 | 173 / 121 |
| legs | 6 / 4 | 20 / 14 | 52 / 36 | 84 / 59 | 116 / 81 | 148 / 104 |
| head | 4 / 3 | 15 / 11 | 39 / 27 | 63 / 44 | 87 / 61 | 111 / 78 |
| boots | 4 / 3 | 13 / 9 | 33 / 23 | 53 / 37 | 73 / 51 | 93 / 65 |
| gloves | 4 / 3 | 13 / 9 | 33 / 23 | 53 / 37 | 73 / 51 | 93 / 65 |
| **5-set `armor`** | **25** | **84** | **218** | **351** | **484** | **618** |

## 9. Accessory base by tier

Accessories give primaries and crit (`cape` is the defensive outlier: `warding` + `evasion`).
`ring`/`amulet` each roll **one** primary of the wearer's choosing at author time (any of the four
— the accessory stat lean).

```
primary_base(L) = round( 2 + 0.35·L )     # ring & amulet primary
cape_warding(L) = round( 0.15 · K(L) / 3 )     # K(L) per COMBAT_FORMULA §5
```

| Tier band | `ring` primary / `crit_rate` | `amulet` primary / `crit_power` | `cape` `warding` / `evasion` |
|---|---|---|---|
| T1 (Lv 1) | 2 / 1.0% | 2 / +0.03 | 4 / 1.0% |
| T2 (Lv 10) | 6 / 1.0% | 6 / +0.03 | 13 / 1.0% |
| T3 (Lv 20) | 9 / 1.5% | 9 / +0.05 | 22 / 1.5% |
| T4 (Lv 30) | 13 / 1.5% | 13 / +0.05 | 33 / 1.5% |
| T5 (Lv 40) | 16 / 2.0% | 16 / +0.07 | 43 / 2.0% |
| T6 (Lv 50) | 20 / 2.0% | 20 / +0.07 | 53 / 2.0% |
| T7 (Lv 60) | 23 / 2.5% | 23 / +0.09 | 63 / 2.5% |
| T8 (Lv 70) | 27 / 2.5% | 27 / +0.09 | 73 / 2.5% |
| T9 (Lv 80) | 30 / 3.0% | 30 / +0.12 | 83 / 3.0% |
| T10 (Lv 90) | 34 / 3.0% | 34 / +0.12 | 93 / 3.0% |

`crit_rate`/`crit_power`/`evasion` from accessories feed `10_systems/STATS.md` §2 and are
soft-capped there (§6) — stacking beyond the band is self-limiting, no special rule here.

## 10. Affix lines — the stat-line budget (Phase D copies this)

Rarity adds **N affix lines** (§5). Each line is one entry from the **affix menu** below (concrete
per-tier magnitudes), subject to two constraints Phase D and `docs/VALIDATION.md` enforce: (a) no
line exceeds the **per-line pe cap**; (b) the item's total affix pe ≤ the **rarity affix budget**.
This is the "total stat budget and how it splits" — base (§7–§9) + up to N menu lines.

**Affix menu** — magnitude of a single rolled line (`u(L) = round(1.5 + 0.22·L)` is the primary
unit):

| Affix line | Lv 1 | Lv 10 | Lv 30 | Lv 50 | Lv 70 | Lv 90 |
|---|---|---|---|---|---|---|
| +primary (`= u`) | 2 | 4 | 8 | 12 | 17 | 21 |
| +`power`/`spellpower` (`2.2u`) | 4 | 9 | 18 | 26 | 37 | 46 |
| +`life` (`11u`) | 22 | 44 | 88 | 132 | 187 | 231 |
| +`essence` (`5u`) | 10 | 20 | 40 | 60 | 85 | 105 |
| +`armor` or +`warding` (`4u`) | 8 | 16 | 32 | 48 | 68 | 84 |
| +`precision` (`3u`) | 6 | 12 | 24 | 36 | 51 | 63 |
| +`crit_rate` | 1.0% | 1.0% | 1.5% | 2.0% | 2.5% | 3.0% |
| +`crit_power` | +0.03 | +0.03 | +0.03 | +0.05 | +0.05 | +0.07 |
| +`evasion` | 1.0% | 1.0% | 1.0% | 1.5% | 1.5% | 2.0% |
| +`haste` (`round(1+0.05L)`) | 1 | 2 | 3 | 4 | 5 | 6 |

**Rarity affix budget** — line count and total pe ceiling (`cap(L) = round(1.4·u(L))` = per-line
pe cap; total = count × cap):

| `rarity` | Lines | pe budget @ Lv 1 | @ Lv 30 | @ Lv 50 | @ Lv 70 | @ Lv 90 |
|---|---|---|---|---|---|---|
| `common` | 0 | 0 | 0 | 0 | 0 | 0 |
| `uncommon` | 1 | 3 | 11 | 17 | 24 | 29 |
| `rare` | 2 | 6 | 22 | 34 | 48 | 58 |
| `epic` | 3 | 9 | 33 | 51 | 72 | 87 |
| `legendary` | 4 | 12 | 44 | 68 | 96 | 116 |

**Affix eligibility by slot** (keeps base identity intact): `weapon` rolls
`power`/`spellpower`/primary/`crit_rate`/`crit_power`/`haste`; armor rolls
primary/`life`/`armor`/`warding`/`haste`; `gloves` may also roll `crit_rate`/`precision`;
`cape` rolls `evasion`/`warding`/`haste`; `ring`/`amulet` roll primary/`crit_rate`/`crit_power`/
`power`/`spellpower`. Armor rolling a primary is the "stat lean" (§2).

**Worked example** — `rare` T6 (Lv 50) `body` armor: base 98 `armor` / 69 `warding`
(16.7 pe); affixes = 2 lines, budget 34 pe: e.g. +12 `might` (12 pe) + +132 `life` (3.96 pe) =
16 pe ≤ 34, per-line cap 17 not exceeded. Total item pe ≈ 32.7.

## 11. Boss unique gear

Each of the 15 bosses (`docs/WORLD_PLAN.md`, 11 region + 4 raid) owns **two** uniques at
`item_equip_0201`–`0230` (mapping owned by `docs/ID_REGISTRY.md`: boss #n → `0199+2n`, `0200+2n`).
Rules:

- **Rarity `epic` or `legendary`.** `req_level` = the boss's level band; slot/type is the unique's
  own (a boss may own e.g. one `weapon` + one `amulet`).
- Standard base line(s) for that slot × tier (§7–§9) **plus 1–2 flourish lines** in place of / in
  addition to ordinary affixes. A flourish is a signature affix that may exceed the §10 per-line
  pe cap by up to **×1.5** (the aspirational-drop allowance) and may be a small `on_hit_proc` /
  `passive_stat_bonus` effect expressed only through existing ops (`10_systems/SKILL_EFFECTS.md`
  — no new rules, P4).
- Total item pe ≤ the `legendary` budget (§10) × 1.5 for uniques. No unique introduces a
  per-element resistance or any token outside GLOSSARY (`10_systems/ELEMENTS.md` OQ).
- Dropped from their boss's table (`10_systems/DROPS.md` boss/raid shape); first regional-boss
  clear grants one of its uniques (bad-luck protection, `10_systems/DROPS.md`).

## 12. Batch-table file convention (formalized by `20_schemas/item.schema.md`)

Items are authored in **category tables**, not one file per item. Each table file:

```
---
id: item_table_<name>              # e.g. item_table_weapons, item_table_armor, item_table_uniques
schema: 20_schemas/item.schema.md
references: [ 10_systems/ITEMS.md, ... ]
---
items:
  - id: item_equip_0001            # each entry's own reserved ID (docs/ID_REGISTRY.md)
    name: ...
    category: equip                # equip | use | etc
    slot: weapon                   # equip: one of §2; omit for use/etc
    weapon_type: blade             # equip weapons only (§3)
    tier: 1
    req_level: 1
    rarity: common
    base: { power: 8 }             # §7–§9 base lines
    affixes: []                    # §10 rolled lines (≤ rarity count / pe budget)
    flavor: "..."                  # ≤2 sentences (docs/VALIDATION.md)
  - id: item_equip_0002
    ...
```

Grouping (aligned to existing `50_content/items/` tree): `equip/item_table_weapons`,
`equip/item_table_armor`, `equip/item_table_accessories`, `equip/item_table_uniques`;
`use/item_table_use`; `etc/item_table_etc_<region_slug>` (16/region) + `etc/item_table_emberstones`
(`item_etc_0193`–`0197`). `20_schemas/item.schema.md` (Phase C) owns the exact field list, types,
and required/optional flags; this doc owns only the table wrapper and the meaning of `base`/
`affixes`/`tier`/`rarity`. Field values reference only GLOSSARY tokens (`docs/VALIDATION.md` §1–§3).

## Open Questions

- SCOPE (`00_vision/SCOPE.md`) lists "~80 armor" and "~24 accessories"; the §4 clean grid yields 50
  core armor (5 slots × 10 tiers) + reserved growth and 30 core accessories. Phase D fills toward
  the SCOPE counts using the reserved `item_equip` ranges (intermediate/region-variant pieces on
  the same §8/§9 value curve, interpolated by `req_level`); exact per-slot SKU count is a Phase D
  call bounded by `docs/ID_REGISTRY.md`. Flagged for the content pass.
- `W` and the §10 affix budgets assume the `power_ref`/`mult m` reference of
  `10_systems/COMBAT_FORMULA.md` §15; if the balance pass finds an at-level geared character lands
  far off `power_ref`, retune `mult m` there (never `normal_life`), and revisit the staff +10%
  `W` lever here. Joint ITEMS/COMBAT_FORMULA call at the C/D gates.
- The `dirk`/`fortune` double-dip (`10_systems/STATS.md` §2.1 OQ) may want a lower `dirk` `W` or a
  capped `power` affix on `dirk` weapons; default keeps the uniform table. Owner: joint
  `10_systems/STATS.md` / `10_systems/COMBAT_FORMULA.md`.
- pe weights (§6) are first-pass balance; if `crit_rate`/`haste` prove over/under-valued after the
  §15 rotation is authored (`10_systems/SKILL_SYSTEM.md`), retune the weight, not the base tables.
- Whether a `legendary` gear affix should ever grant a per-element defense (currently forbidden,
  `10_systems/ELEMENTS.md` OQ) — default no; would require a GLOSSARY Provisional token.
- Set bonuses (wearing N pieces of a themed group) are **not** in this pass; if wanted they attach
  to boss-unique groups (§11) via `passive_stat_bonus` and need a `set_id` field in
  `20_schemas/item.schema.md`. Flagged, not designed.
