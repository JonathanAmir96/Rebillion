# quest.schema.md — One-file-per-quest content shape (quest_NNN)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/QUESTS.md, 10_systems/LEVELING.md, 10_systems/ECONOMY.md, 10_systems/DROPS.md,
10_systems/ITEMS.md, 10_systems/INVENTORY.md, 10_systems/JOBS.md, 10_systems/PERSISTENCE.md,
10_systems/social/RAID.md,
15_maps_system/MAP_INTERACTABLES.md, 15_maps_system/MAPS_SYSTEM.md, docs/ID_REGISTRY.md,
docs/WORLD_PLAN.md, docs/VALIDATION.md

## Purpose

Defines the content shape of one **quest** (`quest_NNN`) — the 120 quests in `00_vision/SCOPE.md`
/ `docs/ID_REGISTRY.md`. A quest file is the data a Phase D author fills and the coding pass
loads: the anatomy fields `10_systems/QUESTS.md` §1 names (giver/turn-in, level gate, prereqs), an
ordered set of the four `10_systems/QUESTS.md` §3 step types, and an `exp`/`shards`/item reward
budgeted against `10_systems/LEVELING.md`/`10_systems/ECONOMY.md` per `10_systems/QUESTS.md`
§4–§5. It is read by the quest runtime (`10_systems/QUESTS.md` §9), the quest-log UI
(`10_systems/QUESTS.md` §8, `10_systems/HUD.md`), and — for `reach`/`collect` steps — the map
interactable system (`15_maps_system/MAP_INTERACTABLES.md`, `15_maps_system/MAPS_SYSTEM.md`).
This schema owns the **field shape and enum owners**; it never restates the reward formulas, the
tag-eligibility rule, or the zone-declaration mechanism — it cites them.

## File conventions

- **One entity per file.** `50_content/quests/quest_NNN.yaml`, zero-padded three digits,
  `quest_001`–`quest_120` all authored (`docs/ID_REGISTRY.md` Quests block): the eleven region
  blocks plus the 8 raid intro/handler quests — `quest_087`–`090` (arc-1 raids),
  `quest_099`–`100` (`raid_deepfrost`), `quest_119`–`120` (`raid_voidtide`) — which are ordinary
  quest files serving `10_systems/social/RAID.md` §3's intro/handler pattern.
  The file's `id` is its filename stem; both immutable.
- **Region ↔ ID block.** A quest's `id` must fall inside its `region`'s sub-range in
  `docs/ID_REGISTRY.md`'s Quests table (e.g. Emberfoot `quest_001`–`010`); this schema does not
  restate the eleven per-region ranges.
