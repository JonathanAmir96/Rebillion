# npc.schema.md — YAML content schema for one authored NPC

References: 00_vision/GLOSSARY.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md, docs/VALIDATION.md,
15_maps_system/MAP_INTERACTABLES.md, 15_maps_system/MAP_CONNECTIONS.md, 10_systems/ECONOMY.md,
10_systems/ENHANCEMENT.md, 10_systems/INVENTORY.md, 10_systems/PERSISTENCE.md,
10_systems/DEATH_PENALTY.md, 10_systems/QUESTS.md, 20_schemas/map.schema.md

Formalizes the YAML typing for one of the 84 authored NPCs (`docs/ID_REGISTRY.md`). Town casts and
per-region NPC counts are `docs/WORLD_PLAN.md`'s; which interactable a service ultimately opens
(inn bed, storage chest, waygate console) is `15_maps_system/MAP_INTERACTABLES.md`'s; prices are
`10_systems/ECONOMY.md`'s. This doc never restates those — it fixes field names, types, the `role`
enum, and the schema-local checks a validator runs on top of them.

**Single-source rule.** Quest linkage lives in quest files only — a quest's `giver_npc` and
`turn_in_npc` fields (`10_systems/QUESTS.md` §1) are the sole place an NPC↔quest relationship is
recorded. This schema has **no** `quests`/`quest_ids`/`gives_quest` field of any kind, and none may
be added without revising this doc; an NPC file that lists a quest fails schema conformance
(`docs/VALIDATION.md` §3).

## Purpose

The content schema for one NPC in the 84-NPC cast (`docs/ID_REGISTRY.md`). Read by: Phase D
region-batch authors writing `npc_NNN.yaml` files; `10_systems/QUESTS.md` content authors wiring
`giver_npc`/`turn_in_npc` references; `20_schemas/map.schema.md` (bidirectional `map`/`npcs`
check); and the Phase E coding pass loading NPC/dialogue/shop data (`60_agents/`, not yet
authored).

## File conventions

One file per NPC at `50_content/npcs/npc_NNN.yaml` — `NNN` zero-padded to 3 digits, matching the
NPC's reserved slot in `docs/ID_REGISTRY.md`'s per-region blocks (`npc_001`–`npc_120`, 84
authored). No batch tables. The file's `id` field and its filename's `NNN` must agree.

## Fields

