# PIXELLAB_PROMPT_LIBRARY.md — PixelLab MCP Call Recipes for the Art Pass

References: `docs/40_assets/ART_BIBLE.yaml`, `docs/40_assets/CHARACTER_COMPOSITING.md`,
`docs/40_assets/SPRITESHEET_SPEC.md`, `docs/40_assets/ANIMATION_STATES.md`,
`docs/40_assets/ANIMATION_TIMING.md`, `docs/40_assets/UI_ART_SPEC.md`,
`docs/15_maps_system/MAP_TRAVERSAL.md`, `docs/10_systems/COMBAT_FORMULA.md`,
`docs/WORLD_PLAN.md`, `docs/70_integrations/ART_GENERATION_RUNBOOK.md`,
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

**Verified against the live PixelLab MCP schemas on 2026-07-24.** Every enum, limit and default
below was read from the server, not assumed. Re-read them at the start of any batch and correct
this doc before executing against it (Open Questions). Tool names are the MCP's own, minus the
`mcp__claude_ai_Pixellab_AI__` prefix.

| Tool | Used by this library for | Recipe |
|---|---|---|
| `create_character` | base body; monsters; NPCs | §2.1, §4.6 |
| `animate_character` | every animated state row | §3 |
| `create_character_state` | jump/fall held poses; dressed variants (a §2.3 lane) | §2.3, §3.2.1 |
| `create_map_object` | anchored parts; terrain chunks; set-pieces; parallax | §2.2, §4.2–§4.5 |
| `create_1_direction_object` | anchored-part **variant batches** (the candidate-grid economy) | §2.2.1 |
| `create_sidescroller_tileset` | AB-001 **built** structures on the tile grid | §4.1 |
| `select_object_frames` / `dismiss_review` | resolving `review`-status candidate grids | §2.2.1 |
| `get_balance` | quartermaster protocol **and** the free authorization probe | §5.3 |
| `delete_animation` | mandatory before any re-roll | `ROLE_ART_QUARTERMASTER.md` retry rule |

**Present in the MCP but deliberately unused** — each for a stated reason, so a future operator
does not "discover" one and reach for the wrong tool:

| Tool | Why not |
|---|---|
| `create_topdown_tileset` | its `view` enum offers only the two top-down angles — no side view. Cannot produce playfield art for this game. |
| `create_building_kit` | its `tile_type` enum is isometric / square-topdown / oblique — no side projection. §4.1's sidescroller tileset covers built structures instead. |
| `create_tiles_pro` | **same defect, less obvious.** Its `tile_view` is a *depth ratio*, not a projection; projection is `tile_type`, whose enum has no side member and defaults to `isometric`. It cannot produce side-view geometry, so it is excluded on exactly the grounds above. |
| `create_isometric_tile`, `create_path_tiles` | isometric / top-down projections; no side-scroller use. |
| `create_8_direction_object` | a side-scroller renders one facing and mirrors it (`CHARACTER_COMPOSITING.md` §1), so 7 of 8 rotations are discarded. Its own tool contract also routes character sprites to `create_character` instead — that second reason is the load-bearing one. |
| `create_portrait_character` | its `portrait_to_character` direction does offer `view: "side"`, but it requires an input portrait, and no portrait art exists or is planned this arc (`CHARACTER_COMPOSITING.md` Open Questions defers portraits entirely). |
| `create_ui_asset`, `create_font` | UI is `UI_ART_SPEC.md`'s, locked. Both collide with it (§5.4) — proposals only, via the `UA-` channel. |

### 0.1 Four enforcement truths (read before writing any call)

The brief for this library assumed PixelLab pins style through parameters. Verified against the
live schemas, that is **largely false**, and the gaps below shape every recipe that follows.

1. **Style parameters are soft, and some are ignored outright.** `create_character`'s own
   contract calls `outline` / `shading` / `detail` "soft guidance — the model may not follow
   exactly"; `shading` is **ignored** in `v3` and `pro` modes, and `outline`/`detail` are hints
   only in `v3`. `create_1_direction_object` accepts **no** style parameters at all (§2.2.1). So
   `ART_BIBLE.yaml`'s `palette.outline.mode` and `shading` block cannot be *guaranteed* by a
   parameter — they are enforced at the `ROLE_ART_DIRECTOR` QA gate
   (`ART_GENERATION_RUNBOOK.md` §5) and by its rejection loop. Set the parameters anyway; never
   treat them as a contract.

   **Every tool's defaults are wrong for this game.** `view` defaults to a top-down angle on
   every tool in the surface, and `outline` defaults to a non-selective mode on every tool that
   has it. Omitting either parameter silently produces a rejected asset — so they are passed
   explicitly on every call, never left to default.

2. **No palette parameter exists.** No tool accepts a palette, a color list, or a named ramp.
   `ART_BIBLE.yaml`'s `palette.ramps` and `palette.neutrals` cannot be pinned at generation time.
   What does exist is a set of **image-reference** levers, which transfer style-and-color from an
   already-approved asset rather than from a specification:

   | Lever | Tool | Note |
   |---|---|---|
   | `reference_image_base64` | `create_character` (`mode: "v3"` only) | The strongest in the surface — its contract states the image "defines identity and style". Rotates one authored sprite into 8 directions. |
   | `use_color_palette_from_reference` | `create_character_state` | Snaps a variant to its source character's palette. The mechanism §2.3 and §3.2.1 lean on. |
   | `style_images` | `create_1_direction_object` | This tool's *only* style control (see truth 1). Mutually exclusive with `size` — §2.2.1. |
   | `background_image` | `create_map_object` | Style-matches a prop into an approved scene (§4.5). Capped at 192×192 in this mode. |
   | `base_tile_id` | `create_sidescroller_tileset` | Chains a tileset to an approved sibling (§4.1). |
   | `color_palette` | `create_ui_asset` | Free-text *hint*, not a lock. UI is out of scope (§5.4). |

   Every one of these needs an **already-approved asset** to reference, so none can bootstrap a
   region — the first asset of any class is generated unreferenced and carries the full palette
   risk. Consequence: palette conformance is a **post-generation indexed remap plus QA**
   (§5.2 step 2), not a generation parameter. This is the largest deviation from the brief's
   assumption, and it is why `ART_GENERATION_RUNBOOK.md` §5's checklist line 1 is load-bearing.

