# DROPS.md — Drop Table Semantics, Shard Faucet & Loot Ownership

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/ECONOMY.md,
10_systems/LEVELING.md, 10_systems/COMBAT_FORMULA.md, 10_systems/ELEMENTS.md,
10_systems/social/PARTY.md, 10_systems/social/RAID.md, 10_systems/PERSISTENCE.md,
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

Exactly one drop table per monster, `drop_mob_NNN` numbered to match its `mob_NNN`
(`docs/ID_REGISTRY.md`; arc-1 `001`–`150`, arc-2 continuing). A table is an unordered list of **rows**, each rolled **independently**
when the monster dies (one monster can drop several rows, or none but its guaranteed `shards`):

| Field | Meaning |
|---|---|
| `ref` | a concrete item ID (`item_equip_*`/`item_use_*`/`item_etc_*`), the literal `shards`, or a named pool `pool_equip_r01`–`r11` (§6) |
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
| `legendary` | 0.0015 | rarest pool rolls, raid uniques |

## 3. Shard faucet — `shards` per kill by monster level

`shards` are the primary faucet (`10_systems/ECONOMY.md` §1). A `guaranteed` `shards` row on every
combat monster; amount rolls uniformly in a ±20% band around the level mean. Formula is
authoritative; the table is the checksum. Tier multiplies the mean.

```
mean_shards_normal(L) = round( 1.5·L + 3 )
range                 = [ round(0.8·mean), round(1.2·mean) ]
tier multiplier: normal ×1 · elite ×4 · boss ×15 · raid boss = §5.4
```

| Mob Lv | `normal` mean (range) | `elite` ×4 | `boss` ×15 |
|---|---|---|---|
| 1 | 5 (4–6) | 20 | 75 |
| 10 | 18 (14–22) | 72 | 270 |
| 20 | 33 (26–40) | 132 | 495 |
| 30 | 48 (38–58) | 192 | 720 |
| 50 | 78 (62–94) | 312 | 1,170 |
| 70 | 108 (86–130) | 432 | 1,620 |
| 90 | 138 (110–166) | 552 | 2,070 |
| 100 | 153 (122–184) | 612 | 2,295 |
| 105 | 160 (128–192) | 640 | 2,400 |

At the `10_systems/LEVELING.md` §1 pace (≈ 480 at-level kills/hour), pure-`normal` hunting income
is ≈ `480 · mean_shards_normal(L)` (≈ 8.6 K/h at Lv 10, ≈ 37 K/h at Lv 50, ≈ 73 K/h at Lv 100);
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
dedicated `fortune` build near Lv 100 reads a `fortune_drop_bonus ≈ 30` from STATS §3, giving
`m ≈ 1.30` (+30% rare-loot rate) — the assassin-fantasy payoff of the `flicker`/`dirk` double-dip
(`10_systems/STATS.md` §2.1) without warping the economy.

### 4.1 `party_drop_bonus` — grouping loot bias

The loot analogue of `10_systems/social/PARTY.md` §4's exp party bonus: same-map hunting improves
**loot**, not just `exp`, so a party out-drops the same players hunting alone (P3, the social pull).
`10_systems/social/PARTY.md` supplies **who is eligible** (its §4 same-map eligibility, count
`n_eligible`); this doc owns the multiplier and how it composes. A fixed lookup on the same-map
eligible member count (a flat table, like the exp party bonus):

| same-map eligible members | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| `party_drop_bonus` | 1.00 | 1.05 | 1.10 | 1.16 | 1.22 | **1.30** |

