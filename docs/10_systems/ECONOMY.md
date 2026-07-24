# ECONOMY.md — Shard Faucets, Sinks, Prices & Fees

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/DROPS.md,
10_systems/LEVELING.md, 10_systems/INVENTORY.md, 10_systems/DEATH_PENALTY.md,
10_systems/QUESTS.md, 10_systems/social/PARTY.md, 10_systems/social/GUILD.md,
10_systems/social/MARKET.md, 10_systems/PERSISTENCE.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the `shards` economy: every faucet, every sink, the vendor price bands, and the
scaling fees (enhancement, stat reallocation). `shards` are the single currency (GLOSSARY),
**earned in-world only** (`00_vision/PILLARS.md` anti-pillars; no pay-style design). Where drops
produce `shards` is `10_systems/DROPS.md` (§3, the faucet numbers); this doc consumes that faucet
and balances it against sinks. Item stat values are `10_systems/ITEMS.md`; enhancement mechanics
are `10_systems/ENHANCEMENT.md` (this doc owns only its **fee**). All balances are
server-authoritative (`10_systems/PERSISTENCE.md`).

## 1. Faucets (where `shards` enter)

| Faucet | Source of number | Notes |
|---|---|---|
| Monster drops | `10_systems/DROPS.md` §3 | **Primary faucet.** ≈ `480 · mean_shards_normal(L)` per hour at-level (§5). |
| Quest rewards | `10_systems/QUESTS.md` (cites this doc) | Per-quest `shards` budgeted against the region band; a supplementary faucet, not the main one. |
| Vendoring | §4 (this doc) | Selling drops/junk at 25% of buy value; a steady secondary faucet. |

No other faucet exists. Defeat does **not** grant or remove `shards`
(`10_systems/DEATH_PENALTY.md` §3). Starting `shards` for a new character: **50** (enough for a
handful of Lesser tonics; §4).

## 2. Sinks (where `shards` leave)

| Sink | Owner of the number | Scales with |
|---|---|---|
| Consumables (tonics/cleanses/scrolls/foods) | §4 (this doc) | level band (§4) |
| Travel (Harborwind Ferry + Harthmoor Coachworks fares) | §7 (this doc) | ring distance |
| Enhancement fee | §3 (this doc) | gear tier × target `+` |
| Stat free-point reallocation | §3.1 (this doc) | `level` |
| Gilded Charter unlock (seasonal battle pass) | §4.3 (this doc) | flat, per 30-day season |
| Guild creation | `10_systems/social/GUILD.md` (fee reserved here) | flat, endgame |
| Market transaction fee | `10_systems/social/MARKET.md` (future) | % of sale |
| **Repairs** | — | **none: no durability system exists** |

**No repair sink.** There is no item durability anywhere in this tree — equipment never degrades,
breaks, or needs repair. This is owned and justified by `10_systems/DEATH_PENALTY.md` §3
(rejected to avoid a wear field on every item and a pay-style repair loop); this doc merely records
that the death/economy consequence is **no repair `shards` sink**. Skill-point respec is **free**
(`10_systems/JOBS.md` §6 / `10_systems/SKILL_SYSTEM.md`); only **stat** free-point reallocation
carries a fee (§3.1). Resting at an inn to rebind (`10_systems/DEATH_PENALTY.md` §4) is **free** at
launch (resolving that doc's rebind-cost OQ from the economy side; a fee may be added later if
bind-hopping is abused).

## 3. Enhancement fee schedule (cited by `10_systems/ENHANCEMENT.md` §5)

One `shards` fee per enhancement attempt (paid on success **and** failure). Rises with gear tier
and target `+` so the high-`+`/high-tier band is the endgame's main `shards` sink:

```
fee(T, n) = round( base_fee(T) · plus_mult(n) )      # n = target enhancement level 1..9
base_fee(T) = round( 3 · mean_shards_normal(T.req_level) )   # DROPS §3
plus_mult(n) = 1 + 0.5·(n - 1)                        # +1 → ×1.0 … +9 → ×5.0
```

