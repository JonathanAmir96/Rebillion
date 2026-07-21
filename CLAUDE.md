# CLAUDE.md — Working Rules for This Repository

Rebillion is a **design-documentation tree** for a 2D side-scrolling MMORPG platformer
(Godot 4.3+ target). This run produces docs + machine-loadable YAML content only — no game
code, no generated art. Read `README.md` for the tree map and
`docs/phase_reports/` (+ `memory.md` once it exists) for current generation state.

## Laws (apply to every edit, human or agent)

1. **Tokens are law.** Use only `docs/00_vision/GLOSSARY.md` tokens for stats, resources,
   currency, and shared enums. The banned legacy-genre terms are listed in
   `docs/VALIDATION.md` §1 — that file is the only place they may appear.
2. **Single source of truth.** Rules live in one system doc; entity shapes in one schema;
   content files hold values + references only. Link, never restate.
3. **IDs are immutable** and must sit inside their `docs/ID_REGISTRY.md` block. Extend
   ranges in a new commit if needed; never renumber.
4. **Flag, don't guess.** Unknown token/rule/number → add to the owning doc's
   `## Open Questions` (every doc ends with that section).
5. **Locked files — do not edit:** `docs/40_assets/ART_BIBLE.yaml`,
   `docs/40_assets/UI_ART_SPEC.md`, `docs/30_engineering/ENGINEERING_STANDARDS.md`
   (owner Agent-3 / master brief). Changes go through their `amendments` /
   Open-Questions channels.
6. **Validate before landing:** the checks in `docs/VALIDATION.md` run on every content
   batch (see `tools/` once the validator lands). US spelling everywhere.

## Current design state (v2, owner revision 2026-07-21)

- Two islands: Emberfoot Isle (training, maps 001–016) → Harborwind Ferry (paid) →
  Harthmoor Isle, a Victoria-style **ring** (Millbrook south hub ↔ Verdant ↔ Gloomwood ↔
  Ashfall ↔ Tidewatch ↔ Millbrook) around the Clockwork Ruins center, with Sunken Depths as
  a coastal spur. 200 maps, 150 monsters (118/24/8), 8 bosses, 2 party quests. Town travel
  is the paid Harthmoor Coachworks (shards) — no free warps. Game cap is Lv 300 (initial
  design); this run authors the first arc, Lv 1–42.
- Jobs: novice → 1st at Lv 8 → 2nd at Lv 40 (lines `bulwark`/`keeneye`/`weaver`/`flicker`);
  3rd jobs named-and-reserved for future arcs.
- Social/economy systems are designed but server-deferred; the interim build is solo with a
  server-authoritative boundary (`docs/10_systems/PERSISTENCE.md`).

## Git & generation workflow

- Work lands on the designated feature branch (currently
  `claude/fable-design-docs-eaubpt`); push with `git push -u origin <branch>`. One concern
  per commit; content commits separate from doc/rule commits.
- Generation is phased A→E with hard gates (vision → systems → schemas/assets → content →
  coding-pass briefs); each phase emits a report in `docs/phase_reports/`.
- PixelLab (art generation, later pass): MCP tools + owner's API token. The token is
  **deliberately not stored in this repo** — ask the owner or use the environment secret
  (suggested var: `PIXELLAB_SECRET`) configured in the Claude Code environment settings.

## For future Claude sessions

Start by reading: `README.md` → `docs/00_vision/GLOSSARY.md` → `docs/WORLD_PLAN.md` →
`memory.md` (state + decisions log, written at the end of the generation run). When
continuing content generation, follow the batch pattern in the phase reports: region-scoped
sub-agents, exemplar-first, validator-gated.
