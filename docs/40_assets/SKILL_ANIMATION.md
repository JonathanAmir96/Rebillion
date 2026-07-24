# SKILL_ANIMATION.md — Skill Animation Clip IDs, Naming & Skill Icons

References: 00_vision/GLOSSARY.md, 40_assets/ANIMATION_STATES.md, 40_assets/ANIMATION_TIMING.md,
40_assets/SPRITESHEET_SPEC.md, 40_assets/ART_BIBLE.yaml, 40_assets/UI_ART_SPEC.md,
40_assets/CHARACTER_COMPOSITING.md, 20_schemas/skill.schema.md, 10_systems/SKILL_SYSTEM.md,
10_systems/SKILL_EFFECTS.md, 10_systems/HUD.md, docs/ID_REGISTRY.md, docs/VALIDATION.md

Owner doc for the **per-skill animation clip ID namespace** — the ids
`20_schemas/skill.schema.md`'s `animation` field carries and `docs/VALIDATION.md` §6 checks —
and for the **skill icon id law** (§5), the parallel derived namespace binding every skill to
its `ui_icon_skill_*` asset (icon construction stays `40_assets/UI_ART_SPEC.md`'s, locked).
This namespace is distinct from the 12 shared body-state tokens
(`40_assets/ANIMATION_STATES.md`) and never redefines them: a skill's visuals are **fx clips
layered over the shared body states**, synced to `40_assets/ANIMATION_TIMING.md`'s timeline.
Frame/atlas packing for these clips follows `40_assets/SPRITESHEET_SPEC.md` unchanged.

## 1. The anchor id — `skill_<line>_NNN_cast`

Every **active** skill declares exactly one anchor clip id in its `animation` field:

```
skill_<line>_NNN_cast        # e.g. skill_bulwark_003_cast, skill_novice_001_cast
```

- `<line>_NNN` must equal the owning skill's own ID stem (`docs/ID_REGISTRY.md` Skills block;
  `skill_novice_NNN` included). The validator derives the expected anchor from the skill id —
  a mismatched stem fails `docs/VALIDATION.md` §6.
- **Passives declare no anchor** (`20_schemas/skill.schema.md`: `animation` optional/absent for
  passives); a passive may still own a `_proc` fx clip (§2).
- The anchor id is a deterministic function of its owning skill's already-registered `id`, not an
  independently allocated identifier, so it carries no `docs/ID_REGISTRY.md` block of its own —
  the same sidecar-to-an-already-registered-entity logic `40_assets/SPRITESHEET_SPEC.md` §7 applies
  to its atlas-manifest `id`. It inherits the skill id's immutability (`CLAUDE.md` law 3): renaming
  or renumbering a `skill_<line>_NNN` id renumbers its anchor in lockstep, in the same commit.

## 2. Derived clip suffixes (the multi-clip rule)

A skill needing more than one visual does **not** get a second `animation` field — further clips
derive from the anchor stem by fixed suffix. This resolves `20_schemas/skill.schema.md`'s
multi-clip open question with no schema change:

| Suffix | Clip | When it exists |
|---|---|---|
| `_cast` | The cast fx overlay, played over the body's `cast` (or `attack`) state | Every active — the anchor (§1) |
| `_proj` | Projectile flight loop | Skills whose effect op is `projectile` (`10_systems/SKILL_EFFECTS.md`) |
| `_impact` | On-hit burst at the target/impact point | Optional; any damaging/statusing active |
| `_loop` | Persistent zone / channel loop (ground effects, auras) | Skills with a lingering area or channel |
| `_proc` | Proc flash for a passive's `on_hit_proc` trigger | Passives only, optional |

Rules: suffixes only from this table (new suffixes are proposed here first, GLOSSARY-style —
never invented in content); each clip is its own row set under
`40_assets/SPRITESHEET_SPEC.md`'s manifest; a referenced-but-missing derived clip is an asset-
pass error, not a content-validation error (only the anchor id is validated from the YAML).

## 3. Sync contract (cited, not restated)

- The body plays its shared state (`cast`/`attack`, `40_assets/ANIMATION_STATES.md`); the
  `_cast` fx clip starts on the same frame 0 and the skill's damage lands on the body state's
  `hit_frame` (`40_assets/ANIMATION_TIMING.md` §3 — the load-bearing contract). Fx clips carry
  **no** `hit_frame` of their own.
