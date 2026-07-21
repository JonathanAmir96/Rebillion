# HUD.md — Always-On HUD & Game-Shell Layout

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md,
10_systems/COMBAT_FORMULA.md, 10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/INVENTORY.md, 10_systems/QUESTS.md,
10_systems/CONTROLS.md, 10_systems/JOBS.md, 10_systems/AI_BEHAVIOR.md, 10_systems/DEATH_PENALTY.md,
10_systems/PERSISTENCE.md, 10_systems/social/CHAT.md, 40_assets/UI_ART_SPEC.md

Owner doc for the **game shell**: the always-on HUD layout, which of its elements are permanent
vs. contextual/toggle, and the frame-variant/font/color usage mapping the rest of this tree cites
by name. Gauge/skill/status *semantics* (pool math, cooldowns, status magnitudes) are owned
elsewhere (`10_systems/STATS.md`, `10_systems/SKILL_SYSTEM.md`, `10_systems/STATUS_EFFECTS.md`);
this doc owns only what is drawn, where, and in what always-on/toggle state. Exact pixel
metrics/hex values are `40_assets/UI_ART_SPEC.md`'s (Phase C); this doc fixes layout regions and
which locked token (frame/color/font) each element uses.

## 1. Frame-variant usage mapping (locked tokens, this doc's authoritative table)

| Frame | Used for |
|---|---|
| `frame_window` | Toggle windows: Inventory, Skills/Character, full Map, Guild |
| `frame_dialog` | Modal confirmations: quest turn-in confirm, vendor confirm, NPC dialogue |
| `frame_quest` | The Quest Log window specifically (`10_systems/QUESTS.md` §8) |
| `frame_system` | Always-on ambient HUD chrome: player plate, minimap, quest tracker, `boss_bar`, toasts |
| `frame_tooltip` | Hover tooltips (item/skill/status tooltips) |
| `frame_input` | Text-entry fields (chat input, search/filter boxes) |
| `frame_button` | Clickable buttons everywhere |
| `frame_slot` | Item/skill/quickslot grid cells (inventory grid, bank grid, skill bar, quickslot bar) |

## 2. Layout overview

```
┌─ plate (frame_system) ──────────────────┐            ┌─ boss_bar (frame_system) ─┐   ┌─ minimap (frame_system) ─┐
│ name_tag Name  Lv NN  Job               │            │  Boss Name    |  |        │   │                        │
└──────────────────────────────────────────┘            └───────────────────────────┘   ├─ quest tracker ────────┤
                                                                                          │  (compact, ≤3 quests) │
                    (toasts stack here, frame_system, top-center)                        └────────────────────────┘

                              (status icon row — verdant/red edge rings)

┌── exp gauge (arcane ramp, full width, thin) ─────────────────────────────────────────────────────────────────┐
├── life (ember) / essence (tide) ──┤        [1][2][3][4][5][6][7][8]  Dodge      [F1][F2][F3][F4]             │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
 chat dock (bottom-left, collapsed)
```

Top-left = player plate. Top-center = `boss_bar` (contextual). Top-right = minimap over the quest
tracker. Center-top, below `boss_bar`, = toast stack. Just above the bottom bar = the status icon
row. Bottom = the main bar (life/essence, 8 skill slots + Dodge + 4 quickslots) with a full-width
thin `exp` strip beneath it. Bottom-left = the chat dock.

## 3. Bottom bar

- **Gauges.** `life` (ember ramp) above `essence` (tide ramp), horizontal bars, left-aligned,
  numeric `current`/`max` in `ui_number` font overlaid. `exp` is a separate, thinner, full-width
  bar (arcane ramp) along the very bottom edge — the classic always-visible progress strip,
  distinct from the two pool gauges above it (`00_vision/GLOSSARY.md` `hud_colors`).
- **Skill bar.** 8 `frame_slot` cells (`10_systems/SKILL_SYSTEM.md` §7), centered, plus the
  dedicated **Dodge** slot (`10_systems/CONTROLS.md` §3) immediately beside them, visually
  distinguished (its own small frame) so it doesn't read as a 9th combat skill.
- **Quickslots.** 4 `frame_slot` cells to the right of the skill bar (`10_systems/INVENTORY.md`
  `use` items).
- **Cooldown wipe.** A clockwise radial wipe over the slot icon, darkened/grayed proportional to
  remaining cooldown, uncovering as it elapses; a numeric countdown (`ui_number`) overlays the
  wipe for cooldowns > 2 s (omitted below that to avoid flicker). A slot the player cannot afford
  (`essence_cost` > current `essence`, `10_systems/SKILL_SYSTEM.md` §5) shows a desaturated/red
  tint distinct from the cooldown wipe.

## 4. Top-left player plate

`frame_system`. Shows: character name (`name_tag` font), `level` (`ui_number`), and job display
name (`ui_small`/`ui_body`) — `"Novice"` pre-Lv 8, else the line's tier title
(`10_systems/JOBS.md` §0, e.g. `"Bulwark"` → `"Ironbrand"` → `"Aegis"`). No portrait/life-readout
duplication here — `life`/`essence` live only in the bottom bar (§3).

