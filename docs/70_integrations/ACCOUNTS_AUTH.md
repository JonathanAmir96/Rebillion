# ACCOUNTS_AUTH.md — Account Model, Session Security & Name Policy

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, 10_systems/PERSISTENCE.md, 10_systems/social/CHAT.md,
10_systems/social/GUILD.md, 30_engineering/ENGINEERING_STANDARDS.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/TELEMETRY_ANALYTICS.md

Owner doc for the **future account system** — the entity `10_systems/PERSISTENCE.md` §2 names as
"Character identity → (future account system)" and defers to here. It designs the account/character
split, credential and session lifecycle, and the character-name policy. It is design only: no code,
no secrets, no cryptographic parameters (`30_engineering/ENGINEERING_STANDARDS.md`, locked — cited,
never edited; the server-authoritative boundary it draws is the boundary this doc satisfies). The
concrete auth-service and gateway components live in `70_integrations/BACKEND_ARCHITECTURE.md`
(sibling, authored this wave); the analytics/PII processing seam lives in
`70_integrations/TELEMETRY_ANALYTICS.md` (sibling, this wave). This doc restates neither — it fixes
the account-layer contract and hands the wiring to those siblings.

## 1. Scope & relationship to PERSISTENCE

`10_systems/PERSISTENCE.md` owns **per-character save state** (its §2 truth ledger) and the
`GameState` facade the solo build writes through. This doc owns the layer **above** that facade: the
account a character belongs to, and the credential/session machinery that proves a client may act as
that account. Nothing here is a save-slot field; account records never live in a character save file
and are never editable by whoever holds a client install (contrast `10_systems/PERSISTENCE.md` §9,
where a local save *is* attacker-editable — that is exactly why import must be re-validated
server-side). Every stored field this doc introduces carries a `10_systems/PERSISTENCE.md` §1
authority tag; the mapping is §8.

## 2. Account model

Two entities, one relationship:

- **Account** — the credential-bearing root: a login identity, its authentication material, and a
  roster of characters. One human, one account (enforcement is a live-ops matter, not designed here).
  An account holds no game-world stats; it holds only who-you-are-to-log-in and what-you-own.
- **Character** — a single playable identity: the `10_systems/PERSISTENCE.md` §2 server-authoritative
  bundle (`level`/`exp`, primary stats, inventory, `shards` wallet, quest flags, skill ranks, bind
  point, guild/party membership). A character belongs to exactly one account and cannot be moved
  between accounts (Open Questions covers gifting/transfer).

**Character slots.** An account has **3 character slots at launch**, matching `10_systems/PERSISTENCE.md`
§6's 3 local save slots exactly — this is deliberate, so the interim solo build's slot shape and the
live account's slot shape are identical and migration is a re-homing, not a reshaping. Slot expansion
beyond 3 is a **future monetization question** and is **not decided here** (Open Questions); the schema
must not hard-code 3 as a structural limit (it is a per-account quota, server-owned).

**Migration story (local slots → account-bound characters).** The interim build stores each character
in a local save slot (`10_systems/PERSISTENCE.md` §5–§6). When a live account system exists, each
local character is imported **once, one-way, upon binding to an account**, reusing
`10_systems/PERSISTENCE.md` §9's offline→online import (never the reverse; a live character never
exports back to a local save). The import's validation/sanitization pass is
`10_systems/PERSISTENCE.md` §9's open item, not re-opened here — this doc only asserts that the
3-slot symmetry means an install's 3 locals map cleanly onto an account's 3 slots.

## 3. Authentication

**Credential options.**

- **Baseline: email + password.** Email is the account handle; it is minimal PII (§6). This is the one
  credential path the design assumes always exists.
- **Platform / storefront SSO — integration points, not launch commitments.** Console/platform accounts
  and PC-storefront sign-in are designed as *seams* that attach to an account (federated identity), so
  a single account may carry email/password plus zero or more linked identities. Which providers,
  and their token-exchange contracts, are `70_integrations/BACKEND_ARCHITECTURE.md`'s to wire and the
  owner's to price (Open Questions). No provider is assumed present.

**Token / session lifecycle.**

- Sign-in issues a **short-lived session token** (a bearer credential the client presents on each
  request) plus a longer-lived **refresh token** used only to mint a new session token when it expires.
  Concrete lifetimes/algorithms are `70_integrations/BACKEND_ARCHITECTURE.md`'s; this doc fixes the
  *shape* (short session, refresh-to-renew) and the invariants below.
- **Single active game session per account.** At most one in-world session may be live for an account
  at a time (§4 governs what happens on a second sign-in). Web/companion read-only surfaces, if any,
  are out of scope here.
