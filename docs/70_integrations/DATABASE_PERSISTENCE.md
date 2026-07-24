# DATABASE_PERSISTENCE.md — Storage Schema, Transactions & Write Cadence

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 10_systems/PERSISTENCE.md,
10_systems/INVENTORY.md, 10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/ECONOMY.md,
10_systems/QUESTS.md, 10_systems/SKILL_SYSTEM.md, 10_systems/STATUS_EFFECTS.md,
10_systems/DROPS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/DEATH_PENALTY.md,
10_systems/social/TRADING.md, 10_systems/social/MARKET.md, 10_systems/social/MAIL.md,
10_systems/social/GUILD.md, 10_systems/social/PARTY.md, 30_engineering/ENGINEERING_STANDARDS.md,
docs/ID_REGISTRY.md, 70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/ACCOUNTS_AUTH.md,
70_integrations/GAMEPLAY_SIMULATION.md, 70_integrations/NETWORK_PROTOCOL.md,
70_integrations/WORLD_CHANNELS.md, 70_integrations/CHAT_SOCIAL_BACKEND.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

Doc 4 of 7 in the backend wave. `70_integrations/BACKEND_ARCHITECTURE.md` is the gated topology
contract; its §9 delegates **storage schema, transaction boundaries, and write cadence** to this
doc, and its §3 fixes the **technology** each store runs on (PostgreSQL for the three transactional
concerns, an append-only log store off Postgres for the seeded-RNG audit stream, Redis + BEAM-native
ETS/Presence for cache). This doc does not re-pick technology or re-map authority — it lands the
`10_systems/PERSISTENCE.md` §2 truth ledger onto concrete tables, defines the transactions that keep
value atomic, and sets what the live server writes immediately versus on a checkpoint cadence. It
restates no system's rules or values: `enhance_level`/soft-pity **semantics** stay
`10_systems/ENHANCEMENT.md`'s (this doc stores the counters), `shards` faucets/sinks stay
`10_systems/ECONOMY.md`'s, the drop/combat roll math stays `10_systems/DROPS.md`/
`10_systems/COMBAT_FORMULA.md`'s. **Implemented when:** after the interim solo build ships and the
owner greenlights a live server (`70_integrations/BACKEND_ARCHITECTURE.md` §6,
`10_systems/PERSISTENCE.md` §5) — until then this is the forward contract the solo `GameState`
facade's local-file store becomes, dormant by design and blocking nothing in the solo build.

## 1. Scope & relationship to the contract stack

- `10_systems/PERSISTENCE.md` **owns** the authority taxonomy (§1), the truth ledger (§2), the solo
  autosave-trigger table (§6), and the `save_version` law (§8). This doc consumes all four and never
  redefines them.
- `70_integrations/BACKEND_ARCHITECTURE.md` **owns** the topology, the server stack, the database
  **technology** (§3), and the authority→component mapping (§5). This doc sits under its §3 table and
  fills in the schema/transaction/cadence detail it delegates in §9.
- `70_integrations/ACCOUNTS_AUTH.md` **owns** the account/character split, credential and session
  lifecycle, and name policy. This doc stores the character-identity row and the `account_id` binding
  it defines but never the credential policy: the password hash's algorithm/parameters are that doc's
  §3 stance and environment-managed (`70_integrations/BACKEND_ARCHITECTURE.md` §10) — cited by name
  and topic here, not depended on by exact section text (that doc is revised in parallel).
- Sibling boundaries this doc does not cross: the tick model and reconciliation cadence are
  `70_integrations/GAMEPLAY_SIMULATION.md`'s; the wire format that carries a save/sync is
  `70_integrations/NETWORK_PROTOCOL.md`'s; channel capacity is `70_integrations/WORLD_CHANNELS.md`'s;
  the social-service internals (relay topology, roster state, live-escrow mechanics) are
  `70_integrations/CHAT_SOCIAL_BACKEND.md`'s. This doc owns only where their durable state lands and
  how it commits.

All DDL below is a **design-level sketch** — field lists and key choices a coding-pass engineer can
estimate from. Concrete column types, index tuning, and the migration framework itself are coding-pass
work (`30_engineering/ENGINEERING_STANDARDS.md`, locked — cited, never edited).

## 2. Storage topology — one database, three schemas, one audit stream, one cache

`70_integrations/BACKEND_ARCHITECTURE.md` §3 lists three transactional concerns — **character DB**,
**wallet/economy ledger**, **social/market DB** — each as its "own logical database/**schema**." This
doc resolves that slash: the three concerns are **three PostgreSQL schemas inside a single database on
a single cluster** (`char`, `wallet`, `social`), each owned by its own least-privilege DB role, **not**
three separate `CREATE DATABASE` databases.

