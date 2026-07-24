# HUD.md — Always-On HUD & Game-Shell Layout

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md,
10_systems/COMBAT_FORMULA.md, 10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/COMBO_SYSTEM.md, 10_systems/INVENTORY.md, 10_systems/QUESTS.md,
10_systems/CONTROLS.md, 10_systems/JOBS.md, 10_systems/AI_BEHAVIOR.md, 10_systems/DEATH_PENALTY.md,
10_systems/PERSISTENCE.md, 10_systems/social/CHAT.md, 10_systems/social/PARTY.md,
10_systems/UI_WINDOWS.md, 40_assets/UI_ART_SPEC.md

Owner doc for the **game shell**: the always-on HUD layout, which of its elements are permanent
vs. contextual/toggle, and the frame-variant/font/color usage mapping the rest of this tree cites
by name. Gauge/skill/status *semantics* (pool math, cooldowns, status magnitudes) are owned
elsewhere (`10_systems/STATS.md`, `10_systems/SKILL_SYSTEM.md`, `10_systems/STATUS_EFFECTS.md`);
this doc owns only what is drawn, where, and in what always-on/toggle state. Exact pixel
metrics/hex values are `40_assets/UI_ART_SPEC.md`'s (Phase C); this doc fixes layout regions and
which locked token (frame/color/font) each element uses.

## 0. Design stance — classic-inspired, original identity

The shell speaks the familiar **classic side-scroller MMO grammar** — a bottom bar carrying the
pool gauges, skill slots, and quickslots; a thin always-visible `exp` strip along the screen's
bottom edge; a top-right minimap; floating damage numbers — because that grammar is instantly
legible to the genre's audience (the working visual reference is
`docs/mockups/gameplay_scene_mockup.html`). It is **inspiration, never reproduction**: no
layout, proportion, icon, frame art, or asset is copied or traced from MapleStory or any other
title. Every concrete element resolves through this tree's own locked identity — the
`frame_*`/font/color tokens of `40_assets/UI_ART_SPEC.md` and `40_assets/ART_BIBLE.yaml`
(change-controlled) — and this game's own vocabulary (`life`/`essence` gauges, `shards` wallet,
ember/tide/arcane ramps), matching the original-identity stance `10_systems/UI_WINDOWS.md`
already fixes for the framed-window family. Divergences are deliberate, not accidental: a
dedicated Dodge slot beside the skill bar (§3), phase-pip boss bars (§6), show-on-damage monster
`life` bars (§6.1), the combo counter (§7.1), and the party-frame column (§4.1) are this game's
own HUD, not a clone's.

## 1. Frame-variant usage mapping (locked tokens, this doc's authoritative table)

| Frame | Used for |
|---|---|
| `frame_window` | Toggle windows: Inventory, Skills/Character, full Map, Party (Party + Board tabs, `10_systems/UI_WINDOWS.md` §4), Guild |
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
├─ party frames (§4.1, contextual) ───────┤            └───────────────────────────┘   ├─ quest tracker ────────┤
│ member · life/essence % · state (×≤5)   │                                              │  (compact, ≤3 quests) │
└──────────────────────────────────────────┘            (toasts stack here, top-center) └────────────────────────┘

                              (status icon row — verdant/red edge rings)

┌── exp gauge (arcane ramp, full width, thin) ─────────────────────────────────────────────────────────────────┐
├── life (ember) / essence (tide) ──┤   [1][2][3][4][5][6][7][8]  Dodge   [F1][F2][F3][F4]   wallet ◇ shards   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
 chat dock (bottom-left, collapsed)
