# AUTONOMOUS_MAINTENANCE.md — Incident-Triggered Agent Repair Loop

References: CLAUDE.md, 00_vision/PILLARS.md, docs/VALIDATION.md, docs/60_agents/roles/ORG.md,
docs/60_agents/roles/ROLE_PRODUCER.md, docs/60_agents/roles/ROLE_QA_VALIDATOR.md,
docs/60_agents/roles/ROLE_GAMEPLAY_DEVELOPER.md, docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md,
10_systems/PERSISTENCE.md, 30_engineering/ENGINEERING_STANDARDS.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/GAMEPLAY_SIMULATION.md,
70_integrations/DATABASE_PERSISTENCE.md, 70_integrations/TELEMETRY_ANALYTICS.md,
70_integrations/CHAT_SOCIAL_BACKEND.md,
docs/phase_reports/BACKEND_CHECKLIST_AUDIT_2026-07-24.md

Owner doc for the **autonomous maintenance loop**: how, once the game is live, production
incidents trigger agent sessions that diagnose, fix, gate, and land repairs in this repository
with minimal owner involvement. Set by owner direction (2026-07-24, recorded in
`docs/phase_reports/BACKEND_CHECKLIST_AUDIT_2026-07-24.md`): reliability is prioritized over
build speed, the Elixir/OTP stack decision stands, and **the end-state of this git tree is an
autonomous, agent-maintained system**. Design only — the trigger transport and CI wiring are
coding-pass work; this doc fixes the loop's shape, contracts, and guardrails so every later
piece is built to serve it.

## 1. Why this tree can be maintained by agents at all

The loop is not bolted on — it is what the tree's existing laws were already building toward:

- **P5 "Data is the game"** (`00_vision/PILLARS.md`): every entity is a schema-conformant file;
  an agent with the schema doc and its referenced system docs can implement or repair a feature
  without asking questions. The docs are the agent's onboarding, permanently.
- **Machine-checkable correctness**: `docs/VALIDATION.md` via `tools/validate.py` (checks 1–6),
  the `CombatMath` cross-language test-vector parity requirement
  (`70_integrations/GAMEPLAY_SIMULATION.md` §3), and the GUT test suites
  (`30_engineering/ENGINEERING_STANDARDS.md`) form a gate an agent's fix must pass — the same
  gate a human's fix must pass. Trust lives in the gates, not in who authored the diff.
- **Structured failure by design**: the OTP supervision model
  (`70_integrations/BACKEND_ARCHITECTURE.md` §2/§8) means a production fault arrives as a
  *structured crash report* from a named supervised process (one map, one instance, one
  service), already scoped to a blast radius — precisely the input an agent triage step needs.
  This synergy is part of why the owner confirmed the stack.

## 2. Trigger sources (what wakes an agent)

| Source | Signal shape | Exists today in |
|---|---|---|
| **OTP supervisor crash reports** | Process identity (map/channel/instance/service), stack trace, restart count; escalation when a restart loops | `70_integrations/BACKEND_ARCHITECTURE.md` §1/§8 |
| **APM / budget-breach alerts** | P95/P99 tick or query latency over budget, pool saturation, memory growth | Unowned — the flagged APM gap (`70_integrations/TELEMETRY_ANALYTICS.md` Open Questions); this loop is its consumer, which raises that item's priority |
| **Balance-telemetry anomalies** | An owning doc's first-pass number drifting outside its stated intent (e.g. `shards` faucet/sink ratio) | `70_integrations/TELEMETRY_ANALYTICS.md` §3/§6 |
| **Ledger anomaly checks** | Wallet materialization ≠ Σ ledger deltas; orphaned escrow; audit-log gap for a committed roll | `70_integrations/DATABASE_PERSISTENCE.md` §3.4/§4 invariants |
| **Player reports** | The moderation/report queue (message or bug reports) | `70_integrations/CHAT_SOCIAL_BACKEND.md` §2 report flow |
| **CI failures on the tree itself** | `tools/validate.py` / test regressions on any branch | `tools/README.md`, `docs/VALIDATION.md` |

Every trigger carries: severity, the failing component's identity, the raw evidence (crash
report, metric window, ledger rows), and a dedup key so one incident storm spawns one session,
not fifty (Open Questions).

## 3. The loop

```
detect (§2) → triage → route (ORG.md tiers) → branch + fix → gate → land → verify → close
```

1. **Triage** — a producer-tier session (`ROLE_PRODUCER`) classifies the incident: blast
   radius (one map's content file vs a systems formula vs server code), severity (economy/
   integrity incidents outrank cosmetic ones), and whether it is *content*, *docs/rules*, or
   *code*.
