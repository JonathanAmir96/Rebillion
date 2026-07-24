# ITEMS.md — Item Categories, Equipment, Rarity & the Stat-Line Budget

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/ELEMENTS.md,
10_systems/JOBS.md, 10_systems/ENHANCEMENT.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/INVENTORY.md, 10_systems/STATUS_EFFECTS.md, 10_systems/SKILL_EFFECTS.md,
10_systems/social/RAID.md, 20_schemas/item.schema.md, 40_assets/ART_BIBLE.yaml,
docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

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

### 1.1 Consumable restore tiers (the tonic ladder)

`use` tonics restore `life`/`essence` in flat amounts that step up in **restore tiers**; each tier
serves a level band and is meant to be out-leveled as its flat restore stops keeping pace
(`10_systems/ECONOMY.md` §4.1). This doc owns the **tier → level-band binding** (delegated here by
`docs/ID_REGISTRY.md` §use); the per-tier `shards` price is `10_systems/ECONOMY.md` §4.1 and the
flat restore magnitudes are Phase D use-item data. The v3 ladder is **seven tiers**, each a
`life`/`essence` pair — five arc-1 tiers (`item_use_0001`–`0010`, Lesser→Prime) plus two arc-2
tiers minted from the reserved `item_use_0017`–`0060` range (raid consumables, owner
`10_systems/social/RAID.md`, draw from the same reserved range above these — reference only):

| Tier | Name (Life / Essence pair) | IDs (life / essence) | Serves band | Arc |
|---|---|---|---|---|
| 1 | Lesser | `0001` / `0006` | Lv 1–9 | 1 |
| 2 | (base) Tonic | `0002` / `0007` | Lv 10–18 | 1 |
| 3 | Greater | `0003` / `0008` | Lv 19–27 | 1 |
| 4 | Superior | `0004` / `0009` | Lv 28–36 | 1 |
| 5 | Prime | `0005` / `0010` | Lv 37–42 (arc-1 top) | 1 |
| 6 | **Sovereign** | `0017` / `0018` | Lv 40–61 | 2 |
| 7 | **Mythic** | `0019` / `0020` | Lv 62–80+ | 2 |

The Lv 40–42 overlap between Prime and Sovereign is the intended arc-1→arc-2 handoff (both are
viable there). Arc-1 bands are compressed to the authored Lv 1–42 arc (the v2 re-scope;
`docs/ID_REGISTRY.md` §use); `10_systems/ECONOMY.md` §4.1 still carries the pre-v2 Lv-100 bands and
prices only through Prime, and must follow this binding and add price rows for Sovereign/Mythic
(Open Questions). Cleanses, scrolls, and foods (`item_use_0011`–`0016`, plus Phase D specialties in
`0021`–`0060`) are un-tiered and not on this ladder.

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

