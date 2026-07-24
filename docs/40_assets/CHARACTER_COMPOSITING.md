# CHARACTER_COMPOSITING.md — Layered Player Sprite Contract (Paper-Doll Model)

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 40_assets/ART_BIBLE.yaml,
40_assets/ANIMATION_STATES.md, 40_assets/ANIMATION_TIMING.md, 40_assets/SPRITESHEET_SPEC.md,
10_systems/ITEMS.md, 10_systems/JOBS.md, 10_systems/PERSISTENCE.md,
30_engineering/ENGINEERING_STANDARDS.md, docs/ID_REGISTRY.md, docs/VALIDATION.md

Owner doc for the **composited player sprite**: the player character is never one baked
spritesheet — it is a fixed-order stack of independently authored **part layers** (base body,
face, hair, and the visible equipment slots) composited at runtime, in the tradition of
classic side-scrolling MMOs. Authorized by owner directive 2026-07-24 (recorded as a scope
amendment in `00_vision/SCOPE.md`): players customize appearance at character creation
(hair style, face, hair color, skin tone) and every worn equip changes the visible sprite —
while **art generation cost stays linear in the number of parts, not the product of their
combinations** (§9). This doc owns the layer registry and z-order, the part classes and their
alignment/anchor law, the palette-swap channels, the per-part export contract, and the style
catalog shape. It does **not** own: equipment slots/stat rules (`10_systems/ITEMS.md`), the 12
animation-state tokens and per-state behavior (`40_assets/ANIMATION_STATES.md`), fps/hit-frame
timing (`40_assets/ANIMATION_TIMING.md`), the atlas grid math (`40_assets/SPRITESHEET_SPEC.md`,
applied here per part), or pixel/palette/shading law (`40_assets/ART_BIBLE.yaml`, locked —
everything here inherits it unchanged).

## 1. Compositing law

- **One skeleton, many skins.** Every part is authored against the **single canonical pose
  set** of the base body (`style_base_00`, §2): same `size_class: small` 32x32 content box
  (`40_assets/ART_BIBLE.yaml` `sizing.player_frame`), same feet-center pivot
  (`SPRITESHEET_SPEC.md` §5), same 9 player states and per-state frame counts
  (`ANIMATION_STATES.md` §5 player row), same frame indices. Layer N frame `walk_03` is
  drawn directly over layer M frame `walk_03` with **zero per-part offset math** — alignment
  is an authoring invariant, not a runtime correction. A part that cannot hold the base
  body's silhouette/pose at a given frame is an invalid part, full stop.
- **The composite is cosmetic only.** Layers never change hitboxes, movement, or timing —
  the state machine, physics, and hit-frames run on the base body's clip data alone
  (`ANIMATION_TIMING.md`); layers are a pure render stack on top.
- **Every ART_BIBLE rule applies per layer and to the final composite**: selective outline,
  1-dominant-ramp-plus-accent usage, silhouette readability. Because parts combine freely,
  each part must also read cleanly against any other legal part — the readability check runs
  on the composite, worst case (darkest skin + darkest outfit), not on isolated parts.
- **Facing** is a horizontal flip of the whole stack, never per-layer. Anchor X mirrors as
  `cw - x` (content-local, `cw = 32`); no part authors separate left/right art.

## 2. Layer registry and z-order

