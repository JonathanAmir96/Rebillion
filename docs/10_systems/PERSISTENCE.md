# PERSISTENCE.md — Save Model & Authority Taxonomy

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, 10_systems/STATS.md,
10_systems/LEVELING.md, 10_systems/INVENTORY.md, 10_systems/ITEMS.md, 10_systems/ECONOMY.md,
10_systems/DROPS.md, 10_systems/ENHANCEMENT.md, 10_systems/SKILL_SYSTEM.md,
10_systems/STATUS_EFFECTS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/QUESTS.md,
10_systems/DEATH_PENALTY.md, 10_systems/CONTROLS.md, 10_systems/CAMERA.md, 10_systems/HUD.md,
10_systems/social/PARTY.md, 10_systems/social/GUILD.md, 10_systems/social/MARKET.md,
30_engineering/ENGINEERING_STANDARDS.md, 70_integrations/GAMEPLAY_SIMULATION.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for **what is saved, who owns the truth, and how the interim solo build stores it**.
Every other system doc in this tree already assumes a three-way `authority` tag
(`server`/`client`/`shared`) and cites this doc for it (`00_vision/PILLARS.md` P6); this is that
tag's sole definition. It does not re-derive any system's *values* (those stay owned where they
already are) — it only says who is allowed to consider a value true, and how the solo build
stores it pending a real server.

## 1. The authority taxonomy (three tags, used by every schema)

Every field in every future `20_schemas/*.schema.md` entry carries exactly one of these three
tags. There is no fourth tag; a field that seems to need one is a modeling error, not a gap here.

| Tag | Meaning |
|---|---|
| `server` | The server is the sole source of truth once live. The client keeps an advisory/simulated copy that may be silently corrected on sync. The client may never mint, self-assign, or re-roll a `server` value. |
| `client` | The client is the sole authority, always. Never synced to or validated by a server, even once one exists — purely local presentation/preference state. |
| `shared` | Both sides track it continuously; the client predicts for responsiveness and the server reconciles (§4). |

## 2. `authority: server` — the truth ledger

| Data | Owning doc |
|---|---|
| Character identity (`nickname`, `job`, appearance, roster slot) | `70_integrations/ACCOUNTS_AUTH.md` §2/§5 (player-facing flow: `10_systems/ACCOUNT.md`) |
| `level` / `exp` / `exp_into_level` | `10_systems/LEVELING.md` |
| Primary stats, free-point allocation, derived-stat recompute | `10_systems/STATS.md` §7–§8 |
| Inventory contents (all 3 tabs) + bank | `10_systems/INVENTORY.md` |
| Equipment worn, `enhance_level`, soft-pity counters | `10_systems/ITEMS.md`, `10_systems/ENHANCEMENT.md` §3/§6 |
| `shards` wallet | `10_systems/ECONOMY.md`, `10_systems/INVENTORY.md` §3 |
| Quest flags / step progress / completed set | `10_systems/QUESTS.md` |
| Skill ranks, respec state, cooldown timers | `10_systems/SKILL_SYSTEM.md` |
| Active status effects (buffs/debuffs, timers, stacks) | `10_systems/STATUS_EFFECTS.md` |
| Drop rolls, loot tag/ownership timers | `10_systems/DROPS.md` §7/§9 |
| Combat resolution (hit/crit/damage/mitigation) | `10_systems/COMBAT_FORMULA.md` §1 |
| Bind point | `10_systems/DEATH_PENALTY.md` §4 |
| Charter state (season index/day, task progress, `charter_mark` balance, charter level, track, claimed-reward set) | `10_systems/BATTLE_PASS.md` §7 (excluded from the §9 import) |
| Capsule state (pull rolls, `capsule_pity` counter, weekly purchase-cap counter, SKU entitlements/receipts) | `10_systems/GACHAPON.md` §7 (excluded from the §9 import) |
| Guild / party / trade / mail / market state | `10_systems/social/GUILD.md`, `10_systems/social/PARTY.md`, `10_systems/social/TRADING.md`, `10_systems/social/MAIL.md`, `10_systems/social/MARKET.md` |
| Collection log progress (discovery state, revealed-drop flags, claimed-reward flags) | `10_systems/COLLECTIONS.md` §8 |
| Cosmetic ownership + appearance loadout | `10_systems/COSMETICS.md` §7 |
| Time-gated counters (daily/weekly resets) | this doc §2.1 |

