# INVENTORY.md — Carry, Pickup, Currency & Storage

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/ITEMS.md, 10_systems/DROPS.md, 10_systems/ECONOMY.md, 10_systems/DEATH_PENALTY.md,
10_systems/COMBAT_FORMULA.md, 10_systems/social/PARTY.md, 10_systems/PERSISTENCE.md,
20_schemas/item.schema.md, 40_assets/ART_BIBLE.yaml, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the player's **carried inventory, currency wallet, item pickup, and bank storage**.
Item categories and stat values are `10_systems/ITEMS.md`; who is *allowed* to loot a drop and for
how long is `10_systems/DROPS.md` §7 (tagging/ownership timer) with party distribution in
`10_systems/social/PARTY.md`; `shards` faucets/sinks are `10_systems/ECONOMY.md`. This doc owns
only the container: tabs, slot counts, stack sizes, the currency cap, the pickup mechanic, and the
inn bank. All of it is server-authoritative (`10_systems/PERSISTENCE.md`; anti-dupe).

## 1. Tabs and slots

Three inventory tabs, one per item category (`10_systems/ITEMS.md` §1) so an item always lands in a
predictable place:

| Tab | Holds | Base slots | Stack size |
|---|---|---|---|
| `equip` | `item_equip_*` | 24 | 1 (unstacked) |
| `use` | `item_use_*` | 24 | 100 |
| `etc` | `item_etc_*` | 24 | 999 |

A **slot** holds one stack (or one unstacked equip). Base **24 slots per tab**. Distinct stacks of
the same stackable item each take a slot until full (e.g., 150 of a 100-stack material = one full
slot of 100 + one of 50).

**Expansion policy (server-flagged).** Each tab expands in **+8-slot** increments to a **maximum of
48**, unlocked via a `shards` purchase at a town NPC (`10_systems/ECONOMY.md` sink) or as a quest
reward. Expansion state is per-character persisted (`10_systems/PERSISTENCE.md`). Designed now,
purchasable-unlock gated behind the live server flag; the solo client ships at the 24 base or a
generous default (Open Questions).

## 2. Stack sizes and quantity

- `use` items stack to **100**, `etc` items to **999**, equips are **unstacked** (1/slot) —
  equips carry per-item state (`enhance_level`, rolled affixes, soft-pity counter;
  `10_systems/ITEMS.md`, `10_systems/ENHANCEMENT.md`) and so can never merge.
- Stacks may be **split** (drag a partial quantity to an empty slot) and auto-**merge** on pickup
  into an existing non-full stack of the same ID before consuming a new slot.

## 3. Currency wallet (`shards`)

`shards` are **not** an inventory slot — they are a single per-character counter shown in the HUD
wallet. **Cap: 2,000,000,000** (design/display cap; stored server-side at 64-bit width for
headroom). At cap, further `shards` gains are **blocked at the source** (a drop that would overflow
is not granted and a HUD notice shows) rather than silently truncated — no `shards` are ever lost
from the stored balance. `shards` are never dropped or lost on defeat (`10_systems/DEATH_PENALTY.md`
§3). Whether the wallet is per-character or an account-shared purse is an
`10_systems/PERSISTENCE.md` decision (default: per-character at launch; §7 Open Questions).

## 4. Pickup — platformer-friendly auto-loot

Pickup is **automatic and contact-based**, not a press-to-loot prompt, to keep the side-scrolling
flow snappy (`00_vision/PILLARS.md` P1). When a drop the player is **eligible** for
(`10_systems/DROPS.md` §7 tagging) comes within the **auto-loot radius** of the player, it is
collected with no input:

- `shards` and stackable `use`/`etc` items **vacuum** toward and into the player automatically.
- Equips **auto-pickup** too, **if** the `equip` tab has a free slot; if the tab is full the equip
  **stays on the ground, still owned** by the player for its ownership window (§6) so nothing is
  lost — a HUD "inventory full" notice shows.
- A **manual-pickup toggle** lets players who want to leave gear behind switch equips (only) to
  press-to-loot; `shards` always auto-collect.

**Auto-loot radius:** **64 px = 4 tiles** at the 16 px grid locked by `40_assets/ART_BIBLE.yaml`
(`10_systems/COMBAT_FORMULA.md` §10) — half a second of travel at `base_move_speed` (128 px/s),
tuned so running past a drop grabs it. The radius value is not load-bearing to any formula; only
the *auto-on-contact* behavior is fixed here.

## 5. Full-inventory handling

