# RAID.md — Raids (Instanced Co-op Runs)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/social/PARTY.md,
10_systems/JOBS.md, 10_systems/LEVELING.md, 10_systems/DROPS.md, 10_systems/QUESTS.md,
10_systems/DEATH_PENALTY.md, 10_systems/SPAWN.md, 10_systems/STATUS_EFFECTS.md,
10_systems/ECONOMY.md, 15_maps_system/MAPS_SYSTEM.md, 10_systems/PERSISTENCE.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the two **raids** (`raid_undervault`, `raid_mainspring`): their level and
party-size gates, how a party starts a run, stage progression, the finale boss and the
solo open-arena path, reward split, and failure/leaver/re-entry bookkeeping. A raid
is a party-instanced co-op run through a short chain of stage maps that ends at an
**existing** region boss (no extra boss slots) — the concept is allocated by
`docs/WORLD_PLAN.md` (Raids section) and the IDs by `docs/ID_REGISTRY.md`. Party
membership, the `exp`-share split, and loot-share modes are `10_systems/social/PARTY.md`'s;
`exp`/kill math is `10_systems/LEVELING.md`; boss defeat/recovery is
`10_systems/DEATH_PENALTY.md`; instancing/respawn is `10_systems/SPAWN.md` +
`15_maps_system/MAPS_SYSTEM.md`. This doc consumes all of those and never restates them — it
owns only the raid wrapper: gates, stage flow, and how the shared reward is scoped.

## 0. Terminology law (owner ruling, 2026-07-24)

**"Raid" fully replaces the legacy "party quest" / "PQ" phrasing across the tree** — the
genre term is retired notation (docs/VALIDATION.md §1). The token family is `raid_<name>`
(replacing the retired `pq_<name>` family). A raid is the instanced co-op run defined by
this doc; there is **no separate raid monster tier** — every raid finale reuses an existing
region boss (`normal`/`elite`/`boss` remain the only entity tiers). This paragraph is the
single statement of that law — sibling docs adopt the term by reference.

## 1. The two raids

Both are party-instanced co-op runs; each ends at an existing boss in its home region (R2
Millbrook / R8 Clockwork), so **no new boss or map slots are minted** — the finale reuses
the region's boss arena as a party-instanced entry.

| Token | Name | Level band | Party size | Stage maps | Finale arena | Boss | Region | Handler quests |
|---|---|---|---|---|---|---|---|---|
| `raid_undervault` | Undervault Heist | Lv 15–22 | 3–6 | `map_038`–`map_040` | `map_042` | The Cellar King (`mob_027`) | `millbrook` (r02) | `quest_087`–`quest_088` |
| `raid_mainspring` | Mainspring Trial | Lv 32–40 | 3–6 | `map_195`–`map_197` | `map_200` | The Custodian (`mob_150`) | `clockwork` (r08) | `quest_089`–`quest_090` |

Stage maps and finale arenas are allocated in `docs/WORLD_PLAN.md` (R2 / R8 sections) and
`docs/ID_REGISTRY.md`; the boss stat-blocks, arena scripting, and each stage's concrete
objective are authored in Phase D (`15_maps_system/MAPS_SYSTEM.md` owns arena scripting; the
handler quests carry the objective text). The handler-quest pair per raid lives in its home
region's quest block (`docs/ID_REGISTRY.md`, Quests) — this doc references them, it does not
restate their steps.

## 2. Starting a run — entry gates

A party starts a run by talking to the raid's handler NPC and accepting its handler quest
(`quest_087`–`quest_090`, `10_systems/QUESTS.md` shape), which opens the instanced entrance
to the first stage map. Entry is refused unless **every** row below holds at the moment the
party enters:

| Gate | Rule |
|---|---|
| Party required | The starter must be in a `10_systems/social/PARTY.md` party — a solo character cannot start a raid run (the solo path is the open arena, §4). |
| Party size | Live roster **3–6** members. Below 3 the entrance refuses (`15_maps_system/MAPS_SYSTEM.md`); the ceiling is the same flat 6 as `10_systems/social/PARTY.md` §1. |
| Level band | Every entering member's `level` within the raid's band (Undervault 15–22, Mainspring 32–40). A member outside the band cannot enter; the band matches `docs/WORLD_PLAN.md`. |
| Same instance | All entering members pass through the same instanced entrance together — the run is allocated to that party alone (§6). |

