# monster.schema.md — One-file-per-monster content shape (mob_NNN)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/STATS.md, 10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/AI_BEHAVIOR.md, 10_systems/SPAWN.md, 10_systems/DROPS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md, 10_systems/LEVELING.md,
10_systems/PERSISTENCE.md, 20_schemas/drop_table.schema.md, 40_assets/ART_BIBLE.yaml,
40_assets/ANIMATION_STATES.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md, docs/VALIDATION.md

## Purpose

Defines the content shape of one **monster** (`mob_NNN`) — the 150 designs in `00_vision/SCOPE.md`
(118 `normal` + 24 `elite` + 8 `boss`, including summon templates authored the same way). A
monster file is the data a Phase D author fills and the coding pass loads: a stat block copied from
the `10_systems/COMBAT_FORMULA.md` §13 budget, an `ai_profile` from `10_systems/AI_BEHAVIOR.md`, an
element affinity set from `10_systems/ELEMENTS.md`, elite/boss abilities composed from the
`10_systems/SKILL_EFFECTS.md` op registry, a `drop_mob_NNN` reference, and the animation/asset
contract. It is read by the combat pipeline (`10_systems/COMBAT_FORMULA.md`), the spawner
(`10_systems/SPAWN.md`), the AI runtime (`10_systems/AI_BEHAVIOR.md`), the loot roller
(`10_systems/DROPS.md`), and the art pipeline (`40_assets/*`). This schema owns the **field shape
and the enum owner** for every field; it never restates the systems' math or rules — it cites them.

This schema is also the **owner of the `tier` enum** (`00_vision/GLOSSARY.md` Entity tiers →
owner `20_schemas/monster.schema.md`) and the entity that `10_systems/SKILL_EFFECTS.md` §12 and
`10_systems/AI_BEHAVIOR.md` §15 point at for summon-template and boss-ability entity shapes.

## File conventions

- **One entity per file.** `50_content/monsters/mob_NNN.yaml`, zero-padded three digits,
  `mob_001`–`mob_150` (`docs/ID_REGISTRY.md` Monsters block). No batch tables — monsters carry
  per-entity AI, abilities, and affinities, so each is its own file.
- The file's `id` **is** its filename stem; both are immutable (`docs/ID_REGISTRY.md`).
- **Tier is fixed by the ID slot.** `docs/ID_REGISTRY.md` lays out each region's block as
  normals-first, then elites, then boss(es); a file's `tier` must match the slot its `mob_NNN`
  occupies (`docs/VALIDATION.md` §4). This schema does not restate the per-region slot numbers.
- Region, level band, biome ramp, and element mix for a monster's `mob_NNN` are its region section
  in `docs/WORLD_PLAN.md`; a Phase D region batch treats that section as its brief.

## Fields

