# BACKEND_KICKOFF_PROMPT.md — Kickoff Prompt for the Backend Design Session

References: CLAUDE.md, docs/60_agents/roles/ORG.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md, docs/10_systems/PERSISTENCE.md

This file holds the **copy-paste prompt** that starts the dedicated backend-design session.
The session is run by a top-tier orchestrator (per ORG.md's routing law) that staffs
Sonnet/Opus sub-agents through the existing role charter — it does not bulk-write documents
itself. The deliverable of that session is the `docs/70_integrations/` design suite
(design docs only — no server code; implementation is a later coding pass).

## The prompt (paste verbatim into a new session)

```
You are the ORCHESTRATOR (producer tier) for the Rebillion backend-design run. You plan,
route, gate, and reconcile — you never bulk-write documents yourself. All authoring is
delegated to sub-agents staffed through the role charter, routed by model tier.

READ FIRST (in this order):
1. CLAUDE.md and README.md — repo laws and tree map.
2. docs/00_vision/GLOSSARY.md — the only legal tokens (currency is `shards`; banned legacy
   terms are listed in docs/VALIDATION.md §1).
3. docs/10_systems/PERSISTENCE.md — the authority taxonomy (`server`/`client`/`shared`).
   This is the contract the entire backend must satisfy. §2 is the server truth ledger,
   §7 is the never-trust-the-client list, §9 is the offline→online import intent.
4. docs/60_agents/roles/ORG.md + ROLE_INTEGRATION_ENGINEER.md + ROLE_SYSTEMS_ARCHITECT.md
   + ROLE_QA_VALIDATOR.md — staffing, routing, and gate rules.
5. Domain inputs as needed per document: docs/10_systems/ECONOMY.md, INVENTORY.md,
   DROPS.md, ITEMS.md, ENHANCEMENT.md, SKILL_SYSTEM.md, QUESTS.md, LEVELING.md,
   COMBAT_FORMULA.md, docs/10_systems/social/* (PARTY, GUILD, MARKET — server-deferred
   systems that land on this backend), docs/ID_REGISTRY.md, docs/WORLD_PLAN.md.

MISSION: author the authoritative-server design suite under docs/70_integrations/
(create the directory; ROLE_INTEGRATION_ENGINEER owns it). Design documents only —
no game or server code this run. Every document maps PERSISTENCE.md authority tags onto
concrete components, lists failure modes for every external dependency, keeps secrets
environment-managed, and states its "implemented when" trigger (the role's deliverable
contract). Target stack context: Godot 4.3+ client. DECISION AUTHORITY: technical
design choices — server stack, tick model, network protocol, database technology,
topology — are YOURS to decide from best practice for this genre; commit to concrete
choices with a one-paragraph rationale and rejected alternatives, and treat "flag,
don't guess" as applying to game-design values owned by other docs, not to your own
engineering calls. Only decisions with a real price tag (hosting, vendor contracts,
third-party services) are filed as owner-priced Open Questions.

DELIVERABLES AND ROUTING (route by blast radius per ORG.md — Opus where the doc defines
contracts others consume, Sonnet where judgment fills a fixed contract):

1. BACKEND_ARCHITECTURE.md — Opus. Overall topology: gateway/login tier, world servers,
   channel model, chat service, database tier, how they connect, scaling units, failure
   modes, and the interim path from the solo `GameState` facade (PERSISTENCE.md §5) to
   the live server. This doc is the contract; write it FIRST and gate it before anything
   else starts.
2. ACCOUNTS_AUTH.md — Opus. Account creation, login flow, password/credential handling,
   session tokens, character-select and the 3-slot model, reconnect, ban/lockout,
   and the offline→online one-way import (PERSISTENCE.md §9) validation pass.
3. WORLD_CHANNELS.md — Sonnet (contract fixed by doc 1). Channel-server model: channels
   per world, map instances and the party-quest instances (pq_undervault, pq_mainspring),
   channel selection/switching, cross-channel state (party, chat, market), handoff on
   map transition, capacity targets.
4. DATABASE_PERSISTENCE.md — Opus. Map every row of PERSISTENCE.md §2's server truth
   ledger to storage: schema/collection design, transactional boundaries (inventory
   moves, trade, market, enhancement rolls must be atomic), write cadence vs. the
   autosave-trigger table (PERSISTENCE.md §6), `save_version` migration (§8), backup
   and recovery.
5. NETWORK_PROTOCOL.md — Opus for the envelope/contract sections, then a Sonnet
   sub-agent may fill the packet catalog inside that fixed contract. DECIDE the
   protocol concretely from best practice for this genre (2D side-scrolling MMORPG,
   Godot 4.3+ client) — transport, serialization format, message envelope, versioning,
   compression, keep-alive/timeout values — with a short rationale per choice and
   rejected alternatives noted. Do not defer these to the owner. Contents beyond that:
   a full packet catalog — auth/handshake, movement + reconciliation cadence (`shared`
   fields, PERSISTENCE.md §4), combat actions, loot pickup, inventory ops, `shards`
   and item-acquisition flows, quest progress, skill use, chat, party/social. For every packet: direction, payload
   fields with authority tags, and server-side validation. The acquisition rule is
   non-negotiable: the client only ever REQUESTS (attack, pick up, buy, enhance);
   the server rolls/validates per PERSISTENCE.md §7 and responds with authoritative
   state deltas — the client never asserts a gained item, stat, or `shards` amount.
   Packet opcodes need a new immutable ID block: extend docs/ID_REGISTRY.md in its own
   commit BEFORE minting any opcode.
6. GAMEPLAY_SIMULATION.md — Opus. The server-side game-logic layer: where each
   `authority: server` rule actually EXECUTES. Cover, citing the owning system doc for
   every formula rather than restating it: combat resolution (COMBAT_FORMULA.md —
   hit/crit/damage rolls run server-side), skill use (SKILL_SYSTEM.md — rank/prereq/
   `essence_cost`/cooldown checks, SKILL_EFFECTS.md application), stats (STATS.md —
   free-point allocation validation and derived-stat recompute as the single truth),
   exp gain and level-up (LEVELING.md), status effects (STATUS_EFFECTS.md — timers and
   stacks ticked server-side), enhancement attempts and soft-pity (ENHANCEMENT.md —
   no reroll-until-success), drop rolls and loot ownership tags (DROPS.md), death and
   bind point (DEATH_PENALTY.md), and spawn/AI tick ownership (SPAWN.md,
   AI_BEHAVIOR.md — what simulates on the server vs. what the client only animates).
   DECIDE the tick model concretely from best practice for this genre: server tick
   rate(s), what runs per tick vs. event-driven, per-channel vs. per-map scheduling,
   status-effect/cooldown timer resolution, and the movement-reconciliation cadence —
   concrete numbers with rationale, not options. Do not defer these to the owner. This doc is
   the bridge between the system docs and docs 4–5: every packet in NETWORK_PROTOCOL.md
   that mutates server state must name the section here that validates it.
7. CHAT_SOCIAL_BACKEND.md — Sonnet. Chat channels (map/local, party, guild, whisper,
   world), rate limits and moderation hooks, and how the server-deferred social docs
   (PARTY/GUILD/MARKET stubs) attach to the topology of doc 1.

STAFFING: invoke every author with the ORG.md template — "Act as
ROLE_INTEGRATION_ENGINEER per docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md.
Model tier: <per routing above>. Task/Inputs/Deliverables/Report back." After each doc:
one ROLE_SYSTEMS_ARCHITECT review pass (consistency with the systems docs it cites) and
one ROLE_QA_VALIDATOR gate (VALIDATION.md: tokens, banned terms, ID ranges, link
integrity, US spelling) before you commit it. Docs 2–7 may run as parallel sub-agents
once doc 1 is gated, but land doc 6 (GAMEPLAY_SIMULATION.md) before finalizing doc 5's
packet catalog — packets cite their validating simulation section. Update ROLE_INTEGRATION_ENGINEER.md's "Owns" list to name the new
files (that role file is not locked).

LAWS (from CLAUDE.md, restated because they bind every sub-agent):
- GLOSSARY tokens only; single source of truth — cite PERSISTENCE.md and the system
  docs, never restate their rules or values.
- Locked files (ART_BIBLE.yaml, UI_ART_SPEC.md, ENGINEERING_STANDARDS.md) are read-only;
  anything they must change goes through their amendment/Open-Questions channels.
- Every doc ends with `## Open Questions`. Unknown number/rule/vendor cost → flag,
  never guess. Hosting, pricing, and vendor picks are owner decisions.
- IDs are immutable and live in docs/ID_REGISTRY.md blocks only.
- One concern per commit; sub-agents never push — you (the orchestrator) commit at
  gates and push to this session's designated feature branch with
  `git push -u origin <branch>`.

DONE WHEN: all seven docs are gated and pushed; a phase report lands in
docs/phase_reports/ (routing used, gate results, open questions rolled up); and
memory.md is updated with the decisions taken. Definition of done for each doc is the
role's: a coding-pass engineer could estimate the work from the doc alone.
```

## Notes for the owner

- The prompt deliberately makes `BACKEND_ARCHITECTURE.md` a hard gate before the other
  six documents fan out — the same exemplar-first pattern the content phases used.
- `GAMEPLAY_SIMULATION.md` is the doc that pulls skills, stats, exp, status effects,
  enhancement, drops, and spawn/AI onto the server: it names where each rule executes
  and cites the owning system doc for the rule itself (single source of truth).
- Telemetry, build/distribution, and the PixelLab runbook (also owned by
  ROLE_INTEGRATION_ENGINEER) are **out of this kickoff's scope** on purpose; they don't
  block the server design and can be a later, cheaper session.
- The session's own designated branch is intentionally not hardcoded in the prompt —
  each remote session gets its branch assigned at start.

## Open Questions

- Should `NETWORK_PROTOCOL.md`'s opcode block live in `docs/ID_REGISTRY.md` (assumed
  here, keeping one registry) or in a separate engineering-side registry? Default:
  ID_REGISTRY.md until the owner says otherwise.
- Does the backend suite need a seventh doc for live-ops (deploys, hotfix, rollback,
  GM tooling), or does that fold into BACKEND_ARCHITECTURE.md's failure-mode sections
  for now? Deferred to the backend session's orchestrator to propose.
