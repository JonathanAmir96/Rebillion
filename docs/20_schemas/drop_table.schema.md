# drop_table.schema.md — Per-monster drop table (drop_mob_NNN) + the region pools file

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/DROPS.md, 10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/ECONOMY.md,
10_systems/social/PARTY.md, 10_systems/PERSISTENCE.md, 20_schemas/monster.schema.md,
20_schemas/item.schema.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md, docs/VALIDATION.md

## Purpose

Defines two related content shapes, both owned by `10_systems/DROPS.md`: one **drop table**
per monster (`drop_mob_NNN`, 150 files, `00_vision/SCOPE.md`) and the single shared **region
pools** file (`pools.yaml`, 12 entries). A `drop_mob_NNN` file is the ordered-independent-rolls
row list `10_systems/DROPS.md` §1 anatomizes: `shards`, region materials, use items, emberstones,
and (elite/boss/raid) an equip-pool roll or boss/raid uniques, shaped per §5's per-tier contract.
`pools.yaml` is the region equip pools `10_systems/DROPS.md` §6 rolls against. Both are read by
the loot roller (`10_systems/DROPS.md` §9, server-authoritative) and reference item identities
owned by `20_schemas/item.schema.md`. This schema owns the **field shape, the enum owners, and the
per-tier shape checks**; it never restates DROPS.md's chance anchors, `shards` faucet formula, or
rarity-weight tables — it cites them.

## File conventions

- **`drop_mob_NNN.yaml` — one entity per file.** `50_content/drop_tables/drop_mob_NNN.yaml`,
  zero-padded three digits, `drop_mob_001`–`drop_mob_150`, number matching its `mob_NNN` exactly
  (`10_systems/DROPS.md` §1, `docs/ID_REGISTRY.md`). The file's `id` is its filename stem; both
  immutable.
- **`pools.yaml` — one shared file, not a per-entity file and not an `20_schemas/item.schema.md`-
  style multi-row-per-category batch either.** `50_content/drop_tables/pools.yaml`, front-matter
  `id: drop_pools`, holding all 11 `pool_equip_r01`–`r11` entries as one `pools:` list
  (`10_systems/DROPS.md` §6, `docs/ID_REGISTRY.md`).
- **Batch-order rule.** A region's `drop_mob_*` files and that region's `etc/materials_r<NN>.yaml`
  (`20_schemas/item.schema.md`) — and, for elite/boss/raid tables, the relevant slice of
  `pools.yaml` — land in the **same content batch**, since a drop table's `ref`s to region
  materials and pools can only resolve once both exist (`docs/VALIDATION.md` §2 referential
  integrity; `docs/VALIDATION.md` Batch protocol).

## Fields

Static content-definition files, loaded identically by client and server; the `authority` tag
marks who owns the *runtime effect* the field drives (`10_systems/PERSISTENCE.md` §1). All rolls
(chance, `qty`, pool selection, `rarity`) are **server-authoritative**
(`10_systems/DROPS.md` §9). Front-matter obeys `docs/VALIDATION.md` check 3.

