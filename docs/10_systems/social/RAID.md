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

## 1. Terminology law (v3 owner revision, 2026-07-23)

**"Raid" fully replaces the legacy "party quest" / "PQ" phrasing across the tree.** The token
family is `raid_<name>` (replacing the retired `pq_<name>` family); the legacy tokens and
phrasing are invalid in all docs and content once the v3 revision lands, and
`docs/VALIDATION.md` §2's referential checks enforce the rename. This paragraph is the single
statement of that law — sibling docs adopt the new term by reference, never by re-declaring it.

Token minting: `raid_<name>` tokens are **minted in `docs/ID_REGISTRY.md`** (the range owner,
same pattern as every other ID family); this doc is the concept owner. A raid that is not in the
registry does not exist.

## 2. The raid roster (v3 — four raids, two arcs)

Placement (which maps, which region, which boss slot) is owned by `docs/WORLD_PLAN.md`; this
table lists the roster by reference and fixes the **rule-side** columns (band, party size):

| Token | Name | Level band | Party | Stage chain | Finale arena | Finale boss |
|---|---|---|---|---|---|---|
| `raid_undervault` | Undervault Heist | 15–22 | 3–6 | `map_038`–`map_040` | `map_042` | `mob_027` |
| `raid_mainspring` | Mainspring Trial | 32–40 | 3–6 | `map_195`–`map_197` | `map_200` | `mob_150` |
| `raid_deepfrost` | Deepfrost | 45–55 | 3–6 | `map_240`–`map_242` | `map_244` (Frostpeak Isle) | `mob_178` |
| `raid_voidtide` | Voidtide | 70–80 | 3–6 | `map_320`–`map_322` | `map_324` (Voidshore) | `mob_234` |

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
  explains the run) and a handler quest (the repeatable turn-in wrapper for clears), authored as
  ordinary `10_systems/QUESTS.md` quests. Arc-1 slots are `quest_087`–`090`
  (`docs/ID_REGISTRY.md`); arc-2 raids mint theirs in the registry the same way.
- **Level band gate — hard, both ends.** Every member's `level` must lie inside the raid's band
  (inclusive) at instance creation. A member who levels past the ceiling mid-run is not ejected;
  the gate applies only at entry.