Twelve gear tiers **T1–T12**, each keyed to a required level aligned to region entry
(`docs/WORLD_PLAN.md`), following `req_level(tier) = 1 + 7·(tier − 1)`. The ladder spans the two
authored arcs: **T1–T6** (arc 1, Lv 1–42) and **T7–T12** (arc 2, Lv 40–80). Weapons and armor
share the tier grid; accessories use the same grid (Phase D may author accessories at fewer bands,
§12). The **Lv 8 first advancement** (`10_systems/JOBS.md`) is the gate at which a character can
first equip a line weapon (past T1's `req_level` 1 by then, at roughly T2). At the top of each arc
the power source is **the arc's top tier + enhancement (`10_systems/ENHANCEMENT.md`) + boss uniques
(§11)**; there is no tier above T12 in the authored design — **Lv 80 is the between-arcs plateau**,
and the game's Lv 300 cap is future-arc design (`00_vision/SCOPE.md`) that will extend this ladder
rather than replace it.

| Tier | `req_level` | Arc | Region context (`docs/WORLD_PLAN.md`) |
|---|---|---|---|
| T1 | 1 | 1 | Emberfoot Isle (starter) |
| T2 | 8 | 1 | Harthmoor ring entry (ferry, 1st advancement) |
| T3 | 15 | 1 | Harthmoor ring (mid) |
| T4 | 22 | 1 | Harthmoor ring |
| T5 | 29 | 1 | Harthmoor ring (upper) |
| T6 | 36 | 1 | Harthmoor ring / Clockwork approach (arc-1 top) |
| T7 | 43 | 2 | Frostpeak Isle (Lv 40–55) |
| T8 | 50 | 2 | Frostpeak Isle |
| T9 | 57 | 2 | Arcane Reach (Lv 53–68) |
| T10 | 64 | 2 | Arcane Reach |
| T11 | 71 | 2 | Voidshore (Lv 66–80) |
| T12 | 78 | 2 | Voidshore (arc-2 top) |

Exact per-region level bands are owned by `docs/WORLD_PLAN.md`; the arc-2 island bands cited above
are the v3 owner revision (2026-07-23).

**ID-block layout** within `item_equip` (`docs/ID_REGISTRY.md` owns the ranges; this is the
intra-block convention). **Arc 1 (`0001`–`0180`):** weapons `0001`–`0040` = 4 lines × 6 tiers,
contiguous by line as minted in `50_content/items/equip/weapons.yaml` (`blade 0001`–`0006`,
`bow 0007`–`0012`, `staff 0013`–`0018`, `dirk 0019`–`0024`, each T1→T6; the block's reserve is
the single unminted tail `0025`–`0040` — intra-line growth, nothing minted there per
`docs/ID_REGISTRY.md`); armor `0041`–`0140` = 5 slots
× 6 tiers (`head`, `body`, `legs`, `boots`, `gloves`, then reserved growth for intermediate/
region-variant pieces); accessories `0141`–`0180` = `cape`/`ring`/`amulet` × tiers. **Arc 2
(`0231`–`0300`, re-blocked from the old `0231`–`0300` growth reserve — no content was ever minted
there, so re-blocking is legal; proposed to `docs/ID_REGISTRY.md`, see Open Questions):** weapons
`0231`–`0254` (4 lines × T7–T12), armor `0255`–`0284` (5 slots × T7–T12), accessories `0285`–`0300`
(16). Boss uniques `0201`–`0222` (§11).

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

`W` follows the closed-form curve `W_phys(L) = round(0.055·L² + 2.05·L + 6)` (with
`L = req_level`) and `W_staff(L) = round(1.10·W_phys(L))` — the table is the per-tier checksum. The
curve is calibrated to `level`, not to tier ordinal, so the v2/v3 re-scope (arc-1 tiers compressed
onto Lv 1–36, arc-2 tiers Lv 43–78) preserves the at-level `power` a character carries at any given
level (the `power_ref` relationship, §7 prose and Open Questions):

| Tier | `req_level` | `W` (`blade`/`bow`/`dirk` → `power`) | `W` (`staff` → `spellpower`) |
|---|---|---|---|
| T1 | 1 | 8 | 9 |
| T2 | 8 | 26 | 29 |
| T3 | 15 | 49 | 54 |
| T4 | 22 | 78 | 86 |
| T5 | 29 | 112 | 123 |
| T6 | 36 | 151 | 166 |
| T7 | 43 | 196 | 216 |
| T8 | 50 | 246 | 271 |
| T9 | 57 | 302 | 332 |
| T10 | 64 | 362 | 398 |
| T11 | 71 | 429 | 472 |
| T12 | 78 | 501 | 551 |

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

Sample columns span both arcs (Lv 1 = T1, 22 = T4, 36 = T6 arc-1 top, 50 = T8, 64 = T10, 78 = T12
arc-2 top); intermediate tiers interpolate on the same formula.

| Slot | Lv 1 | Lv 22 | Lv 36 | Lv 50 | Lv 64 | Lv 78 |
|---|---|---|---|---|---|---|
| body `armor`/`warding` | 7 / 5 | 46 / 32 | 72 / 50 | 98 / 69 | 124 / 87 | 150 / 105 |
| legs | 6 / 4 | 39 / 27 | 62 / 43 | 84 / 59 | 106 / 74 | 129 / 90 |
| head | 4 / 3 | 29 / 20 | 46 / 32 | 63 / 44 | 80 / 56 | 97 / 68 |
| boots | 4 / 3 | 25 / 18 | 39 / 27 | 52 / 36 | 66 / 46 | 80 / 56 |
| gloves | 4 / 3 | 25 / 18 | 39 / 27 | 52 / 36 | 66 / 46 | 80 / 56 |
| **5-set `armor`** | **25** | **164** | **258** | **349** | **442** | **536** |

## 9. Accessory base by tier

Accessories give primaries and crit (`cape` is the defensive outlier: `warding` + `evasion`).
`ring`/`amulet` each roll **one** primary of the wearer's choosing at author time (any of the four
— the accessory stat lean).

