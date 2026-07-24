# SCROLLS.md — Gear-Modification Scrolls (Aspect & Temper)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/ECONOMY.md, 10_systems/DROPS.md,
10_systems/QUESTS.md, 10_systems/PERSISTENCE.md, 20_schemas/item.schema.md,
docs/ID_REGISTRY.md, docs/WORLD_PLAN.md, docs/VALIDATION.md

Owner doc for **gear-modification scrolls**: the `item_use` consumables that change an equip's
**affix lines** after it drops. This is the affix side of the gear-mutation seam. The **base** side
— an item's `power`/`armor`/… base lines and how they grow — is `10_systems/ENHANCEMENT.md`'s
`emberstone` +1..+9 track, and only that. The split is exact and load-bearing:

- **`10_systems/ENHANCEMENT.md` owns base-line growth.** Emberstone is the only way an item's
  **base** lines (`10_systems/ITEMS.md` §7–§9) grow, and it never touches affix lines.
- **This doc owns affix-line change.** Scrolls are the only way an item's **affix** lines
  (`10_systems/ITEMS.md` §10) change after it drops, and they never touch base lines.

That seam is already fixed in `10_systems/ENHANCEMENT.md` §4 — "Each `+` adds a percentage of the
item's **base lines** … never of its affix lines (§10 affixes stay fixed; only the base scales)" —
this doc is the other half of that sentence. Neither system alters an item's `rarity` or its affix
**line count** (`10_systems/ITEMS.md` §5); those are set when the item drops
(`10_systems/DROPS.md` §5.5) and are immutable thereafter.

Scrolls never leave `10_systems/ITEMS.md` §10's budget: they **redirect and perfect** a drop's
affixes toward its budget ceiling — the per-line pe cap and the rarity affix-pe budget — but never
raise that ceiling. Vertical power (a higher ceiling) is owned by emberstone and `rarity`, not here
(§1 contrast). All scroll rolls and results are server-authoritative (§6, `10_systems/PERSISTENCE.md`).

**Scope-out — utility/return scrolls are not this system.** Items like the Millbrook Return Scroll
(`item_use_0013`, `docs/ID_REGISTRY.md`) share the word "scroll" but are plain `use` items with no
gear-mod mechanic; their unowned teleport/return mechanic is `20_schemas/item.schema.md`'s separate
Open Question, not this doc's. This doc governs only the `aspect`/`temper` gear-modification
`scroll_kind`s below.

**Tokens.** The tokens this doc introduces — `aspect`, `temper`, `steady`, `bold`, `perilous`,
`scroll_kind`, `scroll_tier`, `slot_family`, and the family values `weapon_family` / `armor_family`
/ `accessory_family` — are proposed by the producer via `00_vision/GLOSSARY.md` `## Provisional` at
the gate; this doc is their owner-of-semantics once promoted.

## 1. What a scroll is, and the two kinds

A gear-modification scroll is an `item_use` consumable applied to **one** target equip. A scroll's
SKU fixes three things: its `scroll_kind` (§1.1/§1.2), its `scroll_tier` (§2), and its `slot_family`
(§3). A scroll may be applied only to an equip that (a) belongs to its `slot_family` and (b) has
**≥ 1 affix line** — i.e. `uncommon` or better (`10_systems/ITEMS.md` §5). A `common` item (0 affix
lines) has nothing for a scroll to act on and is UI-blocked as a target. No scroll ever changes an
item's `rarity` or its affix **line count**.

### 1.1 `aspect` — reroll one line

An `aspect` scroll **replaces one random affix line** on the target with a freshly rolled line drawn
from `10_systems/ITEMS.md` §10's "Affix eligibility by slot" menu for the target's slot, at the §10
**menu magnitude** (anchor) for the item's `req_level`. It changes which line occupies that slot, not
how many lines exist. Because the replacement is a menu-anchor line, it always lands within the §10
per-line pe cap by construction, and — since any anchor line's pe is ≤ the cap and the budget is
`count × cap` — the item's total affix pe stays within its rarity budget after any reroll.

### 1.2 `temper` — raise one line toward the cap

A `temper` scroll **permanently raises one random eligible affix line's magnitude** by a fixed
**temper step**:

```
temper_step(line, L) = round( tier_pct · anchor(line, L) )      # anchor = §10 menu value at req_level L
```

`tier_pct` is set by `scroll_tier` (§2); `anchor(line, L)` is that line's `10_systems/ITEMS.md` §10
menu magnitude at the item's `req_level`, in the line's own units. Steps are **anchor-based and
linear** (not compounding on the current value), so the number of steps to reach cap is fixed and
readable (`00_vision/PILLARS.md` P1). After the raise, the new magnitude is **clamped down** so that:

