# job.schema.md — Derived JobData Resource shape (coding-pass generated, not Phase D content)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, 10_systems/JOBS.md,
10_systems/STATS.md, 10_systems/SKILL_SYSTEM.md, 10_systems/LEVELING.md, 10_systems/ITEMS.md,
10_systems/QUESTS.md, 10_systems/PERSISTENCE.md, docs/ID_REGISTRY.md, docs/WORLD_PLAN.md,
docs/VALIDATION.md

## Purpose

Defines the **JobData Resource** shape — one per job for the 15 authored jobs (`novice` + the 4
first jobs + the 10 second-job **specializations**) in `10_systems/JOBS.md` §0–§1 (v3 branching
model: the Lv-40 2nd advancement is a permanent choice of one of the line's 2–3 specs,
`00_vision/SCOPE.md`). The four 3rd-tier jobs (Aegis/Skypiercer/Highweaver/Nightdancer) are
named-and-reserved for a future arc (`00_vision/GLOSSARY.md` Job lines; `00_vision/SCOPE.md`
Deliberate scope limits) — no JobData resource is generated for them this run. It describes a
job's identity, its line/tier/spec, its weapon type, its stat-growth model, the skill IDs it
unlocks, and its advancement hook, so the runtime can gate skill tiers and the line/spec choice
(`10_systems/SKILL_SYSTEM.md` §2), apply auto-growth (`10_systems/STATS.md` §4.2), and enforce
advancement (`10_systems/JOBS.md` §1). Read by the
stat/skill/quest runtimes; owned as a shape contract by this schema.

**Deviation — jobs are not authored as `50_content` YAML in this run (state this loudly).** The 15
authored jobs are already **fully specified** in the `10_systems/JOBS.md` §0–§7 roster tables; there is
nothing left to hand-author per job. The coding pass (`60_agents/`, Phase E) **generates** these
JobData Resources deterministically from `10_systems/JOBS.md` (identity, roster, skill ranges),
`10_systems/STATS.md` §4 (growth), and `docs/ID_REGISTRY.md` (skill ranges). This schema therefore
defines the **derived-Resource shape** the generator emits and the coding pass loads — not a
content-authoring template a Phase D agent fills. The `## Template` block shows that derived shape.

## File conventions

- **Not a `50_content/` file.** JobData Resources are engine-side generated artifacts (e.g. a Godot
  `Resource`/`.tres`), produced by the coding pass and stored under an engine data path such as
  `res://data/jobs/job_<id>.tres` — **not** under `50_content/`. Their filename/location is
  the coding pass's (`30_engineering/ENGINEERING_STANDARDS.md`); this schema fixes only the field
  shape.