- `haste` scales fx-clip playback exactly as it scales the body state
  (`40_assets/ANIMATION_TIMING.md` §2/§3.2) so overlays never desync.
- `_proj` flight and `_loop` clips loop untimed; `_impact`/`_proc` are one-shots.

## 4. Monster abilities — explicitly out of this namespace

Monster/boss ability visuals ride the monster's own body states (`cast`, `telegraph`,
`40_assets/ANIMATION_STATES.md`); no `skill_*` clip id may appear on a monster
(`docs/ID_REGISTRY.md` — the player skill ID space is player-only). Whether a future
per-ability fx layer for boss kits is wanted stays `40_assets/SPRITESHEET_SPEC.md`'s open
question, not granted here.

## 5. Skill icon ids

The §1 derived-from-the-skill-id logic extends to the skill's **icon asset**. Every skill —
**active and passive** — binds to exactly one icon:

```
ui_icon_skill_<line>_<NNN>      # e.g. ui_icon_skill_weaver_007; novice: ui_icon_skill_novice_NNN
```

This instantiates the locked `40_assets/UI_ART_SPEC.md` naming (`ui_icon_{category}_{name}`,
category `skill`) with `{name}` = the skill id's `<line>_<NNN>` stem — a deterministic function
of the already-registered skill id, so like the §1 anchor it mints no `docs/ID_REGISTRY.md`
block and inherits the skill id's immutability. The skill file's `icon` field
(`20_schemas/skill.schema.md`) is authored explicitly and must equal this derived value
(validated there, rule 10; `docs/VALIDATION.md` §6) — authored-but-derived, the same
tooling-legibility precedent as item `line_hint`.

- **Construction** is entirely `40_assets/UI_ART_SPEC.md`'s (locked): its icon grids, 1px ink
  outline, single-motif and readable-at-16px rules, and the slot-frame states (empty/filled/
  selected/locked/cooldown) apply as written. Skill icons author on the **24 grid** (the
  HUD/skill-bar square family there) and must survive the 16 grid (tooltips, tracker contexts).
- **Motif** depicts the skill — the thing a player would name it by — never a character,
  weapon skin, or equipment piece: the player sprite is composited
  (`40_assets/CHARACTER_COMPOSITING.md`) and icons must stay appearance-independent.
- **Where it shows**: skill-bar slots and their cooldown wipe (`10_systems/HUD.md`), the
  Skills window, and skill tooltips. Passive icons appear in the Skills window only (passives
  are never slotted, `10_systems/SKILL_SYSTEM.md` §7).

Icons are UI-atlas assets (`40_assets/UI_ART_SPEC.md` export section, `ui_icon_{category}_{name}`
naming), not entity atlases — `40_assets/SPRITESHEET_SPEC.md` does not apply to them.

## Open Questions

- Whether `_impact` bursts should be shareable library clips (one generic per element, reused
  across skills) instead of per-skill ids is an art-pass economy call; per-skill ids stay the
  default — a shared library would be proposed here as a reserved `fx_<element>_impact` family
  first.
- Screen-space flourishes (the boss-slam shake, `10_systems/CAMERA.md` OQ) are presentation
  metadata with no home field yet; if a skill-authored hook is wanted it belongs in
  `20_schemas/skill.schema.md` as a new field, flagged there — not smuggled into a clip suffix.
- Exact fx canvas sizes per clip family (vs the entity `size_class` cells,
  `40_assets/SPRITESHEET_SPEC.md` §4) are an art-pass decision; nothing in this doc fixes pixel
  dimensions.
- **Player atlas linkage — largely resolved by the compositing wave.**
  `40_assets/CHARACTER_COMPOSITING.md` §6 fixes the export half of the old gap: player frames
  are named by **part** ids (`style_*` / `item_equip_NNNN`), each part its own
  `40_assets/SPRITESHEET_SPEC.md` atlas — so fx clips (§2) overlay the composited stack and
  never resolve to rows of a (nonexistent) monolithic player sheet. Still open there, and
  therefore still open here: the player-schema half, and where fx-clip sheets themselves pack
  (single-strip vs. state-row atlases) — an art-pass call alongside the canvas-size question
  above.
