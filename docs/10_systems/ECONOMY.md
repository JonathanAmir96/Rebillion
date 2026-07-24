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
| Town travel — Coachworks fares + Harborwind Ferry | §7 (this doc) | ring-hop distance (coach); flat (ferry) |
| Millbrook Return Scroll (`item_use_0013`) | §4.1 (this doc) | flat — paid recall consumable (§7) |
| Enhancement fee | §3 (this doc) | gear tier × target `+` |
| Stat free-point reallocation | §3.1 (this doc) | `level` |
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

| Tier (`req_level`) | `base_fee` | fee @ +1 | @ +5 | @ +9 |
|---|---|---|---|---|
| T1 (1) | 15 | 15 | 45 | 75 |
| T2 (8) | 45 | 45 | 135 | 225 |
| T3 (15) | 78 | 78 | 234 | 390 |
| T4 (22) | 108 | 108 | 324 | 540 |
| T5 (29) | 141 | 141 | 423 | 705 |
| T6 (36) | 171 | 171 | 513 | 855 |
| T7 (40) | 189 | 189 | 567 | 945 |

Worked: taking one T7 item 0→+9 (guaranteed +1..+5, then the §3-pity risky band, expected ≈ 8
attempts total) costs ≈ **5.1 K `shards`** ≈ 10 min of at-level (Lv 42) income (§5) — a real but
cozy sink, repeated per key item. Pity (`10_systems/ENHANCEMENT.md` §3) bounds the worst case; luck
never inflates the *fee* past the 5-attempt cap per level.

### 3.1 Stat free-point reallocation fee

`10_systems/STATS.md` §4.3 makes the +2/level free pool reallocatable at a town NPC for a `shards`
fee; this doc owns the number:

```
reallocation_fee(L) = round( 50 · L )       # full respec of the free pool
```

Lv 30 → 1,500; Lv 42 (arc end) → 2,100; reference Lv 80 → 4,000. Scales with `level` so it stays a
meaningful choice without ever locking a build (P2 — no trap builds; the pool is always
reallocatable). First-pass; `10_systems/STATS.md`/`10_systems/LEVELING.md` may tune.

## 4. Vendor price bands

Vendors **buy** (player→vendor sell) at **25% of the item's buy value** across the board; they
**sell** (vendor→player) common consumables and basic `common` equip stock. `sell = round(0.25 ·
buy)`.

### 4.1 Consumables (`item_use`, `docs/ID_REGISTRY.md` §use)

The five tonic tiers span the authored Lv 1–42 arc (`docs/ID_REGISTRY.md`; band mapping here,
magnitudes are Phase D `10_systems/ITEMS.md` data):

| Item (life / essence pair) | Serves band | Buy | Sell |
|---|---|---|---|
| Lesser Life / Essence Tonic (`0001`/`0006`) | Lv 1–8 | 15 | 4 |
| Life / Essence Tonic (`0002`/`0007`) | Lv 9–17 | 50 | 13 |
| Greater … (`0003`/`0008`) | Lv 18–25 | 130 | 33 |
| Superior … (`0004`/`0009`) | Lv 26–33 | 280 | 70 |
| Prime … (`0005`/`0010`) | Lv 34–42 | 500 | 125 |
| Antidote (`0011`) / Thaw Salve (`0012`) | any | 50 | 12 |
| Millbrook Return Scroll (`0013`) | any | 2,500 | 625 |
| Hearth Bread (`0014`, food buff) | any | 80 | 20 |
| Sharpening Oil (`0015`) / Ironhide Draught (`0016`) | any | 150 | 37 |

Restore/buff magnitudes are Phase D use-item data (`10_systems/ITEMS.md` §1); this table owns only
price. A tonic tier is meant to be replaced as you out-level its band (its flat restore stops
keeping pace) — the upgrade cadence is itself a rising sink (§6).

**The Millbrook Return Scroll (`0013`) is a paid travel sink, not a cheap convenience.** Per the
`docs/WORLD_PLAN.md` ruling (v2.2) it is a **shard-priced vendor consumable** — a single-use, one-way
recall to Millbrook Central's `main` spawn, purchasable in advance and stockpiled — sold at every
town's general-goods vendor. It is **not free** and there is no free warp anywhere
(`15_maps_system/MAP_CONNECTIONS.md` §3). Its **2,500** `shards` price is set **above the priciest
coach ride to Millbrook** (a 2-hop 1,800-`shards` fare, §7) as a deliberate convenience premium: the
scroll recalls from **anywhere** — including dungeons, arenas, and the station-less Sunken Depths
spur — instantly and without walking to a coach stop, where a coach only runs station-to-station
(§7). Pricing rationale and the fare comparison live in §7.

### 4.2 Equipment (buy value by tier × rarity)

Most equipment comes from drops (`10_systems/DROPS.md`); vendors stock only `common` basics and
buy anything at 25%. Buy value = `base_buy(tier) · rarity_mult`:

