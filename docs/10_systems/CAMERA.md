# CAMERA.md — Side-Scroll Camera Behavior

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/CONTROLS.md, 10_systems/HUD.md, 10_systems/AI_BEHAVIOR.md, 10_systems/SKILL_EFFECTS.md,
10_systems/PERSISTENCE.md, 15_maps_system/MAP_LAYERS.md, 15_maps_system/MAPS_SYSTEM.md,
40_assets/ART_BIBLE.yaml

Owner doc for the **player camera**: the deadzone, facing lookahead, vertical platform-snap
(anti-bob), map-bounds clamping, pixel snapping/zoom policy, arena-lock behavior, and the
screen-shake budget. Parallax layer definitions are `15_maps_system/MAP_LAYERS.md`; this doc
owns only that the camera's tracked position is what those layers scale against. World-space
distances (deadzone, lookahead, bounds) are in **tiles** (`40_assets/ART_BIBLE.yaml` grid unit) —
the tile→pixel scale is not yet locked (open across this tree, e.g.
`10_systems/COMBAT_FORMULA.md` §10). Screen-shake amplitude (§7) is a rendering-layer offset, not
a world distance, so it is given as a small raw-pixel placeholder instead, matching how
`10_systems/COMBAT_FORMULA.md` §10–§11 and `10_systems/INVENTORY.md` §4 already flag their own
px placeholders pending the same lock.

## 1. Deadzone

A rectangle centered on the player within which player movement does **not** pan the camera; the
camera only starts tracking once the player crosses the deadzone's edge.

| Axis | Size |
|---|---|
| Width | 6 tiles |
| Height | 3 tiles |

Vertical is deliberately tighter than horizontal (§3 relies on it to suppress jump-bob).

## 2. Horizontal lookahead (facing direction)

While the player moves continuously in one horizontal direction, the camera eases toward an
additional offset **beyond** the deadzone, in the facing direction, so more of what's ahead is
visible (P1 readability of incoming threats).

| Parameter | Value |
|---|---|
| Max lookahead distance | 3 tiles |
| Ease-in time (reach max) | 0.5 s of continuous one-direction movement |
| Ease-out time (relax to 0) | 0.3 s after stopping or reversing direction |

Ease-out is faster than ease-in on purpose — a direction change should feel responsive, not laggy.

## 3. Vertical platform-snap (grounded-follow)

The camera's vertical anchor tracks the player's **last-grounded** Y position, not their raw,
moment-to-moment Y — so an ordinary jump/fall arc does not bob the camera up and down every hop.

- While airborne, the vertical anchor holds at the last-grounded Y **unless** the player's actual
  Y position exceeds the height-1 deadzone (§1, 3 tiles) from that anchor — a long fall or a
  climb re-engages normal vertical tracking so the camera doesn't lose the player.
- On landing (grounded again, possibly at a different platform height), the anchor re-centers to
  the new grounded Y via a **0.25 s** lerp, not an instant cut.

## 4. Map-bounds clamping

The camera's viewport never shows beyond a map's authored bounds rect (top/bottom/left/right, in
tiles), adjusted for half the viewport's extent so the edge of the map sits flush with the edge
of the screen rather than centering past it. The bounds rect itself is per-map authored data
(`15_maps_system/MAPS_SYSTEM.md`, not yet written) — this doc owns only the clamp behavior that
consumes it.

## 5. Pixel snapping & zoom

- The camera's final render position is **rounded to whole pixels** every frame — no sub-pixel
  camera position — to keep pixel art crisp (`40_assets/ART_BIBLE.yaml` identity).
- **Zoom is an integer multiple only** (1×, 2×, 3×, …); no fractional zoom, and zoom does not
  change dynamically during play (no per-encounter zoom-out effect at launch). The exact default
  multiplier is pending the `40_assets/ART_BIBLE.yaml` tile-scale lock (Open Questions).

## 6. Arena camera lock

Entering an `arena`-type map (`00_vision/GLOSSARY.md` map types), or any map zone flagged as an
arena-lock trigger, switches the camera from normal deadzone-follow to a **locked** mode:

| Behavior | Normal | Arena-locked |
|---|---|---|
| Effective bounds (§4) | Full map rect | The arena's own rect, not the full map |
| Horizontal lookahead (§2) | Active | **Disabled** |
| Vertical platform-snap lerp (§3) | 0.25 s ease | **Disabled** — immediate vertical tracking |

The tighter, un-eased tracking keeps boss telegraphs and arena hazards readable at all times (P1)
— readability over camera smoothness during a fight that matters. The lock releases back to
normal on the boss's death or the player exiting the arena. **Which map/zone triggers the lock,
and the arena's rect, are authored data owned by `15_maps_system/MAPS_SYSTEM.md`** (not yet
written); this doc owns only what the camera *does* once locked, per
`10_systems/AI_BEHAVIOR.md` §15's note that arena-side camera-lock authoring lives in the map
file. A boss `phase_shift` transition (`10_systems/AI_BEHAVIOR.md` §15) may trigger a screen-shake
pulse (§7) but does not itself alter the lock framing.

## 7. Screen-shake budget (small, tiered)

A decaying random-jitter offset applied **after** the tracked camera position (deadzone +
lookahead + platform-snap + clamp, §1–§4) — a pure additive on top, so shake never feeds back into
the tracking math. Only the strongest active tier applies at any moment; shakes do **not** stack.

| Tier | Trigger | Amplitude | Duration |
|---|---|---|---|
| Hit | A `Heavy`-class hit lands on or from the player (`10_systems/COMBAT_FORMULA.md` §11: crit, a `knockback`-op skill, or ≥8% target max `life`) | 2 px | 0.08 s |
| Crit | The hit was a critical (supersedes the Hit tier, does not add to it) | 4 px | 0.12 s |
| Boss slam | A boss/elite ability explicitly flagged for it in its own data | 8 px | 0.25 s |

Ordinary (`Light`-class) hits cause **no** shake — constant jitter from routine combat would hurt
readability, not sell impact (P1). The "boss slam" flag is authored per-ability; the field itself
is owned by `10_systems/SKILL_EFFECTS.md`/`10_systems/AI_BEHAVIOR.md` (Open Questions) — this doc
defines only the resulting camera behavior once that flag fires.

## 8. Parallax coupling

The camera's tracked position (including the §7 shake offset — it is not excluded) is the single
input `15_maps_system/MAP_LAYERS.md`'s background layers scale their own motion against, each at
its own authored fraction of camera delta. This doc asserts only that the coupling point is "the
camera's final per-frame position"; per-layer speed multipliers, layer count, and any layer-side
exceptions are `15_maps_system/MAP_LAYERS.md`'s to define.

## 9. Authority

Camera position, mode (normal/arena-locked), and shake state are **client-only**
(`10_systems/PERSISTENCE.md` authority: `client`) — purely a local presentation concern, never
synced or validated by a server, even once the game is server-authoritative for gameplay state.

## Open Questions

- Deadzone size, lookahead distance/timing, and the vertical re-center lerp (§1–§3) are first-pass
  values chosen for a readable, non-nauseating feel; retune after playtesting once the tile→pixel
  scale locks (`40_assets/ART_BIBLE.yaml`). The §7 shake-amplitude px values are placeholders for
  the same reason and should be revisited alongside them.
- Default integer zoom multiplier (§5) is not chosen here — it is downstream of the
  `40_assets/ART_BIBLE.yaml` tile-scale lock referenced across this tree
  (e.g. `10_systems/COMBAT_FORMULA.md` §10).
- The "boss slam" screen-shake flag's exact field name/location is not yet defined in
  `10_systems/SKILL_EFFECTS.md` or `10_systems/AI_BEHAVIOR.md`; flagged for whichever doc adds
  ability-presentation metadata.
- Whether non-arena "mini-lock" zones (e.g., a tough elite pack in a dungeon corridor) are used in
  Phase D content, beyond the 8 boss arenas (one per region block; `docs/ID_REGISTRY.md`,
  `docs/WORLD_PLAN.md`), is undecided — the mechanism (§6) supports it either way.
- Ultrawide/uncommon aspect ratios and any camera safe-area guarantee are not addressed; likely an
  `40_assets/ART_BIBLE.yaml`/engineering concern once a target resolution is fixed.