**Why schemas, not separate databases — the cross-concern atomicity decision.** The design has
transactions that must move value across concern boundaries and commit as one unit: a two-party trade
swaps items (`char`) and `shards` (`wallet`) and writes a trade log (`social`); a market buy debits/
credits `wallet`, moves an item in `char`, and closes a listing in `social`; mail COD and the
enhancement fee cross `char`↔`wallet` identically (`70_integrations/BACKEND_ARCHITECTURE.md` §7 already
states these "write through the wallet ledger and character DB … inside one Postgres transaction").
PostgreSQL cannot span a transaction across two separate databases without two-phase commit. Placing
the three concerns as **schemas in one database** makes every one of those money-moving operations an
ordinary single-database, multi-schema ACID transaction — no 2PC, no distributed coordinator, no
eventual-consistency window on a ledger that must never transiently show minted or lost value
(`10_systems/INVENTORY.md` §9 anti-dupe; `70_integrations/BACKEND_ARCHITECTURE.md` §3 "no minting, no
loss"). The `§1` "separated by concern so a market outage cannot corrupt character saves" invariant is
preserved at the **schema + role** level: the social-service role has no write grant on `char.*` or
`wallet.*`, so a market-code fault touches only `social.*`, and the §8 degradation table (social →
read-only, character/wallet unaffected) holds exactly as written. A whole-**engine** loss takes down
all three regardless of database-vs-schema split, so co-location weakens no fault-isolation guarantee
the single-engine choice already made.

**Rejected alternatives:**
- **Three separate databases + two-phase commit (`PREPARE TRANSACTION`).** Buys physical DB isolation
  at the cost of 2PC's operational fragility: a leaked prepared transaction pins WAL, blocks vacuum,
  and a coordinator crash strands prepared transactions that must be resolved by hand. Pure downside
  for a single-region, hundreds-to-low-thousands-concurrent world
  (`70_integrations/BACKEND_ARCHITECTURE.md` §2 scale).
- **Three separate databases + outbox / eventual reconciliation.** Gives eventual consistency —
  precisely wrong for a `shards` ledger and item escrow that must be atomic at all times
  (`10_systems/social/TRADING.md` §3 "no partial state is ever visible"). Rejected for value transfer.
- **Postgres foreign-data-wrapper across databases.** Cross-DB FDW writes are not transactional in the
  way a single-database multi-schema commit is; it reintroduces the 2PC problem with more moving parts.

Off the transactional engine, unchanged from `70_integrations/BACKEND_ARCHITECTURE.md` §3:
- **Seeded-RNG audit log** — the append-only log store (partitioned object storage / log-structured
  stream). Write-once, read-rarely (forensic/replay). Holds drop rolls and combat resolution (§3.4).
- **Cache tier** — Redis for cross-node coordination + BEAM-native ETS/Phoenix.Presence for in-node
  ephemeral state. Never a source of truth; holds session/presence/cooldown/live-escrow state (§5).

**Runtime keys vs authored IDs.** `docs/ID_REGISTRY.md` blocks own **design-time authored** content
IDs (`item_equip_*`, `mob_*`, `quest_*`, …), which are immutable and range-bound (CLAUDE.md Law 3).
Runtime, player-created rows (a character, a guild, a market listing, a mail, an item **instance**) are
**not** authored content and carry **server-assigned surrogate primary keys** minted outside the
authored ranges. This doc confirms the `10_systems/social/GUILD.md`-proposed `guild_<NNNNNN>` format
for the guild PK and uses the same server-minted-surrogate convention for the other runtime entities.
The character-identity PK format is `70_integrations/ACCOUNTS_AUTH.md`'s to fix (character identity is
its entity); this doc stores whatever surrogate that doc mints and keys `char.character` on it.

## 3. Truth-ledger → storage map

Every row of `10_systems/PERSISTENCE.md` §2 (as mapped to a store by
`70_integrations/BACKEND_ARCHITECTURE.md` §5) lands below. Owning docs keep their rules; this doc keeps
only the shape.

### 3.1 `char` schema — character DB