The one-free-coach advancement pilgrimage and paid Harthmoor Coachworks travel
(`docs/WORLD_PLAN.md`, `15_maps_system/MAP_CONNECTIONS.md`) get a party to the handler's
town; there is no free warp into the instance itself.

## 3. Stage progression

- **Linear chain.** Each raid is a fixed sequence of party-instanced stage maps (Undervault
  `map_038`→`map_039`→`map_040`; Mainspring `map_195`→`map_196`→`map_197`) ending at the
  finale arena. Stage maps are `dungeon`-type (`docs/WORLD_PLAN.md`; `map` token from
  `00_vision/GLOSSARY.md`).
- **Gated advance.** Each stage carries a completion objective (authored in Phase D via the
  handler quest); clearing it opens the `door` portal to the next stage. The party advances
  together — a member who has not reached the exit does not block the portal, but the
  finale-arena entry re-checks the party-size floor (§2).
- **Finale.** The last portal opens the finale boss arena (§4). The whole instance —
  stages plus arena — is one allocation for the entering party; leaving all stage maps for
  an out-of-chain map ends that member's participation (§6).

The stage objectives, spawn tables, and foothold layouts are Phase D content, not fixed
here; `10_systems/SPAWN.md` owns instanced spawn behavior and
`15_maps_system/MAPS_SYSTEM.md` owns arena/stage scripting.

## 4. The finale boss & the solo open-arena path

The finale reuses the region boss on its own arena map, entered two ways:

- **raid (party-instanced) entry** — reached by clearing the stage chain (§3); the boss is
  allocated to the entering party alone (`10_systems/SPAWN.md`). This is the full-reward
  path (§5).
- **Open (non-raid) entry** — the same arena map has an ordinary open boss entrance that a
  **solo** player (or any party that skips the stages) may use to fight the same boss
  directly, at **reduced reward** (§5). This keeps both bosses soloable content, matching
  `docs/WORLD_PLAN.md`'s "solo players still fight both bosses at reduced reward."

Boss defeat, arena respawn, and a fresh-attempt reset are `10_systems/DEATH_PENALTY.md`
(boss-arena deaths) and `10_systems/SPAWN.md`/`15_maps_system/MAPS_SYSTEM.md`'s — see §7 for
the party bookkeeping this doc owns. Boss CC-immunity for the two finale bosses stands at
`10_systems/STATUS_EFFECTS.md`'s existing boss default (no raid override).

## 5. Rewards & the reduced solo cut

- **Party (full) reward.** A completed raid run's `exp` and loot follow
  `10_systems/social/PARTY.md` exactly — the same-map `exp`-share split (`10_systems/social/PARTY.md`
  §4) and the loot-share modes (`10_systems/social/PARTY.md` §5) — plus the handler quest's
  own completion payout (`10_systems/QUESTS.md`; raid quests must pay `exp`, they are not
  Rift/no-exp content). This doc adds **no** new split math; it only scopes *when* that split
  fires (on a raid finale-boss kill and each handler-quest turn-in).
- **Solo (open-arena) reward.** The open non-raid entry (§4) pays a **reduced** boss reward
  versus the full raid completion — the intended incentive to run the co-op path. The exact
  reduction factor is a `10_systems/DROPS.md` / `10_systems/ECONOMY.md` balance call (Open
  Questions), not fixed here.
- **Boss uniques.** The finale bosses' unique drops (`mob_027` → `item_equip_0203`–`0204`;
  `mob_150` → `item_equip_0215`–`0216`, `docs/ID_REGISTRY.md`) drop and split under
  `10_systems/DROPS.md` + `10_systems/social/PARTY.md` §5 like any boss unique — the open-arena
  cut governs *rate/quantity*, never adds or removes an ID.

## 6. Failure, leavers & roster lock

