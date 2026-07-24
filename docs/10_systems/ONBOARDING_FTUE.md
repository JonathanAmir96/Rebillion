# ONBOARDING_FTUE.md — The First Hour on Emberfoot Isle

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md §R1,
10_systems/CONTROLS.md, 10_systems/QUESTS.md, 10_systems/LEVELING.md, 10_systems/JOBS.md,
10_systems/STATS.md, 10_systems/HUD.md, 10_systems/INVENTORY.md, 10_systems/DEATH_PENALTY.md,
10_systems/ECONOMY.md, 10_systems/SKILL_SYSTEM.md, 10_systems/PERSISTENCE.md,
15_maps_system/MAP_TRAVERSAL.md, 15_maps_system/MAP_CONNECTIONS.md

Owner doc for the **first-time-user experience**: the beat-by-beat path a brand-new character
walks across Emberfoot Isle (`map_001`–`016`, `docs/WORLD_PLAN.md` §R1) in roughly one played
hour, which mechanic each beat teaches, and what device teaches it. This doc invents no new
rules — every mechanic cited below is defined in its owning system doc; this doc only sequences
them onto the region's existing maps and quest block (`quest_001`–`010`, `npc_001`–`010`,
`docs/WORLD_PLAN.md` §R1). Exact quest/NPC content authoring is Phase D's; this doc fixes the
*shape* of the hour Phase D content must hit.

## 1. Design intent

The hour is a single onboarding arc, not a checklist: every mechanic is introduced by something
the player would naturally do next (talk to the NPC standing in the doorway, fight the monster
blocking the path, open the bag because it just received an item) rather than a modal tutorial
popup. `00_vision/PILLARS.md` P1 ("readable, snappy, fair") and P2 ("cozy, not cruel") both apply
directly: Emberfoot's whole level band (Lv 1–7) sits inside `10_systems/DEATH_PENALTY.md` §2's
**0% exp-loss grace band**, so nothing in this hour, including the graduation boss, can cost the
player real progress. The hour's job is confidence, not challenge.

## 2. Pacing targets

| # | Beat | Maps | Target window | Cumulative |
|---|---|---|---|---|
| 1 | Wake, first steps | `map_001` | 0–3 min | 3 min |
| 2 | Elder's hall, quest accept | `map_004` | 3–6 min | 6 min |
| 3 | Outfitter, inn, first gear/shards | `map_002`–`003` | 6–11 min | 11 min |
| 4 | First field, first kill | `map_005` | 11–17 min | 17 min |
| 5 | Ascending fields, skills unlock | `map_006`–`011` | 17–32 min | 32 min |
| 6 | Old Kiln Tunnels (dungeon) | `map_012`–`013` | 32–42 min | 42 min |
| 6a| (optional) the secret map | `map_014` | — (parallel, not counted) | — |
| 7 | Cindermaw, the graduation fight | `map_016` | 42–52 min | 52 min |
| 8 | Ferry boarding | `map_015` → `map_017` | 52–60 min | 60 min |

**Lv 8 by end of hour — decision (2026-07-24): front-loaded scripted grants.** `10_systems/LEVELING.md`
§1's table gives cumulative `/played` for Lv 1→8 as the sum of its per-level rows: 0.08+0.10+0.12+
0.15+0.17+0.20+0.23 ≈ **1.1 h** on open at-level pacing — just past the 60-minute budget. The
intro closes that ≈10-minute gap with **scripted first-clear and guided-quest `exp` beats
front-loaded into the Emberfoot path**: the `quest_001`–`010` block authors its `pct` values at
the **top** of the `10_systems/QUESTS.md` §4 bands, and the island's one-time first-clear grants
(dungeon first-entry, the secret map, the Cindermaw kill) are budgeted from `10_systems/LEVELING.md`
§4's "other" (≈5%) slice. Emberfoot's guided density is deliberately richer than open-world
pacing — the grace-band island is exactly where a compressed curve is safe (0% death loss, §1) —
so the **Lv-8 ferry gate stays a real ≈60-minute promise**, not a soft "≈first hour." Phase D's
Emberfoot content pass must sum quest + first-clear `exp` to ≥ the ≈10-minute equivalent
(≈ 3,800 `exp`, the Lv 7→8 shortfall at the blended rate) and sanity-check real kills-to-Lv-8.