Ten layers, fixed back-to-front order. Layer tokens are GLOSSARY law ("Player sprite
layers"); the seven visible equipment layers **reuse the `10_systems/ITEMS.md` slot tokens
verbatim** — no parallel naming. `ring`/`amulet` render no layer (invisible slots).

| z | Layer token | Part source | Part class (§3) |
|---|---|---|---|
| 0 | `cape` | `cape`-slot equip (`item_equip_NNNN`) | anchored (`torso_px`) |
| 1 | `base` | `style_base_00` + `style_skin_NN` swatch (§5) | animated (the reference skeleton) |
| 2 | `boots` | `boots`-slot equip | animated |
| 3 | `legs` | `legs`-slot equip | animated |
| 4 | `body` | `body`-slot equip | animated |
| 5 | `gloves` | `gloves`-slot equip | animated |
| 6 | `face` | `style_face_NN` (character creation) | anchored (`head_px`) |
| 7 | `hair` | `style_hair_NN` + `style_haircolor_NN` swatch (§5) | anchored (`head_px`) |
| 8 | `head` | `head`-slot equip (hats/helms) | anchored (`head_px`) |
| 9 | `weapon` | `weapon`-slot equip | anchored (`grip_px` + `grip_pose`, §4.2) |

- The base body includes simple neutral undergarb drawn within palette — an empty `body`/
  `legs`/`boots`/`gloves` slot exposes the base layer, never a gap.
- A `head` equip may declare `hides: [hair]` (full helms) and a `body` equip may declare
  `covers: [legs]` (a robe/overall look — the classic single-piece outfit): every layer named
  in `hides`/`covers` is skipped from the stack while that item is worn. `covers` on a `body`
  item means Phase D authors **one** animated part spanning torso-to-ankle instead of a
  matched pair; the item still occupies only its own slot (`10_systems/ITEMS.md` slot rules
  unchanged — this is a visual field, not an equip rule).
- This fixed global z-order is deliberately state-independent (no per-frame z-map) — one
  invariant, no downstream reorder tables. If a specific clip proves to need a weapon-behind-
  body frame, that is an Open Question, not a silent exception.

## 3. Part classes: animated vs. anchored

The token economy (§9) rests on this split:

- **Animated parts** (`base`, `body`, `legs`, `boots`, `gloves`): clothing deforms with limbs,
  so these author a **full frame set** — every state row and frame count exactly matching the
  base body. Expensive; kept to the five layers where per-frame art is unavoidable.
- **Anchored parts** (`cape`, `face`, `hair`, `head`, `weapon`): rigid or near-rigid shapes
  that move with a body point but do not deform per frame. Each authors **1–3 single-frame
  images total** (§3.1); the base body's anchor map (§4) places the image per frame. This is
  what makes a new hair style ~2 generated images instead of ~34.

### 3.1 Anchored-part variant rows and the fallback law

An anchored part's atlas holds 1-frame state rows only, and only for the states below;
**any state without its own row falls back to the part's `idle_00` image**, positioned by
that frame's anchor. Variants stay inside the 12-token naming contract (§6) — a "variant"
IS a 1-frame state row, never a new token:

| Layer | Required rows | Optional rows | Notes |
|---|---|---|---|
| `face` | `idle` (neutral) | `hit` (flinch expression), `die` | hidden during `climb` (§4.1); the mouth/eyes are part of the face image — at 32px there is no separate mouth layer (a mouth is 1–3 px; see Open Questions) |
| `hair` | `idle` (front view), `climb` (back view) | — | `climb` shows the character's back (§4.1) |
| `head` | `idle` (front), `climb` (back) | — | same back-view rule as `hair` |
| `cape` | `idle` | `walk` (flowing variant) | drawn behind everything; back view during `climb` is the cape's `idle` image unchanged |
| `weapon` | `idle` (rest), `jump` (raised), `attack` (strike) | — | which of the three rows renders on a given frame is the anchor map's `grip_pose` call (§4.2); hidden during `climb` (`15_maps_system/MAP_TRAVERSAL.md` §4 already disables attacking there) |

## 4. The anchor map (base-body manifest extension)

The base body's atlas manifest (`style_base_00.atlas.yaml`, shape per `SPRITESHEET_SPEC.md`
§7) gains one block this doc owns — `anchors` — giving, **per state, per frame**, the
content-local pixel each anchored layer attaches to:

```yaml
# appended to the SPRITESHEET_SPEC §7.1 manifest shape; content-local px, [x, y] per frame
anchors:
  idle:
    head_px:  [[16, 9], [16, 10], [16, 9]]        # one entry per authored frame
    torso_px: [[16, 17], [16, 18], [16, 17]]
    grip_px:  [[21, 20], [21, 21], [21, 20]]
    grip_pose: [idle, idle, idle]                  # weapon row sampled per frame (§3.1)
  walk:
    head_px:  [[16, 10], [16, 9], ...]
    ...
  attack:
    grip_pose: [jump, jump, attack, attack, idle]  # raise → strike at the hit-frame → rest
    ...
```

- `head_px` positions `face`, `hair`, `head`; `torso_px` positions `cape`; `grip_px` +
  `grip_pose` position and select the `weapon` image.
- Each anchored part's own sidecar (§6) declares its `origin_px` — the pixel **in the part
  image** that lands on the anchor. Placement is `anchor - origin`, integer math only
  (`ART_BIBLE.yaml` `no_sub_pixel`).
- Anchors are authored once, on the one base body, by inspecting its frames — a few dozen
  coordinate pairs, zero generated art. Mirroring under facing-flip is §1's `cw - x` rule.
- `grip_pose` rows appear only on states where the weapon is visible; `hit_frame` alignment
  law: on `attack`/`cast`, the frame `ANIMATION_TIMING.md` fixes as the hit-frame must carry
  `grip_pose: attack` — the strike image and the damage signal land on the same frame.

### 4.1 Climb (back view)

`climb` is the one state showing the character's back: the base body authors its climb frames
back-on, `face` is skipped entirely, `hair`/`head` sample their `climb` (back-view) row, and
`weapon` is hidden. No other state changes viewpoint.

