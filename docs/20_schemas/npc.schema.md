# npc.schema.md — YAML content schema for one authored NPC

References: 00_vision/GLOSSARY.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md, docs/VALIDATION.md,
15_maps_system/MAP_INTERACTABLES.md, 15_maps_system/MAP_CONNECTIONS.md, 10_systems/ECONOMY.md,
10_systems/ENHANCEMENT.md, 10_systems/INVENTORY.md, 10_systems/PERSISTENCE.md,
10_systems/DEATH_PENALTY.md, 10_systems/QUESTS.md, 20_schemas/map.schema.md

## Purpose

The content schema for one NPC in the 120-NPC cast (`docs/ID_REGISTRY.md`) — formalizing the YAML
typing for a town cast entry (`docs/WORLD_PLAN.md`) whose service ultimately opens an interactable
(inn bed, storage chest, coach station; `15_maps_system/MAP_INTERACTABLES.md`) priced by
`10_systems/ECONOMY.md`. This doc never restates those — it fixes field names, types, the `role`
enum, and the schema-local checks a validator runs on top of them. Read by: Phase D region-batch
authors writing `npc_NNN.yaml` files; `10_systems/QUESTS.md` content authors wiring
`giver_npc`/`turn_in_npc` references; `20_schemas/map.schema.md` (bidirectional `map`/`npcs`
check); and the Phase E coding pass loading NPC/dialogue/shop data (`60_agents/`, not yet
authored).

**Single-source rule.** Quest linkage lives in quest files only — a quest's `giver_npc` and
`turn_in_npc` fields (`10_systems/QUESTS.md` §1) are the sole place an NPC↔quest relationship is
recorded. This schema has **no** `quests`/`quest_ids`/`gives_quest` field of any kind, and none may
be added without revising this doc; an NPC file that lists a quest fails schema conformance
(`docs/VALIDATION.md` §3).

## File conventions

One file per NPC at `50_content/npcs/npc_NNN.yaml` — `NNN` zero-padded to 3 digits, matching the
NPC's reserved slot in `docs/ID_REGISTRY.md`'s per-region blocks (`npc_001`–`npc_120`, 120
authored). No batch tables. The file's `id` field and its filename's `NNN` must agree.

## Fields

Static content-definition files, loaded identically by client and server; per
`10_systems/PERSISTENCE.md` §1 every field carries exactly one `authority` tag in its Notes —
`server` (the value drives a server-adjudicated mechanic), `client` (pure local presentation,
never reconciled), or `shared` (none of this schema's fields need it; see
`20_schemas/map.schema.md`'s `moving_platforms` for the tree's example). Front-matter obeys
`docs/VALIDATION.md` check 3.