- Job-advancement trainer quests are **ordinary quest files** — `10_systems/QUESTS.md` §2 fixes
  that no separate "job-gate" field exists; the trainer relationship is expressed entirely through
  `quest_type: main` + `prereqs` (the prior tier's trainer quest) + the giver being a trainer NPC.
  The four 1st-advancement trainer quests' mutual exclusivity (§2) is wired through each trainer
  NPC's own quest-offer list, **not** a field on this schema (see Open Questions).

## Fields

Static content-definition files, loaded identically by client and server; the `authority` tag
marks who owns the *runtime effect* the field drives (`10_systems/PERSISTENCE.md` §1). Accept
gates, step progress, and turn-in grants are **server-authoritative**
(`10_systems/QUESTS.md` §9). Front-matter obeys `docs/VALIDATION.md` check 3.

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `quest_NNN` | yes | `docs/ID_REGISTRY.md` Quests | Zero-padded; immutable; in-range for its `region` block (Validation). `server`. |
| `schema` | string | yes | this file | Literal `20_schemas/quest.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list[doc name] | yes | `docs/VALIDATION.md` §3 | Baseline `[QUESTS, LEVELING, ECONOMY, DROPS, WORLD_PLAN]` (every `kill` step relies on DROPS §7 tag-eligibility; `region`/step-target placement relies on WORLD_PLAN, matching `20_schemas/npc.schema.md`'s convention for its own `region` field); add `ITEMS` when `rewards.items` present; add `JOBS` for job-trainer quests; add `RAID` for the 8 raid intro/handler quests (`10_systems/social/RAID.md` §3). |
| `name` | string | yes | — | Display name, US spelling. `client`. |
| `region` | enum | yes | `docs/WORLD_PLAN.md` / GLOSSARY Region slugs | Scopes `giver_npc`/`turn_in_npc`/step-target region membership (Validation). `server`. |
| `quest_type` | enum | yes | `10_systems/QUESTS.md` §1 (this doc's own enum) | `main`\|`side`. Drives the §4/§5 reward-budget bands. **Added by this schema** — the task's field list omitted it, but §4/§5's formulas cannot be validated without it (see Open Questions). `server`. |
| `giver_npc` | string `npc_NNN` | yes | `docs/ID_REGISTRY.md` NPCs | The offering NPC. Must exist and live in `region`'s NPC block (Validation). `server`. |
| `turn_in_npc` | string `npc_NNN` | no — defaults to `giver_npc` | `10_systems/QUESTS.md` §1 | If present, must exist and live in `region`'s NPC block (Validation). `server`. |
| `level_requirement` | int 1–300 (cap; authored ≤80) | yes | `10_systems/QUESTS.md` §6 | Hard accept gate. `server`. |
| `recommended_level` | int 1–300 (cap; authored ≤80) | yes | `10_systems/QUESTS.md` §6 | Display-only; no mechanical gate. Normally equals `level_requirement` for `main` (warn if not, §6). `client`. |
| `prereqs` | list[`quest_NNN`] | no — default `[]` | `10_systems/QUESTS.md` §2 | Must-already-be-completed quests; both this and `level_requirement` gate acceptance. Every entry resolves; the full prereq graph is acyclic (Validation, hard — task's explicit rule). `server`. |
| `steps` | list[step] | yes (≥1) | `10_systems/QUESTS.md` §3 | Guideline 1–3, up to 4 for a chain-establisher. Default parallel (any order); see `requires_step`. Sub-fields below. `server`. |
| `steps[].type` | enum | yes | `10_systems/QUESTS.md` §3 (this doc's own fixed 4-value set, not a GLOSSARY family) | `kill`\|`collect`\|`talk`\|`reach`. |
| `steps[].target` | id \| list[id] | yes | type-dependent, below | `kill`: one `mob_NNN` **or a short explicit list** (§3 — count applies across the list, see Open Questions); `collect`: one `item_etc_NNNN` **or** `item_use_NNNN` (§3.1 — task's compressed prefix list omitted the `item_use` case, added here); `talk`: one `npc_NNN`; `reach`: one `map_NNN` (paired with `steps[].zone` below). |
| `steps[].zone` | string | `reach` only | `10_systems/QUESTS.md` §3; `15_maps_system/MAPS_SYSTEM.md` (pending) | The named trigger zone/waypoint on `target` (§3: "map_NNN + a named trigger zone/waypoint"). **Added by this schema** — a bare map id alone under-specifies a `reach` step per QUESTS.md's own anatomy. Format unresolved pending `MAPS_SYSTEM.md` (Open Questions). |
| `steps[].count` | int ≥1 | `kill`/`collect`: yes; `talk`/`reach`: no — default `1` | `10_systems/QUESTS.md` §3 | Repeat count. |
| `steps[].requires_step` | int (1-based index into this quest's own `steps`) | no | `10_systems/QUESTS.md` §3 | Forces sequencing (same prereq-linking pattern as quest-level `prereqs`, §2/§3). Default: all steps open in parallel. Indexing scheme is this schema's own choice — QUESTS.md names the feature but not an addressing mechanism (Open Questions). `server`. |
| `rewards` | map | yes | `10_systems/QUESTS.md` §4–§5 | Sub-fields below. No reward *numbers* are authored by this schema (cited, not restated). |
| `rewards.exp` | int | yes | `10_systems/QUESTS.md` §4; `10_systems/LEVELING.md` §1 | `= round(pct · exp_to_next(quest_level))`, `pct` ∈ the `quest_type`'s §4 band. Every quest pays `exp` — the raid intro/handler quests (`quest_087`–`090`/`099`–`100`/`119`–`120`) are ordinary quests on the ordinary §4/§5 reward bands (`10_systems/social/RAID.md` §3; raid *clear* rewards are `RAID.md` §6's, never a quest field). `server`. |
| `rewards.shards` | int | yes | `10_systems/QUESTS.md` §5; `10_systems/DROPS.md` §3 | `side = mean_shards_normal(quest_level)·4`; `main = mean_shards_normal(quest_level)·15` (exact formula, not a band). `server`. |
| `rewards.items` | list `{id, qty}` | no | `10_systems/ITEMS.md`; `20_schemas/item.schema.md` | No budget cap fixed by `10_systems/QUESTS.md` (Phase D authors against `ITEMS`/`ECONOMY` value bands). Each `id` resolves; `qty` ≥1. `server`. |
| `flavor` | string | yes | `00_vision/PILLARS.md` P1 | ≤2 sentences, US spelling; quest-log/journal description. `client`. |
| `offer_text` | string | yes | `10_systems/QUESTS.md` §8 | ≤2 sentences, `giver_npc`'s dialog voice, shown on offer. `client`. |
| `complete_text` | string | yes | `10_systems/QUESTS.md` §8 | ≤2 sentences, `turn_in_npc`'s dialog voice, shown on turn-in. `client`. |

## Enums

Every enum value comes from its owning registry; this schema points, never redefines.

| Field | Owning registry |
|---|---|
| `region` | `docs/WORLD_PLAN.md` / `00_vision/GLOSSARY.md` Region slugs. |
| `quest_type` | `10_systems/QUESTS.md` §1 (this schema's addition, not a GLOSSARY family): `main`·`side`. |
| `steps[].type` | `10_systems/QUESTS.md` §3 (this doc's own fixed set, not a GLOSSARY family): `kill`·`collect`·`talk`·`reach`. |
| `steps[].target` prefix | Matches `steps[].type`: `mob_NNN` (kill) · `item_etc_NNNN`/`item_use_NNNN` (collect) · `npc_NNN` (talk) · `map_NNN` (reach) — all `docs/ID_REGISTRY.md`. |

## Example

```yaml
# illustrative shape only — not a mirror of the minted quest_014 (real Millbrook files live in
# 50_content/quests/). A Lv-10 quest sits in millbrook's band (Lv 8-14, WORLD_PLAN R2), inside
# the Millbrook quest block quest_011-024 (ID_REGISTRY). Numbers are exact per LEVELING.md §1
# (Lv10 exp_to_next=8,480) and DROPS.md §3 (Lv10 boss-mean=270) via QUESTS.md §4-§5's own formulas.
id: quest_014
schema: 20_schemas/quest.schema.md
references: [QUESTS, LEVELING, ECONOMY, DROPS, WORLD_PLAN, ITEMS]
name: Ticks in the Granary
region: millbrook
quest_type: main
giver_npc: npc_027
level_requirement: 10
recommended_level: 10
prereqs: [quest_010]
steps:
  - type: kill
    target: mob_018
    count: 8
  - type: talk
    target: npc_028
    count: 1
    requires_step: 1        # must finish the kill step before this talk unlocks
rewards:
  exp: 1696                 # round(0.20 * 8,480); main band 15-30% = 1,272-2,544 (QUESTS §4)
  shards: 270                # mean_shards_normal(10)*15 = 18*15 (QUESTS §5 / DROPS §3)
  items:
    - { id: item_use_0001, qty: 3 }
flavor: "Tickmounds have burrowed under the granary floor, and the flour spoils by the sackful.
  Millbrook's tables go hungry while the millworks stand idle."
offer_text: "Clear the bloated things out from under my granary, then tell Sergeant Ashe the
  floor is safe to reopen."
complete_text: "Ashe's word came ahead of you — good work. The stones turn again tonight."
```

## Validation rules

Schema-specific checks, beyond `docs/VALIDATION.md` globals (§1–§4).

1. **ID ↔ region block (hard).** `id` falls in `region`'s `docs/ID_REGISTRY.md` Quests sub-range.
2. **Giver/turn-in (hard).** `giver_npc` and `turn_in_npc` (explicit or defaulted) each resolve to
   an existing `npc_NNN` that lives in `region`'s `docs/ID_REGISTRY.md` NPCs block.
3. **Step target resolution (hard).** Every `steps[].target` (each id, if a `kill` list) resolves
   to an entity of the type its `steps[].type` requires (`docs/VALIDATION.md` §2); `reach` steps
   additionally require a non-empty `zone`.
4. **Kill-step region band (warn).** A `kill` step's target mob(s) should belong to `region`'s
   `docs/ID_REGISTRY.md` Monsters block (or an adjacent band per `docs/WORLD_PLAN.md`); flagged
   loose since a late quest may reasonably send players back to an earlier region.
5. **Collect-step sourcing (warn).** A `collect` step's target item should either appear in a
   `drop_mob_NNN` table for a mob in `region` (`10_systems/QUESTS.md` §3.1's first mechanism,
   `20_schemas/drop_table.schema.md`) or be understood as `quest_object`-granted
   (`15_maps_system/MAP_INTERACTABLES.md` §10, unverifiable from this file alone). Warn-only,
   since the two mechanisms are not distinguishable from the quest file itself.
6. **Prereq graph acyclic (hard).** Every `prereqs[]` entry resolves to an existing `quest_NNN`;
   the directed graph formed by all quests' `prereqs` contains no cycle.
7. **`requires_step` resolution (hard).** Each `steps[].requires_step` is a valid 1-based index
   into this same quest's `steps` list, not self-referential, and introduces no cycle among the
   quest's own steps (same acyclic principle as rule 6, applied locally).
8. **Reward — `exp` (hard).** Every quest: `rewards.exp == round(pct · exp_to_next(level))`
   for some `pct` inside the `quest_type`'s `10_systems/QUESTS.md` §4 band, `exp_to_next` from
   `10_systems/LEVELING.md` §1 at `level_requirement`. There is no zero-`exp` quest class — the
   raid intro/handler quests pay ordinary rewards (`10_systems/social/RAID.md` §3).
9. **Reward — `shards` (hard).** Equals the `10_systems/QUESTS.md` §5 formula exactly
   (`mean_shards_normal(level_requirement)` from `10_systems/DROPS.md` §3, ×4 for `side`, ×15 for
   `main`) — a fixed formula, not a tunable band.
10. **Reward — `items` (hard for resolution only).** Each `id` resolves to an existing item;
    `qty` ≥1. No budget check (none is fixed by `10_systems/QUESTS.md`).
11. **`recommended_level` (warn).** For `quest_type: main`, should equal `level_requirement`
    (`10_systems/QUESTS.md` §6 — "normally equal," not absolute).
12. **`quest_type` ↔ trainer chains (warn).** A quest whose `prereqs` names another trainer quest
    (job-advancement chain, `10_systems/JOBS.md` §1) should be `quest_type: main`
    (`10_systems/QUESTS.md` §2 groups trainer quests under `main`).
13. **Text length (warn).** `flavor`/`offer_text`/`complete_text` each ≤2 sentences
    (`docs/VALIDATION.md` §7 OQ pattern — mechanical length lint is warn-only by default there).

## Template

```yaml
id: quest_{NNN}
schema: 20_schemas/quest.schema.md
references: [QUESTS, LEVELING, ECONOMY, DROPS, WORLD_PLAN]   # add ITEMS if rewards.items; JOBS if trainer quest; RAID if raid intro/handler quest
name: "{Display Name}"
region: {region_slug}
quest_type: {main|side}
giver_npc: npc_{NNN}
level_requirement: {1..300}         # legal to the Lv-300 cap; authored quests top out at 80
recommended_level: {1..300}         # usually == level_requirement for main
steps:
  - type: {kill|collect|talk|reach}
    target: {mob_NNN | [mob_NNN, ...] | item_etc_NNNN | item_use_NNNN | npc_NNN | map_NNN}
    # zone: "{trigger_zone_id}"      # reach only, required for that type
    count: {int}                    # required for kill/collect; default 1 for talk/reach
  # add more step objects (guideline 1-3, up to 4); requires_step forces sequencing
rewards:
  exp: {int}                        # round(pct * exp_to_next(level)) per the quest_type's QUESTS §4 band
  shards: {int}                     # mean_shards_normal(level) * 4 (side) or *15 (main)
  # items: [{ id: item_{equip|use|etc}_{NNNN}, qty: {int} }]   # optional
flavor: "{<=2 sentences}"
offer_text: "{<=2 sentences, giver's dialog voice}"
complete_text: "{<=2 sentences, turn-in's dialog voice}"

# --- optional fields (omit if unused): ---
# turn_in_npc: npc_{NNN}            # defaults to giver_npc
# prereqs: [quest_{NNN}, ...]       # default []
```

## Open Questions

- **`quest_type` added by this schema.** The task's field list did not name it, but
  `10_systems/QUESTS.md` §1's own anatomy table requires it and §4/§5's reward-budget formulas
  branch on it — reward validation is impossible without it. Added rather than silently omitted;
  confirm the field name against any orchestrator convention.
- **`level_requirement`/`giver_npc`/`turn_in_npc` vs. the task's shorthand.** The task brief uses
  `level_req`/`giver`/`turn_in`; `10_systems/QUESTS.md` §1 uses `level_requirement`/`giver_npc`/
  `turn_in_npc` throughout. This schema keeps QUESTS.md's own spelling for cross-doc consistency
  (a Phase D author reading both files should see one vocabulary). Flagged, not guessed.
- **`steps[].zone` is this schema's addition.** `10_systems/QUESTS.md` §3 requires a `reach` step
  to carry both a `map_NNN` and a named trigger zone/waypoint, but that doc explicitly defers the
  zone's declaration shape to `15_maps_system/MAPS_SYSTEM.md` (not yet authored), "assumed
  analogous to `10_systems/SPAWN.md` §1's `spawn_zones` rect pattern but not confirmed" (QUESTS.md's
  own OQ). This schema types `zone` as a bare string placeholder pending that doc; format may
  change.
- **`requires_step` addressing.** `10_systems/QUESTS.md` §3 names the feature but not how one step
  references another. This schema picks a 1-based index into the quest's own `steps` list as the
  simplest self-contained scheme; confirm before Phase D authors sequenced (non-parallel) quests.
- **`kill` step count semantics with a multi-mob target list.** `10_systems/QUESTS.md` §3 allows "a
  short explicit list" of `mob_NNN` for a kill step but does not say whether `count` is a total
  across the list (this schema's assumption — "kill any combination of these N times") or per-mob.
  Confirm at the D gate before multi-target kill steps are authored.
- **Trainer-quest mutual exclusivity has no schema field.** `10_systems/QUESTS.md` §2 fixes that
  the four 1st-advancement trainer quests are mutually exclusive "by authoring convention," wired
  through each trainer NPC's own quest-offer list — a different content file (NPC data) not
  covered by this schema or this task. Nothing here enforces it; flagged so it isn't assumed
  covered.
- **Collect-step sourcing mechanism isn't a field.** Whether a `collect` item comes from the
  ordinary drop pipeline or a `quest_object` (`10_systems/QUESTS.md` §3.1) is determined by *map*
  data (`15_maps_system/MAP_INTERACTABLES.md` §10's `required_quest_flag`), not by anything in this
  quest file — this schema cannot and does not distinguish the two mechanisms; validation rule 5
  is warn-only for exactly this reason.
- **Raid/party quest-credit sharing** is explicitly deferred to `10_systems/social/PARTY.md`
  (`10_systems/QUESTS.md` OQ); this schema assumes unshared (each character needs their
  own kill tag/collect item) and carries no field for it.
