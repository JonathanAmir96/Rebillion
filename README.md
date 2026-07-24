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
  (conventions in `docs/50_content/README.md`)
- `docs/30_engineering/` + `docs/40_assets/` — engineering standards and art/UI bible
  (change-controlled, `CLAUDE.md` Law 5)
- `docs/60_agents/` — coding-pass phase briefs, role charters, and the autonomous-maintenance
  loop (`AUTONOMOUS_MAINTENANCE.md`) · `docs/VALIDATION.md` — pass/fail rules
- `docs/70_integrations/` — platform & pipeline design (backend, accounts/auth, telemetry,
  build/distribution, PixelLab art-pass runbook, wiki export)
- `docs/phase_reports/` — per-phase generation reports (`PHASE_A_REPORT.md`,
  `PHASE_B_REPORT.md`, `PHASE_D_ARC2_REPORT.md`, `ARC2_PLAN_REPORT.md`,
  `PHASE_F_INTEGRATIONS_REPORT.md`, `PHASE_G_EQUIPMENT_REPORT.md`,
  `PHASE_H_CONSISTENCY_REPORT.md`, `PHASE_I_BACKEND_REPORT.md`,
  `SYNC_AUDIT_v3_2026-07-23.md`, `MD_CONNECTIVITY_REPORT.md`,
  `BACKEND_CHECKLIST_AUDIT_2026-07-24.md`, `DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md`,
  `GAMEPLAY_LOOP_REVIEW_2026-07-24.md`, `MD_AUDIT_REPORT_2026-07-24.md`) ·
  `tools/validate.py` — the
  batch validator, usage in `tools/README.md` (VALIDATION checks 1–6);
  `tools/md_graph.py` — the doc connectivity graph; `tools/wiki_gen.py` — static reference
  wiki built from `docs/50_content/` (gitignored `wiki/` output); `tools/regen_quest_exp.py`
  — the quest-`exp` regen vs `docs/10_systems/LEVELING.md` §1
- `docs/mockups/` — non-binding HTML wireframe mock-ups, referenced from
  `docs/40_assets/UI_ART_SPEC.md` (UA-003): `gameplay_scene_mockup.html`,
  `entry_roster_creation_mockup.html`, `town_hub_millbrook_mockup.html`,
  `inventory_character_windows_mockup.html`, `world_travel_mockup.html`,
  `raid_boss_hud_mockup.html`
- `memory.md` — generation state & decisions log (newest-first) · `memory/` — Memory Bank
  (`projectbrief` → `systemPatterns` → `techContext` → `activeContext` → `progress`),
  distilled current-state context for future sessions

Rules of the tree: `CLAUDE.md` Laws 1–6 (glossary tokens · single source of truth · immutable
IDs · flag-don't-guess · change-controlled files · validate before landing).