| Field | Type | Required | References | Notes |
|---|---|---|---|---|
| `id` | string `npc_NNN` | yes | `docs/ID_REGISTRY.md` | Immutable; `NNN` must fall inside this NPC's region block. `server` (identity). |
| `schema` | string | yes | this file | Literal `20_schemas/npc.schema.md` (`docs/VALIDATION.md` §3). |
| `references` | list of string | yes | `docs/VALIDATION.md` §3 | Bare system-doc names (no path/extension) — baseline set in Validation rules. |
| `name` | string | yes | — | Display name; no fixed pattern owned by any doc — a Phase D authoring choice. `client`. |
| `region` | enum | yes | `docs/WORLD_PLAN.md` | Must equal the home `map`'s `region` (Validation). `server`. |
| `map` | string `map_NNN` | yes | `20_schemas/map.schema.md` | That map's `npcs` list must include this NPC's `id`, and vice versa. `server` (world-placement fact). |
| `role` | enum, ≤12 tokens | yes | this schema (see Enums) | Proposed for `00_vision/GLOSSARY.md` Provisional promotion at the C gate, mirroring `10_systems/JOBS.md` §0's pattern for job-line tokens. `server` (gates which services/UI the NPC may serve). |
| `shop` | `{items: [item id]}` | no | `10_systems/ITEMS.md`; `10_systems/ECONOMY.md` §4 | `item_equip_*`/`item_use_*`/`item_etc_*` ids only — **no price field anywhere in this file**; price is always read from the item's own ECONOMY.md band. `server` (transactions are server-authoritative economy state). |
| `services` | list of enum | no | `15_maps_system/MAP_INTERACTABLES.md`; `10_systems/ENHANCEMENT.md`; `10_systems/PERSISTENCE.md` | See Enums; role-service consistency in Validation. `server` — `inn_rest`/`storage`/`coach`/`longship` trigger server-authoritative state elsewhere (bind point, bank contents, coach fare + free-pilgrimage flag, longship fare + scheduled transit) that this file does not itself store. |
| `dialog` | `{greeting, idle?, farewell?}` | `greeting` required; `idle`/`farewell` optional | — | Each ≤2 sentences. `client`. |
| `portrait` | string, token | no | `40_assets/` (not yet authored) | Asset resolved at Phase C/D; no file path. Proposed convention `portrait_<npc_id>` (this schema's own first-pass, see Open Questions). `client`. |
| `flavor` | string, ≤2 sentences | yes | `docs/VALIDATION.md` §7 | General descriptive blurb about the NPC, distinct from what they *say* (`dialog`). `client`. |

## Enums

### `role` (owner: this schema — proposed for GLOSSARY promotion at the C gate)

Aligned to `docs/WORLD_PLAN.md`'s town casts and `15_maps_system/MAP_INTERACTABLES.md`'s services.
11 of the ≤12 budget used now.

| `role` | Typical setting | Implied minimum (Validation) |
|---|---|---|
| `merchant` | General-goods town shop interior (outfitter, fishmonger, chandlery, market hall) | Typically carries `shop`; no forced `services` |
| `innkeeper` | Inn interior, one per bind town (`10_systems/DEATH_PENALTY.md` §4) | `services` ⊇ {`inn_rest`} |
| `blacksmith` | Smithy interior (equipment vendor) | Typically carries `shop`; may also carry `enhance` (see Open Questions) |
| `enchanter` | Dedicated enchanter interior (e.g. Highrune Sanctum, `docs/WORLD_PLAN.md` R10) or a town's smithy | `services` ⊇ {`enhance`} |
| `banker` | Co-located with a `storage_chest` (`15_maps_system/MAP_INTERACTABLES.md` §8) | `services` ⊇ {`storage`}; optional flavor around what is otherwise a self-service object |
| `quest_giver` | Any interior/town/field NPC who offers or accepts a quest | No forced `services`; should be named as `giver_npc`/`turn_in_npc` by ≥1 quest file (soft cross-file check, see Open Questions) |
| `coach_clerk` | Co-located with a `coach_station` (`15_maps_system/MAP_INTERACTABLES.md` §9), one per Harthmoor ring town | `services` ⊇ {`coach`}; grants the one free novice pilgrimage ride (`15_maps_system/MAP_CONNECTIONS.md` §3), otherwise optional flavor around a self-service station |
| `pier_officer` | Stands at an arc-2 longship pier, co-located with a `portal(kind: longship)` (`15_maps_system/MAP_INTERACTABLES.md` §2) | `services` ⊇ {`longship`}; takes the route fare and admits boarders (`15_maps_system/MAP_CONNECTIONS.md` §8.1) — the boarding mechanism, not mere flavor |
| `guide` | Tutorial/help-lean NPC, e.g. near a `main` spawn or a starter town | No forced `services` |
| `handler` | Camp/outpost logistics and raid handlers (the 8 raid-handler quests' NPCs; owner `10_systems/social/RAID.md`) | No forced `services`; `shop`/`services` authored per instance |
| `flavor` | Pure ambiance/lore NPC | No `shop`, no `services` |

A role's implied minimum is a **floor, not a ceiling** — an NPC may carry additional `services`
beyond its role's forced minimum (e.g., a `blacksmith` that also offers `enhance` in a town with no
separate enchanter interior).

### `services` (owner: this schema)

`inn_rest` (`15_maps_system/MAP_INTERACTABLES.md` §7, `10_systems/DEATH_PENALTY.md` §4) ·
`storage` (`15_maps_system/MAP_INTERACTABLES.md` §8, `10_systems/INVENTORY.md` §7) · `enhance`
(`10_systems/ENHANCEMENT.md` — no matching `MAP_INTERACTABLES` object; this service is NPC-driven
only) · `coach` (`15_maps_system/MAP_INTERACTABLES.md` §9, `15_maps_system/MAP_CONNECTIONS.md`
§3; the self-service coach station plus the free-pilgrimage grant) · `longship`
(`15_maps_system/MAP_CONNECTIONS.md` §8 — no matching `MAP_INTERACTABLES` object; the pier officer
*is* the boarding gate, fare per `10_systems/ECONOMY.md` §7.2)

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
   {`enhance`}; `banker` → ⊇ {`storage`}; `coach_clerk` → ⊇ {`coach`}; `pier_officer` → ⊇
   {`longship`}. Other roles carry no forced minimum. A role never *caps* `services` (see Enums).
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
7. **Service/object co-location (soft).** If `services` includes `inn_rest`/`storage`/`coach`, the
   home map's `interactables` should include a matching `inn_bed`/`storage_chest`/`coach_station`
   object; if it includes `longship`, the home map's `portals` should include a matching
   `portal(kind: longship)` boarding portal (`20_schemas/map.schema.md`) — a cross-file consistency
   expectation, not enforceable from this file alone.
8. **Dialog/flavor length.** `dialog.greeting`/`idle`/`farewell` and `flavor` are each ≤2 sentences
   (mechanical linting is `docs/VALIDATION.md` §7's existing warn-only proposal, not a hard fail
   here).

## Template

```yaml
id: npc_{NNN}
schema: 20_schemas/npc.schema.md
references: [WORLD_PLAN, MAP_INTERACTABLES, ECONOMY] # add PERSISTENCE if services non-empty; add ENHANCEMENT if role: enchanter or services includes enhance; add DEATH_PENALTY if services includes inn_rest; add MAP_CONNECTIONS if role: coach_clerk/pier_officer or services includes coach/longship
name: "{Display Name}"
region: { region_slug }
map: map_{NNN}
role: { merchant|innkeeper|blacksmith|enchanter|banker|quest_giver|coach_clerk|pier_officer|guide|handler|flavor }
# shop:                          # optional
#   items: [item_{category}_{NNNN}]
# services: [ { inn_rest|storage|enhance|coach|longship } ]   # optional
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
  an explicit "smithy" only at Millbrook and an explicit "enchanter" only at Highrune Sanctum —
  Emberfoot's and Tidewatch's interior lists name neither. Whether every bind town needs an
  enhance-service NPC, and which role carries it where no smithy/enchanter interior is named, is
  unresolved; flagged for `docs/WORLD_PLAN.md`/`10_systems/ENHANCEMENT.md`'s owners.
- Millbrook's guild hall/tavern/mayor's-house and Arcane Reach's interiors — the Spirehaven inn
  (`map_246`), the *Runewake* deck (`map_247`), and the Highrune sanctum hall (`map_267`)
  (`docs/WORLD_PLAN.md` R10) — don't map cleanly onto one obvious `role` from the enum above. Phase D may
  reuse `quest_giver`/`flavor`/`guide` for these, or a future revision may add 1–2 roles within the
  ≤12 cap. Not resolved here.
- `quest_giver`'s "should appear on ≥1 quest file" expectation is a soft, cross-file-only check —
  this schema cannot enforce it from a single NPC file, and the single-source rule forbids the NPC
  file itself from carrying a quest reference. A real check needs a later reconciliation pass,
  parallel to `docs/VALIDATION.md` §5's world-graph reconciliation for maps; flagged for that doc's
  owner.
- `portrait`'s token convention (`portrait_<npc_id>`, proposed here) has no owner in `40_assets/`
  yet; flag for a future `40_assets/` doc or an `40_assets/ART_BIBLE.yaml` amendment.
- `banker` and `coach_clerk` are treated as optional — a bind town's bank and a ring town's coach
  station function per `15_maps_system/MAP_INTERACTABLES.md` as self-service objects with no NPC
  present (though `coach_clerk` is the only place the free novice pilgrimage ride is granted, so a
  town on the pilgrimage route effectively needs one). `pier_officer`, by contrast, *is* the
  longship boarding gate (`15_maps_system/MAP_CONNECTIONS.md` §8.1) — whether that boarding could
  instead be a self-service pier object (mirroring `coach_station`) is an arc-2 design call, not
  settled here.
- The `coach_clerk`/`pier_officer` roles and the `coach`/`longship` services are proposed for
  `docs/00_vision/GLOSSARY.md` promotion at the C gate with the rest of this enum (see the `role`
  note above); `coach`/`coach_stop` are already GLOSSARY Transport tokens, and the longship spawn
  tokens are flagged in `15_maps_system/MAP_CONNECTIONS.md` §2.
