# CHARACTER_COMPOSITION.md — Player Paper-Doll: Layers, Canonical Rig & Equip Appearance

References: 00_vision/GLOSSARY.md, 00_vision/SCOPE.md, 00_vision/PILLARS.md,
40_assets/ART_BIBLE.yaml, 40_assets/ANIMATION_STATES.md, 40_assets/ANIMATION_TIMING.md,
40_assets/SPRITESHEET_SPEC.md, 40_assets/SKILL_ANIMATION.md, 10_systems/ITEMS.md,
10_systems/HUD.md, 10_systems/PERSISTENCE.md, 20_schemas/item.schema.md,
30_engineering/ENGINEERING_STANDARDS.md, docs/ID_REGISTRY.md, docs/VALIDATION.md

Owner doc for **how the player character is drawn**: the layered paper-doll model, the canonical
player rig every layer conforms to, which equipment slots are visible on the character, the
creation-time identity layers, and the `pc_<layer>_NNN` export identity that resolves the
"player has no `entity_id`" gap `40_assets/ANIMATION_STATES.md` and `40_assets/SPRITESHEET_SPEC.md`
both flagged. Character customization in this game is **equipment-driven plus creation-time
identity** — `00_vision/SCOPE.md` excludes "character cosmetics *beyond equipment*", so what you
wear *is* what you look like; this doc makes that renderable. It does **not** own: equipment
slots/stats (`10_systems/ITEMS.md`), the 12 states or their budgets
(`40_assets/ANIMATION_STATES.md`, `40_assets/ART_BIBLE.yaml`), atlas grid math
(`40_assets/SPRITESHEET_SPEC.md`), timing (`40_assets/ANIMATION_TIMING.md`), or skill visuals
(`40_assets/SKILL_ANIMATION.md`). Cited, never restated.

## 1. The model: one rig, many synchronized layers

The player has **no single spritesheet**. On screen, a character is a stack of independent sprite
layers — base body, face, hair, and one layer per visible equipment slot — composited in a fixed
draw order (§4), all driven by **one** animation state machine. Every layer is authored on the
same canonical rig (§3): identical states, identical frame counts, identical pivot. The compositor
only ever sets one (state, frame) pair and every layer shows its matching cell — layers can never
desync, by construction.

Why this shape:

- **Customization without combinatorics.** ~86 equips (`00_vision/SCOPE.md`) across 7 visible
  slots would need an impossible number of pre-baked sheets; layers make every combination free.
- **Skills stay decoupled** — every layer plays the one shared `cast` clip and skill identity
  lives in the FX overlay (`40_assets/SKILL_ANIMATION.md` §1/§4), so no equip ever needs a
  per-skill clip.
- **Server-cheap.** Another player's appearance is pure data — identity choices + equipped item
  ids (already server-authoritative, `10_systems/PERSISTENCE.md`); the client composes the look
  locally from the same content files.

## 2. Layer registry

Ten layers. Three are **identity layers** (chosen at character creation, immutable in the interim
build — see Open Questions); seven are **equipment layers**, one per visible slot
(`10_systems/ITEMS.md` §2 slots). `ring` and `amulet` have **no layer** — they are icon/tooltip
items only, never drawn on the character.

| Layer token | Kind | Sheet source |
|---|---|---|
| `base` | identity | Creation choice: body + head skin (skin tone = palette variant, §5) |
| `face` | identity | Creation choice |
| `hair` | identity | Creation choice (style sheet × color variant, §5) |
| `weapon` | equipment | Equipped `weapon` item's `appearance` (§6) |
| `head` | equipment | Equipped `head` item's `appearance` |
| `body` | equipment | Equipped `body` item's `appearance` |
| `legs` | equipment | Equipped `legs` item's `appearance` |
| `boots` | equipment | Equipped `boots` item's `appearance` |
| `gloves` | equipment | Equipped `gloves` item's `appearance` |
| `cape` | equipment | Equipped `cape` item's `appearance` |

An empty equipment slot simply contributes no layer (the `base` layer is a fully-dressed-enough
default — simple novice underclothes are part of the base sheet, so an unequipped character is
never a problem to render or to rate).

## 3. The canonical player rig

All layers conform to one rig: the **player required-state set** (`40_assets/ANIMATION_STATES.md`
§5 player row — the 9 `40_assets/ART_BIBLE.yaml`-locked states) at **fixed frame counts** chosen
once here, inside the locked budgets, so every layer's sheet is cell-for-cell congruent:

| State | Rig frame count | Locked budget (cited) |
|---|---|---|
| `idle` | 3 | [2,4] |
| `walk` | 6 | [6,8] |
| `jump` | 2 | [1,2] |
| `fall` | 2 | [1,2] |
| `climb` | 3 | [2,4] |
| `attack` | 5 | [4,6] |
| `cast` | 5 | [4,6] |
| `hit` | 2 | [2,3] |
| `die` | 5 | [4,6] |

