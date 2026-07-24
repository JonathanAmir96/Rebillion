# BATTLE_PASS.md — The Wayfarer's Charter (30-Day Seasonal Reward Ledger)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/QUESTS.md, 10_systems/LEVELING.md, 10_systems/ECONOMY.md, 10_systems/DROPS.md,
10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/INVENTORY.md, 10_systems/HUD.md,
10_systems/PERSISTENCE.md, 10_systems/COSMETICS.md, 10_systems/MONETIZATION.md,
10_systems/GACHAPON.md, 10_systems/social/RAID.md, 15_maps_system/MAP_CONNECTIONS.md,
docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

Owner doc for the **battle-pass system**, in-world the **Wayfarer's Charter**: a 30-day seasonal
ledger of tasks and rewards issued by the **Millbrook Charterhouse**. Two reward lanes — the free
**Wayfarer's lane** (`charter_free`) and the **Gilded lane** (`charter_gilt`), unlocked for a
`shards` fee — progress together through 30 charter levels earned by playing. This doc owns the
season lifecycle, `charter_mark` progression math, task anatomy, reward-lane budget rules, and
the no-power / no-faucet guardrails. The gilt price *number* is `10_systems/ECONOMY.md` §4.4;
task steps reuse `10_systems/QUESTS.md` §3's step grammar (P4 — compose, don't enumerate);
authority is `10_systems/PERSISTENCE.md`'s; season IDs are `docs/ID_REGISTRY.md`'s.

## 1. Pillar contract (read first)

The battle-pass genre pattern is usually a monetization device; Rebillion's is deliberately not:

- **No real money in the charter.** The Gilded lane is bought with `shards`, **earned in-world
  only** (`00_vision/PILLARS.md` anti-pillars). "Paid" here means paid the way the coach and
  the Harborwind Ferry are paid (`15_maps_system/MAP_CONNECTIONS.md`): a `shards` sink,
  recorded in `10_systems/ECONOMY.md` §2. The game's single real-money product is the Cogwork
  Capsule ticket SKU (pillar amendment PA-001, `10_systems/GACHAPON.md`) — it never touches
  the charter: gilt is `shards`-purchased permanently.
- **No exclusive power.** Every stat-bearing item in either lane must be obtainable in ordinary
  play (existing tonics, emberstone tiers, drop-pool equipment). Gilt-lane exclusives are
  **cosmetics only** — zero stats, per `10_systems/COSMETICS.md` §1's laws (§5).
- **No purchasable progress.** Charter levels and `charter_mark`s can never be bought, with
  `shards` or anything else. The gilt fee unlocks a reward *lane*, never progress. The fee is
  **bracketed by the buyer's `level` band** (`10_systems/ECONOMY.md` §4.4) so it stays a real
  slice of playtime at every level instead of decaying into nothing; the bracket sets the
  **price only** — the gilt lane's contents are identical in every bracket, so paying a higher
  bracket never buys more (§5).
- **No `shards` faucet.** Neither lane ever rewards `shards`, and reward-lane vendor value is
  budget-capped (§5.3), preserving `10_systems/ECONOMY.md` §1's "no other faucet exists."
- **Cozy, not FOMO** (P2). All dailies alone — ≈ 15–20 minutes a day — complete the charter with
  two days to spare; weekly trials never expire once unlocked; completing ≈ ⅔ of everything on
  offer finishes the pass (§3).

## 2. Season lifecycle

- A **season** is exactly **30 days**, IDs `season_001`–`season_050` (`docs/ID_REGISTRY.md`),
  minted chronologically. Seasons run back-to-back with no gap; day boundaries are the **daily
  reset** at midnight UTC (server clock once live).
- Season definitions are content files (`50_content/seasons/season_NNN.yaml`, Phase D) conforming
  to `20_schemas/season.schema.md` (Phase C): values and references only — task lists, mark
  values, and reward lanes; every rule lives here.
- **Interim solo build:** the season calendar is per-install — `season_001` day 1 is the install's
  first launch date, day boundaries at local midnight. Charter progress, gilt purchase, and claims
  are **per character** (matching the per-character wallet,
  `10_systems/PERSISTENCE.md` Open Questions). Local-clock tampering is accepted in solo like any
  local save; charter state is excluded from the future offline→online import (§7).

## 3. Progression — `charter_mark`s and charter levels

- **30 charter levels** per season, a flat **70 `charter_mark`s per level** (2,100 total). Both
  lanes advance from the same level track; marks past level 30 are discarded (Open Questions).
- Marks come **only** from charter tasks — no passive trickle from kills or `exp`, so the ledger
  stays legible (P2) and never double-dips the `10_systems/DROPS.md` faucet.

| Source | Cadence | Marks | Season max |
|---|---|---|---|
| **Daily stamps** | 3 per day, expire at daily reset | 25 each (75/day) | 2,250 |
| **Weekly trials** | 3 unlock on days 1 / 8 / 15 / 22; never expire once unlocked | 70 each | 840 |
| | | **Attainable** | **3,090** |