- **Revocation is first-class.** Sign-out, password change, and an account-security action all
  invalidate outstanding refresh tokens; a revoked session cannot be renewed and its next request
  fails closed. The server is the sole authority on token validity — a client may never treat a token
  it holds as proof of anything the server has revoked (`00_vision/PILLARS.md` P6).

**Rate limiting & lockout (stance).** Sign-in attempts are rate-limited per account and per source, and
repeated failures trigger a temporary, escalating lockout rather than a permanent lock (a permanent
lock is a denial-of-service lever against a known email). Exact thresholds/windows are operational and
belong to `70_integrations/BACKEND_ARCHITECTURE.md` runbooks (Open Questions), not designed here.

**Password storage (stance, no parameters).** Passwords are never stored recoverably. They are stored
only as the output of a **modern memory-hard adaptive password-hashing function** (the Argon2 family
is the practice named here), each with a unique per-credential salt. No work factors, no memory/time
parameters, no algorithm version, and no code appear in this design tree — those are set and rotated in
`70_integrations/BACKEND_ARCHITECTURE.md`/ops, from environment-managed configuration, never committed.

## 4. Session security

- **Gateway binding.** An in-world session is bound to the connection through the game **gateway**
  described in `70_integrations/BACKEND_ARCHITECTURE.md` (that doc owns the gateway component; this doc
  owns only the account-side contract it enforces): the gateway validates the session token on connect,
  associates the live connection with the account + active character, and rejects world traffic whose
  token is missing, expired, or revoked (§3). The gateway is the single choke point where "is this
  connection allowed to act as this character?" is answered.
- **Reconnect grace.** A dropped connection does not immediately end the game session: the account's
  in-world session persists for a short **reconnect grace window** during which the same account may
  resume the same character without a full re-sign-in, so a transient network blip is not a logout.
  The window length is `70_integrations/BACKEND_ARCHITECTURE.md`'s to set (Open Questions).
- **Kick-on-second-login.** Because at most one game session per account is allowed (§3), a *successful*
  new sign-in for an account that already has a live (or in-grace) session **displaces** the older one:
  the newer authenticated session wins and the older connection is disconnected with a clear reason.
  This resolves the stolen-credential and stuck-session cases predictably. It is displacement by a
  fully-authenticated login only — an unauthenticated reconnect attempt never displaces a live session.

## 5. Character name policy

- **Uniqueness scope.** A character name is **globally unique across the live world** at creation time
  (server-enforced), mirroring `10_systems/social/GUILD.md` §2's global-uniqueness stance for guild
  names — names surface in social contexts (`10_systems/social/CHAT.md` speech bubbles/whispers,
  `10_systems/social/GUILD.md` rosters) where two identical names would be a real impersonation vector.
  In the interim solo build there is no global namespace to check against (§7).
- **Allowed set & length.** Letters and digits, **3–12 characters**, no spaces, no leading/trailing or
  repeated punctuation; one script/alphabet per name (US English, `00_vision/SCOPE.md` — no
  localization this run). The exact grapheme whitelist is confirmed at implementation; the design fixes
  the 3–12 bound and the no-spaces rule (character names, unlike guild names in
  `10_systems/social/GUILD.md` §2, do **not** permit spaces or apostrophes — a single-word handle reads
  cleaner in a speech bubble).
- **Reserved names.** Creation rejects, case-insensitively and with common look-alike substitutions
  folded: NPC, boss, town, and region names from `docs/WORLD_PLAN.md` (e.g. town names such as
  Millbrook, and boss names such as Cindermaw) and job-instructor names; staff/official titles and any
  "admin/mod/system/GM/official" family (staff-impersonation guard); and a reserved technical set
  (empty, whitespace-only, reserved words). `docs/WORLD_PLAN.md` remains the authority for the world's
  proper nouns — this doc references that list rather than copying it, so it never drifts.