```sql
-- Identity (PERSISTENCE §2 "Character identity"; ACCOUNTS_AUTH §2/§8 owns policy)
character(
  character_id      pk,            -- server-minted surrogate (ACCOUNTS_AUTH owns the format)
  account_id        fk,            -- binding to the account root (ACCOUNTS_AUTH §2)
  name              text unique,   -- global uniqueness (ACCOUNTS_AUTH §5, enforced by this index)
  job_line          enum,          -- novice|bulwark|keeneye|weaver|flicker (GLOSSARY; JOBS owns)
  hair              text,          -- style_hair_NN   ┐ creation appearance picks (ACCOUNT §3);
  face              text,          -- style_face_NN   │ values range-checked against ID_REGISTRY
  hair_color        text,          -- style_haircolor │ "Appearance styles" on write (creation +
  skin              text,          -- style_skin_NN   ┘ any future restyle); CHARACTER_COMPOSITING
                                   --   owns what they render as. Stored as ids, never art refs.
  bind_map          fk map_NNN,    -- bind point (DEATH_PENALTY §4)
  bind_spawn        text,          -- named spawn on bind_map
  save_version      int,           -- §6 migration lineage
  created_ts        timestamptz )

-- level/exp (PERSISTENCE §2; LEVELING owns the curve)
character_progress(
  character_id      pk fk,
  level             int,
  exp_total         bigint,        -- cumulative; exp_into_level is derived from the LEVELING curve
  exp_into_level    bigint )       -- stored for fast read; re-derivable from exp_total on import (§6)

-- primary stats + free-point allocation (PERSISTENCE §2; STATS §7-§8 owns)
character_stats(
  character_id      pk fk,
  might_free        int,           -- the +2/level allocatable pool per stat; base stats derive
  finesse_free      int,           --   from level, so ONLY the free-point inputs are stored
  focus_free        int,
  fortune_free      int )
-- Derived stats (power/armor/warding/crit_*/… , GLOSSARY) are NEVER stored: the server recomputes
-- them from level + free points + worn gear on load (STATS §8 — a client-recomputed derived stat is
-- never trusted). Storing inputs, not outputs, is the anti-cheat posture of the whole ledger.

-- Inventory 3 tabs + bank 3 tabs (INVENTORY §1/§7)
inventory_slot(
  character_id      fk,
  container         enum,          -- carry | bank   (worn is its own table below)
  tab               enum,          -- equip | use | etc  (INVENTORY §1)
  slot_index        int,           -- 0..(unlocked-1)
  item_id           fk item_*,     -- base definition ref
  qty               int,           -- 1 for equip; up to stack cap for use(100)/etc(999)
  instance_id       fk nullable,   -- set for equips (→ item_instance); null for stackables
  locked            bool,          -- slot-lock QoL (INVENTORY §8)
  primary key (character_id, container, tab, slot_index) )

inventory_tab_expansion(              -- +8→48 carry / +8→? bank unlock state (INVENTORY §1/§7)
  character_id fk, container enum, tab enum, slots_unlocked int,
  primary key (character_id, container, tab) )

-- Per-equip mutable state that can never stack (INVENTORY §2)
item_instance(
  instance_id       pk,            -- server-minted surrogate
  item_id           fk item_equip_*,-- base def (ITEMS)
  holder            fk nullable,   -- character_id when carried/worn; NULL while in durable escrow
                                   --   (market listing / mail attachment) — §4
  enhance_level     int,           -- 0..9 (ENHANCEMENT §2 — this doc stores it, ENHANCEMENT owns the rule)
  soft_pity_fails   int,           -- consecutive fails at the current target + (ENHANCEMENT §3;
                                   --   resets to 0 on success, does not carry across + levels)
  rolled_affixes    jsonb,         -- the §10 affix lines rolled once at creation (ITEMS §10) — immutable
  tradeable         bool )         -- untradeable policy (TRADING §4; schema field pending, that doc's OQ)

-- Equipment worn, keyed by slot token (ITEMS §2 roster: weapon/head/body/legs/boots/gloves/cape/
-- ring/amulet + shield/overall from the equipment-v2 wave)
equipment_worn(
  character_id fk, slot enum, instance_id fk item_instance,
  primary key (character_id, slot) )

-- Quest flags / step progress / completed set (QUESTS)
quest_state(
  character_id fk, quest_id fk quest_NNN,
  status enum,                     -- active | completed (the completed set = status='completed' rows)
  steps jsonb,                     -- per-step progress counters for active quests (QUESTS §3)
  accepted_ts timestamptz,
  primary key (character_id, quest_id) )

-- Skill ranks + respec (SKILL_SYSTEM §2/§3). Respec is free/unlimited (§3) so there is no separate
-- respec "state" to persist — current ranks ARE the state; a respec rewrites these rows. The point
-- pool is derived (f(level) − Σ rank), never stored, per STATS' store-inputs rule.
skill_rank(
  character_id fk, skill_id fk skill_<line>_NNN, rank int,  -- 0..10 (max_level 10)
  primary key (character_id, skill_id) )

-- Cooldown timers stay in-memory per BACKEND_ARCHITECTURE §5 (ETS/Redis); only a checkpoint SNAPSHOT
-- is persisted so a relog restores remaining cooldowns (§5 cadence). Not a hot table.
-- Active status effects on save (STATUS_EFFECTS) — likewise snapshot-only (§5).
session_snapshot(
  character_id      pk fk,
  life_current      int,           -- current life/essence pools (STATS) — checkpoint value
  essence_current   int,
  cooldowns         jsonb,         -- skill_id → remaining s (SKILL_SYSTEM §5; in-memory truth, snapshotted)
  status_effects    jsonb,         -- active buffs/debuffs: token, remaining dur, stacks, snapshot
                                   --   source_power/crit_power per STATUS_EFFECTS §1 — written on save only
  checkpoint_ts     timestamptz )
-- Position / velocity are authority:shared and NEVER persisted mid-run (PERSISTENCE §4;
-- BACKEND_ARCHITECTURE §5/§8 — disposable). A restart resumes at bind/last-transition, not last pixel.
```

