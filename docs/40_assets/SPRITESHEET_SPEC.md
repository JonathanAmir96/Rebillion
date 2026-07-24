# SPRITESHEET_SPEC.md — Per-Entity Atlas Contract

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 40_assets/ART_BIBLE.yaml,
40_assets/ANIMATION_STATES.md, 40_assets/ANIMATION_TIMING.md,
30_engineering/ENGINEERING_STANDARDS.md, 20_schemas/monster.schema.md,
20_schemas/npc.schema.md, docs/ID_REGISTRY.md, docs/VALIDATION.md

Owner doc for the concrete spritesheet **contract** implementing `40_assets/ART_BIBLE.yaml`
`export_contract`: how an entity's individually-named frames pack into one atlas, the exact grid
math (dimensions, padding, extrusion), the pivot pixel, and the manifest sidecar the coding pass
reads instead of re-deriving any of it. This doc owns **shape**, not the **values** that fill some
of that shape's fields: base fps per state, haste scaling, and the `hit_frame` default/override law
are `40_assets/ANIMATION_TIMING.md`'s (cited, never restated) — this doc only fixes the field those
numbers land in. Pixel/silhouette/palette treatment and the frame-count ranges themselves stay
`40_assets/ART_BIBLE.yaml`'s, cited by key. Per-state purpose, loop/one-shot behavior, interrupt
rules, and the required-state-per-entity-class matrix stay `40_assets/ANIMATION_STATES.md`'s. This
doc satisfies `30_engineering/ENGINEERING_STANDARDS.md`'s "match SPRITE_PIPELINE/SPRITESHEET_SPEC"
pixel-rendering citation (see Open Questions on the two-name discrepancy there).

## 1. Two-stage pipeline: named frames → packed atlas

`40_assets/ART_BIBLE.yaml` `export_contract.frame_naming` (`{entity_id}_{state}_{NN}`) names one
**logical frame** — that convention does not change here. What this doc adds is the second stage:
those named frames are **packed** into one PNG per entity (the atlas), at fixed grid positions this
doc defines, and a manifest sidecar (§7) records exactly which named frame occupies which cell. A
tool/build step (owned by the eventual Phase E coding pass, not authored here — see Open Questions)
performs the packing; nothing in this doc requires an artist to hand-place cells.

## 2. Atlas contract (power-of-two, padding, extrusion)

Per `40_assets/ART_BIBLE.yaml` `export_contract.atlas`: **power-of-two per entity, 1px padding,
extrude edges.** Concretely, one atlas PNG per `entity_id` (never a shared multi-entity sheet —
`export_contract.forbidden` "mixed pixel densities in one atlas" already rules out anything looser
than one entity per sheet at a single `size_class`):

- **Cell content size** = the entity's `size_class` dimensions (`40_assets/ART_BIBLE.yaml`
  `sizing.size_classes`, cited by key, §4 below) — every cell in the sheet is the same size,
  because every animation state of a given entity renders at that entity's one `size_class`.
- **Padding** = `1px` (`export_contract.atlas`), applied as a full ring around **every** cell,
  including cells on the sheet's outer edge — no special-casing edge cells, so one formula covers
  the whole grid (§3).
- **Extrusion**: the 1px padding ring is filled by duplicating each cell's own outermost content
  pixel row/column outward (not left transparent) — the standard bleed-guard `export_contract.atlas`
  requires. This is a build-step operation, not manual per-frame authoring.
- **Sheet dimensions**: both the total packed width and height round **up** to the next power of two
  (256/512/1024/2048...) after padding is included — never down, so no cell is clipped.

### 2.1 Grid math

Let `cw, ch` = the entity's `size_class` content dimensions (`ART_BIBLE.yaml sizing.size_classes`,
always square today: `tiny 24, small 32, medium 48, large 64, boss 96`), `pad = 1`, `cols` = the
column count (§3), `rows` = the row count (§4):

