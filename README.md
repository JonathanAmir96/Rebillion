# Rebillion — Design Documentation Tree

Design docs, schemas, and machine-loadable YAML content for **Rebillion**, a 2D side-scrolling
MMORPG-style platformer (Godot 4.3+ target). Generated per the master brief in `GENERATE.md`
(kept outside this repo); this tree is the single source of truth for a later coding pass.

Start here:

- `docs/00_vision/` — pillars, scope, and the canonical vocabulary (**GLOSSARY.md — tokens
  are law**)
- `docs/ID_REGISTRY.md` — reserved ID ranges · `docs/WORLD_PLAN.md` — region/map/monster
  allocation
- `docs/10_systems/` + `docs/15_maps_system/` — game rules (prose)
- `docs/20_schemas/` — entity shapes · `docs/50_content/` — values only, referencing the above
- `docs/30_engineering/` + `docs/40_assets/` — engineering standards and art/UI bible (locked)
- `docs/60_agents/` — coding-pass phase briefs · `docs/VALIDATION.md` — pass/fail rules
- `docs/70_integrations/` — platform & pipeline design (backend, accounts/auth, telemetry,
  build/distribution, PixelLab art-pass runbook, wiki export)
- `docs/phase_reports/` — per-phase generation reports · `tools/validate.py` — the batch
  validator (VALIDATION checks 1–4)

Rules of the tree: content files hold values and references, never rule text; every reference
must resolve; unknown terms are proposed in GLOSSARY, never invented silently.
