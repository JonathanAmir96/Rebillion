# ART_GENERATION_RUNBOOK.md — Operating the Future PixelLab Art-Generation Pass

References: docs/00_vision/GLOSSARY.md, docs/VALIDATION.md, docs/40_assets/ART_BIBLE.yaml,
docs/40_assets/UI_ART_SPEC.md, docs/40_assets/SPRITESHEET_SPEC.md,
docs/40_assets/CHARACTER_COMPOSITING.md, docs/40_assets/PIXELLAB_PROMPT_LIBRARY.md,
docs/40_assets/ANIMATION_STATES.md, docs/40_assets/ANIMATION_TIMING.md,
docs/15_maps_system/MAP_TRAVERSAL.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md,
docs/60_agents/roles/ORG.md, docs/60_agents/roles/ROLE_ART_DIRECTOR.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md, docs/70_integrations/BUILD_DISTRIBUTION.md

Owner doc for **operating** the PixelLab MCP generation pass once Phase D content lands — batch
order, credential handling, brief sourcing, and the QA/rejection loop. It does not restate any
visual law: palette ramps, size classes, biome identity, and the AB-001 terrain model stay
`docs/40_assets/ART_BIBLE.yaml`'s (change-controlled); 9-slice/font/window geometry stays
`docs/40_assets/UI_ART_SPEC.md`'s (change-controlled); atlas/frame/pivot shape and hit-frame/fps law stay
`docs/40_assets/SPRITESHEET_SPEC.md` and `docs/40_assets/ANIMATION_TIMING.md`'s. This doc only
sequences the work and gates it, per this role's runbook remit
(`docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`).

## 1. Scope and trigger

This pass **does not run during this design-doc generation run**. It is a future operational
phase, triggered only once Phase D (`50_content/*` YAML — maps, monsters, NPCs, items, skills)
has landed and passed `docs/VALIDATION.md` checks 1–6 for the region(s) in scope. Inputs are
strictly: the validated `50_content/*` YAML for those regions (source of entity IDs, `tier`,
`element`, `size_class`-implying stats, `animation_states`) and the locked `40_assets/*` specs
(the generation brief, §4). Outputs are generated sprite, tile, and UI assets that land in the
**future game project repo** (`docs/70_integrations/BUILD_DISTRIBUTION.md` §1) — they are never
committed to this design tree. This design repo's role in the pass ends at the brief; asset
binaries have no home here.

## 2. Credentials

PixelLab is reached exclusively through the PixelLab MCP tools, authorized as the **claude.ai
PixelLab connector** — the owner authenticates it interactively (`/mcp` → *claude.ai Pixellab
AI* → authorize) against their own claude.ai login. **No API token is consumed by any PixelLab
MCP tool** — verified 2026-07-24 across the whole tool surface, so there is none to hold: not in
the repo, not in an environment variable, not in Claude Code settings
(verified 2026-07-24 against the live MCP; the `PIXELLAB_SECRET` env-var plan this section
previously described was a forward guess that never materialized). Rules, no exceptions:

- **Never ask the owner to paste a PixelLab token**, and never accept one if offered — there is
  no field that consumes it, so a pasted token is pure exposure with zero benefit. If a token
  reaches a transcript, treat it as leaked (final rule below).
- No credential value is **ever** committed to this repo, pasted into a doc, a commit message, a
  log line, a generation prompt, or a chat transcript that could be persisted as an artifact.
  This survives the auth-model change unchanged — it now covers the connector's OAuth
  credentials rather than an API key.
- **If the connector is not authorized, or the MCP tools reject the session**, the runbook halts
  before any generation call — no batch starts, no exemplar is requested. Ask the owner to
  re-authorize via `/mcp`; escalate on the
  `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md` path if that fails. Never substitute a
  hardcoded value or a placeholder credential to "keep moving."
