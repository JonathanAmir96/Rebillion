# item.schema.md — Batch-table content shape for equip/use/etc items

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md,
10_systems/INVENTORY.md, 10_systems/STATS.md, 10_systems/SKILL_EFFECTS.md,
10_systems/STATUS_EFFECTS.md, 10_systems/PERSISTENCE.md, 10_systems/social/RAID.md,
20_schemas/monster.schema.md,
20_schemas/drop_table.schema.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md, docs/VALIDATION.md

## Purpose

Defines the content shape of the **item batch tables** — the `equip` (~162), `use` (~34), and
`etc` (~181) items in `00_vision/SCOPE.md` / `10_systems/ITEMS.md` §1. Unlike monsters/skills,
items are authored many-rows-per-file (`10_systems/ITEMS.md` §12's batch-table convention): a
table file carries front-matter plus an `items:` list, each row one `item_equip_NNNN` /
`item_use_NNNN` / `item_etc_NNNN`. A row is the base/affix stat-line budget copied from
`10_systems/ITEMS.md` §7–§10, the `10_systems/ENHANCEMENT.md` enhancement ceiling, the
`10_systems/ECONOMY.md` price, and (for `use` rows) an effect list from the
`10_systems/SKILL_EFFECTS.md` registry. It is read by the inventory/equip runtime
(`10_systems/ITEMS.md`, `10_systems/INVENTORY.md`), the enhancement NPC UI
(`10_systems/ENHANCEMENT.md`), vendor pricing (`10_systems/ECONOMY.md`), the drop roller
(`10_systems/DROPS.md`, `20_schemas/drop_table.schema.md`), and quest item rewards
(`10_systems/QUESTS.md`). This schema owns the **row field shape and enum owners**; it never
restates the stat-budget formulas, prices, or effect-op parameter schemas — it cites them.

**This schema also fixes the Phase D table filenames** (File conventions below), since
`10_systems/ITEMS.md` §12 only illustrates naming and explicitly defers "this doc owns only the
table wrapper" — binding the names here is this schema's job, not a restatement of ITEMS.md.

## File conventions

- **Batch tables, not one-entity-per-file** (`10_systems/ITEMS.md` §12). Each file is one YAML
  document: front-matter trio + a top-level `items:` list of rows. A table's own `id` is
  `item_table_<name>`, where `<name>` is the file's stem (below).
- **Fixed Phase D file list** (binds ITEMS.md §12's illustrative names to concrete paths; all
  under `50_content/items/`):

| Path | `id` | Row IDs (`docs/ID_REGISTRY.md`) | Authored |
|---|---|---|---|
| `equip/weapons.yaml` | `item_table_weapons` | `item_equip_0001`–`0040` (arc 1, T1–T6) + `0231`–`0254` (arc 2, T7–T12; ID_REGISTRY v3) | arc batches share the file |
| `equip/armor.yaml` | `item_table_armor` | `item_equip_0041`–`0140` (arc 1) + `0255`–`0284` (arc 2) (+ reserved-growth `0181`–`0200`, ITEMS.md §4 OQ) | arc batches share the file |
| `equip/accessories.yaml` | `item_table_accessories` | `item_equip_0141`–`0180` (arc 1) + `0285`–`0300` (arc 2) | arc batches share the file |
| `equip/uniques.yaml` | `item_table_uniques` | `item_equip_0201`–`0222` (bosses #1–#11; `0223`–`0230` reserved) | one batch |
| `use/consumables.yaml` | `item_table_consumables` | `item_use_0001`–`0060` | one batch (`0001`–`0016` well-known, `docs/ID_REGISTRY.md`) |
| `etc/materials_r01.yaml` … `materials_r11.yaml` | `item_table_materials_r<NN>` | that region's 16-item `item_etc` block (`docs/ID_REGISTRY.md`) | **one file per region batch** — lands with that region's `drop_mob_*` files (`20_schemas/drop_table.schema.md` batch-order rule, since region drop tables `ref` these materials) |
| `etc/enhancement.yaml` | `item_table_enhancement` | `item_etc_0193`–`0197` (Emberstone I–V; `0198`–`0200` reserved, unauthored) | one batch |

- The **reserved-growth split** (`0181`–`0200`) is not fixed by this schema —
  `10_systems/ITEMS.md` §4's own Open Question leaves the per-slot SKU count to Phase D
  bounded only by `docs/ID_REGISTRY.md`'s ranges. (`0231`–`0300` was re-blocked at the v3
  gate as the arc-2 weapons/armor/accessories ranges above and is no longer free growth.)
- Field values use only GLOSSARY tokens (`docs/VALIDATION.md` §1); no unknown fields
  (`docs/VALIDATION.md` §3).

## Fields

Static content-definition files, loaded identically by client and server; the `authority` tag
marks who owns the *runtime effect* the field drives (`10_systems/PERSISTENCE.md` §1). Item
identity/stats/enhancement/price are **server-authoritative**; `name`/`flavor` are `client`.
Front-matter obeys `docs/VALIDATION.md` check 3.

### Table (file) level

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `item_table_<name>` | yes | File conventions table above | Must equal `item_table_<this file's stem>`. `server` (identity). |
| `schema` | string | yes | this file | Literal `20_schemas/item.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list[doc name] | yes | `docs/VALIDATION.md` §3 | Baseline `[ITEMS, ECONOMY]`; equip tables add `ENHANCEMENT`; `uniques.yaml` additionally adds `DROPS, WORLD_PLAN` (unique sourcing + boss region-order, §11); `use/consumables.yaml` adds `SKILL_EFFECTS, INVENTORY`; `etc/*` add `INVENTORY, DROPS, WORLD_PLAN` (region theming/materials); `etc/enhancement.yaml` adds `ENHANCEMENT` (no `WORLD_PLAN` — emberstones aren't region-themed). |
| `items` | list[row] | yes | — | One or more rows (below). `server`. |

### Row — common (all categories)

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `items[].id` | string `item_equip_NNNN`\|`item_use_NNNN`\|`item_etc_NNNN` | yes | `docs/ID_REGISTRY.md` Items blocks | Zero-padded 4 digits; immutable; must fall in the correct sub-block for this table (Validation). `server`. |
| `items[].name` | string | yes | `docs/ID_REGISTRY.md` (well-known `item_use_0001`–`0016` only) | US spelling. Well-known use IDs must match the ID_REGISTRY name exactly (Validation). `client`. |
| `items[].category` | enum | yes | this schema (`10_systems/ITEMS.md` §1) | `equip`\|`use`\|`etc`; must match the table's own file (Validation). `server`. |
| `items[].rarity` | enum | yes | `10_systems/ITEMS.md` §5 (GLOSSARY Rarity) | Drives affix-line count/budget **only for `equip`** (§10); on `use`/`etc` rows it is display-tier only (icon border, `40_assets/ART_BIBLE.yaml` `rarity_code`) with no mechanical effect — see Open Questions. `client` (display) / `server` (equip: gates affix rolling). |
| `items[].req_level` | int 1–300 (cap; authored ≤78) | yes | `10_systems/ITEMS.md` §4 (equip); Phase D (use/etc) | Minimum character `level` to equip/benefit as intended. For `equip`, must equal the tier's `req_level` (§4 table). For `use`/`etc`, an authoring guideline (band placement, `10_systems/ECONOMY.md` §4.1/§6), not a hard equip gate. `server`. |
| `items[].price` | map `{buy, sell}` | yes | `10_systems/ECONOMY.md` §4 | Sub-fields below. |
| `items[].price.buy` | int | equip/use: yes; etc: **omit** | `ECONOMY` §4.1 (use)/§4.2 (equip) | Etc items are not vendor-purchasable (`10_systems/ITEMS.md` §1 "mostly vendor/trade value"; emberstones specifically never purchasable, `10_systems/ENHANCEMENT.md` §6) — omit `buy` entirely for `etc` rows. |
| `items[].price.sell` | int | yes | `ECONOMY` §4 | Equip/use: `= round(0.25 · buy)` (hard, `ECONOMY` §4). Etc: authored directly (no `buy` to derive from — see Open Questions, `ECONOMY.md` prices only `use`/`equip`). |
| `items[].flavor` | string | no | `00_vision/PILLARS.md` P1 | ≤2 sentences, US spelling, optional (task brief marks it optional here, unlike monster/skill `flavor`). `client`. |

### Row — `equip` only

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `items[].slot` | enum | yes | `10_systems/ITEMS.md` §2 (GLOSSARY Equipment slots) | One of the 9 tokens. `server`. |
| `items[].weapon_type` | enum | `slot: weapon` only | `10_systems/ITEMS.md` §3 (GLOSSARY Weapon types) | `blade`\|`bow`\|`staff`\|`dirk`. Forbidden on non-weapon slots (Validation). `server`. |
| `items[].line_hint` | enum | `slot: weapon` only | `10_systems/JOBS.md` / GLOSSARY Job lines | The job line this weapon equips (fixed 1:1 by `weapon_type`, `10_systems/ITEMS.md` §3). Redundant with `weapon_type` by design — authored explicitly so tooling/UI never re-derives the mapping (see Open Questions). Must equal the fixed mapping (Validation, hard). `server`/`client`. |
| `items[].tier` | int 1–12 | yes | `10_systems/ITEMS.md` §4 | The `T1`–`T12` gear tier (T1–T6 arc 1, T7–T12 arc 2); keys the §7–§9 base-line lookup. Must correspond to `req_level` per the §4 table (Validation). `server`. |
| `items[].stats` | map `{base, affixes}` | yes | `10_systems/ITEMS.md` §6–§10 | The base+affix stat-line budget (§6: "base lines + affix lines"). Sub-fields below. `server`. |
| `items[].stats.base` | map `{<stat token>: value}` | yes | `ITEMS` §7 (weapon `W`) / §8 (armor+warding by slot×tier) / §9 (accessory by tier) | Rarity-independent; one entry per this slot's fixed base-line set (§2 table, e.g. `body` → `armor`+`warding`). Values copied exactly from the formula for this row's `slot`×`tier` (Validation, hard). |
| `items[].stats.affixes` | list[line] | yes (`[]` for `common`) | `ITEMS` §10 | Rarity-driven rolled lines. Line count = the §5 rarity→count table. Each entry is an **ordinary line** (`stat`/`value`) or, **`uniques.yaml` only**, a **flourish line** (`op`/`flourish`, §11). |
| `items[].stats.affixes[].stat` | enum | ordinary lines: yes | `10_systems/STATS.md` (GLOSSARY stat tokens); eligibility `ITEMS` §10 "Affix eligibility by slot" | Value magnitude must match the §10 affix-menu anchor (or its `u(L)`-interpolated value) for `req_level`. |
| `items[].stats.affixes[].value` | number | ordinary lines: yes | `ITEMS` §10 affix menu | Per-line pe (`ITEMS` §6 weights) ≤ the §10 per-line cap; unique exception below. |
| `items[].stats.affixes[].op` | enum | flourish lines only | `ITEMS` §11; `10_systems/SKILL_EFFECTS.md` §13 (`passive_stat_bonus`)/§16 (`on_hit_proc`) | A flourish may be a small effect instead of a stat line ("expressed only through existing ops," §11) — params per that op's own schema (`SKILL_EFFECTS`). |
| `items[].stats.affixes[].flourish` | bool | flourish lines only | `ITEMS` §11 | `true` marks this line eligible for the §11 **×1.5 per-line pe-cap exception**; absent/false = ordinary §10 rules apply. Uniques only (Validation). |
| `items[].enhance_max` | int | yes | `10_systems/ENHANCEMENT.md` §2 | The top of this item's `+` track. Every equip today uses the same uniform `0`–`9` track (`ENHANCEMENT` §2, "any single equip, all nine slots") — this field must equal `9` (Validation, hard). Authored explicitly for forward-compatibility/tooling rather than assumed; see Open Questions. `server`. |
| `items[].unique_of` | string `mob_NNN` | `uniques.yaml` only | `docs/ID_REGISTRY.md` Monsters + Items (boss-unique mapping); `10_systems/ITEMS.md` §11 | The boss this unique belongs to. Must resolve to a `tier: boss` mob (`20_schemas/monster.schema.md`) whose region-order boss number `n` (region order = `docs/WORLD_PLAN.md` Region overview, `n` = 1–11 only — the four raids end at existing region bosses and add no unique slots, `10_systems/social/RAID.md` §2/§6) makes this row's own `id` one of `item_equip_{0199+2n}` / `{0200+2n}` (uniques `0201`–`0222`, `docs/ID_REGISTRY.md`). Forbidden outside `uniques.yaml` (Validation). `server`. |

### Row — `use` only

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `items[].effects` | list[op] | yes | `10_systems/SKILL_EFFECTS.md` §4/§5/§14/§15 | Ordered effect list, **restricted to `heal`, `restore_essence`, `cleanse_status`, `apply_status`** (this schema's restriction — the task scope names only these four of the 14 ops for consumables). Params validate against each op's own schema; this schema never restates them. May be `[]` only for a utility item with no representable mechanic (e.g., a return scroll — see Open Questions). `server`. |
| `items[].use_cooldown` | float s | yes | this schema (first-pass; no owning system doc fixes item-use pacing today) | Seconds before this item can be used again. `0` = no cooldown. See Open Questions — `10_systems/SKILL_SYSTEM.md` §5 fixes "no GCD" for **skills** only; whether consumables share an analogous rule is unresolved. `server`. |
| `items[].stack` | int | yes | `10_systems/INVENTORY.md` §2 | Must equal **100** (the `use` tab's fixed stack size, `INVENTORY` §1–§2). Redundant with the category constant; authored explicitly (Validation, hard — see Open Questions). `server`. |

### Row — `etc` only

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `items[].source_hint` | string `mob_NNN` \| region slug | yes | `docs/ID_REGISTRY.md` Monsters; `docs/WORLD_PLAN.md` / GLOSSARY Region slugs | Informational: the mob (or region, if multi-mob-sourced) this material typically drops from. Cross-checked (warn) against `drop_mob_*` tables in the same region batch (`20_schemas/drop_table.schema.md`). `client` (tooltip) / advisory only. |
| `items[].stack` | int | yes | `10_systems/INVENTORY.md` §2 | Must equal **999** (the `etc` tab's fixed stack size). Same redundancy note as the `use` row's `stack`. `server`. |

## Enums

Every enum value comes from its owning registry; this schema points, never redefines.

| Field | Owning registry |
|---|---|
| `items[].category` | **This schema** (`10_systems/ITEMS.md` §1 token set): `equip`·`use`·`etc`. |
| `items[].rarity` | `10_systems/ITEMS.md` §5 (GLOSSARY Rarity): `common`·`uncommon`·`rare`·`epic`·`legendary`. |
| `items[].slot` | `10_systems/ITEMS.md` §2 (GLOSSARY Equipment slots), 9 tokens. |
| `items[].weapon_type` | `10_systems/ITEMS.md` §3 (GLOSSARY Weapon types): `blade`·`bow`·`staff`·`dirk`. |
| `items[].line_hint` | `10_systems/JOBS.md` / GLOSSARY Job lines: `bulwark`·`keeneye`·`weaver`·`flicker` (fixed to `weapon_type`, no `novice`). |
| `items[].stats.base`/`affixes[].stat` keys | `10_systems/STATS.md` (GLOSSARY primary/derived stat tokens); slot eligibility `10_systems/ITEMS.md` §10. |
| `items[].stats.affixes[].op` (flourish) | `10_systems/SKILL_EFFECTS.md` §13/§16 only: `passive_stat_bonus`·`on_hit_proc` (not the full 14-op set — flourishes are stat-adjacent, `ITEMS` §11). |
| `items[].unique_of` | `docs/ID_REGISTRY.md` Monsters (must resolve to a `tier: boss` entry, `20_schemas/monster.schema.md`). |
| `items[].effects[].op` (use rows) | `10_systems/SKILL_EFFECTS.md`, restricted subset: `heal`·`restore_essence`·`cleanse_status`·`apply_status`. |
| `items[].effects[].status` (on `apply_status`) | `10_systems/STATUS_EFFECTS.md` (GLOSSARY Status effects). |
| `items[].effects[].tag` (on `cleanse_status`) | `10_systems/STATUS_EFFECTS.md` §2 cleanse tags. |
| `items[].source_hint` | `docs/ID_REGISTRY.md` Monsters (`mob_NNN`) or `docs/WORLD_PLAN.md` / GLOSSARY Region slugs. |

## Example

```yaml
# illustrative — real tables land in Phase D. This file holds all 40 rows item_equip_0001-0040;
# one shown. Numbers are exact per ITEMS.md §7/§10 and ECONOMY.md §4.2 (a checkable worked case).
id: item_table_weapons
schema: 20_schemas/item.schema.md
references: [ITEMS, ENHANCEMENT, ECONOMY]
items:
  - id: item_equip_0002
    name: Verdant Fang
    category: equip
    slot: weapon
    weapon_type: blade
    line_hint: bulwark
    tier: 2
    req_level: 10
    rarity: uncommon
    stats:
      base: { power: 30 }              # ITEMS §7 T2 blade W = 30
      affixes:
        - { stat: might, value: 4 }    # ITEMS §10 Lv10 +primary(u)=4 -> 4.00 pe (§6); uncommon
                                        # budget @Lv10 = 1 line x cap(10)=round(1.4x4)=6 pe: 4<=6 OK
    enhance_max: 9
    price: { buy: 300, sell: 75 }       # ECONOMY §4.2: T2 base_buy 120 x uncommon (x2.5) = 300
    flavor: "A gladeforged blade that hums faintly when swung near living wood."
  # ... item_equip_0001, 0003-0040 (this schema's ID range for equip/weapons.yaml)
```

**Use-row pattern** (illustrative fragment, `use/consumables.yaml`, well-known `item_use_0001`
"Lesser Life Tonic" — name/price fixed by `docs/ID_REGISTRY.md`/`10_systems/ECONOMY.md` §4.1,
restore `amount` is Phase D's):

```yaml
  - id: item_use_0001
    name: Lesser Life Tonic
    category: use
    rarity: common
    req_level: 1
    price: { buy: 15, sell: 4 }         # ECONOMY §4.1 exact (well-known ID, hard-checked)
    effects:
      - { op: heal, scaling: flat, amount: 120 }   # magnitude: Phase D tunes vs Lv1-9 life band
    use_cooldown: 1.0                    # first-pass; see Open Questions
    stack: 100
    flavor: "A watered cordial that dulls the day's scrapes."
```

**Etc-row pattern** (illustrative fragment, `etc/materials_r01.yaml`, Emberfoot region):

```yaml
  - id: item_etc_0001
    name: Cindermaw Fang
    category: etc
    rarity: common
    req_level: 1
    price: { sell: 8 }                   # no buy — etc items are not vendor-purchasable
    source_hint: mob_010                 # Cinder Houndmaster (elite, cross-checked vs drop_mob_010)
    stack: 999
    flavor: "A blunt fang still warm from the kiln-hound's jaw."
```

## Validation rules

Schema-specific checks, run in addition to `docs/VALIDATION.md` globals (§1 banned tokens, §2
referential integrity, §3 schema conformance/front-matter/unknown-fields, §4 ID uniqueness+range).

1. **ID ↔ table membership (hard).** Every `items[].id` falls inside the correct
   `docs/ID_REGISTRY.md` sub-block for the table it's authored in (File conventions table); the
   file's own `id` equals `item_table_<its stem>`.
2. **Category ↔ field gating (hard).** `items[].category` matches the table's category (`equip`
   rows only in `equip/*.yaml`, etc.). `equip`-only fields (`slot`, `weapon_type`, `line_hint`,
   `tier`, `stats`, `enhance_max`, `unique_of`) are forbidden on `use`/`etc` rows; `use`-only
   (`effects`, `use_cooldown`) and `etc`-only (`source_hint`) fields are forbidden outside their
   category; `unique_of` is additionally forbidden outside `equip/uniques.yaml`.
3. **Stat budget — base (hard).** `items[].stats.base` values equal the `10_systems/ITEMS.md`
   §7 (weapon)/§8 (armor)/§9 (accessory) formula/table for this row's `slot`×`tier` exactly (§8's
   `armor`/`warding` may be reallocated between the two only if `10_systems/ITEMS.md` itself
   permits it — it does not; use the table value).
4. **Stat budget — affixes (hard).** Line count equals the `10_systems/ITEMS.md` §5 rarity→count
   table; each ordinary line's per-line pe (`ITEMS` §6 weights applied to `value`) ≤ the §10
   per-line cap for `req_level`; total affix pe ≤ the §10 rarity budget for `req_level`; each
   `stat` is eligible for this row's `slot` per §10's "Affix eligibility by slot." **Flourish
   lines** (`uniques.yaml` only, `flourish: true`) may exceed the per-line cap by up to ×1.5
   (`ITEMS` §11); total item pe (base pe-equivalent + affixes) ≤ the `legendary` budget × 1.5 for
   uniques.
5. **`enhance_max` (hard).** Always `9` (`10_systems/ENHANCEMENT.md` §2 — no per-item variance
   exists today).
6. **`weapon_type`/`line_hint` pairing (hard).** Present if and only if `slot: weapon`;
   `line_hint` equals the fixed `weapon_type`→line mapping (`10_systems/ITEMS.md` §3 / GLOSSARY Job
   lines): `blade`→`bulwark`, `bow`→`keeneye`, `staff`→`weaver`, `dirk`→`flicker`.
7. **`tier` ↔ `req_level` (hard).** `tier` corresponds to `req_level` per the `10_systems/ITEMS.md`
   §4 tier table — `req_level(tier) = 1 + 7·(tier − 1)`, i.e. `T1`=1, `T2`=8, `T3`=15, `T4`=22,
   `T5`=29, `T6`=36, `T7`=43, `T8`=50, `T9`=57, `T10`=64, `T11`=71, `T12`=78.
8. **`unique_of` resolution (hard, `uniques.yaml` only).** Resolves to an existing `mob_NNN` whose
   `tier: boss` (`20_schemas/monster.schema.md`); this row's `id` is one of the two IDs
   `docs/ID_REGISTRY.md` maps to that boss's region-order number (derivation above).
9. **Price — sell formula (hard, equip/use).** `price.sell == round(0.25 · price.buy)`
   (`10_systems/ECONOMY.md` §4). **Price — band fit (warn).** `price.buy` should sit near the
   `10_systems/ECONOMY.md` §4.1 (use) / §4.2 (equip: `base_buy(tier) · rarity_mult`, `legendary`
   suppressed to the `epic` multiplier) reference value; first-pass, tunable.
10. **Well-known use IDs (hard).** `item_use_0001`–`0016` carry the exact `name` **and** the exact
    `price.buy`/`price.sell` from `docs/ID_REGISTRY.md` / `10_systems/ECONOMY.md` §4.1 (these are
    given as literal numbers, not a band, unlike rule 9's general case).
11. **`etc` price (hard).** `price.buy` is never present on an `etc` row (not vendor-purchasable,
    `10_systems/ITEMS.md` §1, `10_systems/ENHANCEMENT.md` §6 for emberstones specifically).
12. **`stack` (hard).** Equals the `10_systems/INVENTORY.md` §2 category constant: `100` (`use`),
    `999` (`etc`).
13. **`effects[].op` restriction (hard, `use` rows).** Every op ∈ {`heal`, `restore_essence`,
    `cleanse_status`, `apply_status`}; every param validates against that op's own schema
    (`10_systems/SKILL_EFFECTS.md` §4/§5/§14/§15).
14. **`source_hint` consistency (warn, `etc` rows).** When naming a `mob_NNN`, that mob's
    `drop_mob_NNN` table (`20_schemas/drop_table.schema.md`) should actually `ref` this item;
    checkable only once that region's drop-table batch lands alongside this materials file (batch-
    order rule, File conventions).
15. **Rarity mechanical scope (warn).** `rarity` on `use`/`etc` rows has no budget consequence
    (rule 4 applies to `equip` only) — see Open Questions.

## Template

```yaml
id: item_table_{name}                    # e.g. weapons, armor, accessories, uniques, consumables,
                                          # materials_r{NN}, enhancement — see File conventions
schema: 20_schemas/item.schema.md
references: [ITEMS, ECONOMY]             # add ENHANCEMENT (equip tables + etc/enhancement.yaml);
                                          # DROPS + WORLD_PLAN (uniques.yaml); INVENTORY + DROPS +
                                          # WORLD_PLAN (etc/*); SKILL_EFFECTS + INVENTORY (use/consumables.yaml)
items:
  - id: item_{equip|use|etc}_{NNNN}
    name: "{Display Name}"
    category: {equip|use|etc}
    rarity: {common|uncommon|rare|epic|legendary}
    req_level: {1..300}                  # legal to the Lv-300 cap; authored items top out at 78 (ITEMS §4)
    price:
      buy: {int}                         # omit entirely for etc rows
      sell: {int}                        # equip/use: round(0.25*buy); etc: authored directly
    # flavor: "{<=2 sentences}"          # optional

    # --- equip only (forbidden on use/etc): ---
    # slot: {weapon|head|body|legs|boots|gloves|cape|ring|amulet}
    # weapon_type: {blade|bow|staff|dirk}      # weapon slot only
    # line_hint: {bulwark|keeneye|weaver|flicker}   # weapon slot only; = fixed weapon_type mapping
    # tier: {1..12}
    # stats:
    #   base: { {stat_token}: {value} }        # ITEMS §7-§9, exact per slot x tier
    #   affixes:                                # count per ITEMS §5 rarity; [] for common
    #     - { stat: {stat_token}, value: {n} }  # ordinary line, ITEMS §10 menu + budget
    #     # uniques.yaml only, in place of/alongside ordinary lines:
    #     # - { op: {passive_stat_bonus|on_hit_proc}, {params per SKILL_EFFECTS}, flourish: true }
    # enhance_max: 9
    # unique_of: mob_{NNN}                     # uniques.yaml only

    # --- use only (forbidden on equip/etc): ---
    # effects:
    #   - { op: {heal|restore_essence|cleanse_status|apply_status}, {params per that op} }
    # use_cooldown: {float_s}
    # stack: 100

    # --- etc only (forbidden on equip/use): ---
    # source_hint: {mob_NNN | region_slug}
    # stack: 999
```

## Open Questions

- **`stats` field naming.** The task's field list names this `stats{}`; `10_systems/ITEMS.md` §12's
  own illustrative row instead uses two top-level siblings, `base:`/`affixes:`. This schema nests
  them as `stats.base`/`stats.affixes` to satisfy the task's field name while preserving the
  base/affix split ITEMS.md's budget math and ENHANCEMENT's "+ scales base, never affixes" rule
  (`10_systems/ENHANCEMENT.md` §4) depend on. Confirm before Phase D authors at scale.
- **`req_level` vs. task's `level_req`.** `10_systems/ITEMS.md`, `10_systems/ENHANCEMENT.md`, and
  `docs/ID_REGISTRY.md` all use `req_level` consistently; this schema keeps that spelling for
  cross-doc consistency rather than the task brief's `level_req` shorthand. Flagged, not guessed.
- **Redundant-but-explicit fields.** `tier` (↔ `req_level` via ITEMS §4), `line_hint` (↔
  `weapon_type` via ITEMS §3), `stack` (↔ category via INVENTORY §2), and `enhance_max` (↔
  ENHANCEMENT §2's uniform 9) are each fully determined by another field or a fixed constant. They
  are kept as explicit authored/validated fields for Phase D and tooling legibility rather than
  derived at load time; flag if the content pipeline would rather compute them instead.
- **`etc` price has no ECONOMY.md owner.** `10_systems/ECONOMY.md` §4 prices only `use` (§4.1) and
  `equip` (§4.2); no table or formula prices `item_etc` materials or emberstones. `etc` rows'
  `price.sell` is therefore Phase D's first-pass number against no cited band — flagged for
  `10_systems/ECONOMY.md` to adopt an etc price section, not guessed here.
- **`use_cooldown` has no owning pacing doc.** `10_systems/SKILL_SYSTEM.md` §5 fixes "no GCD" for
  *skills*; no doc says whether consumables share an analogous per-item or shared cooldown, or
  what the number should be. First-pass field only; flagged for `10_systems/ECONOMY.md` or a
  future combat-pacing doc to own.
- **Scrolls (utility/return) have no representable mechanic.** `10_systems/ITEMS.md` §1 names
  "scrolls (utility/return)" as a `use` sub-kind (e.g. `item_use_0013` Millbrook Return Scroll,
  `docs/ID_REGISTRY.md`), but no doc defines a teleport/return mechanic and the task's four
  permitted `effects` ops (`heal`/`restore_essence`/`cleanse_status`/`apply_status`) cannot express
  one. This schema allows `effects: []` for such rows rather than inventing a 15th op or a new
  field; the actual mechanic is unowned and unflagged elsewhere — raised here for the first time.
- **Rarity's mechanical scope on `use`/`etc`.** The task's common-field list requires `rarity` on
  every row, but `10_systems/ITEMS.md` §5 defines its mechanical meaning (affix-line count) only
  for `equip`. For `use`/`etc` this schema treats `rarity` as cosmetic-only; confirm this is
  intended, or whether those categories should omit it.
- **Boss-unique region-order table — resolved (v3).** `docs/ID_REGISTRY.md` now tabulates the 11
  boss-order→unique pairs by name (Cindermaw `0201`–`0202` … Nyxaris `0221`–`0222`), so
  `unique_of` validation reads the mapping directly instead of recomputing it from
  `docs/WORLD_PLAN.md`'s region order. There are exactly 11 pairs — raid finale bosses are region
  bosses and add none (`10_systems/social/RAID.md` §2).
