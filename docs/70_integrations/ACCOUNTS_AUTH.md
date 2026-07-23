# ACCOUNTS_AUTH.md — Account Model, Session Security, Import Validation & Name Policy

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, 10_systems/PERSISTENCE.md, 10_systems/LEVELING.md, 10_systems/STATS.md,
10_systems/ITEMS.md, 10_systems/ENHANCEMENT.md, 10_systems/INVENTORY.md, 10_systems/SKILL_SYSTEM.md,
10_systems/JOBS.md, 10_systems/QUESTS.md, 10_systems/ECONOMY.md, 10_systems/social/CHAT.md,
10_systems/social/GUILD.md, 30_engineering/ENGINEERING_STANDARDS.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/TELEMETRY_ANALYTICS.md

Owner doc for the **future account system** — the entity `10_systems/PERSISTENCE.md` §2 names as
"Character identity → (future account system)" and defers to here. It designs the account/character
split, credential and session lifecycle, the **offline→online import validation pass**, and the
character-name policy. It is design only: no code, no committed secrets. The concrete auth-service
and gateway *components* live in `70_integrations/BACKEND_ARCHITECTURE.md` (the gated topology
contract, §9 of which assigns this doc the account-side numbers — this revision sets them); the
analytics/PII processing seam lives in `70_integrations/TELEMETRY_ANALYTICS.md` (sibling). This doc
restates neither — it fixes the account-layer contract and hands the wiring to those siblings.

**Decision posture (this revision).** `70_integrations/BACKEND_ARCHITECTURE.md` §9 assigns
reconnect-grace, session-lifetime numbers, and the credential/session lifecycle to this doc — which
this doc reads as covering the hashing choice and the rate-limit/lockout posture; the Phase F
version wrongly deferred them *back* to that doc, a ping-pong the architecture review flagged. This revision **sets those engineering values here**, from best practice, each with a
one-line rationale and rejected alternatives (§3–§4). Only real price-tag items — SSO/storefront
vendors and the email-provider contract — remain owner-priced Open Questions. Secrets (hash pepper,
token-signing keys) stay environment-managed and uncommitted (`70_integrations/BACKEND_ARCHITECTURE.md`
§10; the `PIXELLAB_SECRET` precedent).

## 1. Scope & relationship to PERSISTENCE

`10_systems/PERSISTENCE.md` owns **per-character save state** (its §2 truth ledger) and the
`GameState` facade the solo build writes through. This doc owns the layer **above** that facade: the
account a character belongs to, the credential/session machinery that proves a client may act as that
account, and the **validation gate that admits a local character into the live world** (§2.4).
Nothing here is a save-slot field; account records never live in a character save file and are never
editable by whoever holds a client install. That is exactly the asymmetry `10_systems/PERSISTENCE.md`
§9 draws: a local save *is* attacker-editable, which is why import (§2.4) must be re-validated
server-side and why account credentials never round-trip through a save file. Every stored field this
doc introduces carries a `10_systems/PERSISTENCE.md` §1 authority tag; the mapping is §8.

## 2. Account model, character binding & one-way import

_(BACKEND_ARCHITECTURE.md §9 cites this section for account/character binding + import; anchor held.)_

### 2.1 Two entities, one relationship

- **Account** — the credential-bearing root: a login identity, its authentication material, and a
  roster of characters. One human, one account (enforcement is a live-ops matter, not designed here).
  An account holds no game-world stats; it holds only who-you-are-to-log-in and what-you-own.
- **Character** — a single playable identity: the `10_systems/PERSISTENCE.md` §2 server-authoritative
  bundle (`level`/`exp`, primary stats, inventory, `shards` wallet, quest flags, skill ranks, bind
  point, guild/party membership). A character belongs to exactly one account and cannot be moved
  between accounts (Open Questions covers gifting/transfer). The character's server identity is a
  fresh, server-minted opaque id assigned at creation or at import (§2.4) — not a `docs/ID_REGISTRY.md`
  content id (that registry mints world content, not player characters).

### 2.2 Character slots

