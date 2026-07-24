# job.schema.md — Derived JobData Resource shape (coding-pass generated, not Phase D content)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, 10_systems/JOBS.md,
10_systems/STATS.md, 10_systems/SKILL_SYSTEM.md, 10_systems/LEVELING.md, 10_systems/ITEMS.md,
10_systems/QUESTS.md, 10_systems/PERSISTENCE.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md,
docs/VALIDATION.md

## Purpose

Defines the **JobData Resource** shape. This run **emits 9** JobData Resources — `novice` + the
**first** and **second** jobs of the four lines (`10_systems/JOBS.md` §0). The four **third**-tier
jobs (Lv 80 gate, `memory.md` Decision Contract C2) are canonized-but-reserved and are **not**
emitted this run (`10_systems/JOBS.md` §8 appendix); their names appear only in the clearly-marked
reserved note in the `name` field below. It describes a job's identity, its line/tier band, its weapon
type, its stat-growth model, the skill IDs it unlocks, and its advancement hook, so the runtime can
gate skill tiers (`10_systems/SKILL_SYSTEM.md` §2), apply auto-growth (`10_systems/STATS.md` §4.2),
and enforce advancement (`10_systems/JOBS.md` §1). Read by the stat/skill/quest runtimes; owned as a
shape contract by this schema.

**Deviation — jobs are not authored as `50_content` YAML in this run (state this loudly).** The 9
emitted jobs are already **fully specified** in the `10_systems/JOBS.md` §0–§7 roster tables; there is
nothing left to hand-author per job. The coding pass (`60_agents/`, Phase E) **generates** these
JobData Resources deterministically from `10_systems/JOBS.md` (identity, roster, skill ranges),
`10_systems/STATS.md` §4 (growth), and `docs/ID_REGISTRY.md` (skill ranges). This schema therefore
defines the **derived-Resource shape** the generator emits and the coding pass loads — not a
content-authoring template a Phase D agent fills. The `## Template` block shows that derived shape.

## File conventions

- **Not a `50_content/` file.** JobData Resources are engine-side generated artifacts (e.g. a Godot
  `Resource`/`.tres`), produced by the coding pass and stored under an engine data path such as
  `res://data/jobs/job_<line>_<tier>.tres` — **not** under `50_content/`. Their filename/location is
  the coding pass's (`30_engineering/ENGINEERING_STANDARDS.md`); this schema fixes only the field
  shape.
- **One Resource per emitted job**, **9 total**: `job_novice` + `job_<line>_<tier>` for each of
  {`bulwark`,`keeneye`,`weaver`,`flicker`} × {`first`,`second`}. The four `third`-tier resources are
  **reserved, not emitted this run** (Lv 80 gate, `10_systems/JOBS.md` §8 / `memory.md` C2).
- **No content front-matter trio.** Because a JobData Resource is not a `50_content` YAML, it is
  **exempt from `docs/VALIDATION.md` check 3** (`id`/`schema`/`references` front-matter, which
  applies to content files). It carries a stable `id` for referencing, but no `schema:`/`references:`
  header. This exemption is part of the deviation above — flagged in Open Questions.
- **Generated, not edited.** Every field is derived from an owner doc; hand-editing a JobData is a
  bug. Regenerate from `10_systems/JOBS.md` + `10_systems/STATS.md` instead.

## Fields