Pacing (against 2,100 needed): all-dailies-only finishes on **day 28** exactly; dailies +
prompt weeklies finish around **day 20**; overall ≈ **68%** of attainable marks completes the
charter. Days 29–30 mint no new weeklies — they are catch-up grace. Each daily stamp is sized to
≤ 5–7 minutes of at-level play, so one 20-minute session clears all three (P2).

## 4. Task anatomy — quests' step grammar, reused

A charter task is **one step object** from `10_systems/QUESTS.md` §3 (`kill` / `collect` /
`talk` / `reach`) plus a mark value — no new step types, no new credit rules (kill credit is
`10_systems/DROPS.md` §7; collect sourcing is QUESTS §3.1). This is the daily/weekly system
QUESTS §7's Open Question anticipated: a new system referencing quest anatomy, changing nothing
in it. Quests themselves stay one-time; charter tasks live on the charter panel (§8), never in
the quest log.

- Tasks are **world-generic**, not region-scripted: targets are tier/band-scoped ("30 at-level
  `normal` kills", "defeat 1 at-level `elite`", "ride a `coach` or the ferry", "turn in any
  quest", "collect 15 at-level `item_etc` materials"), so any at-level character can clear them
  where they already play. The at-level window definition is owned by `10_systems/LEVELING.md`
  (Open Questions — not yet formalized there).
- Each season file authors a **daily pool** (~10 task templates) and a **weekly list** (12
  trials). The day's 3 stamps are drawn from the pool by deterministic rotation
  (`(day_index · 3 + slot) mod pool_size`) — no RNG, no reroll mechanic. Weekly trials are
  bigger, at most one per week keyed to group content (a raid clear — any token on
  `10_systems/social/RAID.md` §2's roster) and
  always with a solo-viable alternative in the same week (server-deferred group content must
  never gate the charter; `00_vision/SCOPE.md`).
- Task progress follows quest-step completion criteria exactly and is server-authoritative (§7).

## 5. Reward lanes

Every one of the 30 levels carries a **free-lane** reward; a gilt character claims the **gilt
lane** at the same levels in addition — the gilt lane is a second lane, never a multiplier.
A reward entry is `item_id × qty` or a `choice` of up to 3 such lines (pick one at claim), so a
lane can offer the band-appropriate tonic without scaling items (P4).

### 5.1 What lanes may contain

| Category | Free lane | Gilt lane |
|---|---|---|
| Consumables (tonics, cleanses, scrolls, foods — `item_use`) | yes | yes, larger qty |
| Emberstones (`item_etc_0193`–`0197`, band per `10_systems/ENHANCEMENT.md`) | yes, modest | yes, more |
| Drop-pool equipment (a `pool_equip_rNN` roll, rarity ≤ `rare`) | sparingly | sparingly |
| Capsule tickets (`item_use_0021`, `10_systems/GACHAPON.md` §3) | 4 / season | +8 / season |
| **Charter cosmetics** (`item_cosmetic_0033`–`0048`, the Event/charter sub-block) | level-30 capstone | **featured**: pieces across the lane + gilt capstone |

**Cosmetics are the gilt lane's headline offer** (owner decision 2026-07-24). Each season mints
**up to 6 `item_cosmetic` IDs** from the Event/charter sub-block (`docs/ID_REGISTRY.md`): 1
free-lane level-30 capstone and up to 5 gilt-lane pieces spaced through the lane (suggested
levels 5 / 12 / 20 / 26, gilt capstone at 30) — so a gilt character sees a cosmetic on the
horizon all month, not only at the end. Charter cosmetics are `10_systems/COSMETICS.md`
unlock entries in any of its §2 categories (`skin` / `dye` / `title`), displayed through that
doc's §5 appearance loadout — zero stats, character-bound, no vendor/trade value, no
inventory slot; COSMETICS.md §1's laws apply verbatim.

### 5.2 Power parity rule

Nothing stat-bearing may be gilt-exclusive or charter-exclusive: consumables, emberstones, and
equipment in the lanes must all be obtainable through ordinary play at comparable effort. The
gilt lane buys *more convenience*, never *only-here power*. A season file violating this fails
review (VALIDATION.md check via `20_schemas/season.schema.md`, Phase C).

### 5.3 Faucet guardrail (vendor-value budget)

Charter item rewards (consumables, emberstones, equip rolls) are ordinary items and vendor
normally — so the lanes are budget-capped: the **total vendor value of a season's two full
lanes must stay ≤ 1,500 `shards`** (≈ 4 minutes of Lv 30 income, `10_systems/ECONOMY.md` §5).
Charter cosmetics and capsule tickets carry no vendor value at all. The charter therefore
adds no meaningful `shards` faucet (`10_systems/ECONOMY.md` §1/§6).

### 5.4 Claiming

Rewards are claimed manually from the charter panel (§8), any time during the season. At season
end, earned-but-unclaimed rewards **auto-claim on next login**; inventory overflow handling is
open (Open Questions — default: a 7-day claim queue on the panel into the next season). Nothing
earned is ever forfeited (P2).

## 6. The gilt unlock

- Purchased any time during a season from the **Charterhouse clerk** in Millbrook (an ordinary
  town NPC; ID minted in Phase D from the Millbrook or reserved `npc` block) for a `shards` fee
  **bracketed by the character's `level` band** — the bracket table, its derivation, and the
  charge rule are `10_systems/ECONOMY.md` §4.4's (owner directive 2026-07-24; never restated here).
  The clerk quotes the character's current bracket; the fee is charged once, at purchase, and is
  never re-assessed if the character levels into a higher bracket later in the season.
- Purchase is retroactive: all gilt-lane rewards up to the character's current charter level
  become claimable immediately.
- Per character, per season; it never carries into the next season. There is no gilt-lane
  "level skip," gift, or bundle — the fee is the entire transaction (§1).

## 7. Authority & persistence

All charter state — season index and day, task progress, `charter_mark` balance, charter level,
track (`charter_free`/`charter_gilt`), claimed-reward set — is `authority: server`
(`10_systems/PERSISTENCE.md` §2). The client may never self-grant a mark, level, claim, or the
gilt flag; the solo build enforces the same boundary through the `GameState` facade
(PERSISTENCE §5/§7). Charter state is **excluded from the offline→online import**
(PERSISTENCE §9): live seasons start fresh, so a hand-edited solo save cannot inject season
rewards into the live game — items already claimed in solo remain subject to that import's own
item validation, not this doc's.

## 8. UI hook

The charter panel is a framed window opened from the town/menu bar: current level and mark
progress, today's 3 stamps with per-step counters, this season's weekly trials, both reward
lanes with claim buttons, days remaining, and the gilt unlock. Frame/placement mapping belongs
to `10_systems/HUD.md`'s frame-usage table (flagged there via Open Questions); daily stamps are
deliberately **not** shown in the quest log or compact tracker (`10_systems/QUESTS.md` §8) at
launch.

## Open Questions

- ~~**Owner check — "paid" interpretation.** The owner requested a free + paid pass; per the
  anti-pillars and `00_vision/SCOPE.md` (no monetization) this doc reads "paid" as
  `shards`-purchased.~~ **Resolved 2026-07-24 (owner):** feature approved as designed —
  `shards`-purchased gilt lane, with **cosmetics as the premium offer** (§5.1). No pillar
  amendment needed.
- ~~Vanity pieces occupy real equipment slots, so wearing one forgoes a stat-bearing
  `cape`/`head`.~~ **Resolved at the v3 merge (2026-07-24):** the appearance layer landed
  (`10_systems/COSMETICS.md` §5); charter cosmetics are unlock entries displayed there,
  occupying no equipment slot and visible during combat.
- The "at-level window" used by task scoping (§4) is not formally defined in
  `10_systems/LEVELING.md`; that doc should own it (suggested: the same window that grants full
  `exp`). Flagged there in spirit — resolve at the next gate.
- All numbers (70 marks/level, 25/70 mark values, 3+3 task cadence, the 1,500-`shards` vendor
  budget) are first-pass; retune at the D gate alongside the economy pass.
- ~~The gilt fee (`10_systems/ECONOMY.md` §4.4) is not merely first-pass but structurally
  load-bearing: at a flat price it is ≈ 1.3% of a month's net income by Lv 50, which makes §5's
  free/gilt split a formality while still costing a `charter_gilt` token, retroactive-purchase
  rules, §5.2's parity clause, per-character season state, and claim UI.~~ **Resolved 2026-07-24
  (owner directive, "fee like maple story … when amount increase the tax increased"):** the fee is
  now **progressive by `level` band** — a rising share of a season's modeled income, so the split
  is a real monthly decision at every band and the sink obeys ECONOMY §6's "sinks scale with level"
  guardrail. §1 and §6 cite the rule; ECONOMY §4.4 owns every number, and the share ladder itself
  stays open there pending the D-gate balance pass. Note for §5.1/`season_001` authoring: the
  gilt lane is now a **priced choice at every band**, so its contents must justify the bracket fee
  the buyer actually pays — the §5.2 parity rule is what keeps that from becoming power.
- Season-end overflow (§5.4): claim-queue default is unconfirmed; interacts with
  `10_systems/INVENTORY.md` slot caps.
- Marks past level 30 are discarded (§3); a post-30 repeat crate was considered and deferred
  (mirrors `10_systems/LEVELING.md` §6's cap-`exp` stance).
- Whether the solo build's per-install season calendar should instead be per-character (slot
  created mid-season starts its own day 1?) — default is per-install as written (§2).
- `20_schemas/season.schema.md` and the `50_content/seasons/` exemplar (`season_001`) are Phase
  C/D deliverables, not yet authored; SCOPE.md totals updated to include them.
- HUD.md needs a charter-panel row in its frame-usage mapping (§8) — flagged, not yet added
  there.