An account has **3 character slots at launch**, matching `10_systems/PERSISTENCE.md` §6's 3 local
save slots exactly — deliberate, so the interim solo build's slot shape and the live account's slot
shape are identical and migration is a re-homing, not a reshaping. Slot expansion beyond 3 is a
**future monetization question**, not decided here (Open Questions); the schema must not hard-code 3
as a structural limit — it is a per-account quota, server-owned.

### 2.3 Account creation & migration entry point

- **Account creation.** A prospective account submits an email handle (§6 minimal PII) and a
  password. The password is checked against a minimum-strength policy (length floor and a
  breached-password screen), hashed per §3, and stored; the account is created in a
  `pending-verification` state and an ownership-proof email is sent (email provider is an external
  dependency — failure mode in §3). Sign-in and character creation are permitted, but a configurable
  set of value-bearing actions may be gated on verification (live-ops policy, not fixed here). Account
  creation is rate-limited per source (§3) to blunt mass-signup abuse.
- **Migration story (local slots → account-bound characters).** The interim build stores each
  character in a local save slot (`10_systems/PERSISTENCE.md` §5–§6). When a live account exists, each
  local character is imported **once, one-way, on binding to an account** (§2.4), reusing
  `10_systems/PERSISTENCE.md` §9's offline→online import intent (never the reverse; a live character
  never exports back to a local save). The 3-slot symmetry (§2.2) means an install's 3 locals map
  cleanly onto an account's 3 slots.

### 2.4 Import validation pass (answers `10_systems/PERSISTENCE.md` §9's open question)

`10_systems/PERSISTENCE.md` §9 fixes the *intent* of one-way import and lists three unresolved
options for its validation pass — (a) re-derive `level` from raw `exp`, (b) range-check every
ID/`enhance_level`/`rarity` against `docs/ID_REGISTRY.md` and system-doc bounds, or (c) subset import
— naming the co-owner as "whatever future server-onboarding doc exists." **This doc is that co-owner,
and this section answers the open question.** The committed pass is **(a) and (b) together**, run as a
fail-closed pipeline; **(c) subset-only is rejected as the default** (it needlessly amputates
legitimate progress — see rationale). The uploaded save is treated as **wholly attacker-controlled**
(`10_systems/PERSISTENCE.md` §9): the pipeline trusts *raw ledger inputs* (cumulative `exp`, owned
item ids and quantities) only far enough to re-derive and bounds-check them, and trusts **no derived
or self-asserted value** (`level`, derived stats, allocated-point totals).

The pass runs entirely server-side on the account-bind event, before the character is minted into the
live namespace, in this order — any stage's failure **rejects the whole save with a specific reason**
(reject-not-repair; see rationale):

1. **Envelope & schema.** `save_version` must be recognized (`10_systems/PERSISTENCE.md` §8):
   older migrates forward, an unknown *future* version refuses to load. Structure validates against
   the save schema; an unknown field is a **migration bug, not ignorable input**
   (`10_systems/PERSISTENCE.md` §8) → reject.
2. **Referential integrity.** Every content id in the save — `item_equip_*`/`item_use_*`/`item_etc_*`,
   `skill_<line>_*`, the bind-point `map_*`, `quest_*`, `npc_*` — must resolve to a **minted** id
   inside its `docs/ID_REGISTRY.md` block (`docs/VALIDATION.md` §2/§4). An id that is out of range, or
   points at a *reserved/unminted* slot, → reject.
3. **`level` re-derivation (option a — recompute, never trust).** The stored `level`/
   `exp_into_level` are **discarded** and recomputed from raw cumulative `exp` via
   `10_systems/LEVELING.md`'s curve. The recomputed value is canonical; a mismatch is not an error,
   the derived value simply wins. Derived `level` above the authored-arc cap (Lv 82 across the two
   v3 arcs, `docs/WORLD_PLAN.md`; game cap Lv 300 per
   `00_vision/SCOPE.md`) → reject.