- the line's pe (`10_systems/ITEMS.md` §6 weights) never exceeds the §10 **per-line pe cap**, and
- the item's **total affix pe** never exceeds its `rarity` **affix-pe budget** (§10).

A line already at the per-line cap (or whose remaining budget headroom rounds the effective step to
0) is **ineligible**. `temper` picks its target randomly among the eligible lines only; if **no**
line is eligible the scroll is **UI-blocked before use** — it is not consumed or wasted.

### 1.3 What scrolls do that emberstone does not

|  | Emberstone (`10_systems/ENHANCEMENT.md`) | Scrolls (this doc) |
|---|---|---|
| Lines touched | **base** lines only (§4 seam) | **affix** lines only |
| Vertical power / ceiling | **raises** it (`+1..+9` multiplier on base) | **never** — result stays ≤ §10 budget |
| What varies | magnitude of the fixed base lines | which affix line (`aspect`) / its magnitude within cap (`temper`) |
| `rarity` / affix line count | unchanged | unchanged |
| Randomness | success/fail roll, **pity-bounded** (§3) | success/fail roll, **no pity** at launch (§2) |
| On failure | item untouched (no destruction/downgrade) | item untouched (no destruction/downgrade) |

The identity is the last two rows read together: scrolls are the **horizontal** tuning of a drop
toward the budget it already carries; emberstone and `rarity` are the **vertical** power that sets
that budget. Neither can do the other's job.

## 2. Success tiers (`scroll_tier`)

Each SKU carries one `scroll_tier`. Risk buys **efficiency** (reaching the same ceiling in fewer
attempts / with a better draw), never a higher ceiling — every tier terminates at the §10 per-line
cap and rarity budget.

| `scroll_tier` | Success | `temper` step (`tier_pct` of anchor) | `aspect` draw |
|---|---|---|---|
| `steady` | **100%** | +15% | one random eligible line |
| `bold` | **60%** | +25% | **witnessed reroll** — the result is shown; the player may keep the prior line instead |
| `perilous` | **30%** | +40% | **two candidates** rolled; the higher-pe line is kept |

**On failure the item is completely untouched** — no destruction, no downgrade, no affix loss, ever;
only the scroll is consumed (`00_vision/PILLARS.md` P2, the same cozy stance as
`10_systems/ENHANCEMENT.md` §2, which this doc does not restate). The entire risk is the scroll
itself (currency and time); the worst case of any failed attempt is "the item is exactly as it was."

**No pity.** Because a failed attempt can never harm the item, there is no pity counter on scrolls at
launch (unlike the enhancement track, whose pity exists to bound a *material/fee* worst case,
`10_systems/ENHANCEMENT.md` §3 — a concern scrolls do not share, the item being unharmed either way).
Whether a soft-pity should ease repeated `perilous` failures later is an Open Question.

## 3. Slot families (`slot_family`)

A scroll SKU targets one `slot_family`; it applies only to equips in that family
(`10_systems/ITEMS.md` §2 slot roster, being extended with `shield`/`overall` in that doc's §2/§10
revision — this doc binds to the family grouping, not a hardcoded slot count):

| `slot_family` | Equip slots covered |
|---|---|
| `weapon_family` | `weapon` |
| `armor_family` | `head`, `body`, `legs`, `boots`, `gloves`, `shield`, `overall` |
| `accessory_family` | `cape`, `ring`, `amulet` |

A family mismatch is UI-blocked (an `armor_family` scroll cannot be applied to a `weapon`). Within a
family, the reroll/temper menu is still the **per-slot** §10 eligibility set (a `cape` and a `ring`
share `accessory_family` but draw different lines) — the family gates *which scroll fits*, §10 gates
*which lines it may produce*.

## 4. Acquisition & economy

Scrolls are an economy **sink** by design: buying and consuming-on-fail retire `shards`/items, while
the small vendoring faucet of dropped scrolls (§4.4) never nets positive against them. The faucet of
the *item itself* is drops/quests; the sink is the `shards` and attempts a player spends chasing a
perfect affix set. Net intent: **sink-dominant at every level band**.

