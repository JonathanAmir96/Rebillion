# SKILL_ANIMATION.md — Skill Animation Bindings, FX Clips & Skill Icons

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 40_assets/ART_BIBLE.yaml,
40_assets/ANIMATION_STATES.md, 40_assets/ANIMATION_TIMING.md, 40_assets/SPRITESHEET_SPEC.md,
40_assets/UI_ART_SPEC.md, 40_assets/CHARACTER_COMPOSITION.md, 10_systems/SKILL_SYSTEM.md,
10_systems/SKILL_EFFECTS.md, 10_systems/ELEMENTS.md, 10_systems/JOBS.md, 10_systems/HUD.md,
20_schemas/skill.schema.md, 30_engineering/ENGINEERING_STANDARDS.md, docs/ID_REGISTRY.md,
docs/VALIDATION.md

Owner doc for the three things every skill file's presentation hangs on: the **`animation` id**
naming/resolution rule `20_schemas/skill.schema.md` and `docs/VALIDATION.md` §6 cite, the **skill
FX clip** namespace (the visual layer that makes 56 skills look distinct while the actor plays one
shared clip), and the **skill icon** asset law binding every skill to its `ui_icon_skill_*` asset
(construction/grids owned by the locked `40_assets/UI_ART_SPEC.md`; this doc owns only which icon
id a given skill maps to). It does **not** own: the 12 state tokens, their budgets or interrupt
rules (`40_assets/ANIMATION_STATES.md`); fps/hit-frame law (`40_assets/ANIMATION_TIMING.md`);
atlas grid math (`40_assets/SPRITESHEET_SPEC.md`); skill mechanics of any kind
(`10_systems/SKILL_SYSTEM.md` / `10_systems/SKILL_EFFECTS.md`); or icon pixel construction
(`40_assets/UI_ART_SPEC.md`, locked). It cites all of these and restates none.

## 1. The one-state law: every skill plays `cast`

