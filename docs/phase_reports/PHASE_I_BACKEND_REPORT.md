# PHASE_I_BACKEND_REPORT.md — Backend-Design Wave (docs/70_integrations/ suite)

References: docs/60_agents/BACKEND_KICKOFF_PROMPT.md, docs/60_agents/roles/ORG.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md, docs/10_systems/PERSISTENCE.md,
docs/VALIDATION.md, memory.md

Run date: 2026-07-23 · Orchestrator: producer tier per ORG.md (plan/route/gate/reconcile only —
all authoring delegated) · Branch: `claude/backend-kickoff-prompt-heuefx`

## 1. Mission and outcome

The kickoff (`docs/60_agents/BACKEND_KICKOFF_PROMPT.md`) asked for the authoritative-server
design suite under `docs/70_integrations/` — seven documents, design-only, every one mapping
`10_systems/PERSISTENCE.md` authority tags onto concrete components, with technical decisions
(stack, tick model, protocol, database technology, topology) **decided in-suite**, not deferred
to the owner. **Outcome: all seven docs authored, architect-reviewed, QA-gated, and landed;
`tools/validate.py` reports 88 files, 0 fails, 0 warnings on the finished tree.**

| # | Doc | State | Headline decisions |
|---|---|---|---|
| 1 | BACKEND_ARCHITECTURE.md | Revised (Phase F base) + gated first | Engine-independent Elixir/OTP + Phoenix; PostgreSQL (one DB, three schemas + roles) + append-only RNG audit log + Redis/ETS cache; single logical world + population channels + raid-only instances; scaling-units table; per-store failure modes |
| 2 | ACCOUNTS_AUTH.md | Revised + gated | Argon2id; opaque 60-min session tokens, 30-day rotating refresh; lockout ladder; 90 s reconnect grace; fail-closed offline→online import (re-derive exp + range-check) answering PERSISTENCE §9's open question |
| 3 | WORLD_CHANNELS.md | New + gated | Demand-driven channels (cap 5/map, channel_01 resident, 5-min teardown); occupancy caps 150 town / 60 field; 2,000/node, ~10,000-world targets; 30 s switch cooldown + 5 s combat lock |
| 4 | DATABASE_PERSISTENCE.md | New + gated | One Postgres database, `char`/`wallet`/`social` schemas + least-privilege roles (no 2PC); materialized wallet balance over append-only signed-delta ledger; two-class write cadence; audit-before-commit; save_version two-layer migration |
| 5 | NETWORK_PROTOCOL.md | New (two-stage) + gated | WSS + MessagePack; `[op, seq, ack, t, flags, payload]` envelope; protocol_version handshake; DEFLATE >512 B; 15 s heartbeat/30 s dead inside the 90 s grace; normative acquisition rule; 103-opcode catalog across 13 registry blocks |
| 6 | GAMEPLAY_SIMULATION.md | New + gated | 20 Hz sim / 10 Hz snapshot; per-tick-drained deterministic combat queue; per-map self-scheduling loops that park when empty; timestamp timers; 20 Hz accept-if-plausible reconciliation (resolves PERSISTENCE §4's flag); CombatMath cross-language test-vector parity; §5–§14 validation map cited by every mutating packet |
| 7 | CHAT_SOCIAL_BACKEND.md | New + gated | Four canonical chat channels + flagged `world` proposal; concrete per-channel rate limits; throttle→auto-mute→report→GM-mute ladder; per-system social-tier attachment; roster-bounded presence |

Supporting commits: `docs/ID_REGISTRY.md` packet-opcode block (`op_0001`–`op_9999`, 13 domain
ranges, landed in its own commit **before** any opcode was minted, per the kickoff rule);
ROLE_INTEGRATION_ENGINEER.md Owns-list update.

## 2. Routing used (ORG.md blast-radius law)

| Work | Tier | Notes |
|---|---|---|
| Docs 1, 2, 4, 6 authoring; doc 5 envelope/opcode-scheme | **Opus** | Contract-defining / security-relevant / cross-system |
| Docs 3, 7 authoring; doc 5 packet-catalog fill | **Sonnet** | Judgment inside a contract fixed by a gated doc |
| Architect review (×7) and QA gate (×7) | **Sonnet** | Doc reviews per ORG routing; QA also ran validate.py + mechanical greps |
| Orchestration, gate fixes, reconciliation, commits | **Producer (top tier)** | No bulk authoring; all fixes were review-directed line edits |

Sequencing followed the kickoff exactly: doc 1 gated before the 2/3/4/6/7 parallel fan-out;
doc 6 landed before doc 5's catalog was finalized; the opcode ID block landed in its own commit
before minting.

## 3. Gate results

Every doc took one ROLE_SYSTEMS_ARCHITECT consistency review and one ROLE_QA_VALIDATOR gate;
all fourteen passes returned PASS or PASS-WITH-FLAGS, and every flag was fixed and committed
before the doc was considered landed (fix-or-flag, never "fix later").

- **Doc 1** — QA: one wrong-section citation. Architect: boss arenas were wrongly modeled as
  per-party instances (fixed suite-wide: open-entry arenas are shared map processes with
  SPAWN §3 reset-when-empty; instances are raid-only (v2 wording: PQ)); `shard` banned as a partitioning word
  (currency-token collision); reconnect-number ownership pinned to doc 2.
- **Doc 2** — both passes: citation-precision fixes only; resume-ticket TTL explicitly bound to
  the 90 s grace window.
- **Doc 3** — QA clean. Architect: occupancy-cap table corrected (field maps are 3–6 screens;
  `interior` has a 0/0 density budget and got its own rationale row); party-size ownership split
  corrected; channel-eligibility interpretation formally blessed back into doc 1 §1.
- **Doc 4** — QA clean. Architect **upheld the suite's one deliberate contract deviation**: one
  Postgres database with three schemas + roles instead of doc 1's "separate logical databases,"
  because cross-concern value transfers must commit without 2PC. Doc 1 §1/§3 amended to the
  review's recommended wording (write isolation preserved; shared-resource caveat + per-role
  pool caps flagged owner-priced). Doc 4 also claimed the 60 s checkpoint interval outright,
  closing a dangling cross-deferral.