Every entry above already reads (in its owning doc) "server-authoritative... solo client
simulates/holds an advisory copy... corrected on sync" — this doc is simply the one place that
phrasing is defined instead of repeated.

### 2.1 Time boundaries — daily and weekly resets

Several systems grant time-gated rewards — the raid **first-clear-of-the-day** bonus
(`10_systems/social/RAID.md` §6, `10_systems/LEVELING.md` §3.1) and the **weekly guild goal**
(`10_systems/social/GUILD.md`) — and need one shared, server-authoritative definition of "a day"
and "a week" so every feature resets together:

- **Day boundary:** a fixed **daily reset at 00:00 UTC**. All per-day flags (e.g. each raid's
  first-clear-of-the-day flag, per character) clear at that instant, server-side. UTC (not local
  time) is chosen so a fixed-time global reset is unambiguous and un-gameable by clock changes;
  revisit per-region local resets if the game ships timezoned shards (Open Questions).
- **Week boundary:** the daily reset on a fixed **weekly anchor day** (first-pass **Monday 00:00
  UTC**); weekly counters (guild-goal progress) clear then.
- **Where the flags live:** per-character day/week flags and counters are `authority: server`
  fields on the `GameState` facade (§5) in the solo build — the client reads them, the server
  (future) owns the reset tick. The solo build applies the reset locally on load using the
  save's stored last-reset timestamp vs. the current clock.

Concrete reward numbers stay in each owning doc; this section owns only *when* the boundaries fall.

## 3. `authority: client`

| Data | Owning doc |
|---|---|
| Raw input state | `10_systems/CONTROLS.md` |
| Keybind map | `10_systems/CONTROLS.md` §5 |
| Camera position/mode/shake state | `10_systems/CAMERA.md` §9 |
| UI preferences (window layout, toggle states, tracked-quest selection, damage-number visibility) | `10_systems/HUD.md`, `10_systems/QUESTS.md` |

`client` data is never validated or overwritten by a server, even in the live build — it is
purely local and does not represent anything the game world needs to agree on.

## 4. `authority: shared` — position/velocity

Position and velocity are the one pairing tracked by both sides at once: the client moves the
character immediately on input for responsiveness (P1, snappy), and — once a server exists — the
server periodically reconciles, accepting the client's position if it is plausible against its
own simulation and correcting it otherwise. The interim solo build has no server to reconcile
against, so position/velocity are effectively client-simulated only for now; they are still
tagged `shared` because that is their permanent shape once networked. The concrete reconciliation
algorithm (tolerance envelope, correction/snap method, speed-cap displacement margin) is owned by
`70_integrations/GAMEPLAY_SIMULATION.md` §2 (Phase I backend wave); this doc keeps owning only
the `shared` tag's meaning.

## 5. The solo build: a `GameState` facade over a local save

`00_vision/PILLARS.md` P6 requires the client to be written against a server-authoritative
*boundary* even while running solo. Concretely: every system reads and writes persisted state
through one **`GameState` facade** rather than touching a save file or a future network call
directly, so swapping the backing store later (local file → networked client) never requires
changing calling code. This doc fixes the **data model** (§1–§4) and the **cadence** (§6) that
facade must serve; the GameState save-facade autoload is established in
`30_engineering/ENGINEERING_STANDARDS.md`; its detailed interface/class design is coding-pass
territory.

## 6. Save slots & autosave cadence (solo build)

- **4 character save slots** per install (quota owned by `70_integrations/ACCOUNTS_AUTH.md`
  §2.2, raised 3→4 by owner directive 2026-07-24 — this doc only mirrors the count; the
  player-facing roster flow is `10_systems/ACCOUNT.md`), each an independent character
  (own `server`-tagged state, §2). Keybinds and UI prefs (§3) live in one shared
  **account-level** client config file, independent of the slots, so rebinding a key is not
  per-character.