These are **static content-definition** files, loaded identically by client and server; the
`authority` tag in a note marks who owns the *runtime effect* the field drives, per
`10_systems/PERSISTENCE.md` §1 (`server` = truth is the server's resolution; `client` = local
presentation; `shared` = both, client-predicts). Front-matter obeys `docs/VALIDATION.md` check 3.

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `mob_NNN` | yes | `docs/ID_REGISTRY.md` Monsters | Zero-padded; immutable; must fall in-block and in the correct tier slot (`docs/VALIDATION.md` §4). `server` (identity). |
| `schema` | string | yes | this file | Literal `20_schemas/monster.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list[doc name] | yes | `docs/VALIDATION.md` §3 | Bare `SYSTEM_DOC_NAMES` this file depends on. Normal baseline: `[COMBAT_FORMULA, STATUS_EFFECTS, AI_BEHAVIOR, DROPS, ELEMENTS]`; add `SKILL_SYSTEM, SKILL_EFFECTS` when `abilities` present, `SPAWN` when `respawn_override` set, `LEVELING` recommended (`exp`). |
| `name` | string | yes | — | Display name, US spelling. `client`. |
| `tier` | enum | yes | this schema → **Enums** | `normal` \| `elite` \| `boss`. `server`. Must match ID slot (Validation). |
| `element` | enum | yes | `10_systems/ELEMENTS.md` | **Primary** element: drives the palette ramp/tint (`10_systems/ELEMENTS.md` §4.1, `40_assets/ART_BIBLE.yaml`) and the element of `neutral`-unless-flagged touch damage (`10_systems/COMBAT_FORMULA.md` §13.1). `server` (mult) + `client` (tint). |
| `weak_to` | list[element] | no — default `[]` | `10_systems/ELEMENTS.md` §2 | ×1.5 elements. Mutually exclusive with `resists`/`immune_to`. Keep lists short/thematic (`10_systems/ELEMENTS.md` §2). `server`. |
| `resists` | list[element] | no — default `[]` | `10_systems/ELEMENTS.md` §2 | ×0.5 elements. `server`. |
| `immune_to` | list[element] | no — default `[]` | `10_systems/ELEMENTS.md` §2 | ×0 elements (short-circuits at pipeline step 2). Rare. `server`. |
| `level` | int | yes | `10_systems/COMBAT_FORMULA.md` §13; `docs/WORLD_PLAN.md` | Authored 1–42 this arc (`00_vision/SCOPE.md`; the field's legal range is 1–300, the game cap — values above 42 are future-arc content). Keys the stat budget, `exp`, level dampener, and CC tier scaling. `server`. |
| `size_class` | enum | yes | `40_assets/ART_BIBLE.yaml` `sizing.size_classes` | `tiny`\|`small`\|`medium`\|`large`\|`boss`. Drives sprite size **and** the knockback/CC size multiplier (`10_systems/COMBAT_FORMULA.md` §11 — `boss` size = knockback-immune). `shared`. |
| `stats` | map | yes | `10_systems/COMBAT_FORMULA.md` §13/§13.2; `10_systems/LEVELING.md` §3 | Sub-fields below. **All values are copied from the §13 monster budget** (formulas authoritative, §13.2 tier multipliers) — this schema never restates them. `server`. |
| `stats.life` | int | yes | `COMBAT_FORMULA` §13 | Survival pool. Within ±15% of budget (Validation). |
| `stats.power` | int | yes | `COMBAT_FORMULA` §13 | Weapon rating; drives touch damage (§13.1) and ability scaling (`10_systems/SKILL_EFFECTS.md` §1). |
| `stats.spellpower` | int | **no** (casters) | `COMBAT_FORMULA` §13 | Present only when the mob's abilities/touch scale on magic (parity with `power`, §13). Budget-checked if present. |
| `stats.armor` | int | yes | `COMBAT_FORMULA` §13 | Physical defense. Reallocatable with `warding` keeping the **sum** ≈ the §13 defense budget (Validation). |
| `stats.warding` | int | yes | `COMBAT_FORMULA` §13 | Magic defense. |
| `stats.precision` | int | yes | `COMBAT_FORMULA` §13 | At-level hit baseline (`4·level`). |
| `stats.evasion` | float (%) | yes | `COMBAT_FORMULA` §13 | Kept low by budget; monsters barely dodge. |
| `stats.exp` | int | yes | `10_systems/LEVELING.md` §3 | Per-kill `exp` reward = `exp_per_kill_normal(level) × tier_mult` (§3). The level-difference dampener is applied at award time (`10_systems/COMBAT_FORMULA.md` §9), **not** stored here. |
| `ai_profile` | enum | yes | `10_systems/AI_BEHAVIOR.md` | Exactly one of the 12 profiles. `server`. |
| `ai_params` | map | no | `10_systems/AI_BEHAVIOR.md` §2–§13 | Overrides **only** tunables the chosen profile declares (plus shared §2 tunables it has, e.g. `leash_radius`, `aggro_vertical_band`). Values are `snake_case` → number/bool. `server`. |
| `abilities` | list | **elite/boss only** | `10_systems/SKILL_EFFECTS.md` §17; `10_systems/SKILL_SYSTEM.md` §6 | Named ability rows composed from the op registry. **Forbidden on `normal`** (Validation); required (≥1) on `elite`/`boss`. `server`. Sub-fields below. |
| `abilities[].id` | string (file-local key) | yes | `10_systems/AI_BEHAVIOR.md` §15 (OQ) | `snake_case`, unique within the file; referenced by `phases[].added_abilities`. Not a global ID (see Open Questions). |
| `abilities[].name` | string | yes | — | Display name. `client`. |
| `abilities[].targeting` | token \| map | yes | `10_systems/SKILL_SYSTEM.md` §6 | A shape token (uses §6 geometry defaults) **or** `{shape, <geometry per §6>}`. |
| `abilities[].cooldown` | float s | yes | — | Per-ability real-time cooldown. AI pacing/telegraph feel is the `ai_profile`'s (`10_systems/AI_BEHAVIOR.md`). `server`. |
| `abilities[].telegraph_s` | float s | yes | `10_systems/AI_BEHAVIOR.md` §2 | Wind-up duration; elite/boss abilities **must** play the `telegraph` animation state (`docs/VALIDATION.md` §6), which must appear in `animation_states`. |
| `abilities[].effects` | list[op] | yes | `10_systems/SKILL_EFFECTS.md` §3–§16 | Ordered effect list (same composition rules as skills, §2 there). Magnitudes scale on this mob's `power`/`spellpower` per `10_systems/SKILL_EFFECTS.md` §1 — **never restated in-file**. |
| `phases` | list | **`boss_scripted` only** | `10_systems/AI_BEHAVIOR.md` §15 | The boss phase contract. Forbidden unless `ai_profile: boss_scripted` (Validation). `server`. Sub-fields below. |
| `phases[].phase_id` | int | yes | `AI_BEHAVIOR` §15 | 1-based, ascending. |
| `phases[].life_threshold_pct` | number | yes | `AI_BEHAVIOR` §15 | Enter when boss `life` first drops ≤ this % of max. `phase_id: 1` must be `100`. |
| `phases[].base_profile` | enum | no | `AI_BEHAVIOR` §15 | One of the **other 11** profiles this phase borrows movement/attack from; omit to keep the previous phase's. (The task's "behavior_override" = this + `param_overrides`.) |
| `phases[].param_overrides` | map | no | `AI_BEHAVIOR` §15 | `snake_case` tunables of `base_profile` → new values for this phase. |
| `phases[].added_abilities` | list[ability id] | no | `AI_BEHAVIOR` §15 | Ability keys (into `abilities[]`) unlocked this phase (the task's "abilities_added"). |
| `phases[].enter_telegraph` | bool | no — default `false` | `AI_BEHAVIOR` §15 | If true, entering plays the `phase_shift` state before combat resumes. |
| `animation_states` | list[state] | yes | `40_assets/ANIMATION_STATES.md`; `00_vision/GLOSSARY.md` | Subset of the 12 GLOSSARY states. Must include every state its entity class requires (Validation). `client`. |
| `drop_table` | string `drop_mob_NNN` | yes | `10_systems/DROPS.md` §1; `20_schemas/drop_table.schema.md` | Must equal `drop_mob_<this mob's NNN>` (one table per monster). `server` (rolls, DROPS §9). |
| `respawn_override` | float s | no | `10_systems/SPAWN.md` §3 | Overrides the tier respawn default that `10_systems/SPAWN.md` §3 owns (its `respawn_timer_s`). Omit to inherit. `server`. |
| `summon_owner` | enum/tag | no | `10_systems/SKILL_EFFECTS.md` §12; `10_systems/AI_BEHAVIOR.md` §15 | Present only on a **summon template / transient** entity; marks it summoned and records the owner relation (`player` \| `mob`). The concrete owning instance is bound at runtime by the `summon_entity` op. `server`. See Open Questions (no reserved ID block yet). |
| `flavor` | string | yes | `00_vision/PILLARS.md` P1 | ≤ 2 sentences, US spelling. `client`. |