- **The batch-opening `get_balance` is the authorization check** — it is authenticated, takes no
  arguments, and costs nothing, so the balance reading
  `docs/60_agents/roles/ROLE_ART_QUARTERMASTER.md`'s protocol already requires at the start of
  every batch doubles as proof the connector is live. Run it before the exemplar, so the halt rule
  above fires ahead of any spend rather than after a failed generation call.
- **`list_projects` returns git clone URLs that may embed a push credential.** Never paste its raw
  output into a doc, a batch run log (§6), a commit message, or anywhere else persisted — the
  no-credential-in-artifacts rule above covers it, and this is the one read-only call that can
  produce a live credential as ordinary output.
- **Revocation on suspicion of exposure**: if the connector authorization is ever suspected
  compromised, stop the pass immediately, notify the owner, and do not resume generation until
  the owner has revoked and re-authorized the connector. **Note the blast radius**: the connector
  grant sits downstream of the owner's whole claude.ai login, not a vendor-scoped key. If the
  login itself is what is suspected, revoking the connector is *not* sufficient remediation — the
  owner rotates claude.ai credentials and invalidates active sessions first, then re-authorizes;
  otherwise an attacker holding a live session satisfies the resume condition as easily as the
  owner does.

## 3. Batch order — region-scoped, exemplar-first

Generation follows the same region-scoped, exemplar-first, validator-gated discipline the content
phases already use (`docs/phase_reports/PHASE_A_REPORT.md`, `PHASE_B_REPORT.md`): nothing bulk-
generates before a small, representative sample has cleared QA.

**Region order** follows `docs/WORLD_PLAN.md`'s numbering exactly — Emberfoot Isle (`emberfoot`,
R1) first (it is the training island; its assets set the palette/silhouette baseline before
anything harder), then Millbrook, Verdant, Tidewatch, Gloomwood, Ashfall, Sunken, Clockwork,
Frostpeak Isle (R9), Arcane Reach (R10), Voidshore (R11) in that order. A later region never
generates ahead of an earlier one still failing QA.

**Global batch — the composited player wardrobe** runs once, before R1's monster batch (the
player is on screen everywhere): per-part generation per
`docs/40_assets/CHARACTER_COMPOSITING.md` §9 — its spike gate first (base body + 1 outfit +
2 hairs to validate pose-guided part alignment), then the arc-1 wardrobe — exported per
`docs/40_assets/SPRITESHEET_SPEC.md`'s Player exception (part ID in the `{entity_id}` position).

**Within one region**, asset classes run in this order:

1. **Terrain chunks** (AB-001 hand-painted ground art) — first, because every other class's
   ground-relative framing (pivot, scale read) is judged against them.
2. **Structure tilesets** (towns, interiors, dungeon brickwork, platform props — the 16px-grid
   built environment AB-001 leaves unchanged).
3. **Monsters** (`mob_NNN`, normals → elites → boss, in that tier order).
4. **NPCs** (`npc_NNN`).
5. **Items and icons** (equipment, use/etc icons, drop-visual sprites).
6. **UI** — last, and only once per the whole project, not once per region: UI is a shared
   global system (`docs/40_assets/UI_ART_SPEC.md`), so it exemplar-and-bulk-generates on its own
   schedule after enough regions exist to exercise every rarity/element color it must carry
   (rather than per-region reruns).

**The exemplar gate, per asset class per region:** generate exactly one representative asset (one
terrain chunk, one normal-tier monster, etc.), submit it to the ROLE_ART_DIRECTOR QA gate (§5).
Only a **pass** verdict opens the bulk run for the rest of that class in that region. A **reject**
sends the brief back for correction (§5) before a second exemplar attempt — bulk never starts on
a rejected exemplar's brief.

## 4. Brief-template mapping

Every generation job cites exactly one `40_assets/*` doc as its brief and QA contract; this doc
mints no new visual rules, only points at the owner. **The concrete call for every row below —
tool, parameters, and `description` shape — is `docs/40_assets/PIXELLAB_PROMPT_LIBRARY.md`**;
that doc also records which recipes are currently blocked and must not be batch-generated.

