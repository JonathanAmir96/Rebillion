# ACCOUNT.md — Roster Screen & Character Creation Flow (Player-Facing)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/PERSISTENCE.md, 10_systems/JOBS.md, 10_systems/HUD.md, 10_systems/CONTROLS.md,
40_assets/CHARACTER_COMPOSITING.md, 70_integrations/ACCOUNTS_AUTH.md, docs/WORLD_PLAN.md,
docs/VALIDATION.md

Owner doc for the **player-facing entry flow**: the roster screen a user lands on, the
character-creation steps (nickname check → appearance → confirm), and the identity fields
creation mints. Authorized by owner directive 2026-07-24. The backend truths this flow sits
on are owned elsewhere and only cited here: account/credential model, the **4-slot quota**,
and one-way import (`70_integrations/ACCOUNTS_AUTH.md` §2, quota raised 3→4 by the same
directive); the **character name law** (`70_integrations/ACCOUNTS_AUTH.md` §5 — format,
uniqueness, gates, and rename all live there); save-slot storage and authority tags
(`10_systems/PERSISTENCE.md` §2/§6); job rules (`10_systems/JOBS.md`); appearance parts
(`40_assets/CHARACTER_COMPOSITING.md`). Nothing in those docs is restated as law here.

## 1. Entry: the roster screen

On launch (interim solo build: one install = one implicit account,
`70_integrations/ACCOUNTS_AUTH.md` §7; live build: after login, §3.3/§4.1 there) the player
lands on the **roster screen**: up to **4 characters** (`70_integrations/ACCOUNTS_AUTH.md`
§2.2, the quota's single source of truth), each entry showing nickname, `level`, job display
name (`10_systems/JOBS.md`), and the composited sprite in `idle`
(`40_assets/CHARACTER_COMPOSITING.md`). Empty slots offer **Create**. Selecting a character
enters the world; there is no gameplay outside a selected character. Slot deletion (explicit
type-the-nickname confirmation — destructive, no undo) frees the slot and releases the name
back into the pool, per `70_integrations/ACCOUNTS_AUTH.md` §4.1/§5.

## 2. Creation flow (three steps)

Linear, cancellable at any point (cancel returns to the roster; any name reservation held for
the creation session is released — an availability answer is session-scoped, never a
permanent hold):

1. **Nickname** — text entry plus an explicit **"check name"** action returning a binary
   taken/available answer, in the classic side-scrolling-MMO pattern. The answer comes from
   the authority holder through the `GameState` facade (`10_systems/PERSISTENCE.md` §5):
   interim solo build, a check against the install's own roster (the only namespace that
   exists — trivially cheap, but routed through the same call so the code path is already
   server-shaped); live build, the same call is the server-side global-uniqueness check
   (`70_integrations/ACCOUNTS_AUTH.md` §5 — format, reserved names, and profanity gates all
   run there, never client-side). Advancing requires an available answer.
2. **Appearance** — pick hair, face, hair color, skin tone
   (`40_assets/CHARACTER_COMPOSITING.md` §7), previewed live on the composited sprite. No
   job choice exists here: every character begins `novice` (`10_systems/JOBS.md`), and job
   identity emerges at the Lv 8 advancement — creation is deliberately identity-light.
3. **Confirm** — the record (§3) is minted through the facade, the slot fills, and the
   character enters the world at the starter spawn (`docs/WORLD_PLAN.md` `map_001`).

## 3. What creation mints (identity fields)

The identity slice of the per-character record — everything else stays owned by the docs in
`10_systems/PERSISTENCE.md` §2's table, and the character's server identity is a
server-minted opaque id, never a `docs/ID_REGISTRY.md` content id
(`70_integrations/ACCOUNTS_AUTH.md` §2.1):

| Field | Rule | Authority |
|---|---|---|
| `nickname` | law: `70_integrations/ACCOUNTS_AUTH.md` §5 (rename exists there too — re-runs the full gate) | `server` |
| `job` | starts `novice`, advances per `10_systems/JOBS.md` | `server` |
| appearance (`style_hair_NN`, `style_face_NN`, `style_haircolor_NN`, `style_skin_NN`) | one of each, valid per `docs/ID_REGISTRY.md` ranges (`40_assets/CHARACTER_COMPOSITING.md` §7) | `server` |
| `created_at` | set once at creation | `server` |

## Open Questions

- **Roster/creation screen UI spec.** `40_assets/UI_ART_SPEC.md` is change-controlled; the
  two screens (roster + creation, including the "check name" widget and live appearance
  preview) need an entry through its amendment channel before the coding pass builds them.
- **Name-check UX for the live build:** the wire pair exists
  (`70_integrations/NETWORK_PROTOCOL.md` §9.2 `op_0105`/`op_0194`, creation itself
  `op_0103`/`op_0193` with the appearance picks); what remains open is debounce/rate-limit
  on the probe and the reservation TTL — gateway concerns, flagged there, not designed here.
- **Deleted-character grace period** (undo window before a delete is final) is deliberately
  absent this run; if live-ops wants one, it lands in `70_integrations/ACCOUNTS_AUTH.md`'s
  account model, and this screen only reflects it.
