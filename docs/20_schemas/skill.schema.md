# skill.schema.md — One-file-per-skill content shape (skill_<line>_NNN)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/JOBS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/ELEMENTS.md, 10_systems/STATS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 40_assets/SKILL_ANIMATION.md,
40_assets/ANIMATION_STATES.md, docs/ID_REGISTRY.md, docs/VALIDATION.md

## Purpose

Defines the content shape of one **skill** (`skill_<line>_NNN`, plus `skill_novice_NNN`) — the 84
line skills + 4 novice skills in `00_vision/SCOPE.md` / `10_systems/JOBS.md`. A skill file is the
data a Phase D author fills and the coding pass loads: an identity that must match a
`10_systems/JOBS.md` roster row exactly, a targeting shape from `10_systems/SKILL_SYSTEM.md` §6, an
`essence` cost and cooldown, and a `level_data` table of ordered effect ops drawn from the
`10_systems/SKILL_EFFECTS.md` registry, interpolated per `10_systems/SKILL_SYSTEM.md` §4. It is read
by the skill runtime (`10_systems/SKILL_SYSTEM.md`), the effect resolver
(`10_systems/SKILL_EFFECTS.md`), and the animation pipeline (`40_assets/SKILL_ANIMATION.md`). This
schema owns the **field shape and enum owner** for every field; it never restates the interpolation
math, the op parameter schemas, cost/cooldown bands, or status rules — it cites them.

## File conventions

- **One entity per file.** `50_content/skills/<line>/skill_<line>_NNN.yaml`, where `<line>` ∈
  {`bulwark`, `keeneye`, `weaver`, `flicker`, `novice`} and the folder name equals the line. Novice
  skills live in `50_content/skills/novice/skill_novice_NNN.yaml`.
- **ID ranges** (`docs/ID_REGISTRY.md` Skills; `10_systems/JOBS.md` §1): per line
  `skill_<line>_001`–`021` authored (`022`–`030` reserved), in tier order — `001`–`006` first-job,
  `007`–`013` second-job, `014`–`021` third-job. Novice: `skill_novice_001`–`010` reserved, `001`–
  `004` authored. The file's `id` is its filename stem; both immutable.
- **`line` field naming note.** The master-brief format anchor wrote this identity field as `job`;
  this schema names it **`line`** to match the task's explicit field list and the `00_vision/GLOSSARY.md`
  "Line token" vocabulary. See Open Questions — flagged, not silently chosen.

## Fields

