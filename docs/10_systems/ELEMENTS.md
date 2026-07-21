# ELEMENTS.md — Element System

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md,
20_schemas/monster.schema.md, 10_systems/STATS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/DROPS.md, 40_assets/UI_ART_SPEC.md

Owner doc for the 6 elements in `00_vision/GLOSSARY.md`. Defines what each element means, how
element interacts with monster affinities and player defense, where elements appear across the
game, and the conventional status pairing. The element set is fixed at six; adding or renaming
requires a GLOSSARY Provisional entry, not an edit here.

## 1. The six elements

| Element | Meaning |
|---|---|
| `neutral` | Un-attuned physical force (impact, slash, pierce). The "no element" element. |
| `fire` | Heat, cinder, combustion. |
| `frost` | Cold in all forms — water, ice, chill (frost **covers** water/ice/cold). |
| `nature` | Growth, toxin, thorn, beast. |
| `arcane` | Raw magic, runes, force, anti-magic. |
| `shadow` | Void, curse, decay, the unlit. |

`neutral` is physical; the other five are **attuned** (magical). This split drives mitigation
(§3). There is no seventh "holy/light" element — `arcane` and `nature` cover the bright motifs.

## 2. Interaction model — per-monster affinity lists (not a wheel)

Rebillion deliberately does **not** use a rock-paper-scissors element wheel. There is no fixed
"fire beats nature" table. Instead every monster **declares its own affinities** as three
element lists in its schema (`20_schemas/monster.schema.md`):

- `weak_to` — elements this monster takes extra damage from.
- `resists` — elements this monster shrugs off.
- `immune_to` — elements this monster ignores entirely.

When an attack of element `E` lands on a monster, the **element multiplier** is:

| Condition | Multiplier |
|---|---|
| `E` in `immune_to` | ×0 |
| `E` in `weak_to` | ×1.5 |
| `E` in `resists` | ×0.5 |
| otherwise (including all `neutral` unless explicitly listed) | ×1.0 |

The three lists are **mutually exclusive** — an element may appear in at most one of them
(`00_vision/PILLARS.md` P5; enforced by `VALIDATION.md` referential/schema checks). The element
multiplier is one factor in the full damage pipeline; where it slots in relative to `power`/
`spellpower`, `crit_power`, and mitigation is owned by `10_systems/COMBAT_FORMULA.md`. This doc
owns only the multiplier values and the affinity model.

Design intent (P2, legible): affinities are per-monster so a player learns "this beetle hates
`fire`" from play and telegraph, not from memorizing a global wheel. Authoring guidance —
monsters should carry short, thematic lists (typically 0–2 `weak_to`, 0–2 `resists`, rarely an
`immune_to`); a monster with no lists is plain ×1.0 to everything.

## 3. Player-side defense — deliberately simple

Players do **not** have a six-element resistance grid. Incoming damage is mitigated by exactly
two derived stats (`10_systems/STATS.md`), selected by the element's physical/attuned split:

| Incoming damage element | Mitigated by |
|---|---|
| `neutral` (physical) | `armor` |
| `fire` / `frost` / `nature` / `arcane` / `shadow` (attuned) | `warding` |

That is the whole player-side elemental-defense story: **`warding` is the single knob for all
attuned/elemental damage; `armor` for physical.** Beyond that, the only way to further blunt
elemental damage is through **status effects** (e.g., `fortify` raising `warding`, `veil` while
stealthed) from `10_systems/STATUS_EFFECTS.md`. We keep it this simple on purpose (P2): no
per-element gear resistances, no attunement loadouts. (The actual `armor`/`warding` →
reduction-percentage curve is `10_systems/COMBAT_FORMULA.md`; this doc only routes element →
which stat mitigates it.)

## 4. Where elements appear

