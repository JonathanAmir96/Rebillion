# RAID.md — Raid System (Instanced Co-op Runs)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/LEVELING.md, 10_systems/COMBAT_FORMULA.md, 10_systems/DROPS.md, 10_systems/ITEMS.md,
10_systems/QUESTS.md, 10_systems/SPAWN.md, 10_systems/DEATH_PENALTY.md,
10_systems/STATUS_EFFECTS.md, 10_systems/PERSISTENCE.md, 10_systems/social/PARTY.md,
15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, docs/VALIDATION.md

Owner doc for the **raid**: the instanced, party-scoped co-op run — its entry rules, stage-chain
structure, failure/re-entry model, lockout, and rewards policy. Map/boss **placement** is
`docs/WORLD_PLAN.md`'s; party membership, exp-share, and loot-share are
`10_systems/social/PARTY.md`'s; raid-boss `exp` and drop-table treatment are
`10_systems/LEVELING.md` §3 and `10_systems/DROPS.md`; death/release/re-entry mechanics are
`10_systems/DEATH_PENALTY.md` §5.3; instance spawn allocation is `10_systems/SPAWN.md` §7. This
doc consumes all of those and restates none — it owns only what a raid *is* and the rules that
bind its pieces together.

## 1. Terminology law

**"Raid" fully replaces the legacy "party quest" / "PQ" phrasing across the tree.** The token
family is `raid_<name>` (replacing the retired `pq_<name>` family); the legacy tokens and
phrasing are invalid in all docs and content once the v3 revision lands, and
`docs/VALIDATION.md` §2's referential checks enforce the rename. This paragraph is the single
statement of that law — sibling docs adopt the new term by reference, never by re-declaring it.

Token minting: `raid_<name>` tokens are **minted in `docs/ID_REGISTRY.md`** (the range owner,
same pattern as every other ID family); this doc is the concept owner. A raid that is not in the
registry does not exist.

## 2. The raid roster (four raids, two arcs)

Placement (which maps, which region, which boss slot) is owned by `docs/WORLD_PLAN.md`; this
table lists the roster by reference and fixes the **rule-side** columns (band, party size):

| Token | Name | Level band | Party | Stage chain | Finale arena | Finale boss | Bonus room (§6.E) |
|---|---|---|---|---|---|---|---|
| `raid_undervault` | Undervault Heist | 15–22 | 3–6 | `map_038`–`map_040` | `map_042` | `mob_027` | `map_325` |
| `raid_mainspring` | Mainspring Trial | 32–40 | 3–6 | `map_195`–`map_197` | `map_200` | `mob_150` | `map_326` |
| `raid_deepfrost` | Deepfrost | 45–55 | 3–6 | `map_240`–`map_242` | `map_244` (Frostpeak Isle) | `mob_178` | `map_327` |
| `raid_voidtide` | Voidtide | 70–80 | 3–6 | `map_320`–`map_322` | `map_324` (Voidshore) | `mob_234` | `map_328` |

Every raid runs the same shape: **three stages → finale arena → bonus room**, on one 30-minute run
clock (§4.1) with a separate 90-second bonus clock (§6.E). The per-raid *signature* that keeps the
three stages from feeling interchangeable is §4's.