Static content-definition files, loaded identically by client and server; the `authority` tag in a
note marks who owns the *runtime effect* the field drives (`10_systems/PERSISTENCE.md` §1). Skill
cost/cooldown/`level_data` resolution and targeting are **server-authoritative**
(`10_systems/SKILL_SYSTEM.md` §8); `animation` is client presentation. Front-matter obeys
`docs/VALIDATION.md` check 3.

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `skill_<line>_NNN` | yes | `docs/ID_REGISTRY.md` Skills | Zero-padded; immutable; must fall in the line's authored range and the tier's sub-block (Validation). `server`. |
| `schema` | string | yes | this file | Literal `20_schemas/skill.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list[doc name] | yes | `docs/VALIDATION.md` §3 | Bare `SYSTEM_DOC_NAMES`. Baseline `[SKILL_SYSTEM, SKILL_EFFECTS, SKILL_ANIMATION, STATUS_EFFECTS, ELEMENTS]`; drop `STATUS_EFFECTS`/`ELEMENTS` only if the kit truly uses neither (rare). |
| `name` | string | yes | `10_systems/JOBS.md` §2–§6 roster | Must match the roster row **exactly** (Validation). `client`. |
| `line` | enum | yes | `10_systems/JOBS.md` / GLOSSARY Job lines | `bulwark`\|`keeneye`\|`weaver`\|`flicker`\|`novice`. `server`. |
| `tier` | enum | yes | `10_systems/JOBS.md` §1 | `novice`\|`first`\|`second`\|`third` — the job tier that unlocks the skill; must agree with the ID sub-block (Validation). `server`. |
| `kind` | enum | yes | `10_systems/JOBS.md` roster (A/P) | `active`\|`passive`. Passives are never slotted and always-on (`10_systems/SKILL_SYSTEM.md` §7). `server`. |
| `targeting` | token \| map | yes | `10_systems/SKILL_SYSTEM.md` §6 | One of the 6 GLOSSARY shapes as a bare token (uses §6 geometry defaults) **or** `{shape, <geometry per §6>}`. Passives use `self` (auras use `party`, see `kind`). `server`. |
| `cost` | map `{essence: int}` | yes | `10_systems/SKILL_SYSTEM.md` §5; `10_systems/STATS.md` (`essence`) | Flat default `essence` cost across ranks; **`0` for passives**. Per-rank scaling is expressed in `level_data` (see below). `server`. |
| `cooldown` | float s | yes | `10_systems/SKILL_SYSTEM.md` §5 | Flat default real-time cooldown; `0` for passives. Per-rank scaling via `level_data`. `server`. |
| `max_level` | int | no — default `10` | `10_systems/SKILL_SYSTEM.md` §2 | Fixed at 10 by `10_systems/SKILL_SYSTEM.md` §2; if present must equal 10 (Validation). `server`. |
| `prerequisites` | list `{skill, min_rank}` | no | `10_systems/SKILL_SYSTEM.md` §2 | Same-line skill ids at a minimum rank (1–10). Short/shallow chains only (`10_systems/SKILL_SYSTEM.md` §2 owns the rule; concrete edges authored here). `server`. |
| `level_data` | list[row] | yes | `10_systems/SKILL_SYSTEM.md` §4 | Rows **only** at skill levels `1, 4, 7, 10` (level 1 required); ranks 2/3/5/6/8/9 interpolate at load — this schema never restates the interpolation. `server`. Sub-fields below. |
| `level_data[].level` | int ∈ {1,4,7,10} | yes | `SKILL_SYSTEM` §4 | Authored rank. Ascending, unique. |
| `level_data[].effects` | list[op] | yes | `10_systems/SKILL_EFFECTS.md` §3–§16 | Ordered effect list (composition per §2 there). Op **list/order, `element`, `status`, cleanse `tag`, `summon_entity.entity_ref`, `on_hit_proc.trigger`** must be identical across all rows (non-interpolatable, `SKILL_SYSTEM` §4); only numeric params scale. |
| `level_data[].essence_cost` | int | no | `SKILL_SYSTEM` §4/§5 | Present only to **scale** cost by rank; overrides `cost.essence` at authored ranks and interpolates between. Non-decreasing with rank (warn). `server`. |
| `level_data[].cooldown` | float s | no | `SKILL_SYSTEM` §4/§5 | Present only to scale cooldown by rank; overrides top-level `cooldown`. Non-increasing with rank (warn). `server`. |
| `animation` | string (anim id) | actives yes / passives no | `40_assets/SKILL_ANIMATION.md` | Animation id following `40_assets/SKILL_ANIMATION.md` naming (anchor form `skill_<line>_NNN_cast`). Optional for passives (proc-fx only). `client`. |
| `flavor` | string | yes | `00_vision/PILLARS.md` P1 | ≤ 2 sentences, US spelling. `client`. |

**Cost / cooldown placement (the one cross-cutting rule).** `10_systems/SKILL_SYSTEM.md` §4 lists
`essence_cost` and `cooldown` as interpolatable. This schema resolves that as: the top-level
`cost.essence` / `cooldown` are the **flat value used at every rank**; to make either *scale*, add
`essence_cost` / `cooldown` keys inside the `level_data` rows (at `1/4/7/10`), which define the curve
and override the flat value where present. Top-level values stay required so a value always exists.
This keeps the anchor's flat form valid and honors `10_systems/SKILL_SYSTEM.md` §4/§5 scaling. The
schema restates neither the interpolation formula nor the cost bands.

## Enums

Every enum value comes from its owning registry; this schema points, never redefines.

| Field | Owning registry |
|---|---|
| `line` | `10_systems/JOBS.md` / `00_vision/GLOSSARY.md` Job lines (+`novice`): `bulwark`·`keeneye`·`weaver`·`flicker`·`novice`. |
| `tier` | `10_systems/JOBS.md` §1 job bands: `novice`·`first`·`second`·`third`. |
| `kind` | **This schema**, matched to the `10_systems/JOBS.md` roster A/P column: `active`·`passive`. |
| `targeting` (shape) | `10_systems/SKILL_SYSTEM.md` §6 (GLOSSARY Skill targeting): `melee_arc`·`line`·`projectile`·`aoe_circle`·`self`·`party`. |
| `level_data[].effects[].op` | `10_systems/SKILL_EFFECTS.md` §3–§16 (GLOSSARY Skill effect ops, all 14). |
| `...effects[].element` | `10_systems/ELEMENTS.md` (GLOSSARY Elements). |
| `...effects[].status` | `10_systems/STATUS_EFFECTS.md` (GLOSSARY Status effects). |
| `...effects[].tag` (on `cleanse_status`) | `10_systems/STATUS_EFFECTS.md` §2 cleanse tags. |
| `...effects[].scaling` | `power`·`spellpower` (`10_systems/SKILL_EFFECTS.md` §1; default per line). |
| `...effects[].stats` keys (on `passive_stat_bonus`) | `10_systems/STATS.md` (GLOSSARY stat tokens). |
| `...effects[].trigger` (on `on_hit_proc`) | `10_systems/SKILL_EFFECTS.md` §16: `on_deal`·`on_take`·`on_crit`·`on_kill`·`on_dodge`·`on_cast`. |

## Example

```yaml
# illustrative — real instances land in Phase D. Identity matches the JOBS.md roster row
# (skill_weaver_007 "Fireball"); level_data numbers are first-pass and get tuned in Phase D.
id: skill_weaver_007
schema: 20_schemas/skill.schema.md
references: [SKILL_SYSTEM, SKILL_EFFECTS, SKILL_ANIMATION, STATUS_EFFECTS, ELEMENTS]
name: Fireball
line: weaver
tier: second
kind: active
targeting: { shape: aoe_circle, radius: 3, origin: reticle, reticle_range: 8 }
cost: { essence: 14 }        # flat default; scaled per-rank in level_data below
cooldown: 6.0                # flat default; scaled per-rank below
max_level: 10
level_data:
  - level: 1
    essence_cost: 14
    cooldown: 6.0
    effects:
      - { op: deal_damage, element: fire, mult: 1.4 }
      - { op: apply_status, status: burn, chance: 0.30, dur: 4 }
  - level: 4
    essence_cost: 18
    cooldown: 5.5
    effects:
      - { op: deal_damage, element: fire, mult: 1.9 }
      - { op: apply_status, status: burn, chance: 0.40, dur: 5 }
  - level: 7
    essence_cost: 23
    cooldown: 5.0
    effects:
      - { op: deal_damage, element: fire, mult: 2.4 }
      - { op: apply_status, status: burn, chance: 0.50, dur: 5 }
  - level: 10
    essence_cost: 28
    cooldown: 4.5
    effects:
      - { op: deal_damage, element: fire, mult: 3.0 }
      - { op: apply_status, status: burn, chance: 0.60, dur: 6 }