### `drop_mob_NNN.yaml`

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `drop_mob_NNN` | yes | `docs/ID_REGISTRY.md` Drop tables | Zero-padded; immutable; must equal the filename stem. `server`. |
| `schema` | string | yes | this file | Literal `20_schemas/drop_table.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list[doc name] | yes | `docs/VALIDATION.md` §3 | Baseline `[DROPS, ITEMS]`; add `ENHANCEMENT` when any row refs an emberstone; add `WORLD_PLAN` for `boss`/raid tables (region-order boss-unique mapping, rule 6); add `PARTY` for raid tables (`mob_147`–`150`, loot-split ownership). |
| `owner` | string `mob_NNN` | yes | `10_systems/DROPS.md` §1 | Must equal `mob_<this file's own NNN>` (task's explicit "owner matches filename" rule). `server`. |
| `rows` | list[row] | yes (≥1) | `10_systems/DROPS.md` §1, §5 | Independently rolled on the monster's death. Shape requirements per this mob's tier — Validation. `server`. |
| `rows[].ref` | string | yes | `item.schema.md` IDs; literal `shards`; `pools.yaml` IDs | A concrete `item_equip_*`/`item_use_*`/`item_etc_*` id, the literal token `shards`, or a `pool_equip_r01`–`r11` id (§6). Must resolve (`docs/VALIDATION.md` §2). |
| `rows[].chance` | token \| float | yes | `10_systems/DROPS.md` §2 | One of the six named buckets, **or** a raw float in `[0,1]` (§1/§2 both permit this — see Open Questions re: the task's stricter phrasing). |
| `rows[].qty_min` | int ≥1 | yes | `10_systems/DROPS.md` §1 | Uniform-roll lower bound. `1` fixed when `ref` is an equip id (unstacked, §1). |
| `rows[].qty_max` | int ≥ `qty_min` | yes | `10_systems/DROPS.md` §1 | Uniform-roll upper bound. `1` fixed when `ref` is an equip id. |
| `rows[].rarity_source` | enum | **only when `ref` is a pool id** | `10_systems/DROPS.md` §5.5/§6 | `elite`\|`boss`\|`raid` — selects which §5.5 rarity-weight row instantiates the pooled equip's `rarity`. Forbidden on non-pool rows (Validation). `server`. |
| `rows[].first_clear_guaranteed` | bool | no — default `false` | `10_systems/DROPS.md` §5.3 | Marks this row as the one granted on a character's first-ever clear of this boss (the §5.3 bad-luck-protection guarantee). **Added by this schema** — DROPS.md describes the behavior but names no field for it (see Open Questions); the actual once-per-character bookkeeping is server-tracked state (`10_systems/PERSISTENCE.md`), not expressed here. Boss/raid unique rows only. `server`. |

### `pools.yaml`

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string | yes | this schema | Literal `drop_pools` (fixed, single file). `server`. |
| `schema` | string | yes | this file | Literal `20_schemas/drop_table.schema.md`. |
| `references` | list[doc name] | yes | `docs/VALIDATION.md` §3 | Baseline `[DROPS, ITEMS, WORLD_PLAN]` (pool `id`↔`region` binding, matching `20_schemas/npc.schema.md`'s convention for region-bound content). |
| `pools` | list[pool] | yes (exactly 11) | `10_systems/DROPS.md` §6; `docs/ID_REGISTRY.md` | One per region, `pool_equip_r01`–`r11`. `server`. |
| `pools[].id` | string `pool_equip_rNN` | yes | `docs/ID_REGISTRY.md` | `NN` = the region's two-digit order number (`docs/WORLD_PLAN.md` Region overview, R1–R12). `server`. |
| `pools[].region` | enum | yes | `docs/WORLD_PLAN.md` / GLOSSARY Region slugs | Must correspond to `id`'s `rNN` (Validation). `server`. |
| `pools[].entries` | list `{item, weight}` | yes (≥1) | `10_systems/DROPS.md` §6 | The pool's candidate base equips. `server`. |
| `pools[].entries[].item` | string `item_equip_NNNN` | yes | `20_schemas/item.schema.md` | Must resolve; its `tier` should match the region's level band (`10_systems/ITEMS.md` §4, `docs/WORLD_PLAN.md`) (Validation, warn). `server`. |
| `pools[].entries[].weight` | number | no — default uniform | `10_systems/DROPS.md` §6 ("weighted roughly uniform... or per-pool weights") | Relative pick weight within the pool's step-1 roll. Omit for uniform. `server`. |

## Enums

Every enum value comes from its owning registry; this schema points, never redefines.

| Field | Owning registry |
|---|---|
| `rows[].chance` (token form) | `10_systems/DROPS.md` §2 (this doc's own bucket vocabulary): `guaranteed`·`common`·`uncommon`·`rare`·`epic`·`legendary`. A raw float is also legal (§1/§2), not an enum value. |
| `rows[].rarity_source` | `10_systems/DROPS.md` §5.5 (this doc's own rows): `elite`·`boss`·`raid`. |
| `pools[].region` | `docs/WORLD_PLAN.md` / `00_vision/GLOSSARY.md` Region slugs. |

Non-enum references resolved by `docs/VALIDATION.md` §2 (not enums, but named here since they are
the schema's other controlled vocabularies): `owner`/`rows[].ref` mob and item prefixes —
`docs/ID_REGISTRY.md`; `pools[].entries[].item` — `20_schemas/item.schema.md`.

## Example

```yaml
# illustrative — real instances land in Phase D. mob_010 (Cinder Houndmaster, elite, Lv10) is the
# same worked mob as 20_schemas/monster.schema.md's own example. Shards row: mean_shards_normal(10)
# = round(1.5*10+3) = 18 (DROPS §3); elite x4 = 72; +-20% range = [round(0.8*72), round(1.2*72)]
# = [58, 86]. Elite shape per DROPS §5.2: guaranteed shards, 2-3 materials, one emberstone
# (uncommon), one guaranteed pool roll (rarity_source: elite), one use item (uncommon).
id: drop_mob_010
schema: 20_schemas/drop_table.schema.md
references: [DROPS, ITEMS, ENHANCEMENT]
owner: mob_010
rows:
  - { ref: shards, chance: guaranteed, qty_min: 58, qty_max: 86 }
  - { ref: item_etc_0001, chance: common, qty_min: 1, qty_max: 2 }
  - { ref: item_etc_0002, chance: uncommon, qty_min: 1, qty_max: 1 }
  - { ref: item_etc_0193, chance: uncommon, qty_min: 1, qty_max: 1 }   # Emberstone I (R1 = T1-T2)
  - { ref: pool_equip_r01, chance: guaranteed, qty_min: 1, qty_max: 1, rarity_source: elite }
  - { ref: item_use_0001, chance: uncommon, qty_min: 1, qty_max: 1 }
```

**Boss unique rows pattern** (illustrative fragment, `drop_mob_011`, Cindermaw — region-order boss
`n=1`, owning `item_equip_0201`/`0202` per `docs/ID_REGISTRY.md`'s boss-unique mapping):

```yaml
  - { ref: item_equip_0201, chance: epic, qty_min: 1, qty_max: 1, first_clear_guaranteed: true }
  - { ref: item_equip_0202, chance: legendary, qty_min: 1, qty_max: 1 }
```

**`pools.yaml`** (the second file shape this schema defines — complete for one region, the other
11 follow the same pattern):

```yaml
id: drop_pools
schema: 20_schemas/drop_table.schema.md
references: [DROPS, ITEMS, WORLD_PLAN]
pools:
  - id: pool_equip_r01
    region: emberfoot
    entries:
      - { item: item_equip_0001, weight: 1.0 }   # T1 blade
      - { item: item_equip_0002, weight: 1.0 }   # T2 blade (top-of-region reach)
      - { item: item_equip_0041, weight: 1.0 }   # T1 head armor
  # ... pool_equip_r02 - pool_equip_r11, one per docs/WORLD_PLAN.md region
```

## Validation rules

Schema-specific checks, run in addition to `docs/VALIDATION.md` globals (§1 banned tokens, §2
referential integrity, §3 schema conformance/front-matter, §4 ID uniqueness+range).

1. **Filename ↔ id ↔ owner (hard).** `drop_mob_NNN.yaml`'s `id` equals its filename stem;
   `owner` equals `mob_<same NNN>` (task's explicit rule; `10_systems/DROPS.md` §1).
2. **`ref` resolution (hard).** Every `ref` resolves: an item id in the correct
   `20_schemas/item.schema.md` table for its category, the literal `shards`, or an existing
   `pools[].id` in `pools.yaml` (`docs/VALIDATION.md` §2). Region `item_etc` refs require that
   region's `etc/materials_r<NN>.yaml` to be present in the same batch (File conventions).
3. **`chance` vocabulary (hard).** Either one of the six `10_systems/DROPS.md` §2 tokens or a raw
   float in `[0,1]` (§1 explicitly permits both — see Open Questions on the task-text tension).
4. **Owner tier ↔ per-tier shape (hard).** The owner mob's `tier` — read from its ID slot in
   `docs/ID_REGISTRY.md` Monsters (same derivation `20_schemas/monster.schema.md` Validation rule 1
   uses) — selects which `10_systems/DROPS.md` shape this table must satisfy:
   - **`normal` (§5.1):** a `guaranteed` `shards` row; 1–2 region-material rows at `common`/
     `uncommon`; **no** equip-pool roll by default (a single `uncommon`-pool-at-≤`rare`-chance row
     is permitted, not standard).
   - **`elite` (§5.2):** `guaranteed` `shards`; 2–3 region-material rows at `common`/`uncommon`;
     exactly one emberstone row (region's tier, `10_systems/ENHANCEMENT.md` §1) at `uncommon`;
     exactly one pool-roll row (`rarity_source: elite`); a use-item row at `uncommon`.
   - **`boss` (§5.3, `mob_011`-pattern region bosses):** `guaranteed` `shards`; `guaranteed`
     region-material row(s); emberstone row(s) — 1 `guaranteed` + 1 `uncommon`; exactly one
     `guaranteed` pool-roll row (`rarity_source: boss`); exactly the boss's two unique
     `item_equip` refs (mapping per rule 6 below) each on an `epic`-or-`legendary` row, with
     exactly one carrying `first_clear_guaranteed: true`.
   - **raid boss (§5.4, `mob_147`–`150`):** `guaranteed` `shards` (≥ the `boss` §3 mean floor);
     `guaranteed` raid-token row (Rift `item_etc` `0177`–`0192`); exactly one `guaranteed`
     pool-roll row (`rarity_source: raid`); exactly the raid boss's two unique refs,
     `legendary`-weighted.
5. **`rarity_source` gating (hard).** Present if and only if `ref` is a pool id; value matches the
   owner tier's expected source (`elite`/`boss`/`raid` per rule 4).
6. **Boss/raid unique refs (hard).** An `item_equip` ref inside the `0201`–`0230` `docs/ID_REGISTRY.md`
   block may appear **only** in a `boss`- or raid-boss-tier owner's table (task's explicit "boss
   uniques only in boss tables"), and must be one of the two IDs that doc's boss-unique mapping
   assigns to this owner's region-order number `n` (region order = `docs/WORLD_PLAN.md` Region
   overview R1–R11, then the four Rift raid bosses as `n`=12–15 — the same derivation
   `20_schemas/item.schema.md`'s `unique_of` rule uses, cited once, not restated twice).
7. **Equip `qty` (hard).** `qty_min == qty_max == 1` whenever `ref` is an `item_equip_*` id
   (unstacked, `10_systems/DROPS.md` §1).
8. **`shards` row math (hard).** For the `guaranteed` `shards` row, `[qty_min, qty_max]` equals
   `[round(0.8·mean), round(1.2·mean)]` where `mean = mean_shards_normal(owner.level) ·
   tier_mult` (`10_systems/DROPS.md` §3: `tier_mult` = 1/4/15 for `normal`/`elite`/`boss`; raid
   uses the `boss` mean as a tunable floor, not an exact multiplier — rule 4).
9. **`pools.yaml` shape (hard).** Exactly 12 `pools[]` entries; `id` = `pool_equip_r<NN>` where
   `NN` matches `region`'s order number; `entries[].item` resolves to an existing `item_equip` id
   (`20_schemas/item.schema.md`). **Tier fit (warn):** each entry's item `tier` should sit in the
   region's level band (`10_systems/ITEMS.md` §4, `docs/WORLD_PLAN.md`).
10. **Boss uniques excluded from pools (hard).** No `pools[].entries[].item` falls in the
    `item_equip_0201`–`0230` block (`10_systems/DROPS.md` §6: "Boss uniques are not in pools").
11. **`first_clear_guaranteed` cardinality (warn).** At most one row per boss/raid table carries
    it `true` (§5.3 guarantees "one of the two," not both).

## Template

```yaml
# --- drop_mob_NNN.yaml ---
id: drop_mob_{NNN}
schema: 20_schemas/drop_table.schema.md
references: [DROPS, ITEMS]        # add ENHANCEMENT if any emberstone row; WORLD_PLAN + PARTY for boss/raid tables
owner: mob_{NNN}                  # must equal this file's own NNN
rows:
  - { ref: shards, chance: guaranteed, qty_min: {int}, qty_max: {int} }   # every table has this row
  # --- normal (DROPS §5.1): 1-2 region-material rows, common/uncommon; optional use item at rare ---
  # - { ref: item_etc_{NNNN}, chance: common, qty_min: {int}, qty_max: {int} }
  # --- elite (DROPS §5.2): as normal, plus exactly one emberstone row + one pool row + a use item ---
  # - { ref: item_etc_{emberstone_id}, chance: uncommon, qty_min: 1, qty_max: 1 }
  # - { ref: pool_equip_r{NN}, chance: guaranteed, qty_min: 1, qty_max: 1, rarity_source: elite }
  # --- boss (DROPS §5.3): guaranteed materials + emberstone(s) + guaranteed pool + 2 unique rows ---
  # - { ref: pool_equip_r{NN}, chance: guaranteed, qty_min: 1, qty_max: 1, rarity_source: boss }
  # - { ref: item_equip_{unique_id_1}, chance: epic, qty_min: 1, qty_max: 1, first_clear_guaranteed: true }
  # - { ref: item_equip_{unique_id_2}, chance: legendary, qty_min: 1, qty_max: 1 }
  # --- raid boss (DROPS §5.4, mob_147-150 only): guaranteed raid token + guaranteed raid pool + 2 uniques ---
  # - { ref: item_etc_{raid_token_id}, chance: guaranteed, qty_min: 1, qty_max: 1 }
  # - { ref: pool_equip_r11, chance: guaranteed, qty_min: 1, qty_max: 1, rarity_source: raid }

# --- pools.yaml (single shared file) ---
id: drop_pools
schema: 20_schemas/drop_table.schema.md
references: [DROPS, ITEMS, WORLD_PLAN]
pools:
  - id: pool_equip_r{NN}
    region: {region_slug}
    entries:
      - { item: item_equip_{NNNN} }          # weight optional, defaults uniform
      - { item: item_equip_{NNNN}, weight: {n} }
  # repeat for all 12 regions
```

## Open Questions

- **`chance` — task text vs. DROPS.md.** The task's validation instruction reads "chance values
  only from the DROPS tier set," but `10_systems/DROPS.md` §1/§2 explicitly also permits "a raw
  float." This schema follows DROPS.md (the owning doc) and allows both, flagging the apparent
  stricter reading in the task text rather than silently narrowing what DROPS.md defines.
- **`first_clear_guaranteed` is this schema's invention.** `10_systems/DROPS.md` §5.3 describes the
  first-clear bad-luck-protection guarantee in prose but names no field; a static per-row
  probability table has no other way to flag which of the two uniques is the guaranteed one. The
  actual "has this character cleared before" state is server-tracked
  (`10_systems/PERSISTENCE.md`, parallel to `10_systems/DROPS.md` §8's one-time first-clear `exp`
  grants) — this field only marks *which row*, not *whether granted*. Confirm the field name/shape
  with the orchestrator before Phase D authors all 11 region-boss tables.
- **Raid `shards` (rule 8, raid case).** `10_systems/DROPS.md` §5.4 gives raid `shards` only as "use
  `boss` ×15 as the floor, tuned per raid," not an exact formula like normal/elite/boss — this
  schema can only validate a floor for raid tables, not an exact value. Owner: `10_systems/DROPS.md`
  §9 OQ (raid-token exchange loop, same area).
- **Boss-order table isn't tabulated anywhere.** Same gap `20_schemas/item.schema.md` flags: rule 6
  requires computing "boss #n" from `docs/WORLD_PLAN.md`'s region order; correct today but brittle.
  Flag for `docs/ID_REGISTRY.md` to consider tabulating the 15 boss-order→`mob_NNN`/table pairs.
- **Per-slot pool weighting.** `10_systems/DROPS.md` §6's own Open Question (uniform-across-slots
  vs. weighting toward a player's line weapon) is unresolved; `entries[].weight` supports either
  resolution without a schema change, so this schema takes no position.
- **Raid loot distribution.** Which party member receives a raid table's rolled rows is
  `10_systems/social/PARTY.md`'s (not yet authored); this schema fixes only the table shape
  (`10_systems/DROPS.md` §5.4), not who gets what.
- **Ownership-timer values (60 s/120 s) and per-zone shortening** are `10_systems/DROPS.md` §7's own
  Open Questions and are runtime behavior, not table-file fields — not modeled here.