Tier `req_level`s follow `10_systems/ITEMS.md` §4's v3 twelve-tier ladder (T1–T6 arc 1, T7–T12
arc 2); sampled rows below, intermediate tiers computed from the same formula.

| Tier (`req_level`) | `base_fee` | fee @ +1 | @ +5 | @ +9 |
|---|---|---|---|---|
| T1 (1) | 15 | 15 | 45 | 75 |
| T3 (15) | 78 | 78 | 234 | 390 |
| T5 (29) | 141 | 141 | 423 | 705 |
| T6 (36) | 171 | 171 | 513 | 855 |
| T8 (50) | 234 | 234 | 702 | 1,170 |
| T10 (64) | 297 | 297 | 891 | 1,485 |
| T12 (78) | 360 | 360 | 1,080 | 1,800 |

Worked: taking one T6 item 0→+9 (guaranteed +1..+5, then the §3-pity risky band, expected ≈ 13
attempts total) costs ≈ **7.5 K `shards`** ≈ 16 min of at-level income (§5) — a real but cozy
sink, repeated per key item; because fee and income both scale on `mean_shards_normal`, the same
climb on a T12 item (≈ 15.8 K) costs the same ≈ 16 min at its own level. Pity
(`10_systems/ENHANCEMENT.md` §3) bounds the worst case; luck never inflates the *fee* past the
5-attempt cap per level.

### 3.1 Stat free-point reallocation fee

`10_systems/STATS.md` §4.3 makes the +2/level free pool reallocatable at a town NPC for a `shards`
fee; this doc owns the number:

```
reallocation_fee(L) = round( 50 · L )       # full respec of the free pool
```

Lv 10 → 500; Lv 30 → 1,500; Lv 80 (arc-2 top, `docs/00_vision/SCOPE.md`) → 4,000. The
formula is designed to keep scaling unchanged over the full climb to the Lv 300 cap
(`10_systems/LEVELING.md` §6) as future arcs land. Scales with `level` so it stays a meaningful
choice without ever locking a build (P2 — no trap builds; the pool is always reallocatable).
First-pass; `10_systems/STATS.md`/`10_systems/LEVELING.md` may tune.

## 4. Vendor price bands

Vendors **buy** (player→vendor sell) at **25% of the item's buy value** across the board; they
**sell** (vendor→player) common consumables and basic `common` equip stock. `sell = round(0.25 ·
buy)`.

### 4.1 Consumables (`item_use`, `docs/ID_REGISTRY.md` §use)

| Item (life / essence pair) | Serves band | Buy | Sell |
|---|---|---|---|
| Lesser Life / Essence Tonic (`0001`/`0006`) | Lv 1–9 | 15 | 4 |
| Life / Essence Tonic (`0002`/`0007`) | Lv 10–18 | 60 | 15 |
| Greater … (`0003`/`0008`) | Lv 19–27 | 200 | 50 |
| Superior … (`0004`/`0009`) | Lv 28–36 | 500 | 125 |
| Prime … (`0005`/`0010`) | Lv 37–42 (arc-1 top) | 1,000 | 250 |
| Sovereign … (`0017`/`0018`) | Lv 40–61 (arc 2) | 1,200 | 300 |
| Mythic … (`0019`/`0020`) | Lv 62–80+ (arc 2) | 1,500 | 375 |
| Antidote (`0011`) / Thaw Salve (`0012`) | any | 50 | 12 |
| Millbrook Return Scroll (`0013`) | any | 100 | 25 |
| Hearth Bread (`0014`, food buff) | any | 80 | 20 |
| Sharpening Oil (`0015`) / Ironhide Draught (`0016`) | any | 150 | 37 |

