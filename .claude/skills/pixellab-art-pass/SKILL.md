---
name: pixellab-art-pass
description: Use when generating any game art for Rebillion through the PixelLab MCP — sprites, monsters, NPCs, terrain chunks, tilesets, set-pieces, parallax, or player paper-doll parts. Also use when asked to run an art batch, pick PixelLab parameters, write a generation prompt, or QA a generated asset.
---

# Rebillion art pass (PixelLab MCP)

Generating art here is gated. Three docs must clear a call before it is sent, and they are not
interchangeable. Read them in this order — do not start from memory, the tool surface changes.

1. `docs/40_assets/PIXELLAB_PROMPT_LIBRARY.md` — **which tool, which parameters, which
   description shape.** Start here; every recipe is in it.
2. `docs/70_integrations/ART_GENERATION_RUNBOOK.md` — batch order, region sequence, exemplar and
   spike gates, credentials, QA/rejection loop.
3. `docs/60_agents/roles/ROLE_ART_QUARTERMASTER.md` — cost, budget band, Lane A vs Lane B.

The visual law itself is `docs/40_assets/ART_BIBLE.yaml` (locked), plus `SPRITESHEET_SPEC.md`,
`ANIMATION_STATES.md`, `ANIMATION_TIMING.md`, `CHARACTER_COMPOSITING.md`. Cite by key; never
restate a value; never edit a change-controlled file (`CLAUDE.md` Law 5).

## Before the first call

- **`get_balance` first — it is both the auth check and the budget check.** It is authenticated,
  takes no arguments, and costs nothing. If it fails, the connector is not authorized: stop and
  ask the owner to re-authorize via `/mcp` (RUNBOOK §2). Never work around it.
- **Connector, not a token.** PixelLab authorizes through the owner's claude.ai login. Never ask
  for or accept a pasted token — no tool consumes one, and the only fields that would take the
  string ship it to a third party and persist it there.
- **Re-read the live MCP schemas.** The library's §0 says when its enums and limits were last
  verified. If PixelLab has shipped changes since, correct the library first, then generate.
- **`view: "side"` on everything, always explicit.** Every tool in the surface defaults to a
  top-down angle, and every `outline` defaults to a non-selective mode — omitting either silently
  produces a rejected asset. Watch the spelling: `create_1_direction_object` says
  `"sidescroller"`, everything else says `"side"`.
- **Never name an IP in a prompt.** `ART_BIBLE.yaml` `identity.anti_goals` locks "must NOT clone
  any existing IP". The Maple-style lineage is expressed through parameters and genre vocabulary —
  library §1.2.1. A description with a franchise name is rejected before it is sent.

## Never use `pro` mode on an animation

`animate_character` in `pro` mode **ignores `frame_count`** and substitutes a size-derived
constant, which no `ART_BIBLE.yaml` `animation.frame_budgets` range can accommodate. Nothing
downstream catches it — the runbook's QA lines do not check frame count and `VALIDATION.md` has no
atlas-manifest check, so it surfaces in Phase E as wrong clip lengths and `hit_frame` indices
pointing into clips that no longer have that shape.

This overrides the quartermaster's quality ladder, which escalates *toward* `pro` after a QA
rejection. `v3` for every animation, every time.

## The traps that silently break output

Full detail in library §0.1 and §5.2.

1. **Canvas ≠ content box, both ways.** Output is larger than the requested character size — crop
   every frame to its `SPRITESHEET_SPEC.md` §4 content box and register the feet-contact line on
   §5's pivot row. Crop to the *content box*, not the sprite's bounding box, or the character bobs
   between states. The inverse case blocks anchored parts entirely (below).
2. **No palette parameter exists.** Conformance is a post-generation indexed remap plus QA, never
   a generation-time guarantee. Style params are soft; `shading` is ignored outright in `v3`/`pro`;
   `create_1_direction_object` has no style params at all.
3. **`keep_first_frame: false` on every v3 `animate_character` call.** It defaults true and stores
   the reference frame at index 0, shifting every later index by one — which desyncs `hit_frame`
   from the weapon's `grip_pose`, not just the atlas column count. Rejected by `template`/`pro`.
4. **`create_map_object` output auto-deletes after 8 hours.** Download inside the batch session.
5. **Close every `review`-status candidate grid** with `select_object_frames` or `dismiss_review`
   before the batch ends — an unresolved grid strands the call's full cost.
6. **Discard unused rotations** so no off-pose frame reaches the atlas, and **record the `seed`**
   so a rejected asset can be re-rolled deterministically.

## Blockers — stop and escalate, do not improvise

- **Anchored parts (`cape`/`face`/`hair`/`head`/`weapon`) are BLOCKED.** Both object tools floor at
  a 32px canvas the subject fills, but these must occupy a fraction of the player frame. Cropping
  can't rescale and downscaling is barred. Five of ten layers; do not bulk-generate.
- **Animated equip parts (`body`/`legs`/`boots`/`gloves`) are BLOCKED** — no primitive animates a
  part-only layer against an external skeleton. Three untested lanes; the global wardrobe spike
  gate decides.
- **`hit` cannot be generated inside its frame budget.** `jump`/`fall` resolve to held poses for
  the base body, but their anchor-map and animated-part consequences are still open.
- **`shading`, `detail`, player proportions, and the side-profile cardinal are unset.** All are
  gate decisions, recorded in the batch report when made. Do not pick one to keep moving.
- **`telegraph`/`phase_shift`/`spawn` frame budgets are proposed, not blessed.** Do not
  batch-generate those states.

**Unblocked today:** the base body (§2.1), its animations (§3), monsters/NPCs/bosses (§4.6),
built-structure tilesets (§4.1), terrain chunks (§4.2), and set-pieces (§4.3).

## Order of work

Base body → **animate it** → `create_character_state` for jump/fall → **then** author the anchor
map from those frames → anchored parts → animated parts → atlas packing. The anchor map records
per-state-per-frame positions, so it cannot be authored from `create_character`'s static rotations
— that ordering error will stall step 1 or produce guessed coordinates nothing validates.

Within a region: terrain chunks → structure tilesets → monsters → NPCs → items/icons. UI is global
and last, and goes through the `UA-` amendment channel, never authored ad hoc.

Exemplar gate per asset class per region: generate exactly one, pass QA, then bulk. A reject sends
the brief back — bulk never starts on a rejected exemplar. Two regeneration attempts, then
escalate; it is a spec question at that point, not a prompt-tuning one.
