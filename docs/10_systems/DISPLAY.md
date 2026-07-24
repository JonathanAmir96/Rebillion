# DISPLAY.md — Window Mode & Scaling Policy

References: 00_vision/GLOSSARY.md, 40_assets/ART_BIBLE.yaml, 10_systems/CAMERA.md,
10_systems/HUD.md, 10_systems/CONTROLS.md, 10_systems/PERSISTENCE.md,
30_engineering/ENGINEERING_STANDARDS.md

Owner doc for the game window: display mode, how `40_assets/ART_BIBLE.yaml`'s locked
resolution policy meets a real monitor, and where the setting lives. Authorized by owner
directive 2026-07-24. This is the doc `10_systems/CAMERA.md` §"once a target resolution is
fixed" and `10_systems/HUD.md`'s matching flag were waiting on — the target resolution *is*
fixed (`ART_BIBLE.yaml` `pixel.resolution_policy`: render base 640x360, integer-only scaling,
nearest filter; locked, cited, never restated). This doc owns only the window-mode law around
it.

## 1. Fullscreen by default

The game launches **fullscreen** (owner directive): borderless fullscreen at the desktop
resolution — never exclusive-mode with a display-mode switch, so alt-tab is instant and
multi-monitor setups are undisturbed. A **windowed** mode exists as a toggle (§3), sized to
the largest integer scale that fits the desktop with margin.

## 2. Integer scaling + letterbox

Fullscreen composition per the locked policy: the 640x360 render target scales by the
**largest integer factor** that fits the monitor (1080p → 3x = 1920x1080 exact; 1440p → 4x
= 2560x1440 exact; 4K → 6x), and any remainder letterboxes/pillarboxes in solid `ink`
(`ART_BIBLE.yaml` `palette.neutrals.ink`) — never a non-integer stretch, never a crop
(`resolution_policy.scaling` is integer-only law; `30_engineering/ENGINEERING_STANDARDS.md`'s
pixel-rendering line already binds the coding pass to it). UI renders inside the same 640x360
target (`10_systems/HUD.md` chrome included), so nothing ever draws at a mixed pixel density
(`ART_BIBLE.yaml` `export_contract.forbidden`).

## 3. The setting

| Aspect | Rule |
|---|---|
| Setting | `display_mode`: `fullscreen` (default) \| `windowed` |
| Where | System menu (`10_systems/HUD.md` `frame_system`) + `Alt+Enter` toggle (joins the reserved bindings in `10_systems/CONTROLS.md` §5's client keybind map) |
| Authority | `client` (`10_systems/PERSISTENCE.md` §3) — pure local preference, stored in the account-level client config alongside keybinds/UI prefs (`10_systems/PERSISTENCE.md` §6), never per-character |

## Open Questions

- **Sub-1080p / odd monitors:** below 720p the largest integer factor is 1x (640x360 in a
  large letterbox). Accepted for this run; a fractional-scale escape hatch is deliberately
  not designed (it would break integer-only law) — revisit only if hardware telemetry ever
  demands it.
- **Windowed default size** (largest-fit-with-margin, §1) is a coding-pass heuristic, not a
  design number — flag for Phase E rather than inventing a constant here.
- **Ultrawide:** pillarboxed at integer scale by §2; whether a wider render base ever becomes
  an option is an `ART_BIBLE.yaml` amendment-channel question (resolution policy is locked),
  not this doc's.
