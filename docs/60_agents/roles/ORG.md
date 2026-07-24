# ORG.md — The Rebillion Virtual Studio (Agent Roles & Model Routing)

References: CLAUDE.md, docs/00_vision/PILLARS.md, docs/VALIDATION.md

A "company" of agent roles. Any prompt (this run or a future session) staffs work by
pointing an agent at one role file: *"Act as ROLE_X per docs/60_agents/roles/ROLE_X.md;
here is your task."* The role file fixes the agent's mission, owned files, reading list,
deliverable contract, and model tier — so prompts stay short and routing stays consistent.

## Org chart

```
ROLE_PRODUCER (orchestrator, top tier)
├── ROLE_SYSTEMS_ARCHITECT (rules, formulas, schemas, map-system + social rule docs)
├── ROLE_WORLD_BUILDER     (regions, maps, arenas — incl. boss arena mechanics/geometry)
├── ROLE_MONSTER_DESIGNER  (elite/boss stat-blocks, skill kits, mob manifests)
├── ROLE_NARRATIVE_WRITER  (NPCs, quests, flavor)
├── ROLE_CONTENT_AUTHOR    (mechanical YAML mass-production)
├── ROLE_ART_DIRECTOR      ("Agent-3" — art bible, UI spec, PixelLab QA)
├── ROLE_QA_VALIDATOR      (VALIDATION.md enforcement, batch gates)
├── ROLE_INTEGRATION_ENGINEER (backend/platform/pipeline design)
└── ROLE_GAMEPLAY_DEVELOPER   (future coding pass, Godot)
```

## File ownership map (no path orphaned)

| Path | Owning role | Notes |
|---|---|---|
| `docs/10_systems/*.md` | ROLE_SYSTEMS_ARCHITECT | balance surface = one logical writer |
| `docs/10_systems/social/*.md` | ROLE_SYSTEMS_ARCHITECT | **producer sign-off** required (server-deferred) |
| `docs/15_maps_system/*.md` | ROLE_SYSTEMS_ARCHITECT | map-system rule docs (traversal/connections/layers/interactables) |
| `docs/20_schemas/*.md` | ROLE_SYSTEMS_ARCHITECT | entity shapes |
| `docs/50_content/maps/*` | ROLE_WORLD_BUILDER | per-map YAML; boss arena mechanics/geometry |
| `docs/50_content/monsters/*`, `docs/50_content/skills/*` (monster kits) | ROLE_MONSTER_DESIGNER | elite/boss stat-blocks + kits + manifests |
| `docs/50_content/npcs/*`, `docs/50_content/quests/*` | ROLE_NARRATIVE_WRITER | words players read |
| `docs/40_assets/*` | ROLE_ART_DIRECTOR | locked core via amendment channels only |
| `docs/70_integrations/*` (incl. ART_GENERATION_RUNBOOK.md) | ROLE_INTEGRATION_ENGINEER | ART_DIRECTOR holds QA veto over art-pipeline outputs |
| `docs/VALIDATION.md`, `docs/00_vision/*`, `docs/WORLD_PLAN.md`, `docs/ID_REGISTRY.md`, `memory.md` | ROLE_PRODUCER | architect/QA propose edits via producer sign-off |

## Model routing law

Route by **blast radius, not volume** (a task is "hard" when others depend on its output
or it reasons across systems; volume of mechanical work is the only reason to go cheap):

| Difficulty | Model tier | Typical work |
|---|---|---|
| Easy — low-ambiguity template fill | **Haiku** | normal-mob YAML from a manifest, monster manifests / roster fill-out, drop/item table rows, token scans, stub docs |
| Medium — judgment inside a fixed contract | **Sonnet** | region map batches, quests/NPCs, elite monster stat-blocks + skill kits, schema docs, asset specs, doc reviews |
| Hard — defines rules others consume / cross-system | **Opus** | core formulas, leveling/economy curves, schemas for combat entities, boss stat-blocks + skill kits, boss + arena design, backend architecture, coding-pass briefs |
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
