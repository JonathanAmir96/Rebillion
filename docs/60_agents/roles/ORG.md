# ORG.md — The Rebillion Virtual Studio (Agent Roles & Model Routing)

References: CLAUDE.md, docs/00_vision/PILLARS.md, docs/VALIDATION.md

A "company" of agent roles. Any prompt (this run or a future session) staffs work by
pointing an agent at one role file: *"Act as ROLE_X per docs/60_agents/roles/ROLE_X.md;
here is your task."* The role file fixes the agent's mission, owned files, reading list,
deliverable contract, and model tier — so prompts stay short and routing stays consistent.

## Org chart

```
ROLE_PRODUCER (orchestrator, top tier)
├── ROLE_SYSTEMS_ARCHITECT (rules, formulas, schemas)
├── ROLE_WORLD_BUILDER     (regions, maps, arenas)
├── ROLE_NARRATIVE_WRITER  (NPCs, quests, flavor)
├── ROLE_CONTENT_AUTHOR    (mechanical YAML mass-production)
├── ROLE_ART_DIRECTOR      ("Agent-3" — art bible, UI spec, PixelLab QA)
│   └── ROLE_ART_QUARTERMASTER (PixelLab budget gate — balance check + self-vs-PixelLab routing)
├── ROLE_QA_VALIDATOR      (VALIDATION.md enforcement, batch gates)
├── ROLE_SECURITY_ENGINEER (anti-cheat & data-integrity assurance, security review gates)
├── ROLE_INTEGRATION_ENGINEER (backend/platform/pipeline design)
├── ROLE_BACKEND_ENGINEER  (live-server implementation & ops — Elixir/OTP coding pass)
└── ROLE_GAMEPLAY_DEVELOPER   (future coding pass, Godot)
```

## Role files (index)

Every role above has a charter file in this directory — read it before staffing that role:

- `docs/60_agents/roles/ROLE_PRODUCER.md`
- `docs/60_agents/roles/ROLE_SYSTEMS_ARCHITECT.md`
- `docs/60_agents/roles/ROLE_WORLD_BUILDER.md`
- `docs/60_agents/roles/ROLE_NARRATIVE_WRITER.md`
- `docs/60_agents/roles/ROLE_CONTENT_AUTHOR.md`
- `docs/60_agents/roles/ROLE_ART_DIRECTOR.md`
- `docs/60_agents/roles/ROLE_ART_QUARTERMASTER.md`
- `docs/60_agents/roles/ROLE_QA_VALIDATOR.md`
- `docs/60_agents/roles/ROLE_SECURITY_ENGINEER.md`
- `docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`
- `docs/60_agents/roles/ROLE_BACKEND_ENGINEER.md`
- `docs/60_agents/roles/ROLE_GAMEPLAY_DEVELOPER.md`

## Model routing law

Route by **blast radius, not volume** (a task is "hard" when others depend on its output
or it reasons across systems; volume of mechanical work is the only reason to go cheap):

| Difficulty | Model tier | Typical work |
|---|---|---|
| Easy — low-ambiguity template fill | **Haiku** | normal-mob YAML from a manifest, drop/item table rows, token scans, stub docs |
| Medium — judgment inside a fixed contract | **Sonnet** | region map batches, quests/NPCs, elite monsters, schema docs, asset specs, doc reviews |
| Hard — defines rules others consume / cross-system | **Opus** | core formulas, leveling/economy curves, schemas for combat entities, boss + arena design, backend architecture, coding-pass briefs |
| Orchestration — plan, gate, reconcile, review | **Top tier (producer)** | phase gates, world-graph reconciliation, conflict resolution; never bulk-generates |

**Escalation rule:** any agent that hits unresolved ambiguity files an `## Open Questions`
entry and (if blocked) escalates one tier up via the producer — never guesses.
**Demotion rule:** a lead may pre-compute manifests (names, stats, slots) so the tier
below can execute mechanically; that is the preferred way to make cheap generation safe.

## Standing laws for every role
- GLOSSARY tokens only; banned legacy terms per VALIDATION.md §1. US spelling.
- Reference, never restate; one source of truth per rule/field/term.
- Locked files (ART_BIBLE.yaml, UI_ART_SPEC.md, ENGINEERING_STANDARDS.md) are touched by
  no one; ROLE_ART_DIRECTOR alone operates their amendment channels.
- Every doc ends with `## Open Questions`. Every batch passes VALIDATION.md before landing.
- No PixelLab MCP call without a same-batch `get_balance` check routed through
  ROLE_ART_QUARTERMASTER — simple assets are self-generated, generations are spent only
  per its decision matrix.
- No git pushes by staff roles; the producer commits/pushes at gates.

## Invocation template (for prompts)

```
Act as <ROLE_NAME> per docs/60_agents/roles/<ROLE_FILE>.md.
Model tier: <per ORG.md routing — easy/medium/hard>.
Task: <one paragraph>.
Inputs: <files to read first, beyond the role's standing reading list>.
Deliverables: <exact file paths>.
Report back: files written, tokens/IDs consumed, open questions.
```

## Open Questions
- Should future sessions add a ROLE_AUDIO_DESIGNER once AUDIO_DESIGN.md exists? Default:
  fold under ROLE_ART_DIRECTOR until audio scope grows.