## 3. Beat 1 — Wake and first steps (`map_001`, Emberfoot Village)

The character spawns at `map_001`'s `main` spawn. **Movement and jump** (`10_systems/CONTROLS.md`
§1–§2, jump-buffer/coyote-time §4) are taught by level design, not a prompt: the path from spawn
to the elder's hall crosses one trivially small foothold gap, just enough that the player presses
`Space` once on their own. The HUD's always-on elements (player plate, minimap, bottom bar,
`10_systems/HUD.md` §11) are simply present from frame one — nothing calls them out; a first-time
player learns their meaning by watching them react to what they do next.

## 4. Beat 2 — Elder's hall, first quest (`map_004`)

The novice guide NPC (`docs/WORLD_PLAN.md` §R1's "novice guide … in Emberfoot Village's elder's
hall") is the first `talk` interaction, teaching the Interact key. Accepting the region's opening
`main` quest (drawn from the `quest_001`–`010` block, `10_systems/QUESTS.md` §1) auto-opens
`frame_quest` and populates the compact tracker (`10_systems/QUESTS.md` §8, `10_systems/HUD.md`
§5) — the quest log's own UI is the only "how to track a quest" lesson given. The quest's `reach`
step sends the player to the outfitter, chaining Beat 3 without a separate waypoint marker beyond
the quest tracker's step text.

## 5. Beat 3 — Outfitter and inn (`map_003`, `map_002`)

A `collect`/`talk` step at the outfitter grants the character's starter weapon (the weapon-agnostic
`novice` kit, `10_systems/JOBS.md` §6) — receiving it is the first item to ever enter the `equip`
tab, which is the natural moment to teach the Inventory toggle (`10_systems/CONTROLS.md` §1) and
equipping a slot (`10_systems/INVENTORY.md` §1–§2). At the inn, the character's **bind point**
defaults to `map_001` already (`10_systems/DEATH_PENALTY.md` §4); resting here is optional flavor,
not a required tutorial step. The general-store/inn vendor is where the starting **50 `shards`**
(`10_systems/ECONOMY.md` §1) gets its first spend — a Lesser Life Tonic (15 `shards`,
`10_systems/ECONOMY.md` §4.1) — teaching the wallet display and a quickslot (`F1`–`F4`,
`10_systems/CONTROLS.md` §1) in one purchase.

## 6. Beat 4 — First field, first kill (`map_005`)

A `kill` step sends the player to Emberfoot's first field. Basic attack (Left Mouse Button,
`10_systems/CONTROLS.md` §1) is taught purely by there being a monster in the way. The first kill
delivers, together: the first `exp` gain (visible on the bottom-bar strip, `10_systems/HUD.md` §3),
the first drop (auto-loot on contact, `10_systems/INVENTORY.md` §4), and — once enough kills land —
the first level-up (full `life`/`essence` refill + stat growth toast, `10_systems/LEVELING.md` §5).
No dialogue explains any of this; the HUD's own feedback (gauge fill, a "Level Up" success toast,
`10_systems/HUD.md` §9) is the lesson.

## 7. Beat 5 — Ascending fields, skills come online (`map_006`–`011`)

Fields 006–011 carry the region's monster-gradient climb (Lv 1→8 monotonically,
`docs/WORLD_PLAN.md` "Map order & monster gradient law"), fed by further `kill`/`collect` quest
steps from the same `quest_001`–`010` block. This is where the remaining mechanics land, each on
first opportunity rather than a fixed script order:

- **Skill unlock & essence use.** The first skill point (Lv 2, `10_systems/SKILL_SYSTEM.md` §2)
  lets the player learn a `skill_novice_*` active and slot it to a bar key (`1`–`8`,
  `10_systems/CONTROLS.md` §1); casting it for the first time is the first `essence` spend,
  visible as the tide-ramp gauge dropping beneath `life` (`10_systems/HUD.md` §3).
- **Dodge slot.** A mobility novice skill (Tumble) fills the dedicated Dodge binding
  (`10_systems/CONTROLS.md` §3) once learned — its own small frame distinguishes it from the eight
  general slots at a glance.