| Surface | Role | Owner (reference, not restated here) |
|---|---|---|
| Skill effects | Each damaging/status skill declares its element | `10_systems/SKILL_SYSTEM.md`, `10_systems/SKILL_EFFECTS.md` |
| Monster affinities | `weak_to` / `resists` / `immune_to` lists (§2) | `20_schemas/monster.schema.md` |
| Region identity | Each region has dominant element(s) for theme/tuning | `docs/WORLD_PLAN.md` "Element affinity summary" |
| Damage-number tinting | Floating combat numbers are tinted per element | `40_assets/UI_ART_SPEC.md` |
| Drops/materials | Region element flavors drop tables and etc-materials | `10_systems/DROPS.md`, `docs/WORLD_PLAN.md` |

Region dominant elements are **not** copied here — the authoritative per-region list is
`docs/WORLD_PLAN.md` "Element affinity summary". A monster inherits its region's palette ramp
(`40_assets/ART_BIBLE.yaml`) but may still carry any affinity list; region element is a tuning
and identity guide, not a hard constraint on a monster's `weak_to`/`resists`.

### 4.1 Damage-number tint
Each element maps to one tint token consumed by `40_assets/UI_ART_SPEC.md` for floating combat
numbers. The exact palette values are locked in the UI/art layer; this doc only asserts a 1:1
element→tint mapping exists so that `neutral`, `fire`, `frost`, `nature`, `arcane`, and `shadow`
are each visually distinguishable. Tint hex/ramp is owned by `40_assets/UI_ART_SPEC.md` /
`40_assets/ART_BIBLE.yaml`.

## 5. Element ↔ status pairing (guideline, not a rule)

Convention for which statuses (`10_systems/STATUS_EFFECTS.md`) an offensive element typically
applies, so content reads consistently. This is **authoring guidance only** — a skill or monster
may pair any status with any element when it has a reason; nothing enforces the table.

| Element | Conventionally applies | Notes |
|---|---|---|
| `neutral` | `sunder`, `stun` | Physical impact — armor-break and stagger. |
| `fire` | `burn` | Ignite damage-over-time. |
| `frost` | `chill`, `freeze` | Slow escalating to hard freeze. |
| `nature` | `poison`, `root` | Toxin damage-over-time and entangle. |
| `arcane` | `blind`, `weaken` | Sense/mind disruption; the go-to **anti-stealth** element — arcane sources pierce `veil`. |
| `shadow` | `silence`, `weaken` | Curse-like suppression; carries the `veil` (stealth) flavor. |

Buffs (`empower`, `fortify`, `swiftness`, `regen`, `clarity`, `veil`) are largely
element-agnostic self/party effects; only `regen` (nature) and `veil` (shadow) carry a soft
thematic lean and none are element-gated. The single cross-element interaction promoted from
guideline to a **stated intent** is anti-stealth: `arcane` is the element that counters `veil`
(detail and any reveal mechanic live in `10_systems/STATUS_EFFECTS.md`).

## Open Questions

- Should any player-facing per-element resistance ever exist (e.g., a `legendary` gear affix or
  a region-attunement consumable)? Default **no** — `warding` + status only. Flag for possible
  `10_systems/ITEMS.md` affix consideration; would require a GLOSSARY note if it introduces
  per-element tokens.
- Mitigation routing when a **physical** weapon carries an **elemental** skill (e.g., a `blade`
  skill dealing `fire`): default is that the damage instance uses its skill-declared element to
  pick `armor` vs `warding` (so that `fire` blade hit → `warding`). Confirm with
  `10_systems/SKILL_SYSTEM.md` / `10_systems/COMBAT_FORMULA.md`.
- "True"/unmitigated damage that bypasses both `armor` and `warding` is **not** in scope; flag if
  a Rift raid boss (`docs/WORLD_PLAN.md` R12) needs it. Default: no such damage type.
- The element→status pairing (§5) is a guideline; if content authoring needs it mechanically
  enforced, promote it to a rule. Owner call: keep as guideline for now.