```
cell_box_w = cw + 2*pad
cell_box_h = ch + 2*pad
sheet_content_w = cols * cell_box_w
sheet_content_h = rows * cell_box_h
sheet_w = next_power_of_two(sheet_content_w)
sheet_h = next_power_of_two(sheet_content_h)

# top-left pixel of a given cell's CONTENT (padding excluded) at (row, col), both 0-indexed:
content_x(row, col) = col * cell_box_w + pad
content_y(row, col) = row * cell_box_h + pad
# that cell's content rect is (content_x, content_y, cw, ch) — this is the Godot AtlasTexture.region
```

### 2.2 Column count policy

`cols` = the **largest** frame count authored across every state row this entity declares (e.g., if
`walk` is authored at 8 frames and every other row is 5 or fewer, `cols = 8`). Every row reserves
the full `cols` width even where its own state needs fewer frames — unused trailing cells stay fully
transparent and are never referenced by any `AtlasTexture` region. This trades a little unused sheet
space for a fixed invariant that matters more: **column index always equals frame index**, so no
row-specific offset math exists anywhere downstream. Given the locked frame budgets top out at 8
(`walk`, `40_assets/ART_BIBLE.yaml animation.frame_budgets`), the waste is small. See Open Questions
if a future VRAM audit wants tighter (ragged) packing instead.

### 2.3 Worked examples

**Small player, full 9-state set** (`idle, walk, jump, fall, climb, attack, cast, hit, die` —
`40_assets/ANIMATION_STATES.md` §5 player row; `size_class: small` → `cw=ch=32`): `cols=8` (walk's
locked max), `rows=9`. `cell_box = 34x34`. `sheet_content = 272x306` → `sheet = 512x512`.

**Boss, full elite/boss-class set** (`idle, walk, attack, cast, hit, die, telegraph, phase_shift,
spawn`; `size_class: boss` → `cw=ch=96`): `cols=8`, `rows=9`. `cell_box = 98x98`.
`sheet_content = 784x882` → `sheet = 1024x1024`.

In the boss example, `attack`'s row is index 2 (canonical-order position, §4); if that row's
`hit_frame` is 2 (`40_assets/ANIMATION_TIMING.md` default formula for a 5-frame clip), its content
rect is `content_x = 2*98+1 = 197`, `content_y = 2*98+1 = 197`, size `96x96`.

## 3. Row layout: canonical order, filtered to the entity's declared set

Rows follow the **12-token canonical order** fixed by `40_assets/ANIMATION_STATES.md` §1 — `idle,
walk, jump, fall, climb, attack, cast, hit, die, telegraph, phase_shift, spawn` — **filtered down**
to exactly the states this entity declares (its `animation_states` field, `20_schemas/monster.schema.md`;
the equivalent player/NPC list per `40_assets/ANIMATION_STATES.md` §5). Row 0 is therefore the
*earliest-in-canonical-order* state the entity actually has, not necessarily `idle` for every class
(every entity class's required set happens to start with `idle` per §5 there, but an entity may
authors extra optional states from the same doc's "floor, not ceiling" allowance, §5 there, which
does not change this row-assignment rule).

Because row index is entity-specific (two entities with different declared sets do **not** share row
meaning), the manifest's `states.<token>.row` field (§7) is the single source of truth — nothing may
infer a row from a state name or from another entity's layout.

## 4. Frame cells at size_class dimensions

Cell **content** size is exactly the entity's `size_class` value from `40_assets/ART_BIBLE.yaml`
`sizing.size_classes` — this doc does not restate those five pixel pairs, only points at the key.
Padding (§2) sits **outside** that content box; the content box itself is never resized, letterboxed,
or padded internally — a `medium` entity's every cell is exactly `48x48` content pixels, full stop.

## 5. Pivot: feet-center, exact pixel per asset

`40_assets/ART_BIBLE.yaml` `sizing.pivot: feet-center` and `export_contract.pivot_export`
("feet-center; document exact pixel per asset") are the rule; this section is that documentation.
Because pivot is a pure function of `size_class` (every asset in a class shares identical cell
dimensions), the exact pixel is fixed and enumerable:

| `size_class` | Content `(w, h)` | Pivot, content-local `(x, y)` |
|---|---|---|
| `tiny` | 24, 24 | 12, 24 |
| `small` | 32, 32 | 16, 32 |
| `medium` | 48, 48 | 24, 48 |
| `large` | 64, 64 | 32, 64 |
| `boss` | 96, 96 | 48, 96 |