When a tab is full, owned drops of that category **remain on the ground within their ownership
window** (§6) rather than being destroyed, auto-sold, or blocking the kill. The player frees a slot
(use an item, vendor, bank) and re-collects before the despawn timer. Nothing is ever auto-vendored
or auto-destroyed without input (P2 — the game never quietly takes your loot).

## 6. Loot ownership & the pickup timer (cited, not owned)

Eligibility and timing are **owned by `10_systems/DROPS.md` §7** and consumed here:

- A drop is **tagged** to whoever earned the kill; only eligible players may auto-loot it.
- **Exclusive window 60 s** (only tagger/party), then **free-for-all 60–120 s**, then **despawn at
  120 s** (`10_systems/DROPS.md` §7). This doc's pickup mechanic (§4) obeys those windows; it does
  not redefine them.
- In a party, **which member receives a shared drop** is `10_systems/social/PARTY.md`'s
  distribution rule; this inventory accepts whatever PARTY assigns to this character.

## 7. Bank storage (inn, designed now, server-flagged)

A **bank** lets a character stash items beyond the carried inventory, accessed at an **inn
interior in any bind town** (arc 1: Emberfoot Village `map_001`, Millbrook Central `map_018`,
Mossmere `map_043`, Tidewatch Port `map_071`, Cindershelf `map_125`; arc 2: Frosthaven
`map_204`, Spirehaven `map_245`, Duskwatch Landing `map_285` — the bind-town list is
`10_systems/DEATH_PENALTY.md` §4's, per `docs/WORLD_PLAN.md` v3). The bank mirrors the three tabs:

| Bank tab | Holds | Base slots | Stack size |
|---|---|---|---|
| `equip` | `item_equip_*` | 32 | 1 |
| `use` | `item_use_*` | 32 | 100 |
| `etc` | `item_etc_*` | 32 | 999 |

- **Per-character at launch**; an **account-shared vault tab** (share gear/mats across your
  characters) is designed as a later server-flagged addition, not enabled in the solo pass.
- Banked contents persist server-side (`10_systems/PERSISTENCE.md`); the bank is the primary place
  to hold region materials (`item_etc`) between crafting/quest turn-ins and spare enhanced gear.
- Bank expansion follows the §1 policy (+8/tab, `shards` sink `10_systems/ECONOMY.md`), separate
  from carried-inventory expansion.

Depositing/withdrawing `shards` is **not** modeled (the wallet §3 is already account/character
state, not a bankable stack); the bank stores items only.

## 8. Quality-of-life

- **Auto-sort** per tab (group by category → tier → rarity, stack merge).
- **Slot lock** to protect an item from sort/quick-vendor.
- **Quick-vendor** sells all unlocked `common` equips at a vendor (prices `10_systems/ECONOMY.md`
  §4) with a confirm — a convenience faucet, never automatic (§5).

## 9. Authority

Inventory, wallet, bank, expansion state, and every pickup are **server-authoritative** in the live
build (`00_vision/PILLARS.md` P6; contract `10_systems/PERSISTENCE.md`). The solo client holds an
advisory copy; the server validates on sync to prevent duplication or unearned `shards`. No client
may mint items or `shards` or self-assign a drop it was not tagged for
(`10_systems/DROPS.md` §7).

## Open Questions

- Base slot count (24/tab) and the +8→48 expansion cap are first-pass; if the solo pass should ship
  more generous (no purchasable gating without a server), default to the 48 max unlocked in solo
  and gate expansion purchases only on the live server. Owner: this doc with
  `10_systems/PERSISTENCE.md`.
- `shards` wallet scope (per-character vs account-shared) and whether the bank ever holds `shards`
  are `10_systems/PERSISTENCE.md` calls; §3/§7 assume per-character wallet, item-only bank.
- Auto-loot radius (64 px) and vacuum speed inherit `10_systems/COMBAT_FORMULA.md` §10's tile-scale
  Open Question; finalize when `40_assets/ART_BIBLE.yaml` locks the scale.
- Whether a full `equip` tab should offer an **auto-vendor-`common`-on-pickup** opt-in (to avoid
  ground-clutter at high kill rates) is floated but **off by default** (§5's never-take-without-
  input rule). Flag if high-level farming proves too slot-pressured.
- Account-shared vault tab and cross-character mail-based item transfer are deferred to the social
  pass; if added, mail item-attachment limits belong to `10_systems/social/MAIL.md` (which already
  owns mail attachment policy), not here.