4. **Bounds re-check (option b — legal against system-doc ceilings).** Against the **derived** level:
   - Primary-stat allocation total ≤ the free-point budget that level legally grants
     (`10_systems/STATS.md` §4.2–§4.3; compute order and server authority §7–§8); excess → reject.
   - Per item, `enhance_level` ≤ its cap (`10_systems/ENHANCEMENT.md`) and `rarity` ∈ the
     `00_vision/GLOSSARY.md` rarity enum and legal for that item (`10_systems/ITEMS.md`).
   - `shards` wallet, item stack sizes, and inventory/bank tab occupancy ≤
     `10_systems/INVENTORY.md`'s ceilings (§1–§3, §7).
   - Skill ranks ≤ the max rank the character's job line and derived level allow
     (`10_systems/SKILL_SYSTEM.md`); the job line ∈ `10_systems/JOBS.md`'s legal set and legal for the
     derived level (e.g. a 2nd-job line requires Lv 40). Illegal line/level → reject.
   - Quest completed-set internally consistent (no completed quest whose prerequisite is unmet,
     `10_systems/QUESTS.md`).
5. **Recompute derived fields — do not import them.** Derived stats (`power`, `armor`, `warding`, …)
   are **never** imported; they are recomputed from primary stats + equipment (`10_systems/STATS.md`
   §8), matching `10_systems/PERSISTENCE.md` §7 "no client-recomputed derived stat treated as truth."
6. **Identity & global uniqueness.** The character name is re-run through the full §5 creation gate,
   now including the live global-uniqueness check the local namespace never had (§7). A collision
   forces a rename at import. The character is then minted a fresh server identity (§2.1) and bound to
   the account.
7. **One-way idempotency lock.** Import consumes the local save's binding once: a server-side record
   keyed to the save's identity marks it imported, so the same local save cannot be imported twice
   (into the same or another account). It never exports back (`10_systems/PERSISTENCE.md` §9).

**Rationale — combine (a)+(b), reject (c)-as-default, reject-not-repair.** Re-deriving `level` from
raw `exp` (a) closes the single highest-value forgery (a hand-set `level` with an inflated stat
budget) at its root; bounds-checking every id and cap (b) closes item/currency/enhance forgery. The
two are complementary, not alternatives — (a) validates the *progression axis*, (b) the *inventory
axis*. **(c) subset import is rejected as the default** because dropping a legitimate player's
equipment/quest history to be "safe" punishes the honest majority to spite a forger the (a)+(b) pass
already catches; (c) is retained only as an owner-selectable "cosmetic-safe-mode" fallback, not the
launch behavior. **Reject-not-repair** (fail the save with a reason rather than silently clamp an
over-cap value) is chosen because a silent clamp is itself an exploit oracle — an attacker probes the
clamp boundary to learn the exact legal ceiling and lands a maximal legal save; the one exception is
`level`, which is a canonical *recompute*, not a clamp.

**Residue flagged as genuine game-design Open Questions** (not engineering): whether a name collision
at import auto-suffixes or forces a manual rename (UX call); whether an otherwise-legal save whose
`shards`/items exceed a *since-nerfed* economy ceiling is rejected or grandfathered (economy-policy
call, joint with `10_systems/ECONOMY.md`); and whether import is offered to players at all, or only as
a one-time launch-window migration (product call). Filed in Open Questions.

## 3. Authentication, credentials & session lifecycle

_(BACKEND_ARCHITECTURE.md §9 cites this section for credential handling / no-auth-bypass; anchor held.)_

### 3.1 Credential options

- **Baseline: email + password.** Email is the account handle; it is minimal PII (§6). This is the
  one credential path the design assumes always exists.
- **Platform / storefront SSO — seams, not launch commitments.** Console/platform accounts and
  PC-storefront sign-in attach to an account as federated identities, so a single account may carry
  email/password plus zero or more linked identities. Which providers and their token-exchange
  contracts are owner-priced and `70_integrations/BACKEND_ARCHITECTURE.md`'s to wire (Open Questions).
  No provider is assumed present. **Failure mode:** an SSO provider outage disables *that* sign-in
  path only; email/password remains, and linked-identity sign-in fails closed (never falls back to an
  unauthenticated session).

### 3.2 Password storage (algorithm + parameter posture — SET here)

