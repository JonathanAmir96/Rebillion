# DROPS.md — Drop Table Semantics, Shard Faucet & Loot Ownership

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/ECONOMY.md,
10_systems/LEVELING.md, 10_systems/COMBAT_FORMULA.md, 10_systems/ELEMENTS.md,
10_systems/social/PARTY.md, 10_systems/social/PARTY_QUEST.md, 10_systems/PERSISTENCE.md,
20_schemas/monster.schema.md,
20_schemas/drop_table.schema.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md,
50_content/drop_tables/pools.yaml

Owner doc for **what a monster drops and who may pick it up**: the drop-table row shape, the drop
chance vocabulary, the `shards` faucet (per-kill `shards` by monster level), how `fortune` biases
loot, the per-tier table shapes, the region equip pools, and the tagging/ownership rules. Item
*definitions* and `rarity` semantics are `10_systems/ITEMS.md`; `emberstone` behavior is
`10_systems/ENHANCEMENT.md`; the `shards` *economy* (prices, sinks, income balance) is
`10_systems/ECONOMY.md`; party loot *distribution* is `10_systems/social/PARTY.md`. This doc owns
the roll; those own what the rolled thing is worth or how a party splits it.

## 1. Drop table & row shape

Exactly one drop table per monster, `drop_mob_001`–`drop_mob_150`, number matching its `mob_NNN`
(`docs/ID_REGISTRY.md`). A table is an unordered list of **rows**, each rolled **independently**
when the monster dies (one monster can drop several rows, or none but its guaranteed `shards`):

| Field | Meaning |
|---|---|
| `ref` | a concrete item ID (`item_equip_*`/`item_use_*`/`item_etc_*`), the literal `shards`, or a named pool `pool_equip_r01`–`r08` (§6) |
| `chance` | probability in `[0,1]`, expressed as a §2 named bucket or a raw float |
| `qty_min`–`qty_max` | integer quantity rolled uniformly if the row hits (unstacked equips are always 1) |
| `rarity_source` | *(pool rows only)* which §5 rarity-weight row instantiates the equip's `rarity` |

`20_schemas/drop_table.schema.md` (Phase C) formalizes the field types; this doc owns the roll
semantics. Every `ref` must resolve (`docs/VALIDATION.md` §2). Region pools are authored in
`50_content/drop_tables/pools.yaml`.

## 2. Drop chance vocabulary

Named probability buckets a `chance` may use (or a raw float). These are **drop probabilities**,
not to be confused with item `rarity` (`10_systems/ITEMS.md` §5) — though a `legendary`-rarity item
naturally sits on a `legendary`-chance row. Tune per monster within these anchors.

| Bucket | `chance` | Typical use |
|---|---|---|
| `guaranteed` | 1.00 | `shards` on any kill; boss pool/material rows |
| `common` | 0.40 | region etc materials from `normal` mobs |
| `uncommon` | 0.15 | a second material, `elite` emberstone, use items |
| `rare` | 0.04 | `elite` pool roll, use items from `normal` |
| `epic` | 0.008 | boss uniques (region), high-end pool rolls |
| `legendary` | 0.0015 | rarest pool rolls, the more prized boss uniques |

## 3. Shard faucet — `shards` per kill by monster level

`shards` are the primary faucet (`10_systems/ECONOMY.md` §1). A `guaranteed` `shards` row on every
combat monster; amount rolls uniformly in a ±20% band around the level mean. Formula is
authoritative; the table is the checksum. Tier multiplies the mean.

```
mean_shards_normal(L) = round( 1.5·L + 3 )
range                 = [ round(0.8·mean), round(1.2·mean) ]
tier multiplier: normal ×1 · elite ×4 · boss ×15
```

The formula covers the full Lv 1–300 curve; the checksum table samples only the authored arc
(monsters top out at Lv 42, `docs/WORLD_PLAN.md`). Future arcs sample the same formula at their
bands — no new faucet rule needed.

| Mob Lv | `normal` mean (range) | `elite` ×4 | `boss` ×15 |
|---|---|---|---|
| 1 | 5 (4–6) | 20 | 75 |
| 10 | 18 (14–22) | 72 | 270 |
| 20 | 33 (26–40) | 132 | 495 |
| 30 | 48 (38–58) | 192 | 720 |
| 40 | 63 (50–76) | 252 | 945 |
| 42 | 66 (53–79) | 264 | 990 |

