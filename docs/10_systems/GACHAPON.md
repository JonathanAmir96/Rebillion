# GACHAPON.md — The Cogwork Capsule (Bounded Real-Money Gacha)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/MONETIZATION.md, 10_systems/COSMETICS.md, 10_systems/BATTLE_PASS.md,
10_systems/ECONOMY.md, 10_systems/DROPS.md, 10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md,
10_systems/SCROLLS.md, 10_systems/INVENTORY.md, 10_systems/PERSISTENCE.md,
15_maps_system/MAP_INTERACTABLES.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

Owner doc for the **gachapon system**, in-world the **Cogwork Capsule**: salvaged vending
automata from the Clockwork Ruins, restored by Millbrook tinkers, that dispense a random prize
per **capsule ticket** (`item_use_0021`). Tickets are earned free (charter lanes, rare world
drops) **and purchasable for real money** — the game's only real-money product, permitted by
owner amendment **PA-001** (2026-07-24): the single bounded exception to
`10_systems/MONETIZATION.md`'s MON-001 cosmetic-only charter, logged there and in
`00_vision/PILLARS.md`, and bounded by the §1 caps. This doc owns the machine, ticket sources, odds/pity, prize-pool rules, and the
containment guardrails. The prize pool's values are Phase D content
(`50_content/gacha/capsule_pool.yaml`); shards economy interactions are recorded in
`10_systems/ECONOMY.md` §6; authority is `10_systems/PERSISTENCE.md`'s.

## 1. The PA-001 containment caps (non-negotiable design bounds)

The owner accepted **small** pay-for-convenience, not a pay-to-win economy. Every cap below is
load-bearing; a change to any of them is a new pillar-amendment decision, not a Phase D tune:

1. **Power ceiling.** Every stat-relevant prize must be obtainable through ordinary play at
   comparable rates: consumables, emberstones, gear-modification scrolls
   (`10_systems/SCROLLS.md` SKUs, `item_use_0061`–`0078` — owner-approved as the capsule's
   "rare hit"), and equipment rolls capped at rarity **`rare`** from the player's existing
   region pools. **Never** dispensed: `epic`, `legendary`, boss uniques, or any capsule-only
   stat item. Capsule exclusives are cosmetics only (§5).
2. **Earnable free.** Tickets flow from the Wayfarer's Charter (both lanes,
   `10_systems/BATTLE_PASS.md` §5.1) and as a rare world drop — a paying player accelerates
   pulls, never accesses content others cannot reach.
3. **Purchase cap.** At most **10 tickets per character per week** may be bought with real
   money. No bulk discounts beyond §6's single small pack bonus; no "limited-time" pressure
   mechanics, ever.
4. **Published odds + pity.** The machine's UI displays the full §5 odds table before every
   pull; the §5 pity guarantee is stated there too.
5. **No real-money ↔ `shards` bridge.** Tickets can never be bought or sold for `shards`, and
   every dispensed prize has **vendor value 0** (§7) — money can never become `shards`, so
   `10_systems/ECONOMY.md` §1's faucet law is untouched.

## 2. The machine

One Cogwork Capsule stands in **Millbrook** (the social heart, P3) at launch; additional ring-town
machines may be placed later. It is a town interactable
(`15_maps_system/MAP_INTERACTABLES.md` — a `capsule` interactable kind is owed there, Open
Questions); interacting opens the capsule panel: ticket count, odds table, pity progress, pull
button (single or 10-pull; a 10-pull is ten independent §5 rolls, no changed odds).

## 3. Capsule tickets — `item_use_0021`

An ordinary `item_use` inventory item (etc-tab stack rules per `10_systems/INVENTORY.md`),
consumed one per pull. Buy/sell value **0** (never vendorable, never `shards`-purchasable).

| Source | Amount | Notes |
|---|---|---|
| Charter free lane | 4 / season | `10_systems/BATTLE_PASS.md` §5.1 |
| Charter gilt lane | +8 / season | gilt total 12/season |
| Rare world drop | ≈ 1 per 6–8 h at-level play (owner-set band) | drop-table row, Phase D (`10_systems/DROPS.md`) |
| Real-money pack (live build only) | ≤ 10 / week / character | §6; the solo build has **no store** |

## 4. Pull resolution

