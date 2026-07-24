# CONTROLS.md — Input Map, Buffering & Rebinding

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/SKILL_SYSTEM.md,
10_systems/SKILL_EFFECTS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/COMBO_SYSTEM.md,
10_systems/INVENTORY.md,
10_systems/CAMERA.md, 10_systems/HUD.md, 10_systems/PERSISTENCE.md, 10_systems/social/CHAT.md

Owner doc for **input**: the default keyboard and gamepad maps, the jump-buffer/coyote-time
windows, rebinding policy, and how a gamepad navigates framed UI. Skill/quickslot *semantics*
(cooldowns, costs, targeting) are `10_systems/SKILL_SYSTEM.md`/`10_systems/INVENTORY.md`; this
doc owns only which physical input triggers which bound action, resolving the bar-size/input
forward reference `10_systems/SKILL_SYSTEM.md` §7 leaves to this doc.

## 1. Default keyboard map

| Action | Primary | Alt |
|---|---|---|
| Move left / right | `A` / `D` | `Left` / `Right` arrow |
| Jump | `Space` | — |
| Drop-through (one-way platform) | `Down`/`S` held + `Space` | `Down` arrow + `Space` |
| Climb up / down | `W` / `S` (context: near a climbable) | `Up` / `Down` arrow |
| Interact | `E` | — |
| Attack (basic) | Left Mouse Button | — |
| Dodge (dedicated mobility slot, §3) | `Left Shift` | — |
| Skill slots 1–8 | `1`–`8` | — |
| Quickslots 1–4 (use items) | `F1`–`F4` | — |
| Aim / reticle (`aoe_circle`/`projectile` ground-target, `10_systems/SKILL_SYSTEM.md` §6) | Mouse position | — |
| Toggle Inventory | `I` | — |
| Toggle Skills/Character | `K` | — |
| Toggle Quest Log (`frame_quest`) | `L` | — |
| Toggle Map | `M` | — |
| Toggle Guild | `G` | — |
| Toggle Party (the party-finder Board tab lives inside it — `10_systems/UI_WINDOWS.md` §4, `10_systems/social/PARTY_FINDER.md`) | `P` | — |
| Chat focus | `Enter` | — |
| Close / back (topmost framed window) | `Escape` | — |
| Toggle fullscreen (`display_mode`, `10_systems/DISPLAY.md` §3) | `Alt+Enter` | — |

Facing (which way the character/attacks/aim point) follows the mouse-cursor side of the
character when a mouse is present; absent horizontal aim input, facing follows the last-pressed
move direction. Drop-through and climb share the `Down`/`Up` keys with movement — context
(standing on a one-way platform + `Space`, vs. adjacent to a climbable) disambiguates them; no
separate keys are bound for these context-sensitive actions.

## 2. Default gamepad map (Xbox naming; PlayStation equivalent in parens)

| Action | Button |
|---|---|
| Move / climb up-down | Left Stick |
| Jump | `A` (`Cross`) |
| Attack (basic) | `X` (`Square`) |
| Interact | `Y` (`Triangle`) |
| Dodge | `B` (`Circle`) |
| Skill slots 1–4 | D-Pad (Up/Right/Down/Left) |
| Skill slots 5–8 | `LB`/`L1` held + D-Pad |
| Quickslots 1–4 | `RB`/`R1` held + D-Pad |
| Aim / reticle | Right Stick |
| Menu hub (Inventory/Skills/Quests/Map/Guild/Party) | `Start`/`Options` |
| Tab-switch within an open menu | `LB`/`RB` |
| Confirm / select (in menu) | `A` |
| Back / close (in menu) | `B` |
| Context action (in menu — e.g. quick-use, abandon) | `Y` |