| Tier (`req_level`) | `base_buy` (`common`) |  | `rarity_mult` |  |
|---|---|---|---|---|
| T1 (1) | 30 |  | `common` | ×1 |
| T2 (8) | 100 |  | `uncommon` | ×2.5 |
| T4 (22) | 360 |  | `rare` | ×8 |
| T6 (36) | 870 |  | `epic` | ×30 |
| T7 (40) | 1,050 |  | `legendary` | ×30 (suppressed) |

`base_buy` for intermediate tiers interpolates (T3 210, T5 570).
**`legendary` and boss-unique vendor value is suppressed to the `epic` multiplier** so the best
gear is used or traded on the future market (`10_systems/social/MARKET.md`), never vendored for a
`shards` windfall (an inflation guard, §6). Example vendoring faucet: a `rare` T6 drop sells for
`round(0.25 · 870 · 8)` = **1,740** `shards` (≈ 3 min of income) — a satisfying but non-dominant
faucet.

## 5. Potion economics vs hunting income

A session must net **positive** while potions take a real **~20–30%** bite at combat-heavy levels
(P2 — you always come out ahead, but consumables matter). Model: at-level income =
`480 · mean_shards_normal(L)` (`10_systems/DROPS.md` §3 × `10_systems/LEVELING.md` §1 kills/hour);
potion spend assumes ≈ **18 tonics/hour** of the band tonic (≈ 1 per 27 kills, given
`10_systems/COMBAT_FORMULA.md` §12 i-frames make cozy combat low-attrition).

| Player Lv | Band tonic (buy) | Income/hr | Potion spend/hr | Bite | Net/hr |
|---|---|---|---|---|---|
| 8 | Lesser (15) | 7,200 | 270 | 3.8% | +6,930 |
| 17 | Life (50) | 13,920 | 900 | 6.5% | +13,020 |
| 25 | Greater (130) | 19,680 | 2,340 | 11.9% | +17,340 |
| 33 | Superior (280) | 25,440 | 5,040 | 19.8% | +20,400 |
| 42 | Prime (500) | 31,680 | 9,000 | 28.4% | +22,680 |

The bite deliberately **rises into the Lv 30–42 arc endgame** (the combat-heavy dungeon and
Clockwork years), peaking near the 28% target at the Lv 42 arc end. Early levels (8–25) sit under
20% — intended tutorial gentleness (P2). Net is positive at every level, funding the enhancement
(§3) and gear (§4) sinks that turn surplus `shards` into power. Exact restore amounts (Phase D
use-item data)
set the real drink rate; if tonics restore more/less than the ~40%-of-band-`life` assumption here,
drinks/hour shifts and the bite with it — retune tonic **price** (§4.1), not the faucet.

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
- **Guild creation** reserves a large flat sink (placeholder ~100,000 `shards`, owner
  `10_systems/social/GUILD.md`) to soak endgame surplus.
- **Bounded worst-case costs.** Enhancement pity (`10_systems/ENHANCEMENT.md` §3) caps the fee a
  single upgrade can demand, so no sink is an infinite `shards` pit (P2).

## 7. Travel sinks — Harthmoor Coachworks fares & Harborwind Ferry

Town-to-town travel is a **paid `shards` sink**, not a free warp (P3 — a legible world you traverse,
not teleport across). `15_maps_system/MAP_CONNECTIONS.md` §3 owns the **rules** (which towns carry a
station, the no-cooldown/no-unlock policy, the one free novice pilgrimage ride, the ferry rules);
this section owns the **numbers** it hands off. `docs/WORLD_PLAN.md`'s "Harthmoor Coachworks" table
is the authoritative list of stations; fares here never add or move one.

**Derivation.** Fares are anchored to the `10_systems/DROPS.md` §3 shard faucet: at-level hunting
income is `≈ 480 · mean_shards_normal(L)` (DROPS §3), which DROPS publishes as ≈ 8.6 K/hr at Lv 10,
≈ 16 K/hr mid-arc (Lv 20, ≈ 264 `shards`/min), ≈ 23 K/hr at Lv 30, ≈ 32 K/hr at the Lv 42 arc end.
A **1-ring-hop coach ride is priced at ≈ 4 minutes of that mid-arc income** (1,000 `shards`); each
additional ring hop adds ≈ 80% (2 hops → 1,800). This keeps a coach ride a cozy few-minutes sink
mid-arc — real, but never a tax — and cheaper still per-minute as income rises through the late arc.

### 7.1 Coach fares (`shards`, per ride)

Fare scales with **ring-hop distance** between the two stations along `docs/WORLD_PLAN.md`'s ring
order **Millbrook ↔ Verdant ↔ Gloomwood ↔ Ashfall ↔ Tidewatch ↔ Millbrook**, with **Millbrook
Central the hub** most rides route through conceptually (`15_maps_system/MAP_CONNECTIONS.md` §3).
Gloomwood carries no station, so the shortest ring path between two stations may pass through it
without stopping. Ring-hop distance is the minimum number of ring steps between the two stations'
regions (Rosen Harbor and Millbrook Central both sit in the south Millbrook hub = 0 hops apart).