### 4.1 Drops
Per `10_systems/DROPS.md` §5 tier shapes (this doc cites, it does not author the tables — those are
Phase D content against DROPS.md's shapes): `normal` mobs carry scroll rows at the `rare` chance
bucket (`10_systems/DROPS.md` §2); `elite` mobs at `uncommon`; bosses may carry `bold`/`perilous`
rows. Exact rows and which SKU sits where are Phase D drop-table content.

**Raid bonus rooms.** The four raid bonus rooms (`10_systems/social/RAID.md` §6.E, `map_325`–
`map_328`) are a named scroll source: every `reactor` there rolls its raid's bonus table, which
carries `steady` at `uncommon`, `bold` at `rare`, and `perilous` at `epic`. The `slot_family` (§3)
stocked is banded to that raid's level band. This is a better *rate* than the field, never an
exclusive — the same SKUs drop and vendor elsewhere (§4.1–§4.2), so a solo player is never locked
out of a scroll tier (`00_vision/PILLARS.md` P2). The rates are RAID.md §6.E's; the node count is
**6 per room**, authored on `map_325`–`map_328`. That makes the faucet computable and it has not
been checked against §4.4's sink-dominant requirement — per clear, per member, 6 nodes pay ≈0.9
`steady` · 0.24 `bold` · 0.048 `perilous`, and if the per-member-copy reading of
`10_systems/social/PARTY.md` §5 holds, a 6-member party multiplies that by 6. A repeatable run
paying ≈1.4 `bold` and ≈0.3 `perilous` per clear would contradict §4.2's "drop-/quest-only chase
item" stance. Flagged in RAID.md's Open Questions and owed to §4.4 before bonus-room content is
final — and that check must now be run against **both** new sources together, not the bonus room
alone: `10_systems/GACHAPON.md`'s Cogwork Capsule also draws these SKUs (10% of pulls, `scroll_tier`
weighted `steady` 60 / `bold` 30 / `perilous` 10). Two repeatable `perilous` faucets landed in the
same period against a §4.2 stance that calls `bold`/`perilous` drop-/quest-only chase items. Note
the bonus room *helps* `10_systems/MONETIZATION.md`'s PA-001 cap rather than straining it — it is
free-play evidence that the gacha's scroll prizes are not exclusives — but the combined faucet is
what §4.4's sink-dominant requirement has to clear.

### 4.2 Vendor / shard shop
Only `steady`-tier scrolls are vendor-purchasable — a pure recurring `shards` sink. `bold` and
`perilous` scrolls are **drop-/quest-only** (chase items), never on a vendor shelf. Prices are
`10_systems/ECONOMY.md`'s to own; this doc sets no numbers. `10_systems/ECONOMY.md` §2's sink table
already lists scrolls under "Consumables (tonics/cleanses/scrolls/foods)" — that is the standing
hook; the concrete price rows in `10_systems/ECONOMY.md` §4.1 are an Open Question for the D gate.

### 4.3 Quest rewards
Scrolls appear as quest rewards banded by region per `10_systems/QUESTS.md` (cited only; magnitudes
and which quests grant which SKU are that doc's / Phase D's).

### 4.4 Faucet/sink balance
Scroll **purchases** (§4.2) and **consumed-on-fail attempts** (§2) are `shards`/item sinks that scale
with how hard a player is chasing a perfect affix set — i.e. with their gear investment. A **dropped**
scroll vendors at the standard 25% of buy value (`10_systems/ECONOMY.md` §4), a minor faucet. Because
a chase costs many attempts per perfected item while each dropped scroll returns only a quarter of one
SKU's value, the system is sink-dominant at every band (`10_systems/ECONOMY.md` §6 inflation guard).

## 5. IDs & SKU-block layout

Gear-modification scrolls occupy a new `item_use` block **`item_use_0061`–`0078`** (18 SKUs =
3 `slot_family` × 2 `scroll_kind` × 3 `scroll_tier`), with **`0079`–`0090` reserved** for scroll
growth. `docs/ID_REGISTRY.md` owns these ranges; the registry extension landed in a companion producer
commit (the block sits inside the `item_use_0001`–`0100` space, after the `0017`–`0060`
Phase-D reservation). This doc owns only the **intra-block layout convention**:

| Range | `slot_family` | Order within the six |
|---|---|---|
| `0061`–`0066` | `weapon_family` | `aspect` steady/bold/perilous, then `temper` steady/bold/perilous |
| `0067`–`0072` | `armor_family` | same order |
| `0073`–`0078` | `accessory_family` | same order |

SKU display names are Phase D content (`20_schemas/item.schema.md`).

## 6. Authority (`10_systems/PERSISTENCE.md` §1)

| Data / action | `authority` |
|---|---|
| Scroll application roll (success/fail) + which line is targeted + reroll draw | `server` |
| Rewritten (`aspect`) / raised (`temper`) affix-line values on the item | `server` (item state) |
| Per-line temper-step count, if persisted for UI/tooling | `server` |
| Preview UI (odds, candidate/witnessed-reroll display, eligible-line highlight) | `client` |

