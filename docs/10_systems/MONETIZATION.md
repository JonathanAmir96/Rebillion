# MONETIZATION.md — Cosmetic-Only Monetization Direction (MON-001)

References: 00_vision/PILLARS.md, 00_vision/SCOPE.md, 00_vision/GLOSSARY.md,
10_systems/ECONOMY.md, 10_systems/ITEMS.md, 10_systems/INVENTORY.md, 10_systems/PERSISTENCE.md,
15_maps_system/MAP_INTERACTABLES.md, 15_maps_system/MAPS_SYSTEM.md, 40_assets/ART_BIBLE.yaml,
docs/WORLD_PLAN.md

**Status: direction-only, server-deferred.** Fixed by owner amendment **MON-001**
(2026-07-23), which also amends `00_vision/PILLARS.md` (anti-pillars) and `00_vision/SCOPE.md`
(out-of-scope wording). This run authors **no** store content, no premium items, no store UI,
and no schema fields — everything here waits for a live-service arc with real servers
(`10_systems/PERSISTENCE.md`). The doc exists so every other system reserves the right seams
now instead of retrofitting them later.

## 1. Owner intent

Community health outranks revenue. The game's draw is the social, cozy-grind loop
(`00_vision/PILLARS.md` P2/P6); pay-to-win would trade that away for short-term income and is
rejected outright. Monetization is therefore **cosmetic-only**, plus in-world sponsor/supporter
placements that live inside the fiction of the world.

## 2. The no-pay-to-win charter (hard rules)

Every future store decision is validated against these five rules; a purchase that fails any
one of them is out, regardless of revenue.

1. **No purchased power.** Nothing bought with real money may carry or modify any
   GLOSSARY stat (primary, derived, or otherwise), damage, defense, or combat behavior.
   Premium goods are purely presentational — `client`-authority fields only, per
   `10_systems/PERSISTENCE.md` tagging.
2. **No market laundering.** Premium goods are account-bound: never tradable, never listable
   on the market (`10_systems/social/MARKET.md`). There is no real-money → `shards` path.
3. **No grind shortcuts.** No `exp` boosts, drop-rate boosts, or inventory/storage expansions
   for real money. Default: excluded entirely (Open Questions).
4. **No paid randomness.** No gacha/loot-box mechanics for real money; every premium item is a
   direct, priced purchase.
5. **Currency separation.** `shards` remain earned in-world only (`10_systems/ECONOMY.md`);
   the premium currency (`gleam`, provisional — §4) never converts to or from `shards` in
   either direction.

## 3. Revenue streams (direction)

### 3.1 Cosmetic layer

A separate **appearance layer** of zero-stat cosmetic slots rendered above the equipment
slots (`10_systems/ITEMS.md` equipment-slot tokens). Wearing a cosmetic changes look only;
the equipped gear keeps supplying all stats. Ownership is server-authoritative; rendering is
`client`. The slot list is **not** designed here — it landed (2026-07-24) in
`10_systems/COSMETICS.md` §5, the owner doc for the earned cosmetic system; a future premium
store sells into that same layer under this doc's charter, minting its own reserved ID block
(never `10_systems/COSMETICS.md`'s earned blocks). The paper-doll layer ordering must still be
settled before the Phase E coding pass fixes the character render pipeline.

### 3.2 Sponsor & supporter billboards

Town maps (`map_type: town`, starting with the Millbrook hub — `docs/WORLD_PLAN.md`) reserve
in-world **billboard** placements: a future interactable type to be added by amendment to
`15_maps_system/MAP_INTERACTABLES.md`. Two tenancy modes:

- **`shards` rental (in-game, not revenue).** Players and guilds rent a billboard to show a
  guild crest or message. This is a social feature and a `shards` **sink** — the fee lands as
  a `10_systems/ECONOMY.md` §2 row in a future amendment (flagged there).
- **Real-money sponsor/supporter placements.** A paying supporter or sponsor gets a billboard
  slot in a main town. All creatives are produced **in-world**: pixel art conforming to
  `40_assets/ART_BIBLE.yaml` (palette, resolution, tone), themed to the world's fiction. No
  external ad-network integration, no programmatic banners, no off-tone brand assets —
  rejected both for identity (P7) and because programmatic in-game ad revenue is negligible
  below very large player counts.

### 3.3 Explicitly rejected

Pay-to-win of any kind (§2) · programmatic/ad-network in-game advertising (§3.2) ·
subscriptions that gate content or power · paid convenience (repair fees, energy systems,
revive tokens) · durability systems introduced as a monetization hook
(`10_systems/DEATH_PENALTY.md` already rejects durability outright).

## 4. Premium currency (provisional)

`gleam` — proposed Provisional GLOSSARY token (pending promotion at a phase gate). Bought
with real money only; spends only in the cosmetic/supporter store; account-bound; never
trades, never converts to `shards` (§2.5). Semantics beyond this paragraph (denominations,
pricing) are deferred to the live-service arc.

## 5. Server authority

All premium entitlements (owned cosmetics, active billboard tenancies, `gleam` balances) are
server-authoritative (`10_systems/PERSISTENCE.md`); the client renders entitlements it is
told about and asserts nothing. The solo interim build ships **none** of this.

## Open Questions

- `gleam` token name is Provisional (GLOSSARY) — promote or rename at the next phase gate.
- ~~Exact cosmetic slot list~~ **resolved 2026-07-24:** the slot list is owned by
  `10_systems/COSMETICS.md` §5 (title / weapon skin / outfit skin / dye / crest flourish).
  Still open: the paper-doll layer *order*, which must land before Phase E fixes the character
  render stack — owner: `10_systems/COSMETICS.md` with the render-stack pass.
- Are any convenience purchases (e.g., cosmetic-adjacent quality-of-life like extra character
  slots) acceptable under the charter? Default: character slots yes (no in-world power),
  everything touching `exp`/drops/inventory no (§2.3).
- Billboard interactable shape, placement budget per town, and `shards` rental fee — owners:
  `15_maps_system/MAP_INTERACTABLES.md` + `10_systems/ECONOMY.md`, at the arc where servers
  land.
- Store pricing, regional pricing, and refunds — deferred to the live-service arc; not a
  design-tree concern yet.
