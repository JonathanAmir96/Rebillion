# ACCOUNT.md — Account, Character Roster & Creation Flow

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/PERSISTENCE.md, 10_systems/JOBS.md, 10_systems/HUD.md, 10_systems/CONTROLS.md,
40_assets/CHARACTER_COMPOSITING.md, 30_engineering/ENGINEERING_STANDARDS.md, docs/VALIDATION.md

Owner doc for the **account layer**: the character roster (slot count), the character
**creation flow** a new user walks on first entry, the **nickname law** (format + global
uniqueness check), and the character-record identity fields. Authorized by owner directive
2026-07-24. This fills the seat `10_systems/PERSISTENCE.md` §2 reserved as "(future account
system)" for character identity. It does not own: what is saved or who holds authority
(`10_systems/PERSISTENCE.md`, whose taxonomy this doc uses), job/advancement rules
(`10_systems/JOBS.md`), appearance parts and their IDs
(`40_assets/CHARACTER_COMPOSITING.md`), or any login/network protocol (out of this run's
scope, `00_vision/SCOPE.md` — the interim build treats one install as one account).

## 1. Account model (interim solo build)

One install = one account. There is no username/password, registration, or online login in
this run (`00_vision/SCOPE.md` excludes networking/backend); the account is implicit, and its
data is the roster (§2) plus the shared account-level client config
(`10_systems/PERSISTENCE.md` §6 — keybinds/UI prefs are account-level, not per-character).
Everything in this doc is written against the `GameState` facade boundary
(`10_systems/PERSISTENCE.md` §5) so a real account service can replace the local store without
touching calling code — the solo build is a rehearsal for the boundary, not an exception.

## 2. Character roster — 4 slots

An account holds up to **4 characters** (owner directive 2026-07-24; supersedes the earlier
3-slot figure — `10_systems/PERSISTENCE.md` §6 now cites this section as the roster owner).
Each slot is one independent character with its own full `server`-tagged state
(`10_systems/PERSISTENCE.md` §2). On launch the player lands on the **roster screen**: up to
4 entries, each showing nickname, `level`, job display name (`10_systems/JOBS.md`), and the
composited sprite in `idle` (`40_assets/CHARACTER_COMPOSITING.md`); empty slots offer
**Create**. Selecting a character enters the world; there is no gameplay outside a selected
character.

- **Deletion** frees the slot after an explicit type-the-nickname confirmation (a destructive,
  irreversible act — no soft-delete/undo this run). Whether the freed nickname releases
  immediately or after a cooldown is an Open Question.
- Slot count is a design cap, not a technical one; raising it is an ordinary revision to this
  section, never a silent change elsewhere.

## 3. Character record — identity fields

The identity slice of the per-character record (everything else stays owned by the docs in
`10_systems/PERSISTENCE.md` §2's table):

| Field | Rule | Authority |
|---|---|---|
| `nickname` | §4 law; immutable this run (no rename — Open Question) | `server` |
| `job` | starts `novice`, advances per `10_systems/JOBS.md` | `server` |
| appearance (`style_hair_NN`, `style_face_NN`, `style_haircolor_NN`, `style_skin_NN`) | one of each, valid per `docs/ID_REGISTRY.md` ranges; chosen at creation (`40_assets/CHARACTER_COMPOSITING.md` §7) | `server` |
| `created_at` | set once at creation | `server` |

## 4. Nickname law

- **Format:** 4–12 characters, letters and digits only, must start with a letter
  (`^[A-Za-z][A-Za-z0-9]{3,11}$`). No spaces, punctuation, or non-ASCII this run (bitmap font
  scope, `40_assets/ART_BIBLE.yaml` `ui.font`; revisit with localization, which
  `00_vision/SCOPE.md` excludes).
- **Display is case-preserving; uniqueness is case-insensitive** — `Rebill` and `rebill` are
  the same name.
- **Uniqueness is global** (one namespace across all accounts and characters), decided by the
  authority holder at creation time: the creation UI asks **"check name"** and gets a binary
  taken/available answer, in the classic side-scrolling-MMO pattern. An available answer is a
  short-lived reservation for the creation session only, released on cancel — never a
  permanent hold.
- **Who answers the check:** the `GameState` facade (`10_systems/PERSISTENCE.md` §5). Interim
  solo build: it checks the local install's roster (the only namespace that exists — a
  4-slot local check is trivially cheap but runs through the same call so the code path is
  already server-shaped). Live build: the same call becomes a server database lookup, per the
  `server` authority tag — the client **never** decides availability itself
  (`10_systems/PERSISTENCE.md` §7 spirit: no self-assigned `server` values).
- **Reserved names:** NPC display names in shipped content and system terms (e.g. "GM"-style
  staff prefixes) are refused as exact case-insensitive matches. The concrete reserved/
  profanity list is deliberately not authored in this tree (Open Question — live-ops data,
  not design canon).

## 5. Creation flow (new user, first entry)

Linear, three steps, cancellable at any point (cancel returns to the roster and releases any
name reservation):

1. **Nickname** — text entry + "check name" (§4); advancing requires an available answer.
2. **Appearance** — pick hair, face, hair color, skin tone
   (`40_assets/CHARACTER_COMPOSITING.md` §7; the four choices in §3's record), previewed live
   on the composited sprite. No job choice exists here: every character begins `novice`
   (`10_systems/JOBS.md`), and job identity emerges at the Lv 8 advancement — creation is
   deliberately identity-light.
3. **Confirm** — the record (§3) is minted through the facade, the slot fills, and the
   character enters the world at the starter spawn (`docs/WORLD_PLAN.md` `map_001`).

Screen layout/art for roster and creation UI is `40_assets/UI_ART_SPEC.md` territory (locked;
its amendment channel — Open Question there, not here).

## Open Questions

- **Freed-nickname policy on deletion** (§2): immediate release vs. cooldown (a cooldown
  frustrates squatting-recycling but needs a timer the interim build must persist). Default
  leaning: immediate release in the solo build (single-install namespace makes squatting
  moot), cooldown decided when a real server lands.
- **Rename service** (§3): deliberately absent this run; if a future arc adds one, it is a
  `server`-authoritative operation with the same §4 check, and its price/cooldown belongs to
  `10_systems/ECONOMY.md`.
- **Reserved/profanity name list** (§4): live-ops data outside design canon — flag for the
  future server-onboarding doc alongside `10_systems/PERSISTENCE.md` §9's import pass.
- **Roster screen & creation UI spec** (§5): `40_assets/UI_ART_SPEC.md` is locked; the two
  screens need an entry through its amendment channel before the coding pass builds them.
- **Account-level unlocks** (future): nothing account-scoped exists this run beyond client
  config; if account-shared anything arrives (vault, cosmetics), it lands here first, per
  `10_systems/PERSISTENCE.md`'s Open Question on account-shared purses.