- **Instance allocated to the party.** Entering a raid (§2) allocates the whole run — stages
  and finale — to that party alone (`10_systems/SPAWN.md`), the same party-instanced model
  `10_systems/social/PARTY.md` relies on. The participating count is fixed at instance
  creation and never re-scales mid-run — not on a fall, a leave, a disconnect, or a late
  arrival (no hidden re-scaling, `00_vision/PILLARS.md` P1).
- **Leaver / disconnect.** A member who leaves the party or disconnects drops out of the
  run; there is **no backfill** into a live instance. The run continues for the remaining
  members. Attrition below the size-3 entry floor does not abort a run already in progress
  (the floor is an entry gate, not a sustain gate); an instance with **no** members left
  closes and its progress is lost.
- **Restart.** A closed or abandoned instance is restarted from the handler NPC (§2) as a
  fresh run — stage progress does not carry over across a closed instance.

## 7. Death, release & re-entry within a run

Within a live run, a fallen member's defeat, self-service recovery, and walk-back are
governed by `10_systems/DEATH_PENALTY.md` (its instanced boss-arena death handling) — not
restated here. This doc fixes only the raid bookkeeping layered on top:

- A **fallen** member stays on the `10_systems/social/PARTY.md` roster and on the party HUD
  plates (`10_systems/social/PARTY.md` §3) in the distinct fallen state that doc already
  defines.
- While fallen and still physically inside the instance, a member remains `exp`/loot-eligible
  (`10_systems/social/PARTY.md` §4–§5) for kills that land before they recover, per that
  doc's same-map rule.
- A member who recovers out of the instance (to a bind town or staging area per
  `10_systems/DEATH_PENALTY.md`) fails the same-instance gate until they walk back through
  the run's entrance while the attempt is still live; if they cannot return before the run
  closes (§6), they forfeit their share of the remainder.

## Server Dependency

Instance allocation, roster-locked participation, `exp`/loot arbitration, and stage/finale
progression are all `authority: server` (`10_systems/PERSISTENCE.md` §1–§2;
`00_vision/PILLARS.md` P6) — a client cannot self-certify who is in the instance or award
itself raid rewards. Raids are **instanced co-op and server-deferred** like the rest of
`10_systems/social/`: **the interim solo build ships the two raids' party path present but
dormant** — no second character exists to form the required 3–6 party, so no raid instance ever
opens. The **solo open-arena boss entries** (§4), by contrast, are single-player content and
playable in the interim build now (`10_systems/DEATH_PENALTY.md` boss-arena rules), at the
reduced reward (§5).

## Open Questions

- **Per-character reward lockout / cooldown between raid completions** (e.g. once-per-day, or
  an entry-item gate) is not derivable from existing docs — undecided. Owner:
  `10_systems/ECONOMY.md` jointly with this doc. Default until set: no lockout (repeatable),
  which the solo/open-arena reduced cut (§5) already discourages farming against.
- The **reduced-reward factor** for the open non-raid arena entry (§4–§5) is unset — a
  `10_systems/DROPS.md` / `10_systems/ECONOMY.md` faucet-balance call.
- Whether the level band (§2) is enforced as a hard floor **and** ceiling, or only a floor
  (letting over-band players assist), is first-pass; default is the full-band check. Retune
  with `10_systems/social/PARTY.md` §4's anti-power-leveling falloff once telemetry exists.
- Whether mid-run attrition below the size-3 floor (§6) should instead soft-abort or offer a
  regroup window is flagged, not resolved; default keeps the run alive for whoever remains.
- The exact split of each handler-quest **pair** (`quest_087`/`088`, `quest_089`/`090`)
  between intro-and-finale roles is Phase D quest-authoring detail
  (`10_systems/QUESTS.md`); this doc only pins the pair-to-raid mapping.
- Whether party-instanced allocation for the two raid arenas is homed in `10_systems/SPAWN.md`
  or `15_maps_system/MAPS_SYSTEM.md` needs one owner to claim it in v2 (the former Rift-arena
  instancing text is being retired) — see Handoffs to the systems/maps lanes.