`Start`/`Options` opens a single tabbed menu hub rather than six separate dedicated buttons
(gamepads don't have six free buttons to spare); once inside, `LB`/`RB` cycle the same six
panels keyboard reaches via §1's individual keys. `LT`/`RT` (`L2`/`R2`) and `Back`/`View` are
**unassigned at launch** (Open Questions). Chat has no gamepad text-entry path at launch — see
Open Questions and `10_systems/social/CHAT.md` (stub).

## 3. The Dodge slot

Per `10_systems/SKILL_SYSTEM.md` §7 ("dedicated inputs for basic attack, dodge, and jump"), Dodge
is a **9th, separate slot** from the 8 general skill slots — its own binding (`Left Shift` /
`B`/`Circle`), holding exactly one player-assigned mobility skill (e.g. `skill_novice_002` Tumble,
`skill_keeneye_003` Backstep, `skill_flicker_002` Shadowstep) so a character's core evade never
competes with combat-skill bar space. This doc owns only the input binding; which skills are
eligible for the Dodge slot (presumably `dash`/`leap`-op skills, `10_systems/SKILL_EFFECTS.md`
§9–§10) and its re-slotting rule are `10_systems/SKILL_SYSTEM.md`'s to confirm (Open Questions).

## 3.1 Combo input model — sequences, not chords

The combo layer (`10_systems/COMBO_SYSTEM.md`) adds **no bindings and no chords**: a combo is
the player's existing inputs pressed in *sequence* — e.g. basic attack (LMB / `X`) → skill `2`
(D-Pad Right) → skill `3` (D-Pad Down) inside the chain window. This is a deliberate input-design
choice over held-modifier chords (`Ctrl`+key patterns): sequences keep every action on its §1/§2
binding, stay fully rebindable under §5, and work identically on gamepad, where no spare modifier
exists beyond the §2 bumper banks. Sequencing respects each skill's own cast/recovery lock
(`10_systems/SKILL_SYSTEM.md` §5); there is no extra combo input buffer at launch (Open
Questions). Chain rules, timing, and rewards are entirely `10_systems/COMBO_SYSTEM.md`'s — this
doc owns only the statement that combos ride the ordinary input map.

## 4. Input buffering windows

| Window | Value | Meaning |
|---|---|---|
| Jump buffer | **0.10 s** | A jump pressed up to 0.10 s *before* landing is queued and fires on landing. |
| Coyote time | **0.08 s** | A jump pressed up to 0.08 s *after* walking off a ledge still succeeds as if grounded. |

Both are client-side input-feel windows (`10_systems/PERSISTENCE.md` authority: `client`) layered
on top of, not a replacement for, the movement/physics the engine resolves; they exist purely so a
frame-perfect input never feels punished (`00_vision/PILLARS.md` P1).

## 5. Rebinding policy

- **Keyboard: fully rebindable**, any single action to any key, with a conflict warning (not a
  hard block) on duplicate assignment.
- **Gamepad: face-button roles only** — `A`/`X`/`Y`/`B` may be reassigned among themselves (e.g.
  swap Attack and Interact); the D-Pad skill-bank + bumper-modifier structure, the stick roles,
  and the Menu-hub button are **fixed** to keep the controller layout learnable and support-able.
- Rebind state is per-account client config, **not** per character (`10_systems/PERSISTENCE.md`
  authority: `client`) — it does not live in a character save slot.

## 6. Controller navigation of framed UI

Opening any toggle window (`10_systems/HUD.md`'s `frame_window`/`frame_dialog`/`frame_quest`
panels) repurposes the Left Stick/D-Pad from gameplay to UI focus movement for as long as that
window is topmost:

| Input | UI action |
|---|---|
| Left Stick / D-Pad | Move focus between rows/slots/buttons in the topmost window |
| `A` | Confirm / select the focused element |
| `B` | Back one level, or close the topmost window if already at its root |
| `LB` / `RB` | Switch tabs (e.g. Inventory's `equip`/`use`/`etc` tabs, `10_systems/INVENTORY.md` §1) |
| `Y` | Context action on the focused element (quick-use an item, abandon the selected quest, etc.) |

In the interim solo build, opening a full toggle window **pauses world simulation** (consistent
with `10_systems/SKILL_SYSTEM.md` §5's "cooldowns pause with the game (solo)" note) — a solo-only
convenience that does not hold once the client runs against a live, server-authoritative world.

## Open Questions

- `LT`/`RT` and `Back`/`View` are reserved, unassigned gamepad inputs; candidates raised but not
  decided: a future targeting-cycle, a block/parry mechanic, or a quick-map toggle. Flag for a
  playtesting pass.
- Gamepad chat entry (on-screen keyboard, quick-phrase wheel, or none at launch) is undecided;
  owner `10_systems/social/CHAT.md` once authored.
- Dodge-slot skill eligibility (which skills may be assigned there) and whether re-slotting it
  costs anything are `10_systems/SKILL_SYSTEM.md`'s open call (§3 above); this doc assumes free
  re-slotting matching that doc's §7 general skill-bar policy.
- Exact jump-buffer/coyote-time values (§4) are first-pass, chosen at the high end of typical
  platformer feel; retune after playtesting against `10_systems/COMBAT_FORMULA.md` §10's cadence
  once real frame timing is measured.
- Whether keyboard-only players (no mouse) get a fixed-facing-range aim fallback beyond "last
  move direction" is not specified; flag if playtesting shows aiming `aoe_circle`/`projectile`
  skills without a mouse feels imprecise.
- Mouse-and-keyboard vs. gamepad simultaneous hot-swap mid-session (common in PC action games) is
  assumed supported (last-used device drives on-screen prompts) but not detailed here.
- Whether a skill input pressed during another skill's recovery should queue into a short combo
  buffer (like §4's jump buffer, so a tight chain never drops to a swallowed press) is deferred
  to playtesting with `10_systems/COMBO_SYSTEM.md`'s window; launch behavior is no buffer —
  presses during the cast/recovery lock are ignored.
