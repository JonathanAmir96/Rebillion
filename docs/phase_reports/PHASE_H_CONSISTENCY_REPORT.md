# PHASE_REPORT — Phase H (Consistency Wave: v2 stragglers, missing owners, validator)

Status: **complete** (2026-07-23, single-session wave). Scope: close the debt standing between
the tree and Phase D — the never-run B-revision straggler wave, two declared-but-missing owner
docs, four blocked C-gate decisions, the batch validator, and the F/G cross-doc leftovers.

## 1. v2 straggler wave (the B-revision SCOPE.md flagged)

~30 docs still described the v1 world (Lv 100 cap, 12 regions, Rift raids, free waygates).
Every remnant re-anchored to v2 (two islands, 8 regions/bosses, 2 PQs, arc Lv 1–42, cap 300):

- **Raid tier → future arcs.** PARTY §6, SPAWN §7, DEATH_PENALTY §5.3, DROPS §5.4,
  STATUS_EFFECTS §3, COMBAT_FORMULA §13.2/§13.3 re-anchored to the PQ-instanced finales
  (`pq_life = normal_life·70·N`, boss-row damage, 10-min enrage, TTK ≈ 6.2 min across N=3–6);
  raid table shapes/enums removed from drop_table/monster/quest/item schemas (`raid`
  rarity row kept as an explicitly reserved future-arc token).
- **Waygates → paid Coachworks.** MAP_CONNECTIONS §1/§3/§4/§6 rewritten (no unlock state, paid
  rides, ferry pattern); MAP_INTERACTABLES §2/§9 (`coach` portal kind, `coach_station` object);
  map/npc schemas renamed end-to-end (`coach_stop` spawn, `coachman` role, `coach` service);
  ECONOMY gains §4.3 travel fares + a §2 sink row (WORLD_PLAN's fare-owner hook, previously
  dangling).
- **v2 numbers propagated.** Job gates 8/40 with per-line home-town instructors (JOBS §1);
  13 authored skills/line = 56 total (JOBS §7, SKILL_SYSTEM); tier grid T1–T6 authored at
  `req_level` 1/8/15/22/29/36, T7–T10 reserved (ITEMS §4); 8 boss uniques `0201`–`0216`
  (ITEMS §11); five bind towns with v2 map IDs (DEATH_PENALTY §4, INVENTORY §7); 8 region pools
  (DROPS §6 + schemas); monster `level` 1–42 and 118/24/8 tier counts (monster.schema); quest
  `exp` exemption for "Rift-band" quests removed (QUESTS §4, quest.schema); map-type counts and
  the 8-biome tileset table (MAPS_SYSTEM §2, MAP_LAYERS §4); v2 tonic bands + `steady` scroll
  shelf (ECONOMY §4.1); telemetry `evt_release`/death contexts (TELEMETRY_ANALYTICS).
- **Terminus re-decision.** MAP_CONNECTIONS §7's v1 Frostpeak/Clockwork chutes died with the v1
  graph; re-decided for v2 as one Sunken Depths drop chute (`map_176` → `map_094`,
  `from_sunken`, `dead_end`). VALIDATION §5 now names the authorized edge set (WORLD_PLAN table
  + §7 addition).
- **Curve framing.** LEVELING presents the curve formula-first (detail table = reference;
  authored arc top Lv 42 ≈ 1.75 M cumulative `exp`); §6 rewritten as the soft-asymptote
  "beyond the arc" policy; growth-past-Lv-100 flagged as future-arc OQs in STATS/SKILL_SYSTEM.

## 2. New owner docs (previously declared but missing)

- **`10_systems/social/PARTY_QUEST.md`** — pq_* owner (GLOSSARY/SCOPE/ID_REGISTRY/WORLD_PLAN all
  pointed at it): stage/finale structure, 3–6 party gate with hard level floor, instance
  lifecycle, death/release via DEATH_PENALTY §5.3, handler-quest rewards (`quest_087`–`090`),
  repeat value = drops.
- **`40_assets/SKILL_ANIMATION.md`** — skill animation clip registry (VALIDATION §6's naming
  owner): `skill_<line>_NNN_cast` anchor + derived suffixes (`_proj`/`_impact`/`_loop`/`_proc`),
  sync bound to ANIMATION_TIMING's hit-frame contract. Forward-reference notes in
  ANIMATION_STATES/skill.schema/SPRITESHEET resolved.

## 3. C-gate decisions closed (in owning docs)

1. `base_move_speed` = **128 px/s** (COMBAT_FORMULA §10 adopts MAP_TRAVERSAL's 8 tiles/s at the
   AB-001 16 px grid; 200 px/s placeholder retired).
2. `docs/ID_REGISTRY.md` reserves **`mob_ability_<mob_NNN>_01`–`_08`** (per-monster ability
   namespace) and **`mob_151`–`mob_160`** (summon templates, count-exempt) — unblocks boss kits
   and `summon_entity.entity_ref`.
3. SKILL_EFFECTS **`condition` enum frozen**: `below_life_pct:X` · `while_veiled` · `vs_marked`
   · `while_stance` (validator-checkable).
4. VALIDATION §5 **authorized-edge-set wording** (see §1).

## 4. Validator (`tools/validate.py`)

Implements VALIDATION checks 1–4 + the H1/Open-Questions structure gate; locked files and phase
reports exempt; content checks (front-matter, ID range/uniqueness) activate as `50_content/`
lands. First full-tree run caught real breaks, all fixed in the same commit: wrong
`10_systems/PARTY.md` paths (actual home `social/`), GUILD's dangling `guild.schema.md` path,
ART_GENERATION_RUNBOOK's `docs/CLAUDE.md` path. **Tree validates clean: 80 files, 0 fails.**

## 5. F/G cross-doc leftovers closed

- MAPS_SYSTEM §5 tag-catalog governance → AUDIO_DESIGN (per the F-wave decision).
- ECONOMY §4.1 `steady` scroll price rows (SCROLLS' filed question).
- SCOPE count bumps: equip ~86 → ~98, use ~30 → ~48.
- COLLECTIONS `sighted` radius confirmed: `max(aggro_radius, 6)` tiles, standard vertical band.
- Still open (deliberately, owner-priced): the COLLECTIONS set-completion `shards` faucet
  amendment (titles-only until an ECONOMY faucet-list amendment lands).

## Open Questions rollup

No new open questions were minted by this wave; resolutions above struck their entries in the
owning docs (STATUS_EFFECTS, COMBAT_FORMULA, MAP_TRAVERSAL, MAP_CONNECTIONS, AI_BEHAVIOR,
SKILL_EFFECTS, skill.schema, ANIMATION_STATES, COLLECTIONS, MAPS_SYSTEM, SCOPE). Everything else
in the per-doc `## Open Questions` sections stands as the pre-D backlog; the E-gate rollup into
VALIDATION.md remains Phase E work.
