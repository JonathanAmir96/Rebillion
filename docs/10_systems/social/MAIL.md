# MAIL.md — Asynchronous Mail, Attachments & COD (Stub)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/social/TRADING.md,
10_systems/social/MARKET.md, 10_systems/ECONOMY.md, 10_systems/INVENTORY.md,
10_systems/PERSISTENCE.md

**Purpose.** Store-and-forward messages between players who are not online together: a text body
plus an optional item and/or `shards` attachment, with cash-on-delivery (COD) so a sender can
demand payment before the recipient claims it. Exists so trading
(`10_systems/social/TRADING.md`) is not the only transfer path across sessions.

## Planned scope
- Compose: recipient, subject, body, optional single item attachment, optional `shards`, optional
  `cod_amount` (a `shards` sum the recipient must pay to release the attachment; 0 = free).
- Send costs a flat `shards` fee (`10_systems/ECONOMY.md` sink, amount not fixed here).
- Mailbox has a capacity cap; unclaimed mail expires after N days and returns any attachment to
  the sender untouched (never destroyed, `00_vision/PILLARS.md` P2).
- Claim is a discrete action, not proximity auto-loot (`10_systems/INVENTORY.md` §4) — needs
  inventory room and, if `cod_amount` > 0, the `shards` to pay it.
- Defers to `10_systems/social/TRADING.md` §4's untradeable policy (quest items never attach;
  boss uniques can).

## Dependencies
Tradeability rules are `10_systems/social/TRADING.md`'s; send/COD flow and fees are
`10_systems/ECONOMY.md`'s; claim obeys `10_systems/INVENTORY.md`'s carry/wallet rules; storage is
`10_systems/PERSISTENCE.md`'s; sale proceeds may route here from `10_systems/social/MARKET.md`
(flagged, unresolved).

## Reserved vocabulary
None; `cod_amount` is a field name, not a shared enum.

## Data sketch
```yaml
mail_id: <server-assigned>
sender: player_ref
recipient: player_ref
subject: "..."
body: "..."
attachment: { item_ref: item_equip_0207, qty: 1 }   # optional, single item
shards_attached: 0
cod_amount: 0              # shards recipient must pay to claim the attachment
sent_ts: <server timestamp>
expires_ts: <server timestamp>
```

## Server Dependency
Mail is an asynchronous mailbox held server-side by definition (`authority: server`,
`10_systems/PERSISTENCE.md` §1–§2). **The interim solo build ships mail dormant**: compose UI may
exist but has no valid recipient, since no other character exists to receive it.

## Open Questions
- Send fee, mailbox capacity, and expiry window are unset — owner `10_systems/ECONOMY.md` jointly
  with this doc.
- Whether an attachment may ever hold more than one item/stack is undecided; default is one.
- Whether `10_systems/social/MARKET.md` proceeds deliver via mail is flagged in both stubs, not
  resolved.
- No HUD frame or keybind is reserved yet for a mailbox panel.