Passwords are never stored recoverably. **Chosen: Argon2id**, a unique per-credential salt, plus an
optional server-side **pepper** drawn from an environment-managed key (never committed;
`70_integrations/BACKEND_ARCHITECTURE.md` §10). A documented **parameter floor** is fixed here so no
deployment ships weaker than baseline: **memory ≥ 19 MiB (m ≥ 19456 KiB), iterations t ≥ 2,
parallelism p ≥ 1** (the OWASP Argon2id baseline). The *exact* deployed cost is tuned upward to the
hosting hardware (target ~250–500 ms/hash) and rotated in ops from environment-managed configuration
— the floor and algorithm are law here; the tuned cost is operational.

- Rationale: Argon2id is the current memory-hard, GPU/ASIC-resistant password-hashing standard (PHC
  winner); a fixed floor prevents a weak deployment while leaving ops headroom to raise cost as
  hardware improves.
- Rejected: **bcrypt** — no memory-hardness, weaker against GPU cracking; retained only as a
  break-glass fallback where an Argon2 binding is unavailable, and rehashed to Argon2id on next login.
  **scrypt** — acceptable but Argon2id is the newer, better-parameterized choice with solid BEAM
  bindings. **Committing work factors into this tree** — rejected on principle: they must be tunable
  and rotatable in ops without a doc/code change.
- On any successful login where the stored parameters are below the current tuned cost, the password
  is transparently rehashed at the new cost (upgrade-on-login).

### 3.3 Login flow

1. Client submits handle + password to the **auth service**
   (`70_integrations/BACKEND_ARCHITECTURE.md` §1).
2. Rate-limit / lockout gate (§3.5) is evaluated *before* the hash comparison, so a locked account
   spends no hashing budget.
3. Argon2id verify (§3.2). On mismatch, the failure counter increments (§3.5) and a **uniform**
   "invalid credentials" response is returned — the same message and comparable timing whether the
   email exists or not, so the endpoint is not an account-enumeration oracle.
4. On success: issue tokens (§3.4), reset the failure counter, and return the character roster for
   character-select (§4.1).

### 3.4 Session & refresh tokens (format, signing, lifetime — SET here)

Sign-in issues a **session token** (short-lived bearer credential presented to the gateway on connect
and to auth-service calls) plus a longer-lived **refresh token** (used only to mint a new session
token).

- **Format & signing — chosen: opaque, high-entropy (≥256-bit) random tokens stored server-side** in
  the session/presence cache (Redis + BEAM ETS/Presence, `70_integrations/BACKEND_ARCHITECTURE.md`
  §3); the server-side lookup *is* the validation. Where a self-contained artifact is genuinely needed
  — the reconnect **resume ticket** (§4) — it is an HMAC-signed short-TTL token using an
  environment-managed signing key (§10 of the topology contract); its TTL is pinned to the §4.3
  reconnect-grace window (90 s) plus a small clock-skew margin, so a late-window reconnect never
  fails on an expired ticket.
  - Rationale: **revocation is first-class** (§3.6); an opaque token backed by a server record is
    revoked *instantly* by deleting the record.
  - Rejected: **self-contained JWTs** — cannot be revoked before expiry without a denylist that
    defeats their statelessness anyway, so an opaque token + store lookup is strictly simpler and
    revokes on the spot. The one signed artifact (resume ticket) is scoped and short-lived precisely
    because it is *not* revocable mid-life.
- **Session-token lifetime — 60 minutes.** Rationale: long enough to cover a normal play session's
  control-plane calls without constant refresh, short enough that a leaked token self-expires within
  the hour; the live gateway connection persists via its §4 binding, so token expiry does not drop an
  in-flight session. Rejected: 5–15 min (web default) — needlessly chatty for a game client holding a
  long-lived socket, where the socket, not the token, is the liveness signal.
- **Refresh-token lifetime — 30 days, sliding, rotating.** Each refresh use issues a *fresh* refresh
  token and invalidates the prior one; reuse of an already-rotated token is treated as theft and
  revokes the whole token family. Rationale: a month of "remember me" convenience with rotation as a
  built-in theft detector. Rejected: a non-rotating long-lived refresh — a stolen refresh token would
  be usable for its full life undetected.
- **Single active game session per account.** At most one in-world session may be live for an account
  (§4 governs a second sign-in). Web/companion read-only surfaces, if any, are out of scope here.