Restore/buff magnitudes are Phase D use-item data (`10_systems/ITEMS.md` §1); this table owns only
price. The tier→band binding is `10_systems/ITEMS.md` §1.1's (the v3 seven-tier ladder: five
arc-1 tiers plus the arc-2 Sovereign/Mythic pairs; the Lv 40–42 Prime/Sovereign overlap is the
intended arc handoff) — restated here as price rows only. The Sovereign/Mythic prices are
first-pass, deliberately flatter than the arc-1 doubling so the §5 bite stays bounded (Open
Questions). A tonic tier is meant to be replaced as you out-level its band (its flat restore
stops keeping pace) — the upgrade cadence is itself a rising sink (§6).

**`steady` scroll shelf** (`10_systems/SCROLLS.md` §4.2 — vendor sells `steady` tier only;
`bold`/`perilous` are drop-/quest-only; resolves that doc's filed §4.1-price-rows question):

| Scroll SKU (`steady`, `docs/ID_REGISTRY.md` scroll block) | Buy | Sell |
|---|---|---|
| Weapon-family `aspect` | 800 | 200 |
| Weapon-family `temper` | 1,200 | 300 |
| Armor-family `aspect` | 500 | 125 |
| Armor-family `temper` | 750 | 188 |
| Accessory-family `aspect` | 600 | 150 |
| Accessory-family `temper` | 900 | 225 |

### 4.3 Travel fares (pointer)

Travel fare numbers live in **§7** (ferry & coach §7.1, longship §7.2) — one table, one owner.
Each fresh character's **one free ride** from Rosen Harbor to their job instructor's town (the
advancement pilgrimage, `docs/WORLD_PLAN.md`) waives the fare once and only once, server-tracked.
Fares are deliberately below one minute of at-band hunting income (§5) — paid convenience, never
a wall (`00_vision/PILLARS.md` P2); walking the ring stays free.

### 4.2 Equipment (buy value by tier × rarity)

Most equipment comes from drops (`10_systems/DROPS.md`); vendors stock only `common` basics and
buy anything at 25%. Buy value = `base_buy(tier) · rarity_mult`:

| Tier (`req_level`) | `base_buy` (`common`) |  | `rarity_mult` |  |
|---|---|---|---|---|
| T1 (1) | 30 |  | `common` | ×1 |
| T2 (8) | 120 |  | `uncommon` | ×2.5 |
| T4 (22) | 600 |  | `rare` | ×8 |
| T6 (36) | 1,800 |  | `epic` | ×30 |
| T8 (50) | 4,000 |  | `legendary` | ×30 (suppressed) |
| T10 (64) | 8,000 |  | | |
| T12 (78) | 13,000 |  | | |

Tier `req_level`s per `10_systems/ITEMS.md` §4 (v3 twelve-tier ladder); `base_buy` for
intermediate tiers interpolates (T3 300, T5 1,050, T7 2,800, T9 6,000, T11 10,500).
**`legendary` and boss-unique vendor value is suppressed to the `epic` multiplier** so the best
gear is used or traded on the future market (`10_systems/social/MARKET.md`), never vendored for a
`shards` windfall (an inflation guard, §6). Example vendoring faucet: a `rare` T6 drop sells for
`round(0.25 · 1800 · 8)` = **3,600** `shards` (≈ 8 min of Lv 36 income) — a satisfying but
non-dominant faucet.

### 4.3 Gilded Charter price (cited by `10_systems/BATTLE_PASS.md` §6)

Unlocking a season's gilt reward lane costs a flat **6,000 `shards`**, per character, per
30-day season — ≈ 16 minutes of Lv 30 at-level income (§5), ≈ 42 minutes at Lv 10: a real
monthly sink that stays cozy (P2). Mechanics, guardrails, and everything else about the
charter are `10_systems/BATTLE_PASS.md`'s; this doc owns only the number. The charter adds
**no faucet**: neither lane ever rewards `shards`, and the season reward lanes' total vendor
value is capped at 1,500 `shards` (`10_systems/BATTLE_PASS.md` §5.3), so §1's faucet list is
unchanged. First-pass number; retune at the D gate.

## 5. Potion economics vs hunting income

A session must net **positive** while potions take a real **~20–30%** bite at combat-heavy levels
(P2 — you always come out ahead, but consumables matter). Model: at-level income =
`480 · mean_shards_normal(L)` (`10_systems/DROPS.md` §3 × `10_systems/LEVELING.md` §1 kills/hour);
potion spend assumes ≈ **18 tonics/hour** of the band tonic (≈ 1 per 27 kills, given
`10_systems/COMBAT_FORMULA.md` §12 i-frames make cozy combat low-attrition).

| Player Lv | Band tonic (buy) | Income/hr | Potion spend/hr | Bite | Net/hr |
|---|---|---|---|---|---|
| 10 | Life Tonic (60) | 8,640 | 1,080 | 12.5% | +7,560 |
| 30 | Superior (500) | 23,040 | 9,000 | 39.1% | +14,040 |
| 50 | Sovereign (1,200) | 37,440 | 21,600 | 57.7% | +15,840 |
| 70 | Mythic (1,500) | 51,840 | 27,000 | 52.1% | +24,840 |
| 90 | Mythic (1,500) | 66,240 | 27,000 | 40.8% | +39,240 |

Band tonics per `10_systems/ITEMS.md` §1.1's v3 ladder. The bite **rises through the 30–70 band**
(the combat-heavy dungeon years) then eases past 80 as income outpaces the capped Mythic price;
early levels (10–18) sit well under 20% — intended tutorial gentleness (P2). Net stays positive
at every level (the hard law), funding the enhancement (§3) and gear (§4) sinks that turn surplus
`shards` into power. Note the honest recompute against the v3 band compression: the modeled bite
now **overshoots the ~20–30% target from the Superior band up** under the unchanged arc-1 prices
and the fixed 18-drinks/hour assumption — flagged for D-gate retune (Open Questions). Exact
restore amounts (Phase D use-item data) set the real drink rate; if tonics restore more/less than
the ~40%-of-band-`life` assumption here, drinks/hour shifts and the bite with it — retune tonic
**price** (§4.1), not the faucet.

## 6. Inflation guardrails (for the future server)

Designed now so the eventual live economy does not inflate (`00_vision/PILLARS.md` P6):

- **Sinks scale with level.** Enhancement fee (§3, ∝ tier × `+`), tonic price (§4.1, ∝ band),
  reallocation fee (§3.1, ∝ `level`) all rise, so a high-level player's `shards` outflow grows with
  their income — no late-game surplus with nothing to spend on.
- **Suppressed high-rarity vendor value** (§4.2) keeps the best gear out of the vendor faucet,
  routing it to the future player market (a `shards` **transfer**, not a faucet) whose transaction
  fee (`10_systems/social/MARKET.md`) is a further sink.
- **No faucet from nothing.** `shards` come only from in-world play (§1); defeat, idling, and
  logging in grant none (`10_systems/DEATH_PENALTY.md` §3).
- **The Cogwork Capsule never mints `shards`** (`10_systems/GACHAPON.md` §1/§7, pillar
  amendment PA-001): capsule tickets cannot be bought or sold for `shards`, and every
  dispensed prize carries vendor value 0 — the game's one real-money product has no path into
  the `shards` supply, so §1's faucet list is unchanged.
- **The Gilded Charter is a recurring sink, not a faucet** (§4.3): a flat monthly `shards`
  outflow per participating character, with the reward lanes' vendor value budget-capped
  (`10_systems/BATTLE_PASS.md` §5.3) so claiming rewards never becomes a `shards` entry point.
- **Guild creation** reserves a large flat sink (placeholder ~100,000 `shards`, owner
  `10_systems/social/GUILD.md`) to soak endgame surplus.
- **Bounded worst-case costs.** Enhancement pity (`10_systems/ENHANCEMENT.md` §3) caps the fee a
  single upgrade can demand, so no sink is an infinite `shards` pit (P2).

## 7. Transport fares (coach, ferry, longship)

Records the paid-transport `shards` fares that `docs/WORLD_PLAN.md` delegates to this doc (its
Coachworks and ferry paragraphs point here; the numbers were previously unwritten — this section
fills that standing delegation) and adds the arc-2 `longship` rows. **Rules** for each mode
(portal semantics, scheduling, spawns, the free-ride flag) are `15_maps_system/MAP_CONNECTIONS.md`'s
transport taxonomy + §8; this section owns only the numbers. All fares are `shards`, charged at
boarding, server-authoritative (`10_systems/PERSISTENCE.md`). Travel is a low-friction loop
(`00_vision/PILLARS.md` P3), so a fare is a **light convenience sink**, not a wall — every fare
below is a small fraction of at-level income (§5), and for the scheduled `longship` the real-time
sail (`15_maps_system/MAP_CONNECTIONS.md` §8), not the shards, is the trip's true cost.

### 7.1 Ferry & coach (paid, instant)

| Mode | Fare | Note |
|---|---|---|
| Harborwind Ferry (Emberfoot ↔ Rosen Harbor, `map_015`) | 40 | Flat; the small crossing fare `docs/WORLD_PLAN.md` previews (Lv ~8 band — ≈ 30 s of Lv 10 income, §5). |
| Coach — 1 ring segment | 120 | Adjacent Harthmoor Coachworks stations. |
| Coach — 2 ring segments | 220 | Longest current hop (e.g. Mossmere ↔ Tidewatch Port, either way around). |
| Coach — 3+ ring segments | 320 | **Future headroom — no current station pair spans 3+ segments** (owner ruling 2026-07-24: `docs/WORLD_PLAN.md`'s ring closure makes Cindershelf ↔ Tidewatch Port adjacent; row kept for future stations). |

Coach ring-distance = number of ring-road segments between the two stations (station adjacency per
`docs/WORLD_PLAN.md`). The one free Rosen Harbor→instructor-town ride (the advancement pilgrimage)
is `docs/WORLD_PLAN.md`'s rule; this table charges every other ride. First-pass, anchored so even
the longest coach hop is well under a minute of in-band income (§5) — coaches are a convenience
shortcut, a minor sink by design (P3), never a gate.

### 7.2 Longship (paid, scheduled — arc-2 island network)

Fare scales with **route length**; the concrete `route_id`→length-class assignment and endpoint
maps live in `docs/WORLD_PLAN.md`'s arc-2 edge table (cited, never restated here). Anchored to the
arc-2 band (Lv 40–80) income (§5) and `mean_shards_normal` back-solved from §3's enhancement
`base_fee` (`mean_shards_normal(40) ≈ 63`, `(70) ≈ 108`): each fare is well under a minute of
at-level income, keeping the scheduled ride — not the shards — the trip's real cost.

| Route length class | Fare | ≈ anchor |
|---|---|---|
| Short (1 hop — Harthmoor pier ↔ nearest new-island port) | 300 | ≈ 5 × `mean_shards_normal(40)` |
| Medium (2 hops) | 500 | ≈ 8 × |
| Long (inter-island, 3+ hops) | 800 | ≈ 13 × (≈ 45 s of Lv 50 income, §5) |

**Free first crossing (adopted):** each character's **first** longship crossing after completing
the Lv 40 2nd advancement is waived by the pier officer — the arc-2 counterpart to
`docs/WORLD_PLAN.md`'s free advancement-pilgrimage coach ride. One-time, per-character,
server-authoritative flag (`10_systems/PERSISTENCE.md`); every later crossing pays the table fare.

## Open Questions

- Every number here (starting `shards`, fee coefficients, tonic prices, `base_buy`, the 18
  drinks/hour assumption) is first-pass, balanced against `10_systems/DROPS.md` §3 and
  `10_systems/LEVELING.md` §1. Retune at the D gate once real spawn density and potion restore
  values land; adjust **prices/fees**, never the `10_systems/DROPS.md` faucet or
  `10_systems/COMBAT_FORMULA.md` `normal_life`.
- **Tonic bite overshoot (§5).** Recomputed against `10_systems/ITEMS.md` §1.1's compressed v3
  bands, the modeled potion bite exceeds the ~20–30% target from Superior up (peaking ≈ 58% at
  Lv 50) even with the deliberately flat Sovereign/Mythic prices. Retune the tonic price ladder
  (§4.1) — or revisit the 18-drinks/hour assumption — at the D gate once Phase D restore values
  land. Owner: this doc with `10_systems/ITEMS.md`.
- The §4.1 `steady` scroll-shelf prices predate the v3 revision and have not been re-anchored to
  the new bands — known debt; revisit with `10_systems/SCROLLS.md` at the D gate.
- Quest `shards` reward budgets (§1) depend on `10_systems/QUESTS.md` honoring a per-region share;
  the split of the total faucet between hunting-drops and quests is unfixed here (default: drops
  dominant, quests supplementary). Confirm with `10_systems/QUESTS.md` at the D gate.
- Market transaction-fee rate and guild-creation fee are stubs owned by the `social/` docs; if
  those systems change the sink budget materially, revisit §6. Flagged, server-dependent.
- A "mastery `exp` → `shards`" post-cap soft sink is floated by `10_systems/LEVELING.md` §6 OQ but
  **not** adopted here (default: cap `exp` discarded). If wanted it is a faucet and belongs in §1,
  balanced against §2.
- Whether stat reallocation should be cheaper/free below some level (to lower the early
  experimentation barrier) is open; default is the flat `50·L` curve (§3.1).
- (MON-001) A billboard-rental `shards` sink in town maps is reserved by
  `10_systems/MONETIZATION.md` §3.2; if adopted it lands as a §2 sink row in a future
  amendment. The premium currency (`gleam`, GLOSSARY Provisional) never converts to or from
  `shards` in either direction — no monetization faucet or sink may ever appear in this doc.
- §7 fares (ferry 40; coach 120/220/320 by ring distance; longship 300/500/800 by route length)
  are first-pass, anchored to §5 income and §3's `mean_shards_normal`. §7.1 also *fills*
  `docs/WORLD_PLAN.md`'s previously-unwritten ferry/coach fare delegation (§4.3's earlier sketch —
  ferry 25, coach `100 × hops` — is superseded; §4.3 is now a pointer, resolved 2026-07-24); if
  that owner intended a
  different band, retune here (never the `10_systems/DROPS.md` faucet). Route→length-class mapping
  for §7.2 is `docs/WORLD_PLAN.md`'s arc-2 edge table's; confirm the class count matches the fare
  tiers when that table lands.
- §7.2 free-first-crossing is adopted (mirrors the free pilgrimage coach ride). The exact trigger
  is "Lv 40 2nd-advancement completed" flag; if `10_systems/JOBS.md` keys the advancement
  differently, align the flag. Whether the waiver should instead attach to the Deepway
  (`15_maps_system/MAP_CONNECTIONS.md` §9, the free walking route) rather than the paid longship is
  a minor call — default keeps it on the longship (the paid mode, where a waiver is meaningful).
- **Resolved (2026-07-24, owner ruling): the 3+-segment coach tier stays as explicit future
  headroom.** §7.1's row now says so (no current station pair spans 3+ segments — WORLD_PLAN's
  ring closure makes the old example pair adjacent), and the 2-segment row carries the real
  longest-hop example (Mossmere ↔ Tidewatch Port).