At the `10_systems/LEVELING.md` §1 pace (≈ 480 at-level kills/hour), pure-`normal` hunting income
is ≈ `480 · mean_shards_normal(L)` (≈ 8.6 K/h at Lv 10, ≈ 30 K/h at Lv 40, the arc's end);
`10_systems/ECONOMY.md` §5 balances this against sinks. `shards` are **not** affected by `fortune`
(§4) — income stays steady and legible (P2); only item luck varies.

## 4. `fortune` loot bias (applying the STATS hook)

`10_systems/STATS.md` §3 owns the `fortune_drop_bonus` hook (a percentage derived from `fortune`)
and leaves its application and any cap to this doc. Application — read the hook value from STATS,
then:

```
m = 1 + min(fortune_drop_bonus, 100) / 100          # DROPS caps the bonus at +100% (×2)
```

`m` multiplies (a) the `chance` of any **sub-`guaranteed` item/material/emberstone/unique row**,
and (b) the **weight of `uncommon`-and-rarer outcomes** in a §5 pool rarity roll (weights
renormalized after). It does **not** touch `guaranteed` rows, `shards` (§3), or `qty`. An adjusted
`chance` is clamped to ≤ 0.95 so luck never silently makes a drop certain. The cap rarely binds: a
dedicated `fortune` build at the arc's end (Lv 40+) reads a `fortune_drop_bonus ≈ 10–12` from
STATS §3, giving `m ≈ 1.1` (+~10% rare-loot rate, growing with future arcs' stat totals) — the
assassin-fantasy payoff of the `flicker`/`dirk` double-dip
(`10_systems/STATS.md` §2.1) without warping the economy.

## 5. Per-tier table shapes

The baseline shape each monster tier's `drop_mob` table follows. Content may add thematic rows
within these shapes; the guarantees are the contract.

### 5.1 `normal`
- `shards` — `guaranteed`, §3 `normal` range.
- 1–2 region etc materials (`item_etc`, that region's block per `docs/WORLD_PLAN.md`) — `common` /
  `uncommon`.
- A use item (tonic/cleanse) — `rare`.
- **No** equip pool roll by default (gear is the payoff of `elite`+; a per-mob single `uncommon`
  pool row at ≤ `rare` chance is permitted but not standard).

### 5.2 `elite`
- `shards` — `guaranteed`, §3 `elite` (×4).
- 2–3 etc materials — `common`/`uncommon` (elites are the material-density farm,
  `10_systems/LEVELING.md` §3).
- One emberstone of the region's tier (`10_systems/ENHANCEMENT.md` §1) — `uncommon`.
- **One pool roll** from `pool_equip_r<region>` (§6), `rarity_source = elite` (§5.5).
- A use item — `uncommon`.

### 5.3 `boss` (region boss)
- `shards` — `guaranteed`, §3 `boss` (×15).
- Region materials — `guaranteed` (crafting/quest mats).
- Emberstone(s) — 1 `guaranteed` + a 2nd at `uncommon`.
- **One guaranteed pool roll**, `rarity_source = boss` (§5.5) — a `rare`+ equip every kill.
- **Boss uniques** — the boss's two uniques (`10_systems/ITEMS.md` §11), each on an `epic` row
  (or `legendary` for the more prized one). **First-ever clear guarantees one** of the two
  (bad-luck protection, P2); later kills roll the chance.

### 5.4 Party-quest boss drops
The two party-quest finale bosses (`pq_undervault` → The Cellar King, `pq_mainspring` → The
Custodian; `docs/WORLD_PLAN.md`) are **existing regional bosses** — their tables follow the
standard §5.3 boss shape, no separate tier. In a party, who receives which roll is
`10_systems/social/PARTY.md`'s distribution rule, not this doc's. PQ-specific reward shaping
(the reduced-reward solo open-arena entry, any run-completion bonuses) is owned by
`10_systems/social/PARTY_QUEST.md` — linked, not restated here.

### 5.5 Pool rarity-roll weights (`rarity_source`)

A pool roll (§6) first picks a base equip from the region pool, then rolls its `rarity`
(`10_systems/ITEMS.md` §5 turns `rarity` into affix lines). `fortune` (§4) biases these before
renormalization.

| `rarity_source` | `common` | `uncommon` | `rare` | `epic` | `legendary` |
|---|---|---|---|---|---|
| `elite` | 55 | 35 | 9 | 1 | 0.2 |
| `boss` | 0 | 30 | 50 | 18 | 2 |

## 6. Region equip pools (`pool_equip_r01`–`r08`)

A named pool per region (`docs/ID_REGISTRY.md`; contents authored in
`50_content/drop_tables/pools.yaml`). A pool lists the **base equip IDs** (`item_equip_*` weapons/
armor/accessories) whose `tier` matches that region's level band (`10_systems/ITEMS.md` §4,
`docs/WORLD_PLAN.md`). A **pool roll**:

1. pick a base item from the pool (weighted roughly uniform across slots, or per-pool weights in
   `pools.yaml`);
2. roll its `rarity` from the §5.5 row for the source tier (`fortune`-biased, §4);
3. instantiate affix lines for that `rarity` per `10_systems/ITEMS.md` §10.

Pools are region-scoped so a monster drops **level-appropriate** gear (P2 legible progression). A
pool `ref` in a `drop_mob` row means "roll this pool," not a specific item. Boss uniques are **not**
in pools — they are direct `ref` rows (§5.3).

## 7. World drop, tagging & ownership

Drops are **tagged** to whoever earned the kill; loot is not free-for-all off the corpse.

- **Tag eligibility.** A player (or their party, `10_systems/social/PARTY.md`) becomes eligible by
  **dealing or taking damage** to/from the monster before it dies (the "anyone-who-tagged" rule).
  Untagged bystanders cannot loot.
- **Ownership timer.** On death, drops spawn owned by the tagger(s) for an **exclusive window of
  60 s**; during it only eligible players may pick up. From 60–120 s the drop is **free for
  anyone**; at **120 s** unclaimed drops **despawn**. `shards` and quest items auto-route to the
  tagger and never lie on the ground for others.
- **Solo vs party.** Solo, the single tagger owns everything. In a party, eligibility is shared and
  **which member receives each drop is `10_systems/social/PARTY.md`'s distribution rule**
  (round-robin / need-vs-greed / free-for-all — owned there, not here). This doc owns tagging and
  the timer; PARTY owns the split.
- Pickup mechanics (auto-loot radius, full-inventory handling) are `10_systems/INVENTORY.md`; this
  doc owns only *who is allowed* and *for how long*.

## 8. Non-drop rewards (the exp "other 5%")

First-time events grant small one-time `exp` (`10_systems/LEVELING.md` §4 "other" ≈ 5%): a
region-boss **first clear**, a **first kill** of each bestiary species, and secret-map discovery.
These are one-time grants tracked in persistence (`10_systems/PERSISTENCE.md`), authored alongside
`drop_mob`/map data in Phase D; magnitudes are `10_systems/LEVELING.md`'s budget, not restated
here. The first-clear **unique guarantee** (§5.3) is this doc's rule.

## 9. Authority

All rolls (drop `chance`, `qty`, pool selection, `rarity`, `fortune` bias, tagging, timers) are
**server-authoritative** in the live build (`00_vision/PILLARS.md` P6; contract
`10_systems/PERSISTENCE.md`). The solo client simulates them; the server is truth on sync. No
client may re-roll a table or self-assign a rarity.

## Open Questions

- Chance-bucket anchors (§2), the §3 `shards` formula, and §5.5 rarity weights are first-pass;
  balance against `10_systems/ECONOMY.md` §5 (income vs sinks) and `10_systems/COMBAT_FORMULA.md`
  §14 (kills/hour) at the D gate. If income drifts, tune §3, not the item budgets.
- The `fortune` cap (+100%, §4) and whether it should also nudge `shards` slightly are open;
  default keeps `shards` `fortune`-free for steady income. Owner: this doc with
  `10_systems/ECONOMY.md`.
- Whether PQ finale runs deserve an extra completion row (beyond the standard §5.3 boss table) is
  `10_systems/social/PARTY_QUEST.md`'s call; flag any table-shape need back here before the
  Clockwork/PQ content batch (Phase D).
- Ownership-timer values (60 s / 120 s) and whether dungeons/arenas shorten them are first-pass;
  confirm against `10_systems/social/PARTY.md` loot rules and `15_maps_system/MAPS_SYSTEM.md` zone
  behavior.
- Per-slot pool weighting (§6) — uniform vs weighting toward the player's line's weapon — is a
  `pools.yaml` authoring choice; default uniform-across-slots so all lines share a pool. Flag if
  weapon drops feel too diluted across four types.