The `authority` tag marks who owns the runtime effect the field drives (`10_systems/PERSISTENCE.md`
§1). JobData feeds the **server-authoritative** stat recompute (`10_systems/STATS.md` §8) and skill
gate (`10_systems/SKILL_SYSTEM.md` §8); display strings are `client`.

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `job_<line>_<tier>` | yes | this schema; `10_systems/JOBS.md` §0 | `job_novice` for the shared class; else `job_<line>_<tier>`. A derived-resource id, **not** an `docs/ID_REGISTRY.md`-minted content ID (no job block exists — see Open Questions). `server`. |
| `name` | string | yes | `10_systems/JOBS.md` §0 | Display name. **Emitted this run:** `Novice`; `Bulwark`/`Ironbrand`, `Keeneye`/`Pathstalker`, `Weaver`/`Runeweaver`, `Flicker`/`Duskstep`. **Reserved (3rd tier, not emitted):** `Aegis`, `Skypiercer`, `Highweaver`, `Nightdancer`. Must match the §0 table (Validation). `client`. |
| `line` | enum | yes | `10_systems/JOBS.md` / GLOSSARY Job lines | `bulwark`\|`keeneye`\|`weaver`\|`flicker`\|`novice`. `server`. |
| `tier` | enum | yes | `10_systems/JOBS.md` §1 | `novice`\|`first`\|`second` emitted; `third` is a canonized-but-reserved value (Lv 80, `memory.md` C2), not emitted this run. `server`. |
| `advancement_level` | int | yes | `10_systems/JOBS.md` §1 | The `level` at which this job is entered: `1` (novice), `8` (first), `40` (second). The Lv-80 `third` gate is canonized-but-reserved (`memory.md` C2) and not emitted this run. Must agree with `tier` (Validation). `server`. |
| `weapon_type` | enum | no (omit for novice) | `00_vision/GLOSSARY.md` Weapon types; `10_systems/ITEMS.md` | The line's weapon (`blade`/`bow`/`staff`/`dirk`); one per line (`10_systems/JOBS.md` §0). **Omitted for `novice`** (weapon-agnostic starter kit, `10_systems/JOBS.md` §6). Equip-restriction enforcement is `10_systems/ITEMS.md`'s. `server`. |
| `stat_growth` | map | yes | `10_systems/STATS.md` §4.1–§4.3 | The auto-growth + free-pool model, **baked from `10_systems/STATS.md` §4** at generation (this schema never restates the deltas). Sub-fields below. `server`. |
| `stat_growth.main_primary` | enum \| null | yes | `10_systems/STATS.md` §1; `10_systems/JOBS.md` §0 | The line's driving primary (`might`/`finesse`/`focus`/`fortune`) that auto-grows fastest from Lv 9 (`10_systems/STATS.md` §4.2). **`null` for `novice`** (all four grow equally). |
| `stat_growth.base_primaries` | map | yes | `10_systems/STATS.md` §4.1 | Lv-1 base (global `5/5/5/5`); identical across all 9 emitted jobs (copied from `10_systems/STATS.md` §4.1). |
| `stat_growth.growth_rows` | list[row] | yes | `10_systems/STATS.md` §4.2 | Per-band auto-growth deltas, copied verbatim from `10_systems/STATS.md` §4.2 (novice band = +1 all; advanced band = main / off deltas). Row shape `{band, applies_levels, main_delta, off_delta}`. |
| `stat_growth.free_points_per_level` | int | yes | `10_systems/STATS.md` §4.3 | Global free-allocation grant per level-up (copied from §4.3). Identical across jobs. |
| `skills` | list[skill id] | yes | `docs/ID_REGISTRY.md` Skills; `10_systems/JOBS.md` §1 | The skill IDs this job **tier unlocks** — its ID sub-block: first `skill_<line>_001`–`006`, second `007`–`013` (`014`–`021` = reserved third tier, not emitted); `job_novice` → `skill_novice_001`–`004`. Cumulative availability (prior tiers) is composed by the runtime (`10_systems/SKILL_SYSTEM.md` §2), not this list. Must match the range (Validation). `server`. |
| `advancement` | map | yes | `10_systems/JOBS.md` §1 | The advancement hook into this job. Sub-fields below. `server`. |
| `advancement.requires_prior` | string (job id) \| null | yes | `10_systems/JOBS.md` §1 | The job that must precede this one (linear chain: `first`←`job_novice`, `second`←`first`, `third`←`second`). `null` for `novice`. |
| `advancement.trainer_town` | string `map_NNN` \| null | yes | `10_systems/JOBS.md` §1; `docs/ID_REGISTRY.md` | The line's **home-town map** whose instructor issues **both** the 1st and 2nd advancement (`10_systems/JOBS.md` §1): `bulwark`→`map_125` (Cindershelf), `keeneye`→`map_071` (Tidewatch Port), `weaver`→`map_043` (Mossmere), `flicker`→`map_018` (Millbrook Central). Same value for a line's first and second tiers; the Lv-40 2nd advancement additionally routes through a Clockwork Ruins trial (`10_systems/JOBS.md` §1) — not a separate town. `null` for `novice`. `server`. |
| `advancement.quest` | string `quest_NNN` \| null | yes | `10_systems/JOBS.md` §1; `10_systems/QUESTS.md`; `docs/ID_REGISTRY.md` | The trainer quest gate. **`null` until Phase D authors trainer quests** (`10_systems/JOBS.md` §1 OQ); when set, a `quest_NNN` in the trainer town's quest block. `server`. |
| `advancement.trainer_npc` | string `npc_NNN` \| null | yes | `10_systems/JOBS.md` §1; `docs/ID_REGISTRY.md` | The job-trainer NPC. **`null` until Phase D**; when set, an `npc_NNN` in the trainer town's NPC block. `server`. |