- **Ropes/one-way platforms.** The path naturally includes a climbable and a drop-through ledge
  (`15_maps_system/MAP_TRAVERSAL.md` §3–§4), teaching both without a dedicated tutorial map.

## 8. Beat 6 — Old Kiln Tunnels, the first dungeon (`map_012`–`013`)

The first `dungeon`-type map (`00_vision/GLOSSARY.md` map types) — denser encounters, tighter
corridors — teaches that map type's identity by contrast with the open fields just left. A
quest step tied to the tunnels' elite/boss-adjacent trash (`10_systems/DROPS.md` tagging rules,
cited not restated) is the natural reason to be there rather than a "go here" instruction alone.

**Beat 6a — the secret (`map_014`), optional.** Not on the critical path and not required by any
quest step (`10_systems/QUESTS.md` never gates a `main` quest behind a `secret` map). It exists
purely as a curiosity reward for a player who explores off the tunnels' main line — first taste
that Emberfoot rewards wandering, a habit the much larger Harthmoor Isle leans on far more. It
does not appear in the pacing table's cumulative time because it costs the *player's* optional
minutes, not the FTUE's required ones.

## 9. Beat 7 — Cindermaw, the graduation fight (`map_016`, arena)

The region's `main` quest chain culminates in a `reach`/`kill` step at the Kiln Heart arena — the
first `arena`-type map (`00_vision/GLOSSARY.md`) and the first `boss_bar` the player has ever seen
(contextual, top-center, `10_systems/HUD.md` §6). Cindermaw (`mob_012`, Lv 8, single phase,
"generous telegraphs," `docs/WORLD_PLAN.md` §R1) is designed to be beatable by a Lv 7–8 novice on
the starter kit; because the fight sits inside the Novice tier, **a death here costs 0% exp**
(`10_systems/DEATH_PENALTY.md` §2) — the graduation fight is, deliberately, a fight the player
cannot be set back by, only taught by. On defeat, per `docs/WORLD_PLAN.md`'s boss-unique rule,
Cindermaw drops the region's one boss-unique `item_equip` pair — the player's first taste of a
notable item, motivating the gear chase that begins in earnest on Harthmoor.

## 10. Beat 8 — Boarding the Harborwind Ferry (`map_015` → `map_017`)

Quest turn-in back at Emberfoot Village flags the character as ready to leave; the elder/dockhand
dialogue points to the ferry rather than gating travel behind another quest step — the dock
portal at `map_001` is simply always open (`docs/WORLD_PLAN.md` "Cross-region walk edges"). Riding
the Harborwind Ferry (`map_015`, a combat-free `interior`) for its small `shards` fare
(`docs/WORLD_PLAN.md`, fare figure owned by `10_systems/ECONOMY.md`) is the character's first paid
transit, previewing the fare-based Coachworks model that replaces free warps on Harthmoor. Arrival
at Rosen Harbor (`map_017`) is the hour's closing beat: the coachman's one free ride to the
character's chosen line's instructor town begins the **advancement pilgrimage**
(`10_systems/JOBS.md` §1, `docs/WORLD_PLAN.md` "Job instructors") — the 1st-job advancement itself
is Harthmoor content, outside this doc's scope (§11).

## 11. Deliberately NOT taught in hour one

These are cut on purpose, not by oversight — each has its own home once the player reaches
Harthmoor:

- **Job-line selection and the 1st advancement quest itself.** The character graduates Emberfoot
  still `novice`; choosing a line and completing the trainer quest happens at the instructor's
  home town post-ferry (`10_systems/JOBS.md` §1).
- **Coach fares beyond the ferry.** The Harthmoor Coachworks network (`docs/WORLD_PLAN.md`
  "Harthmoor Coachworks") has five stations and ring-distance pricing; Emberfoot has exactly one
  paid transit (the ferry) and nothing else to compare it against yet.
- **Social systems** (party, guild, trade, chat, market) — server-deferred everywhere
  (`00_vision/PILLARS.md` P6), and irrelevant to a solo island with no other players' content to
  interact with.
