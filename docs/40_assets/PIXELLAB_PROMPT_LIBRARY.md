---
id: pixellab_prompt_library
schema: 40_assets/PIXELLAB_PROMPT_LIBRARY.md
references: [ART_BIBLE, CHARACTER_COMPOSITING, SPRITESHEET_SPEC, ANIMATION_STATES,
             ANIMATION_TIMING, UI_ART_SPEC, MAP_TRAVERSAL, ART_GENERATION_RUNBOOK,
             ROLE_ART_DIRECTOR, ROLE_ART_QUARTERMASTER, ID_REGISTRY, VALIDATION]
tool_surface_verified: 2026-07-24   # live PixelLab MCP schema read; re-verify per § 0.1
---

# PIXELLAB_PROMPT_LIBRARY.md — PixelLab MCP Call Recipes for the Art Pass

References: `docs/40_assets/ART_BIBLE.yaml`, `docs/40_assets/CHARACTER_COMPOSITING.md`,
`docs/40_assets/SPRITESHEET_SPEC.md`, `docs/40_assets/ANIMATION_STATES.md`,
`docs/40_assets/ANIMATION_TIMING.md`, `docs/40_assets/UI_ART_SPEC.md`,
`docs/15_maps_system/MAP_TRAVERSAL.md`, `docs/70_integrations/ART_GENERATION_RUNBOOK.md`,
`docs/60_agents/roles/ROLE_ART_DIRECTOR.md`, `docs/60_agents/roles/ROLE_ART_QUARTERMASTER.md`,
`docs/ID_REGISTRY.md`, `docs/VALIDATION.md`

Owner doc for the **concrete PixelLab MCP call** behind every asset class: which tool, which
parameter values, and the shape of the `description` string. It is the missing middle layer
between two docs that already exist and are not re-stated here — `ART_GENERATION_RUNBOOK.md`
owns *when* a batch runs, in what order, under what credentials, and through which QA gate;
`ROLE_ART_QUARTERMASTER.md` owns *whether* a call is worth its generations (cost table, budget
bands, Lane A/Lane B routing, the mandatory `get_balance` check). This doc owns neither. It also
mints **no visual law**: every pixel, palette, ramp, size, pivot, frame-count, fps and export
value stays in `ART_BIBLE.yaml` / `SPRITESHEET_SPEC.md` / `ANIMATION_STATES.md` /
`ANIMATION_TIMING.md` and is cited by key, never restated.

`ART_BIBLE.yaml`, `UI_ART_SPEC.md` and `ENGINEERING_STANDARDS.md` are change-controlled
(`CLAUDE.md` Law 5). Nothing here edits them. Where a recipe needs a value those files do not
supply, it goes to `## Open Questions` — never to an invented default (`CLAUDE.md` Law 4).

**Every character, object and tile call in this library is side-view.** Rebillion is a
side-scrolling platformer; a top-down asset is a rejected asset, not a stylistic variant.

---

## 0. The verified tool surface

Read live from the PixelLab MCP on the date in this doc's `tool_surface_verified` front-matter
field. Tool names are the MCP's own, minus the `mcp__claude_ai_Pixellab_AI__` prefix.

| Tool | Used by this library for | Recipe |
|---|---|---|
| `create_character` | base body; monsters; NPCs | §2.1, §4.6 |
| `animate_character` | every animated state row | §3 |
| `create_character_state` | identity-preserving dressed variants (the §2.3 workaround) | §2.3 |
| `create_map_object` | anchored parts; terrain chunks; set-pieces; parallax | §2.2, §4.2–§4.5 |
| `create_1_direction_object` | anchored-part **variant batches** (the candidate-grid economy) | §2.2.1 |
| `create_sidescroller_tileset` | AB-001 **built** structures on the 16 px grid | §4.1 |
| `create_tiles_pro` | the only palette-transfer lever in the surface (`style_options`) | §1.3 |
| `select_object_frames` / `dismiss_review` | resolving `review`-status candidate grids | §2.2.1 |
| `get_balance` | quartermaster protocol — not this doc's | `ROLE_ART_QUARTERMASTER.md` |
| `delete_animation` | mandatory before any re-roll | `ROLE_ART_QUARTERMASTER.md` retry rule |

**Present in the MCP but deliberately unused by this library** — each for a stated reason, so a
future operator does not "discover" them and reach for the wrong one:

| Tool | Why not |
|---|---|
| `create_topdown_tileset` | its `view` enum offers only the two top-down angles — no side view. Cannot produce playfield art for this game. |
| `create_building_kit` | its `tile_type` enum is isometric / square-topdown / oblique — no side projection. §4.1's sidescroller tileset covers built structures instead. |
| `create_8_direction_object` | a side-scroller renders one facing and mirrors it (`CHARACTER_COMPOSITING.md` §1); 7 of 8 rotations are paid for and discarded. Its own tool contract also routes character sprites to `create_character` instead. |
| `create_portrait_character` | no sprite-scale portrait exists in this arc — `CHARACTER_COMPOSITING.md` Open Questions defers portraits entirely. |
| `create_ui_asset`, `create_font` | UI is `UI_ART_SPEC.md`'s, locked. Both collide with it (§5.4) — proposals only, via the `UA-` channel. |
| `create_isometric_tile`, `create_path_tiles` | isometric / top-down projections; no side-scroller use. |

### 0.1 Three enforcement truths (read before writing any call)