```
primary_base(L) = round( 2 + 0.35·L )     # ring & amulet primary
cape_warding(L) = round( 0.15 · K(L) / 3 )     # K(L) per COMBAT_FORMULA §5
```

`crit_rate`/`evasion` step +0.5% every two tiers (1.0% → 3.5%); `crit_power` steps
+0.03/+0.05/+0.07/+0.09/+0.12/+0.15 by tier pair.

| Tier band | `ring` primary / `crit_rate` | `amulet` primary / `crit_power` | `cape` `warding` / `evasion` |
|---|---|---|---|
| T1 (Lv 1) | 2 / 1.0% | 2 / +0.03 | 4 / 1.0% |
| T2 (Lv 8) | 5 / 1.0% | 5 / +0.03 | 11 / 1.0% |
| T3 (Lv 15) | 7 / 1.5% | 7 / +0.05 | 18 / 1.5% |
| T4 (Lv 22) | 10 / 1.5% | 10 / +0.05 | 25 / 1.5% |
| T5 (Lv 29) | 12 / 2.0% | 12 / +0.07 | 32 / 2.0% |
| T6 (Lv 36) | 15 / 2.0% | 15 / +0.07 | 39 / 2.0% |
| T7 (Lv 43) | 17 / 2.5% | 17 / +0.09 | 46 / 2.5% |
| T8 (Lv 50) | 20 / 2.5% | 20 / +0.09 | 52 / 2.5% |
| T9 (Lv 57) | 22 / 3.0% | 22 / +0.12 | 59 / 3.0% |
| T10 (Lv 64) | 24 / 3.0% | 24 / +0.12 | 66 / 3.0% |
| T11 (Lv 71) | 27 / 3.5% | 27 / +0.15 | 73 / 3.5% |
| T12 (Lv 78) | 29 / 3.5% | 29 / +0.15 | 80 / 3.5% |

`crit_rate`/`crit_power`/`evasion` from accessories feed `10_systems/STATS.md` §2 and are
soft-capped there (§6) — stacking beyond the band is self-limiting, no special rule here.

## 10. Affix lines — the stat-line budget (Phase D copies this)

Rarity adds **N affix lines** (§5). Each line is one entry from the **affix menu** below (concrete
per-tier magnitudes), subject to two constraints Phase D and `docs/VALIDATION.md` enforce: (a) no
line exceeds the **per-line pe cap**; (b) the item's total affix pe ≤ the **rarity affix budget**.
This is the "total stat budget and how it splits" — base (§7–§9) + up to N menu lines.

**Affix menu** — magnitude of a single rolled line (`u(L) = round(1.5 + 0.22·L)` is the primary
unit):

| Affix line | Lv 1 | Lv 22 | Lv 36 | Lv 50 | Lv 64 | Lv 78 |
|---|---|---|---|---|---|---|
| +primary (`= u`) | 2 | 6 | 9 | 12 | 16 | 19 |
| +`power`/`spellpower` (`2.2u`) | 4 | 13 | 20 | 26 | 35 | 42 |
| +`life` (`11u`) | 22 | 66 | 99 | 132 | 176 | 209 |
| +`essence` (`5u`) | 10 | 30 | 45 | 60 | 80 | 95 |
| +`armor` or +`warding` (`4u`) | 8 | 24 | 36 | 48 | 64 | 76 |
| +`precision` (`3u`) | 6 | 18 | 27 | 36 | 48 | 57 |
| +`crit_rate` | 1.0% | 1.5% | 1.5% | 2.0% | 2.5% | 3.0% |
| +`crit_power` | +0.03 | +0.03 | +0.03 | +0.05 | +0.07 | +0.07 |
| +`evasion` | 1.0% | 1.0% | 1.0% | 1.5% | 1.5% | 2.0% |
| +`haste` (`round(1+0.05L)`) | 1 | 2 | 3 | 4 | 4 | 5 |

**Rarity affix budget** — line count and total pe ceiling (`cap(L) = round(1.4·u(L))` = per-line
pe cap; total = count × cap):