### 3.2 `wallet` schema — wallet / economy ledger

The `shards` wallet (`10_systems/PERSISTENCE.md` §2; per-character at launch, that doc's confirmed OQ)
is modeled as a **materialized balance plus an append-only journal**, so balance is always
reconstructable and value can be neither minted nor lost (`70_integrations/BACKEND_ARCHITECTURE.md` §3).

```sql
wallet(
  character_id  pk fk,
  balance       bigint,       -- 64-bit width (INVENTORY §3); display/design cap 2,000,000,000
  updated_ts    timestamptz )

wallet_ledger(                 -- append-only; every balance change writes one row in the SAME txn
  entry_id      pk,
  character_id  fk,
  delta         bigint,        -- signed
  balance_after bigint,
  reason        enum,          -- drop_faucet | quest_reward | vendor_sell | vendor_buy |
                               --   enhancement_fee | coach_fare | ferry_fare | respec_fee |
                               --   trade_in | trade_out | market_list_fee | market_proceeds |
                               --   market_purchase | mail_cod_in | mail_cod_out | mail_shards |
                               --   guild_fee   (numbers all owned by ECONOMY / the social docs)
  ref           text,          -- trade_id / listing_id / mail_id / enhancement audit-ref, when applicable
  ts            timestamptz )
```

`wallet.balance` is a same-transaction materialization of `Σ delta`; the ledger is the truth and the
backup-verify drill (§7) sums it against `balance`. A credit that would push `balance` over the
`10_systems/INVENTORY.md` §3 cap is **rejected before commit** (blocked at source, never truncated) —
the rule is INVENTORY's, the enforcement point is here.

### 3.3 `social` schema — social / market DB

```sql
guild(                          -- durable (a guild persists whether or not its leader is online, GUILD §3)
  guild_id   pk,                -- server-minted 'guild_<NNNNNN>' (§2; confirms GUILD's proposed format)
  name       text unique,       -- global uniqueness (GUILD §2)
  crest      jsonb,             -- { shape, symbol, primary, accent } (GUILD §5)
  motd       text,              -- ≤200 chars (GUILD §6)
  roster_cap int,               -- 20..60 in +10 steps (GUILD §4)
  created_ts timestamptz )
guild_member(
  guild_id fk, character_id fk unique,   -- one membership per character (GUILD §1)
  rank enum,                    -- leader | officer | member (GUILD §3)
  rank_label text, joined_ts timestamptz,
  primary key (guild_id, character_id) )

market_listing(                 -- durable async escrow (persists across sessions, unlike a live trade)
  listing_id pk, seller fk character_id,
  instance_id fk item_instance nullable,  -- escrowed equip (its item_instance.holder = NULL while listed)
  item_id fk, qty int,
  ask_price bigint, listing_fee_paid bigint,   -- rate owned by ECONOMY (MARKET)
  listed_ts timestamptz, expires_ts timestamptz,
  status enum )                 -- active | sold | expired | canceled (MARKET data sketch)

mail(                           -- durable store-and-forward mailbox + COD escrow (MAIL)
  mail_id pk, sender fk character_id, recipient fk character_id,
  subject text, body text,
  attach_instance_id fk item_instance nullable,  -- single item attachment, escrowed until claim/return
  shards_attached bigint, cod_amount bigint,     -- MAIL data sketch
  sent_ts timestamptz, expires_ts timestamptz,
  status enum )                 -- unread | read | claimed | expired_returned

trade_log(                      -- append-only anti-fraud record of COMPLETED trades (TRADING §5)
  trade_id pk, character_a fk, character_b fk,
  offer_a jsonb, offer_b jsonb, ts timestamptz )
```

**Ephemeral, authoritative-but-not-durable social state** (held by the social/world tier in ETS/Redis,
never written to Postgres — `70_integrations/CHAT_SOCIAL_BACKEND.md` owns the mechanics):
- **Party** — roster, HUD-plate data, loot-mode, rotation counter (`10_systems/social/PARTY.md`). A
  party does not survive logout/disband (a party of 1 auto-disbands, PARTY §1); it is live coordination
  state, so it has **no durable table**. Its authority is server-held, its lifetime is the session.
- **Live trade session** — the in-flight offer/lock/confirm escrow (`10_systems/social/TRADING.md` §3)
  lives in the escrow-in-flight cache while both parties are present; only the atomic swap (§4.2) and
  the `trade_log` row are durable.
- **Chat** — stateless relay off the gateway/social tier (`70_integrations/BACKEND_ARCHITECTURE.md`
  §7); nothing persisted here.

The durable-vs-ephemeral split is deliberate: **asynchronous** transfers (market listing, mail
attachment) escrow **durably** because they outlive a session; **synchronous** transfers (live trade)
escrow in **cache** because both parties are present for the whole session.

### 3.4 Audit log store — off Postgres (append-only)

Two `authority: server` rows from `10_systems/PERSISTENCE.md` §2 are NOT durable game state but a
**write-once forensic stream**, per `70_integrations/BACKEND_ARCHITECTURE.md` §3/§5:

- **Drop rolls & loot tagging** (`10_systems/DROPS.md` §7/§9): one record per roll — seed, `mob_NNN`,
  eligible tagger `character_id`(s), `fortune` bias input, and outputs (pool selection, `rarity`,
  `qty`, resolved `item_*`). The 60/120 s ownership-window timers (`10_systems/DROPS.md` §7) are
  **runtime** state in the map process, not persisted; only the roll is logged. The item, once picked
  up, becomes a durable `char` inventory/`item_instance` row on **loot commit** (§4.1).
- **Combat resolution** (`10_systems/COMBAT_FORMULA.md` §1): one record per hit event — seed, attacker,
  target, skill/ability ref, and outputs (hit/crit/damage/mitigation). High-write, read-rarely; the
  durable consequence (`life` change, a death) is applied in the session/`char` layer, not here.

Both flow through the single seeded RNG service so any result is server-verifiable later against this
log (`70_integrations/BACKEND_ARCHITECTURE.md` §2/§4). Retention window and storage class are
**owner-priced** — see `70_integrations/BACKEND_ARCHITECTURE.md` Open Questions (§3); not duplicated
here.

## 4. Transaction boundaries

Every operation below commits as **one ACID transaction** (or refuses whole). Because the three
concerns are schemas in one database (§2), any transaction spanning `char`+`wallet`+`social` is an
ordinary multi-schema commit — no 2PC. Gated rolls (enhancement, drops, combat) obey an **audit-first
ordering**: the seeded roll is appended to the audit log (§3.4) *before* the Postgres transaction that
applies its result, so a committed consequence always has a preceding audit record; if the audit log is
unwritable the roll is blocked and nothing commits (`10_systems/PERSISTENCE.md` §7;
`70_integrations/BACKEND_ARCHITECTURE.md` §8 "an ungated roll is worse than a paused one"). An orphan
audit record for a roll whose Postgres commit then failed is acceptable — the log is a superset of
applied results, marked attempted.

| Transaction | Schemas / rows | Atomicity note |
|---|---|---|
| **Inventory move / split / merge / bank deposit-withdraw** | `char`: the affected `inventory_slot` rows (± `item_instance.holder`, `inventory_tab_expansion`) | Single-schema; commits synchronously (a lost move could dupe/lose an item, so it is never cadence-deferred). Slot uniqueness PK prevents two items in one slot |
| **Loot commit** (pickup of an eligible drop) | `char`: insert `inventory_slot` / `item_instance` (auto-merge into an existing stack first, INVENTORY §2) | Synchronous; the roll was already audit-logged (§3.4). Refused if `char` is unreachable (BACKEND §8) rather than accepting an unsaved item |
| **Enhancement attempt** | audit-first (roll) → `char`: `item_instance.enhance_level` (on success) + `soft_pity_fails` (reset/increment) + one emberstone `qty−1`; `wallet`: fee `delta` + `wallet_ledger` (`enhancement_fee`) | One `char`+`wallet` txn. Stone + fee consumed on success **and** fail (ENHANCEMENT §2). No "reroll until success" — one roll, one commit (PERSISTENCE §7) |
| **Two-party trade swap** | `char`: both sides' `inventory_slot`/`item_instance.holder`; `wallet`: both balances + two `wallet_ledger` rows (`trade_in`/`trade_out`); `social`: `trade_log` insert | One txn across all three schemas — both offers change hands or neither (TRADING §3). Wallet-cap check pre-commit (TRADING §3). The co-location decision (§2) is what makes this atomic without 2PC |
| **Market list** | `char`: remove seller `inventory_slot`, set `item_instance.holder=NULL`; `wallet`: listing-fee `delta` + ledger (`market_list_fee`); `social`: insert `market_listing(status=active)` | One txn; the item is in durable escrow the instant it leaves inventory (MARKET) |
| **Market buy** | `wallet`: buyer `delta` (`market_purchase`) + seller `delta` (`market_proceeds`, minus fee) + ledger rows; `char`: `item_instance.holder=buyer` + insert buyer `inventory_slot`; `social`: `market_listing.status=sold` | One txn. Proceeds may instead route via mail (`10_systems/social/MARKET.md`/`MAIL.md` unresolved OQ) — either path is a Postgres write in the same commit; not decided here |
| **Market cancel / expire** | `social`: `status=canceled\|expired`; `char`: return `item_instance` to seller inventory | One txn (expiry runs as a scheduled sweep, §5) |
| **Mail send (with COD)** | `social`: insert `mail`; `char`: attachment `item_instance.holder=mail`; `wallet`: `shards_attached` + send-fee debit + ledger | One txn; attachment/`shards` escrowed durably until claim/return (MAIL) |
| **Mail claim** | `wallet`: recipient `cod_amount` debit + sender `cod_amount` credit + `shards_attached` credit + ledger; `char`: attachment `item_instance.holder=recipient` + insert `inventory_slot`; `social`: `mail.status=claimed` | One txn; claim needs inventory room and the COD `shards` up front (MAIL) — checked pre-commit |
| **Mail expiry return** | `char`+`wallet`+`social`: attachment + `shards_attached` back to sender, `status=expired_returned` | One txn; scheduled sweep (§5). Nothing destroyed (MAIL, PILLARS P2) |
| **Level-up / quest turn-in** | `char`: `character_progress` (± `character_stats` free points, `quest_state`, `inventory_slot` for item rewards); `wallet`: reward `delta` + ledger | One txn per milestone; see §5 (immediate) |
| **Guild create / roster / crest / MOTD op** | `wallet`: fee debit + ledger (`guild_fee`); `social`: `guild` / `guild_member` rows | One `wallet`+`social` txn where a fee applies (GUILD §1/§4/§5), else `social`-only |

## 5. Write cadence

Two write classes, mapping `10_systems/PERSISTENCE.md` §6's solo autosave triggers onto server-side
triggers.

**Immediate (synchronous, transactional) writes** — committed within their own §4 transaction and
acknowledged to the client only on commit. Anything that moves value, crosses the account-to-account
boundary, or is a milestone that must never be lost: `shards` change, any item gain/loss (loot commit,
trade, market, mail), enhancement result + fee, quest turn-in reward, level-up, bind-point set
(`10_systems/DEATH_PENALTY.md` §4), and all guild/market/mail/trade state. These are the "transactional
events"; a crash cannot lose a committed one (`70_integrations/BACKEND_ARCHITECTURE.md` §8 — re-route to
last **persisted** point).