- **Profanity / impersonation filtering (stance).** A name is passed through a profanity/slur filter
  and the reserved/look-alike checks above; the concrete wordlist and match rules are a **live-ops
  policy applied server-side**, deliberately not authored in this tree (matching
  `10_systems/social/GUILD.md` §2's identical deferral). Filtering is a creation-time gate plus a
  post-hoc report/rename channel — not a promise of perfection.
- **Rename policy.** A character may be renamed after creation; a rename re-runs the full §5 gate
  (uniqueness, allowed set, reserved, profanity) and frees the old name back into the pool. Whether a
  rename costs `shards`, is throttled, or is a paid convenience is a monetization/economy question and
  is **not decided here** (Open Questions) — the mechanism is designed, the price is not.

## 6. Account data & privacy

- **Minimal PII.** An account stores the least identifying data that lets someone sign in and recover
  access: the account handle (email), authentication material (§3, hashed — never the password),
  linked-identity references for SSO (§3), and account-lifecycle timestamps. No real name, address, or
  payment data is designed into the account record here; anything payment-adjacent belongs to a
  storefront/monetization design not in this run's scope (`00_vision/SCOPE.md`).
- **Deletion & export posture.** The design assumes a data-subject **deletion** path (account +
  characters purged or irreversibly anonymized) and an **export** path (a machine-readable dump of an
  account's own data). Deletion of *analytics/telemetry* data and any pseudonymization boundary is
  `70_integrations/TELEMETRY_ANALYTICS.md`'s (sibling, this wave) — this doc owns deletion of the
  *account/character* records, that sibling owns the behavioral-data side, and the two must agree on a
  single delete signal (Open Questions). Retention windows are operational, not fixed here.

## 7. Interim solo build & "implemented when"

Per the role contract, **none of §2–§6 ships in the interim solo build** — there is no server, no
network account, no global name namespace, and no session gateway to bind to
(`00_vision/SCOPE.md` excludes networking/backend; `10_systems/PERSISTENCE.md` §5's facade is local).
The **one** thing that ships now is the **forward-compatible character-identity shape**: each local
character already carries a stable identity (a character id from `docs/ID_REGISTRY.md`'s scheme and a
name field validated against the §5 *format* rules that need no server — allowed set, length, reserved
static proper-noun list from `docs/WORLD_PLAN.md`), so that when an account system lands, binding a
local character to an account is a re-homing (§2) and not a reshape. The name-*uniqueness* check (§5),
all of authentication (§3), all of session security (§4), and the privacy paths (§6) are dormant until
a server exists.

**Implemented when:** a live authoritative server / gateway exists to own the account namespace and
adjudicate sessions — i.e. when `70_integrations/BACKEND_ARCHITECTURE.md` moves from design to a
running service and `10_systems/PERSISTENCE.md`'s server-authority tags become real rather than
rehearsed. Until then this doc is a forward contract, not a build target.

## 8. Field → authority-tag map

Per role contract, every stored field maps to a `10_systems/PERSISTENCE.md` §1 tag. Account-layer
records sit above the per-character `GameState` facade; they are all `authority: server` because they
are truth no client may mint or hold — the client only ever holds a bearer copy of a token the server
can revoke (§3).

| Field | Owner | Authority tag |
|---|---|---|
| Account handle (email) | this doc §2/§6 | `server` |
| Password hash + salt | this doc §3 | `server` (never on client) |
| Linked SSO identity refs | this doc §3 | `server` |
| Character-slot roster + quota | this doc §2 | `server` |
| Character identity (id, name, account binding) | this doc §5 / `10_systems/PERSISTENCE.md` §2 | `server` |
| Per-character game state (`level`, stats, inventory, `shards`, …) | `10_systems/PERSISTENCE.md` §2 | `server` |
| Session token (client-held bearer copy) | this doc §3 | `server`-issued, advisory on client (never authoritative) |
| "Remember me" / last-used-handle UI convenience | this doc §3 | `client` (`10_systems/PERSISTENCE.md` §3 — local preference only) |

## Open Questions

- **Slot expansion & pricing.** Whether accounts can buy character slots beyond 3, and at what price,
  is a monetization decision deferred to the owner (`00_vision/SCOPE.md` lists none planned this run).
  The schema keeps 3 as a server-owned quota, not a structural cap, so raising it is data.
- **SSO providers.** Which platform/storefront identities are supported, and their token-exchange
  contracts, are owner/vendor-priced and `70_integrations/BACKEND_ARCHITECTURE.md`'s to wire.
- **Rate-limit / lockout / reconnect-grace / session-lifetime numbers (§3–§4)** are operational and
  belong to `70_integrations/BACKEND_ARCHITECTURE.md` runbooks, not this design doc.
- **Character transfer/gifting.** §2 forbids moving a character between accounts; whether a future
  paid transfer or account-merge path exists is undecided.
- **Rename cost/throttle (§5).** Mechanism designed, price/throttle not — joint with
  `10_systems/ECONOMY.md`'s sink budget if it ever costs `shards`.
- **Unified delete signal (§6).** This doc (account/character deletion) and
  `70_integrations/TELEMETRY_ANALYTICS.md` (behavioral-data deletion) must converge on one delete
  request contract; owner: the two docs jointly.
- **Name-uniqueness namespace granularity.** §5 assumes one global namespace (single-world). If the
  live service is ever multi-world/multi-shard, whether names are per-world or global reopens here.