Formula: `pivot = (cw/2, ch)` — horizontal center, vertical **at the content box's bottom edge**
(the feet-ground contact line), never `ch-1`, since the pivot is a boundary between the sprite and
the ground plane, not a sampled pixel. **Pivot is content-local** — it is expressed against the
`cw x ch` content box (§4), never against the padded `cell_box` (§2), because the `AtlasTexture`
region Godot reads already excludes padding (§2.1); padding is purely an export/extrusion safety
margin and never enters pivot or gameplay math.

Every asset's manifest (§7) states its own `pivot.content_px` explicitly (copied from this table per
its `size_class`) rather than leaving the pivot as an implicit convention a downstream tool must
recompute — satisfying "document exact pixel per asset" literally, per-file.

### 5.1 Engine wiring note

All frames of one entity share one `size_class`, so one pivot serves every frame of every state —
no per-frame pivot variation exists. In Godot 4's `AnimatedSprite2D`: `centered = true`,
`offset = Vector2(0, -ch/2)` places the node's local origin at the content box's bottom-center
(derivation: default centered draws the texture's geometric center at the origin; shifting the draw
by `-ch/2` on Y moves the origin to the bottom edge instead). E.g. `medium` → `offset = (0, -24)`.
This is a design-level implementation note for the Phase E coding pass, not new pixel-rendering law —
`30_engineering/ENGINEERING_STANDARDS.md`'s pixel-rendering rules (nearest filter, no mipmaps, pixel
snapping) are unchanged and cited, not restated (§8).

## 6. Frame naming