**Checkpoint (batched) writes** — the mutable-but-reconstructible live-session state, flushed to
`session_snapshot` (§3.1) on a cadence, never per event: current `life`/`essence`, `exp_into_level`
between level-ups, skill cooldown remainders (in-memory truth per `70_integrations/BACKEND_ARCHITECTURE.md`
§5), and active status-effect timers/stacks (`10_systems/STATUS_EFFECTS.md`; "character DB on save" per
§5). **Position/velocity is never persisted mid-run** (`10_systems/PERSISTENCE.md` §4). On a crash the
player resumes from the last checkpoint, losing at most one interval of `exp_into_level` and shedding
transient status timers — exactly `70_integrations/BACKEND_ARCHITECTURE.md` §8's disposable-`shared`
guarantee.

| `10_systems/PERSISTENCE.md` §6 solo trigger | Server-side trigger | Class |
|---|---|---|
| Level-up | Level-up transaction | Immediate |
| Quest turn-in | Turn-in transaction | Immediate |
| Map/zone transition | Checkpoint flush of `session_snapshot` at the transition | Checkpoint (natural low-risk point) |
| Periodic timer, every 60 s | Per-active-character periodic checkpoint flush — the interval is THIS doc's write-cadence value (per `70_integrations/GAMEPLAY_SIMULATION.md`'s own boundary statement): **60 s**, matching `10_systems/PERSISTENCE.md` §6's solo backstop; retune on load telemetry | Checkpoint (backstop) |
| Clean application quit | Clean logout: final checkpoint flush + session release | Checkpoint + immediate |
| *(no solo analog)* | Trade swap / market / mail / enhancement / guild op | Immediate (value transfer; solo has no second party) |
| *(no solo analog)* | Scheduled sweep: mail/market expiry return | Immediate transaction per expired row |