## Enums

Points at owners; never redefines members.

| Field | Owning registry |
|---|---|
| `line` | `10_systems/JOBS.md` / `00_vision/GLOSSARY.md` Job lines (+`novice`). |
| `tier` | `10_systems/JOBS.md` §1: `novice`·`first`·`second`·`third`. |
| `weapon_type` | `00_vision/GLOSSARY.md` Weapon types (owner `10_systems/ITEMS.md`): `blade`·`bow`·`staff`·`dirk`. |
| `stat_growth.main_primary` | `00_vision/GLOSSARY.md` Primary stats (owner `10_systems/STATS.md`): `might`·`finesse`·`focus`·`fortune` (or `null`). |
| `advancement.trainer_town` | `docs/ID_REGISTRY.md` Maps — the four line **home-town** IDs (`10_systems/JOBS.md` §1): `map_125`·`map_071`·`map_043`·`map_018` (or `null`). |

## Example

```yaml
# illustrative — a DERIVED resource (coding pass generates all 9 from JOBS.md + STATS.md;
# this is not authored in Phase D). Growth values are copied from STATS.md §4 — do not hand-edit.
id: job_bulwark_first
name: Bulwark
line: bulwark
tier: first
advancement_level: 8
weapon_type: blade
stat_growth:
  main_primary: might
  base_primaries: { might: 5, finesse: 5, focus: 5, fortune: 5 }   # STATS §4.1 (global)
  growth_rows:                                                     # STATS §4.2 (copied)
    - { band: novice,   applies_levels: "2-8", main_delta: 1, off_delta: 1 }
    - { band: advanced, applies_levels: "9+",  main_delta: 3, off_delta: 1 }
  free_points_per_level: 2                                         # STATS §4.3 (global)
skills: [skill_bulwark_001, skill_bulwark_002, skill_bulwark_003, skill_bulwark_004, skill_bulwark_005, skill_bulwark_006]
advancement:
  requires_prior: job_novice
  trainer_town: map_125   # Cindershelf (Ashfall) — Bulwark line home town (JOBS §1)
  quest: null          # Phase D trainer quest (JOBS §1 OQ)
  trainer_npc: null    # Phase D trainer NPC
```

## Validation rules

Schema-specific checks. Note: JobData is **exempt from `docs/VALIDATION.md` check 3** (front-matter)
per File conventions; it is still subject to referential integrity (check 2) and ID uniqueness
(check 4, `id` unique among jobs).

1. **Identity ↔ roster (hard).** `id`, `name`, `line`, `tier`, `advancement_level`, and (for the 8
   advancement jobs) `weapon_type` must match the `10_systems/JOBS.md` §0/§1 roster: `tier`→`advancement_level` is
   `novice`→1, `first`→8, `second`→40 (the reserved `third`→80 is not emitted this run); `weapon_type` is the line's GLOSSARY weapon;
   `job_novice` omits `weapon_type` and sets `main_primary: null`.
2. **Skill list ↔ ID range (hard).** `skills` equals the line+tier sub-block from `docs/ID_REGISTRY.md`
   / `10_systems/JOBS.md` §1: first `001`–`006`, second `007`–`013`,
   `job_novice` `skill_novice_001`–`004` (the reserved `third` `014`–`021` block is not emitted this
   run). Every id exists as a skill content file (check 2). No id outside the line's block.
3. **`main_primary` (hard).** For the 8 emitted advancement jobs (first + second per line), `stat_growth.main_primary` is the line's
   primary (`bulwark`→`might`, `keeneye`→`finesse`, `weaver`→`focus`, `flicker`→`fortune`,
   `10_systems/STATS.md` §1 / `10_systems/JOBS.md` §0); `job_novice` → `null`.
4. **Growth baked from STATS (hard).** `stat_growth.base_primaries`, `growth_rows`, and
   `free_points_per_level` must equal the `10_systems/STATS.md` §4.1/§4.2/§4.3 values (the generator
   copies them; a mismatch means the resource drifted from the owner doc).
