# PARTY_QUEST.md — Party Quests (Instanced Co-op Runs)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, 10_systems/social/PARTY.md, 10_systems/QUESTS.md, 10_systems/SPAWN.md,
10_systems/DEATH_PENALTY.md, 10_systems/DROPS.md, 10_systems/LEVELING.md,
10_systems/COMBAT_FORMULA.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_CONNECTIONS.md,
15_maps_system/MAP_INTERACTABLES.md, 10_systems/PERSISTENCE.md, 10_systems/HUD.md

Owner doc for the **party quest** (`pq_*`) concept: what a PQ is, its stage/finale structure, the
entry gate, instance lifecycle, and reward policy. `docs/WORLD_PLAN.md` fixes *which* maps and
bosses each PQ uses; `docs/ID_REGISTRY.md` owns the `pq_<name>` tokens and the handler-quest ID
block; party membership/size rules are `10_systems/social/PARTY.md`'s; party-instance spawning is
`10_systems/SPAWN.md` §7's; fallen/Release flow is `10_systems/DEATH_PENALTY.md` §5.3's. This doc
consumes all of those and owns only the PQ-specific rules that none of them state.

## 1. The two party quests (this arc)

Two instanced co-op runs; each ends at an **existing region boss** — a PQ mints no extra boss
slots (`docs/WORLD_PLAN.md` "Party quests").

| Token | Name | Level band | Party | Stage maps | Finale arena | Finale boss |
|---|---|---|---|---|---|---|
| `pq_undervault` | Undervault Heist | 15–22 | 3–6 | `map_038`–`map_040` | `map_042` | The Cellar King (`mob_027`) |
| `pq_mainspring` | Mainspring Trial | 32–40 | 3–6 | `map_195`–`map_197` | `map_200` | The Custodian (`mob_150`) |

Future PQs mint their `pq_<name>` token in `docs/ID_REGISTRY.md` first, then add a row here.

## 2. Entry gate

- **Party of 3–6, no exceptions.** The 3-member floor is this doc's rule (a PQ is co-op content;
  below 3 the stage mechanics degenerate); the 6 cap is `10_systems/social/PARTY.md` §1's flat
  party cap, not a second number.
- **Level floor is hard**: every member must be at or above the band's minimum (15 / 32). There is
  **no upper cap** — over-leveled members may enter; the `exp` falloff
  (`10_systems/COMBAT_FORMULA.md` §9, `10_systems/social/PARTY.md` §4) makes farming down-band
  unrewarding without a trap wall (`00_vision/PILLARS.md` P2).
- **The leader triggers entry** at the PQ's entry portal with the full party present on that map;
  entry allocates a fresh party instance (`10_systems/SPAWN.md` §7 mechanism, applied to the PQ's
  stage chain and finale). The Undervault entry stands in Millbrook Central's undervault quarter
  (`map_018`); the Mainspring entry stands in the Clockwork gearworks approach to `map_195`.
  Concrete portal/interactable authoring is Phase D map work (`20_schemas/map.schema.md`), not
  fixed here.

## 3. Stage rules

- Stages are an **ordered chain**: each stage map's exit portal is sealed until that stage's
  objective completes, then opens to the next stage; the last stage opens into the finale arena.
- **Stage objectives reuse existing mechanisms only** — `kill`-pattern clears
  (`10_systems/SPAWN.md` zone spawns scoped to the instance), `collect`/`quest_object` interactions
  (`15_maps_system/MAP_INTERACTABLES.md` §10), and `reach` triggers (`10_systems/QUESTS.md` §3
  vocabulary). No PQ-only mechanic types are minted; concrete per-stage objectives are Phase D
  content authored in the stage map + handler quest files.
- **Leaving the instance** (portal out, party leave/kick, logout past the grace in §5) removes that
  character from the run; they may walk back in through the entry portal while the run is live.

## 4. Finale rules

- The finale is the region's **existing arena and boss** (`15_maps_system/MAPS_SYSTEM.md` §8),
  fought **party-instanced**: the PQ instance carries into the arena, and the boss's `life` scales
  with party size per `10_systems/COMBAT_FORMULA.md` §13.3 (`N` fixed at instance creation —
  `10_systems/social/PARTY.md` §6 bookkeeping).
- **Open entry still exists.** Solo (or non-PQ) players fight the same boss through the arena's
  normal open `door` at the unscaled `boss` budget (`10_systems/COMBAT_FORMULA.md` §13.2), on the
  shared-arena rules of `15_maps_system/MAPS_SYSTEM.md` §8 — at reduced reward (no §6 PQ
  completion rewards; the boss's own `10_systems/DROPS.md` §5.3 table only).

## 5. Death, release & disconnect

Deaths inside a PQ (stages and finale alike) use `10_systems/DEATH_PENALTY.md` §5.3's
party-instance flow — fallen state, self-service Release to the map holding the PQ entry portal,
walk-back re-entry while the run is live, full-wipe reset. A disconnected member is treated as
having left (§3) after a **60 s grace**; reconnecting inside the grace restores them in place.
The run itself dissolves when the party completes the finale, fully wipes in it, disbands, or
every member has left the instance.

## 6. Rewards

- **Handler quests** (`quest_087`–`quest_090`, `docs/ID_REGISTRY.md`: intro + completion per PQ,
  cast in R2/R8's NPC blocks) carry the one-time PQ rewards through the normal
  `10_systems/QUESTS.md` §4–§5 budget bands — no PQ-specific reward currency or budget table
  exists.
- **Repeat value is drops.** A PQ is freely repeatable with no lockout (`00_vision/PILLARS.md`
  P2); each finale kill pays the boss's ordinary `10_systems/DROPS.md` §5.3 table (including the
  first-ever-clear unique guarantee, which triggers on the character's first kill of that boss
  through either entry). Stage monsters pay their normal tables. The one-time handler quests do
  **not** repeat (`10_systems/QUESTS.md` §7 — no repeatable quests at launch).
- `exp` inside a PQ follows the ordinary party split (`10_systems/social/PARTY.md` §4); a PQ is a
  loot-and-story path, not the fast `exp` path (`10_systems/LEVELING.md` §3's tier policy).

## Server Dependency

Instance allocation, stage-objective state, and reward arbitration are `authority: server`
(`10_systems/PERSISTENCE.md`; `00_vision/PILLARS.md` P6). **The interim solo build ships PQs
present but dormant** — the entry requires a party of 3, which the solo build cannot form
(`10_systems/social/PARTY.md` Server Dependency); both finale bosses stay reachable solo through
the open arena entry (§4).

## Open Questions

- Concrete per-stage objectives (and whether either PQ wants a light puzzle beat built from
  `quest_object` interactions) are Phase D authoring; this doc fixes only the mechanism whitelist
  (§3).
- Whether the 3-member floor should drop to 2 if live telemetry shows the party-forming funnel is
  too tight at the 15–22 band; default holds at 3.
- A PQ-completion collection/`title` hook (`10_systems/COLLECTIONS.md`) is deliberately not wired
  in this pass; flag for that doc's owner if PQ completion should feed a milestone.
- The disconnect grace (60 s, §5) is first-pass; confirm against `10_systems/PERSISTENCE.md`'s
  reconnect semantics once the server pass designs them.