### 3.5 Rate limiting & lockout (posture — SET here)

- **Per-account sign-in:** **5 failed attempts per 15-minute window** trips lockout escalation.
  Rationale: comfortably above fat-finger retries, well below an online brute-force rate.
- **Lockout — temporary and escalating, never permanent:** on tripping, lock **1 minute**, then
  **double each subsequent trip** (1 → 2 → 4 → 8 …) capped at **15 minutes**; the failure counter and
  backoff reset on a clean login or after **1 hour** of no attempts. Rationale: escalating backoff
  defeats a patient online brute-forcer while the cap + auto-reset denies an attacker a permanent
  denial-of-service lever against a known email. Rejected: **permanent lock after N** (a DoS lever
  against any known address); **fixed short lock** (too weak against a slow brute-forcer).
- **Per-source (IP) sign-in:** an aggregate cap (baseline **30 attempts / 15 min / source**) catches
  credential-stuffing that stays under each account's radar; a tripped source is met with escalating
  backoff / a challenge step rather than a hard block, so a shared NAT is not fully locked out.
- **Account creation per source:** baseline **5 / hour / source** to throttle mass-signup abuse.
- Exact numbers are a **posture with concrete defaults** set here; ops may tune them in
  environment-managed config, but the *shape* (per-account + per-source, escalating, capped,
  auto-resetting, never permanent) is fixed. **Failure mode:** if the distributed rate-limit
  coordination (Redis, `70_integrations/BACKEND_ARCHITECTURE.md` §8) is degraded, the gate fails
  **closed** to a conservative per-node local limit, never open.

### 3.6 Revocation (first-class)

Sign-out, password change, and any account-security action invalidate outstanding refresh tokens (and
their families, §3.4); a revoked session cannot be renewed and its next request fails closed. The
server is the sole authority on token validity — a client may never treat a token it holds as proof of
anything the server has revoked (`00_vision/PILLARS.md` P6). **Failure mode:** if the auth service is
down, existing sessions run on already-issued tokens until expiry and new logins **queue rather than
bypass** auth (`70_integrations/BACKEND_ARCHITECTURE.md` §8) — there is no unauthenticated fallback.

## 4. Session security, character-select & reconnect

_(BACKEND_ARCHITECTURE.md §9 cites this section for the reconnect-grace window; anchor held.)_

### 4.1 Character-select & the 3-slot model

After login (§3.3), the auth service returns the account's character roster — up to **3 slots**
(§2.2, mirroring `10_systems/PERSISTENCE.md` §6). Selecting a slot binds that character to the session
(one active character per session, §3.4). Empty slots offer character creation (name gated by §5);
slot deletion frees the slot and frees the name back into the pool (§5). Character-select is the
transition point where the account-level session (§3.4) narrows to a specific character; the gateway
binding (§4.2) is established on entering the world with the selected character.

### 4.2 Gateway binding

An in-world session is bound to the connection through the game **gateway**
(`70_integrations/BACKEND_ARCHITECTURE.md` §1 owns the component; this doc owns the account-side
contract it enforces): the gateway validates the session token on connect, associates the live
connection with the account + active character, and rejects world traffic whose token is missing,
expired, or revoked (§3). It is the single choke point answering "may this connection act as this
character?" **Failure mode:** gateway down → total outage by design (single public endpoint);
horizontal replicas behind a balancer mitigate, and a dropped connection resumes within the reconnect
grace (§4.3) with no state minted client-side (`70_integrations/BACKEND_ARCHITECTURE.md` §8).

### 4.3 Reconnect grace (window length — SET here)

A dropped connection does not immediately end the game session: the account's in-world session
persists for a **reconnect grace window of 90 seconds**, during which the same account may resume the
same character (via the §3.4 signed resume ticket) without a full re-sign-in — a transient network
blip is not a logout.

- Rationale: 90 s covers real-world wifi/cellular blips, elevator/subway drops, and short client GC
  pauses, while not holding the single-session lock (§3.4) and the character's world slot so long that
  a legitimate fresh login is blocked.