- **One Resource per job**, 15 total: `job_novice` + `job_<line>_first` for each of
  {`bulwark`,`keeneye`,`weaver`,`flicker`} + one `job_<line>_<spec>` per specialization
  (`10_systems/JOBS.md` §0): `job_bulwark_ironbrand`, `job_bulwark_stoneguard`,
  `job_bulwark_warcaller`, `job_keeneye_pathstalker`, `job_keeneye_sureshot`,
  `job_weaver_runeweaver`, `job_weaver_cindercall`, `job_weaver_frostbind`,
  `job_flicker_duskstep`, `job_flicker_wildcard`. Third-tier jobs are named-and-reserved for a
  future arc (`00_vision/GLOSSARY.md` Job lines; `00_vision/SCOPE.md` Deliberate scope limits) —
  no third-tier resource is generated this run.
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
| `id` | string | yes | this schema; `10_systems/JOBS.md` §0 | `job_novice` for the shared class; `job_<line>_first` for a first job; `job_<line>_<spec>` for a specialization (spec tokens per `10_systems/JOBS.md` §0). A derived-resource id, **not** an `docs/ID_REGISTRY.md`-minted content ID (no job block exists — see Open Questions). `server`. |
| `name` | string | yes | `10_systems/JOBS.md` §0 | Display name — `Novice`; `Bulwark`, `Keeneye`, `Weaver`, `Flicker`; `Ironbrand`, `Stoneguard`, `Warcaller`, `Pathstalker`, `Sureshot`, `Runeweaver`, `Cindercall`, `Frostbind`, `Duskstep`, `Wildcard`. (The reserved 3rd-tier names `Aegis`/`Skypiercer`/`Highweaver`/`Nightdancer` have no resource this run.) Must match the §0 table (Validation). `client`. |
| `line` | enum | yes | `10_systems/JOBS.md` / GLOSSARY Job lines | `bulwark`\|`keeneye`\|`weaver`\|`flicker`\|`novice`. `server`. |
| `tier` | enum | yes | `10_systems/JOBS.md` §1 | `novice`\|`first`\|`second`\|`third`. Every specialization resource is `tier: second` (the Lv-40 branch is within the 2nd advancement, `10_systems/JOBS.md` §1). `server`. |
| `spec` | enum | required iff `tier: second`; forbidden otherwise | `10_systems/JOBS.md` §0 | This resource's specialization token — one of its `line`'s specs (`ironbrand`\|`stoneguard`\|`warcaller` / `pathstalker`\|`sureshot` / `runeweaver`\|`cindercall`\|`frostbind` / `duskstep`\|`wildcard`). Must agree with `id` (Validation). `server`. |
| `advancement_level` | int | yes | `10_systems/JOBS.md` §1 | The `level` at which this job is entered: `1` (novice), `8` (first — choose a line, permanent), `40` (second — choose **one** of the line's 2–3 specializations, permanent; `10_systems/JOBS.md` §1 branching choice rule). The 3rd tier has no authored advancement level (default gate Lv 80, a future-arc decision — `10_systems/JOBS.md` §1) and no resource exists to carry one. Must agree with `tier` (Validation). `server`. |
| `weapon_type` | enum | no (omit for novice) | `00_vision/GLOSSARY.md` Weapon types; `10_systems/ITEMS.md` | The line's weapon (`blade`/`bow`/`staff`/`dirk`); one per line (`10_systems/JOBS.md` §0). **Omitted for `novice`** (weapon-agnostic starter kit, `10_systems/JOBS.md` §6). Equip-restriction enforcement is `10_systems/ITEMS.md`'s. `server`. |
| `stat_growth` | map | yes | `10_systems/STATS.md` §4.1–§4.3 | The auto-growth + free-pool model, **baked from `10_systems/STATS.md` §4** at generation (this schema never restates the deltas). Sub-fields below. `server`. |
| `stat_growth.main_primary` | enum \| null | yes | `10_systems/STATS.md` §1; `10_systems/JOBS.md` §0 | The line's driving primary (`might`/`finesse`/`focus`/`fortune`) that auto-grows fastest from Lv 9 (`10_systems/STATS.md` §4.2). **`null` for `novice`** (all four grow equally). |
| `stat_growth.base_primaries` | map | yes | `10_systems/STATS.md` §4.1 | Lv-1 base (global `5/5/5/5`); identical across all 15 authored jobs (copied from `10_systems/STATS.md` §4.1). |
| `stat_growth.growth_rows` | list[row] | yes | `10_systems/STATS.md` §4.2 | Per-band auto-growth deltas, copied verbatim from `10_systems/STATS.md` §4.2 (novice band = +1 all; advanced band = main / off deltas). Row shape `{band, applies_levels, main_delta, off_delta}`. |
| `stat_growth.free_points_per_level` | int | yes | `10_systems/STATS.md` §4.3 | Global free-allocation grant per level-up (copied from §4.3). Identical across jobs. |
| `skills` | list[skill id] | yes | `docs/ID_REGISTRY.md` Skills; `10_systems/JOBS.md` §1 | The skill IDs this job **unlocks** — its ID sub-block: first `skill_<line>_001`–`006` (shared by all of the line's specs); spec #1 `007`–`013`, spec #2 `014`–`020`, spec #3 `021`–`027` (each spec resource lists only its own 7-skill block); `job_novice` → `skill_novice_001`–`004`. `skill_<line>_028`–`045` are **reserved** for the deferred 3rd tier and `046`–`060` for growth (`10_systems/JOBS.md` §1; `docs/ID_REGISTRY.md`) — never in an authored `skills` list. Cumulative availability (novice + first + the character's one chosen spec — sibling specs stay permanently locked) is composed by the runtime (`10_systems/SKILL_SYSTEM.md` §2 line/spec gate), not this list. Must match the range (Validation). `server`. |
| `advancement` | map | yes | `10_systems/JOBS.md` §1 | The advancement hook into this job. Sub-fields below. `server`. |
| `advancement.requires_prior` | string (job id) \| null | yes | `10_systems/JOBS.md` §1 | The job that must precede this one: `first`←`job_novice`; every spec of a line ← that line's `job_<line>_first` (the Lv-40 branch point — a character enters exactly **one** of the siblings, permanently; mutual exclusivity is the per-character runtime rule, `10_systems/JOBS.md` §1 / `10_systems/SKILL_SYSTEM.md` §2, not a resource-level link). `null` for `novice`. A `third`←`second` link is not applicable — `third` is named-and-reserved only (`00_vision/GLOSSARY.md` Job lines; `00_vision/SCOPE.md` Deliberate scope limits). |
| `advancement.trainer_town` | enum \| null | yes | `10_systems/JOBS.md` §1; `docs/WORLD_PLAN.md` "Job instructors" | The line's home-town region hosting its job instructor (`bulwark`→`ashfall` [Cindershelf], `keeneye`→`tidewatch` [Tidewatch Port], `weaver`→`verdant` [Mossmere], `flicker`→`millbrook` [Millbrook Central]); the **same** instructor issues both first and second advancement (`10_systems/JOBS.md` §1). `null` for `novice`. `server`. |
| `advancement.quest` | string `quest_NNN` \| null | yes | `10_systems/JOBS.md` §1; `10_systems/QUESTS.md`; `docs/ID_REGISTRY.md` | The trainer quest gate. **`null` until Phase D authors trainer quests** (`10_systems/JOBS.md` §1 OQ); when set, a `quest_NNN` in the trainer town's quest block. `server`. |
| `advancement.trainer_npc` | string `npc_NNN` \| null | yes | `10_systems/JOBS.md` §1; `docs/ID_REGISTRY.md` | The job-trainer NPC. **`null` until Phase D**; when set, an `npc_NNN` in the trainer town's NPC block. `server`. |

## Enums

Points at owners; never redefines members.

| Field | Owning registry |
|---|---|
| `line` | `10_systems/JOBS.md` / `00_vision/GLOSSARY.md` Job lines (+`novice`). |
| `tier` | `10_systems/JOBS.md` §1: `novice`·`first`·`second`·`third`. |
| `spec` | `10_systems/JOBS.md` §0 / `00_vision/GLOSSARY.md` Job lines (v3): `ironbrand`·`stoneguard`·`warcaller` (bulwark) · `pathstalker`·`sureshot` (keeneye) · `runeweaver`·`cindercall`·`frostbind` (weaver) · `duskstep`·`wildcard` (flicker). |
| `weapon_type` | `00_vision/GLOSSARY.md` Weapon types (owner `10_systems/ITEMS.md`): `blade`·`bow`·`staff`·`dirk`. |
| `stat_growth.main_primary` | `00_vision/GLOSSARY.md` Primary stats (owner `10_systems/STATS.md`): `might`·`finesse`·`focus`·`fortune` (or `null`). |
| `advancement.trainer_town` | `docs/WORLD_PLAN.md` region slugs (job-instructor home towns per `docs/WORLD_PLAN.md` "Job instructors"): `ashfall`·`tidewatch`·`verdant`·`millbrook` (or `null`). |

## Example

```yaml
# illustrative — a DERIVED resource (coding pass generates all 15 from JOBS.md + STATS.md;
# this is not authored in Phase D). Growth values are copied from STATS.md §4 — do not hand-edit.
# A specialization resource: Stoneguard, one of bulwark's three Lv-40 branch choices (JOBS §2.3).
id: job_bulwark_stoneguard
name: Stoneguard
line: bulwark
tier: second
spec: stoneguard
advancement_level: 40
weapon_type: blade
stat_growth:
  main_primary: might
  base_primaries: { might: 5, finesse: 5, focus: 5, fortune: 5 }   # STATS §4.1 (global)
  growth_rows:                                                     # STATS §4.2 (copied)
    - { band: novice,   applies_levels: "2-8", main_delta: 1, off_delta: 1 }
    - { band: advanced, applies_levels: "9+",  main_delta: 3, off_delta: 1 }   # specified to Lv 100 today; extension toward cap 300 is STATS §4.2's future-arc design
  free_points_per_level: 2                                         # STATS §4.3 (global)
skills: [skill_bulwark_014, skill_bulwark_015, skill_bulwark_016, skill_bulwark_017, skill_bulwark_018, skill_bulwark_019, skill_bulwark_020]
advancement:
  requires_prior: job_bulwark_first   # Lv-40 branch point: siblings ironbrand/warcaller are mutually exclusive per character (JOBS §1)
  trainer_town: ashfall        # bulwark home town = Cindershelf (Ashfall), WORLD_PLAN "Job instructors"; trial routes through the Clockwork Ruins
  quest: null          # backfilled by the generator from the Phase D trainer-quest set (JOBS §1 OQ)
  trainer_npc: null    # backfilled from the Phase D trainer NPC
```

## Validation rules

Schema-specific checks. Note: JobData is **exempt from `docs/VALIDATION.md` check 3** (front-matter)
per File conventions; it is still subject to referential integrity (check 2) and ID uniqueness
(check 4, `id` unique among jobs).

1. **Identity ↔ roster (hard).** `id`, `name`, `line`, `tier`, `spec`, `advancement_level`, and
   (for the 14 authored advancement jobs) `weapon_type` must match the `10_systems/JOBS.md` §0/§1
   roster: `tier`→`advancement_level` is `novice`→1, `first`→8, `second`→40; `spec` is present iff
   `tier: second`, is one of the **line's own** spec tokens (2 for `keeneye`/`flicker`, 3 for
   `bulwark`/`weaver`), and agrees with `id`; `third` has no authored advancement level
   (named-and-reserved only — no third-tier resource exists this run); `weapon_type` is the line's
   GLOSSARY weapon (every spec keeps its line's weapon, `10_systems/JOBS.md` §1); `job_novice`
   omits `weapon_type` and sets `main_primary: null`.
2. **Skill list ↔ ID range (hard).** `skills` equals the job's sub-block from `docs/ID_REGISTRY.md`
   / `10_systems/JOBS.md` §1: first `001`–`006`; spec #1 `007`–`013`, spec #2 `014`–`020`, spec #3
   `021`–`027` (a spec resource lists exactly its own 7-skill block); `job_novice`
   `skill_novice_001`–`004`. `028`–`045` (reserved 3rd tier) and `046`–`060` (reserved growth)
   never appear in an authored `skills` list. Every id exists as a skill content file (check 2).
   No id outside the line's block.
3. **`main_primary` (hard).** For the 14 authored advancement jobs, `stat_growth.main_primary` is the line's
   primary (`bulwark`→`might`, `keeneye`→`finesse`, `weaver`→`focus`, `flicker`→`fortune`,
   `10_systems/STATS.md` §1 / `10_systems/JOBS.md` §0) — identical across a line's specs (the Lv-40
   branch is a skill-kit choice, not a stat re-class, `10_systems/JOBS.md` §1); `job_novice` → `null`.