5. **Advancement chain (hard).** `advancement.requires_prior` forms the linear chain
   (`first`←`job_novice`, `second`←`first`; `novice`→`null`) with no branching
   (`00_vision/SCOPE.md`). `advancement.trainer_town` is the line's home-town `map_NNN`
   (`map_125`/`map_071`/`map_043`/`map_018` per line, identical for first and second) and `null` for
   novice (`10_systems/JOBS.md` §1).
6. **Advancement hooks resolve when set (hard-when-present).** `advancement.quest`/`trainer_npc` are
   `null` until Phase D; once set they must resolve to a `quest_NNN`/`npc_NNN` in the trainer town's
   block (`docs/ID_REGISTRY.md`, `docs/WORLD_PLAN.md`) — in the line's home town (Cindershelf /
   Tidewatch Port / Mossmere / Millbrook Central) for both first and second advancement
   (`10_systems/JOBS.md` §1). A non-null broken ref fails (check 2).

## Template

```yaml
# DERIVED resource shape (coding pass emits 9 of these: novice + first/second per line).
# Not a 50_content authoring template. Third tier is reserved (Lv 80) and NOT emitted this run.
id: job_{line}_{tier}                 # job_novice for the shared class
name: "{JOBS.md §0 display name}"
line: {bulwark|keeneye|weaver|flicker|novice}
tier: {novice|first|second}            # third tier reserved (Lv 80), not emitted this run
advancement_level: {1|8|40}            # novice 1 / first 8 / second 40
stat_growth:
  main_primary: {might|finesse|focus|fortune}   # null for novice
  base_primaries: { might: {n}, finesse: {n}, focus: {n}, fortune: {n} }   # from STATS §4.1
  growth_rows:                                                             # from STATS §4.2
    - { band: novice,   applies_levels: "2-8", main_delta: {n}, off_delta: {n} }
    - { band: advanced, applies_levels: "9+",  main_delta: {n}, off_delta: {n} }
  free_points_per_level: {n}                                              # from STATS §4.3
skills: [{the line+tier ID sub-block from ID_REGISTRY / JOBS §1}]
advancement:
  requires_prior: {prior job id | null}
  trainer_town: {map_125|map_071|map_043|map_018|null}   # line home town (JOBS §1); null for novice
  quest: {quest_NNN | null}            # null until Phase D authors trainer quests
  trainer_npc: {npc_NNN | null}        # null until Phase D
# weapon_type omitted for novice; else:
# weapon_type: {blade|bow|staff|dirk}
```

## Open Questions

- **No job ID block in `docs/ID_REGISTRY.md`.** Jobs are derived Resources, not minted content IDs,
  so this schema proposes `job_<line>_<tier>` / `job_novice` without a reserved registry block. If a
  block is later wanted (e.g., for quest/save references to a job), add it to `docs/ID_REGISTRY.md`;
  until then these IDs are schema-local. Confirm at the C/E gate.
- **Front-matter exemption.** JobData carries no `id`/`schema`/`references` front-matter trio because
  it is not a `50_content` file (`docs/VALIDATION.md` check 3 targets content files). Confirm the
  validator special-cases derived-resource schemas so this exemption is explicit rather than a silent
  gap in check 3.
- **Growth redundancy.** All growth fields except `main_primary` are global constants
  (`10_systems/STATS.md` §4.1–§4.3), baked identically into all 9 emitted resources. If the coding pass
  prefers a single shared growth model referenced by `main_primary` alone, that is an
  `30_engineering/ENGINEERING_STANDARDS.md` implementation choice; this schema documents the
  self-contained form. Default: baked-per-resource.
- **Cumulative vs per-tier `skills`.** This schema lists each job's **own tier** unlock block and
  leaves cumulative availability to the runtime (`10_systems/SKILL_SYSTEM.md` §2). If the coding pass
  wants JobData to enumerate all skills usable at that job (prior tiers included), that is a generator
  choice — flag it; default is per-tier.
- **Advancement quest/NPC IDs are Phase D.** `advancement.quest`/`trainer_npc` stay `null` until
  `10_systems/QUESTS.md` / Phase D author the trainer quests and NPCs (`10_systems/JOBS.md` §1 OQ);
  the generator backfills them then. Whether a `shards`/item gate accompanies the quest is
  `10_systems/ECONOMY.md`/`10_systems/QUESTS.md`'s call (default quest-only).
