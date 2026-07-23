# TRADING.md — Direct Player Trade

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/JOBS.md, 10_systems/ITEMS.md,
10_systems/INVENTORY.md, 10_systems/ECONOMY.md, 10_systems/ENHANCEMENT.md, 10_systems/QUESTS.md,
10_systems/COMBAT_FORMULA.md, 10_systems/SKILL_SYSTEM.md, 10_systems/social/CHAT.md,
10_systems/social/MARKET.md, 10_systems/PERSISTENCE.md, docs/ID_REGISTRY.md

Owner doc for **direct player-to-player trade**: the invite/accept handshake, the dual-confirm
escrow that swaps two offers atomically, what may and may not be offered, and the guards against
scams and abuse. Trading is a synchronous, face-to-face exchange between two present characters —
it is not the future asynchronous listings board (`10_systems/social/MARKET.md`), which has no
live handshake and its own escrow shape. Item categories and `rarity` are `10_systems/ITEMS.md`;
carried inventory and the `shards` wallet are `10_systems/INVENTORY.md`; `shards` faucets/sinks are
`10_systems/ECONOMY.md`. This doc owns only the trade session itself and never restates those.

## 1. Requirements to open a trade

Both characters must satisfy every row below the instant the trade window opens, and the session
auto-cancels the moment any of them stops holding (§3):

| Requirement | Value | Rationale |
|---|---|---|
| Character `level` | both ≥ **Lv 8** | The 1st job advancement (`10_systems/JOBS.md` §1) — a novice has cleared the tutorial band (`00_vision/PILLARS.md` P2) before handling player exchanges. |
| Same map | both on the same `map_NNN` | No cross-map trading; keeps the exchange face-to-face. |
| Proximity | within **4 tiles** | Placeholder tile count pending the px scale lock (`40_assets/ART_BIBLE.yaml`), the same open item as `10_systems/COMBAT_FORMULA.md` §10 / `10_systems/SKILL_SYSTEM.md` §6. |
| Session state | neither already in an active trade | One trade session per character at a time (§5). |

## 2. Invite / accept flow

1. **Invite** — Player A targets Player B (in-world target, or a roster/whisper entry per
   `10_systems/social/CHAT.md`) and sends a trade request. Requires §1 at send time.
2. **Accept / decline** — B sees an accept/decline prompt. Declining, or a **30 s** timeout,
   cancels the request with no state change on either side.
3. **Window opens** — on accept, both clients open a paired trade window; §1 is re-validated at
   this instant and continuously afterward (§3).

## 3. The escrow session — offer, lock, confirm, atomic swap

Each side builds its own offer independently and privately:

| Field | Limit |
|---|---|
| Item slots | 8 (subject to §4 tradeability and the recipient's `10_systems/INVENTORY.md` tab having room) |
| `shards` | 0 up to the offering character's full wallet; a swap that would push the receiving wallet over the `10_systems/INVENTORY.md` §3 cap is rejected before it executes, never silently truncated |

State machine (both sides progress independently until the final step):

| Step | Action | Effect |
|---|---|---|
| Offer | either side adds/removes items or sets a `shards` amount | freely editable |
| **Lock** | a side clicks Lock | that side's offer is frozen; unlocking to edit again clears **both** sides' Confirm (the scam guard, §5) |
| **Confirm** | once **both** sides are locked | a Confirm control appears for both; each must explicitly confirm |
| **Swap** | the instant both Confirms land | the server executes one atomic transfer — both offers change hands together or neither does; no partial state is ever visible to either client |
| Cancel | either side, any time before Swap | session closes; every item/`shards` amount stays exactly where it was — nothing is transferred pre-swap |

An idle session (no Lock/Confirm/Cancel from either side) auto-cancels after **120 s**, returning
both sides to their normal inventory state untouched.

## 4. What can be offered — untradeable policy

**Decision: boss uniques are tradeable; quest items are never tradeable.**

| Category | Tradeable? |
|---|---|
| Boss unique equipment (`item_equip_0201`–`0230`, `10_systems/ITEMS.md` §11) | **Yes** — no special-case removal; enhancement level and affixes travel with the item (Open Questions). |
| A one-off `item_etc` minted solely for a quest's `collect` step (`10_systems/QUESTS.md` §3.1, first bullet) | **No** — hardcoded, never offerable, regardless of any other flag. |
| An ordinary shared regional material a quest also targets (`10_systems/QUESTS.md` §3.1, first bullet) | Tradeable — it is an ordinary `etc` item with independent vendor/trade value; a quest wanting some of it does not revoke that (`10_systems/QUESTS.md` §3.1 already confirms non-questers loot/use the same material normally). |
| Other ordinary `equip`/`use`/`etc` items | Tradeable by default. |
| `shards` | Always tradeable, subject to the receiving wallet cap (§3). |

The concrete `tradeable`/`untradeable` field belongs on the item schema (Phase C,
`20_schemas/item.schema.md`, authored, but does not yet define this field) — this doc fixes the
**policy** the field must encode, not the field itself (Open Questions).

## 5. Scam guards & rate limits

- **Re-confirm on change** — any edit to a locked offer (via unlock) clears both sides' Confirm
  state (§3). This is the core defense against a last-second bait-and-switch: nobody can confirm
  against an offer that has since changed.
- **Trade log** — every completed trade is written to a server-side log (both character IDs, full
  offer contents, timestamp) for anti-fraud review; a short recent-trades list is player-visible
  client-side.
- **Session exclusivity** — one active trade session per character (§1); a second invite sent or
  received while already in a session is refused.
- **Cooldown** — a **5 s** cooldown after any trade closes (completed or canceled) before that
  character may open another.
- **Volume ceiling** — a first-pass soft cap of **20 completed trades/hour** per character, an
  anti-bot/anti-farming ceiling pending real economy telemetry (Open Questions).

## Server Dependency

An atomic two-sided swap needs a single transaction authority both clients trust — a peer client
cannot safely execute its own half and assume the other side honored theirs. Every field a trade
session touches (both offers, lock/confirm state, the swap, the trade log) is `authority: server`
(`10_systems/PERSISTENCE.md` §1–§2; `00_vision/PILLARS.md` P6). **The interim solo build ships the
entire trade system present but dormant**: the invite/offer/escrow UI exists in the client but
there is no second character ever present to trade with, so no session ever opens.

## Open Questions

- Level floor (Lv 8), proximity (4 tiles), offer slot count (8), and every timeout/rate-limit
  number in §3/§5 are first-pass; retune once live-server telemetry exists. Owner: this doc with
  `10_systems/ECONOMY.md`.
- The `tradeable`/`untradeable` field's exact name/type has no schema home yet (§4); proposed for
  `20_schemas/item.schema.md` at Phase C.
- Phase D needs a concrete way to mark a one-off quest-minted `etc` item as untradeable (§4) — no
  ID sub-range distinguishes it from an ordinary regional material (`docs/ID_REGISTRY.md`,
  `10_systems/QUESTS.md` §3.1); it must be a per-item authoring flag, not an ID-range rule.
- Whether enhancement level and soft-pity counters (`10_systems/ENHANCEMENT.md`) travel with a
  traded item is assumed **yes** (persisted item state) but not explicitly confirmed by that doc.
- Whether a per-trade `shards` ceiling beyond the receiving wallet cap is needed as an extra
  anti-laundering guard is open; default relies on the wallet cap alone.
- Trade log retention length and any further player-facing exposure beyond a short recent-history
  list is a live-ops / `10_systems/PERSISTENCE.md` policy call, not fixed here.
- Neither `10_systems/HUD.md`'s frame-variant table nor `10_systems/CONTROLS.md`'s input map yet
  assigns a frame type or an open-trade trigger/keybind — flagged for those docs, not designed
  here.