## 5. Top-right: minimap + quest tracker

Minimap sits in `frame_system`, top-right (locked position). The compact quest tracker
(`10_systems/QUESTS.md` §8) sits directly beneath it, also `frame_system`, showing up to 3
tracked quests' name + current-step progress. Both are ambient chrome, not draggable windows.

## 6. `boss_bar` — top-center

A wide `frame_system` bar, contextual (§11): appears on boss/flagged-elite aggro, disappears on its
death or the player leaving the encounter. Shows the boss name (`ui_title` font) and a `life` bar
in the ember ramp (matching `hud_colors life`, reinforcing "this is a life pool" at a glance) with
no numeric percentage by default (Open Questions) — mystery/telegraph-driven readability over an
exact number (P1). **Phase pips**: small markers along the bar at each `life_threshold_pct`
(`10_systems/AI_BEHAVIOR.md` §15), dividing it into that boss's phase count; the pip nearest the
current threshold briefly flashes on a `phase_shift` transition.

## 7. Damage numbers

`dmg_number` font, spawned at the hit location, floating up and fading over ≈0.8 s.

| Case | Treatment |
|---|---|
| Normal hit | Base size, element tint (`10_systems/ELEMENTS.md` §4.1 mapping; hex owned by `40_assets/UI_ART_SPEC.md`) |
| Crit | ≈50% larger, brief punch-scale-in, same element tint |
| Miss / Immune | Text `"Miss"`/`"Immune"` (`10_systems/COMBAT_FORMULA.md` §2 steps 1–2), neutral color, no element tint |
| Heal | `+`-prefixed number, tinted with `hud_colors life` (ember) rather than an element, associating it with the `life` gauge |

## 8. Status icon row

Centered, directly above the bottom bar. One icon per active status, each with a radial duration
ring reusing the same wipe language as §3's cooldown wipe, edge-colored **verdant for a buff,
red for a debuff** (per the locked UI bible). Row capacity is exactly **12** — this is not an
arbitrary UI limit, it is `10_systems/STATUS_EFFECTS.md` §1's hard per-entity status cap, so no
overflow/scroll handling is needed. Hidden entirely when no statuses are active.

## 9. Toasts

`frame_system`, color-coded by semantic category (exact hues `40_assets/UI_ART_SPEC.md`'s):
**success** (level-up, quest turn-in), **warning** (inventory full,
`10_systems/INVENTORY.md` §4–§5; `shards` cap reached, `10_systems/INVENTORY.md` §3), **info**
(bind point changed, `10_systems/DEATH_PENALTY.md` §4; quest available). Stack top-center, below
`boss_bar` when one is showing; up to 3 visible at once (further toasts queue), each shown ≈4 s
then a 0.3 s fade.

## 10. Chat dock (placeholder)

Bottom-left, collapsed by default (last 3–4 lines, semi-transparent), expands/focuses on
`10_systems/CONTROLS.md`'s chat-focus key. All chat mechanics (channels, history, moderation) are
`10_systems/social/CHAT.md`'s — a stub not yet authored; this doc reserves only the screen
position and the always-on-collapsed default (§11).

## 11. Always-on vs. toggle (defaults)

| Element | Default |
|---|---|
| Bottom bar (gauges, skill bar, quickslots) | Always-on |
| Player plate | Always-on |
| Minimap | Always-on |
| Quest tracker | Always-on **while ≥1 quest is tracked**; auto-hidden otherwise; player may also manually collapse it |
| `boss_bar` | Contextual/automatic — shows on boss/flagged-elite aggro, hides on death/exit; not player-toggled |
| Damage numbers | Always-on; player preference to disable exists (client pref, `10_systems/PERSISTENCE.md`) |
| Status icon row | Always-on while ≥1 status is active; auto-hidden otherwise |
| Toasts | Always-on (not disable-able — some carry important state, e.g. inventory-full) |
| Chat dock | Always-on, collapsed; cannot be fully hidden at launch (Open Questions) |
| Inventory / Skills / Quest Log / Map / Guild | Toggle-only, via `10_systems/CONTROLS.md` |

## Open Questions

- Whether `boss_bar` should optionally show an exact `life` percentage (accessibility option) vs.
  staying bar-only is undecided; default is bar + pips only, no number.
- Whether toasts should get a "reduce frequency"/mute-by-category player preference beyond the
  fixed 3-stack/4 s timing is unresolved.
- Fully hiding the chat dock (vs. always-collapsed-visible) is not offered at launch; flag if
  `10_systems/social/CHAT.md` wants a hide option once authored.
- HUD scaling for uncommon aspect ratios / safe-area guarantees is not addressed here; likely an
  engineering/`40_assets/ART_BIBLE.yaml` concern once a target resolution locks.
- Exact pixel sizes, hex values, and icon art for every element above are
  `40_assets/UI_ART_SPEC.md`'s (Phase C); this doc fixes layout and token usage only.
- Whether the player plate should ever show a portrait/character-icon is not modeled; default is
  text-only (name/level/job).
