# QUESTS.md — Quest Anatomy, Rewards & Log UX

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, 10_systems/LEVELING.md, 10_systems/ECONOMY.md, 10_systems/DROPS.md,
10_systems/ITEMS.md, 10_systems/INVENTORY.md, 10_systems/JOBS.md, 10_systems/HUD.md,
10_systems/CONTROLS.md, 10_systems/PERSISTENCE.md, 10_systems/SPAWN.md,
10_systems/social/PARTY.md, 10_systems/social/RAID.md, 15_maps_system/MAP_INTERACTABLES.md,
15_maps_system/MAPS_SYSTEM.md, 20_schemas/quest.schema.md

Owner doc for **quests**: the fields every quest is built from, the four step types, how a
`collect` step sources its item, the `exp`/`shards` reward budget formulas, level gating,
abandon/retry/repeat policy, and the quest-log UX hook. `exp` curve math is
`10_systems/LEVELING.md`; `shards` faucet/sink balance is `10_systems/ECONOMY.md`; item
definitions are `10_systems/ITEMS.md`; kill-credit tagging is `10_systems/DROPS.md` §7. This doc
never restates those — it only sets the *quest-side* budget and shape. The authored quests and
their per-region ID blocks (arc-1 `quest_001`–`090`, arc-2 `quest_091`–`120`) are
`docs/ID_REGISTRY.md`'s; `docs/WORLD_PLAN.md` supplies region level bands. `20_schemas/quest.schema.md` (Phase C) formalizes field types; this
doc owns the anatomy and the numbers Phase D content copies.

## 1. Quest anatomy (fields)

| Field | Meaning |
|---|---|
| `id` | `quest_NNN` (`docs/ID_REGISTRY.md`) |
| `region` | Owning region slug (`docs/WORLD_PLAN.md`); scopes its `npc`/mob references |
| `quest_type` | `main` \| `side` (this doc's own enum — region critical-path/job-trainer vs optional) |
| `giver_npc` | `npc_NNN` who offers the quest |
| `turn_in_npc` | `npc_NNN` who accepts completion; defaults to `giver_npc` if omitted |
| `level_requirement` | Minimum character `level` to accept (hard gate) |
| `recommended_level` | Display-only guidance level (§6); usually equals `level_requirement` on `main` quests |
| `prereqs` | List of `quest_NNN` that must already be completed (§2) |
| `steps` | Ordered/unordered list of step objects (§3) |
| `rewards` | `exp`, `shards`, optional item lines (§4–§5) |

## 2. Prereqs — chains are just links, not a token

A quest chain is nothing but one quest's `prereqs` naming an earlier `quest_NNN`; there is **no**
separate "chain" step type or field. `level_requirement` and `prereqs` both gate *accepting* the
quest (both must hold). Job-advancement trainer quests (`10_systems/JOBS.md` §1) are ordinary
`main` quests: the 2nd/3rd-tier trainer quest's `prereqs` names the previous tier's trainer quest,
which is what actually enforces "already that line, already that tier" — no separate job-gate
field is needed. The four 1st-advancement trainer quests (one per line) are **mutually
exclusive by authoring convention**: completing one sets the character's line
(`10_systems/JOBS.md` §1) and the other three must stop being offered to that character from then
on; this doc fixes the exclusivity, Phase D wires it through each trainer NPC's quest list.

## 3. Step types (four — fixed set)

| Step type | Target | Notes |
|---|---|---|
| `kill` | One or a short explicit list of `mob_NNN`, × count | Credit follows `10_systems/DROPS.md` §7 tag-eligibility (deal/take damage before death); no separate quest-kill-credit rule |
| `collect` | `item_etc_NNNN` (or `item_use_NNNN`), × count | Sourced per §3.1 below |
| `talk` | One `npc_NNN` | May be the giver, the turn-in NPC, or a third party |
| `reach` | `map_NNN` + a named trigger zone/waypoint | Zone declaration mechanism is `15_maps_system/MAPS_SYSTEM.md`'s (a `10_systems/SPAWN.md`-`spawn_zones`-like rect), not defined here |

A step may optionally declare `requires_step` (another step in the same quest, same
prereq-linking pattern as §2) to force sequencing; default is **parallel** — all of a quest's
steps are open simultaneously and may complete in any order. Guideline: 1–3 steps per quest,
up to 4 for a chain-establishing quest (P1/P2 legibility — a quest log entry should read at a
glance).

### 3.1 Sourcing a `collect` step

Two sourcing mechanisms, no others:

- **Quest-flagged etc item.** The target is an ordinary `item_etc_NNNN` (`10_systems/ITEMS.md`
  §1) — either an existing regional material or a one-off item minted in that region's etc block
  — obtained through the normal monster-drop pipeline (`10_systems/DROPS.md` drop-table rows).
  It behaves like any other `etc` item while carried: normal `10_systems/INVENTORY.md` etc-tab
  slot/stack rules apply, it is not exempt from slot caps, and non-questers may loot the same
  material for its ordinary vendor/crafting value if it is a shared material.
- **Dedicated `quest_object` interactable.** For collect sources that should be a fixed
  world point rather than a kill (a lootable node, a chest, a corpse), the step targets a
  `quest_object` placed on a map. `15_maps_system/MAP_INTERACTABLES.md` owns the interactable's
  full mechanics (placement, respawn, visibility to non-questers); this doc only requires that
  interacting with a `quest_object` tagged to the step's quest grants the collect item (or
  increments the step directly) once.

