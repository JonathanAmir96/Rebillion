# GLOSSARY.md — Canonical Vocabulary (Tokens Are Law)

The only legal tokens for stats, resources, currency, and shared enums. Every doc, schema, and
content file uses these spellings exactly (snake_case, US spelling). Semantics live in each
family's **owner doc** — this file defines the token and one-line gloss only; never restate
rules here, and never restate this list elsewhere. Legacy genre terms are **banned**; the
canonical banned-token list lives in `docs/VALIDATION.md` §1 (the only file allowed to spell
them out).

New term needed? Add it under **Provisional** with an Open Question. Silent invention of tokens
anywhere else in the tree is a validation failure.

## Primary stats (owner: 10_systems/STATS.md)

| Token | Abbrev | Gloss |
|---|---|---|
| `might` | MGT | Melee/physical power stat |
| `finesse` | FIN | Ranged/precision stat |
| `focus` | FOC | Spell/essence stat |
| `fortune` | FOR | Crit, evasion, and drop-luck stat |

## Derived stats (owner: 10_systems/STATS.md)

| Token | Gloss |
|---|---|
| `life` | Survival resource pool; 0 = defeat |
| `essence` | Skill resource pool |
| `power` | Weapon attack rating |
| `spellpower` | Magic attack rating |
| `armor` | Physical defense rating |
| `warding` | Magic defense rating |
| `precision` | Accuracy rating (hit chance input) |
| `evasion` | Avoidance rating |
| `crit_rate` | Critical hit chance |
| `crit_power` | Critical hit damage multiplier |
| `haste` | Movement + attack speed rating |

## Meta tokens

| Token | Gloss |
|---|---|
| `shard` / `shards` | Currency (singular / plural) |
| `exp` | Experience points token |
| `level` | Character/monster level |
| `emberstone` | Enhancement material (10_systems/ENHANCEMENT.md); visual flavor may be reskinned by ART_BIBLE amendment |

## Entity tiers (owner: 20_schemas/monster.schema.md)
`normal` · `elite` · `boss`

## Rarity (owner: 10_systems/ITEMS.md; colors locked in 40_assets/ART_BIBLE.yaml `rarity_code`)
`common` · `uncommon` · `rare` · `epic` · `legendary`

## Elements (owner: 10_systems/ELEMENTS.md)
`neutral` · `fire` · `frost` · `nature` · `arcane` · `shadow`
(`frost` covers water/ice/cold; `neutral` is un-attuned physical.)

## Status effects (owner: 10_systems/STATUS_EFFECTS.md)
Debuffs: `burn` · `poison` · `chill` · `freeze` · `stun` · `root` · `silence` · `blind` ·
`sunder` · `weaken`
Buffs: `empower` · `fortify` · `swiftness` · `regen` · `clarity` · `veil`
Cleanse tags (promoted at B gate): `burn_type` · `poison_type` · `chill_type` ·
`control_type` · `sense_type` · `curse_type`

## AI profiles (owner: 10_systems/AI_BEHAVIOR.md)
`passive_wanderer` · `timid_grazer` · `aggressive_charger` · `territorial_guard` ·
`ambush_lurker` · `ranged_skirmisher` · `aerial_swooper` · `pack_hunter` · `support_caller` ·
`kamikaze_burster` · `stationary_turret` · `boss_scripted`

## Skill effect ops (owner: 10_systems/SKILL_EFFECTS.md)
`deal_damage` · `apply_status` · `cleanse_status` · `heal` · `restore_essence` ·
`grant_shield` · `knockback` · `pull` · `dash` · `leap` · `taunt` · `summon_entity` ·
`passive_stat_bonus` · `on_hit_proc`

## Skill targeting (owner: 10_systems/SKILL_SYSTEM.md)
`melee_arc` · `line` · `projectile` · `aoe_circle` · `self` · `party`

## Animation states (owner: 40_assets/ANIMATION_STATES.md)
`idle` · `walk` · `jump` · `fall` · `climb` · `attack` · `cast` · `hit` · `die` ·
`telegraph` · `phase_shift` · `spawn`

## Map types (owner: 15_maps_system/MAPS_SYSTEM.md)
`field` · `dungeon` · `town` · `interior` · `arena` · `secret`