## Enums

Every enum value comes from its owning registry; this schema **points**, it does not redefine
members.

| Field | Owning registry |
|---|---|
| `tier` | **This schema** (`00_vision/GLOSSARY.md` Entity tiers → owner `20_schemas/monster.schema.md`): `normal` · `elite` · `boss`. |
| `element`, `weak_to[]`, `resists[]`, `immune_to[]`, `abilities[].effects[].element` | `10_systems/ELEMENTS.md` (GLOSSARY Elements). |
| `size_class` | `40_assets/ART_BIBLE.yaml` `sizing.size_classes` (GLOSSARY Size classes). |
| `ai_profile`, `phases[].base_profile` | `10_systems/AI_BEHAVIOR.md` (GLOSSARY AI profiles). |
| `ai_params` keys, `phases[].param_overrides` keys | The tunables the relevant profile declares in `10_systems/AI_BEHAVIOR.md` §2–§15. |
| `abilities[].targeting` (shape) | `10_systems/SKILL_SYSTEM.md` §6 (GLOSSARY Skill targeting). |
| `abilities[].effects[].op` | `10_systems/SKILL_EFFECTS.md` §3–§16 (GLOSSARY Skill effect ops). |
| `abilities[].effects[].status` (on `apply_status`/`cleanse_status`) | `10_systems/STATUS_EFFECTS.md` (GLOSSARY Status effects / cleanse tags). |
| `animation_states[]` | `40_assets/ANIMATION_STATES.md` (GLOSSARY Animation states). |
| `summon_owner` | `player` · `mob` (this schema; the runtime owner instance is not authored). |