`party_drop_bonus` multiplies the **same sub-`guaranteed` `chance` rolls** `m` (§4) multiplies —
item/material/emberstone/unique rows and the pool rarity-weight bias — and **composes with
`fortune` by multiplication**: the applied factor is `m · party_drop_bonus · guild_drop_buff`,
where `guild_drop_buff` is the optional guild grouping buff (`10_systems/social/GUILD.md` §10,
default 1.00, baseline `1.05` when 2+ guildmates share the party, lifted to `1.10` for the week
after a met weekly guild goal — the time-boxed lift is `10_systems/social/GUILD.md` §11's). It does
**not** touch
`guaranteed` rows, `shards`, or `qty`. The combined-adjusted `chance` obeys the **same ≤ 0.95
clamp** as §4, so no combination of grouping and `fortune` ever makes a drop certain. A solo-in-party
member (everyone else off-map) draws `1.00` — no bonus without company.

**Table locked at the 2026-07-24 balance pass** — the combined grouping-plus-`fortune` ceiling
checks out against the faucet:

- **Combined factor.** `m · party_drop_bonus · guild_drop_buff` ≤ 2.00 × 1.30 × 1.05 = **×2.73**
  hard ceiling at the baseline buff, 2.00 × 1.30 × 1.10 = **×2.86** during a
  `10_systems/social/GUILD.md` §11 weekly-goal lift week (the §4 `m` cap is nearly unreachable — a
  dedicated `fortune` build reads `m ≈ 1.30`, giving a realistic ceiling of
  1.30 × 1.30 × 1.05 ≈ **×1.77**, or 1.30 × 1.30 × 1.10 ≈ **×1.86** in a lift week).
- **Clamp check.** Only `common` (0.40) rows can hit the 0.95 clamp, and only at the theoretical
  ceiling (0.40 × 2.73 = 1.09, and 0.40 × 2.86 = 1.14 in a lift week → both clamped); at the
  realistic ceiling 0.40 × 1.77 = 0.71 (0.40 × 1.86 = 0.74 in a lift week) stays under it. Rare+
  rows stay small everywhere (`epic` 0.008 → 0.023 worst-case) — no drop becomes certain and no
  rarity band collapses.
- **Aggregate faucet.** Material/use rows duplicate per eligible member
  (`10_systems/social/PARTY.md` §5), so six partied players already generate the same per-player
  drop count as six solo hunters; `party_drop_bonus` adds at most **+30%** item supply on top
  (+36.5% with the baseline guild buff, +43% during a §11 lift week) — a bounded carrot,
  deliberately smaller than the exp twin's +100%, and `shards` (the primary faucet, §3) are
  untouched entirely.

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

### 5.4 raid boss (raid-entry kill)
- Applies to a **raid-entry** kill of one of the four raid finale bosses
  (`mob_027`/`mob_150`/`mob_178`/`mob_234`, `10_systems/social/RAID.md` §2). The **same boss killed
  via the open (non-raid) arena entry** (`10_systems/social/RAID.md` §7) is a plain region-boss kill
  and takes §5.3 instead — the entry context is the whole of the reward difference
  (`10_systems/social/RAID.md` §6); no other math forks.
- Party-shared loot; **who receives which roll is `10_systems/social/PARTY.md`'s distribution
  rule**, not this doc. This doc owns the table shape:
- `shards` — `guaranteed`, large (raid `shards` = §3 `boss` mean × the raid `life` factor is
  overkill; use `boss` ×15 as the floor, tuned per raid).
- **Raid tokens** — the raid's `raid_token` (`item_etc_0177` Undervault Seal / `0178` Mainspring
  Cog / `0179` Deepfrost Shard / `0180` Voidtide Pearl, `docs/ID_REGISTRY.md`) — `guaranteed`, one
  per participating member; **raid entry only** (an open-arena solo kill of the same boss drops
  none, resolving the shared-boss question). The **first-clear-of-the-day** grants **one extra**
  token to each member (`10_systems/LEVELING.md` §3.1; day boundary per
  `10_systems/PERSISTENCE.md`). Tokens are spent at the **Raid Quartermaster** on the
  raid-exclusive gear (`item_equip_0223`–`0230`) and cosmetics (`item_cosmetic_0001`–`0008`) —
  catalog/prices owned by `10_systems/ITEMS.md`, exchange rules by `10_systems/social/RAID.md`.
- **One guaranteed pool roll**, `rarity_source = raid` (§5.5) — `rare`+ emphasis.
- **The bonus room is a separate table, not a row here.** A raid-entry kill also opens that raid's
  bonus room (`10_systems/social/RAID.md` §6.E); its `reactor` nodes roll
  `drop_raid_bonus_<raid>` (`50_content/drop_tables/`), which is **not** part of this boss table
  and is not rolled on the boss's death. Its chance buckets are §2's, unchanged.
- **Raid uniques** — the finale boss's two uniques come from the boss's **own** drop table
  (`10_systems/ITEMS.md` §11; no separate raid-only unique list, `10_systems/social/RAID.md` §6),
  `legendary`-weighted on a raid-entry kill.

### 5.5 Pool rarity-roll weights (`rarity_source`)

A pool roll (§6) first picks a base equip from the region pool, then rolls its `rarity`
(`10_systems/ITEMS.md` §5 turns `rarity` into affix lines). `fortune` (§4) biases these before
renormalization.

| `rarity_source` | `common` | `uncommon` | `rare` | `epic` | `legendary` |
|---|---|---|---|---|---|
| `elite` | 55 | 35 | 9 | 1 | 0.2 |
| `boss` | 0 | 30 | 50 | 18 | 2 |
| `raid` | 0 | 0 | 40 | 45 | 15 |

The `raid` row fires **only** on a raid-entry finale-boss kill (§5.4); the same boss soloed via the
open (non-raid) arena entry rolls the `boss` row (§5.3, `10_systems/social/RAID.md` §6–§7).

## 6. Region equip pools (`pool_equip_r01`–`r11`)

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
in pools — they are direct `ref` rows (§5.3/§5.4).

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
- **`party_drop_bonus` (§4.1) — locked 2026-07-24.** The table (1.00/1.05/1.10/1.16/1.22/1.30) and
  its multiplication with `m` and `guild_drop_buff` under the ≤ 0.95 clamp are final (ceiling
  arithmetic in §4.1). Remaining open only for telemetry: whether per-member duplication plus the
  +30% party lift over-supplies any *specific* material once real hunting data exists — if so, tune
  that material's row `chance`, never this table. Owner: this doc with `10_systems/ECONOMY.md`.
- **Resolved (2026-07-24 contradiction fix): concrete raid-token IDs.** The four tokens are
  committed in §5.4 (`item_etc_0177` Undervault Seal · `0178` Mainspring Cog · `0179` Deepfrost
  Shard · `0180` Voidtide Pearl) and minted in `docs/ID_REGISTRY.md`; the rest of the reserved
  raid-token block (`item_etc_0177`–`0192`) stays open for future raids. The token → raid-gear
  exchange catalog/prices remain `10_systems/ITEMS.md`'s (`10_systems/social/RAID.md` §6.B–C); this
  doc fixes only that the `guaranteed` raid-entry token grant exists (§5.4, a runtime entry-context
  grant per `20_schemas/drop_table.schema.md` rule 4 — never extra static rows).
- Ownership-timer values (60 s / 120 s) and whether dungeons/arenas shorten them are first-pass;
  confirm against `10_systems/social/PARTY.md` loot rules and `15_maps_system/MAPS_SYSTEM.md` zone
  behavior.
- Per-slot pool weighting (§6) — uniform vs weighting toward the player's line's weapon — is a
  `pools.yaml` authoring choice; default uniform-across-slots so all lines share a pool. Flag if
  weapon drops feel too diluted across four types.