- **Party size 3–6.** Entry requires a party (mechanics, roster, and leadership entirely
  `10_systems/social/PARTY.md`'s) of 3–6 members, all on the herald's map. The **leader**
  initiates entry through the herald; the whole party is moved into the fresh instance together.
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
set is fixed; a raid may not invent one. Per-raid stage scripts (which pattern on which stage,
counts, spawn sets) are Phase D content authored against these three patterns.

## 5. Failure, wipe, re-entry & lockout

- **Within an attempt:** individual death, Release, and walk-back re-entry follow
  `10_systems/DEATH_PENALTY.md` §5.3 exactly; the party-side bookkeeping (fallen roster state,
  eligibility while fallen) is `10_systems/social/PARTY.md` §6's. Both are consumed unchanged.
- **Full wipe** (every member fallen, or every member Released/left the instance): the attempt
  ends and the instance dissolves. Stage progress does not persist across attempts — a new entry
  starts at stage 1.
- **Failure is free:** no lockout, no cooldown, no penalty beyond
  `10_systems/DEATH_PENALTY.md`'s ordinary death costs. Retry immediately from the herald.
- **Clear cooldown (default):** after a successful finale-boss kill, each participating
  character carries a **30-minute per-character, per-raid cooldown** before entering a new
  instance of that raid. No daily or weekly lockout — raids are meant to be re-runnable loot
  runs, and the cooldown exists only to keep clear-chaining from beating field play as a
  `shards`/loot faucet. The timer is server-tracked (§8). Tuning is flagged, not settled (Open
  Questions).
- Disbanding the party or the leader leaving mid-run does not dissolve the instance by itself;
  the instance dissolves when it is empty. Leadership succession inside a run is
  `10_systems/social/PARTY.md` §2's.

## 6. Rewards — raids are the loot path

Design intent (v3.1): **a raid clear is both a strong `exp` event and the loot path.** In the
MapleStory-inspired shape, `exp` arrives on **each stage cleared** and peaks in a headline
**completion bonus** on the finale kill; `10_systems/LEVELING.md` §3/§3.1 owns and sizes every raid
`exp` grant (cited, not restated) so a clear is excellent for its band without letting
cooldown-gated raiding beat hunting as the mandatory pacing path (`00_vision/PILLARS.md` P2).

- **`exp` — per stage, then a headline clear bonus.** A raid pays `exp` at three moments, all
  budgeted by `10_systems/LEVELING.md` §3/§3.1 (magnitudes there, not restated here):
  1. **Stage mobs** pay ordinary per-kill `exp` as the party clears them
     (`10_systems/LEVELING.md` §2–§3), shared per `10_systems/social/PARTY.md` §4.
  2. **Each stage clear** grants a flat `raid_stage_exp` to **every eligible member** (not split)
     the moment that stage's objective (§4) completes — the sub-step reward.
  3. **The finale-boss kill** grants the headline `raid_clear_exp` completion bonus to every
     eligible member (not split) — deliberately the run's **best `exp`** — *on top of* the boss's
     own kill `exp` (`10_systems/LEVELING.md` §3's raid-boss row, split per
     `10_systems/social/PARTY.md` §4).
  The stage and clear grants are **flat per-member** (the whole party is rewarded for finishing, not
  a pool to divide) — the MapleStory-inspired feel. This makes a raid an `exp` **event**, not a
  farm: the per-character clear cooldown (§5) keeps clear-chaining from displacing hunting as the
  pacing anchor.
- **Boss uniques.** The finale boss's uniques come from **the boss's normal drop table**
  (`10_systems/DROPS.md` §5.3–§5.4, `10_systems/ITEMS.md` §11) — no separate raid-only unique
  table. A raid-context kill receives `10_systems/DROPS.md`'s raid-boss treatment; an
  open-arena solo kill of the same boss (§7) receives the plain region-boss treatment. That
  entry-context distinction is the whole of "reduced reward" — no other reward math is forked.
- **Loot arbitration.** Who receives a discrete drop is `10_systems/social/PARTY.md` §5's
  (loot-share modes) over `10_systems/DROPS.md` §7's tag-eligibility — consumed unchanged.
- **Raid-exclusive consumables.** Raid stage devices and clear rewards may grant raid-exclusive
  use items minted from the reserved `item_use` range (`docs/ID_REGISTRY.md`, `item_use_0017`–
  `0060` block); concrete items are Phase D content.
- **First clear.** Each raid grants a one-time first-clear reward per character, folded into
  `10_systems/LEVELING.md` §4's "other" (≈5%) one-time-grant budget alongside first-kill and
  discovery grants (`10_systems/DROPS.md` §8's family) — budgeted there, not here.

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
arbitration, and the §5 clear-cooldown timers are all server truth a client may not self-certify.
**In the interim solo build, raids ship present but dormant** — the party system is dormant
(`10_systems/social/PARTY.md` §Server Dependency), so no party ever forms and no herald entry
succeeds; heralds stand in the world with a "gather a party" refusal line. The solo player's path
to all four bosses is §7's open arena entry, which works fully offline. The `GameState` facade
(`10_systems/PERSISTENCE.md` §5) still carries the raid-side fields (first-clear flags, cooldown
timers) so the live server swap changes no calling code.

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
- **Lockout tuning.** The 30-minute clear cooldown (§5) is a first-pass default serving one
  target — raid-clear chaining must not beat at-level field play as a loot/`shards` faucet
  (`10_systems/DROPS.md` / `10_systems/ECONOMY.md` faucet balance). Retune with telemetry;
  alternatives (daily count, no cooldown at all) stay open. Owner: this doc with
  `10_systems/ECONOMY.md`.
- **Contribution-weighted vs even reward split.** `10_systems/social/PARTY.md` §4 owns the
  exp-split math (contribution-weighted + presence) and its own Open Questions already flag
  reconciling that split against `10_systems/LEVELING.md` §3's raid total. Whether raid rewards
  (first-clear grants, stage-device consumables, any future raid token) should follow that same
  weighted split or stay strictly per-member-even is unresolved; default at this revision:
  per-member-even for everything except the boss `exp` pool, which is PARTY.md §4's. Owner:
  `10_systems/social/PARTY.md`, consulted by this doc.
- **Raid-boss drop treatment on shared bosses.** `10_systems/DROPS.md` §5.4's raid-boss table is
  written Rift-scoped (raid tokens from a Rift `item_etc` block). How much of it applies to a
  raid-context kill of the arc-1 **shared** bosses (`mob_027`/`mob_150`, §6) — in particular
  whether they drop any raid token at all — needs a DROPS-side pass. Owner:
  `10_systems/DROPS.md`.
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
