---
name: pixellab-art-pass
description: Use when generating any game art for Rebillion through the PixelLab MCP — sprites, monsters, NPCs, terrain chunks, tilesets, set-pieces, parallax, or player paper-doll parts. Also use when asked to run an art batch, pick PixelLab parameters, write a generation prompt, or QA a generated asset.
---

# Rebillion art pass (PixelLab MCP)

Generating art here is gated. Three docs must clear a call before it is sent, and they are not
interchangeable. Read them in this order — do not start from memory, the tool surface changes.

1. `docs/40_assets/PIXELLAB_PROMPT_LIBRARY.md` — **which tool, which parameters, which
   description shape.** Start here; every recipe is in it.
2. `docs/70_integrations/ART_GENERATION_RUNBOOK.md` — batch order, region sequence, exemplar
   gate, credentials, QA/rejection loop.
3. `docs/60_agents/roles/ROLE_ART_QUARTERMASTER.md` — cost, budget band, Lane A vs Lane B.
   **`get_balance` before any generation call, every batch. No exceptions.**

The visual law itself is `docs/40_assets/ART_BIBLE.yaml` (locked), plus `SPRITESHEET_SPEC.md`,
`ANIMATION_STATES.md`, `ANIMATION_TIMING.md`, `CHARACTER_COMPOSITING.md`. Cite by key; never
restate a value; never edit a change-controlled file (`CLAUDE.md` Law 5).

## Before the first call

- **Re-read the live MCP schemas.** The library's `tool_surface_verified` front-matter date says
  when its enums and limits were last checked. If PixelLab has shipped changes since, correct the
  library first, then generate.
- **`view: "side"` on everything.** This is a side-scroller. A top-down asset is a rejected asset.
  Watch the enum traps: `create_1_direction_object` spells it `"sidescroller"`, `create_tiles_pro`
  uses `tile_view: "side"`, and the tileset tools spell detail `"highly detailed"` where
  `create_character` says `"high detail"`.
- **Never name an IP in a prompt.** `ART_BIBLE.yaml` `identity.anti_goals` locks "must NOT clone
  any existing IP". The Maple-style lineage is expressed through parameters and genre vocabulary —
  see the library §1.2.1. A description containing a franchise name is rejected before it is sent.

## The four things that silently break output

Each is verified against the live schema and each has bitten this pipeline by design, not by
accident. Full detail in the library's §0.1 and §5.2.

1. **Canvas ≠ content box.** `create_character` returns a canvas ~40% larger than `size`;
   `create_map_object` floors at 32px. Crop every frame to its `SPRITESHEET_SPEC.md` §4 content
   box and register the feet-contact line on §5's pivot row — crop to the *content box*, not the
   sprite's bounding box, or the character bobs between states.
2. **No palette parameter exists.** Palette conformance is a post-generation indexed remap plus
   QA, never a generation-time guarantee. Style params are soft; `shading` is ignored entirely in
   `v3`/`pro`.
3. **`keep_first_frame: false` on every `animate_character` call.** It defaults true and stores an
   extra reference frame, so `frame_count: 8` silently yields 9 and breaks the atlas
   column-equals-frame-index invariant.
4. **`create_map_object` output auto-deletes after 8 hours.** Download inside the batch session or
   pay to regenerate.

## Known blockers — do not improvise past these

These are open in the library and unresolved. If a task runs into one, stop and escalate to
`ROLE_ART_DIRECTOR` rather than picking a value:

- **Animated equip parts** (`body`/`legs`/`boots`/`gloves`) have no direct tool —
  `animate_character` cannot animate a part-only layer against an external skeleton. Lane
  undecided. The base body and anchored parts are unblocked; the wardrobe batch is not.
- **`hit` cannot be generated inside its frame budget** — `frame_count` accepts even 4–16 only,
  which does not intersect `animation.frame_budgets.hit`. `jump`/`fall` are resolved (held poses,
  library §3.2.1); `hit` is not.
- **`shading` has no ART_BIBLE binding**, **player proportions are unfixed**, and **which cardinal
  is the side profile is unverified** — all three are R1 exemplar-gate decisions, recorded in the
  batch report when made.
- **`telegraph`/`phase_shift`/`spawn` frame budgets are proposed, not blessed**
  (`ANIMATION_STATES.md` §2.2). Do not batch-generate those states.

## Order of work

Base body first — it defines the skeleton and the anchor map every other part is authored against.
Then anchored parts, then animated parts, then atlas packing. Within a region: terrain chunks →
structure tilesets → monsters → NPCs → items/icons. UI is global and last, and goes through the
`UA-` amendment channel, never authored ad hoc.

Exemplar gate per asset class per region: generate exactly one, pass QA, then bulk. A reject sends
the brief back — bulk never starts on a rejected exemplar. Two regeneration attempts, then
escalate; it is a spec question at that point, not a prompt-tuning one.