Either way, the required quantity is **consumed automatically on turn-in** (§9) — no separate
"discard" action is needed, and a player who abandons before turn-in simply keeps whatever they
already picked up (it is an ordinary item with ordinary value).

## 4. Reward budget — `exp`

```
quest_exp = round( pct · exp_to_next(quest_level) )     # exp_to_next per 10_systems/LEVELING.md §1
```

| `quest_type` | `pct` band |
|---|---|
| `main` (incl. job-trainer) | 15%–30% |
| `side` | 5%–10% |

| `quest_level` | `exp_to_next` (`10_systems/LEVELING.md` §1) | `main` reward (15–30%) | `side` reward (5–10%) |
|---|---|---|---|
| 1 | 80 | 12–24 | 4–8 |
| 10 | 3,200 | 480–960 | 160–320 |
| 20 | 19,700 | 2,955–5,910 | 985–1,970 |
| 30 | 66,600 | 9,990–19,980 | 3,330–6,660 |
| 50 | 336,440 | 50,466–100,932 | 16,822–33,644 |
| 70 | 1,002,000 | 150,300–300,600 | 50,100–100,200 |
| 90 | 2,277,960 | 341,694–683,388 | 113,898–227,796 |
| 99 | 3,112,560 | 466,884–933,768 | 155,628–311,256 |

A region's total quest `exp` should land near **≈25%** of the `exp` needed to clear that region's
level band (`10_systems/LEVELING.md` §4 — cited, not restated); Phase D sums each region's
authored quests against that target and tunes individual `pct` within the bands above, per
`10_systems/LEVELING.md`'s own Open Question on this reconciliation. **Raid intro/handler quests**
(arc-1 `quest_087`–`090`; arc-2 `quest_099`–`100` and `quest_119`–`120`; `docs/WORLD_PLAN.md`,
`10_systems/social/RAID.md` §3) are authored as ordinary quests and pay **normal region-budget
`exp`** for their band (§4 above, `10_systems/LEVELING.md` §4) — the authored arcs top out at Lv 80
and there is **no post-cap zero-`exp` band** in scope (the `level` cap is 300,
`10_systems/LEVELING.md` §1/§6). The raid **clear** reward itself is the finale-boss `exp` and loot
(`10_systems/LEVELING.md` §3, `10_systems/social/RAID.md` §6), separate from these quests
(handler-quest **repeatability** vs §7's one-time-per-character launch policy is flagged in Open
Questions).

## 5. Reward budget — `shards`

Reuses `10_systems/DROPS.md` §3's existing tier multipliers rather than inventing new ones (P4):
a `side` quest pays the **elite-kill** `shards` mean at the quest's level, a `main` quest pays the
**boss-kill** mean — i.e., read the `elite`/`boss` column of that table directly.

| `quest_type` | `shards` reward |
|---|---|
| `side` | `= mean_shards_normal(quest_level) · 4` (`10_systems/DROPS.md` §3 `elite` column) |
| `main` | `= mean_shards_normal(quest_level) · 15` (`10_systems/DROPS.md` §3 `boss` column) |

| `quest_level` | `side` (×4) | `main` (×15) |
|---|---|---|
| 1 | 20 | 75 |
| 10 | 72 | 270 |
| 20 | 132 | 495 |
| 30 | 192 | 720 |
| 50 | 312 | 1,170 |
| 70 | 432 | 1,620 |
| 90 | 552 | 2,070 |
| 99 | 608 | 2,280 |

`10_systems/ECONOMY.md` treats this as a supplementary faucet, not the main one (its §1); it may
retune the multipliers above at the D gate if the total faucet drifts. **Item rewards** (an
`item_equip`/`item_use`/`item_etc` line in addition to `exp`/`shards`) are permitted and common for
`main` quests (e.g., a trainer quest's line-appropriate starter gear, or a boss-adjacent quest's
region material) — no separate budget cap is fixed here; Phase D authors them against
`10_systems/ITEMS.md`/`10_systems/ECONOMY.md` value bands.