2. **Route** — per `docs/60_agents/roles/ORG.md`'s model-routing law (route by blast radius):
   content-level repairs to `ROLE_CONTENT_AUTHOR`, engine/server code to
   `ROLE_GAMEPLAY_DEVELOPER` / `ROLE_INTEGRATION_ENGINEER`, rule/formula changes to
   `ROLE_SYSTEMS_ARCHITECT` — each invoked with its role charter, the incident evidence, and
   the owning docs from §1's reading-list discipline.
3. **Fix** — on a fresh branch, one concern per commit (CLAUDE.md law), with a regression
   test or validator rule added whenever the bug class allows one: an incident that recurs
   must be *caught by a gate* the second time, not re-diagnosed.
4. **Gate** — `ROLE_QA_VALIDATOR` runs the full contract: `tools/validate.py`, the test
   suites, banned-token scan, doc-connectivity check. Fix-or-flag applies unchanged: a fix
   that cannot pass gates is not landed "to fix later."
5. **Land & verify** — merge per §4's autonomy ladder, deploy per the ops runbook (coding
   pass), then confirm the original trigger signal cleared. An incident is closed by the
   *signal going quiet*, never by the agent asserting success.

## 4. Autonomy ladder (what may land without the owner)

Default policy — first-pass, owner-tunable (Open Questions):

| Tier | Change class | Policy |
|---|---|---|
| **A — autonomous** | Content-file value fixes inside existing schema/budget bounds; broken references; test/validator additions; crash fixes in server code that change no design rule; doc cross-reference repairs | Agent lands on green gates; owner sees a digest, not a review request |
| **B — owner-notified** | New content entries; dependency/infra version bumps; performance changes within the stated tick/latency budgets | Lands on green gates + a notification with rollback instructions; owner may revert |
| **C — owner-gated** | Anything touching a *rule*: combat/economy formulas, schema shapes, GLOSSARY tokens, ID_REGISTRY ranges, the autonomy ladder itself, this doc, locked files' amendment channels, any wallet/ledger **data** repair | Agent prepares the branch + analysis; the owner merges. Never autonomous |

Two hard floors beneath the ladder: **locked files stay locked** (CLAUDE.md law 5 — agents go
through amendment channels regardless of tier), and **no agent ever mutates production ledger
data directly** — a ledger anomaly's *code* fix can be tier A/B, but the data correction it
implies is always tier C with the evidence attached (`10_systems/PERSISTENCE.md` §7's spirit,
extended to operators).

## 5. Guardrails

- **The gates are the authority.** An agent may not skip, weaken, or special-case
  `docs/VALIDATION.md` checks or test suites to make its own fix pass; changing a gate is
  itself a tier-C change.
- **Secrets never enter the tree** (`70_integrations/BACKEND_ARCHITECTURE.md` §10) — incident
  evidence is scrubbed of credentials/tokens before it reaches an agent prompt.
- **Fail-closed inheritance**: where a fix cannot be verified against the trigger signal
  (signal source itself is down), the loop stops and escalates to the owner rather than
  landing unverified — the same stance the server takes on unprovable truth
  (`70_integrations/BACKEND_ARCHITECTURE.md` §8).
- **Budget/rate bound**: concurrent incident sessions and per-incident retry counts are
  capped (Open Questions) so an incident storm cannot consume the owner's subscription
  fighting itself; past the cap, incidents queue for the owner.
- **Everything is a branch + PR**: no agent commits to the default branch directly, at any
  tier — tier A means auto-*merge* on green, not push-to-main.

## Open Questions

- **Trigger transport** — how a §2 signal becomes an agent session (webhook → scheduled
  session, a queue poller, or platform-native triggers) is coding-pass wiring; requirements
  fixed here: dedup key, severity, evidence payload, secrets scrubbing.
- **The APM gap is now load-bearing**: this loop's highest-value trigger class (budget
  breaches) depends on the unowned operational-telemetry item flagged in
  `70_integrations/TELEMETRY_ANALYTICS.md` Open Questions — that item should be scheduled
  early in the backend coding pass.
- **Autonomy-ladder tuning** (§4): the A/B/C boundaries, notification digest cadence, and the
  concurrent-session/retry caps (§5) are first-pass defaults; the owner ratifies or adjusts
  them before the loop is first armed. The ladder itself notes it is tier-C to change.
- **Incident-history memory** — where closed incidents and their fixes are recorded so future
  triage sessions can pattern-match (a `memory.md` section, a per-incident report file under
  `docs/phase_reports/`, or an external tracker) is undecided; default proposal: an
  `INCIDENTS.md` log at repo root, one line per closed incident, linking the fix commit.
- **Rollback authority** — whether tier-A/B changes that *pass* gates but degrade a live
  metric may be autonomously reverted by a follow-up agent (a revert is itself a change) is
  unresolved; default: yes for clean reverts of the loop's own recent merges, tier-C
  otherwise.