## 5. Palette-swap channels (free variety)

Two channels multiply looks at **zero** generation cost, applied as indexed-color ramp remaps
at import time (build step), never as HSV shifts at runtime (`ART_BIBLE.yaml` forbids
off-palette colors; a remap between authored ramps cannot leave palette):

- **`style_skin_NN`** — remaps the base body's skin ramp. The authored base uses one
  canonical skin ramp; each swatch entry names the replacement ramp.
- **`style_haircolor_NN`** — remaps the hair part's ramp the same way; every `style_hair_NN`
  is authored once in the canonical ramp and shipped in all swatches.

Constraint flag: `ART_BIBLE.yaml` `palette.ramps` (locked) contains no dedicated skin-tone
ramps, and hair colors beyond the five existing ramps + neutrals would be off-palette. A
proposed amendment (skin-tone ramp set + hair-color swatch list) is flagged for Agent-3 in
Open Questions — swatch **counts** are reserved in `docs/ID_REGISTRY.md` now, but no swatch
color values are canon until that amendment lands.

## 6. Per-part export contract

Every part — animated or anchored — is exported and packed **exactly as one
`SPRITESHEET_SPEC.md` entity**: same PNG/atlas/padding/pivot/import-preset law, same
`{entity_id}_{state}_{NN}` frame naming (`ART_BIBLE.yaml` `export_contract.frame_naming`),
with the **part ID standing in the `{entity_id}` position**:

- Appearance parts: `style_base_00`, `style_hair_NN`, `style_face_NN`
  (`docs/ID_REGISTRY.md` "Appearance styles" block). Swatch entries (`style_skin_NN`,
  `style_haircolor_NN`) are **data-only** — they name ramp remaps and never own art files.
- Equipment visuals: the item's own `item_equip_NNNN` — a worn item's sprite part needs no
  second ID. Example frames: `item_equip_0043_walk_05` (an animated `body` piece),
  `style_hair_03_climb_00` (a hair back view).

Anchored parts add one sidecar field in their `.atlas.yaml` (legal under §7's shape as an
extension this doc owns, like `anchors`): `origin_px: [x, y]` (§4). Folder layout extends
`SPRITESHEET_SPEC.md` §9's `characters/player/` node:

```
assets/characters/player/
  base/style_base_00/            # style_base_00.png + style_base_00.atlas.yaml (+ anchors)
  hair/style_hair_NN/
  face/style_face_NN/
  equip/item_equip_NNNN/         # visible-slot items only; one folder per item
```

This resolves the export-naming half of the "player has no `entity_id`" open question
(`ANIMATION_STATES.md`, `SPRITESHEET_SPEC.md`): player frames are named by **part** IDs, and
no monolithic player sheet exists to need an ID. The player-schema half stays open (§ Open
Questions). Job lines share the one base body — job identity is worn equipment + weapon
(`10_systems/ITEMS.md` §3), not a per-line body.

## 7. Character creation choices

At creation the player picks exactly: `style_hair_NN`, `style_face_NN`, `style_haircolor_NN`,
`style_skin_NN` (base body is fixed at `style_base_00` this arc). Choices persist on the
character record (server-authoritative, `10_systems/PERSISTENCE.md`; field addition flagged
in Open Questions) and are freely re-stylable later only through systems a future doc may add
— nothing in this run sells or drops appearance (`00_vision/SCOPE.md`: no vanity shop, no
monetization).

## 8. Style catalog (content file shape)

One Phase D content file, `50_content/styles/style_catalog.yaml`, values-only per tree law:

```yaml
id: style_catalog
schema: 40_assets/CHARACTER_COMPOSITING.md
references: [ART_BIBLE, ITEMS, ID_REGISTRY]
entries:
  - id: style_hair_01
    layer: hair
    name: "Millbrook Crop"
  - id: style_haircolor_00
    layer: hair            # swatch entries carry the layer they remap
    ramp: TBD              # ART_BIBLE amendment pending (§5) — no color values until then
  - id: style_skin_00
    layer: base
    ramp: TBD
  - id: style_face_01
    layer: face
    name: "Steady Gaze"
```

Equip visuals need no catalog entry — `20_schemas/item.schema.md` gains the optional visual
fields (`covers`, `hides`, §2) via that schema's own channel (Open Questions).

## 9. Generation strategy and the token economy (PixelLab)

The point of this whole contract. Naive per-look generation is the product of every choice;
composited generation is the **sum of parts**, and palette swaps multiply looks for free.
Frame math uses the player's 9 states at mid-budget ≈ 34 frames/full set
(`ANIMATION_STATES.md` §2). Illustrative first-arc wardrobe (authored counts per
`docs/ID_REGISTRY.md` reservations; Phase D may adjust):