4. **Growth baked from STATS (hard).** `stat_growth.base_primaries`, `growth_rows`, and
   `free_points_per_level` must equal the `10_systems/STATS.md` §4.1/§4.2/§4.3 values (the generator
   copies them; a mismatch means the resource drifted from the owner doc).
5. **Advancement tree (hard).** `advancement.requires_prior` forms the v3 branching tree
   (`00_vision/SCOPE.md`, `10_systems/JOBS.md` §1): `first`←`job_novice`; every spec of a line ←
   that line's `job_<line>_first`. A character enters exactly one spec at Lv 40 and the sibling
   specs are permanently locked for it — a per-character runtime rule (`10_systems/SKILL_SYSTEM.md`
   §2 line/spec gate), not a resource-level link. A `third`←`second` link is not applicable this
   run (named-and-reserved). `advancement.trainer_town` is the line's home-town region for **both**
   advancements — the same instructor issues the Lv-40 spec choice, whose trial routes through the
   Clockwork Ruins (`bulwark`→`ashfall`, `keeneye`→`tidewatch`, `weaver`→`verdant`,
   `flicker`→`millbrook`; `docs/WORLD_PLAN.md` "Job instructors"), `null` for novice.
6. **Advancement hooks resolve when set (hard-when-present).** `advancement.quest`/`trainer_npc` are
   `null` until Phase D; once set they must resolve to a `quest_NNN`/`npc_NNN` in the trainer town's
   block (`docs/ID_REGISTRY.md`, `docs/WORLD_PLAN.md`) — a trainer quest/NPC in the line's
   home-town region block for both first and second advancement (bulwark→Cindershelf/Ashfall,
   keeneye→Tidewatch Port/Tidewatch, weaver→Mossmere/Verdant, flicker→Millbrook Central/Millbrook;
   `docs/WORLD_PLAN.md` "Job instructors"). A non-null broken ref fails (check 2).