- Rejected: **30 s** — too tight; a common connectivity gap or client hang exceeds it and forces a
  full re-login and map reload. **5 min** — holds the one-session lock and the character's live world
  process far past any genuine blip, and lengthens the window a displaced/hijacked session lingers.

### 4.4 Kick-on-second-login

Because at most one game session per account is allowed (§3.4), a *successful, fully-authenticated*
new sign-in for an account that already has a live (or in-grace) session **displaces** the older one:
the newer session wins and the older connection is disconnected with a clear reason. This resolves the
stolen-credential and stuck-session cases predictably. Displacement requires a complete authentication
— an unauthenticated reconnect attempt (§4.3) never displaces a live session.

## 5. Character name policy

- **Uniqueness scope.** A character name is **globally unique across the live world** at creation
  time (server-enforced), mirroring `10_systems/social/GUILD.md` §2's global-uniqueness stance for
  guild names — names surface in social contexts (`10_systems/social/CHAT.md` speech
  bubbles/whispers, `10_systems/social/GUILD.md` rosters) where two identical names are a real
  impersonation vector. In the interim solo build there is no global namespace to check against (§7);
  the check goes live at import (§2.4 step 6) and at live creation.
- **Allowed set & length.** Letters and digits, **3–12 characters**, no spaces, no leading/trailing
  or repeated punctuation; one script/alphabet per name (US English, `00_vision/SCOPE.md` — no
  localization this run). The exact grapheme whitelist is confirmed at implementation; the design
  fixes the 3–12 bound and the no-spaces rule (character names, unlike guild names in
  `10_systems/social/GUILD.md` §2, do **not** permit spaces or apostrophes — a single-word handle
  reads cleaner in a speech bubble).
- **Reserved names.** Creation rejects, case-insensitively and with common look-alike substitutions
  folded: NPC, boss, town, and region names from `docs/WORLD_PLAN.md` (e.g. town names such as
  Millbrook, boss names such as Cindermaw) and job-instructor names; staff/official titles and any
  "admin/mod/system/GM/official" family (staff-impersonation guard); and a reserved technical set
  (empty, whitespace-only, reserved words). `docs/WORLD_PLAN.md` remains the authority for the
  world's proper nouns — this doc references that list rather than copying it, so it never drifts.
