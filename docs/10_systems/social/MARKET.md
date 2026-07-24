# MARKET.md — Asynchronous Player Market (Stub)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/social/TRADING.md,
10_systems/social/MAIL.md, 10_systems/ECONOMY.md, 10_systems/INVENTORY.md, 10_systems/ITEMS.md,
10_systems/PERSISTENCE.md

**Purpose.** A searchable listings board where a seller posts an item for a `shards` asking price
and any player may buy it without both being online together — the asynchronous counterpart to
`10_systems/social/TRADING.md`'s live exchange.

## Planned scope
- **List**: seller picks an item + `qty`, sets `ask_price` in `shards`, pays a listing fee
  (`10_systems/ECONOMY.md` "Market transaction fee," a % of sale, not fixed here).
- **Escrow**: a listed item leaves `10_systems/INVENTORY.md` immediately and is server-held until
  sold or delisted — the same "item never lost" spirit as `10_systems/social/TRADING.md`'s swap.
- **Search/browse**: filter by category/slot/tier/`rarity` (`10_systems/ITEMS.md` tokens) and
  price.
- **Buy**: buyer pays `ask_price`; item transfers; proceeds (minus fee) reach the seller.
- **Delist**: seller cancels an unsold listing any time; item returns to inventory.
- Reuses `10_systems/social/TRADING.md`'s untradeable policy: quest items never list; capsule
  prizes and capsule tickets never list (bound on dispense, `10_systems/GACHAPON.md` §7 — this
  is what keeps real money from reaching `shards` by listing, GACHAPON §1.5); boss uniques can.

## Dependencies
Untradeable policy is `10_systems/social/TRADING.md`'s; fees/price bands are
`10_systems/ECONOMY.md`'s; escrow/proceeds obey `10_systems/INVENTORY.md`; listings are stored by
`10_systems/PERSISTENCE.md`; proceeds may route through `10_systems/social/MAIL.md` (flagged,
unresolved).

## Reserved vocabulary
None; `ask_price`/`listing_fee` are field names, not shared enums.

## Data sketch
```yaml
listing_id: <server-assigned>
seller: player_ref
item_ref: item_equip_0207
qty: 1
ask_price: 50000           # shards
listing_fee_paid: 1000     # shards, rate owned by 10_systems/ECONOMY.md
listed_ts: <server timestamp>
expires_ts: <server timestamp>
status: active               # active | sold | expired | canceled
```

## Server Dependency
A shared listings board is server-hosted state visible to every player (`authority: server`,
`10_systems/PERSISTENCE.md` §1–§2). **The interim solo build ships the market UI dormant**: the
browse screen renders empty and listing is disabled (nothing to sell to).

## Open Questions
- Listing fee rate, duration, and max concurrent listings per character are unset — owner
  `10_systems/ECONOMY.md` jointly with this doc.
- Whether `legendary`/boss-unique listings need a price floor/ceiling is flagged for
  `10_systems/ECONOMY.md`.
- Proceeds delivery (wallet credit vs `10_systems/social/MAIL.md`) is undecided.