One ticket → one server-side roll against the season-agnostic prize pool
(`50_content/gacha/capsule_pool.yaml`, schema `20_schemas/capsule_pool.schema.md`, Phase C).
Equipment prizes reuse the existing `pool_equip_rNN` roll of the character's current region band
(`10_systems/DROPS.md` mechanics, P4 — compose, don't enumerate) with rarity clamped to ≤
`rare`. Consumable and emberstone prizes are band-appropriate to the character's `level`
(same banding the charter lanes use); scroll prizes draw a `10_systems/SCROLLS.md` SKU whose
`slot_family` matches gear the character owns, tier-weighted per §5.

## 5. Odds & pity (first-pass numbers)

| Prize band | Odds | Contents |
|---|---|---|
| Consumable bundle | 55% | band tonics / foods / utility scrolls, small stacks |
| Emberstone cache | 20% | band emberstone (`item_etc_0193`–`0197`), 1–3 |
| Gear-modification scroll | 10% | one of `10_systems/SCROLLS.md`'s 18 SKUs (`item_use_0061`–`0078`), matched to the character's gear; `scroll_tier` weighted `steady` 60 / `bold` 30 / `perilous` 10 |
| Equipment roll | 12% | `pool_equip_rNN` at character band, rarity ≤ `rare` |
| **Capsule cosmetic** | 3% | one capsule-exclusive cosmetic (`item_cosmetic_0049`–`0064`) |

- **Pity:** a capsule cosmetic is guaranteed within **40 pulls** (the `capsule_pity`
  per-character counter, resets on any cosmetic hit). A capped buyer (§1.3) reaches pity in
  ≈ a month; a free gilt player (12 tickets/season) reaches it across seasons or by luck.
- Capsule cosmetics are the machine's identity: **exclusive cosmetics are allowed** (the
  power-parity rules of PA-001 and `10_systems/BATTLE_PASS.md` §5.2 govern stats, not looks).
  They are `10_systems/COSMETICS.md` unlock entries in any of its §2 categories, displayed
  through that doc's §5 appearance loadout — zero stats, character-bound, no vendor/trade
  value (COSMETICS §1). Duplicate cosmetic rolls re-roll once against the capsule list; a
  full-collection duplicate falls back to an emberstone cache.
- All numbers first-pass; retune at the D gate. The odds table as *displayed* must always match
  the served pool (a validation rule for `capsule_pool.schema.md`).

## 6. The real-money SKU (live build only)

- Packs: **1** ticket, **5** tickets, and **10+1** tickets (the sole bonus, §1.3) — subject to
  the 10-per-week purchase cap (bonus ticket included in the count).
- Real-currency pricing is a store/business decision, not a design number — owner sets it at
  live-ops launch (Open Questions). This doc fixes only the caps and pack shapes.
- The interim solo build ships **no store**: tickets come only from the charter and world drops,
  and the SKU/purchase-cap machinery is dormant behind the server boundary (§7).
- The Gilded Charter remains `shards`-purchased — real money never touches the battle pass
  (`10_systems/BATTLE_PASS.md` §1).

## 7. Economy & authority guardrails

- **Vendor value 0 on everything dispensed.** Prizes are marked non-vendorable at dispense time
  — this needs a per-instance `no_vendor` flag on inventory items
  (`10_systems/INVENTORY.md` / `20_schemas/item.schema.md`, Phase C addition — Open Questions).
  Combined with §1.5, the capsule adds **no `shards` faucet** (`10_systems/ECONOMY.md` §6).
- All capsule state is `authority: server` (`10_systems/PERSISTENCE.md` §2): pull rolls, pity
  counter, weekly purchase-cap counter, and SKU entitlements/receipts. The client never rolls a
  prize (PERSISTENCE §7's "no self-assigned drop" rule applies verbatim). Ticket counts live in
  ordinary server-authoritative inventory.
- Capsule state (pity, cap counters, receipts) is **excluded from the offline→online import**
  (PERSISTENCE §9), same stance as charter state.

## 8. Compliance (design obligations, not legal advice)

Real-money random rewards carry store and regulatory obligations the design must support:
odds disclosure in-UI before purchase and pull (§1.4 makes this structural), age-rating label
changes (in-game purchases + random items), and restricted markets where paid loot boxes are
limited or banned — the SKU must be regionally disableable, with the machine falling back to
earned-tickets-only mode (which the solo build already is). A proper legal/compliance review
before live-ops launch is flagged in Open Questions.

## Open Questions

- Real-currency pack pricing (§6) — owner decision at live-ops launch; design fixes caps/shapes
  only.
- The per-instance `no_vendor` flag (§7) does not yet exist in `20_schemas/item.schema.md` /
  `10_systems/INVENTORY.md` — owed at Phase C; cosmetics need no flag (they are non-item
  unlock entries, `10_systems/COSMETICS.md` §3) but item prizes — consumables, emberstones,
  scrolls, equip rolls — are ordinary inventory items and need the instance flag.
- Whether real-money ticket packs are direct-priced or priced in `gleam` once the
  MONETIZATION.md §4 store exists — open; either way the §1.3 weekly cap and §1.5 no-`shards`
  bridge bind.
- `15_maps_system/MAP_INTERACTABLES.md` needs a `capsule` interactable kind (§2) — flagged, not
  yet added there.
- The rare world-drop ticket rate (exact value inside the owner-set 6–8 h band) and its
  drop-table placement are Phase D work with `10_systems/DROPS.md`; unresolved whether it
  drops from all at-level normals or elites only (default: all at-level normals, very low
  rate).
- Whether the weekly purchase cap should be account-wide rather than per-character once
  accounts exist (PERSISTENCE §2's future account system) — default per-character now, revisit
  with the account design.
- Regional SKU disablement (§8) implies a server-side feature flag design that belongs to the
  future live-ops/server docs — flagged, not designed here.
- `20_schemas/capsule_pool.schema.md` (Phase C) and `50_content/gacha/capsule_pool.yaml`
  (Phase D) are owed; SCOPE totals updated.