- **Profanity / impersonation filtering (stance).** A name passes through a profanity/slur filter and
  the reserved/look-alike checks above; the concrete wordlist and match rules are a **live-ops policy
  applied server-side**, deliberately not authored in this tree (matching `10_systems/social/GUILD.md`
  §2's identical deferral). Filtering is a creation-time gate plus a post-hoc report/rename channel —
  not a promise of perfection.
- **Rename policy.** A character may be renamed after creation; a rename re-runs the full §5 gate
  (uniqueness, allowed set, reserved, profanity) and frees the old name back into the pool. Whether a
  rename costs `shards`, is throttled, or is a paid convenience is a monetization/economy question,
  **not decided here** (Open Questions) — the mechanism is designed, the price is not.

## 6. Account data & privacy

- **Minimal PII.** An account stores the least identifying data that lets someone sign in and recover
  access: the account handle (email), authentication material (§3, hashed — never the password),
  linked-identity references for SSO (§3), and account-lifecycle timestamps. No real name, address, or
  payment data is designed into the account record here; anything payment-adjacent belongs to a
  storefront/monetization design out of this run's scope (`00_vision/SCOPE.md`).
- **Deletion & export posture.** The design assumes a data-subject **deletion** path (account +
  characters purged or irreversibly anonymized) and an **export** path (a machine-readable dump of an
  account's own data). Deletion of *analytics/telemetry* data and any pseudonymization boundary is
  `70_integrations/TELEMETRY_ANALYTICS.md`'s (sibling) — this doc owns deletion of the
  *account/character* records, that sibling owns the behavioral-data side, and the two must agree on a
  single delete signal (Open Questions). Retention windows are operational, not fixed here.
- **Email dependency.** Account verification, password reset, and security-action notices depend on an
  external email provider. **Failure mode:** provider outage blocks new-account verification and
  password-reset delivery (existing sign-in is unaffected); reset links are single-use and short-TTL
  so a delayed delivery cannot be replayed. Which provider, and its contract, is owner-priced (Open
  Questions).

## 7. Interim solo build & "implemented when"

Per the role contract, **none of §2.3–§6 ships in the interim solo build** — there is no server, no
network account, no global name namespace, and no session gateway to bind to (`00_vision/SCOPE.md`
excludes networking/backend; `10_systems/PERSISTENCE.md` §5's facade is local). The **one** thing that
ships now is the **forward-compatible character-identity shape**: each local character already carries
a stable identity (a local character id and a name field validated against the §5 *format* rules that
need no server — allowed set, length, and the reserved static proper-noun list from
`docs/WORLD_PLAN.md`), so that when an account system lands, binding a local character to an account is
a re-homing (§2) and not a reshape. The name-*uniqueness* check (§5), all of authentication (§3), all
of session security (§4), the import *validation* pass (§2.4), and the privacy paths (§6) are dormant
until a server exists.

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
| Password hash + salt (Argon2id, §3.2) | this doc §3 | `server` (never on client) |
| Linked SSO identity refs | this doc §3 | `server` |
| Character-slot roster + quota | this doc §2 | `server` |
| Character identity (server id, name, account binding) | this doc §5 / `10_systems/PERSISTENCE.md` §2 | `server` |
| Import-consumed marker (one-way lock, §2.4) | this doc §2 | `server` |
| Per-character game state (`level`, stats, inventory, `shards`, …) | `10_systems/PERSISTENCE.md` §2 | `server` |
| Session / refresh token (client-held bearer copy) | this doc §3 | `server`-issued, advisory on client (never authoritative) |
| "Remember me" / last-used-handle UI convenience | this doc §3 | `client` (`10_systems/PERSISTENCE.md` §3 — local preference only) |

## Open Questions

- **Slot expansion & pricing.** Whether accounts can buy character slots beyond 3, and at what price,
  is a monetization decision deferred to the owner (`00_vision/SCOPE.md` lists none planned this run).
  The schema keeps 3 as a server-owned quota, not a structural cap, so raising it is data.
- **SSO providers (owner/vendor-priced).** Which platform/storefront identities are supported, and
  their token-exchange contracts, are owner-priced and `70_integrations/BACKEND_ARCHITECTURE.md`'s to
  wire.
- **Email provider (owner-priced).** The verification/reset/notice email vendor and its contract
  (§6) carry a real price tag; the design fixes the flows and their failure mode, not the vendor.
- **Character transfer/gifting.** §2 forbids moving a character between accounts; whether a future
  paid transfer or account-merge path exists is undecided.
- **Rename cost/throttle (§5).** Mechanism designed, price/throttle not — joint with
  `10_systems/ECONOMY.md`'s sink budget if it ever costs `shards`.
- **Unified delete signal (§6).** This doc (account/character deletion) and
  `70_integrations/TELEMETRY_ANALYTICS.md` (behavioral-data deletion) must converge on one delete
  request contract; owner: the two docs jointly.
- **Name-uniqueness namespace granularity.** §5 assumes one global namespace (single-world). If the
  live service is ever multi-world/multi-shard, whether names are per-world or global reopens here
  (also flagged by `70_integrations/BACKEND_ARCHITECTURE.md`'s Open Questions).
- **Import residue (game-design, from §2.4).** Name-collision behavior at import (auto-suffix vs
  forced rename); whether an otherwise-legal save exceeding a *since-nerfed* economy ceiling is
  rejected or grandfathered (joint with `10_systems/ECONOMY.md`); and whether import is a permanent
  player-facing feature or a one-time launch-window migration (product call). The **validation
  algorithm itself is decided** (§2.4) — these are the residual design knobs, not the security pass.

_Engineering values SET in this revision (no longer deferred): Argon2id + parameter floor (§3.2);
opaque server-stored session tokens, 60-min session / 30-day rotating refresh (§3.4); per-account
5/15min + escalating-capped lockout and per-source caps (§3.5); 90-second reconnect grace (§4.3).
These are this doc's calls per `70_integrations/BACKEND_ARCHITECTURE.md` §9, not Open Questions._