3. **`ART_BIBLE.yaml`'s `pixellab_defaults.negatives` has no field to occupy.** No tool in the
   surface accepts a negative prompt. The `negatives` string is unreachable as a parameter; the
   anti-goals it encodes survive only as QA rejection criteria. Do not fold negatives into the
   `description` string, which would spend prompt budget on tokens the model reads as *subject
   matter* ("no gradients" invites gradients). **AB-002's `pose_ref` inject is unreachable the
   same way** — see Open Questions for both.

4. **Canvas ≠ content box, in both directions.** `create_character`'s `size` is the *character*
   size; its contract states the canvas comes out ~40% larger to leave animation headroom (its
   own example: 48 px character → ~68 px canvas). That is the *too-large* direction, and §5.2
   step 1's crop handles it. The **inverse** case is unsolved and blocks §2.2: `create_map_object`
   and `create_1_direction_object` both floor at a 32 px canvas which the subject fills, but an
   anchored part must occupy a *fraction* of the player frame. Cropping relocates, it does not
   rescale, and downscaling is barred by `ART_BIBLE.yaml` `no_sub_pixel` and
   `export_contract.forbidden`. See Open Questions — anchored parts are **blocked**, not merely
   fiddly.

---

## 1. The shared parameter spine

Every call is built from this spine plus its own recipe row. Nothing here introduces a value;
each row binds an `ART_BIBLE.yaml` key to the enum member the MCP accepts — or marks the binding
absent.

### 1.1 Parameters

| Parameter | Value | Bound to | Note |
|---|---|---|---|
| `view` | `"side"` | the game's genre (`ART_BIBLE.yaml` `identity.genre`) | **Enum trap:** `create_character`, `create_map_object` and `create_8_direction_object` spell it `view: "side"`; `create_1_direction_object` spells it `view: "sidescroller"`. Two tools, two spellings, and every default is top-down. |
| `outline` | `"selective outline"` | `ART_BIBLE.yaml` `palette.outline.mode` | Exact enum match. Absent entirely from `create_1_direction_object`. Soft guidance per §0.1(1); every default is non-selective. |
| `shading` | ⚠ **unbound** | `ART_BIBLE.yaml` `shading.model` + `shading.ramp_steps` | No enum member expresses a stepped ramp at the locked step count. The full domain is `flat` / `basic` / `medium` / `detailed shading` — and `create_sidescroller_tileset` adds a fifth, `highly detailed shading`. **Open Question**; the gate picks per tool family, and this doc pre-narrows nothing. |
| `detail` | ⚠ **unbound** | — | `ART_BIBLE.yaml` `pixel.art_style` fixes outline treatment, not detail level; no key carries one. **Enum trap:** character/object tools use `"high detail"`, `create_sidescroller_tileset` uses `"highly detailed"`. **Open Question**, same gate as `shading`. |
| `size` / `width` / `height` | the entity's `size_class` value | `ART_BIBLE.yaml` `sizing.size_classes` | Cited by key, never restated. Every class fits `create_character`'s standard-mode ceiling of 128 px — but see `ART_BIBLE.yaml`'s own open question on boss sizing, which if resolved upward forces `v3`. Output is still cropped per §5.2 step 1. |
| `text_guidance_scale` | tool default | — | Exists on `create_character` and the tileset tools **only** — not on `create_map_object` or `create_1_direction_object`. Raise only for a motif the model keeps dropping. |
| `n_directions` | `4` | `CHARACTER_COMPOSITING.md` §1 (one facing, stack mirrors) | The floor — the API has no `1`. Rotations beyond the kept facing are discarded (§5.2 step 5) but **not separately billed**: standard mode is one generation regardless of direction count. Ignored in `v3`/`pro`. |
| `mode` | `"standard"` (create) / `"v3"` (animate) | `ROLE_ART_QUARTERMASTER.md` complexity rubric | That doc routes mode by budget band — **subject to the §3.2 precondition**, which forbids `pro` for any entity with a locked frame budget. |

### 1.2 The `description` string

`ART_BIBLE.yaml` `pixellab_defaults` fixes what a description may contain: `style_prompt_core`
verbatim, plus only the injects listed in `per_asset_injects_only`, extended by amendment
**AB-002** for composited-part generation. The template — angle brackets mark a substitution,
everything else is literal:

```
description = <ART_BIBLE pixellab_defaults.style_prompt_core, pasted verbatim>
            + ", " + <subject / silhouette>
            + ", " + <motif — ART_BIBLE environment.biome_identity[<region>].motif for placed art>
            + ", " + <palette_accent — the ramp KEY from ART_BIBLE palette.ramps, by name>
            + ", " + <part-only clause, §2.2 — anchored parts only>
```

Three rules, all inherited:

- **The core string is pasted, never paraphrased and never summarized.** It is a locked value in
  a change-controlled file; reproducing it in this doc would fork it (Law 2). Read it from
  `ART_BIBLE.yaml` at call time.