## Example

```yaml
# illustrative — real instances land in Phase D. Values here are the §13 budget for a
# Lv 10 elite (Emberfoot's elite slot); tune level/values per WORLD_PLAN R1 (Lv 1-8 band)
# during the region batch.
id: mob_011
schema: 20_schemas/monster.schema.md
references: [COMBAT_FORMULA, STATUS_EFFECTS, AI_BEHAVIOR, DROPS, ELEMENTS, SKILL_SYSTEM, SKILL_EFFECTS, LEVELING]
name: Cinder Houndmaster
tier: elite
element: fire
weak_to: [frost]
resists: [fire]
immune_to: []
level: 10
size_class: large
stats:
  life: 4050        # 675 (§13 Lv10) × 6 (§13.2 elite)
  power: 54         # 36 × 1.5
  armor: 78         # 60 × 1.3
  warding: 78       # 60 × 1.3  (armor+warding sum = 156 = 120 × 1.3)
  precision: 44     # 40 × 1.1
  evasion: 5.3      # 3.3% + 2% (§13.2 elite)
  exp: 400          # exp_per_kill_normal(10)=80 × 5 (LEVELING §3 elite)
ai_profile: aggressive_charger
ai_params:
  charge_speed_mult: 3.0     # profile-declared tunable (AI_BEHAVIOR §5)
  charge_recover_s: 2.8
abilities:
  - id: cinder_slam
    name: Cinder Slam
    targeting: { shape: aoe_circle, radius: 3, origin: self }
    cooldown: 8.0
    telegraph_s: 1.0
    effects:
      - { op: deal_damage, element: fire, mult: 1.6 }
      - { op: apply_status, status: burn, chance: 0.5, dur: 6 }
animation_states: [idle, walk, jump, fall, attack, telegraph, hit, die, spawn]
drop_table: drop_mob_011
respawn_override: 120
flavor: "A scarred alpha that herds the kiln's fire-hounds by scent and snarl. It slams the
  ground to scatter cinders before it charges."
```

## Validation rules

Schema-specific checks, run in addition to `docs/VALIDATION.md` globals (§1 banned tokens, §2
referential integrity, §3 schema conformance/front-matter, §4 ID uniqueness+range, §6 asset
contract).

1. **Tier ↔ ID slot (hard).** `tier` must match the slot `id` occupies in the `docs/ID_REGISTRY.md`
   Monsters table for its region (normals / elites / boss). A boss ID slot may not hold a `normal`,
   etc. (`docs/VALIDATION.md` §4).