Every packed cell corresponds to exactly one `40_assets/ART_BIBLE.yaml` `export_contract.frame_naming`
identity, verbatim: `{entity_id}_{state}_{NN}` (`NN` = 2-digit, zero-based, per that key). `{state}`
is always one of the 12 exact `40_assets/ANIMATION_STATES.md` §1 tokens; `{entity_id}` is `mob_NNN`
or `npc_NNN` (`docs/ID_REGISTRY.md`) for monsters/NPCs. The player has no registered `entity_id`
today (see Open Questions, inherited from `40_assets/ANIMATION_STATES.md`'s own flag) — examples
below use the placeholder literal `player`, which is illustrative only, not a minted ID. This naming
identifies a frame whether it is still a loose exported PNG (pre-packing) or a cell inside the packed
atlas (post-packing, §1); the manifest (§7) is what maps a given name to its packed cell.

## 7. Atlas manifest sidecar

One manifest file per entity, `<entity_id>.atlas.yaml`, living beside `<entity_id>.png` (§8 folder
layout). It follows the tree's usual content front-matter convention (`id`, `schema`, `references`)
so it validates the same way other content files do; its `id` reuses the owning entity's own `id` —
no new `docs/ID_REGISTRY.md` block is needed, since this is a sidecar to an already-registered
entity, not a new registrable content type.

### 7.1 Shape

```yaml
id: mob_010                        # = the owning entity's id (mob_NNN | npc_NNN | player-placeholder)
schema: 40_assets/SPRITESHEET_SPEC.md
references: [ART_BIBLE, ANIMATION_STATES, ANIMATION_TIMING]
size_class: large                  # 40_assets/ART_BIBLE.yaml sizing.size_classes key
sheet:
  file: mob_010.png
  dimensions_px: [1024, 512]        # power-of-two, padding included (§2.1)
  cell_content_px: [64, 64]         # = size_class dims (§4)
  padding_px: 1
  extruded: true
  cols: 8                           # §2.2 — max frame_count across this entity's declared states
pivot:
  mode: feet-center                 # ART_BIBLE.yaml sizing.pivot
  content_px: [32, 64]              # §5 table value for this size_class — exact, per-asset
states:                             # keys: subset of the 12 canonical tokens this entity declares
  idle:     { row: 0, frame_count: 3, fps_ref: idle }
  walk:     { row: 1, frame_count: 6, fps_ref: walk }
  attack:   { row: 2, frame_count: 5, fps_ref: attack, hit_frame: 2 }
  telegraph:{ row: 3, frame_count: 3, fps_ref: telegraph }
  hit:      { row: 4, frame_count: 3, fps_ref: hit }
  die:      { row: 5, frame_count: 5, fps_ref: die }
  spawn:    { row: 6, frame_count: 4, fps_ref: spawn }
```

### 7.2 Field notes

- **`states.<token>.row`** — authoritative row index for this entity (§3); never inferred.
- **`states.<token>.frame_count`** — the number of frames this asset actually authors, inside the
  `[min,max]` budget `40_assets/ART_BIBLE.yaml animation.frame_budgets` (9 locked states) or
  `40_assets/ANIMATION_STATES.md` §2.2 (3 proposed states) owns. `cols` (§2.2) is the max of these
  across all declared states, not this field.
- **`states.<token>.fps_ref`** — a pointer into `40_assets/ANIMATION_TIMING.md`'s base-fps-per-state
  table, not a restated number (`ENGINEERING_STANDARDS.md` rule 6, no magic numbers). Today
  `fps_ref` always equals the state token itself (a flat one-fps-per-state law, `ANIMATION_TIMING`
  §1) — it stays a separate explicit key rather than an implicit same-name lookup so a future
  tier-specific fps split does not require an atlas-manifest schema change.
- **`states.attack.hit_frame` / `states.cast.hit_frame`** — present **only** on `attack`/`cast` rows
  (never `telegraph`/other one-shots); the exact 0-indexed frame that fires the combat hit signal.
  Value and default-formula law belong to `40_assets/ANIMATION_TIMING.md`; this field is where Phase
  D writes whatever that law (or an authored override) resolves to. `docs/VALIDATION.md` §6 does not
  yet check this field's presence — see Open Questions.
- Every `states` key must be one of the 12 `40_assets/ANIMATION_STATES.md` tokens and must match an
  entry in this entity's own `animation_states` field (`20_schemas/monster.schema.md` /
  `20_schemas/npc.schema.md` once that schema gains the field, see that doc's own Open Questions) —
  the manifest and the content file's declared state list are two views of the same set and must
  agree; a mismatch is a referential-integrity gap this doc flags for `docs/VALIDATION.md` (Open
  Questions) rather than resolves itself.

## 8. Godot import preset

Cites `40_assets/ART_BIBLE.yaml` `export_contract.godot_import`
(`texture_filter: Nearest, mipmaps: false, fix_alpha_border: true`) and
`30_engineering/ENGINEERING_STANDARDS.md`'s matching pixel-rendering line; neither is restated as new
law here, only bound to a concrete `.import` preset every entity atlas PNG uses, so no file needs
manual per-asset toggling (data-driven, `ENGINEERING_STANDARDS.md` prime directive 1):

| Setting | Value | Source |
|---|---|---|
| Filter | Off / Nearest | `godot_import.texture_filter` |
| Mipmaps | Off | `godot_import.mipmaps` |
| Fix Alpha Border | On | `godot_import.fix_alpha_border` |
| Repeat | Disabled | atlas cells must never wrap/tile |
| Compress Mode | Lossless | preserves exact palette colors — `export_contract.forbidden` "AA downsampling on export" rules out any lossy VRAM-compressed path |

Applied as one named Godot Import Preset (e.g. `pixel_art_entity_atlas`) over the whole
`assets/characters/` subtree (§9), rather than per-file settings, so every new entity atlas inherits
it automatically.

## 9. Folder layout under `assets/`

`30_engineering/ENGINEERING_STANDARDS.md`'s project structure names a top-level `assets/` node;
`40_assets/ART_BIBLE.yaml` `meta.applies_to` lists eight asset categories
(`characters, monsters, npcs, tilesets, props, projectiles, fx, ui`). This doc's per-state-row grid
contract is specifically for **animated entities** — the classes `40_assets/ANIMATION_STATES.md` §5
defines (player, monster tiers, summon, npc) — not for tiles/props/projectiles/fx/ui, whose atlas
shapes (if any) are a different, not-yet-authored contract (Open Questions).

**Player exception (composited entity):** the player is never one baked sheet — it renders as
a layer stack per `40_assets/CHARACTER_COMPOSITING.md`, and **each part** (base body, hair,
face, visible-equip visual) is packed as its own entity under this doc's full contract, with
the part's ID (`style_*` / `item_equip_NNNN`) standing in the `{entity_id}` position. That doc
also owns the two manifest extensions its parts carry (`anchors` on the base body, `origin_px`
on anchored parts); everything else in §1–§8 applies to player parts unchanged.

```
assets/
  characters/
    player/
      <layer>/<part_id>/         # composited parts — see 40_assets/CHARACTER_COMPOSITING.md §6
        <part_id>.png
        <part_id>.atlas.yaml
    monsters/
      mob_NNN/
        mob_NNN.png
        mob_NNN.atlas.yaml
    npcs/
      npc_NNN/
        npc_NNN.png
        npc_NNN.atlas.yaml
  tilesets/     # out of this doc's scope — 40_assets/ART_BIBLE.yaml environment.tile_grid_px
  props/        # out of this doc's scope
  projectiles/  # out of this doc's scope
  fx/           # out of this doc's scope
  ui/           # out of this doc's scope — 40_assets/UI_ART_SPEC.md owns 9-slice/icon grids
```

One folder per `mob_NNN`/`npc_NNN` (rather than a flat `monsters/mob_010.png` alongside
`mob_010.atlas.yaml`) keeps a future multi-file per-entity asset (e.g., a distinct portrait, per
`20_schemas/npc.schema.md` `portrait` field) colocated without renaming the sheet itself.

## Open Questions

- **`ENGINEERING_STANDARDS.md`'s "SPRITE_PIPELINE/SPRITESHEET_SPEC" citation names two docs.**
  Only this file exists in the tree; whether `SPRITE_PIPELINE` is an alternate/legacy name for this
  same doc, or a distinct, not-yet-authored companion (e.g., the frames→atlas build tooling of §1,
  as opposed to this doc's static contract), is unconfirmed. This doc treats itself as satisfying
  that citation; flagged for `ENGINEERING_STANDARDS.md`'s owner to reconcile the name.
- **Player has no registered `entity_id`.** Inherits `40_assets/ANIMATION_STATES.md`'s own flagged
  gap (no ID prefix, no `player.schema.md`). This doc's `player/` folder and manifest `id` use the
  placeholder literal `player` illustratively only; the real convention (a minted prefix, or the
  job-line tokens doubling as `entity_id`) is that doc's open question, not resolved here.
- **Telegraph/phase_shift/spawn budgets are still proposed, not blessed.** `40_assets/ANIMATION_STATES.md`
  §2.2's three frame-count ranges are pending Agent-3 sign-off into `40_assets/ART_BIBLE.yaml`
  `amendments[]`. This doc's worked examples (§2.3) using those states' frame counts will need
  recomputing if the blessed numbers differ from the proposal.
- **Column-count policy is this doc's own simplicity call.** §2.2's full-width-rows decision (versus
  tighter ragged packing) trades sheet footprint for a fixed column-equals-frame-index invariant.
  Flag if a future texture-memory budget pass wants the tighter layout instead.
- **Per-ability clip granularity does not exist yet.** `20_schemas/monster.schema.md` `abilities[]`
  rows carry no clip id of their own — every elite/boss ability that plays through `cast` (or
  `attack`) shares that one state row's `hit_frame`/frame count in this doc's manifest. Whether a
  future per-ability animation-id layer (parallel to the still-unauthored
  `40_assets/SKILL_ANIMATION.md` for player skills, flagged by both `20_schemas/skill.schema.md` and
  `40_assets/ANIMATION_STATES.md`) is needed for monster kits is not resolved here.
- **`docs/VALIDATION.md` has no check for this manifest.** §6 there validates an entity's
  `animation_states` field and skill `animation` ID naming, but nothing yet checks the atlas
  manifest sidecar itself (power-of-two dimensions, `hit_frame` present on every `attack`/`cast` row,
  `states` keys agreeing with the entity's own `animation_states` list). Flagged for
  `docs/VALIDATION.md`'s owner to extend §6 (or add a check) once this contract is in active use.
- **Packing tool ownership is unassigned.** Whether the frames→atlas build step (§1) is a Phase D
  content-authoring tool or a Phase E coding-pass utility is not settled by any doc read for this
  task; flagged for `60_agents/` scoping.
