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
| T3 (20) | 99 | 99 | 297 | 495 |
| T5 (40) | 189 | 189 | 567 | 945 |
| T6 (50) | 234 | 234 | 702 | 1,170 |
| T8 (70) | 324 | 324 | 972 | 1,620 |
| T10 (90) | 414 | 414 | 1,242 | 2,070 |

Worked: taking one T6 item 0→+9 (guaranteed +1..+5, then the §3-pity risky band, expected ≈ 8
attempts total) costs ≈ **10.5 K `shards`** ≈ 17 min of at-level income (§5) — a real but cozy
sink, repeated per key item. Pity (`10_systems/ENHANCEMENT.md` §3) bounds the worst case; luck
never inflates the *fee* past the 5-attempt cap per level.

### 3.1 Stat free-point reallocation fee

`10_systems/STATS.md` §4.3 makes the +2/level free pool reallocatable at a town NPC for a `shards`
fee; this doc owns the number:

```
reallocation_fee(L) = round( 50 · L )       # full respec of the free pool
```

Lv 30 → 1,500; Lv 50 → 2,500; Lv 100 → 5,000. Scales with `level` so it stays a meaningful choice
without ever locking a build (P2 — no trap builds; the pool is always reallocatable). First-pass;
`10_systems/STATS.md`/`10_systems/LEVELING.md` may tune.

## 4. Vendor price bands

Vendors **buy** (player→vendor sell) at **25% of the item's buy value** across the board; they
**sell** (vendor→player) common consumables and basic `common` equip stock. `sell = round(0.25 ·
buy)`.

### 4.1 Consumables (`item_use`, `docs/ID_REGISTRY.md` §use)

| Item (life / essence pair) | Serves band | Buy | Sell |
|---|---|---|---|
| Lesser Life / Essence Tonic (`0001`/`0006`) | Lv 1–9 | 15 | 4 |
| Life / Essence Tonic (`0002`/`0007`) | Lv 10–29 | 60 | 15 |
| Greater … (`0003`/`0008`) | Lv 30–49 | 200 | 50 |
| Superior … (`0004`/`0009`) | Lv 50–69 | 500 | 125 |
| Prime … (`0005`/`0010`) | Lv 70–100 | 1,000 | 250 |
| Antidote (`0011`) / Thaw Salve (`0012`) | any | 50 | 12 |
| Millbrook Return Scroll (`0013`) | any | 100 | 25 |
| Hearth Bread (`0014`, food buff) | any | 80 | 20 |
| Sharpening Oil (`0015`) / Ironhide Draught (`0016`) | any | 150 | 37 |

Restore/buff magnitudes are Phase D use-item data (`10_systems/ITEMS.md` §1); this table owns only
price. A tonic tier is meant to be replaced as you out-level its band (its flat restore stops
keeping pace) — the upgrade cadence is itself a rising sink (§6).

### 4.2 Equipment (buy value by tier × rarity)

Most equipment comes from drops (`10_systems/DROPS.md`); vendors stock only `common` basics and
buy anything at 25%. Buy value = `base_buy(tier) · rarity_mult`:

| Tier (`req_level`) | `base_buy` (`common`) |  | `rarity_mult` |  |
|---|---|---|---|---|
| T1 (1) | 30 |  | `common` | ×1 |
| T2 (10) | 120 |  | `uncommon` | ×2.5 |
| T4 (30) | 600 |  | `rare` | ×8 |
| T6 (50) | 1,800 |  | `epic` | ×30 |
| T8 (70) | 4,000 |  | `legendary` | ×30 (suppressed) |
| T10 (90) | 8,000 |  | | |

`base_buy` for intermediate tiers interpolates (T3 300, T5 1,050, T7 2,800, T9 6,000).
**`legendary` and boss-unique vendor value is suppressed to the `epic` multiplier** so the best
gear is used or traded on the future market (`10_systems/social/MARKET.md`), never vendored for a
`shards` windfall (an inflation guard, §6). Example vendoring faucet: a `rare` T6 drop sells for
`round(0.25 · 1800 · 8)` = **3,600** `shards` (≈ 5 min of income) — a satisfying but non-dominant
faucet.

## 5. Potion economics vs hunting income

A session must net **positive** while potions take a real **~20–30%** bite at combat-heavy levels
(P2 — you always come out ahead, but consumables matter). Model: at-level income =
`480 · mean_shards_normal(L)` (`10_systems/DROPS.md` §3 × `10_systems/LEVELING.md` §1 kills/hour);
potion spend assumes ≈ **18 tonics/hour** of the band tonic (≈ 1 per 27 kills, given
`10_systems/COMBAT_FORMULA.md` §12 i-frames make cozy combat low-attrition).

| Player Lv | Band tonic (buy) | Income/hr | Potion spend/hr | Bite | Net/hr |
|---|---|---|---|---|---|
| 10 | Life Tonic (60) | 8,640 | 1,080 | 12.5% | +7,560 |
| 30 | Greater (200) | 23,040 | 3,600 | 15.6% | +19,440 |
| 50 | Superior (500) | 37,440 | 9,000 | 24.0% | +28,440 |
| 70 | Prime (1,000) | 51,840 | 18,000 | 34.7% | +33,840 |
| 90 | Prime (1,000) | 66,240 | 18,000 | 27.2% | +48,240 |

The bite deliberately **rises into the 50–70 band** (the combat-heavy dungeon years) then eases at
90 as income outpaces the capped Prime tonic price. Early levels (10–30) sit under 20% — intended
tutorial gentleness (P2). Net is positive at every level, funding the enhancement (§3) and gear
(§4) sinks that turn surplus `shards` into power. Exact restore amounts (Phase D use-item data)
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
- A "mastery `exp` → `shards`" post-cap soft sink is floated by `10_systems/LEVELING.md` §6 OQ but
  **not** adopted here (default: cap `exp` discarded). If wanted it is a faucet and belongs in §1,
  balanced against §2.
- Whether stat reallocation should be cheaper/free below some level (to lower the early
  experimentation barrier) is open; default is the flat `50·L` curve (§3.1).
- (MON-001) A billboard-rental `shards` sink in town maps is reserved by
  `10_systems/MONETIZATION.md` §3.2; if adopted it lands as a §2 sink row in a future
  amendment. The premium currency (`gleam`, GLOSSARY Provisional) never converts to or from
  `shards` in either direction — no monetization faucet or sink may ever appear in this doc.