The brief for this library assumed PixelLab pins style through parameters. Verified against the
live schemas, that is **partly false**, and the three gaps below shape every recipe that follows.
They are stated here once rather than repeated per recipe.

1. **Style parameters are soft, and some are ignored outright.** `create_character`'s own
   contract calls `outline` / `shading` / `detail` "soft guidance — the model may not follow
   exactly"; `shading` is **ignored** in `v3` and `pro` modes, and `outline`/`detail` are hints
   only in `v3`. So `ART_BIBLE.yaml`'s `palette.outline.mode` and `shading` block cannot be
   *guaranteed* by a parameter — they are enforced at the `ROLE_ART_DIRECTOR` QA gate
   (`ART_GENERATION_RUNBOOK.md` §5) and by the rejection loop, exactly as that runbook already
   specifies. Set the parameters anyway (they help); never treat them as a contract.

2. **No palette parameter exists.** Not one character, object or sidescroller-tileset tool
   accepts a palette, a color list, or a color-reference image. `ART_BIBLE.yaml`'s `palette.ramps`
   and `palette.neutrals` therefore cannot be pinned at generation time at all. The only four
   palette levers in the entire surface are:
   - `create_tiles_pro` → `style_options: {"color_palette": true}` against `style_images`
     (a genuine palette copy — tiles only);
   - `create_1_direction_object` → `style_images` (up to 8 refs, style transfer including color);
   - `create_character_state` → `use_color_palette_from_reference: true` (snaps a variant to its
     source character's palette — the mechanism §2.3 leans on);
   - `create_ui_asset` → `color_palette` (a free-text *hint*, not a lock).

   Consequence: palette conformance is a **post-generation indexed remap plus QA**, not a
   generation parameter (§5.2 step 2). This is the single largest deviation from the brief's
   assumption, and it is why `ART_GENERATION_RUNBOOK.md` §5's checklist line 1 is load-bearing
   rather than a formality.

3. **`ART_BIBLE.yaml`'s `pixellab_defaults.negatives` has no field to go in.** No tool in the
   surface accepts a negative prompt. The `negatives` string is unreachable as a parameter; the
   anti-goals it encodes survive only as QA rejection criteria. Flagged in Open Questions — do
   not fold negatives into the `description` string, which would spend prompt budget on tokens
   the model reads as *subject matter* ("no gradients" invites gradients).

4. **Canvas ≠ content box.** `create_character`'s `size` is the *character* size; its contract
   states the canvas comes out **~40 % larger** to leave animation headroom (its own example:
   48 px character → ~68 px canvas). `create_map_object` clamps width/height to a **32 px
   minimum**. Neither equals `SPRITESHEET_SPEC.md` §4's exact `size_class` content box, and
   neither places the pivot at §5's feet-center. A crop-and-register step is therefore
   **mandatory** on every generated frame (§5.2 step 1) — it is not optional cleanup.

---

## 1. The shared parameter spine

Every call in this library is built from this spine plus its own recipe row. Nothing here
introduces a value; each row binds an `ART_BIBLE.yaml` key to the enum member the MCP actually
accepts.

### 1.1 Parameters

| Parameter | Value | Bound to | Note |
|---|---|---|---|
| `view` | `"side"` | the game's genre (`ART_BIBLE.yaml` `identity.genre`) | Non-negotiable on `create_character`, `create_map_object`, `create_8_direction_object`. **Enum trap:** `create_1_direction_object` spells the same concept `"sidescroller"`, and `create_tiles_pro` spells it `tile_view: "side"`. Three tools, three spellings. |
| `outline` | `"selective outline"` | `ART_BIBLE.yaml` `palette.outline.mode` (`selective`) | Exact enum match. Available on `create_character`, `create_map_object`, `create_sidescroller_tileset`. Soft guidance per §0.1(1). |
| `shading` | ⚠ **unbound** | `ART_BIBLE.yaml` `shading.model` + `shading.ramp_steps` | No enum member means "4-step stepped ramp, no gradients". Candidates are `"basic shading"` and `"medium shading"`. **Open Question** — the R1 exemplar gate picks one and it is recorded there, not guessed here. |
| `detail` | per recipe | `ART_BIBLE.yaml` `pixel.art_style` | **Enum trap:** `create_character` / `create_map_object` use `"high detail"`; `create_sidescroller_tileset` uses `"highly detailed"`. Not interchangeable. |
| `size` / `width` / `height` | the entity's `size_class` value | `ART_BIBLE.yaml` `sizing.size_classes` | Cited by key, never restated. All five classes fall inside `create_character`'s standard-mode range. Output is still cropped per §5.2 step 1. |
| `text_guidance_scale` | tool default | — | Raise only for a motif the model keeps dropping; log the change in the batch ledger. |
| `n_directions` | `4` | `CHARACTER_COMPOSITING.md` §1 (one facing, stack mirrors) | The floor — the API has no `1`. Three of four rotations are discarded (§5.2 step 5). Ignored in `v3`/`pro`, which always bill 8. |
| `mode` | `"standard"` | `ROLE_ART_QUARTERMASTER.md` complexity rubric | That doc routes mode by budget band; this doc never picks `pro` on its own initiative. |

### 1.2 The `description` string

`ART_BIBLE.yaml` `pixellab_defaults` already fixes what a description may contain:
`style_prompt_core` verbatim, plus **only** the injects listed in `per_asset_injects_only`
(`silhouette`, `palette_accent`, `motif`, `size_class`, `state_list`) — extended by amendment
**AB-002** with `part_layer` and `pose_ref` for composited-part generation. The template:

```
description = "<ART_BIBLE pixellab_defaults.style_prompt_core, verbatim>"
            + ", " + <subject / silhouette>
            + ", " + <motif — ART_BIBLE environment.biome_identity[<region>].motif for placed art>
            + ", " + <palette_accent — the ramp KEY from ART_BIBLE palette.ramps, by name>
            + [part-only clause, §2.2]
```

Three rules, all inherited:

- **The core string is pasted, never paraphrased.** It is a locked value in a change-controlled
  file; reproducing it in this doc would fork it (Law 2). Read it from `ART_BIBLE.yaml` at call
  time.
- **Name ramps, never hex.** `"ember ramp"`, not any color literal — the model cannot honor a
  hex value anyway (§0.1(2)), and restating hex here would violate Law 2 twice over.
  `palette.usage_rules` (1 dominant ramp + neutrals + ≤1 accent) is judged **per part** for
  composites, per AB-002.
- **No negatives in the description.** §0.1(3).
- **No IP names in the description.** §1.2.1.

### 1.2.1 The Maple-style lineage vs. the anti-clone rule

Rebillion's design lineage is explicitly the classic Maple-style side-scrolling MMO, and the tree
already records it where it changes behavior: foothold terrain with hand-painted chunks
(`ART_BIBLE.yaml` amendment **AB-001**, `MAP_TRAVERSAL.md`), the paper-doll composited player
sprite (**AB-002**, `CHARACTER_COMPOSITING.md` — "in the tradition of classic side-scrolling
MMOs"), the framed-box UI identity (`UI_ART_SPEC.md` — "same family as classic 2D MMOs, NOT a
copy"), and the ring-shaped hub world (`WORLD_PLAN.md`). That lineage is **structural law** and it
is why the recipes above look the way they do — one facing, feet-center pivot, layered stack,
16 px built grid, non-tiled organic ground.

It is also the one thing that must never reach a `description` string. `ART_BIBLE.yaml`
`identity.anti_goals` carries "must NOT clone any existing IP" as a locked value, and
`UI_ART_SPEC.md` repeats the "NOT a copy" framing. Naming the IP in a prompt fails that value
twice over: it is the anti-goal stated literally, and it steers the generator toward recognizable
copies of protected character and tile art — which QA would then have to reject after paying for
it.

So the lineage is expressed **through the parameters and the genre vocabulary**, never through a
franchise name:

| Say this in the prompt | Not this |
|---|---|
| `view: "side"`, one facing, feet-center framing | any franchise or title name |
| "layered paper-doll part, just the \<layer\>, no body" | a named game's character or class |
| the `ART_BIBLE.yaml` `environment.biome_identity[<region>].motif` for the region | a named game's town, map, or region |
| the ramp key from `ART_BIBLE.yaml` `palette.ramps` | "the palette from \<game\>" |
| "framed pixel UI panel with chunky readable border" | a named game's UI |

This is not a style preference — it is `ART_BIBLE.yaml` `identity.anti_goals` enforced at the one
point where a prompt could violate it. A description containing a franchise name is a rejected
call before it is sent, not a QA finding after.

### 1.3 Palette transfer, where it is available

The one place a palette genuinely transfers is `create_tiles_pro`:

```
create_tiles_pro(
  description   = "1). <tile A> 2). <tile B> ...",     # numbered, per its own contract
  style_images  = [<approved, QA-passed tile from this region>],
  style_options = {"color_palette": true, "outline": true, "shading": true, "detail": true},
  tile_view     = "side",
)
```

Use it for **follow-on** tile batches once a region's exemplar has passed QA — it is the cheapest
way to hold a region's ramp across a set. It cannot bootstrap a region (there is no approved
reference yet), so the exemplar itself goes through §4.1.

---

## 2. Part 1 — Modular equipment & appearance parts (paper-doll)

Binds to `CHARACTER_COMPOSITING.md`: the ten-layer stack and z-order (§2), the animated /
anchored split (§3), the anchor law (§4), and the token economy (§9). Every part is authored
against `style_base_00`'s canonical pose set, at `ART_BIBLE.yaml` `sizing.player_frame`, with the
feet-center pivot of `SPRITESHEET_SPEC.md` §5 — **not** canvas center, which is what PixelLab
returns (§0.1(4)).

Part IDs come from `docs/ID_REGISTRY.md`'s "Appearance styles" block (`style_*`) or the worn
item's own `item_equip_NNNN`, standing in the `{entity_id}` position of
`ART_BIBLE.yaml` `export_contract.frame_naming` (AB-002; `CHARACTER_COMPOSITING.md` §6).

### 2.1 The base body — generated first, always

It defines the skeleton, the pose set, and the anchor map every other part is authored against
(`CHARACTER_COMPOSITING.md` §9). Nothing else in the wardrobe may generate before it has passed
QA.

```
create_character(
  name         = "style_base_00",
  description  = <§1.2 template; subject = the neutral-undergarb base body of
                  CHARACTER_COMPOSITING.md §2; skin ramp = the canonical AB-002 skin_NN
                  swatch named by ART_BIBLE amendment AB-002>,
  view         = "side",
  size         = <ART_BIBLE sizing.size_classes[ sizing.player_frame ] — cited, not restated>,
  n_directions = 4,
  outline      = "selective outline",
  shading      = <§1.1 Open Question>,
  detail       = "medium detail",
  body_type    = "humanoid",
  proportions  = <Open Question — see below>,
  mode         = "standard",
)
```

- `proportions` accepts a preset (`default`, `chibi`, `cartoon`, `stylized`, `realistic_male`,
  `realistic_female`, `heroic`) or custom ratios. **No doc in this tree fixes player body
  proportions** — `ART_BIBLE.yaml` fixes the 32 px frame but not the head-to-body read. Open
  Question; the R1 exemplar gate settles it, and once settled it is identical on every humanoid
  asset forever (it is a silhouette-identity decision, not a per-asset knob).
- The base body ships one **canonical** skin ramp only. The other four `style_skin_NN` swatches
  are palette remaps at import (`CHARACTER_COMPOSITING.md` §5) and cost **zero** generations —
  never generate a second base body for a skin tone.
- `climb` shows the character's back (`CHARACTER_COMPOSITING.md` §4.1). `create_character`'s
  4-direction output includes a rear rotation; keep it as the climb reference rather than
  generating a separate back-view character.

### 2.2 Anchored parts — `cape`, `face`, `hair`, `head`, `weapon`

1–3 single-frame images each (`CHARACTER_COMPOSITING.md` §3.1), not frame sets. This is the whole
reason a new hair style costs ~2 images instead of ~34.

```
create_map_object(
  description = <§1.2 template>
              + ", just the <layer> alone, no body, no character, no shadow,
                 transparent background",
  view        = "side",
  width       = 32, height = 32,      # create_map_object's floor; crop per §5.2 step 1
  outline     = "selective outline",
  shading     = <§1.1 Open Question>,
  detail      = "medium detail",
)
```

The part-only clause is **prose, not a parameter** — no tool has a "part only" flag. It is the one
place where wording carries real load, so it is stated the same way every time: name the layer,
then negate body / character / shadow, then affirm transparency.

| Layer | Rows to generate (`CHARACTER_COMPOSITING.md` §3.1) | Anchor it lands on (§4) | Part sidecar |
|---|---|---|---|
| `cape` | `idle`; optional `walk` | `torso_px` | `origin_px` |
| `face` | `idle`; optional `hit`, `die` | `head_px` | `origin_px` |
| `hair` | `idle` (front) + `climb` (back) | `head_px` | `origin_px` |
| `head` | `idle` (front) + `climb` (back) | `head_px` | `origin_px` |
| `weapon` | `idle` (rest), `jump` (raised), `attack` (strike) | `grip_px` + `grip_pose` | `origin_px` |

- Every anchored part declares `origin_px` in its `.atlas.yaml` (`CHARACTER_COMPOSITING.md` §4/§6)
  — the pixel *in the part image* that lands on the base body's anchor. Placement is
  `anchor − origin`, integer only (`ART_BIBLE.yaml` `no_sub_pixel`). Reading `origin_px` off a
  generated image is a human/QA step; nothing in the MCP emits it.
- The weapon's three rows exist because the anchor map's `grip_pose` selects between them per
  frame, and `CHARACTER_COMPOSITING.md` §4 requires the `attack` row to land on exactly the frame
  `ANIMATION_TIMING.md` §3 fixes as the hit-frame. Generate all three or the strike desyncs from
  the damage signal.
- Any state without its own row falls back to the part's `idle_00` image (§3.1) — that fallback is
  why this table is short, and it must not be "helpfully" filled in with extra generated rows.

#### 2.2.1 The candidate-grid economy (use this for variant families)

`create_1_direction_object` returns a **grid of candidates in one call**, count set by `size`:
≤42 px → 64 candidates, ≤85 px → 16, ≤170 px → 4. At the 32 px part size that is **64 hair
variants, or 64 hats, for one call's generations**. The result enters `review` status; inspect it
with `get_object`, then keep or discard:

```
create_1_direction_object(
  description      = <§1.2 template + part-only clause>,
  item_descriptions = [<per-variant descriptions, one per candidate>],
  view             = "sidescroller",          # NOT "side" — this tool's enum differs (§1.1)
  size             = 32,
  style_images     = [<QA-passed sibling part, ≤256 px>],   # palette carry-over, §0.1(2)
)
→ get_object(object_id)
→ select_object_frames(object_id, indices=[...])   # each kept index becomes its own object
→ dismiss_review(object_id)                        # if none are worth keeping
```

This is the cheapest route to the twelve hair styles, six hats, and twenty-four weapons of
`CHARACTER_COMPOSITING.md` §9's wardrobe table. Route the spend through
`ROLE_ART_QUARTERMASTER.md` first — its cost table prices this tool at the high end, so a single
call that yields 64 usable candidates and a single call that yields 3 cost the same.

### 2.3 Animated parts — `base`, `body`, `legs`, `boots`, `gloves` ⚠

**There is no PixelLab primitive that animates a part-only layer against an external skeleton.**
`animate_character` requires a `character_id` from `create_character`; a transparent shirt with no
body is not a character. `CHARACTER_COMPOSITING.md` §9's "pose-guided per-frame generation" names
an outcome the current tool surface does not directly provide. This is the largest gap in the
library and it is **not** papered over with a plausible-looking call.

Two candidate lanes, neither blessed — the R1 spike gate (`ART_GENERATION_RUNBOOK.md` §3's
"base body + 1 outfit + 2 hairs") exists precisely to decide between them, and it should now be
read as deciding *this*:

- **Lane B-dressed.** Generate the *dressed* figure as `create_character_state(character_id=<base
  body>, edit_description="wearing <the outfit>", use_color_palette_from_reference=true)` — which
  preserves the base body's identity and palette across all rotations — animate that, then extract
  the part layer by differencing against the base body's matching frames. Costs a full frame set
  per outfit and needs a differencing step nothing owns yet.
- **Lane A.** Author the animated equip parts as self-generated art per
  `ROLE_ART_QUARTERMASTER.md`'s Lane A contract, using the base body's frames as the pose guide.
  Zero PixelLab generations; carries `placeholder: true` until the budget allows otherwise.

Whichever wins, the alignment invariant is unchanged and non-negotiable: layer N frame `walk_03`
must overdraw layer M frame `walk_03` with **zero offset math** (`CHARACTER_COMPOSITING.md` §1).
A part that cannot hold the base body's pose at a given frame is an invalid part.

---

## 3. Part 2 — Frame-by-frame animation

Spritesheets are never hand-laid. Frames ride the character's fixed skeleton via
`animate_character`, which is what prevents the shimmer and inter-frame morph that free
per-frame generation produces. States and counts are `ANIMATION_STATES.md` §5's player row and
`ART_BIBLE.yaml` `animation.frame_budgets`; fps and hit-frame are `ANIMATION_TIMING.md`'s; atlas
packing is `SPRITESHEET_SPEC.md`'s. None of those numbers are restated here.

### 3.1 The call

```
animate_character(
  character_id       = <from §2.1>,
  animation_name     = <one of the 12 ANIMATION_STATES.md §1 tokens — exact, never a synonym>,
  action_description = <movement/pose only, e.g. "walking"; no locations, no objects>,
  mode               = "v3",
  directions         = ["east"],        # one facing; the stack mirrors (§3.3)
  frame_count        = <ART_BIBLE animation.frame_budgets[<state>] — see §3.2>,
  keep_first_frame   = false,           # ← load-bearing, see below
)
```

- **`keep_first_frame: false` is mandatory.** It defaults to `true`, which stores the input
  reference frame *in addition* to the generated ones — `frame_count = 8` then stores **9**
  frames. Nine frames in a row budgeted for eight silently breaks `SPRITESHEET_SPEC.md` §2.2's
  `cols` = max-frame-count invariant and its column-index-equals-frame-index guarantee. Set it
  false on every call.
- `animation_name` must be the exact state token. `SPRITESHEET_SPEC.md` §7.2 requires the atlas
  manifest's `states` keys to match the entity's declared `animation_states`; a clip named
  `"run"` instead of `walk` fails `docs/VALIDATION.md` check 6 downstream.
- `action_description` carries movement only, per the tool's own contract. The style spine (§1.2)
  lives on `create_character`; re-injecting it here does nothing useful.
- `mode: "template"` is available and costs less (1 generation/direction), with a large humanoid
  template list (`walk`, `walking-*`, `running-*`, `jumping-1`, `two-footed-jump`, `taking-punch`,
  `fireball`, `falling-back-death`, …). **Its frame count is fixed by the template**, so it can
  only be used where that count happens to land inside the state's `ART_BIBLE.yaml` budget —
  unverifiable until the template is run once. Treat template mode as a §3.2-constrained
  optimization the exemplar gate confirms per state, not a default.

### 3.2 The frame-budget collision ⚠

`animate_character`'s `frame_count` accepts **even integers 4–16 only** (v3). Intersecting that
with `ART_BIBLE.yaml` `animation.frame_budgets` for the nine player states:

| State | Budget (`ART_BIBLE animation.frame_budgets`) | Reachable via `frame_count` | Recipe |
|---|---|---|---|
| `idle` | cited | 4 | `frame_count = 4` (budget's top end; the low end is unreachable) |
| `walk` | cited | 6, 8 | either |
| `jump` | cited | **none** | §3.2.1 |
| `fall` | cited | **none** | §3.2.1 |
| `climb` | cited | 4 | `frame_count = 4` |
| `attack` | cited | 4, 6 | either; `hit_frame` per `ANIMATION_TIMING.md` §3.1 |
| `cast` | cited | 4, 6 | either; same |
| `hit` | cited | **none** | ⚠ **Open Question** |
| `die` | cited | 4, 6 | either |

Six of nine states are fine. Three are not, and they are not the same problem:

#### 3.2.1 `jump` / `fall` — resolved by held-pose generation, not by animation

`ANIMATION_STATES.md` §1.1 already states that at these states' locked budget "play through once"
and "hold a pose" are functionally the same thing — the clip plays its frames once, then holds the
last for the physics duration `MAP_TRAVERSAL.md` §1 owns. A held pose is a **still**, so the
correct primitive is not `animate_character` at all:

```
create_character_state(
  character_id     = <base body>,
  edit_description = "<the jump rise pose | the descent pose>",
  use_color_palette_from_reference = true,
)
```

…then take the side-facing rotation as the state's frame(s). This follows `ANIMATION_STATES.md`
§1.1 rather than working around it, and it costs a state variant instead of a whole clip.

#### 3.2.2 `hit` — a genuine gap

`hit`'s budget tops out below `frame_count`'s floor of 4, and 3 is odd besides. Unlike jump/fall,
`hit` is a real short clip with a flinch read, not a held pose, and `ANIMATION_TIMING.md` §5 lines
its playback length up against `COMBAT_FORMULA.md` §11's hitstun windows — so over-generating to 4
frames and discarding one would change the clip's authored length and desync that table. No doc in
this tree authorizes either an over-generate-and-trim rule or a budget change. **Open Question**,
flagged for `ROLE_ART_DIRECTOR` — a `frame_budgets.hit` amendment (`AB-`) and a trim rule are both
plausible; neither is invented here.

### 3.3 One facing

`CHARACTER_COMPOSITING.md` §1 fixes facing as a horizontal flip of the whole stack, never
per-layer, with anchors mirroring as `cw − x`. So exactly one profile facing is generated and the
engine mirrors it. `animate_character` in `v3` mode defaults to **south only** — for a side-view
character that is the wrong rotation, so `directions` is always passed explicitly. Which cardinal
label corresponds to the side profile under `view: "side"` is confirmed once, at the R1 exemplar
gate, and recorded there (Open Question).

### 3.4 Generation order

Per `CHARACTER_COMPOSITING.md` §9, and it is an order, not a preference:

1. `style_base_00` (§2.1) → QA → **the anchor map is authored by inspecting its frames** (§4
   there) — a few dozen coordinate pairs, zero generated art, and every later part depends on it.
2. Anchored parts (§2.2) — cheapest, single stills.
3. Animated equip parts (§2.3) — once its lane is decided.
4. Pack to atlases per `SPRITESHEET_SPEC.md` §2 (cell size, `cols`, power-of-two, 1 px padding,
   extrusion, feet-center pivot). That contract is complete; this doc adds nothing to it.

Monsters, NPCs and bosses are **not** composited — they are single entities, generated per §4.6
and animated with the same §3.1 call against their own required state set
(`ANIMATION_STATES.md` §5).

---

## 4. Part 3 — Environment

AB-001 splits the environment in two, and the split decides the tool:

### 4.1 BUILT structures → seamless tileset

Towns, interiors, dungeon brickwork, platform props — everything AB-001 leaves on the 16 px grid.

```
create_sidescroller_tileset(
  lower_description      = <the platform/center material, e.g. "cracked basalt brick">,
  transition_description = <the surface/top layer, e.g. "warm cinder crust">,
  transition_size        = <0.0 none | 0.25 light | 0.5 heavy>,
  tile_size              = {"width": <ART_BIBLE environment.tile_grid_px>,
                            "height": <same key>},
  outline                = "selective outline",
  shading                = <§1.1 Open Question>,
  detail                 = "highly detailed",     # ← this tool's enum, not "high detail" (§1.1)
  base_tile_id           = <the previous QA-passed tileset's base tile id, when chaining>,
  seed                   = <recorded in the batch ledger for reproducibility>,
)
```

- This tool is purpose-built for the job: side-view, transparent background, flat platform
  surfaces, seamless — it satisfies `ART_BIBLE.yaml` `environment.seamless` for exactly the
  category AB-001 leaves seamless.
- `lower_description` / `transition_description` are the material split, sourced from
  `ART_BIBLE.yaml` `environment.biome_identity[<region>].motif` — cited by key per region, never
  restated here.
- **Chain within a region.** Generate the region's first tileset, read its base tile id from
  `get_sidescroller_tileset`, then pass that as `base_tile_id` on the next. This is the only
  mechanism holding a region's look together across tilesets, and it partially compensates for
  §0.1(2)'s missing palette lock.
- `seed` is recorded per the runbook's §6 bookkeeping, so a QA re-roll is reproducible.

### 4.2 ORGANIC ground → hand-painted terrain chunks, NOT tiles

AB-001 is explicit: organic ground is **not** built from seamless tiles. It is hand-painted
`terrain_chunk` art snapped to `foothold` segments of arbitrary angle (`MAP_TRAVERSAL.md`, which
also keeps the 16 px grid as the measurement lens). Generating a chunk as a tileset would
contradict a landed amendment.

```
create_map_object(
  description = <§1.2 template; subject = a ground chunk that reads as a continuous slope/ledge;
                 motif = ART_BIBLE environment.biome_identity[<region>].motif>,
  view        = "side",
  width  = <chunk span>, height = <chunk depth>,     # 32–400 px
  outline = "selective outline",
  shading = <§1.1 Open Question>,
  detail  = "medium detail",
)
```

QA for these is `ART_GENERATION_RUNBOOK.md` §5 line 4 — the chunk must snap to its briefed
foothold segment with no visible seam or floating edge. Chunks are generated **first** in a
region (that runbook's §3 order), because every other class's ground-relative framing is judged
against them.

### 4.3 Static set-pieces

Buildings, portals, NPC stalls, ropes, ladders, reactors — `create_map_object` at `view: "side"`,
same spine. Behavior-carrying set-pieces take their visual tell from `ART_BIBLE.yaml`
`interactables` (portal shimmer, rope braid, ladder rungs, reactor chip/highlight, loot bounce),
cited by key.

### 4.4 Parallax layers

`ART_BIBLE.yaml` `environment.depth_layers` orders four bands and states the treatment
(desaturate + darken with depth). Generate each band as its own `create_map_object` at
`view: "side"`, wide enough to loop horizontally, and inject the band's depth into the subject
clause. The desaturation/darkening itself is applied as a post-pass against the ramp — it is a
palette operation, and per §0.1(2) no parameter performs it.

### 4.5 Style matching against an existing scene

`create_map_object` accepts a `background_image` (base64) plus an `inpainting` config
(`oval` / `rectangle` / `mask`, mask convention **white = generate, black = preserve**). When a
prop must sit inside an already-approved scene, this matches its art style and auto-detects
dimensions. Useful for the second and later props of a region; it needs an approved scene first.

### 4.6 Monsters, NPCs, bosses

`create_character` per §2.1's shape, with:

- `size` = the entity's `ART_BIBLE.yaml` `sizing.size_classes` value (all five classes fit
  standard mode's range);
- `body_type: "quadruped"` + `template` (`bear`/`cat`/`dog`/`horse`/`lion`) for four-legged mobs —
  humanoid `proportions` are ignored for these;
- the required state set from `ANIMATION_STATES.md` §5 driving §3.1's calls, including
  `telegraph` for elites/bosses and `phase_shift` for bosses;
- ⚠ `telegraph` / `phase_shift` / `spawn` frame budgets are still **proposed, not blessed**
  (`ANIMATION_STATES.md` §2.2). `ART_GENERATION_RUNBOOK.md`'s Open Questions already bars
  batch-generating those three against the proposed numbers. This library inherits that bar.

---

## 5. Part 4 — Clean-pixel & export directives

### 5.1 What is already law (cited, not restated)

- **Prompt-side enforcement**: `ART_BIBLE.yaml` `pixellab_defaults.style_prompt_core`, reused
  verbatim per call (§1.2). Its companion `negatives` has no parameter to occupy — §0.1(3).
- **Import settings**: `ART_BIBLE.yaml` `export_contract.godot_import` (Nearest filter, mipmaps
  off, fix alpha border), bound to a concrete named Godot preset by `SPRITESHEET_SPEC.md` §8 with
  Repeat disabled and Compress Mode lossless.
- **Hard prohibitions**: `ART_BIBLE.yaml` `export_contract.forbidden` — mixed pixel densities in
  one atlas, AA downsampling on export, off-palette colors without an amendment.
- **Atlas / naming / pivot**: `ART_BIBLE.yaml` `export_contract.atlas` + `frame_naming` +
  `pivot_export`, made concrete by `SPRITESHEET_SPEC.md` §2–§7.
- **QA gate and rejection loop**: `ART_GENERATION_RUNBOOK.md` §5, including its two-attempt bound
  before escalation.

### 5.2 What the export contract does **not** state — steps this library adds

Each exists because of a verified property of the generator, not as extra process. Nothing below
overrides §5.1.

1. **Crop to content box and register the pivot.** PixelLab returns a canvas ~40 % larger than the
   requested character size, and clamps objects to a 32 px floor (§0.1(4)). Every frame is cropped
   to its exact `SPRITESHEET_SPEC.md` §4 content box and positioned so the feet-contact line sits
   on §5's pivot row for that `size_class`. Cropping to the *sprite's* bounding box instead is the
   classic failure — it makes the character bob between states, which is precisely the
   float/sink `ART_BIBLE.yaml` `sizing.pivot`'s "HARD RULE" comment exists to prevent. Crop to the
   **content box**, then place the art inside it.
2. **Indexed palette remap.** Because no palette parameter exists (§0.1(2)), every accepted asset
   is remapped to `ART_BIBLE.yaml` `palette` ramps at import, the same build-step mechanism
   `CHARACTER_COMPOSITING.md` §5/§10 already specifies for skin and hair swatches (a remap between
   authored ramps cannot leave palette). A remap that cannot land on-ramp without visible damage
   is a **QA reject**, not a remap to force — that is the `export_contract.forbidden` off-palette
   line arriving one step later than expected.
3. **Frame-count reconciliation.** Confirm the stored frame count equals the authored
   `frame_count` — `keep_first_frame` (§3.1) is the one setting that silently adds a frame.
4. **Download before expiry.** `create_map_object` results **auto-delete after 8 hours**. Any
   §2.2 / §4.2–§4.4 output not retrieved inside that window is lost and must be regenerated at
   full cost. Retrieve and store in the same batch session.
5. **Discard unused rotations.** `n_directions` has no `1`; three (or seven) rotations are billed
   and generated. Keep the profile facing, discard the rest, and never let a stray rotation reach
   the atlas — it would land as an off-pose frame in a state row.
6. **Resolve `review` status.** `create_1_direction_object` leaves candidate grids in `review`.
   Close every one with `select_object_frames` or `dismiss_review` before the batch ends, so no
   half-finished object is mistaken for a QA-passed asset.
7. **Record `seed` and tool version.** `ART_GENERATION_RUNBOOK.md` §6 already requires content ID,
   brief doc, job ID and QA verdict per job; add the `seed` (where the tool accepts one) so a
   rejected asset can be re-rolled deterministically against a corrected prompt.

### 5.3 What this library does not enforce

Cost, budget bands, lane routing, and the mandatory pre-call `get_balance` are
`ROLE_ART_QUARTERMASTER.md`'s, in full. Batch order, region sequence, the exemplar gate, and
credential handling are `ART_GENERATION_RUNBOOK.md`'s, in full. A recipe in this doc is only
legal to execute once both of those have cleared it.

### 5.4 UI — proposals only

`UI_ART_SPEC.md` is locked and reached only through its `UA-` amendment channel. Two verified
collisions are recorded here as **proposals for that channel**, not as recipes:

- `create_ui_asset` produces a whole panel at a **192 px minimum**, aspect-gated, with no 9-slice
  output and no patch-margin parameter. `UI_ART_SPEC.md` requires 3×3 nine-slice frames on its
  own `base_tile_px` / `corner_px` / `patch_margins` geometry. The tool cannot satisfy that
  contract directly; a slicing post-pass would have to.
- `create_font`'s `glyph_px` enum offers `8 / 16 / 32 / 64`. `UI_ART_SPEC.md`'s text styles include
  sizes that are not members of that set. Its own Open Question ("original vs licensed pixel
  font") is upstream of this and unresolved.

---

## 6. Handoff map

| Question | Owner |
|---|---|
| What must the art look like? | `ART_BIBLE.yaml` (locked) |
| What shape does it export in? | `SPRITESHEET_SPEC.md` |
| Which states, how many frames? | `ANIMATION_STATES.md` + `ART_BIBLE.yaml` `animation.frame_budgets` |
| How fast, and which frame hits? | `ANIMATION_TIMING.md` |
| How do player layers stack and align? | `CHARACTER_COMPOSITING.md` |
| **Which tool call, with which parameters?** | **this doc** |
| In what order, under what credentials, past which QA gate? | `ART_GENERATION_RUNBOOK.md` |
| Is it worth the generations, and in which lane? | `ROLE_ART_QUARTERMASTER.md` |
| Does it pass? | `ROLE_ART_DIRECTOR.md` |

---

## Open Questions

- **`shading` enum has no ART_BIBLE binding (§1.1).** `ART_BIBLE.yaml` `shading.model`
  ("cel/stepped ramp (no gradients)") and `shading.ramp_steps` have no exact counterpart in the
  MCP enum; `"basic shading"` and `"medium shading"` are both plausible. Flagged for
  `ROLE_ART_DIRECTOR` to fix at the R1 exemplar gate and record there. No default is assumed in
  this doc.
- **`pixellab_defaults.negatives` is unreachable (§0.1(3)).** No tool in the surface accepts a
  negative prompt, so a locked `ART_BIBLE.yaml` value has no delivery mechanism. Flagged for
  `ROLE_ART_DIRECTOR`: either an `AB-` amendment restating `negatives` as QA-rejection criteria
  (which is how it already functions), or confirmation that it is intentionally advisory.
- **No palette parameter exists (§0.1(2)).** Palette conformance is a post-generation remap plus
  QA, not a generation-time guarantee. Confirm that `ART_GENERATION_RUNBOOK.md` §5 line 1 is
  intended to carry that full weight, and whether §5.2 step 2's remap belongs in this doc or in
  the packing tool whose ownership `SPRITESHEET_SPEC.md` already flags as unassigned.
- **Animated equip parts have no direct tool (§2.3).** `animate_character` cannot animate a
  part-only layer against an external skeleton, so `CHARACTER_COMPOSITING.md` §9's pose-guided
  per-frame generation has no primitive. Lane B-dressed (state + difference) vs Lane A
  (self-generated) is undecided; the runbook's existing R1 spike gate should be read as the
  decision point. This blocks the wardrobe batch, not the base body.
- **`hit` cannot be generated inside its frame budget (§3.2.2).** `frame_count`'s even-4-to-16
  domain does not intersect `ART_BIBLE.yaml` `animation.frame_budgets.hit`. Needs either an `AB-`
  budget amendment or an authorized over-generate-and-trim rule; `ANIMATION_TIMING.md` §5's
  hitstun alignment means trimming is not cost-free. Flagged for `ROLE_ART_DIRECTOR`.
- **`idle` and `climb` are pinned to one reachable frame count (§3.2).** Both budgets' low ends
  are unreachable via `frame_count`. Confirm that authoring at the top of budget is acceptable
  rather than a de-facto narrowing of a locked range.
- **Player body proportions are unfixed (§2.1).** No doc in the tree states the player's
  head-to-body read; `create_character` requires a preset or custom ratios. A silhouette-identity
  decision (`ART_BIBLE.yaml` `readability.silhouette_first`), so it belongs to
  `ROLE_ART_DIRECTOR`, once, for every humanoid asset.
- **Which cardinal is the side profile (§3.3).** Under `view: "side"`, which `directions` member
  yields the profile facing is unverified; `v3` defaults to `south`, which is wrong for a
  side-scroller. Confirm at the R1 exemplar gate and record it in the batch report.
- **Template-mode frame counts are unverified (§3.1).** `mode: "template"` costs less but fixes
  frame count from the template, and no template's count is published. Whether any template lands
  inside an `ART_BIBLE.yaml` budget can only be measured. Flagged for the exemplar gate; until
  then `v3` is the recipe.
- **`ROLE_ART_QUARTERMASTER.md`'s cost table names tools this surface spells differently.** That
  doc lists `create_map_object` alongside `create_1_direction_object` / `create_8_direction_object`
  without pricing the first, and leaves all tileset-tool costs unmeasured (its own Open Question).
  The verified surface in §0 should be reconciled into that table after the first measured batch;
  not edited here, as it is that role's file.
- **UI tools collide with the locked UI spec (§5.4).** `create_ui_asset`'s minimum size / missing
  9-slice output and `create_font`'s `glyph_px` enum both conflict with `UI_ART_SPEC.md`. Recorded
  as `UA-` channel proposals only; no UI recipe is authored in this doc.
- **`tool_surface_verified` will go stale.** Every enum, limit and default in this doc was read
  from the live MCP on that date. PixelLab ships changes; re-read the schemas at the start of any
  art-pass batch and correct this doc before executing a recipe against them.