animation: skill_weaver_007_cast
flavor: "A packed bloom of essence-fire lobbed onto a point and left to smolder. The blast lands,
  the ground keeps burning."
```

Passive pattern (illustrative, `skill_weaver_005` "Attunement"): `kind: passive`, `targeting: self`,
`cost: { essence: 0 }`, `cooldown: 0`, a single `level_data[].effects` row of one
`{ op: passive_stat_bonus, stats: { spellpower: ..., essence: ... } }` scaled across ranks; no
`animation`. Proc passives use one `on_hit_proc` op instead; hybrid passives (e.g.
`skill_flicker_021`) use `passive_stat_bonus` + `on_hit_proc`.

## Validation rules

Schema-specific checks, beyond `docs/VALIDATION.md` globals (§1–§4, §6).

1. **Identity ↔ roster (hard).** `line`, `tier`, `kind`, and `name` must match the
   `10_systems/JOBS.md` §2–§6 roster row for this `id` **exactly** (name string included). The tier
   must agree with the ID sub-block (`001`–`006`→`first`, `007`–`013`→`second`, `014`–`021`→`third`,
   `skill_novice_*`→`novice`; `10_systems/JOBS.md` §1). `id` in-range (`docs/VALIDATION.md` §4).
2. **Ops validate (hard).** Every `effects[]` op token is one of the 14
   (`10_systems/SKILL_EFFECTS.md`) and every param validates against that op's schema (§3–§16):
   required params present, enums from their owners, values in the op's authoring bounds.
3. **`level_data` shape (hard).** Row `level`s are a subset of `{1,4,7,10}`, ascending, unique, with
   level 1 present. Non-interpolatable fields (op list/order, `element`, `status`, cleanse `tag`,
   `summon_entity.entity_ref`, `on_hit_proc.trigger`) are identical across every row
   (`10_systems/SKILL_SYSTEM.md` §4).
4. **Monotonicity (warn).** `deal_damage.mult` and status magnitudes non-decreasing with rank;
   per-rank `essence_cost` non-decreasing; `cooldown` non-increasing (`10_systems/SKILL_SYSTEM.md`
   §4, `00_vision/PILLARS.md` P2 — ranking never worsens a skill).
5. **Passive shape (hard).** `kind: passive` ⇒ `cost.essence: 0`, `cooldown: 0` (or omitted),
   `targeting` ∈ {`self`, `party`}, and `effects[]` uses only `passive_stat_bonus` and/or
   `on_hit_proc` (no direct offensive ops); `party` targeting requires the `passive_stat_bonus`
   `scope: party_aura` (`10_systems/SKILL_EFFECTS.md` §13, e.g. `skill_bulwark_019`).
6. **`max_level` (hard).** If present, `max_level == 10` (`10_systems/SKILL_SYSTEM.md` §2).
7. **Prerequisites (hard).** Each `prerequisites[].skill` is a **same-line** skill id that exists,
   with `min_rank` 1–10; no self-reference; no cycles (`10_systems/SKILL_SYSTEM.md` §2).
8. **Element ↔ line leaning (warn).** Elements used in `effects[]` should sit within the line's
   leaning (`10_systems/JOBS.md` per-line "Element leaning" + `10_systems/ELEMENTS.md` §5 guideline).
   Warn-only — leanings are loose by design.
9. **Animation (hard for actives).** `active` skills carry an `animation` id following
   `40_assets/SKILL_ANIMATION.md` naming (`docs/VALIDATION.md` §6); passives may omit it.

## Template

```yaml
id: skill_{line}_{NNN}          # novice: skill_novice_{NNN}
schema: 20_schemas/skill.schema.md
references: [SKILL_SYSTEM, SKILL_EFFECTS, SKILL_ANIMATION, STATUS_EFFECTS, ELEMENTS]
name: "{exact JOBS.md roster name}"
line: {bulwark|keeneye|weaver|flicker|novice}
tier: {novice|first|second|third}      # must agree with the ID sub-block
kind: {active|passive}
targeting: {shape token, or { shape: {token}, <geometry per SKILL_SYSTEM §6> }}   # passives: self (auras: party)
cost: { essence: {int} }               # 0 for passives
cooldown: {float_s}                    # 0 for passives
level_data:
  - level: 1
    effects:
      - { op: {SKILL_EFFECTS op}, {params per that op} }
  # add rows at 4, 7, 10 to scale (ranks 2/3/5/6/8/9 interpolate, SKILL_SYSTEM §4);
  # to scale cost/cooldown, add essence_cost / cooldown keys inside these rows.