## Equipment slots (owner: 10_systems/ITEMS.md)
`weapon` · `head` · `body` · `legs` · `boots` · `gloves` · `cape` · `ring` · `amulet`

## Weapon types (owner: 10_systems/ITEMS.md; one per job line)
`blade` (might) · `bow` (finesse) · `staff` (focus) · `dirk` (fortune)

## Size classes (locked by 40_assets/ART_BIBLE.yaml `sizing.size_classes`)
`tiny` · `small` · `medium` · `large` · `boss`

## Job lines (owner: 10_systems/JOBS.md; promoted at B gate, revised v2)

| Stat | Line token | 1st job (Lv 8) | 2nd job (Lv 40) | 3rd job (future arc) |
|---|---|---|---|---|
| `might` | `bulwark` | Bulwark | Ironbrand | Aegis |
| `finesse` | `keeneye` | Keeneye | Pathstalker | Skypiercer |
| `focus` | `weaver` | Weaver | Runeweaver | Highweaver |
| `fortune` | `flicker` | Flicker | Duskstep | Nightdancer |

`novice` is the shared pre-advancement class (Lv 1–7). Skill IDs: `skill_<line>_NNN` plus
`skill_novice_NNN`. 3rd jobs are named-and-reserved only — this run authors the Lv 1–42
arc; the game cap is 300 (initial design; see SCOPE.md).

## Guild crest shapes (owner: 40_assets/UI_ART_SPEC.md; data rules in social/GUILD.md)
`heater` · `round` · `banner` · `diamond` · `crest_ornate`

## Player sprite layers (owner: 40_assets/CHARACTER_COMPOSITING.md; owner directive 2026-07-24)
`base` · `face` · `hair`, plus the seven visible equipment-slot tokens (`weapon` · `head` ·
`body` · `legs` · `boots` · `gloves` · `cape`) reused verbatim as layer names; `ring`/`amulet`
render no layer. Z-order and part classes live in the owner doc, never restated.

## ID prefixes (ranges owned by docs/ID_REGISTRY.md)
`map_NNN` · `mob_NNN` · `item_equip_NNNN` · `item_use_NNNN` · `item_etc_NNNN` ·
`skill_<line>_NNN` · `npc_NNN` · `quest_NNN` · `drop_mob_NNN` · `pool_equip_rNN` ·
`style_<category>_NN` (category ∈ `base`/`hair`/`face`/`skin`/`haircolor`;
40_assets/CHARACTER_COMPOSITING.md)

## Region slugs (owner: docs/WORLD_PLAN.md; v2 two-island world)
`emberfoot` · `millbrook` · `verdant` · `tidewatch` · `gloomwood` · `ashfall` · `sunken` ·
`clockwork` (shorthand `r01`–`r08`, in that order). Islands: **Emberfoot Isle** (r01) and
**Harthmoor Isle** (r02–r08). Slugs `frostpeak` / `arcane_reach` / `voidshore` / `rift` are
reserved for future expansions — invalid in this run's content.

## Party quests (owner: 10_systems/social/PARTY_QUEST.md)
`pq_undervault` · `pq_mainspring`

## Terrain (owner: 15_maps_system/MAP_TRAVERSAL.md; v2.4 foothold model)
`foothold` (walkable segment, arbitrary angle; the ground truth of platforming) ·
`terrain_chunk` (hand-painted ground art snapped to footholds; ART_BIBLE amendment AB-001)

## Transport (owner: 15_maps_system/MAP_CONNECTIONS.md; v2.2)
`coach` (paid town-to-town portal kind, fares in shards per ECONOMY.md) · `coach_stop`
(arrival spawn id) · the Harborwind Ferry (paid island crossing). The earlier free-warp
"waygate" mechanism is retired — that token is invalid in content.

## Provisional (pending promotion at a phase gate)
- None currently. (Job lines, cleanse tags, and crest shapes were promoted at the B gate.)

## Open Questions
- ~~Split `haste` into move/attack tokens?~~ **Resolved at B gate:** kept combined; conversion
  percentages owned by 10_systems/STATS.md §5. Reopen only if animation breakpoints demand it.