2. **Stat budget ±15% (hard).** Compute the `10_systems/COMBAT_FORMULA.md` §13 budget for this
   `level`, apply the §13.2 tier multipliers (every `boss` uses the §13.2 boss row — no separate
   scaling tier exists; `mob_147`–`mob_149` are Clockwork elites and `mob_150` is the Clockwork
   boss, `docs/ID_REGISTRY.md`):
   `life`, `power`, `spellpower` (if present), `precision`, and `evasion` must each land within
   ±15% of their budgeted value; `armor` + `warding` are checked as a **sum** against the defense
   budget (±15%), since §13 permits reallocation between them (neither may be negative or zero).
   `exp` must be within ±15% of the `10_systems/LEVELING.md` §3 value for the mob's `level` and
   `tier`. This schema restates none of those formulas — the validator reads them from the owner.
3. **Affinity mutual-exclusion (hard).** No element appears in more than one of
   `weak_to`/`resists`/`immune_to` (`10_systems/ELEMENTS.md` §2).
4. **Element ↔ region mix (warn).** `element` should appear in this region's element mix
   (`docs/WORLD_PLAN.md` per-region section / "Element affinity summary"). Warn-only: region element
   is a tuning guide, not a hard constraint (`10_systems/ELEMENTS.md` §4).
5. **Abilities gating (hard).** `abilities` is present (≥1 row) **iff** `tier` ∈ {`elite`,`boss`};
   `normal` monsters carry none (`10_systems/SKILL_EFFECTS.md` §17 monster kits are elite/boss). Each
   ability's `effects[]` ops and params validate against `10_systems/SKILL_EFFECTS.md` §3–§16; each
   `targeting` shape is a `10_systems/SKILL_SYSTEM.md` §6 token; `abilities[].id` keys are unique in
   the file.
6. **Phases gating (hard).** `phases` is present **iff** `ai_profile: boss_scripted`. `phase_id`s are
   1-based and ascending; the first phase has `life_threshold_pct: 100`; each
   `param_overrides` key is a tunable of that phase's `base_profile`; every `added_abilities` entry
   resolves to an `abilities[].id` in this file (`10_systems/AI_BEHAVIOR.md` §15).