- **These counts are law for every `pc_*` sheet** — a layer may not author more or fewer frames in
  any state (this is the whole trick; `docs/VALIDATION.md` §6 enforces it once `pc_*` sheets land).
- `hit_frame` for `attack`/`cast` = **2**, the `40_assets/ANIMATION_TIMING.md` §3.1 default for a
  5-frame clip, written into each manifest per that doc's law.
- Size class is `small` (32×32) — `40_assets/ART_BIBLE.yaml` `sizing.player_frame`, pivot per
  `40_assets/SPRITESHEET_SPEC.md` §5 (16, 32).
- Atlas math per `40_assets/SPRITESHEET_SPEC.md` §2 with this rig: `cols = 6` (walk), `rows = 9`,
  `cell_box = 34×34` → `sheet_content = 204×306` → **`sheet = 256×512` per layer**.
- **One shared action set.** The rig has exactly one `attack` and one `cast` clip — there are
  **no per-`weapon_type` stance variants** in this pass. The weapon layer's own frames plus the
  skill FX overlay (`40_assets/SKILL_ANIMATION.md` §3) carry the blade/bow/staff/dirk read; the
  body swings the same way for all four. This keeps every armor sheet at 9 rows instead of
  9 + 4×2 and is the single biggest cost-control decision in this doc — per-weapon stances are
  flagged as a future enhancement (Open Questions).

## 4. Draw order & head-slot rule

Back → front, fixed:

```
cape → base → face → hair → boots → legs → body → gloves → head → weapon
```

- The `head` layer draws over `hair`. A `head` equip's appearance sheet declares
  `covers_hair: true|false` in its manifest (§7): `true` (full helms) hides the `hair` layer
  entirely; `false` (circlets, hoods that show fringe) leaves it drawn. Partial hair
  (hat-with-fringe composites) is deliberately out of first-pass scope — Open Questions.
- `weapon` draws frontmost, always. A behind-the-back sheathed/idle weapon position is not
  modeled in this pass (the weapon layer is drawn in-hand in all states) — Open Questions.