| Asset type | Generation brief / QA contract (owner, cited not restated) |
|---|---|
| Character, monster, NPC sprites (all states) | `40_assets/SPRITESHEET_SPEC.md` (atlas/frame/pivot shape) + `40_assets/ANIMATION_STATES.md` (required state set per entity class, §5 there) + `40_assets/ANIMATION_TIMING.md` (fps/hit-frame law, informs frame count choice) + `40_assets/ART_BIBLE.yaml` `sizing`/`palette`/`shading` (size class, ramp, cel-shading) |
| Terrain chunks | `40_assets/ART_BIBLE.yaml` amendment `AB-001` (hand-painted, foothold-snapped ground art) + `15_maps_system/MAP_TRAVERSAL.md` (the foothold segments/gap budgets the chunk art must visually read against — arbitrary angles, no seamless-tile assumption) |
| Structure tilesets (towns/interiors/dungeon brickwork/props) | `40_assets/ART_BIBLE.yaml` `environment.tile_grid_px` + `AB-001`'s carve-out that the 16px grid still governs these |
| UI (frames, buttons, windows, tags, cursor, guild-crest parts) | `40_assets/UI_ART_SPEC.md` (9-slice geometry, font, color roles, naming) |
| Items / icons | `40_assets/ART_BIBLE.yaml` `rarity_code` (ring/tint colors) + `40_assets/UI_ART_SPEC.md` icon-grid rules (16/24/32px, single motif) |
| Projectiles / fx | No dedicated brief exists yet in `40_assets/*` — generate against `40_assets/ART_BIBLE.yaml`'s general `pixel`/`palette`/`shading` rules only, and flag the gap (Open Questions) rather than improvising a brief. |

`ART_BIBLE.yaml`'s `pixellab_defaults` (`style_prompt_core`, `negatives`,
`per_asset_injects_only`) is the shared prompt scaffold underneath every row above — each brief
injects only its own silhouette/palette-accent/motif/size-class/state-list, never rewrites the
core style prompt.

## 5. QA checklist (ROLE_ART_DIRECTOR gate)

Every generated asset, exemplar or bulk, is checked against all of the following before it is
accepted. Any single failure is a reject, never a "close enough" pass
(`docs/60_agents/roles/ROLE_ART_DIRECTOR.md` Definition of done):

1. **Palette-ramp conformance** — the asset's dominant ramp matches its `biome_identity` (terrain,
   tilesets) or its declared element/rarity accent (monsters, items); no off-palette color without
   a landed `AB-NNN` amendment.
2. **Size-class silhouette** — content-box dimensions match the entity's `size_class`, pivot sits
   at feet-center, and the asset reads correctly in solid-black silhouette.
3. **Required animation states present** — the exported state set matches
   `40_assets/ANIMATION_STATES.md` §5's required set for the entity's class; elites and bosses
   include `telegraph` (`docs/VALIDATION.md` §6); bosses additionally include `phase_shift`.
4. **Terrain-chunk foothold fit** — a terrain chunk snaps cleanly to the foothold segment(s) it
   was briefed against (arbitrary angle, per `AB-001`/`MAP_TRAVERSAL.md`), with no visible seam or
   floating edge at the snap points.
5. **Export contract conformance** — PNG RGBA, transparent background, correct atlas padding/
   extrusion, and frame naming exactly matching `{entity_id}_{state}_{NN}`.

**Rejection loop:** a failing asset is regenerated against the same brief with a corrected
prompt injection first. If a second attempt fails for the same reason, that is treated as a brief
or spec gap, not a generator problem — escalate to ROLE_ART_DIRECTOR's amendment channel
(`ART_BIBLE.yaml` `amendments[]`) or Open-Questions channel (`UI_ART_SPEC.md`). **Locked files are
never edited directly** by this pass or by this role, regardless of how clear the fix seems —
only their owner's channel may land a change.

## 6. Bookkeeping