| Ring-hop distance | Fare (`shards`) | ≈ mid-arc income (Lv 20) |
|---|---|---|
| 0 (same hub: Rosen Harbor ↔ Millbrook Central) | 300 | ≈ 1 min |
| 1 hop | 1,000 | ≈ 4 min |
| 2 hops | 1,800 | ≈ 7 min |

Two hops is the maximum between any two of the five stations. Full station-pair matrix (both
directions cost the same; Phase D copies this):

| From \ To | Rosen Harbor | Millbrook Central | Mossmere | Cindershelf | Tidewatch Port |
|---|---|---|---|---|---|
| **Rosen Harbor** (`map_017`) | — | 300 | 1,000 | 1,800 | 1,000 |
| **Millbrook Central** (`map_018`) | 300 | — | 1,000 | 1,800 | 1,000 |
| **Mossmere** (`map_043`) | 1,000 | 1,000 | — | 1,800 | 1,800 |
| **Cindershelf** (`map_125`) | 1,800 | 1,800 | 1,800 | — | 1,000 |
| **Tidewatch Port** (`map_071`) | 1,000 | 1,000 | 1,800 | 1,000 | — |

Cindershelf (Ashfall) is the far station — 2 hops from the Millbrook hub going back through
Tidewatch — so rides to/from it are the priciest, matching the "Cindershelf is deliberately the
boldest first trip" note (`docs/WORLD_PLAN.md`). The **one free novice pilgrimage ride** (Rosen
Harbor → the character's job-instructor town, `15_maps_system/MAP_CONNECTIONS.md` §3) waives one
fare per character, server-authoritative (`10_systems/PERSISTENCE.md`); every ride thereafter is
paid at the table above.

### 7.2 Harborwind Ferry fare

The **Harborwind Ferry** (`map_015`) is the sole crossing between Emberfoot Isle and Harthmoor Isle
and charges a **flat 150 `shards` per crossing**, both directions (`15_maps_system/MAP_CONNECTIONS.md`
§3.1). It is deliberately **small** — ≈ 1 min of Lv-8 income (≈ 7.2 K/hr, DROPS §3) — because it
gates every fresh Lv-8 novice leaving the training island; a character has always out-hunted the
50-`shards` starting purse (§1) well before reaching the dock, so the fare is a token sink, not a
wall. It is a separate line item from the coach fares (they never combine on one trip).

### 7.3 Millbrook Return Scroll vs the fare table

The **Millbrook Return Scroll** (`item_use_0013`, priced in §4.1 at **2,500** `shards`) is the paid
magic alternative to walking or coaching home. It is priced **above the 1,800-`shards` maximum coach
fare to Millbrook** as a convenience premium: unlike a coach — which runs only station-to-station and
must be reached on foot — the scroll recalls to Millbrook Central from **anywhere** (mid-field, a
dungeon, an arena, or the station-less Sunken Depths spur, `15_maps_system/MAP_CONNECTIONS.md` §7),
instantly, and is **bought in advance and carried**. That anywhere-instant convenience is what the
premium buys. There is **no free recall** and no free warp (`15_maps_system/MAP_CONNECTIONS.md` §3).

## Open Questions

- Every number here (starting `shards`, fee coefficients, tonic prices, `base_buy`, the 18
  drinks/hour assumption) is first-pass, balanced against `10_systems/DROPS.md` §3 and
  `10_systems/LEVELING.md` §1. Retune at the D gate once real spawn density and potion restore
  values land; adjust **prices/fees**, never the `10_systems/DROPS.md` faucet or
  `10_systems/COMBAT_FORMULA.md` `normal_life`.
- Quest `shards` reward budgets (§1) depend on `10_systems/QUESTS.md` honoring a per-region share;
  the split of the total faucet between hunting-drops and quests is unfixed here (default: drops
  dominant, quests supplementary). Confirm with `10_systems/QUESTS.md` at the D gate.
- Market transaction-fee rate and guild-creation fee are stubs owned by the `social/` docs; if
  those systems change the sink budget materially, revisit §6. Flagged, server-dependent.
- No cap-`exp` "mastery → `shards`" sink is needed this arc — under cap 300 all `exp` in the Lv 1–42
  arc goes to levels (`10_systems/LEVELING.md` §6, no post-cap discard). If a future arc's tail ever
  wants an `exp`-overflow sink it belongs in §1, balanced against §2.
- Whether stat reallocation should be cheaper/free below some level (to lower the early
  experimentation barrier) is open; default is the flat `50·L` curve (§3.1).
- Coach fares, the ferry fare, and the Return Scroll price (§7, §4.1) are first-pass, derived from
  the `10_systems/DROPS.md` §3 faucet at the mid-arc (Lv 20) income anchor. They are **flat**, not
  level-scaled, so their real bite shrinks as income rises across the arc — intended (travel should
  feel cheaper as you grow), but confirm at the D gate that a 2-hop 1,800-`shards` fare is not
  punishing for an under-income Lv 8–14 player who coaches early. If the ring-distance/Millbrook-hub
  pricing model in `15_maps_system/MAP_CONNECTIONS.md` §3 needs adjustment once these land, flag it
  back to that doc's owner (its Open Questions handed the fare table here).
