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
| `raid_token` | Raid-earned currency spent on raid-exclusive rewards (per-raid variants; 10_systems/social/RAID.md, 10_systems/DROPS.md) |
| `party_drop_bonus` | Drop-chance multiplier from same-map party size (owner: 10_systems/DROPS.md; the loot analogue of PARTY.md §4's exp party bonus) |
| `guild_contribution` | Points a guild accrues from members' raids and party hunts, driving guild level/unlocks (owner: 10_systems/social/GUILD.md) |
| `party_finder` | The server-side listing board for forming parties/raids (owner: 10_systems/social/PARTY_FINDER.md) |
| `nickname` | Player-chosen unique character name (name law: 70_integrations/ACCOUNTS_AUTH.md §5; player-facing flow: 10_systems/ACCOUNT.md) |

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

## Job lines (owner: 10_systems/JOBS.md; branching 2nd jobs)

| Stat | Line token | 1st job (Lv 8) | 2nd-job specializations (Lv 40, choose one) | 3rd tier (future arc) |
|---|---|---|---|---|
| `might` | `bulwark` | Bulwark | Ironbrand (`ironbrand`) · Stoneguard (`stoneguard`) · Warcaller (`warcaller`) | Aegis |
| `finesse` | `keeneye` | Keeneye | Pathstalker (`pathstalker`) · Sureshot (`sureshot`) | Skypiercer |
| `focus` | `weaver` | Weaver | Runeweaver (`runeweaver`) · Cindercall (`cindercall`) · Frostbind (`frostbind`) | Highweaver |
| `fortune` | `flicker` | Flicker | Duskstep (`duskstep`) · Wildcard (`wildcard`) | Nightdancer |

`novice` is the shared pre-advancement class (Lv 1–7). The 2nd advancement (Lv 40) is a
permanent choice of one specialization within the line (rules: 10_systems/JOBS.md). Skill
IDs: `skill_<line>_NNN` plus `skill_novice_NNN`. 3rd-tier jobs are named-and-reserved only —
this run authors two arcs to Lv 80 (Voidshore elites overshoot to 82); the game cap is 300
(initial design; see SCOPE.md).

## Guild crest shapes (owner: 40_assets/UI_ART_SPEC.md; data rules in social/GUILD.md)
`heater` · `round` · `banner` · `diamond` · `crest_ornate`

## Player sprite layers (owner: 40_assets/CHARACTER_COMPOSITING.md; owner directive 2026-07-24)
`base` · `face` · `hair`, plus the seven visible equipment-slot tokens (`weapon` · `head` ·
`body` · `legs` · `boots` · `gloves` · `cape`) reused verbatim as layer names; `ring`/`amulet`
render no layer. Z-order and part classes live in the owner doc, never restated.

## ID prefixes (ranges owned by docs/ID_REGISTRY.md)
`map_NNN` · `mob_NNN` · `item_equip_NNNN` · `item_use_NNNN` · `item_etc_NNNN` ·
`item_cosmetic_NNNN` · `skill_<line>_NNN` · `npc_NNN` · `quest_NNN` · `drop_mob_NNN` ·
`pool_equip_rNN` · `style_<category>_NN` (category ∈ `base`/`hair`/`face`/`skin`/`haircolor`;
40_assets/CHARACTER_COMPOSITING.md) · `season_NNN` (10_systems/BATTLE_PASS.md)

## Region slugs (owner: docs/WORLD_PLAN.md; five-island world)
`emberfoot` · `millbrook` · `verdant` · `tidewatch` · `gloomwood` · `ashfall` · `sunken` ·
`clockwork` · `frostpeak` · `arcane_reach` · `voidshore` (shorthand `r01`–`r11`, in that
order). Islands: **Emberfoot Isle** (r01), **Harthmoor Isle** (r02–r08), and the Arc-2 far
isles **Frostpeak Isle** (r09), **Arcane Reach** (r10), **Voidshore** (r11). Slug `rift` is
reserved for future expansions — invalid in this run's content.

## Raids (owner: 10_systems/social/RAID.md; replaces the retired "party quest"/`pq_*` family)
`raid_undervault` · `raid_mainspring` · `raid_deepfrost` · `raid_voidtide`

## Party-finder activity (owner: 10_systems/social/PARTY_FINDER.md)
`field_hunt` · `raid` · `quest` · `boss` · `social` — the listing categories on the
`party_finder` board.

## Terrain (owner: 15_maps_system/MAP_TRAVERSAL.md; foothold model)
`foothold` (walkable segment, arbitrary angle; the ground truth of platforming) ·
`terrain_chunk` (hand-painted ground art snapped to footholds; ART_BIBLE amendment AB-001)

## Transport (owner: 15_maps_system/MAP_CONNECTIONS.md)
`coach` (paid town-to-town portal kind, fares in shards per ECONOMY.md) · `coach_stop`
(arrival spawn id) · `coach_station` (the coach kiosk interactable;
15_maps_system/MAP_INTERACTABLES.md) · `coach_clerk` / `pier_officer` (transport-staff NPC
roles; 20_schemas/npc.schema.md) · the Harborwind Ferry (paid instant island crossing) ·
`from_ferry` (ferry arrival spawn id; MAP_CONNECTIONS.md §2) · the Deepway (free
Lv-40-gated underground passage, Cindershelf `map_125` → `map_201`–`203` → Frosthaven; owner
WORLD_PLAN.md/MAP_CONNECTIONS.md) · `longship` (paid
**scheduled** Arc-2 inter-island portal kind, 2–3 min real-time sail on a deck map) ·
`longship_deck` (deck boarding spawn id) · `longship_dock` (pier arrival spawn id) ·
`level_gate` (optional portal property: minimum `level` to pass; rules MAP_CONNECTIONS.md §9).
The earlier free-warp "waygate" mechanism is retired — that token is invalid in content.

## Provisional (pending promotion at a phase gate)
- `combo_momentum` — the player-only sustained damage-dealt multiplier built by chaining
  distinct damage sources (basic attack + `deal_damage` actives) inside the chain window ·
  `combo_burst` — the finisher reward for a three-distinct-source sequence. Owner:
  10_systems/COMBO_SYSTEM.md (which also owns all magnitudes/timing). Promote both at the
  next phase gate once content or schemas consume them as field values.
- `gleam` — premium cosmetic-only currency (real money; account-bound; never converts to or
  from `shards`). Owner: 10_systems/MONETIZATION.md (MON-001). OQ: promote or rename at the
  next phase gate.
- `raid_herald` — NPC archetype: the staging-area NPC that fronts a raid's entry
  (10_systems/social/RAID.md). Promote if Phase D NPC content uses it as a field value.
- `guild_level` — a guild's progression tier, raised by `guild_contribution`
  (10_systems/social/GUILD.md §9). Promote if it becomes a field value in guild content/schemas.
- Cosmetic categories — `title` (cosmetic display string; grants from collection milestones,
  10_systems/COLLECTIONS.md §7, and raid SKUs) · `dye` · `skin` · `crest_flourish`; owner
  10_systems/COSMETICS.md (§2), which is the character-display consumer `title`'s original
  promotion condition waited on. Promote all four at the next phase gate once the first
  cosmetic content batch consumes them. (`title` originally ported from the
  equipment-v2/F-gate wave at the v3 merge.)
- `shield` / `overall` — equipment slot tokens from the equipment-v2 wave (off-hand
  defensive piece; body+legs single piece). Semantics: 10_systems/SCROLLS.md's companion
  ITEMS §2 revision, **not yet integrated with the v3 T1–T12 content** — IDs re-homed to
  `item_equip_0181`–`0200` at the v3 merge (see ID_REGISTRY). Promote with that
  integration wave.
- `req_line` — optional equip-restriction field (values = job-line tokens); owner
  10_systems/ITEMS.md. (Equipment-v2 wave.)
- Scroll vocabulary — `scroll_kind` (`aspect` · `temper`), `scroll_tier` (`steady` ·
  `bold` · `perilous`), `slot_family` (`weapon_family` · `armor_family` ·
  `accessory_family`); owner 10_systems/SCROLLS.md. Promote when Phase D scroll content
  lands.
- Charter family (owner: 10_systems/BATTLE_PASS.md; added 2026-07-24, promote at the next
  gate): `charter` (the 30-day seasonal reward ledger — in-world the Wayfarer's Charter) ·
  `charter_free` / `charter_gilt` (track enum: free lane / `shards`-purchased gilt lane) ·
  `charter_mark` (charter progression point) · `season` (one 30-day charter cycle; IDs
  `season_NNN`, block in docs/ID_REGISTRY.md)
- Capsule family (owner: 10_systems/GACHAPON.md; added 2026-07-24 under pillar amendment
  PA-001, the bounded exception to MON-001): `capsule` (the Cogwork Capsule gacha machine /
  interactable kind) · `capsule_ticket` (one pull; item `item_use_0021`) · `capsule_pity`
  (the per-character guaranteed-cosmetic counter)

## Open Questions
- None blocking. (The `haste` move/attack split was resolved at the B gate: kept combined;
  conversion percentages owned by 10_systems/STATS.md §5. Reopen only if animation breakpoints
  demand it. Charter and capsule families promote at the next phase gate — owner
  confirmations 2026-07-24.)