- Facing is handled by horizontal flip of the entire composed stack (standard side-scroller
  convention; single-side authoring, per `40_assets/ART_BIBLE.yaml`'s few-frames principle).

## 5. Identity layers & creation options

Creation-time customization is **mechanism-first** in this doc; authored option counts are
first-pass and flagged:

- **`base`** — one drawn body sheet; **4 skin tones** as palette variants of it. A palette
  variant is a recolor of an authored sheet through a swap table; each variant still mints its own
  `pc_base_NNN` id (§7) so every on-disk sheet remains individually addressable.
- **`face`** — **6** authored faces (eyes/expression at 32px scale; readable, not detailed —
  silhouette-first, `40_assets/ART_BIBLE.yaml`).
- **`hair`** — **8** authored styles × **4** colors (palette variants), colors drawn from
  ART_BIBLE-ramp-derived swap tables (no off-palette colors without amendment).

One unisex body rig serves all characters in this pass (no gendered rig split — a second body rig
doubles every identity *and* equipment sheet and is a scope call for the owner, not this doc;
flagged). All identity choices are data on the character record (`10_systems/PERSISTENCE.md`),
immutable in the interim build; a paid barber/mirror NPC is a future-economy idea, not designed
here.

## 6. Equipment appearance binding

Every **equip** item row in a visible slot carries an `appearance` field
(`20_schemas/item.schema.md`) referencing the `pc_<slot>_NNN` sheet it renders as:

- `appearance` is **required** for the seven visible slots, **forbidden** for `ring`/`amulet`.
- The reference must sit in the `docs/ID_REGISTRY.md` block matching the item's own `slot`
  (a `body` item may not point at a `pc_legs_*` sheet).
- **Many-to-one sharing is the norm**: tier reskins should share or palette-vary sheets (a Lv 8
  and Lv 15 blade can be the same silhouette, recolored — each recolor minting its own `pc_*` id,
  §5). Budget guidance, not law: distinct silhouettes are what boss uniques and rarity flexes are
  for (`10_systems/ITEMS.md` §11).
- The item's **icon** (`20_schemas/item.schema.md` `icon`) is a separate, unrelated asset
  (`40_assets/UI_ART_SPEC.md` item-icon rules) — inventory art never doubles as layer art.

## 7. Export identity: `pc_<layer>_NNN` (the entity_id answer)

The player has no single `entity_id` — **each layer sheet is its own export entity**. A `pc_*` id
serves as the `{entity_id}` in the locked `40_assets/ART_BIBLE.yaml`
`export_contract.frame_naming` pattern (`{entity_id}_{state}_{NN}`), exactly as `mob_NNN`/`npc_NNN`
do:

```
pc_body_004_cast_02      # frame 02 of the cast clip of body-armor appearance sheet 004
pc_hair_003_walk_05
```

- ID blocks live in `docs/ID_REGISTRY.md` (Player appearance layers); ids are immutable and
  range-checked like every other id (`docs/VALIDATION.md` §4). The layer tokens and `pc_` prefix
  are registered in `00_vision/GLOSSARY.md` (Provisional, pending C-gate promotion).
- Each sheet gets a `40_assets/SPRITESHEET_SPEC.md` §7 manifest (`<pc_id>.atlas.yaml`,
  `id` = the `pc_id`, `schema: 40_assets/SPRITESHEET_SPEC.md`), with the §3 rig's states/counts and
  — for `head` sheets only — the additional `covers_hair` boolean (§4). This is the one field this
  doc adds to that manifest shape, scoped to `pc_head_*` manifests.
- This resolves the open player-`entity_id` question in `40_assets/ANIMATION_STATES.md` /
  `40_assets/SPRITESHEET_SPEC.md`: the answer is *plural*. The "player" row in the required-set
  matrix applies to the canonical rig — and therefore to every layer sheet. Job-line tokens are
  **not** used as export ids (a character's line changes at advancement; its sheets don't).

Folder layout, filling in `40_assets/SPRITESHEET_SPEC.md` §9's `player/` placeholder:

```
assets/characters/player/
  base/    pc_base_NNN/    pc_base_NNN.png  + .atlas.yaml
  face/    pc_face_NNN/    ...
  hair/    pc_hair_NNN/    ...
  weapon/  pc_weapon_NNN/  ...
  head/    pc_head_NNN/    ...        # manifest carries covers_hair
  body/    pc_body_NNN/    ...
  legs/    pc_legs_NNN/    ...
  boots/   pc_boots_NNN/   ...
  gloves/  pc_gloves_NNN/  ...
  cape/    pc_cape_NNN/    ...
```

## 8. Runtime & authority notes (design-level, for the Phase E pass)

In Godot terms (`30_engineering/ENGINEERING_STANDARDS.md`'s patterns, not new law): one rig node
owns the state machine; each layer is an `AnimatedSprite2D` (or equivalent) child built from its
sheet's manifest, all subscribed to the rig's single (state, frame) clock — signals up, calls
down; frame data always from manifests, never hardcoded (data-driven prime directive). Appearance
is assembled from: character record (identity ids) + equipped items' `appearance` refs — both
server-authoritative data (`10_systems/PERSISTENCE.md`); the composition itself is pure client
presentation. Skill FX overlays sit above the whole stack (`40_assets/SKILL_ANIMATION.md` §4);
status/HUD feedback never draws on the character (`10_systems/HUD.md` §8).

## Open Questions

- **Identity option counts (§5) are first-pass** (4 skins / 6 faces / 8×4 hair): owner may resize
  before Phase D asset briefs; the mechanism (authored sheet × palette variant, each variant its
  own `pc_*` id) is this doc's actual law.
- **Single unisex rig (§5)** is a cost decision, not a creative ruling — a second body rig doubles
  every sheet in §7's tree. Owner call; flagged, not decided.
- **No per-`weapon_type` stance variants (§3)** — one shared `attack`/`cast` set. If playtesting
  says a bow drawn like a sword breaks readability (P1), the extension path is per-weapon-type
  `attack`/`cast` **rows appended to the rig** (state tokens unchanged, extra manifest rows keyed
  `attack@bow` — naming TBD then), which multiplies only the two action rows, not the whole sheet.
  Deliberately deferred.
- **Partial hat/hair compositing (§4)** — `covers_hair` is all-or-nothing; fringe-preserving hats
  need a split hair sheet (front/back rows) and are deferred.
- **Sheathed/idle weapon position (§4)** — weapon always drawn in-hand this pass.
- **`pc_id`-as-`entity_id` reading (§7)** instantiates the locked ART_BIBLE pattern with a new id
  family rather than amending it; flagged for Agent-3 acknowledgment through the ART_BIBLE
  amendment channel alongside the pending frame-budget items — no wording change requested.
- **Palette-swap tooling ownership** (who generates recolor variants — Phase D content tooling or
  the Phase E pass) is unassigned, same gap as `40_assets/SPRITESHEET_SPEC.md`'s packing-tool
  question; flagged for `60_agents/` scoping.
- **Ring/amulet stay invisible** by design this pass; if a future arc wants visible accessory
  flair, it should arrive as new layers here, never as baked base-sheet art.