## 6. Level requirement & recommended-level display

`level_requirement` is a **hard accept gate** — the giver NPC will not offer the quest below it.
`recommended_level` is **display-only** (shown in the quest log/tracker, §8) and carries no
mechanical gate; it exists for quests picked up early (a `side` quest offered below its "ideal"
level as a breadcrumb) so the player can judge fit before accepting. For `main` quests the two
values are normally equal.

## 7. Abandonment, retry & repeat policy

- **Abandon anytime**, no penalty: the quest leaves the active log, no `exp`/`shards` are lost
  (none were granted pre-turn-in), and any `collect`-step items already picked up are kept —
  they are ordinary items (§3.1), not clawed back.
- **Retry** is simply re-accepting from `giver_npc`; the §2/§6 accept gates are re-checked exactly
  as on first accept. There is no cooldown on re-accepting an abandoned (not-yet-completed) quest.
- **Repeatable policy — launch: none.** Every quest is **one-time per character**: once turned in
  it cannot be accepted again. There is no daily/weekly repeatable quest system at launch (see
  Open Questions).

## 8. Quest log UX hook

- **Full log** — the `frame_quest` window (`10_systems/HUD.md`'s frame-usage mapping; opened via
  the quest-log key, `10_systems/CONTROLS.md`) lists all active/available/completed quests and, per
  selected quest, shows giver, each step's progress (`x`/`y`), the reward preview (§4–§5), and
  Track/Abandon actions.
- **Compact tracker** — top-right, always visible while ≥1 quest is tracked (`10_systems/HUD.md`
  owns its position/frame/always-on-vs-toggle default). Shows up to **3** simultaneously tracked
  quests at once, each as a one-line name + current step's progress counter; which quests are
  tracked (of the player's active set) is a player choice made from the full log.
- **Concurrency cap.** A character may hold up to **20** active (accepted, not turned in) quests
  at once — generous enough to never bind normal region-by-region play (90 quests total, mostly
  cleared in sequence).
- Controller navigation of the full log follows `10_systems/CONTROLS.md`'s framed-UI rules.

## 9. Authority

Quest acceptance, step progress, prereq checks, and turn-in (including the `exp`/`shards`/item
grant) are **server-authoritative** in the live build (`00_vision/PILLARS.md` P6; contract
`10_systems/PERSISTENCE.md`); the solo client simulates and persists the same state locally
through the same authority model. No client may mark a step complete or grant a turn-in reward
without its accept gates (§2, §6) and step-completion criteria (§3) actually being met.

## Open Questions

- Quest kill/collect credit-sharing **among party members** (does a party member's kill/collect
  count for everyone nearby?) is resolved by `10_systems/social/PARTY.md` §4: a `kill`-step's credit
  shares across same-map members with that step active (mirroring `10_systems/DROPS.md` §7's shared
  tag), while a `collect`-step does **not** share — credit requires the item in hand. Raids inherit
  this same model for stage objectives (`10_systems/social/RAID.md` §4). This doc's §3 `kill` step
  defers there; no separate quest-side rule.
- **Raid handler-quest repeatability.** `10_systems/social/RAID.md` §3 describes the raid handler
  quest as a **repeatable** clear turn-in wrapper, but §7 above sets the launch policy at
  one-time-per-character with no repeatable-quest system. Reconcile before Phase D authors the
  handler quests: either the raid clear-reward loop routes through `10_systems/social/RAID.md`'s own
  clear/cooldown mechanics (not a re-acceptable quest), or the handler is the first sanctioned
  exception to §7. Owner: this doc with `10_systems/social/RAID.md`.
- Exact per-quest `pct` within the §4 bands, and the regional ≈25% reconciliation, is Phase D
  authoring work per `10_systems/LEVELING.md` §4's own Open Question; not resolved to the exact
  quest here.
- `quest_object` full mechanics (respawn timer, whether non-questers can see/interact with it) are
  owned by `15_maps_system/MAP_INTERACTABLES.md`, not yet authored; this doc only fixes the
  grant-on-interact contract (§3.1).
- The `reach`-step trigger-zone declaration (map-side schema shape) is pending
  `15_maps_system/MAPS_SYSTEM.md`; assumed analogous to `10_systems/SPAWN.md` §1's `spawn_zones`
  rect pattern but not confirmed.
- Daily/weekly/repeatable quests are explicitly **not** a launch feature (§7); if added later it
  is a new system referencing this doc's anatomy, not a change to it.
- Whether a quest may ever require an equipped item level / job line beyond `level_requirement`
  (e.g., a line-specific side quest) is not modeled; default is any character meeting the level +
  prereqs may accept any quest.