- **Autosave triggers** (write the active slot's `GameState` to disk):

| Trigger | Rationale |
|---|---|
| Level-up | A milestone worth never losing to a crash |
| Quest turn-in | Same — a completed reward should be durable immediately |
| Map/zone transition | A natural, low-risk save point between activities |
| Periodic timer, every 60 s | Backstop for long uninterrupted sessions in one zone |
| Clean application quit | Final flush |

File format and on-disk layout are `30_engineering/ENGINEERING_STANDARDS.md`'s; this doc fixes
only the slot count and the trigger table above.

## 7. What is never trusted from the client

Even with no live server to defend against, the `GameState` facade enforces these locally so the
same code path holds unchanged once a real server exists — the solo build is a rehearsal for the
boundary, not an exception to it:

- No self-assigned drop `rarity`/`qty`/pool result (`10_systems/DROPS.md` §9).
- No minted items or `shards`, and no self-assigned drop the character wasn't tagged for
  (`10_systems/INVENTORY.md` §9).
- No client-recomputed derived stat treated as truth over the facade's stored value
  (`10_systems/STATS.md` §8).
- No "reroll until success" on enhancement attempts (`10_systems/ENHANCEMENT.md` §6).
- No skipped `essence_cost`/cooldown/prereq gate on skill or quest actions
  (`10_systems/SKILL_SYSTEM.md` §8, `10_systems/QUESTS.md` §9).

## 8. `save_version` — migration/versioning field

Every save file carries a `save_version` integer. On load, if it is lower than the build's
current version, a migration step runs (owned by `30_engineering/ENGINEERING_STANDARDS.md`) before
any system reads through the facade; an unrecognized *future* `save_version`
(the file is newer than the running build) refuses to load rather than silently truncating data.
No system may drop an unrecognized field silently — an unknown field is a migration bug, not
ignorable input.

## 9. Offline → online migration (one-way import)

Intent: a character built in the interim solo build should be importable **once** into a future
live server, never the reverse (a live character cannot be exported back down into a solo save).
This is a real risk, not a formality: a local save file is, unlike a real server, editable by
whoever holds it, so a naive "trust the file" import would let a hand-edited save inject an
illegally-progressed character into the live economy. This doc fixes the *intent* only; the
validation/sanitization pass an import must run is unresolved (Open Questions) — no import design
is assumed safe by default.

## Open Questions

- The offline→online import's validation pass is the most important open item here: does it (a)
  re-derive `level` from raw cumulative `exp` and re-simulate stat growth rather than trusting
  stored derived values, (b) range-check every item ID/`enhance_level`/`rarity` against
  `docs/ID_REGISTRY.md` and `10_systems/ITEMS.md`/`10_systems/ENHANCEMENT.md` legal bounds, or (c)
  restrict import to a subset (e.g., cosmetic/account state only, character re-leveled live)?
  Not decided — owner: this doc, jointly with whatever future server-onboarding doc exists.
- ~~Position/velocity reconciliation algorithm (§4) is explicitly deferred — out of this run's
  scope per `00_vision/SCOPE.md`; do not design it prematurely here.~~ **Resolved 2026-07-24:**
  owned by `70_integrations/GAMEPLAY_SIMULATION.md` §2 (accept-if-plausible tolerance envelope,
  error-blend vs hard-snap correction, speed-cap displacement margin — Phase I backend wave).
- Whether the `shards` wallet and bank are per-character (assumed, matching
  `10_systems/INVENTORY.md` §3/§7's default) or ever account-shared is confirmed here as
  **per-character** for the solo build and the interim server; an account-shared purse/vault is a
  later, explicitly opt-in addition, not a launch item.
- `save_version`'s migration framework (§8) has no concrete implementation yet; flagged for
  `30_engineering/ENGINEERING_STANDARDS.md` (authored and locked per CLAUDE.md Law 5), which
  establishes the GameState save facade but does not yet specify the concrete migration
  framework; the migration step is deferred to the coding pass.
- Cloud-save / multi-device sync for the solo build is not addressed; assumed local-disk-only
  until a server exists.
- Whether a corrupted/unreadable save slot should attempt partial recovery or hard-fail to a
  "create new character" prompt is unresolved.