Skill cooldowns and active status effects therefore live in the session cache during play and reach
Postgres only on a checkpoint or logout, matching `70_integrations/BACKEND_ARCHITECTURE.md` §5's
"cooldowns in-memory (ETS/Redis)" and "status effects → character DB on save".

## 6. `save_version` & schema migration in the live-DB world

`10_systems/PERSISTENCE.md` §8 fixes the law; this is its live-database realization.

- **Two version layers.** (a) A **schema version** on the database itself (a `schema_migrations`
  ledger; the concrete framework is `30_engineering/ENGINEERING_STANDARDS.md`'s coding-pass item,
  cited never restated). (b) A per-row `save_version` on `char.character`, carried forward so an
  imported solo save (`10_systems/PERSISTENCE.md` §9) and a live-born row share one versioning lineage.
- **Forward-only migrations at deploy.** Migrations run before the new build serves any row; additive
  migrations (new columns/tables) are the norm; a destructive migration is gated and reviewed, never a
  silent drop.
- **Unknown-field law.** No loader silently ignores a column/field it does not recognize
  (`10_systems/PERSISTENCE.md` §8 — an unknown field is a migration bug, not ignorable input). This is
  the live analog of the solo save's "no dropped field" rule.
- **Forward-version refusal.** A server node whose code predates the DB's schema version — or an import
  whose solo `save_version` is newer than the live schema — **refuses to serve/import** (fails closed)
  rather than truncating, exactly as `10_systems/PERSISTENCE.md` §8 refuses a future `save_version`.