Every **active skill**, of every line, plays the actor's **`cast`** state
(`40_assets/ANIMATION_STATES.md` §1: "Magic/skill clip for damage, heal, or buff ops"). The
`attack` state is reserved for the **basic attack** only. There is no per-skill body clip: a
character has exactly one `cast` clip (per `40_assets/CHARACTER_COMPOSITION.md`'s canonical rig),
and per-skill visual identity comes entirely from the FX layer (§3). This is deliberate:

- It keeps the paper-doll tractable — a customizable player (`40_assets/CHARACTER_COMPOSITION.md`)
  composites many equipment layers, and every layer would need every per-skill body clip if skills
  owned body poses. One `cast` clip per layer means **any skill works with any appearance
  combination by construction**.
- It honors the locked frame budgets (`40_assets/ART_BIBLE.yaml` `animation.frame_budgets`, `cast`
  [4,6]) — 56 distinct body clips would be incompatible with "few frames done well."
- Hit-frame honesty (`00_vision/PILLARS.md` P1) is preserved: the damage signal still comes from
  one authored frame of one clip (§2).

**Passives play nothing** (`20_schemas/skill.schema.md`: `animation` omitted for passives); a proc
passive may carry a name-derived proc FX clip (§3, `proc` part).

## 2. The `animation` id — naming and resolution

Every active skill's `animation` field is exactly:

```
skill_<line>_NNN_cast          # e.g. skill_weaver_007_cast; novice: skill_novice_NNN_cast
```

i.e. **the skill's own immutable id + the literal suffix `_cast`** — the anchor form
`20_schemas/skill.schema.md` already carries, now confirmed as law (`docs/VALIDATION.md` §6
enforces it). The suffix names the *binding*, not a new state token: the id resolves, entirely by
convention, to (a) the actor entering the `cast` state and (b) the FX clip set derived in §3. One
`animation` id per skill, always — multi-part visuals are expressed as derived FX parts (§3), never
as a second animation id (this resolves `20_schemas/skill.schema.md`'s multi-clip Open Question).

**Timing.** The `cast` clip's playback rate and `hit_frame` law are `40_assets/ANIMATION_TIMING.md`'s
(§1–§3 there); the manifest field they land in is `40_assets/SPRITESHEET_SPEC.md` §7.1's. The
skill's effect ops fire on the `cast` row's `hit_frame` signal — never on a duplicate timer
(`30_engineering/ENGINEERING_STANDARDS.md`). For **`projectile`-targeted skills**, this doc confirms
the reading `40_assets/ANIMATION_TIMING.md` §3.3 left open: `hit_frame` fires the projectile's
**spawn/release**; damage applies later, on the projectile's own travel-time collision signal (the
standard Hitbox/Area2D pattern there). All other shapes resolve their targets at the `hit_frame`
signal itself (`10_systems/SKILL_SYSTEM.md` §6 owns the geometry).

## 3. Skill FX clips — derived namespace, no new authored fields

FX clips are named by **derivation from data already in the skill file** (id + targeting shape) —
no new schema fields, no per-skill FX manifest:

```
fx_<skill_id>_<part>           # parts: cast | proj | impact | proc
```

| Part | When it exists | Plays |
|---|---|---|
| `fx_<skill_id>_cast` | Every active skill | Overlaid on the composed character, started in sync with the `cast` clip's frame 0; anchored to the actor's pivot. The swing arc, rune flash, bowstring flare — whatever sells this skill on the caster. |
| `fx_<skill_id>_proj` | `targeting: projectile` only | The travelling body itself, looping for the projectile's flight (`10_systems/SKILL_SYSTEM.md` §6 owns speed/range/gravity). Spawned at the `hit_frame` release (§2). |
| `fx_<skill_id>_impact` | `projectile` (at collision) and `aoe_circle` (at the resolved origin) | One-shot burst at the point of effect. `melee_arc`/`line` skills may optionally add it (played once per target hit) — optional, not derived-required. |
| `fx_<skill_id>_proc` | Passives with `on_hit_proc` (optional) | One-shot flourish on the proc's owner when the proc fires (`10_systems/SKILL_EFFECTS.md` §16). |

Notes, per shape (`10_systems/SKILL_SYSTEM.md` §6 owns all geometry — nothing below redefines it):

- **`aoe_circle`** ground-target telegraph discs are engine-drawn primitives (a tinted disc/ring),
  not authored FX clips — they must scale to any `radius`/`telegraph` combination, so they cannot
  be fixed sprites.
- **`self`/`party`** skills carry only the `cast` overlay. Ongoing buff feedback is the status icon
  row's job (`10_systems/HUD.md` §8), not a persistent on-character aura loop — deliberately, to
  keep a 6-player screen readable (`00_vision/PILLARS.md` P1). Flagged in Open Questions if a
  future pass wants auras.
- **`summon_entity`** skills use the summoned entity's own `spawn` state
  (`40_assets/ANIMATION_STATES.md` §5 summon row) as the arrival visual; the skill itself still
  gets its `cast` overlay.
- **Monster abilities** have no per-ability clip layer (`40_assets/SPRITESHEET_SPEC.md` Open
  Questions); this namespace is player-skill-only until that question is resolved.

### 3.1 FX sheet contract

FX clips are **single-row strips** (frame index = column, no multi-state rows): the file is
`fx_<skill_id>_<part>.png` plus a manifest sidecar reusing `40_assets/SPRITESHEET_SPEC.md` §7's
front-matter shape (`schema: 40_assets/SKILL_ANIMATION.md`, one `frames`/`fps` entry instead of a
`states` map). Frame naming extends `40_assets/ART_BIBLE.yaml` `export_contract.frame_naming`
verbatim, with the fx id in the `{entity_id}` position: `fx_<skill_id>_<part>_{NN}`. Folder:
`assets/fx/skills/<line>/` (the `fx/` node `40_assets/SPRITESHEET_SPEC.md` §9 reserves and scopes
out of its own contract). Padding/extrusion/power-of-two and the Godot import preset are
`SPRITESHEET_SPEC` §2/§8's, applied unchanged.

**Proposed frame budgets and fps** — `40_assets/ART_BIBLE.yaml` `animation.frame_budgets` covers
only the 12 states, and that file is locked, so like `40_assets/ANIMATION_STATES.md` §2.2 these are
a **proposal** pending Agent-3 blessing via the `amendments[]` channel, not canon:

| Part | Proposed budget | Proposed fps | Rationale |
|---|---|---|---|
| `cast` overlay | [3,6] | 12 | Must read within the `cast` clip's own playthrough; never longer than it (hard rule regardless of the blessed numbers). |
| `proj` loop | [2,4] | 10 | A travelling body needs shimmer, not narrative; loops for flight. |
| `impact` | [3,6] | 12 | The payoff frame set; snappy per `ART_BIBLE animation.principle`. |
| `proc` | [2,4] | 12 | A glint, not an event — must not read as a second skill. |

**Sizing.** `cast`/`proc` overlays use the actor's `size_class` content box
(`40_assets/SPRITESHEET_SPEC.md` §4; player = `small`, 32×32). `proj` ≤ 16×16 first-pass.
`impact` boxes depend on the tile→pixel scale, which is still the open lock
(`10_systems/COMBAT_FORMULA.md` §10 via `10_systems/SKILL_SYSTEM.md` §6) — first-pass cap 64×64,
flagged in Open Questions.

### 3.2 FX palette

An FX clip's accent ramp follows the skill's **`element`** through the element→color mapping
`10_systems/ELEMENTS.md` §4.1 owns (the same mapping HUD damage numbers use,
`10_systems/HUD.md` §7) — cited, not restated. Elementless (`neutral`) skills use their line's
"Element leaning" (`10_systems/JOBS.md` §2–§6, per-line sections) to pick the accent instead.
All other pixel rules — one dominant ramp, selective outline, no gradients — are
`40_assets/ART_BIBLE.yaml`'s, unchanged (FX are in its `applies_to` list).

## 4. Customization invariant (the contract with CHARACTER_COMPOSITION)

The player is a composed paper-doll (`40_assets/CHARACTER_COMPOSITION.md`); skills must work over
**every** appearance combination. Three hard rules follow:

1. **FX never bake character pixels.** No skin, hair, or equipment pixels may appear inside any
   `fx_*` frame — the overlay is transparent wherever the character shows through.
2. **All layers play `cast` in lockstep.** Every appearance layer authors the canonical rig's
   `cast` clip (`40_assets/CHARACTER_COMPOSITION.md` §3), so the weapon, gloves, and body swing as
   one; the FX overlay syncs to the same frame clock. No layer, including the weapon, gets a
   per-skill variant clip.
3. **Icons are appearance-independent.** A skill's icon (§5) depicts the skill, never the
   character or a specific weapon skin.

## 5. Skill icons

Every skill — **active and passive** — has exactly one icon asset:

```
ui_icon_skill_<line>_<NNN>      # e.g. ui_icon_skill_weaver_007; novice: ui_icon_skill_novice_NNN
```

This instantiates the locked `40_assets/UI_ART_SPEC.md` naming (`ui_icon_{category}_{name}`,
category `skill`) with `{name}` = the skill id's `<line>_<NNN>` stem — a 1:1 derivation from the
skill's immutable id, so the mapping can never drift. The skill file's `icon` field
(`20_schemas/skill.schema.md`) is authored explicitly and must equal this derived value
(validated there) — the same authored-but-derived precedent as item `line_hint`.

- **Construction** is entirely `40_assets/UI_ART_SPEC.md`'s (locked): its icon grids, 1px ink
  outline, single motif, readable-at-16px rule, and slot-frame states (cooldown wipe, locked,
  selected) apply as written. Skill icons are authored on the **24 grid** (the skill-bar slot
  size family there) and must survive the 16 grid for tooltips/tracker contexts.
- **Motif**: the skill's defining shape or op — the thing the player would name it by (a shield
  wall, a triple arrow, a fire bloom) — with the accent ramp chosen exactly as §3.2 (element, else
  line leaning). Never a portrait, never a weapon skin.