7. **`ai_params` keys (hard).** Every key overrides a tunable the chosen `ai_profile` declares in
   `10_systems/AI_BEHAVIOR.md` (§2 shared tunables + the profile's own list). Unknown keys fail.
8. **Animation required-set (hard).** `animation_states` uses only `40_assets/ANIMATION_STATES.md`
   tokens and includes the set that doc requires for the entity class. Known-required today:
   `elite`/`boss` must include `telegraph` (`docs/VALIDATION.md` §6) and `spawn` (the entrance
   flourish, `10_systems/SPAWN.md` §6); `boss_scripted` must additionally include `phase_shift`
   (`10_systems/AI_BEHAVIOR.md` §14–§15) when any phase sets `enter_telegraph: true`; every animated
   monster includes `idle` and `die`. `40_assets/ANIMATION_STATES.md` is the authority on the full
   per-class set (it lands this phase).
9. **Drop-table pairing (hard).** `drop_table` equals `drop_mob_<this mob's NNN>` and resolves to a
   file/entry under `50_content/drop_tables/` (`10_systems/DROPS.md` §1, `docs/VALIDATION.md` §2).
10. **Size ↔ knockback (advisory).** `size_class: boss` implies knockback/CC immunity
    (`10_systems/COMBAT_FORMULA.md` §11, `10_systems/STATUS_EFFECTS.md` §3); the validator may warn if
    a non-`boss` tier monster is given `size_class: boss`, since that grants CC immunity to a normal.

## Template

```yaml
id: mob_{NNN}
schema: 20_schemas/monster.schema.md
references: [COMBAT_FORMULA, STATUS_EFFECTS, AI_BEHAVIOR, DROPS, ELEMENTS]   # add SKILL_SYSTEM, SKILL_EFFECTS if abilities; SPAWN if respawn_override; LEVELING recommended
name: "{Display Name}"
tier: {normal|elite|boss}
element: {neutral|fire|frost|nature|arcane|shadow}
level: {1..42}                 # authored arc; legal field range 1-300 (game cap)
size_class: {tiny|small|medium|large|boss}
stats:
  life: {int}
  power: {int}
  armor: {int}
  warding: {int}
  precision: {int}
  evasion: {float_pct}
  exp: {int}
  # optional: spellpower: {int}   # casters only
ai_profile: {one of the 12 AI_BEHAVIOR profiles}
animation_states: [{states from ANIMATION_STATES.md; elite/boss add telegraph + spawn; boss_scripted add phase_shift}]
drop_table: drop_mob_{NNN}
flavor: "{<=2 sentences}"

# --- optional fields (omit if unused): ---
# weak_to: [{element}]          # default []
# resists: [{element}]          # default []
# immune_to: [{element}]        # default []
# ai_params: { {profile-declared tunable}: {value} }
# respawn_override: {float_s}   # overrides SPAWN.md §3 tier default
# summon_owner: {player|mob}    # only on summon templates / transient entities

# --- REQUIRED for elite/boss only (>=1 ability); FORBIDDEN on normal: ---
# abilities:
#   - id: {snake_case_key}
#     name: "{Display}"
#     targeting: {shape token, or { shape: {token}, <geometry per SKILL_SYSTEM §6> }}
#     cooldown: {float_s}
#     telegraph_s: {float_s}
#     effects:
#       - { op: {SKILL_EFFECTS op}, {params per that op} }

# --- REQUIRED only when ai_profile: boss_scripted; FORBIDDEN otherwise: ---
# phases:
#   - phase_id: 1
#     life_threshold_pct: 100
#     # base_profile / param_overrides / added_abilities / enter_telegraph optional per AI_BEHAVIOR §15
#   - phase_id: 2
#     life_threshold_pct: {<=100}
#     base_profile: {one of the other 11 profiles}
#     param_overrides: { {tunable}: {value} }
#     added_abilities: [{ability id}]
#     enter_telegraph: true
```

## Open Questions

- **Monster/boss-ability ID prefix.** `abilities[].id` and `summon_owner`/summon-template entity IDs
  have no reserved block in `docs/ID_REGISTRY.md` today (only `skill_<line>_NNN` for player skills);
  `10_systems/AI_BEHAVIOR.md` §15 flags the same gap and proposes `mob_ability_<mob_NNN>_NN`. This
  schema uses a **file-local** `abilities[].id` key pending that ID_REGISTRY decision; confirm before
  Phase D authors boss kits and whether summon templates consume `mob_NNN` slots or a new block.
- **`references` list vs `exp`/animation deps.** The master-brief anchor's normal-mob `references`
  omits `LEVELING` even though `stats.exp` is sourced from `10_systems/LEVELING.md` §3, and omits the
  asset doc `ANIMATION_STATES`. This schema keeps the anchor's 5-doc baseline valid and only
  *recommends* adding `LEVELING`/`SKILL_*`/`SPAWN` when directly referenced; confirm whether the
  validator should require `LEVELING` whenever `exp` is present.
- **Monster crit/haste/essence.** The §13 budget names no `crit_rate`/`crit_power`/`haste`/`essence`
  for monsters, so this schema authors none (system defaults; monster abilities are cooldown-gated,
  not `essence`-gated). Flag if a specific boss needs authored crit or haste.
- **`animation_states` required-set finalization.** `40_assets/ANIMATION_STATES.md` is cited as the
  owner of the per-class required set but lands in this same phase; the known-required subset in
  Validation §8 is drawn from `docs/VALIDATION.md` §6, `10_systems/SPAWN.md` §6, and
  `10_systems/AI_BEHAVIOR.md`. Reconcile once that asset doc is authored.
- **`size_class` default.** This schema requires `size_class` (it drives knockback §11 and art); it
  is intentionally not defaulted so a physics-relevant value is never silently assumed. Confirm no
  batch process wants a `medium` default.