- **Import path.** The one-way offline→online import (`10_systems/PERSISTENCE.md` §9,
  `70_integrations/ACCOUNTS_AUTH.md` §2) migrates the solo save's `save_version` up to the live schema
  as part of its validation pass; that validation pass itself is `10_systems/PERSISTENCE.md` §9's open
  item, not re-decided here.

## 7. Backup & recovery

Posture per store; concrete cadence numbers, retention windows, and the hosting/failover topology are
**owner-priced** (`70_integrations/BACKEND_ARCHITECTURE.md` §3/§10 Open Questions — cited, not
duplicated).

- **PostgreSQL cluster (`char`/`wallet`/`social`).** Continuous WAL archiving for **point-in-time
  recovery (PITR)**, plus periodic base snapshots. PITR is the primary guarantee because it can target
  the instant before a bad deploy or corruption. The `wallet` ledger's recoverability is the strictest
  case — money — and the append-only `wallet_ledger` (§3.2) means a restored balance is verifiable by
  re-summing deltas.
- **Append-only RNG audit log.** Already write-once/immutable on partitioned storage; its durability
  is replication, its retention window and storage tier are the owner cost decision above. Not part of
  the transactional backup/PITR set.
- **Redis / ETS cache.** Not backed up — it is not a source of truth
  (`70_integrations/BACKEND_ARCHITECTURE.md` §3). On restart it is rebuilt from Postgres; in-flight
  live-trade escrow and party state are lost by design (a dropped trade session leaves both sides'
  items untouched, `10_systems/social/TRADING.md` §3).
- **Restore drill expectation.** A periodic, rehearsed restore-from-backup: recover the Postgres
  cluster to a scratch instance from PITR, verify each `wallet` balance equals `Σ wallet_ledger.delta`,
  and confirm a sample of `char.character` rows load at their `save_version`. Cadence is live-ops; a
  backup never restored is not a backup.

## 8. Failure modes & degradation

Per `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`, every external dependency lists a failure
mode. These extend `70_integrations/BACKEND_ARCHITECTURE.md` §8 with the storage-tier specifics; that
table's stances (fail-loud in dev, fail-safe in prod; refuse rather than fabricate) hold unchanged.

| Dependency | Failure mode | Degradation / stance |
|---|---|---|
| PostgreSQL cluster (mid-transaction) | Failure during a §4 commit | The transaction **rolls back** whole; the action is refused; no partial or minted/lost value is ever visible (`10_systems/social/TRADING.md` §3). Client shows failure, retries |
| `char` schema unreachable | Saves fail | Block state-mutating actions (loot commit, level-up, turn-in); read-only play may continue briefly (BACKEND §8) |
| `wallet` schema unreachable | Ledger writes fail | Freeze `shards` faucets/sinks and all trade/market/mail value transfer; combat/movement continue (BACKEND §8) |
| `social` schema unreachable | Social writes fail | Guild/market/mail degrade to read-only or unavailable; core play unaffected (BACKEND §8). Schema+role isolation (§2) is what confines the blast radius here |
| Append-only audit log unwritable | A gated roll cannot be recorded | **Block** the roll — enhancement, drop, combat — before its Postgres consequence (audit-first, §4). An ungated roll is worse than a paused one (PERSISTENCE §7, BACKEND §8) |
| Seeded RNG service unreachable | No verifiable roll | Same stance: block every roll it gates (BACKEND §8) |
| Redis unreachable | Cross-node coordination degrades | BEAM-native ETS covers in-node cooldown/escrow/session state; a live trade (single-node session) still commits; cross-node presence may lag until recovery (BACKEND §8). Truth is untouched (cache is never truth) |
| Checkpoint write fails (§5) | A `session_snapshot` flush errors | Session continues on the last good checkpoint; the flush is retried next interval; a failed checkpoint never blocks movement or combat — only transactional writes (§4) can block an action |