## Template

```yaml
# DERIVED resource shape (coding pass emits 15 of these). Not a 50_content authoring template.
id: {job_novice | job_{line}_first | job_{line}_{spec}}
name: "{JOBS.md §0 display name}"
line: {bulwark|keeneye|weaver|flicker|novice}
tier: {novice|first|second}           # third is named-and-reserved only, not authored (see Fields)
# spec: {spec token}                  # required iff tier: second — one of the line's specs (JOBS §0)
advancement_level: {1|8|40}           # per tier; 40 = the permanent one-spec branch choice (JOBS §1)
stat_growth:
  main_primary: {might|finesse|focus|fortune}   # null for novice; identical across a line's specs
  base_primaries: { might: {n}, finesse: {n}, focus: {n}, fortune: {n} }   # from STATS §4.1
  growth_rows:                                                             # from STATS §4.2
    - { band: novice,   applies_levels: "2-8", main_delta: {n}, off_delta: {n} }
    - { band: advanced, applies_levels: "9+",  main_delta: {n}, off_delta: {n} }   # STATS §4.2 (specified to Lv 100; cap-300 extension is future-arc)
  free_points_per_level: {n}                                              # from STATS §4.3
skills: [{the job's ID sub-block from ID_REGISTRY / JOBS §1: first 001-006; spec blocks 007-013 / 014-020 / 021-027}]
advancement:
  requires_prior: {job_novice | job_{line}_first | null}   # specs hang off their line's first job (the Lv-40 branch)
  trainer_town: {ashfall|tidewatch|verdant|millbrook|null}
  quest: {quest_NNN | null}            # backfilled by the generator from the Phase D trainer-quest set
  trainer_npc: {npc_NNN | null}        # backfilled from the Phase D trainer NPC
# weapon_type omitted for novice; else:
# weapon_type: {blade|bow|staff|dirk}
```