- **Doc 6** — QA: one citation split. Architect: ~20 systemic off-by-one internal section
  references corrected (load-bearing for the packet catalog); verbatim formula restatements
  trimmed to citations; cooldowns clarified as the lazily-checked timer exception; parked-map
  arena reset mechanism stated; `round(raw)` rounding convention flagged to COMBAT_FORMULA's
  owner; inventory/bank execution addendum added, closing the one PERSISTENCE §2 ledger row
  without an executing section.
- **Doc 7** — QA: one overclaimed citation (presence indicator reframed as a proposal).
  Architect: party state corrected to doc 4's ephemeral ETS/Redis classification; report-queue
  schema marked pending; market listing-fee ownership circularity (ECONOMY ↔ MARKET stub)
  flagged; whisper behavior during reconnect grace made explicit.
- **Doc 5** — QA clean (opcodes verified in-range, no duplicates; full-tree validator clean).
  Architect: the `client` authority tag was being overloaded for request fields, contradicting
  PERSISTENCE §1's three-tags-of-state law — resolved by a catalog-owned `intent` wire-role
  annotation with an explicit non-claim of PERSISTENCE vocabulary (PERSISTENCE untouched);
  inventory ops now cite GAMEPLAY_SIMULATION §11; `op_0405 death_penalty_delta` minted to carry
  §12's server-computed consequences (final count 103 opcodes).

## 4. Open Questions rollup (filed in their owning docs; owner-priced or game-design only)

- **Owner-priced (real price tag):** hosting/cloud vendor, region(s), managed-service and
  pooling-layer selection; RNG audit-log retention window/storage tier; cross-region failover;
  SSO/storefront vendors and email-provider contract; character-slot pricing (docs 1, 2, 4).
- **Game-design / cross-doc residue:** MARKET proceeds via wallet vs MAIL (pre-existing);
  market listing-fee number ownership (ECONOMY ↔ MARKET circularity); `world` chat-channel and
  roster presence-indicator adoption (CHAT.md/GLOSSARY/PARTY/GUILD owners); report/moderation
  table schema (DATABASE_PERSISTENCE next pass); `round(raw)` rounding convention
  (COMBAT_FORMULA owner); shop-pricing and coach-fare validation ownership (no
  GAMEPLAY_SIMULATION section owns vendor flows — flagged in doc 5); out-of-combat rest regen
  (still unowned upstream); reconciliation-envelope and rate-limit numbers marked first-pass
  pending telemetry; snapshot interest-management (WORLD_CHANNELS follow-up); whether GLOSSARY
  should note the engineering-side `op_NNNN` family (ID_REGISTRY note).
- **Import residue (doc 2):** name-collision UX, nerfed-economy grandfathering, import window
  permanence.

None block the solo build or Phase D content generation.

## 5. Deferred by design

Telemetry, build/distribution, and the PixelLab runbook were **out of this kickoff's scope**
(kickoff "Notes for the owner") — their Phase F docs stand unmodified. The proposed live-ops
doc (deploys/hotfix/rollback/GM tooling) was the kickoff's own open question: this run folded
GM tooling seams into CHAT_SOCIAL_BACKEND §2 and left deploy/rollback to a later, cheaper
session — a dedicated LIVE_OPS.md remains a sensible successor doc for ROLE_INTEGRATION_ENGINEER.

## 6. v3 merge reconciliation (at landing)

The suite was authored against the v2 world and merged into the v3.1 line (five islands, two
authored arcs, Phase D complete) when landing on main. Per the tree's standing merge policy, v3
wins world facts and the suite was retargeted in the merge commit: `pq_*` → `raid_*`
(arc-1 stage/finale map IDs unchanged), `PARTY_QUEST.md` → `social/RAID.md` (floor now RAID
§2/§3, lifecycle §5), the WORLD_CHANNELS raid table extended to all four raids, the
NETWORK_PROTOCOL raid-token enum widened (opcode numbers untouched; packet names renamed
pre-release), ACCOUNTS_AUTH's import cap re-cited to the v3 authored-arc cap, and the
packet-opcode registry block re-appended into the v3 ID_REGISTRY. Strict v3 `tools/validate.py`:
0 failures, 0 warnings after reconciliation. Residue flagged in memory.md: capacity targets were
sized against the v2 world — still valid as launch targets, re-check at the balance pass.

## Open Questions

- Should the next backend session author LIVE_OPS.md (deploys, hotfix, rollback, GM tooling)
  as doc 8 of the suite, or does it wait for the coding pass to exist first? Default: wait;
  nothing in the suite blocks on it.