## 9. Secrets & implemented-when

- **Secrets are environment-managed, never committed** (`70_integrations/BACKEND_ARCHITECTURE.md` §10;
  `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`). Database credentials, the per-schema role
  passwords, Redis auth, and the audit-log store's write credentials live in environment-managed
  configuration, set and rotated in ops — never in this tree.
- **Implemented when:** a live authoritative server exists — after the interim solo build ships and the
  owner greenlights it (`70_integrations/BACKEND_ARCHITECTURE.md` §6, §10;
  `10_systems/PERSISTENCE.md` §5). Until then the solo `GameState` facade writes a local file
  (`30_engineering/ENGINEERING_STANDARDS.md` owns that format); this schema is the networked backing
  store it becomes, dormant by design.

## Open Questions

- **Runtime PK formats.** This doc confirms `10_systems/social/GUILD.md`'s `guild_<NNNNNN>` and uses
  server-minted surrogates for `item_instance`/`market_listing`/`mail`/`trade_log`. The
  **character-identity** PK format is `70_integrations/ACCOUNTS_AUTH.md`'s to fix (that doc is revised
  in parallel); this doc stores whatever it mints and keys `char.character` on it — no independent
  scheme is invented here. None of these are `docs/ID_REGISTRY.md` authored-content IDs (§2).
- **Hosting / managed-service / region / failover** for the Postgres cluster and audit-log store are
  owner-priced and already filed in `70_integrations/BACKEND_ARCHITECTURE.md` Open Questions (§3/§10) —
  cited, not reopened. Single-region, single-writer wallet primary is assumed at launch (BACKEND §1/§8).
- **RNG audit-log retention window and storage tier** (§3.4) are owner-priced — pointer to
  `70_integrations/BACKEND_ARCHITECTURE.md` §3 Open Questions, not decided here.
- **Market-proceeds delivery** (wallet credit vs `10_systems/social/MAIL.md`) is unresolved in the
  `10_systems/social/MARKET.md`/`MAIL.md` stubs; §4 supports either as a same-commit Postgres write and
  does not force the choice.
- **Solo→online import validation** (`10_systems/PERSISTENCE.md` §9) — the re-derive/range-check
  pass is now designed in `70_integrations/ACCOUNTS_AUTH.md` §2.4 (this wave); §6 only fixes that
  import runs the schema-version migration and refuses a forward-version save. Not re-decided here.
- **Per-role connection-pool caps.** The schemas-in-one-database design (§2) preserves write
  isolation, not resource isolation — WAL, checkpointer, autovacuum, and the connection budget are
  shared. The mitigation is per-role connection-pool limits at the pooling layer (e.g. per-role
  PgBouncer pools); which pooler and what caps is an ops/owner-priced item alongside the
  `70_integrations/BACKEND_ARCHITECTURE.md` hosting decision.
- **Concurrency-control discipline inside §4 transactions.** §4 fixes *what* commits atomically;
  the *how* of concurrent access — explicit row locks (`SELECT … FOR UPDATE` on the touched
  `inventory_slot`/`item_instance`/`wallet` rows before validate-then-write), a deterministic
  cross-transaction lock order to prevent deadlock, and/or a serializable isolation level with
  retry — is not yet fixed. The slot-uniqueness PK and the append-only ledger already make the
  worst races fail closed, but the two-party swap and market-buy paths touch multiple rows across
  schemas and need one declared discipline before implementation (owner's backend security
  checklist, 2026-07-24 — anti-duplication requirement;
  `docs/phase_reports/BACKEND_CHECKLIST_AUDIT_2026-07-24.md`). Same home should state the
  (assumed, currently unwritten) rule that all SQL is parameterized/prepared — never
  string-concatenated. Owner: this doc at its next revision, with the coding pass.
- **Account/credential store placement.** The password hash and account root
  (`70_integrations/ACCOUNTS_AUTH.md` §8) are grouped under the character DB by
  `70_integrations/BACKEND_ARCHITECTURE.md` §5; whether they sit in the `char` schema or a dedicated
  `account` schema owned solely by the auth-service role is a hardening detail to settle jointly with
  that doc's revision — default: a separate `account` schema, auth-service-write-only.