## Open Questions

- **No job ID block in `docs/ID_REGISTRY.md`.** Jobs are derived Resources, not minted content IDs,
  so this schema proposes `job_novice` / `job_<line>_first` / `job_<line>_<spec>` without a reserved registry block. If a
  block is later wanted (e.g., for quest/save references to a job), add it to `docs/ID_REGISTRY.md`;
  until then these IDs are schema-local. Confirm at the C/E gate.
- **Front-matter exemption.** JobData carries no `id`/`schema`/`references` front-matter trio because
  it is not a `50_content` file (`docs/VALIDATION.md` check 3 targets content files). Confirm the
  validator special-cases derived-resource schemas so this exemption is explicit rather than a silent
  gap in check 3.
- **Growth redundancy.** All growth fields except `main_primary` are global constants
  (`10_systems/STATS.md` §4.1–§4.3), baked identically into all 15 resources. If the coding pass
  prefers a single shared growth model referenced by `main_primary` alone, that is an
  `30_engineering/ENGINEERING_STANDARDS.md` implementation choice; this schema documents the
  self-contained form. Default: baked-per-resource.
- **Cumulative vs per-job `skills`.** This schema lists each job's **own** unlock block and leaves
  cumulative availability (novice + first + the character's one chosen spec) to the runtime
  (`10_systems/SKILL_SYSTEM.md` §2 line/spec gate). If the coding pass wants JobData to enumerate
  all skills usable at that job (prior tiers included), that is a generator choice — flag it;
  default is per-job.
- **Advancement quest/NPC IDs are Phase D.** `advancement.quest`/`trainer_npc` stay `null` until
  `10_systems/QUESTS.md` / Phase D author the trainer quests and NPCs (`10_systems/JOBS.md` §1 OQ);
  the generator backfills them then. Whether a `shards`/item gate accompanies the quest is
  `10_systems/ECONOMY.md`/`10_systems/QUESTS.md`'s call (default quest-only).