**Naming/manifest.** Every generated asset ties back to its content ID through
`ART_BIBLE.yaml`'s `export_contract.frame_naming` (`{entity_id}_{state}_{NN}`) and, for animated
entities, the atlas manifest sidecar (`40_assets/SPRITESHEET_SPEC.md` §7, `<entity_id>.atlas.yaml`
beside `<entity_id>.png`). `entity_id` is always the entity's own registered ID
(`mob_NNN`/`npc_NNN`/`item_equip_NNNN`/etc. per `docs/ID_REGISTRY.md`) — no ad hoc naming. A batch
run log records, per job: content ID, brief doc + version cited, PixelLab job ID, the QA
verdict (§5), and — where the tool accepts one — the `seed` plus the tool-surface verification date
from `40_assets/PIXELLAB_PROMPT_LIBRARY.md` §0, so a rejected asset can be re-rolled
deterministically against a corrected prompt and anyone can tell which schema revision a call was
written against. Enough for anyone to trace a shipped asset back to the exact brief it was generated
against.

**Failure modes and retry stance:**

| Failure | Response |
|---|---|
| Generation quota / rate limit exhausted | Pause the batch at the current asset; resume in the next available window. Never fall back to a manual, QA-bypassing asset to "unblock" the batch. |
| Generation drift (output ignores palette/silhouette/state brief after 2 regeneration attempts) | Stop retrying; escalate per §5's rejection loop — this is a brief/spec question, not a prompt-tuning one. |
| MCP/service outage | Halt the batch entirely; retry once the service is confirmed healthy. No partial-batch "best effort" landing. |
| Connector unauthorized or session rejected — at batch start **or** mid-batch | Halt immediately per §2; do not continue on cached/previously-successful auth state. The start-of-batch case is caught by §2's `get_balance` probe before any spend; the mid-batch case surfaces on a failing call. |

Bounded retries only (2 regeneration attempts per asset before escalation, per §5); an asset is
never shipped "close enough" to a failed checklist line.

## Open Questions

- **Frames→atlas packing tool ownership is unassigned** (`40_assets/SPRITESHEET_SPEC.md` Open
  Questions): whether this runbook's "bulk" stage includes atlas packing, or only raw named-frame
  export with packing left to a later Phase E tool, is not settled here.
- **`telegraph`/`phase_shift`/`spawn` frame budgets are still a proposal**, not landed in
  `ART_BIBLE.yaml amendments[]` (`40_assets/ANIMATION_STATES.md` §2.2). This runbook should not
  batch-generate those three states against the proposed numbers until Agent-3 blesses them.
- **No brief exists yet for projectiles/fx** (§4's last row) — flagged for
  `docs/60_agents/roles/ROLE_ART_DIRECTOR.md` to either author a dedicated spec or confirm the
  general `ART_BIBLE.yaml` rules suffice.
- **Headless/scheduled runs may have no connector (§2).** The claude.ai PixelLab connector is
  authorized interactively against the owner's login; an unattended run (cron, CI, a background
  agent) may find the MCP absent, and there is no token fallback to substitute. Whether the art
  pass is therefore attended-only, or needs a separate unattended credential path from PixelLab,
  is unresolved — flagged for `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`. Until settled,
  treat every batch as attended and let §2's halt rule fire rather than seeking a workaround.
- **PixelLab job concurrency/credit-cost model** is unknown at doc-authoring time (no owner
  pricing data was available for this task); regional batch sizing may need revisiting once real
  quota/cost figures are known.
- **Destination path in the future game project repo** for generated assets (exact `assets/`
  mount point relative to that repo's root) is `docs/70_integrations/BUILD_DISTRIBUTION.md`'s
  concern once that repo exists; not fixed here.
- **UI's "enough regions exist" trigger (§3)** — the exact region-count threshold before the
  global UI batch starts is not fixed; default is after Emberfoot + Millbrook (enough rarity/
  element variety to exercise the icon/rarity-ring rules) but this is a first-pass guess, not a
  rule.