- **Bank storage and inventory-tab expansion** (`10_systems/INVENTORY.md` §1, §7) — the base
  24-slot tabs are never stressed by Emberfoot's short quest chain and small loot pool.
- **Enhancement** (`10_systems/ENHANCEMENT.md`) and **stat free-point reallocation fees**
  (`10_systems/ECONOMY.md` §3.1) — both real `shards` sinks meant for a character with a build to
  refine, which a `novice` does not yet have (`10_systems/STATS.md` §4.1's undifferentiated 5/5/5/5
  start).
- **Raids** — the two Harthmoor raids (`raid_undervault`, `raid_mainspring`) live entirely on
  Harthmoor; the arc-2 raids (`raid_deepfrost`, `raid_voidtide`) live farther still, on the far
  isles (`10_systems/social/RAID.md` §2).
- **The rest of the world map.** Emberfoot's sixteen maps are the whole of the player's world for
  this hour; the ring's geography (`docs/WORLD_PLAN.md` "World graph") is not previewed beyond the
  ferry's destination name.

## 12. Failure and skip tolerance

Nothing in this hour is hard-gated beyond `10_systems/QUESTS.md` §2/§6's ordinary `prereqs`/
`level_requirement` accept gates — there is no invisible wall forcing the beat order above. A
player who ignores every NPC and simply runs into `map_005` can fight there unquested; one who
sprints straight to the Kiln Heart arena portal at Lv 1 can walk in and get soundly beaten by a Lv
8 boss with generous telegraphs — a bad time, not a broken one, and consistent with
`00_vision/PILLARS.md` P1 ("a player who dies should know why"). Skipping dialogue costs the player
nothing mechanically (quest `exp`/`shards`/items are simply not yet collected, per
`10_systems/QUESTS.md` §7's no-penalty abandon/re-accept model) — the beats above describe the
*intended* path, not an enforced one. Whether the arena portal itself deserves a soft
level-suggestion gate (a sign, not a wall) is flagged in Open Questions.

## 13. FTUE completion tracking

Completion is not a new piece of state. It is read entirely off existing `server`-authoritative
quest flags (`10_systems/QUESTS.md` §9, `10_systems/PERSISTENCE.md` §2 "Quest flags / step
progress / completed set") — specifically, whether the character has turned in the region's
closing `main` quest (the Cindermaw/ferry-boarding quest in the `quest_001`–`010` block). No
separate `ftue_complete` flag, timer, or client-side milestone is introduced; any system that needs
to ask "has this character finished onboarding" asks the same quest-completion query every other
system already uses. This keeps the FTUE fully inside the authority model
`10_systems/PERSISTENCE.md` §1 already defines, with nothing new to validate.

## Open Questions

- **Resolved (2026-07-24 contradiction fix): Lv-8 gate vs the 60-minute intro.** Decision in §2:
  the intro front-loads scripted first-clear/guided-quest `exp` (top-of-band quest `pct`s +
  LEVELING §4 "other" one-time grants) so Lv 8 lands inside the hour; the ferry gate stays a real
  60-minute promise. Remaining work is Phase D's: author `quest_001`–`010` to the §2 budget and
  sanity-check real kills-to-Lv-8 against LEVELING's unmeasured ≈480-kills/hour assumption.
- Whether the Kiln Heart arena portal (`map_016`) should carry a soft level-suggestion gate (a
  sign/dialogue warning, not a hard block) for a player who rushes there under-leveled is undecided
  (§12); default per this doc is no gate, consistent with the no-invisible-walls stance, but flagged
  for a playtesting pass.
- Whether the elder's-hall opening quest should be a single quest or a short 2–3 quest
  introductory chain (affecting exactly how many of `quest_001`–`010` Beats 2–5 consume before
  reaching the dungeon) is Phase D content authoring, not fixed here.
- This doc assumes the interior order `map_002` inn / `map_003` outfitter / `map_004` elder's hall,
  reading `docs/WORLD_PLAN.md` §R1's listed order ("inn, outfitter, elder's hall") as sequential;
  if Phase D assigns those three IDs differently, only this doc's beat-to-map labels need
  relabeling, not its sequence or teaching intent.