**Authority tags:** like `20_schemas/map.schema.md`, this schema's fields are static, design-time
content (a shop's stock list, a greeting line) — `10_systems/PERSISTENCE.md`'s `server`/`client`/
`shared` taxonomy governs *save state*, not this authored content, so most rows carry no tag.
Where a `services` entry ties to genuine server-authoritative runtime state elsewhere (a bank's
contents, a bind point), the tag is noted on `services`, not invented per sub-field here.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string `npc_NNN` | yes | Front-matter; immutable; `NNN` must fall inside this NPC's region block (`docs/ID_REGISTRY.md`) |
| `schema` | string | yes | Front-matter; literal `20_schemas/npc.schema.md` |
| `references` | list of string | yes | Front-matter; bare system-doc names (no path/extension) — baseline set in Validation rules |
| `name` | string | yes | Display name; no fixed pattern owned by any doc — a Phase D authoring choice |
| `region` | enum, region slug | yes | Owner: `docs/WORLD_PLAN.md`; must equal the home `map`'s `region` (Validation) |
| `map` | string `map_NNN` | yes | Home map. That map's `npcs` list must include this NPC's `id`, and vice versa (`20_schemas/map.schema.md`) |
| `role` | enum, ≤12 tokens (this doc) | yes | Owner: this schema (see Enums); proposed for `00_vision/GLOSSARY.md` Provisional promotion at the C gate, mirroring `10_systems/JOBS.md` §0's pattern for job-line tokens |
| `shop` | `{items: [item id]}` | no | `item_equip_*`/`item_use_*`/`item_etc_*` ids only — **no price field anywhere in this file**; price is always read from the item's own `10_systems/ECONOMY.md` §4 band |
| `services` | list of enum (this doc) | no | See Enums; role-service consistency in Validation. `inn_rest`/`storage`/`waygate` tie to `server`-authoritative state elsewhere (bind point — `10_systems/DEATH_PENALTY.md` §4; bank contents — `10_systems/INVENTORY.md` §7/`10_systems/PERSISTENCE.md`; waygate unlock set — `15_maps_system/MAP_CONNECTIONS.md` §3) that this file does not itself store |
| `dialog` | `{greeting, idle?, farewell?}` | `greeting` required; `idle`/`farewell` optional | Each ≤2 sentences |
| `portrait` | string, token | no | Asset resolved at Phase C/D; no file path. Proposed convention `portrait_<npc_id>` (this schema's own first-pass — no `40_assets/` doc owns portrait tokens yet, see Open Questions) |
| `flavor` | string, ≤2 sentences | yes | General descriptive blurb about the NPC, distinct from what they *say* (`dialog`) |

## Enums

### `role` (owner: this schema — proposed for GLOSSARY promotion at the C gate)

Aligned to `docs/WORLD_PLAN.md`'s town casts and `15_maps_system/MAP_INTERACTABLES.md`'s services.
10 of the ≤12 budget used now.

| `role` | Typical setting | Implied minimum (Validation) |
|---|---|---|
| `merchant` | General-goods town shop interior (outfitter, fishmonger, chandlery, market hall) | Typically carries `shop`; no forced `services` |
| `innkeeper` | Inn interior, one per bind town (`10_systems/DEATH_PENALTY.md` §4) | `services` ⊇ {`inn_rest`} |
| `blacksmith` | Smithy interior (equipment vendor) | Typically carries `shop`; may also carry `enhance` (see Open Questions) |
| `enchanter` | Dedicated enchanter interior (e.g. Arcane Sanctum) or a town's smithy | `services` ⊇ {`enhance`} |
| `banker` | Co-located with a `storage_chest` (`15_maps_system/MAP_INTERACTABLES.md` §8) | `services` ⊇ {`storage`}; optional flavor around what is otherwise a self-service object |
| `quest_giver` | Any interior/town/field NPC who offers or accepts a quest | No forced `services`; should be named as `giver_npc`/`turn_in_npc` by ≥1 quest file (soft cross-file check, see Open Questions) |
| `waygate_keeper` | Co-located with a `waygate_console` (`15_maps_system/MAP_INTERACTABLES.md` §9) | `services` ⊇ {`waygate`}; optional flavor around what is otherwise a self-service object |
| `guide` | Tutorial/help-lean NPC, e.g. near a `main` spawn or a starter town | No forced `services` |
| `handler` | Camp/outpost logistics (e.g. Rift-camp vendors/handlers, `docs/WORLD_PLAN.md` R12) | No forced `services`; `shop`/`services` authored per instance |
| `flavor` | Pure ambiance/lore NPC | No `shop`, no `services` |

A role's implied minimum is a **floor, not a ceiling** — an NPC may carry additional `services`
beyond its role's forced minimum (e.g., a `blacksmith` that also offers `enhance` in a town with no
separate enchanter interior).

### `services` (owner: this schema)

`inn_rest` (`15_maps_system/MAP_INTERACTABLES.md` §7, `10_systems/DEATH_PENALTY.md` §4) ·
`storage` (`15_maps_system/MAP_INTERACTABLES.md` §8, `10_systems/INVENTORY.md` §7) · `enhance`
(`10_systems/ENHANCEMENT.md` — no matching `MAP_INTERACTABLES` object; this service is NPC-driven
only) · `waygate` (`15_maps_system/MAP_INTERACTABLES.md` §9, `15_maps_system/MAP_CONNECTIONS.md`
§3)

## Example

Illustrative — real instances land in Phase D.

```yaml
id: npc_002
schema: 20_schemas/npc.schema.md
references: [WORLD_PLAN, MAP_INTERACTABLES, ECONOMY, PERSISTENCE, DEATH_PENALTY]
name: Mira Hearthwell
region: emberfoot
map: map_002
role: innkeeper
shop:
  items: [item_use_0001, item_use_0006]
services: [inn_rest]
dialog:
  greeting: "Warm bed, warmer stew — sit before you fall over."
  farewell: "Mind the cinders on your way out."
portrait: portrait_npc_002
flavor: "Mira has run Emberfoot's inn since before the kiln went quiet, and misses the noise."
```

## Validation rules

Schema-specific checks beyond `docs/VALIDATION.md`'s globals (§1–§7 there):

1. **Role-service consistency.** `innkeeper` → `services` ⊇ {`inn_rest`}; `enchanter` → ⊇
   {`enhance`}; `banker` → ⊇ {`storage`}; `waygate_keeper` → ⊇ {`waygate`}. Other roles carry no
   forced minimum. A role never *caps* `services` (see Enums).
2. **Shop resolution.** Every `shop.items[]` id resolves to an existing `item_equip_*`/
   `item_use_*`/`item_etc_*` content entry (`docs/VALIDATION.md` §2); no price field may appear
   anywhere in this file.
3. **Vendor stock rarity.** Any `item_equip_*` listed in `shop.items` must be `common` rarity
   (`10_systems/ECONOMY.md` §4.2 — vendors stock only `common` basics); `item_use_*`/`item_etc_*`
   entries carry no rarity restriction.
4. **Region/ID placement.** `id`'s `NNN` falls inside this NPC's `region`'s block
   (`docs/ID_REGISTRY.md`); `region` equals the home `map`'s `region`
   (`20_schemas/map.schema.md`).
5. **Bidirectional home-map listing.** `map` resolves to an existing map file whose `npcs` list
   includes this NPC's `id`, and vice versa.
6. **No quest fields.** This schema defines no `quest`/`quests`/`giver_for`/similar field; a
   content file adding one fails schema conformance (`docs/VALIDATION.md` §3) per the
   single-source rule above.
7. **Service/object co-location (soft).** If `services` includes `inn_rest`/`storage`/`waygate`,
   the home map's `interactables` (or, for `waygate`, its `portals`) should include a matching
   `inn_bed`/`storage_chest`/`waygate_console` object (`20_schemas/map.schema.md`) — a cross-file
   consistency expectation, not enforceable from this file alone.
8. **Dialog/flavor length.** `dialog.greeting`/`idle`/`farewell` and `flavor` are each ≤2 sentences
   (mechanical linting is `docs/VALIDATION.md` §7's existing warn-only proposal, not a hard fail
   here).

## Template

```yaml
id: npc_{NNN}
schema: 20_schemas/npc.schema.md
references: [WORLD_PLAN, MAP_INTERACTABLES, ECONOMY] # add PERSISTENCE if services non-empty; add ENHANCEMENT if role: enchanter or services includes enhance; add DEATH_PENALTY if services includes inn_rest; add MAP_CONNECTIONS if role: waygate_keeper or services includes waygate
name: "{Display Name}"
region: { region_slug }
map: map_{NNN}
role: { merchant|innkeeper|blacksmith|enchanter|banker|quest_giver|waygate_keeper|guide|handler|flavor }
# shop:                          # optional
#   items: [item_{category}_{NNNN}]
# services: [ { inn_rest|storage|enhance|waygate } ]   # optional
dialog:
  greeting: "{≤2 sentences}"
  # idle: "{≤2 sentences}"       # optional
  # farewell: "{≤2 sentences}"   # optional
# portrait: portrait_npc_{NNN}   # optional
flavor: "{≤2 sentences}"
```

## Open Questions

- `blacksmith` vs. `enchanter` role boundary: `10_systems/ENHANCEMENT.md` §5 ties the `enhance`
  service's fee to "a town smith interior," but `docs/WORLD_PLAN.md`'s per-town interior lists name
  an explicit "smithy" only at Millbrook and an explicit "enchanter" only at Arcane Sanctum —
  Emberfoot's and Tidewatch's interior lists name neither. Whether every bind town needs an
  enhance-service NPC, and which role carries it where no smithy/enchanter interior is named, is
  unresolved; flagged for `docs/WORLD_PLAN.md`/`10_systems/ENHANCEMENT.md`'s owners.
- Millbrook's guild hall/tavern/mayor's-house and Arcane Reach's athenaeum/observatory interiors
  (`docs/WORLD_PLAN.md`) don't map cleanly onto one obvious `role` from the enum above. Phase D may
  reuse `quest_giver`/`flavor`/`guide` for these, or a future revision may add 1–2 roles within the
  ≤12 cap. Not resolved here.
- `quest_giver`'s "should appear on ≥1 quest file" expectation is a soft, cross-file-only check —
  this schema cannot enforce it from a single NPC file, and the single-source rule forbids the NPC
  file itself from carrying a quest reference. A real check needs a later reconciliation pass,
  parallel to `docs/VALIDATION.md` §5's world-graph reconciliation for maps; flagged for that doc's
  owner.
- `portrait`'s token convention (`portrait_<npc_id>`, proposed here) has no owner in `40_assets/`
  yet; flag for a future `40_assets/` doc or an `40_assets/ART_BIBLE.yaml` amendment.
- Whether `banker`/`waygate_keeper` NPCs are ever mechanically required (vs. purely optional
  flavor standing near a self-service interactable) is not settled by any system doc; this schema
  treats both roles as optional — a bind town's bank/waygate can function per
  `15_maps_system/MAP_INTERACTABLES.md` with no NPC present at all.