```

Top-left = player plate, with the party frames (§4.1) stacked directly beneath it. Top-center =
`boss_bar` (contextual). Top-right = minimap over the quest tracker. Center-top, below `boss_bar`,
= toast stack. Just above the bottom bar = the status icon row. Bottom = the main bar
(life/essence, 8 skill slots + Dodge + 4 quickslots, and the `shards` wallet readout right-aligned)
with a full-width thin `exp` strip beneath it. Bottom-left = the chat dock. In-world, non-boss
monsters carry their own small `life` bar beneath the sprite (§6.1).

## 3. Bottom bar

- **Gauges.** `life` (ember ramp) above `essence` (tide ramp), horizontal bars, left-aligned,
  numeric `current`/`max` in `ui_number` font overlaid. `exp` is a separate, thinner, full-width
  bar (arcane ramp) along the very bottom edge — the classic always-visible progress strip,
  distinct from the two pool gauges above it (`40_assets/ART_BIBLE.yaml` `hud_colors`).
- **Skill bar.** 8 `frame_slot` cells (`10_systems/SKILL_SYSTEM.md` §7), centered, plus the
  dedicated **Dodge** slot (`10_systems/CONTROLS.md` §3) immediately beside them, visually
  distinguished (its own small frame) so it doesn't read as a 9th combat skill.
- **Quickslots.** 4 `frame_slot` cells to the right of the skill bar (`10_systems/INVENTORY.md`
  `use` items).
- **Wallet.** The `shards` counter (`10_systems/INVENTORY.md` §3 — that doc owns the wallet, its
  cap, and overflow behavior; this doc owns only the placement) sits **right-aligned in the bottom
  bar**, right of the quickslots: a small `shards` icon plus the balance in `ui_number` (tabular,
  so a ticking balance doesn't jitter). Always-on (§11). The same balance is mirrored in the
  Inventory window footer (`10_systems/UI_WINDOWS.md` §2) — one value, two readouts.
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

## 4.1 Party frames — below the plate (contextual)

The region `10_systems/social/PARTY.md` §3 forward-references: while in a party, up to **5**
compact member plates (everyone but self) stack vertically beneath the player plate, top-left,
in `frame_system`. Each plate shows what PARTY §3 specifies — member name (`name_tag`), `level`,
the job-line icon, `life` and `essence` as **percentage bars** (ember/tide ramps, no numerics —
exact pools are the member's own business), a same-map indicator dot, and alive/**fallen** state
(`10_systems/DEATH_PENALTY.md` §5.3; a fallen member's plate desaturates with a fallen glyph —
fallen members remain rendered, resolving that doc's party-frame Open Question on the HUD side).
Plate order = PARTY.md's roster order (leader first). Hidden entirely when not in a party;
**server-deferred and dormant in the interim solo build** like the rest of the party system
(`00_vision/PILLARS.md` P6) — the layout region is reserved now so the shell is
multiplayer-shaped from day one. Clicking/target-selecting via party frames is not modeled at
launch (support `party`-shape skills target by radius, `10_systems/SKILL_SYSTEM.md` §6, not by
frame click).

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

## 6.1 Monster `life` bars — non-boss, beneath the sprite (owner decision 2026-07-24)

Every `normal`- and `elite`-tier monster shows a small `life` bar drawn **beneath its sprite**
(anchored under the feet-center pivot, below the animation so it never overlaps the name tag
above). Rules:

- **Show-on-damage.** Hidden while the monster is untouched at full `life`; appears on the first
  damage instance it takes and **fades out 4 s after the last damage** (or on death — the bar
  never lingers over a `die` animation). It does not show during the `spawn` state
  (`10_systems/SPAWN.md` §6 — the entrance is invulnerable anyway).
- **Look.** Ember ramp fill on an ink track (matching the player `life` gauge and `boss_bar`, so
  "this is a `life` pool" reads identically everywhere), no numeric readout — the bar is a
  proportion, the damage numbers (§7) are the arithmetic. Width scales with the monster's size
  class (`40_assets/ART_BIBLE.yaml` `sizing.size_classes`): roughly sprite-width for
  `tiny`/`small`/`medium`, clamped for `large` so it never spans the screen. Exact pixel metrics
  are `40_assets/UI_ART_SPEC.md`'s (Phase C amendment channel).
- **Elite trim.** An `elite`'s bar carries a thin `frame_system`-style edge and sits alongside its
  ember.light name tag — a glance distinguishes "elite at half" from "normal at half."
- **Bosses never show one.** `boss`-tier and raid bosses use the top-center `boss_bar` (§6)
  exclusively; a second under-sprite bar would duplicate state and clutter the arena.
- Player preference to hide monster bars exists (client pref, `10_systems/PERSISTENCE.md`),
  same as damage numbers (§11).

This resolves the monster-`life`-feedback gap flagged in
`docs/phase_reports/GAMEPLAY_LOOP_REVIEW_2026-07-24.md` §4.1, per owner direction (bar beneath
the animation, non-boss tiers only).

## 7. Damage numbers

`dmg_number` font, spawned at the hit location, floating up and fading over ≈0.8 s.

| Case | Treatment |
|---|---|
| Normal hit | Base size, element tint (`10_systems/ELEMENTS.md` §4.1 mapping; hex owned by `40_assets/UI_ART_SPEC.md`) |
| Crit | ≈50% larger, brief punch-scale-in, same element tint |
| Miss / Immune | Text `"Miss"`/`"Immune"` (`10_systems/COMBAT_FORMULA.md` §2 steps 1–2), neutral color, no element tint |
| Heal | `+`-prefixed number, tinted with `hud_colors life` (ember) rather than an element, associating it with the `life` gauge |

## 7.1 Combo counter (`10_systems/COMBO_SYSTEM.md` state; this doc owns the drawing)

Right of screen center, vertically about a third down — clear of the top-center `boss_bar`/toast
stack, the top-right minimap column, and the bottom bar. Contextual: appears at **2+ links**,
hidden otherwise; fades ≈0.5 s after the chain resets. Shows the link count in the `dmg_number`
font with a small `ui_small` label, plus up to three momentum-tier pips that fill as tiers I–III
engage (tiers gated by advancement — `10_systems/COMBO_SYSTEM.md` §3; a locked tier's pip renders
as an empty socket). A `combo_burst` (`10_systems/COMBO_SYSTEM.md` §4) plays a brief punch-scale
flash on the counter, reusing §7's crit punch-scale language. No `frame_*` chrome — like damage
numbers, it is combat feedback, not a window. `combo_momentum` is **not** a status and never
appears in the §8 status icon row. Exact pixel metrics/animation are `40_assets/UI_ART_SPEC.md`'s
(Phase C amendment channel).

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
| Bottom bar (gauges, skill bar, quickslots, wallet) | Always-on |
| Player plate | Always-on |
| Party frames (§4.1) | Contextual — shown while in a party; hidden otherwise (dormant in solo) |
| Monster `life` bars (§6.1) | Contextual — show-on-damage, 4 s fade; player preference to disable |
| Minimap | Always-on |
| Quest tracker | Always-on **while ≥1 quest is tracked**; auto-hidden otherwise; player may also manually collapse it |
| `boss_bar` | Contextual/automatic — shows on boss/flagged-elite aggro, hides on death/exit; not player-toggled |
| Damage numbers | Always-on; player preference to disable exists (client pref, `10_systems/PERSISTENCE.md`) |
| Combo counter (§7.1) | Contextual — shows at 2+ links, hides on chain reset; not player-toggled (momentum changes real damage, so the state stays visible) |
| Status icon row | Always-on while ≥1 status is active; auto-hidden otherwise |
| Toasts | Always-on (not disable-able — some carry important state, e.g. inventory-full) |
| Chat dock | Always-on, collapsed; cannot be fully hidden at launch (Open Questions) |
| Inventory / Skills / Quest Log / Map / Party / Guild | Toggle-only, via `10_systems/CONTROLS.md` |

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