| `rarity` | Lines | pe budget @ Lv 1 | @ Lv 22 | @ Lv 36 | @ Lv 50 | @ Lv 64 | @ Lv 78 |
|---|---|---|---|---|---|---|---|
| `common` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `uncommon` | 1 | 3 | 8 | 13 | 17 | 22 | 27 |
| `rare` | 2 | 6 | 16 | 26 | 34 | 44 | 54 |
| `epic` | 3 | 9 | 24 | 39 | 51 | 66 | 81 |
| `legendary` | 4 | 12 | 32 | 52 | 68 | 88 | 108 |

**Affix eligibility by slot** (keeps base identity intact): `weapon` rolls
`power`/`spellpower`/primary/`crit_rate`/`crit_power`/`haste`; armor rolls
primary/`life`/`armor`/`warding`/`haste`; `gloves` may also roll `crit_rate`/`precision`;
`cape` rolls `evasion`/`warding`/`haste`; `ring`/`amulet` roll primary/`crit_rate`/`crit_power`/
`power`/`spellpower`. Armor rolling a primary is the "stat lean" (§2).

**Worked example** — `rare` T8 (Lv 50) `body` armor: base 98 `armor` / 69 `warding`
(16.7 pe); affixes = 2 lines, budget 34 pe: e.g. +12 `might` (12 pe) + +132 `life` (3.96 pe) =
16 pe ≤ 34, per-line cap 17 not exceeded. Total item pe ≈ 32.7.

## 11. Boss unique gear