animation: skill_{line}_{NNN}_cast     # actives only; omit for passives
flavor: "{<=2 sentences}"

# --- optional fields (omit if unused): ---
# max_level: 10                        # fixed by SKILL_SYSTEM §2; only 10 is valid
# prerequisites: [{ skill: skill_{line}_{NNN}, min_rank: {1..10} }]   # same line only
```

## Open Questions

- **`line` vs `job` field name.** The master-brief format anchor labels the identity field `job`;
  this schema uses **`line`** (the task's explicit field list + `00_vision/GLOSSARY.md` "Line token"
  vocabulary). If the orchestrator intends the literal anchor key `job`, rename here — flagged rather
  than guessed. Whichever is chosen, the value is a GLOSSARY line token.
- **`condition` enum for `passive_stat_bonus`/`on_hit_proc`.** `10_systems/SKILL_EFFECTS.md` §16 (OQ)
  leaves the `condition` vocabulary (`below_life_pct:X`, `while_veiled`, `vs_marked`, …) open-ended
  and asks that it be frozen at the C gate so `docs/VALIDATION.md` can enum-check it. Until frozen,
  authors use only the examples named there; this schema cannot enum-validate `condition` yet.
- ~~`40_assets/SKILL_ANIMATION.md` lands this phase~~ **Resolved:** it exists; the anchor form
  `skill_<line>_NNN_cast` is confirmed as the validated id, and multi-clip skills derive further
  clips by fixed suffix (`_proj`/`_impact`/`_loop`/`_proc`, its §2) with no schema change here.
- **Summon `entity_ref` targets.** Skills with `summon_entity` (`skill_keeneye_010`,
  `skill_weaver_017`, `skill_flicker_015`) reference a summon-template entity whose ID block is the
  open `20_schemas/monster.schema.md` / `docs/ID_REGISTRY.md` question; confirm the ref format at the
  C gate (`10_systems/SKILL_EFFECTS.md` §12 OQ).
- **Per-skill cast/recovery window.** `10_systems/SKILL_SYSTEM.md` §5 describes a per-skill
  cast+recovery input-lock separate from `cooldown`; whether it is authored as a field here or
  derived from the `animation` clip length is unresolved (SKILL_SYSTEM §5 / COMBAT_FORMULA §10 OQ).
  This schema does not yet carry a `cast_time`/`recovery` field.