- **Where it shows**: skill-bar slots and their cooldown wipe (`10_systems/HUD.md` §3), the
  Skills window (`frame_window`, `10_systems/HUD.md` §1), and skill tooltips (`frame_tooltip`).
  Passive icons appear in the Skills window only (passives are never slotted,
  `10_systems/SKILL_SYSTEM.md` §7).

Icon count for this run: 56 (13 × 4 lines + 4 novice, `00_vision/SCOPE.md`). Icons are UI-atlas
assets (`40_assets/UI_ART_SPEC.md` export section), not entity atlases — `40_assets/SPRITESHEET_SPEC.md`
does not apply to them.

## 6. Authority & pipeline

Everything this doc owns is **client presentation** (`20_schemas/skill.schema.md` marks
`animation` client-side; `10_systems/PERSISTENCE.md` boundary): the server resolves skill effects
from `hit_frame`-equivalent server timing and never reads FX or icons. PixelLab briefs for FX and
icons inherit `40_assets/ART_BIBLE.yaml` `pixellab_defaults` / `40_assets/UI_ART_SPEC.md`'s brief
rule, injecting only motif, accent ramp, part, and size — per-asset briefs are a Phase D/asset-pass
concern, not authored here.

## Open Questions

- **FX budgets/fps (§3.1) are a proposal** pending Agent-3 blessing into `40_assets/ART_BIBLE.yaml`
  `amendments[]` (same channel as `40_assets/ANIMATION_STATES.md` §2.2's three state budgets — the
  two proposals should land as one amendment if possible). Phase D must not author FX frame counts
  against these numbers until blessed.
- **`impact` sizing cap (§3.1)** inherits the open tile→pixel scale lock
  (`10_systems/COMBAT_FORMULA.md` §10); the 64×64 first-pass cap needs revisiting once the scale
  lands, especially for boss-radius `aoe_circle` skills.
- **`line`-shape beam visuals**: a long `line` skill (up to 12 tiles) cannot be sold by a 32px
  caster overlay alone; whether beams get a dedicated tiling FX part (e.g. `fx_<skill_id>_beam`)
  or remain overlay+impact-only is deferred until the tile scale locks.
- **Persistent buff auras (§3)** are deliberately absent (status icon row carries the feedback);
  flag for a future polish pass if playtesting wants on-character loops for long buffs.
- **Monster per-ability FX** — this namespace is player-only; `40_assets/SPRITESHEET_SPEC.md`'s
  per-ability-clip Open Question owns the monster side.
- **Icon art for the 4 novice skills vs. line skills** shares one namespace; if a future arc adds
  3rd-job skills (`014`–`021` reserved), their icons follow the same derivation with no new rules.