| Generated asset | Count | Frames each | Frames total |
|---|---|---|---|
| Base body (full set, canonical skin) | 1 | ~34 | ~34 |
| Animated equip visuals (`body`/`legs`/`boots`/`gloves` pieces, 4 slots x 6 tiers) | 24 | ~34 | ~816 |
| Hats (`head` slot, 6 tiers, front + back) | 6 | 2 | 12 |
| Weapons (4 lines x 6 tiers, 3 poses) | 24 | 3 | 72 |
| Hair styles (front + back) | 12 | 2 | 24 |
| Faces (neutral + hit) | 8 | 2 | 16 |
| Skin / hair-color swatches | 5 + 6 | 0 (remap) | 0 |
| **Total generated** | | | **~974** |

Distinct player looks covered: 12 hair x 6 hair colors x 8 faces x 5 skins x the full
mix-and-match wardrobe ≈ **10⁵–10⁶ composites from under 1,000 generated frames**; baking
each look as its own sheet would cost ~34 frames **per look** — three to four orders of
magnitude more. Every future addition stays linear: one new hair = 2 frames, one new outfit
= ~34–68, one new color = 0.

Generation order (Phase D → art pass): base body first (it defines the skeleton and anchor
map every other part is authored against); then per-part generation feeds the base body's
frames as the pose reference with `ART_BIBLE.yaml` `pixellab_defaults` plus a
transparent-background, "part only, no body" instruction — the part inject list stays inside
`per_asset_injects_only`. Anchored parts generate as single stills (cheapest); animated
equips reuse the base body's animation via pose-guided per-frame generation rather than
free generation per frame.

## 10. Engine wiring note (design-level, Phase E)

One parent player node drives the state machine and clip timing from the base body's manifest;
each layer is a child sprite sharing the parent's flip and frame index — animated parts sample
their own atlas at the same `(state, frame)`, anchored parts apply §4 placement. Ramp remaps
bake per-swatch textures at import (a handful of small PNGs) rather than a runtime palette
shader — simplest thing that satisfies `30_engineering/ENGINEERING_STANDARDS.md` pixel
rules; the coding pass may substitute a shader with identical output. Not new rendering law —
nearest/no-mipmap/pixel-snap all inherit unchanged.

## Open Questions

- **Skin/hair swatch ramps need an ART_BIBLE amendment (Agent-3).** `palette.ramps` (locked)
  has no skin-tone ramps and no hair-color set; §5's swatch channels reserve counts only.
  Proposed: one 4-step skin ramp family (~5 tones) and ~6 hair swatches derived from existing
  ramp values where possible. No swatch is canon until an `amendments[]` entry lands.
- **`20_schemas/item.schema.md` needs the visual fields.** `covers`/`hides` (§2) and an
  implicit "this equip has a sprite part" marker are not in the item schema today; flagged
  for that schema's owner. Until then, Phase D equip content must not author these fields.
- **Player schema half of the `entity_id` question stays open.** §6 settles export naming
  (part IDs), but whether a `player.schema.md` / character-record schema should exist — and
  where appearance fields (§7) land in `10_systems/PERSISTENCE.md`'s character record — is
  still the cross-doc question `ANIMATION_STATES.md` flagged; not resolved here.
- **Validator extensions.** `docs/VALIDATION.md` has no checks yet for: `style_*` IDs in
  registry range (check 4 should cover once the block exists — confirm), anchor-map presence/
  arity on the base-body manifest (one `[x,y]` per authored frame), anchored-part rows drawn
  only from §3.1's tables, and catalog `layer` values from the GLOSSARY layer list. Flagged
  for the VALIDATION owner.
- **Fixed z-order vs. per-frame z-map.** §2 deliberately rejects MapleStory-style per-frame
  z-maps for one global order. If a clip needs weapon-behind-body (e.g., a sheathe pose in a
  future arc), revisit with a per-state override field rather than a full z-map.
- **Separate mouth layer rejected at 32px — revisit only with portraits.** The user-facing
  wish "choose a mouth" is served by face styles at sprite scale; if a future arc adds large
  portrait art (`npc.schema.md` `portrait` precedent), mouth/eye sub-layers belong to that
  portrait spec, not this sprite stack.
- **Character-creation screen UI.** `40_assets/UI_ART_SPEC.md` is locked; the creation
  screen's layout/widgets go through its amendment channel, not this doc.
- **Cape motion.** Cape as anchored-with-optional-`walk`-variant (§3.1) is a first-pass
  economy call; if capes read as stiff in playtest, promote `cape` to an animated part (costs
  ~34 frames per cape) — a per-part class change, no contract change.