The two arc-1 raids end at **existing region bosses** (no extra boss slots — their finale arenas
double as the regions' open boss arenas, `docs/WORLD_PLAN.md` R2/R8). The two arc-2 raids and
their bosses live on the new second-arc islands; their names, region sections, and boss
identities are `docs/WORLD_PLAN.md`'s (cite the mob IDs above, nothing more).

## 3. Entry

- **Raid herald.** Each raid is entered through a **raid herald** NPC standing at the raid's
  staging area — the map its stage chain branches from (placement per `docs/WORLD_PLAN.md`;
  concrete NPC IDs per each region's NPC block in `docs/ID_REGISTRY.md`). The herald is the
  only entrance to the stage chain; the stage maps have no open portals.
- **Intro/handler quest pattern.** Each raid carries an intro quest (unlocks the herald dialog,
  explains the run) and a handler quest (a **one-time** first-clear turn-in that closes the intro
  arc), both authored as ordinary `10_systems/QUESTS.md` quests under that doc's §7
  one-time-per-character launch policy — **repeat clears are not a quest**: every reward for a
  repeat clear (stage/completion `exp` grants, the first-clear-of-the-day bonus, `raid_token`
  income, loot) flows through this doc's own clear mechanics (§5–§6) and
  `10_systems/LEVELING.md` §3.1, with no re-acceptable quest wrapper. (Resolved 2026-07-24 —
  this bullet previously called the handler "repeatable," contradicting QUESTS §7.) Arc-1 slots
  are `quest_087`–`090` (`docs/ID_REGISTRY.md`); arc-2 raids mint theirs in the registry the
  same way.
- **Level band gate — hard, both ends.** Every member's `level` must lie inside the raid's band
  (inclusive) at instance creation. A member who levels past the ceiling mid-run is not ejected;
  the gate applies only at entry.
- **Party size 3–6.** Entry requires a party (mechanics, roster, and leadership entirely
  `10_systems/social/PARTY.md`'s) of 3–6 members, all on the herald's map. The **leader**
  initiates entry through the herald; the whole party is moved into the fresh instance together.
- **Channel claim — one party per raid, per channel.** A raid is **claimed** on the channel its
  party entered from (`70_integrations/WORLD_CHANNELS.md` §2 owns the claim's server-side shape).
  While `raid_undervault` is claimed on channel 3, no second party on channel 3 may enter it —
  they must switch channels to find a free one, or wait. The claim is **per raid token, not per
  raid map**: a claim on `raid_undervault` never blocks `raid_mainspring` on the same channel.
  - **The instance is still private.** This is a *gate on entry*, not a shared map — the party
    that claims the raid still receives its own instance (§4), so the claim never exposes a run to
    another party's spawns, loot, or wipes. It is scarcity at the door, not a contested dungeon.
  - **Claim lifetime:** taken at instance creation, released the moment the instance dissolves —
    on clear, on any §5 wipe cause, or on the instance emptying. A disconnected party releases its
    claim on the same 60 s disconnect grace that governs the instance
    (`70_integrations/WORLD_CHANNELS.md` §2), so a dropped group cannot strand a channel.
  - **The herald reports it.** Standing at a herald on a channel where the raid is claimed gives a
    refusal line naming the state ("the vault is already spoken for"), not a silent failure — the
    player is told to change channels, which is the intended loop.
  - **Why a claim and not a queue:** channel-hopping to find a free raid is the intended social
    texture (the MapleStory-inspired feel this system is named for), and it stays legible — a
    player can see and act on it. A queue would hide the same scarcity behind a wait with no
    player agency. Whether scarcity is wanted *at all* once the game is live is flagged in Open
    Questions; it is a lever, not a law.
- No entry fee at this revision (a `shards` fee is an economy lever, not assumed — see Open
  Questions).

## 4. Instancing & the stage chain

A raid run is a **party-instanced stage chain ending in a finale arena instance**: entering
allocates a private copy of the stage maps and finale arena to the entering party alone
(`10_systems/SPAWN.md` §7's allocation model; instance state is `authority: server` per §8
below). Party composition `N` is fixed at instance creation and never re-scales mid-run — same
no-hidden-re-scaling law `10_systems/social/PARTY.md` §6 fixes (`00_vision/PILLARS.md` P1).

**Stages are sequential and one-way forward.** Each stage map has a locked exit portal that
opens when the stage objective completes; the party advances together. Clearing the last stage
opens the finale arena, where the raid boss waits.

**Stage-clear objective patterns.** Stage objectives are built only from
`10_systems/QUESTS.md` §3's fixed verb set (`kill` / `collect` / `talk` / `reach`) plus
`quest_object` interactables (`15_maps_system/MAP_INTERACTABLES.md`) — no raid-only verbs:

| Pattern | Built from | Shape |
|---|---|---|
| Kill gate | `kill` | Defeat a required count, or named elite(s), spawned for the instance |
| Collect-and-deposit | `collect` + `quest_object` | Gather stage items (mob drops or interactable nodes) and deposit them at a stage device |
| Puzzle | `reach` + `quest_object` | Members trigger zones or operate interactables in the right order or simultaneously — the co-op platforming stage |

There is no escort verb in `10_systems/QUESTS.md` and therefore **no escort stages** — the verb
set is fixed; a raid may not invent one.

**No-repeat law.** A raid's three stages must use **three different patterns** — one kill gate, one
collect-and-deposit, one puzzle, in whatever order that raid's signature calls for. A raid that
runs the same pattern twice is invalid content (`docs/VALIDATION.md` §2). This is what keeps a run
from reading as three rooms of the same fight.

**Signature mechanic (one per raid).** Beyond the pattern, each raid carries a **signature** — a
single environmental rule that colors all three of its stages and gives the raid its identity. A
signature is built from the same fixed verb set and `quest_object`/`reactor` interactables; it
invents no new verb and no new interactable type. The four signatures and the stage line-ups they
produce:

| Raid | Signature | Stage 1 | Stage 2 | Stage 3 |
|---|---|---|---|---|
| `raid_undervault` | **The haul** — carried stage items slow their carrier and draw the vault's wardens; the party must cover whoever is loaded | `map_038` the Sunken Larders — *kill gate* | `map_039` the Flooded Ledger Vaults — *collect-and-deposit* | `map_040` the Grain King's Approach — *puzzle* (simultaneous levers) |
| `raid_mainspring` | **The beat** — hazards fire on a fixed clockwork cycle, identical every run; the stage is learned, not out-statted | `map_195` the Sundered Cogworks — *puzzle* (plates in beat order) | `map_196` the Flywheel Vault — *collect-and-deposit* | `map_197` the Escapement Antechamber — *kill gate* |
| `raid_deepfrost` | **The thaw** — ice gates and frozen footing yield only to heat carried brazier to brazier | `map_240` the Sundered Gate — *collect-and-deposit* (embers to braziers) | `map_241` the Frozen Cistern — *puzzle* (melting/refreezing platforms) | `map_242` the Rimewyrm's Antechamber — *kill gate* |
| `raid_voidtide` | **The tide** — the water level cycles on a timer; footing, reachable ledges, and what spawns all change with it | `map_320` the Sunken Approach — *puzzle* (cross at low tide) | `map_321` the Eclipse Gallery — *kill gate* (spawns per surge) | `map_322` the Last Approach — *collect-and-deposit* (gathered between surges) |

Map placement is `docs/WORLD_PLAN.md`'s and the map IDs above are cited from it, never minted here.
Concrete per-stage numbers (required counts, spawn sets, lever counts, cycle periods) are Phase D
content authored against the pattern + signature this table fixes.

### 4.1 The run clock

A raid run is **timed end to end** — one clock for the whole run, not one per stage:

```
raid_run_timer = 30 min          # all four raids, first pass
```

- **Starts** the moment the party is placed in stage 1, and runs continuously across every stage
  and the finale arena. It does **not** pause between stages, on death, or during the boss fight.
- **Expiry is a wipe**, on §5's terms exactly — the attempt ends, the instance dissolves, stage
  progress does not persist, and there is **no** penalty beyond `10_systems/DEATH_PENALTY.md`'s
  ordinary death costs. Retry immediately from the herald.
- **Stops** on the finale-boss kill. The bonus stage (§6.E) runs on its own separate clock and is
  never charged against this one.
- **The boss enrage timer nests inside it.** `10_systems/COMBAT_FORMULA.md` §13.3's 12-minute
  enrage is unchanged and starts when the finale arena is entered; whichever of the two clocks
  expires first ends the attempt. Because the run clock never pauses, a party that spends 25
  minutes on the stage chain meets the boss with 5 minutes of run clock, not 12 — the stage chain
  and the boss draw on one budget. That coupling is the point: it makes stage play matter *to* the
  boss fight instead of being a toll paid before it.
- **One clock rather than per-stage clocks** is deliberate: a party may bank time on a stage it
  knows and spend it on one it does not, which is the pacing decision worth having. The budget
  stays legible and identical for every party — no hidden rescaling (`00_vision/PILLARS.md` P1).
- The clock is **server-authoritative** (§8) and drawn by `10_systems/HUD.md` §6.2, with warning
  states at 5:00 and 1:00 remaining.

The 30-minute value is a first pass sized against the ≈25-minute modeled clear (Open Questions) —
about 20% headroom for a party still learning the stages. Flagged for telemetry, not settled.

## 5. Failure, wipe, re-entry & lockout

- **Within an attempt:** individual death, Release, and walk-back re-entry follow
  `10_systems/DEATH_PENALTY.md` §5.3 exactly; the party-side bookkeeping (fallen roster state,
  eligibility while fallen) is `10_systems/social/PARTY.md` §6's. Both are consumed unchanged.
- **Full wipe** — any one of four causes: every member fallen; every member Released/left the
  instance; the **run clock** expiring (§4.1, 30 min); or the finale boss's **enrage timer**
  expiring (`10_systems/COMBAT_FORMULA.md` §13.3 owns that timer and its 12-minute value). In every
  case the attempt ends and the instance dissolves. Stage progress does not persist across
  attempts — a new entry starts at stage 1, on a fresh run clock.
- **Failure is free:** no lockout, no cooldown, no penalty beyond
  `10_systems/DEATH_PENALTY.md`'s ordinary death costs. Retry immediately from the herald.
- **Clear cooldown (default):** after a successful finale-boss kill, each participating
  character carries a **15-minute per-character, per-raid cooldown** before entering a new
  instance of that raid. No daily or weekly lockout — raids are meant to be re-runnable social
  loot runs, and the cooldown exists only to keep clear-chaining from beating field play as a
  `shards`/loot faucet. The pull that actually paces the social rhythm is the **first-clear-of-the-day
  bonus** (§6), not this cooldown — the cooldown is short (down from a prior 30-minute default) so a
  group that wants to keep running together can, while the daily beat is what rewards logging in to
  raid each day. The timer is server-tracked (§8). Tuning is flagged, not settled (Open Questions).
- Disbanding the party or the leader leaving mid-run does not dissolve the instance by itself;
  the instance dissolves when it is empty. Leadership succession inside a run is
  `10_systems/social/PARTY.md` §2's.

## 6. Rewards — raids are the social centerpiece

Design intent: **a raid clear is the social centerpiece — a strong `exp` event, the loot path, and
the only source of `raid_token`-gated exclusive rewards.** The reward package is built to pull
players into grouping **by desire, not by taxing solos** (`00_vision/PILLARS.md` P2/P3): every reward
here is a carrot for the grouped player, and the solo path to every finale boss stays open at reduced
reward (§7). Nothing in a raid is strictly required to progress solo — the exclusive equips are
aspirational side-grades, and the cosmetics carry no stats — so grouping is the **better**, not the
**only**, path. The four reward streams a clear pays:

**A. `exp` — per stage, then a headline clear bonus.** A raid pays `exp` at three moments, all
budgeted and sized by `10_systems/LEVELING.md` §3/§3.1 (magnitudes there, not restated here):
  1. **Stage mobs** pay ordinary per-kill `exp` as the party clears them
     (`10_systems/LEVELING.md` §2–§3), shared per `10_systems/social/PARTY.md` §4.
  2. **Each stage clear** grants a flat `raid_stage_exp` to **every eligible member** (not split)
     the moment that stage's objective (§4) completes — the sub-step reward.
  3. **The finale-boss kill** grants the headline `raid_clear_exp` completion bonus to every
     eligible member (not split) — deliberately the run's **best `exp`** — *on top of* the boss's
     own kill `exp` (`10_systems/LEVELING.md` §3's raid-boss row, split per
     `10_systems/social/PARTY.md` §4).
The stage and clear grants are **flat per-member** (the whole party is rewarded for finishing, not
a pool to divide) — the MapleStory-inspired feel. These grants are an **elective accelerator** that
sits outside `10_systems/LEVELING.md` §4's mandatory source-split, so a raid is an `exp` **event**
that never becomes the mandatory pacing path (P2).

**B. Raid tokens (`raid_token`).** On a **finale-boss clear**, every eligible raid member is
**guaranteed** their raid's `raid_token` (`00_vision/GLOSSARY.md`; per-raid variants
`item_etc_0177` Undervault Seal · `item_etc_0178` Mainspring Cog · `item_etc_0179` Deepfrost Shard ·
`item_etc_0180` Voidtide Pearl, `docs/ID_REGISTRY.md`). The guaranteed grant is a **runtime grant
keyed by entry context** (`10_systems/DROPS.md` §5.4 — one per participating member, raid entry
only; never authored as extra static rows in the boss's drop table,
`20_schemas/drop_table.schema.md` rule 4) and is consumed here, not restated. Tokens are spent at the **Raid Quartermaster** — a vendor NPC
whose item catalog and prices are `10_systems/ITEMS.md`'s and whose placement (the raid staging
towns / Millbrook) is `docs/WORLD_PLAN.md`'s. This doc owns only that the token is guaranteed per
member on a finale clear and that the Quartermaster's exclusive stock is `raid_token`-gated.

**C. Raid-exclusive rewards (the desire pull).** Only the Raid Quartermaster sells these, only for
that raid's `raid_token`, and they exist nowhere else in the game. Per raid:
  - **Two raid-exclusive equips** (`item_equip_0223`–`0230`, two per raid — undervault 0223–24 ·
    mainspring 0225–26 · deepfrost 0227–28 · voidtide 0229–30, `docs/ID_REGISTRY.md`). These are
    **aspirational side-grades, not strictly-required best-in-slot** — the field and boss-unique gear
    (`10_systems/ITEMS.md`, `10_systems/DROPS.md` §5.3) keeps solo play fully viable, and the raid
    equips are a lateral flavor of power, not a gate (P2). Their stats and token prices are
    `10_systems/ITEMS.md`'s; this doc owns only that they are `raid_token`-gated and raid-exclusive.
  - **One raid-exclusive cosmetic + title** (`item_cosmetic_0001`–`0008`, one per raid,
    `docs/ID_REGISTRY.md`). **No stats**, per the cosmetic-only charter
    (`10_systems/MONETIZATION.md`, `00_vision/PILLARS.md` anti-pay-to-win) — pure prestige a grouped
    player wears to show the clear. Catalog and price are `10_systems/ITEMS.md`'s; equip/display
    rules are `10_systems/COSMETICS.md`'s.

**D. First-clear-of-the-day bonus (the daily social beat).** The **first successful clear of a given
raid, per character, per day** (the day boundary — a fixed daily reset at 00:00 UTC — is
`10_systems/PERSISTENCE.md` §2.1's, consumed here by reference) pays a bonus **on top of** the
ordinary A/B grants:
  - **2× that raid's `raid_clear_exp`** completion bonus (the doubled value is
    `10_systems/LEVELING.md` §3.1's — referenced, not restated), and
  - **one bonus `raid_token`** (the same per-raid token as B).
Subsequent same-day clears of that raid pay the normal grants (single `raid_clear_exp`, single
token). There is **no weekly lockout and no clear cap** — this daily beat is the "log in and raid
together" rhythm, a carrot that rewards showing up each day, not a tax that punishes running more.
The first-of-the-day state (per character, per raid) is server-tracked (§8).

**E. The bonus stage (the chance payoff).** On a **raid-entry** finale-boss kill, a portal opens in
the finale arena onto that raid's **bonus room** — a separate instanced map, one per raid
(`map_325` Undervault Cache · `map_326` Mainspring Treasury · `map_327` Deepfrost Hoard ·
`map_328` Voidtide Trove, `docs/ID_REGISTRY.md`). This is the run's chance-based payoff, distinct
from every guaranteed grant above.

- **Raid entry only.** An open-arena solo kill of the same boss (§7) opens no portal and has no
  bonus room. Same entry-context distinction the rest of §6 runs on — no other reward math forks.
- **Its own clock:** `bonus_timer = 90 s`, starting when the first member enters. It is **separate
  from the run clock** (§4.1), which has already stopped on the boss kill — a slow stage chain
  never shortens the payoff. On expiry every member is returned to the herald's staging map and
  the instance dissolves.
- **One-way, no re-entry.** The portal closes behind the party; a member who leaves early does not
  get back in. There is no failure state — the bonus room is pure upside, and leaving with nothing
  is only possible by ignoring it.
- **Contents:** the room is filled with `reactor` interactables
  (`15_maps_system/MAP_INTERACTABLES.md` §4 — the existing type, no new mechanic), each carrying
  the raid's bonus `drop_table_ref`. `respawn_timer_s` is set beyond the 90 s clock so every node
  is **one-shot**: the room holds a fixed pool of rolls, and racing it is a co-op scramble, not a
  DPS check. No monsters spawn in a bonus room.
- **The chance table.** Every reactor rolls the raid's bonus table, built only from
  `10_systems/DROPS.md` §2's existing named buckets — this doc fixes the row shape, `10_systems/DROPS.md`
  owns the bucket values and Phase D owns the concrete per-raid SKUs:

| Row | Bucket | Notes |
|---|---|---|
| `shards` | `guaranteed` (1.00) | small per node; the floor that makes every node worth hitting |
| Gear-modification scroll, `steady` tier | `uncommon` (0.15) | `10_systems/SCROLLS.md` (`item_use_0061`–`0078`), `slot_family` banded to the raid |
| Raid-exclusive consumable | `uncommon` (0.15) | the `item_use_0021`–`0060` block already reserved below |
| Gear-modification scroll, `bold` tier | `rare` (0.04) | a chase tier — never vendor-sold (`10_systems/SCROLLS.md` §4.2) |
| One extra `raid_token` | `rare` (0.04) | a small bump on top of §6.B's guaranteed grant |
| Gear-modification scroll, `perilous` tier | `epic` (0.008) | the top chase tier |

This makes the raid bonus room a **named acquisition source for gear-modification scrolls**
(`10_systems/SCROLLS.md` §4.1 carries the reciprocal line). It is a *chance* stream by design:
§6.A–D already guarantee a clear's worth in `exp` and tokens, so the bonus room adds variance and a
reason to run one more time without ever being the thing a player must farm. Nothing here is
power-exclusive — the scrolls are the same SKUs the field and vendors supply
(`10_systems/SCROLLS.md` §4.1–§4.2), so the bonus room is a better *rate*, not a locked door (P2).

Who receives each reactor's `loot_drop` is `10_systems/social/PARTY.md` §5's loot-share rule over
`10_systems/DROPS.md` §7's tag-eligibility — consumed unchanged, exactly as field loot is.

Supporting reward rules (unchanged in shape):

- **Boss uniques.** The finale boss's uniques come from **the boss's normal drop table**
  (`10_systems/DROPS.md` §5.3–§5.4, `10_systems/ITEMS.md` §11) — no separate raid-only unique
  table. A raid-context kill receives `10_systems/DROPS.md`'s raid-boss treatment; an
  open-arena solo kill of the same boss (§7) receives the plain region-boss treatment. That
  entry-context distinction is the whole of "reduced reward" — no other reward math is forked.
- **Loot arbitration.** Who receives a discrete drop is `10_systems/social/PARTY.md` §5's
  (loot-share modes) over `10_systems/DROPS.md` §7's tag-eligibility — consumed unchanged. The
  guaranteed `raid_token` (B) is a per-member grant, not a contested corpse roll, so it is not
  subject to loot arbitration.
- **Raid-exclusive consumables.** Raid stage devices and clear rewards may grant raid-exclusive
  use items minted from the reserved `item_use` range (`docs/ID_REGISTRY.md`, `item_use_0021`–
  `0060` block); concrete items are Phase D content.
- **First-ever clear (one-time).** Separate from the daily beat (D): each raid also grants a
  one-time first-*ever*-clear reward per character, folded into `10_systems/LEVELING.md` §4's
  "other" (≈5%) one-time-grant budget alongside first-kill and discovery grants
  (`10_systems/DROPS.md` §8's family) — budgeted there, not here.

## 7. Solo fallback (arc-1 rule, kept for all four raids)

The finale boss remains **soloable via the arena's open (non-raid) entry at reduced reward** —
the arc-1 rule (`docs/WORLD_PLAN.md`) is retained game-wide, including on the two arc-2 raids.
The open entry is the region arena's ordinary door: no party, no herald, no stage chain, no
cooldown interaction with §5, and the kill is a plain region-boss kill (`boss` tier per
`10_systems/LEVELING.md` §3 / `10_systems/DROPS.md` §5.3). Only the raid entry produces
raid-tier rewards (§6). Raid-boss combat scaling for the party context is
`10_systems/COMBAT_FORMULA.md` §13.3's (see Open Questions on its assumed party-size range).

## 8. Server Dependency

Raid instancing is `authority: server` end to end (`10_systems/PERSISTENCE.md` §1–§2,
`00_vision/PILLARS.md` P6): instance allocation, stage-objective state, the fixed `N`, loot/`exp`
arbitration, the guaranteed `raid_token` grants (§6.B/§6.D), the per-character/per-raid
first-clear-of-the-day flags (§6.D), and the §5 clear-cooldown timers are all server truth a client
may not self-certify. The timers and rolls added by this revision are the same:
- **The run clock** (§4.1) and the **bonus clock** (§6.E) are server-held countdowns. The client
  renders them (`10_systems/HUD.md` §6.2) from server ticks and may not author expiry — a client
  claiming "still 3 minutes left" past the server's expiry is refused, like any other
  `authority: server` field.
- **Bonus-room reactor rolls** (§6.E) are rolled server-side against the raid's `drop_table_ref`,
  the same path every other drop takes (`10_systems/DROPS.md` §1); the client never rolls loot.
- **Bonus-room eligibility** — whether the portal opens at all — is the server's entry-context
  record of the kill (raid entry vs. open arena, §7), not a client assertion.
**In the interim solo build, raids ship present but dormant** — the party system is dormant
(`10_systems/social/PARTY.md` §Server Dependency), so no party ever forms and no herald entry
succeeds; heralds stand in the world with a "gather a party" refusal line. The solo player's path
to all four bosses is §7's open arena entry, which works fully offline. The `GameState` facade
(`10_systems/PERSISTENCE.md` §5) still carries the raid-side fields (first-ever-clear flags,
first-clear-of-the-day flags, cooldown timers) so the live server swap changes no calling code.
The stage chain, the run clock, and the bonus rooms (`map_325`–`map_328`) are dormant with the rest
of the raid — the four bonus-room maps ship authored and unreachable, since the only door into one
is a raid-entry boss kill (§6.E) and no raid entry can succeed. They need no `GameState` field:
both clocks and the bonus roll are per-instance transient state that exists only inside a live run,
never across a save.

## Open Questions

- **Rename migration completeness.** The v3 rename (§1) touches every file that carried the
  legacy phrasing or `pq_<name>` tokens — at minimum `00_vision/GLOSSARY.md` (token family
  block), `00_vision/SCOPE.md`, `docs/WORLD_PLAN.md`, `docs/ID_REGISTRY.md` (map/quest
  conventions + token block), `10_systems/QUESTS.md` (Open Questions), `20_schemas/quest.schema.md`,
  `CLAUDE.md`, and the phase reports. Siblings are revising several of these in parallel; run
  `docs/VALIDATION.md` §1–§2 across the tree after all v3 edits land to confirm no legacy
  phrasing survives. Owner: orchestrator, with this doc as the reference.
- **Resolved — v1 "Rift raid" collision reconciled.** `10_systems/social/PARTY.md` §6 now
  describes exactly this doc's roster — party-instanced runs across the four v3 finale arenas
  (`map_042`/`map_200`/`map_244`/`map_324`) at the binding **3–6** party size, fixing
  `10_systems/COMBAT_FORMULA.md` §13.3's assumed `N` range at 3–6 — and the stale Rift-era
  references (party 4–6, `map_197`–`map_200`, "R12") are gone from PARTY/SPAWN/COMBAT_FORMULA.
  The remaining DROPS-side question is tracked in its own entry below.
- **Lockout tuning — 15-minute cooldown confirmed at the 2026-07-24 balance pass.** With the
  retuned `10_systems/LEVELING.md` §3.1 grants, even back-to-back clear-chaining pays less `exp`/hour
  than at-level field hunting (arithmetic in that doc's Open Questions), and the token faucet is
  bounded at 1/clear regardless of pace — so the short cooldown holds its one target (chaining must
  not beat field play as a loot/`shards` faucet) without needing to be longer. The daily pacing pull
  stays with the **first-clear-of-the-day bonus** (§6.D), not the cooldown. Remaining open only for
  telemetry: if live runs clear much faster than the modeled ≈ 25 minutes, revisit the cooldown and
  the LEVELING §3.1 amounts together (alternatives — a longer cooldown, a daily clear count, no
  cooldown at all — stay available). Owner: this doc with `10_systems/ECONOMY.md`.
- **Resolved (2026-07-24 contradiction fix): day-boundary definition for the
  first-clear-of-the-day bonus (§6.D).** `10_systems/PERSISTENCE.md` §2.1 now defines the shared
  time boundaries — a fixed **daily reset at 00:00 UTC** (fixed UTC rollover chosen over
  per-account local and rolling-24h variants), plus the weekly Monday 00:00 UTC anchor — and
  explicitly names this doc's per-character, per-raid first-clear-of-the-day flag among the per-day
  flags cleared at that instant, carried on the `GameState` facade (PERSISTENCE §5) next to the
  first-ever-clear flags and cooldown timers (§8). §6.D consumes that boundary by reference, and
  the same definition serves the weekly guild goal (`10_systems/social/GUILD.md` §11), so the whole
  social package shares one clock as this entry asked. Nothing remains open here.
- **Contribution-weighted vs even reward split.** `10_systems/social/PARTY.md` §4 owns the
  exp-split math (contribution-weighted + presence) and its own Open Questions already flag
  reconciling that split against `10_systems/LEVELING.md` §3's raid total. Whether raid rewards
  (first-clear grants, stage-device consumables) should follow that same weighted split or stay
  strictly per-member-even is unresolved; default at this revision: per-member-even for everything
  except the boss `exp` pool, which is PARTY.md §4's. The `raid_token` grants (§6.B, §6.D) resolve
  this specific case — they are authored as **flat guaranteed per-member** grants (every eligible
  member gets one; the daily bonus adds a second), never a pool to divide — so they sit outside the
  weighted-split question entirely. Owner: `10_systems/social/PARTY.md`, consulted by this doc.
- **Resolved — raid-boss drop treatment on shared bosses.** `10_systems/DROPS.md` §5.4 now applies
  its raid-boss table (including the guaranteed per-member `raid_token` from the `item_etc_0177`–
  `0180` block) to a **raid-entry** kill of all four finale bosses, the arc-1 **shared** bosses
  (`mob_027`/`mob_150`) included; an open-arena solo kill of the same boss (§7) drops **no** token
  and takes the plain region-boss table (§5.3). The entry-context distinction (§6) is the whole of
  the difference. Nothing remains open here.
- **Entry fee.** Whether raid entry charges a `shards` fee (a sink lever) is deliberately left
  open; default none (§3). Owner: `10_systems/ECONOMY.md` with this doc.
- **Per-stage / completion `exp` values (§6).** The `raid_stage_exp` / `raid_clear_exp` amounts are
  **fixed authored numbers** owned by `10_systems/LEVELING.md` §3.1 (first-pass, one flat value per
  raid — no formula). This doc fixes only the reward *structure* (per-stage grant + completion
  bonus, flat per-member); the numbers and their tuning are LEVELING's.
- **Resolved — arc-2 ID ranges minted.** `map_240`–`244`, `map_320`–`324`, `mob_178`,
  `mob_234`, the arc-2 herald NPCs, and the arc-2 intro/handler quest slots all sit inside
  `docs/ID_REGISTRY.md`'s extended blocks, and the `frostpeak`/`arcane_reach`/`voidshore`
  slugs are live in `00_vision/GLOSSARY.md` (only `rift` stays reserved-future). Phase D
  landed the content and `docs/VALIDATION.md`'s checks pass — nothing remains open here.
- **"Raid herald" term.** Coined here as the entry-NPC role name; needs a Provisional entry in
  `00_vision/GLOSSARY.md` if it is to appear in content files (NPC `role` fields) rather than
  prose only. Owner: GLOSSARY gatekeeper at the next phase gate.
- **Run-clock value (§4.1).** `raid_run_timer = 30 min` is a first pass, derived from the
  ≈25-minute modeled clear plus ~20% learning headroom — it is **not** measured. The number is
  wrong in a specific direction if the model is wrong: the four raids span Lv 15–22 to Lv 70–80 and
  currently share one flat value, so a single clock may be generous for `raid_undervault` (three
  short low-level stages) and tight for `raid_voidtide` (tide cycles gate movement, so the stage
  chain has a hard floor no amount of DPS removes). Alternatives if telemetry says so: per-raid
  values, or a clock derived from stage count × a per-pattern budget. Deliberately **not** split
  per-raid at this revision — one number is easier to falsify than four. Owner: this doc with
  `10_systems/LEVELING.md` at the balance pass.
- **Signature mechanics need a per-stage authoring pass (§4).** The four signatures (haul / beat /
  thaw / tide) fix each raid's identity and the pattern each stage runs, but the numbers that make
  them playable are unauthored: the haul's carry penalty magnitude, the beat's cycle period, the
  thaw's brazier count and melt duration, the tide's surge period and its interaction with
  `15_maps_system/MAP_TRAVERSAL.md` footholds. Each is Phase D content; none can be validated by
  `docs/VALIDATION.md` until authored. Flagged rather than guessed per CLAUDE.md Law 4. Owner:
  Phase D content pass against this doc's §4 table.
- **Do the tide/beat signatures need a new interactable param?** §4 asserts every signature is
  buildable from the existing `quest_object` / `reactor` types with no new param, and the haul and
  thaw clearly are. The **beat** (a hazard firing on a fixed cycle) and the **tide** (a map-wide
  water level on a cycle) both imply a *periodic, map-owned* state that
  `15_maps_system/MAP_INTERACTABLES.md` does not currently model — its `respawn_timer_s` is
  per-node, not a shared map clock. Either those two signatures are expressed as many
  independently-timed nodes (works, but drifts out of phase and loses the "learnable" property
  that is the whole point of the beat), or MAP_INTERACTABLES gains one shared-cycle param. Not
  resolved here because the owning doc is not this one. Owner:
  `15_maps_system/MAP_INTERACTABLES.md`, raised by this doc.
- **Bonus-room table values (§6.E).** The row shape is fixed here; the bucket assignments
  (`uncommon` for `steady` scrolls, `rare` for `bold`, `epic` for `perilous`) are a first pass
  chosen to mirror `10_systems/SCROLLS.md` §4.1's field-drop ordering, and the **node count per
  bonus room is unauthored** — which matters more than the per-node rates, since expected yield is
  `nodes × rate` and only the product is balanceable. Until node counts land, the scroll faucet
  this adds cannot be checked against `10_systems/SCROLLS.md` §4.4's sink-dominant requirement or
  `10_systems/ECONOMY.md` §6's inflation guard. Owner: `10_systems/SCROLLS.md` and
  `10_systems/ECONOMY.md` jointly, at the same pass that authors the node counts.
- **Does the bonus room want a floor?** As authored, a party that clears the boss with a bad set of
  rolls leaves with `shards` only. That is honest variance and §6.A–D already guarantee the clear's
  real value — but it is also the most likely source of "the bonus room felt bad" feedback. A
  pity/floor rule (e.g. one guaranteed `steady` scroll per clear) is the obvious lever and is
  deliberately **not** taken at this revision: adding a floor later is a one-line change, removing
  one after players have it is not. Owner: this doc, post-telemetry.
