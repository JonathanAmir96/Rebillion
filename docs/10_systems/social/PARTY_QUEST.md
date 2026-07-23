# PARTY_QUEST.md — Party Quests (Instanced Co-op Runs)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/social/PARTY.md, 10_systems/QUESTS.md, 10_systems/DROPS.md,
10_systems/DEATH_PENALTY.md, 10_systems/SPAWN.md, 10_systems/PERSISTENCE.md,
15_maps_system/MAPS_SYSTEM.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for **party quests** (`pq_*` tokens, `docs/ID_REGISTRY.md`): what a PQ is, the run
flow through stages to the finale, the solo open-entry rule, and PQ-specific reward shaping.
Party membership, exp share, and loot distribution are `10_systems/social/PARTY.md`; drop-table
shapes are `10_systems/DROPS.md`; the handler quests' anatomy is `10_systems/QUESTS.md`; death
consequences are `10_systems/DEATH_PENALTY.md`; instance allocation is `10_systems/SPAWN.md`
with map/arena scripting in `15_maps_system/MAPS_SYSTEM.md`. This doc restates none of those.

## 1. Definition

A party quest is an **instanced co-op run** for a **registered party of 3–6**
(`10_systems/social/PARTY.md` §1): a short chain of party-instanced stage maps ending at a boss
arena. The two PQs are the game's **only party-instanced content** (`00_vision/SCOPE.md`); there
are no raids or other instanced group formats in this run. Entry goes through the PQ's **handler
NPC** and its handler quests `quest_087`–`quest_090` (2 per PQ; anatomy owned by
`10_systems/QUESTS.md`, cast in the R2/R8 NPC blocks per `docs/ID_REGISTRY.md`).

## 2. The two party quests (allocation: `docs/WORLD_PLAN.md`)

| PQ | Level band | Stages | Finale arena | Finale boss |
|---|---|---|---|---|
| `pq_undervault` — Undervault Heist | Lv 15–22 | `map_038`–`map_040` | `map_042` (The Cellar Deep) | The Cellar King (`mob_027`) |
| `pq_mainspring` — Mainspring Trial | Lv 32–40 | `map_195`–`map_197` | `map_200` (The Mainspring) | The Custodian (`mob_150`) |

The finale bosses are the **existing regional bosses** — a PQ adds no extra boss slots
(`docs/WORLD_PLAN.md`); the finale is a party-instanced allocation of the same arena encounter.

## 3. Run flow

1. The party leader starts the run at the handler NPC with a registered party of 3–6 present;
   `10_systems/SPAWN.md` §7 allocates the instance to that party alone.
2. Stages run **in order** (`map_038`→`039`→`040`, `map_195`→`196`→`197`); clearing a stage's
   objective opens the portal to the next. Stage objectives and scripting are Phase D map data
   (`15_maps_system/MAPS_SYSTEM.md`).
3. The final stage opens into the **finale arena** and the boss fight. Clearing it ends the run;
   the party exits to the arena's parent region.

## 4. Solo open entry (reduced reward)

Each finale arena also keeps its ordinary **open (non-PQ) entry**: a solo player may walk in and
fight the boss without a party or handler quest (`docs/WORLD_PLAN.md`). Open-entry kills pay a
**reduced reward** relative to a PQ finale kill — this doc owns that shaping; the reduction
multiplier is first-pass **deferred to Phase D balance** (Open Questions). Stages are PQ-only;
open entry reaches the arena, never the stage chain.

## 5. Rewards

- **Boss drops** follow the standard `10_systems/DROPS.md` §5.3 boss shape (see its §5.4 note);
  in-party distribution follows `10_systems/social/PARTY.md` §5, exp share its §4 — this doc
  narrows neither in this pass.
- **Handler-quest rewards** (`quest_087`–`quest_090`) are ordinary quest rewards, budgeted and
  shaped by `10_systems/QUESTS.md` / `10_systems/ECONOMY.md`.
- Any PQ-only completion bonus beyond these is not designed in this pass (flag to
  `10_systems/DROPS.md` if one is added — its OQ tracks the hook).

## 6. Death in a party quest

Standard `10_systems/DEATH_PENALTY.md` rules apply — no PQ-specific penalty. A fallen member
stays on the roster in the fallen state (`10_systems/social/PARTY.md` §6) and, on release, is
**released to the instance entrance** (the PQ's handler-side entry point) rather than their bind
town, so a live run can be rejoined by walking back in while the party holds the instance.

## 7. Server dependency

Party quests are **server-dependent** content: instance allocation, stage state, and reward
arbitration are `authority: server` (`10_systems/PERSISTENCE.md`; `00_vision/PILLARS.md` P6).
**The interim solo build** matches `10_systems/PERSISTENCE.md`'s solo stance: no party can form
(`10_systems/social/PARTY.md` Server Dependency), so the stage chain is unreachable — but the §4
solo open entry works, so both finale bosses remain fightable solo at reduced reward.

## Open Questions

- The exact reduced-reward multiplier for §4 open-entry kills (drop-side and/or exp-side) is a
  Phase D balance call with `10_systems/DROPS.md`/`10_systems/LEVELING.md`.
- Whether cleared stages are replayable for no reward (practice runs) or simply closed until a
  new run starts. Default: closed.
- Lockout/cooldown — runs per party or per character per day, if any. Default: none at launch;
  revisit against the `10_systems/ECONOMY.md` faucet balance.
- Contribution rules inside stages (whether stage objectives require per-member participation or
  any-member completion counts for all). Default: any-member, mirroring
  `10_systems/social/PARTY.md` §4's kill-credit sharing.