The solo client may preview odds and simulate a result; the server is truth on sync — no
client-side "reroll until the outcome is good" (`00_vision/PILLARS.md` P6, same stance as
`10_systems/ENHANCEMENT.md` §6 and `10_systems/DROPS.md` §9).

## 7. Worked example — `temper` on a `rare` Lv 50 body piece

Start: a `rare` (2 affix lines) T8 `body` armor, `req_level` 50 (`10_systems/ITEMS.md` §4: T8 = Lv 50). Base 98 `armor` / 69 `warding`
(`10_systems/ITEMS.md` §8) = 16.7 pe. Affixes: **+12 `might`** (12 pe) + **+132 `life`**
(132 × 0.03 = 3.96 pe) = 15.96 pe of affix budget, against the `rare` @ Lv 50 budget of **34 pe**;
per-line cap **17 pe** (`10_systems/ITEMS.md` §10). All arithmetic uses §6 pe weights.

Apply a **`bold` `temper`** (`armor_family`; 60% success, +25% step). The `might` line's anchor at
Lv 50 is 12, so `temper_step = round(0.25 · 12) = 3`. Say the roll targets the `might` line and
succeeds:

- new line = **+15 `might`** = 15 pe. Per-line cap 17 pe: `15 ≤ 17` OK. Item total affix pe
  = 15 + 3.96 = 18.96 ≤ 34 OK. Applied.
- On the 40% **failure**, the piece is byte-for-byte unchanged; only the scroll is gone.

A second `bold` `temper` on the same line: `round(0.25 · 12) = 3` → 18 pe, which exceeds the 17 pe
cap, so it **clamps to +17 `might`** = 17 pe. The line is now at cap and becomes **ineligible** for
any further `temper` (UI-blocked as a target choice).

Risk buys only the *pace* to that same ceiling, never a higher one:

| Tier | step (of anchor 12) | attempts 12 pe → 17 pe cap |
|---|---|---|
| `steady` | `round(0.15·12)=2` | 3 (12→14→16→17 clamp) |
| `bold` | `round(0.25·12)=3` | 2 (12→15→17 clamp) |
| `perilous` | `round(0.40·12)=5` | 1 (12→17 clamp) |

All three roads dead-end at the **17 pe per-line cap** and the **34 pe rarity budget** — the drop's
own §10 ceiling. After capping the `might` line, total affix pe = 17 + 3.96 = 20.96 ≤ 34; and any
emberstone `+N` on this piece still scales only its 98/69 **base**, never these affix numbers
(`10_systems/ENHANCEMENT.md` §4 seam). An `aspect` scroll here would instead swap one of the two
lines (say +12 `might` → +132 `life`, or +48 `armor`) at menu magnitude — different affixes, same
line count, same budget.

## Open Questions

- **Soft-pity for `perilous` fails.** No pity exists on scrolls at launch (§2) — justified because a
  failed attempt never harms the item, so the worst case is bounded currency/time, not a lost item.
  Whether a soft-pity (e.g. accumulating success chance on repeated `perilous` failures at the same
  scroll) is wanted later is deferred; if added it would be a chance-only counter (never an item
  guarantee) tagged `server` (§6). Owner: this doc with `10_systems/ECONOMY.md`.
- **`10_systems/ECONOMY.md` §4.1 scroll price rows.** `10_systems/ECONOMY.md` §2's sink table already
  names scrolls under consumables (§4.2 hook), but §4.1 has no concrete `buy`/`sell` rows for the
  `steady` vendor SKUs. Those rows are needed at the D gate. Owner: `10_systems/ECONOMY.md` (this doc
  files, does not price).
- **Duplicate-line rerolls.** May an `aspect` reroll produce a line whose `stat` already occupies
  another slot on the item (two `might` lines)? Default: **yes** — stacking is self-limited by the
  §10 per-line cap and the rarity budget, so a duplicate is never free power; forbidding it would add
  a special case. Flag if content wants distinct-line guarantees on high-rarity gear.
- **`temper` target selection.** `temper` picks its raised line **uniformly at random** among eligible
  lines (§1.2). Whether a future "directed temper" SKU (player chooses the line, at a steeper price /
  lower success) is wanted is deferred; it would be a new `scroll_kind` and a new ID sub-block within
  the §5 reserved `0079`–`0090`, not a change to these SKUs. Owner: this doc.
- **Drop/quest scroll placement.** Exact `10_systems/DROPS.md` §5 rows (which mobs/bosses carry which
  SKU and tier) and `10_systems/QUESTS.md` region banding (§4.1/§4.3) are Phase D content against
  those docs' shapes; this doc fixes only the buckets (`rare`/`uncommon`, boss `bold`/`perilous`) and
  the vendor `steady`-only rule (§4.2). Flagged for the D content batch.