Each of the 11 bosses (`docs/WORLD_PLAN.md`: 8 arc-1 region bosses + 3 arc-2 island bosses, one
per new island) owns **two** uniques at `item_equip_0201`–`0222` (mapping owned by
`docs/ID_REGISTRY.md`: boss #n → `0199+2n`, `0200+2n`, n = 1..11; `0217`–`0222` are the arc-2
bosses #9–#11. `0223`–`0230` are the raid-exclusive gear (§13), not boss uniques). Rules:

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

## 13. Raid-exclusive gear & the Raid Quartermaster

The **Raid Quartermaster** is a vendor NPC (placement in the raid staging towns / Millbrook,
`docs/WORLD_PLAN.md`) that sells raid-exclusive rewards for `raid_token`s (earned per
`10_systems/social/RAID.md` §6 / `10_systems/DROPS.md` §5.4). This is the raids-as-centerpiece
loot loop (`00_vision/PILLARS.md` P3) — desirable, but **not** required to progress (P2, solo
stays viable).

- **Raid-exclusive equipment — two per raid** (undervault `item_equip_0223`–`0224`
  · mainspring `0225`–`0226` · deepfrost `0227`–`0228` · voidtide `0229`–`0230` · orrery
  `0301`–`0302`, the appended fifth-raid pair — the family is deliberately discontiguous,
  `docs/ID_REGISTRY.md`). `req_level` = the
  raid's level band; `rarity` `epic`. Built to the §7–§10 base+affix budget for that band with
  **one signature flourish line** (like a boss unique, §11), but the total item pe is capped at the
  ordinary `epic` budget — deliberately a **side-grade** with a distinctive identity, **not** a
  strict upgrade over same-band boss uniques or top-tier crafted gear. A solo player who never
  raids is never behind the power curve; the raid gear is a *flavor and prestige* choice.
- **Raid cosmetics — `item_cosmetic_0001`–`0008` (first four raids) + `0065`–`0066` (`raid_orrery`),
  one title + one cosmetic effect per raid.** No
  stats (`10_systems/MONETIZATION.md` cosmetic-only charter; `00_vision/PILLARS.md` anti-pay-to-win).
  Purely the "I cleared the Voidtide" flex that drives social prestige.
- **Pricing (locked 2026-07-24, `raid_token`s).** Prices are set so a piece takes **several
  clears**, not one — aspirational but attainable against the faucet of 1 token/clear (2 on the
  first-of-day, `10_systems/social/RAID.md` §6.D):

  | Quartermaster SKU | Price (`raid_token`) | Clears to earn (daily first-clear / casual) |
  |---|---|---|
  | Raid-exclusive equip (each of the 2) | **10** | 5 days of first-clears / 10 clears |
  | Raid title (`item_cosmetic`, per raid) | **15** | 8 days / 15 clears |
  | Raid cosmetic effect (`item_cosmetic`, per raid) | **20** | 10 days / 20 clears |

  A raid's full catalog (2 equips + title + effect) is 55 tokens ≈ four weeks of daily
  first-clears — a season-scale chase, never a single lucky night. Prices sit mid/high in the old
  first-pass target bands (equip 8–12, cosmetic 15–20) because the token faucet is guaranteed
  (no drop luck to compensate). Equips remain **side-grades** (capped at the ordinary `epic`
  budget above — never best-in-slot over same-band boss uniques). Tokens are per-raid variants, so
  each catalog is chased by running *its* raid. Concrete SKUs authored in Phase D.

## Open Questions

- **Resolved (2026-07-24 md audit): the ID_REGISTRY arc-2 re-block + `item_use` mints landed.**
  `docs/ID_REGISTRY.md` carries the full layout (weapons `0231`–`0254`, armor `0255`–`0284`,
  accessories `0285`–`0300`, uniques `0201`–`0222`, `0223`–`0230` + `0301`–`0302` raid gear), the tonics
  `item_use_0017`–`0020` are minted in `50_content/items/use/consumables.yaml`, §1.1 reads seven
  tiers, and `00_vision/SCOPE.md` lists the v3 counts (~170 equip).
- **ENHANCEMENT emberstone band mapping (arc-2) — owner `10_systems/ENHANCEMENT.md`.** §4's twelve
  tiers now need enhancement stones through T12. Recommendation: keep one stone per **two** tiers and
  add **Emberstone VI** at the reserved `item_etc_0198`, re-mapping to the v3 `req_level`s — I → T1–T2
  (Lv 1–14), II → T3–T4 (15–28), III → T5–T6 (29–42), IV → T7–T8 (43–56), V → T9–T10 (57–70),
  VI → T11–T12 (71–80). Owner ENHANCEMENT; do not edit from here. (The stale worked-example
  clause once flagged here was fixed in ENHANCEMENT §4 — T6 `W` = 151 is cited correctly there.)
- **`shield` / `overall` slot integration (pending wave).** `docs/ID_REGISTRY.md` reserves
  `item_equip_0181`–`0200` for the equipment-v2 `shield`/`overall` pieces (GLOSSARY Provisional;
  semantics in `10_systems/SCROLLS.md`'s companion ITEMS revision), and this doc's §2 nine-slot
  table does not yet carry them — the §2/§10 roster integration with the v3 T1–T12 ladder is the
  follow-up wave ID_REGISTRY's own Open Questions name. Owner: this doc + SCROLLS wave. (Made
  discoverable from here by the 2026-07-24 md audit.)
- **ECONOMY tonic re-band + new price rows — owner `10_systems/ECONOMY.md` §4.1.** That table still
  carries pre-v2 Lv-100 tonic bands and stops at Prime. It should adopt the seven-tier tier→band
  binding in §1.1 (arc-1 tiers compressed to Lv 1–42) and add `shards` price rows for the two arc-2
  tonics (`item_use_0017`/`0018` Sovereign, `0019`/`0020` Mythic) continuing its rising-sink curve
  above Prime. Restate bands in one place only (this doc owns the binding; ECONOMY references it).
- **Arc-2 region context depends on WORLD_PLAN/GLOSSARY promotion.** §4's arc-2 island bands
  (Frostpeak/Arcane Reach/Voidshore) and the `item_etc` material blocks (`0129`–`0176`, 16/island)
  and equip pools (`pool_equip_r09`–`r11`) are owned by `docs/WORLD_PLAN.md` / `10_systems/DROPS.md`;
  those island region-slugs are still marked "reserved / invalid in this run's content" in
  `00_vision/GLOSSARY.md` and must be promoted for arc-2 before that content lands. Referenced here,
  not owned.
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
- (MON-001) **Resolved owner (2026-07-24):** the zero-stat cosmetic appearance layer reserved by
  `10_systems/MONETIZATION.md` §3.1 is now owned by `10_systems/COSMETICS.md` — its §5 fixes the
  loadout slot list (title / weapon skin / outfit skin / dye / crest flourish) rendered above this
  doc's §2 equipment slots. Still open here: the paper-doll layer *ordering* must be settled with
  the Phase E render-stack pass. No cosmetic items are authored this run.