- **Name ramps, never hex.** The ramp key by name — the model cannot honor a hex value anyway
  (§0.1(2)), and restating hex here would violate Law 2 twice over. `palette.usage_rules` is
  judged **per part** for composites, per AB-002.
- **No negatives (§0.1(3)) and no IP names (§1.2.1) in the description.**

Of `per_asset_injects_only`'s members, `size_class` and `state_list` are carried as
*parameters* rather than prose (`size`, `frame_count`), `part_layer` survives as §2.2's
part-only clause, and `pose_ref` has no delivery mechanism at all — Open Questions.

### 1.2.1 The Maple-style lineage vs. the anti-clone rule

Rebillion's design lineage is explicitly the classic Maple-style side-scrolling MMO, and the tree
already records it where it changes behavior: foothold terrain with hand-painted chunks
(`ART_BIBLE.yaml` amendment **AB-001**, `MAP_TRAVERSAL.md`), the paper-doll composited player
sprite (**AB-002**, `CHARACTER_COMPOSITING.md` — "in the tradition of classic side-scrolling
MMOs"), the framed-box UI identity (`UI_ART_SPEC.md` — "same family as classic 2D MMOs, NOT a
copy"), and the ring-shaped hub world (`WORLD_PLAN.md`). That lineage is **structural law** and it
is why the recipes here look the way they do — one facing, feet-center pivot, layered stack,
on-grid built structures, non-tiled organic ground.

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

A description containing a franchise name is a rejected call before it is sent, not a QA finding
after.

---

## 2. Part 1 — Modular equipment & appearance parts (paper-doll)

Binds to `CHARACTER_COMPOSITING.md`: the ten-layer stack and z-order (§2), the animated /
anchored split (§3), the anchor law (§4), and the token economy (§9). Every part is authored
against `style_base_00`'s canonical pose set, at `ART_BIBLE.yaml` `sizing.player_frame`, with the
feet-center pivot of `SPRITESHEET_SPEC.md` §5 — **not** canvas center, which is what PixelLab
returns (§0.1(4)).

Part IDs come from `docs/ID_REGISTRY.md`'s "Appearance styles" block (`style_*`) or the worn
item's own `item_equip_NNNN`, standing in the `{entity_id}` position of `ART_BIBLE.yaml`
`export_contract.frame_naming` (AB-002; `CHARACTER_COMPOSITING.md` §6).

### 2.1 The base body — generated first, always

It defines the skeleton, the pose set, and the anchor map every other part is authored against
(`CHARACTER_COMPOSITING.md` §9). Nothing else in the wardrobe may generate before it has passed
QA **and been animated** (§3.4 — the anchor map needs frames, not rotations).

```
create_character(
  name         = "style_base_00",
  description  = <§1.2 template; subject = the neutral-undergarb base body of
                  CHARACTER_COMPOSITING.md §2; skin ramp = the canonical AB-002 swatch>,
  view         = "side",
  size         = <ART_BIBLE sizing.size_classes[ sizing.player_frame ]>,
  n_directions = 4,
  outline      = "selective outline",
  shading      = <§1.1 Open Question>,
  detail       = <§1.1 Open Question>,
  body_type    = "humanoid",
  proportions  = <Open Question — JSON *string*, e.g. '{"type": "preset", "name": "..."}';
                  a bare preset name is a rejected call>,
  mode         = "standard",
)
```

- `proportions` accepts a preset (`default`, `chibi`, `cartoon`, `stylized`, `realistic_male`,
  `realistic_female`, `heroic`) or custom ratios, and must be passed as a **JSON string**. **No
  doc in this tree fixes player body proportions.** Open Question; it is a silhouette-identity
  decision, settled once for every humanoid asset — so it belongs to the global wardrobe spike
  gate, not a per-region one.
- The base body ships one **canonical** skin ramp only. The remaining `style_skin_NN` swatches are
  palette remaps at import (`CHARACTER_COMPOSITING.md` §5) and cost **zero** generations — never
  generate a second base body for a skin tone.
- `climb` shows the character's back (`CHARACTER_COMPOSITING.md` §4.1). The 4-direction output
  includes a rear rotation; keep it as the climb reference rather than generating a second
  character.

### 2.2 Anchored parts — `cape`, `face`, `hair`, `head`, `weapon` ⚠ BLOCKED

Which rows each layer authors, which anchor positions it, and the `idle_00` fallback law are
`CHARACTER_COMPOSITING.md` §3.1 and §2 — read there, not here. This doc adds only the call and
the one sidecar field the generator cannot emit:

```
create_map_object(
  description = <§1.2 template>
              + ", just the <layer> alone, no body, no character, no shadow,
                 transparent background",
  view        = "side",
  width  = 32, height = 32,      # the tool's floor — see the blocker below
  outline     = "selective outline",
  shading     = <§1.1 Open Question>,
  detail      = <§1.1 Open Question>,
)
```

**This recipe does not currently produce placeable art.** Both object tools floor at a 32 px
canvas that the subject fills, but an anchored part must occupy a fraction of the player frame
(`ART_BIBLE.yaml` `sizing.player_frame`) — a hair or hat generated this way arrives at
whole-character scale. §5.2 step 1's crop relocates; it cannot rescale, and downscaling is barred
twice (`ART_BIBLE.yaml` `no_sub_pixel`, `export_contract.forbidden`). This blocks five of ten
layers and the entire wardrobe of anchored parts. Open Question — do not bulk-generate against
this recipe until it resolves.

- The part-only clause is **prose, not a parameter** — no tool has a "part only" flag. It is the
  one place where wording carries real load, so it is phrased identically every time: name the
  layer, negate body / character / shadow, affirm transparency.
- Every anchored part declares `origin_px` in its `.atlas.yaml` (`CHARACTER_COMPOSITING.md`
  §4/§6) — the pixel *in the part image* that lands on the base body's anchor. Reading `origin_px`
  off a generated image is a human/QA step; nothing in the MCP emits it, and no validator checks
  it.
- The weapon's rows exist because the anchor map's `grip_pose` selects between them per frame, and
  `CHARACTER_COMPOSITING.md` §4 requires the `attack` row to land on exactly the frame
  `ANIMATION_TIMING.md` §3 fixes as the hit-frame. Generate the full row set or the strike
  desyncs from the damage signal.

#### 2.2.1 The candidate-grid economy

`create_1_direction_object` returns a **grid of candidates in one call**, and the count is set by
the *effective* size — smaller size, more candidates. That makes it the cheapest route to a
variant family (the hair, hat and weapon counts in `CHARACTER_COMPOSITING.md` §9). Two facts
govern it, and they conflict:

- `size` and `style_images` are **mutually exclusive**. Passing both is a rejected call.
- When `style_images` is present it sets the output size — so the *reference's* dimensions decide
  the candidate count, not your intent.

So there are two recipes, not one, and the first cannot carry palette:

```
# Bootstrap — no approved sibling exists yet. Maximum candidates, zero style control.
create_1_direction_object(
  description       = <§1.2 template + part-only clause>,
  item_descriptions = [<one per candidate, length <= the count derived from size>],
  view              = "sidescroller",        # NOT "side" — this tool's enum differs (§1.1)
  size              = <small enough for the candidate count you want>,
)

# Follow-on — carries palette from an approved sibling. Candidate count follows the reference.
create_1_direction_object(
  description       = <§1.2 template + part-only clause>,
  item_descriptions = [<one per candidate>],
  view              = "sidescroller",
  style_images      = [<QA-passed sibling part — its size sets the grid; a large
                        reference collapses the grid toward a single candidate>],
)
→ get_object(object_id)                            # candidates land in `review` status
→ select_object_frames(object_id, indices=[...])   # each kept index becomes its own object
→ dismiss_review(object_id)                        # if none are worth keeping
```

- **This tool accepts no `outline`, `shading`, `detail` or `text_guidance_scale`.** `style_images`
  is its sole style control — which makes a QA-passed sibling mandatory for any part that must
  match, not optional. The bootstrap recipe has no style enforcement whatsoever and leans entirely
  on QA.
- It is priced at the surface's high end regardless of how many candidates come back, so a call
  that yields many and a call that yields one cost the same. Route the spend through
  `ROLE_ART_QUARTERMASTER.md` first — and note its rubric tiers "small objects" cheaply, which
  this tool is not (Open Questions).
- §2.2's scale blocker applies here too — the floor is the same.

### 2.3 Animated parts — `body`, `legs`, `boots`, `gloves` ⚠ BLOCKED

(`base` is **not** in this set — it is generated by §2.1 and is unblocked.)

**No PixelLab primitive animates a part-only layer against an external skeleton.**
`animate_character` requires a `character_id` from `create_character`; a transparent shirt with no
body is not a character. `CHARACTER_COMPOSITING.md` §9's "pose-guided per-frame generation" names
an outcome no single parameter provides. This blocks the great majority of the player frame budget
in that doc's §9 table, so it is not papered over with a plausible-looking call.

Three candidate lanes, none blessed. The runbook's global wardrobe spike gate exists to decide
between them, and should now be read as deciding *this*:

- **Lane A — self-generate.** Author the animated equip parts per `ROLE_ART_QUARTERMASTER.md`'s
  Lane A contract, using the base body's frames as the pose guide. Zero PixelLab generations;
  carries `placeholder: true` until budget allows otherwise.
- **Lane B — dressed-and-differenced.** `create_character_state(character_id=<base body>,
  edit_description="wearing <the outfit>", use_color_palette_from_reference=true)` preserves the
  base body's identity and palette across rotations; animate that, then extract the part layer by
  differencing against the base body's matching frames. Costs a full frame set per outfit and
  needs a differencing step nothing owns yet. Note it also has no defined answer for `jump`/`fall`,
  whose base frames come from a *different* character (§3.2.1) and so cannot be differenced the
  same way.
- **Lane C — keyframe interpolation.** `animate_character` and `animate_object` accept
  `custom_start_frame_base64` + `end_frame_base64` in `v3` mode and animate *between* the supplied
  poses. That is pose-guided generation in the literal sense and is the closest primitive in the
  surface. Whether alignment survives — and whether a part-only layer can be made to satisfy the
  `character_id` requirement at all — is untested and cannot be tested without spending.

Whichever wins, the alignment invariant is unchanged and non-negotiable: layer N frame `walk_03`
must overdraw layer M frame `walk_03` with **zero offset math** (`CHARACTER_COMPOSITING.md` §1). A
part that cannot hold the base body's pose at a given frame is an invalid part.

---

## 3. Part 2 — Frame-by-frame animation

Spritesheets are never hand-laid. Frames ride the character's fixed skeleton via
`animate_character`, which is what prevents the shimmer and inter-frame morph that free per-frame
generation produces. States and counts are `ANIMATION_STATES.md` §5's player row and
`ART_BIBLE.yaml` `animation.frame_budgets`; fps and hit-frame are `ANIMATION_TIMING.md`'s; atlas
packing is `SPRITESHEET_SPEC.md`'s. None of those numbers are restated here.

### 3.1 The call

```
animate_character(
  character_id       = <from §2.1>,
  animation_name     = <one of the 12 ANIMATION_STATES.md §1 tokens — exact, never a synonym>,
  action_description = <movement/pose only, e.g. "walking"; no locations, no objects>,
  mode               = "v3",                  # REQUIRED — see §3.2
  directions         = [<§3.3 Open Question — the side-profile cardinal, unconfirmed>],
  frame_count        = <§3.2 — computed against ART_BIBLE animation.frame_budgets>,
  keep_first_frame   = false,                 # v3 only; load-bearing, see below
)
```

- **`keep_first_frame: false` on every v3 call.** It defaults to `true`, which stores the input
  reference frame *in addition* to the generated ones. That is not just a count problem: the extra
  frame lands at index 0 and **shifts every subsequent index by one**, so the `hit_frame` recorded
  per `ANIMATION_TIMING.md` §3 points one frame late and the strike image desyncs from the damage
  signal (`CHARACTER_COMPOSITING.md` §4's `grip_pose` law). It also breaks
  `SPRITESHEET_SPEC.md` §2.2's column-index-equals-frame-index invariant. The parameter is
  **rejected** by `template` and `pro` modes, which manage frame storage themselves.
- `animation_name` must be the exact state token (`ANIMATION_STATES.md` §6 — "never an
  abbreviation or synonym"; `SPRITESHEET_SPEC.md` §7.2 requires the manifest's `states` keys to
  match). **No validator check covers this** — `docs/VALIDATION.md` check 6 validates a content
  file's `animation_states` field, not a clip name, and does not cover the player at all. It is a
  QA-gate responsibility.
- `action_description` carries movement only, per the tool's own contract. The style spine (§1.2)
  lives on `create_character`; re-injecting it here does nothing.
- **`mode: "template"` does not save money.** Its cost matches `v3` at every `size_class` in
  `ART_BIBLE.yaml` `sizing.size_classes`, so the only reason to choose it is frame count — and
  several template ids publish theirs in the identifier (`walking-6-frames`, `walking-8-frames`,
  `running-4-frames`, `fight-stance-idle-8-frames`, …). Where a published count falls inside a
  state's budget, template mode is a legitimate alternative; where it does not, it is not.

### 3.2 Frame count, and the `pro`-mode precondition ⚠

**`frame_count` is honored in `v3` mode only.** In `pro` mode it is *ignored* and replaced by a
constant derived from character size; in `template` mode the template's own count applies. So:

> **`pro` mode is forbidden for any entity carrying a locked frame budget** — which is every
> player and monster asset in the tree. It silently returns a size-derived frame count that no
> `ART_BIBLE.yaml` `animation.frame_budgets` range can accommodate, and nothing downstream catches
> it: `ART_GENERATION_RUNBOOK.md` §5's QA lines do not check frame count, and
> `SPRITESHEET_SPEC.md`'s own Open Questions confirm `docs/VALIDATION.md` has no atlas-manifest
> check. This constraint overrides `ROLE_ART_QUARTERMASTER.md`'s quality ladder, whose retry rule
> escalates *toward* `pro` after a QA rejection.

Within `v3`, the reachable counts are not free choice. The rule, computed at call time rather than
tabulated here (the budgets are locked values this doc must not fork):

```
reachable(state) = ART_BIBLE.animation.frame_budgets[state]  ∩  { even integers 4..16 }
```

Applying it to `ANIMATION_STATES.md` §5's player row yields three states whose intersection is
**empty** — `jump`, `fall`, and `hit` cannot be generated by `animate_character` at all. Two other
states admit exactly one legal value, silently pinning them to one end of a locked range (Open
Questions). The remaining four are unconstrained within their budget.

#### 3.2.1 `jump` / `fall` — held poses, not clips

`ANIMATION_STATES.md` §1.1 already states that at these states' locked budget "play through once"
and "hold a pose" are functionally the same thing, and `ANIMATION_TIMING.md` §1 blesses the
single-frame case explicitly. A held pose is a **still**, so the correct primitive is not
`animate_character`:

```
create_character_state(
  character_id     = <base body>,
  edit_description = "<the jump rise pose | the descent pose>",
  use_color_palette_from_reference = true,
)
```

…then take the side-facing rotation as the state's frame. This follows `ANIMATION_STATES.md` §1.1
rather than working around it. Two consequences the operator must carry, neither resolved:

- It collapses a locked range to its low end, the same narrowing flagged for the pinned states
  above.
- The frames come from a **different `character_id`**, so `CHARACTER_COMPOSITING.md` §1's
  zero-offset invariant is not guaranteed at these frames — `create_character_state` preserves
  *identity*, which is not pixel-exact skeleton alignment. The anchor map therefore has two
  authoring passes against two different entities (§3.4).

#### 3.2.2 `hit` — a genuine gap

`hit`'s budget maximum sits below `frame_count`'s floor, and is odd besides. Unlike jump/fall it is
a real flinch clip, not a held pose. Generating outside a locked `ART_BIBLE.yaml` budget is not
authorized by any doc, and trimming a generated clip back into range costs a beat of the motion
read. **Open Question**, flagged for `ROLE_ART_DIRECTOR` — a `frame_budgets.hit` amendment (`AB-`)
and an authorized trim rule are both plausible; neither is invented here.

### 3.3 One facing

`CHARACTER_COMPOSITING.md` §1 fixes facing as a horizontal flip of the whole stack, never
per-layer, with anchors mirroring by that doc's own formula (cited, not restated — and see Open
Questions, which flags an off-by-one ambiguity in it). Exactly one profile facing is generated and
the engine mirrors it. `animate_character` in `v3` mode defaults to a single non-side rotation, so
`directions` is always passed explicitly. **Which cardinal corresponds to the side profile under
`view: "side"` is unconfirmed** — it is an Open Question, and §3.1 carries a placeholder rather
than a guess, because a wrong cardinal generates a full state set in the wrong rotation without
erroring.

### 3.4 Generation order

Per `CHARACTER_COMPOSITING.md` §9, and it is an order, not a preference. The anchor map is the
hinge: it records, **per state per frame**, where each anchored layer attaches — so it cannot be
authored until the frames exist, and `create_character` alone returns only static rotations.

1. `create_character` → `style_base_00` (§2.1) → QA.
2. `animate_character` (§3.1) for every state whose count is reachable in `v3` (§3.2).
3. `create_character_state` (§3.2.1) for `jump` / `fall`.
4. **Now** author the anchor map by inspecting the frames from steps 2–3
   (`CHARACTER_COMPOSITING.md` §4) — a few dozen coordinate pairs, zero generated art, two source
   entities. Every later part depends on it.
5. Anchored parts (§2.2) — blocked, see §0.1(4).
6. Animated equip parts (§2.3) — blocked, lane undecided.
7. Pack to atlases per `SPRITESHEET_SPEC.md` §2. That contract is complete; this doc adds nothing.

Monsters, NPCs and bosses are **not** composited — they are single entities, generated per §4.6 and
animated with the same §3.1 call against their own required state set (`ANIMATION_STATES.md` §5).

---

## 4. Part 3 — Environment

AB-001 splits the environment in two, and the split decides the tool.

### 4.1 BUILT structures → seamless tileset

Towns, interiors, dungeon brickwork, platform props — everything AB-001 leaves on the tile grid.

```
create_sidescroller_tileset(
  lower_description      = <the platform/center material>,
  transition_description = <the surface/top layer>,
  transition_size        = <the tool's none | light | heavy steps>,
  tile_size              = {"width":  <ART_BIBLE environment.tile_grid_px>,
                            "height": <ART_BIBLE environment.tile_grid_px>},
  outline                = "selective outline",
  shading                = <§1.1 Open Question>,
  detail                 = <§1.1 Open Question — this tool's enum spelling differs>,
  base_tile_id           = <the previous QA-passed tileset's base tile id, when chaining>,
  seed                   = <recorded per §5.2 step 7>,
)
```

- Purpose-built for the job: side-view, transparent background, flat platform surfaces, seamless —
  satisfying `ART_BIBLE.yaml` `environment.seamless` for exactly the category AB-001 leaves
  seamless.
- The two material descriptions are sourced from
  `ART_BIBLE.yaml` `environment.biome_identity[<region>].motif`, cited per region.
- **Chain within a region.** Generate the region's first tileset, read its base tile id from
  `get_sidescroller_tileset`, then pass it as `base_tile_id` on the next. This is the mechanism
  holding a region's look together across tilesets, and it partially compensates for §0.1(2)'s
  missing palette lock.
- `detail` here must not silently exceed what characters get — `ART_BIBLE.yaml`
  `readability.contrast` requires characters to read *above* tiles, so a maximum-detail background
  under a medium-detail character inverts the rule. The gate sets both together.

### 4.2 ORGANIC ground → hand-painted terrain chunks, NOT tiles

AB-001 is explicit: organic ground is **not** built from seamless tiles. It is hand-painted
`terrain_chunk` art snapped to `foothold` segments of arbitrary angle (`MAP_TRAVERSAL.md`, which
also keeps the tile grid as the measurement lens). Generating a chunk as a tileset would contradict
a landed amendment.

```
create_map_object(
  description = <§1.2 template; subject = a ground chunk reading as a continuous slope/ledge;
                 motif = ART_BIBLE environment.biome_identity[<region>].motif>,
  view        = "side",
  width  = <chunk span>, height = <chunk depth>,     # basic mode: up to the tool's 400 px cap
  outline     = "selective outline",
  shading     = <§1.1 Open Question>,
  detail      = <§1.1 Open Question>,
)
```

QA is `ART_GENERATION_RUNBOOK.md` §5 line 4 — the chunk must snap to its briefed foothold segment
with no visible seam or floating edge. Chunks generate **first** in a region (that runbook's §3
order), because every other class's ground-relative framing is judged against them.

### 4.3 Static set-pieces

Buildings, portals, NPC stalls, ropes, ladders, reactors — `create_map_object` at `view: "side"`,
same spine. Behavior-carrying set-pieces take their visual tell from `ART_BIBLE.yaml`
`interactables`, cited by key.

### 4.4 Parallax layers ⚠

`ART_BIBLE.yaml` `environment.depth_layers` orders the bands and states the treatment. Generate
each band as its own `create_map_object` at `view: "side"`, and apply the desaturation/darkening as
a post-pass against the ramp — it is a palette operation, and per §0.1(2) no parameter performs it.

**Horizontal looping is unsolved.** `create_map_object` caps below the render width in
`ART_BIBLE.yaml` `pixel.resolution_policy`, and nothing in its contract makes output seamless —
that guarantee lives only on the tileset tools. A band that does not wrap shows a seam on every
scroll cycle, and `ART_GENERATION_RUNBOOK.md` §5 has no QA line for parallax. Open Question.

### 4.5 Style matching against an existing scene

`create_map_object` accepts a `background_image` plus an `inpainting` config (`oval` / `rectangle`
/ `mask`; mask convention **white = generate, black = preserve**). When a prop must sit inside an
already-approved scene, this matches its art style and auto-detects dimensions — the fourth palette
lever in §0.1(2)'s table. **This mode caps at 192×192**, well below basic mode's ceiling. It needs
an approved scene first, so it is a second-and-later-prop tool.

### 4.6 Monsters, NPCs, bosses

`create_character` per §2.1's shape, with:

- `size` = the entity's `ART_BIBLE.yaml` `sizing.size_classes` value;
- `body_type: "quadruped"` + `template` (`bear`/`cat`/`dog`/`horse`/`lion`) for four-legged mobs —
  humanoid `proportions` are ignored for these;
- the required state set from `ANIMATION_STATES.md` §5 driving §3.1's calls, including `telegraph`
  for elites/bosses and `phase_shift` for bosses;
- §3.2's `pro`-mode prohibition applies in full — bosses are exactly the tier
  `ROLE_ART_QUARTERMASTER.md`'s rubric routes toward `pro`, and exactly the tier whose frame
  budgets `pro` would violate;
- ⚠ `telegraph` / `phase_shift` / `spawn` frame budgets are still **proposed, not blessed**
  (`ANIMATION_STATES.md` §2.2). `ART_GENERATION_RUNBOOK.md`'s Open Questions already bars
  batch-generating those three against the proposed numbers. This library inherits that bar.

---

## 5. Part 4 — Clean-pixel & export directives

### 5.1 What is already law (cited, not restated)

- **Prompt-side enforcement**: `ART_BIBLE.yaml` `pixellab_defaults.style_prompt_core`, reused
  verbatim per call (§1.2). Its companion `negatives` has no parameter to occupy — §0.1(3).
- **Import settings**: `ART_BIBLE.yaml` `export_contract.godot_import`, bound to a concrete named
  Godot preset by `SPRITESHEET_SPEC.md` §8.
- **Hard prohibitions**: `ART_BIBLE.yaml` `export_contract.forbidden`.
- **Atlas / naming / pivot**: `ART_BIBLE.yaml` `export_contract.atlas`, `frame_naming` and
  `pivot_export`, made concrete by `SPRITESHEET_SPEC.md` §2–§7.
- **QA gate and rejection loop**: `ART_GENERATION_RUNBOOK.md` §5, including its two-attempt bound
  before escalation.

### 5.2 What the export contract does **not** state — steps this library adds

Each exists because of a verified property of the generator. Nothing below overrides §5.1.

1. **Crop to content box and register the pivot.** PixelLab returns a canvas larger than the
   requested character size (§0.1(4)). Every frame is cropped to its `SPRITESHEET_SPEC.md` §4
   content box and positioned so the feet-contact line sits on §5's pivot row for that
   `size_class`. Cropping to the *sprite's* bounding box instead is the classic failure — it makes
   the character bob between states, the float/sink that `ART_BIBLE.yaml` `sizing.pivot`'s
   HARD-RULE comment exists to prevent. Crop to the **content box**, then place the art inside it.
2. **Indexed palette remap.** Because no palette parameter exists (§0.1(2)), every accepted asset
   is remapped to `ART_BIBLE.yaml` `palette` ramps at import — the same build-step mechanism
   `CHARACTER_COMPOSITING.md` §5/§10 specifies for skin and hair swatches. A remap that cannot land
   on-ramp without visible damage is a **QA reject**, not a remap to force.
3. **Frame reconciliation.** Confirm the stored frame count equals the authored `frame_count`
   **and that frame 0 is a generated frame, not the retained reference pose** — a retained
   reference shifts every index by one and desyncs `hit_frame` from `grip_pose` (§3.1). A
   count-only check catches the first failure and misses the second.
4. **Download before expiry.** `create_map_object` results **auto-delete after 8 hours**. Anything
   from §2.2 or §4.2–§4.5 not retrieved inside that window is lost and must be regenerated at full
   cost. Whether the same clock runs on `create_1_direction_object` review objects is unstated by
   the schema — treat it as if it does (§5.2 step 6).
5. **Discard unused rotations.** `n_directions` has no `1`. Keep the profile facing, discard the
   rest, and never let a stray rotation reach the atlas — it would land as an off-pose frame in a
   state row. (They are discarded, not separately billed — §1.1.)
6. **Resolve `review` status.** `create_1_direction_object` leaves candidate grids in `review`.
   Close every one with `select_object_frames` or `dismiss_review` before the batch ends — an
   unresolved grid strands the call's full cost.
7. **Record `seed` and tool-surface date** in the per-job ledger `ART_GENERATION_RUNBOOK.md` §6
   owns, so a rejected asset re-rolls deterministically and every call is traceable to the schema
   revision it was written against.

### 5.3 What this library does not enforce

Cost, budget bands, lane routing, and the pre-call `get_balance` are `ROLE_ART_QUARTERMASTER.md`'s
in full. Batch order, region sequence, the exemplar and spike gates, and credential handling are
`ART_GENERATION_RUNBOOK.md`'s in full. A recipe here is only legal to execute once both have
cleared it.

One note that belongs to neither: **`get_balance` is also the authorization probe.** It is
authenticated, takes no arguments, and costs nothing, so the batch-opening balance check doubles as
proof the connector is authorized — letting `ART_GENERATION_RUNBOOK.md` §2's halt rule fire before
the exemplar spend rather than after it.

Several tools this library depends on are **unpriced** in `ROLE_ART_QUARTERMASTER.md`'s cost table
— see Open Questions. Until they are, follow that doc's own measure-on-first-use rule: price the
first call by balance delta and record it before any bulk run.

### 5.4 UI — proposals only

`UI_ART_SPEC.md` is locked and reached only through its `UA-` amendment channel. Two verified
collisions are recorded as **proposals for that channel**, not recipes:

- `create_ui_asset` produces a whole panel at a minimum size far above icon scale, aspect-gated,
  with no 9-slice output and no patch-margin parameter — its `pieces` field accepts only
  rounded-rect / circle / polygon. `UI_ART_SPEC.md` requires 3×3 nine-slice frames on its own
  `base_tile_px` / `corner_px` / `patch_margins` geometry. The tool cannot satisfy that contract
  directly; a slicing post-pass would have to. (That no 9-slice metadata is *returned* is
  consistent with the schema but not positively verifiable from it.)
- `create_font`'s `glyph_px` enum offers only four sizes. Cross-checked against `UI_ART_SPEC.md`'s
  text styles, **only one of its six styles** has a reachable glyph size. Its own Open Question
  ("original vs licensed pixel font") is upstream of this and unresolved.

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

**Blockers — no bulk generation against these until resolved**

- **Anchored parts have no working scale (§0.1(4), §2.2).** `create_map_object` and
  `create_1_direction_object` both floor at a 32 px canvas the subject fills, but an anchored part
  must occupy a fraction of `ART_BIBLE.yaml` `sizing.player_frame`. Cropping relocates without
  rescaling, and `no_sub_pixel` plus `export_contract.forbidden` bar downscaling. Whether the part
  is prompted to sit small-in-frame, generated against a scaled-up base body, or routed to Lane A
  is undecided. Blocks five of ten layers. Flagged for `ROLE_ART_DIRECTOR`.
- **Animated equip parts have no direct primitive (§2.3).** `animate_character` needs a
  `character_id`, not a part-only layer. Lanes A / B / C are all untested; Lane C
  (`custom_start_frame_base64` + `end_frame_base64`) is the closest thing in the surface and has
  never been tried. Decide at the global wardrobe spike gate.
- **`hit` cannot be generated inside its frame budget (§3.2.2).** Needs either an `AB-` budget
  amendment or an authorized trim rule.

**Unbound values — the gate must set these before the first batch**

- **`shading` and `detail` have no `ART_BIBLE` binding (§1.1).** Neither has a key that expresses
  a value, and the enums differ between the character/object tools and
  `create_sidescroller_tileset` (which also carries a fifth `shading` member). Two decisions, not
  one, and `readability.contrast` couples them — characters must read above tiles. This doc
  pre-narrows nothing.
- **Player body proportions are unfixed (§2.1).** A silhouette-identity decision
  (`ART_BIBLE.yaml` `readability.silhouette_first`), settled once for every humanoid asset — so it
  belongs to the **global wardrobe spike gate**, not a per-region exemplar gate.
- **Which cardinal is the side profile (§3.3).** Unverified; `v3` defaults to a non-side rotation.
  A wrong value generates a full state set in the wrong rotation without erroring.

**Contradictions and gaps in other docs**

- **The anchor mirror formula may be off by one (§3.3).** `CHARACTER_COMPOSITING.md` §1 gives one
  form; for **pixel indices** in `[0, cw-1]` the mirror is one less than that. That doc calls
  anchors pixels and gives pixel examples, while `SPRITESHEET_SPEC.md` §5 explicitly makes the
  *pivot* a boundary coordinate — two conventions, one formula. Head anchors sit at the horizontal
  center and mirror identically under both, so the error would show only on off-center anchors
  (weapon grip) — a 1 px jitter on every left-facing frame, with no validator check
  (`CHARACTER_COMPOSITING.md` already flags the missing anchor checks). Flagged for that doc's
  owner; this doc cites the rule rather than restating it.
- **The anchor-map example arity is unreachable (§3.4).** `CHARACTER_COMPOSITING.md` §4's manifest
  example shows per-state entry counts that §3.2's reachable set cannot produce. An operator
  copying the example's shape desyncs the anchor map from the generated frames. Flagged for that
  doc's owner.
- **Parallax has no seamless mechanism (§4.4).** No tool in the verified surface produces a
  horizontally-looping non-tiled band, and `ART_GENERATION_RUNBOOK.md` §5 has no QA line for the
  class. Either parallax needs a tiling post-pass or the band is composited/mirrored in-engine — a
  Phase E decision, not a generation-time one.
- **`pose_ref` is unreachable (§1.2).** AB-002 added it to `pixellab_defaults.per_asset_injects_only`
  as "base-body frames as pose guide", but no tool accepts a pose reference in the sense that inject
  means — the same class of gap as `negatives` (§0.1(3)). Both are flagged for `ROLE_ART_DIRECTOR`:
  either an `AB-` amendment restating them as QA criteria and lane-C inputs, or confirmation that
  they are advisory.
- **Locked ranges are silently narrowed (§3.2, §3.2.1).** Two states admit exactly one legal
  `frame_count`, and the jump/fall held-pose resolution collapses another range to its low end.
  Confirm that authoring at one end of a locked range is acceptable rather than a de-facto
  narrowing.
- **`ROLE_ART_QUARTERMASTER.md`'s cost table is incomplete for this library.** It prices neither
  `create_map_object` (this doc's most-used tool), nor `create_character_state` (load-bearing for
  jump/fall and Lane B), nor the tileset tools (its own flagged gap). Its `animate_character` v3
  bands are also stated against *character* size while the vendor formula uses *canvas* size, which
  §0.1(4) shows is ~40% larger — enough to shift a size class across a cost boundary. Its rubric
  additionally tiers "small objects" cheaply, which does not fit `create_1_direction_object`.
  Reconcile after the first measured batch; that role owns the file.
- ~~This doc proposes a ledger extension it does not own (§5.2 step 7).~~ **Resolved 2026-07-24:**
  `seed` and the tool-surface date landed in `ART_GENERATION_RUNBOOK.md` §6's per-job ledger by
  that doc's own edit — §5.2 step 7 now cites an existing requirement rather than proposing one.
- **`tool_surface_verified` will go stale.** Every enum, limit and default here was read from the
  live MCP on the date in §0. PixelLab ships changes; re-read the schemas at the start of any batch
  and correct this doc before executing a recipe against them.
