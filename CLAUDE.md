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

## Current design state (v2 canon, reconciled + merged 2026-07-24)

- **Two islands, one authored arc** (Lv 1–42 content; game cap 300, initial design; job
  gates 8 / 40 / 80-reserved): Emberfoot Isle (training, maps 001–016) → Harborwind Ferry
  (paid) → Harthmoor Isle, a Victoria-style **ring** (Millbrook south hub ↔ Verdant ↔
  Gloomwood ↔ Ashfall ↔ Tidewatch ↔ Millbrook) around the Clockwork Ruins center, with
  Sunken Depths as a coastal spur. Totals: **200 maps, 150 monsters (118/24/8), 8 bosses,
  2 raids** (`raid_undervault` / `raid_mainspring` — "raid" is the owner-ruled term for the
  instanced co-op runs, replacing the retired party-quest phrasing; owner doc
  `docs/10_systems/social/RAID.md`; no separate raid monster tier — finales reuse region
  bosses). Town travel is the paid Harthmoor Coachworks (shards, fares in ECONOMY §7) —
  no free warps. Each job line has a home ring town with its instructor
  (Bulwark→Cindershelf, Keeneye→Tidewatch Port, Weaver→Mossmere, Flicker→Millbrook); maps
  follow the WORLD_PLAN monster-gradient law. Terrain is Maple-style footholds + painted
  terrain chunks (ART_BIBLE amendment AB-001; movement rules in MAP_TRAVERSAL.md).
- Jobs: novice → 1st at Lv 8 → 2nd at Lv 40 (linear, no branching this arc); **3rd job at
  Lv 80 — gate canonized, content reserved for future arcs** (rosters in
  `docs/10_systems/JOBS.md`). Pacing (owner-ratified C3′, `memory.md`): Lv 40 ≈ 30 h ·
  Lv 80 ≈ 166 h · Lv 100 ≈ 300 h of `/played`.
- Social/economy systems are designed but server-deferred; the interim build is solo with a
  server-authoritative boundary (`docs/10_systems/PERSISTENCE.md`).
- Monetization (owner amendment MON-001, 2026-07-23): cosmetic-only + in-world sponsor
  billboards, hard no-pay-to-win charter — `docs/10_systems/MONETIZATION.md`. Direction only;
  no store content is authored this run.
- **v3-lineage material** (5 islands / 11 regions / arc 2 / branching specs — the parallel
  lineage merged over on 2026-07-24) is **non-canonical**: its content files and extra docs
  remain in-tree pending owner pruning or re-ratification. See `memory.md` MERGE NOTE and
  the ID_REGISTRY repeal note. Do not build on it.

## Git & generation workflow

- Work lands on the session's designated feature branch; push with
  `git push -u origin <branch>`. One concern per commit; content commits separate from
  doc/rule commits.
- Generation is phased A→E with hard gates (vision → systems → schemas/assets → content →
  coding-pass briefs); each phase emits a report in `docs/phase_reports/`.
- **Phase status (2026-07-24, v2 canon):** A (vision), B (systems), C (schemas/assets), and
  the **B2 v2-reconciliation + C3′ pacing retune** (`PHASE_B2_REPORT.md`) are complete.
  **Phase D (content) has not started against v2 canon** — the `50_content/` tree presently
  in-repo was authored by the non-canonical v3 lineage and must be pruned or re-ratified
  before or during D (see `memory.md` MERGE NOTE). `tools/validate.py` is v3-configured and
  must be re-aimed at v2 canon before gating (VALIDATION Open Questions). `memory.md` is
  the authoritative live log.
- PixelLab (art generation, later pass): MCP tools + owner's API token. The token is
  **deliberately not stored in this repo** — ask the owner or use the environment secret
  (suggested var: `PIXELLAB_SECRET`) configured in the Claude Code environment settings.

## For future Claude sessions

Start by reading: `README.md` → `docs/00_vision/GLOSSARY.md` → `docs/WORLD_PLAN.md` →
`memory.md` (state + decisions log, written at the end of the generation run). When
continuing content generation, follow the batch pattern in the phase reports: region-scoped
sub-agents, exemplar-first, validator-gated.

**Doc connectivity (rule):** every markdown doc must be **reachable from `README.md`** by
following links — README's "Start here" section is the tree's index (there is no `docs/` index
file; README is the root). Run `python3 tools/md_graph.py` to rebuild the link graph and
BFS-check it (report: `docs/phase_reports/MD_CONNECTIVITY_REPORT.md`); the tree is currently
one connected component, 98/98 README-reachable. After any wave that adds docs — especially a
parallel-session merge — re-run it and link any new "unreferenced" file from its natural index
(that is exactly how the F/G/H reports and the role files first slipped in undiscoverable).

**Staffing sub-agents:** use the virtual-studio role charter in `docs/60_agents/roles/`
(`ORG.md` = org chart + model routing: easy→Haiku, medium→Sonnet, hard→Opus, route by
blast radius). Invoke as: "Act as ROLE_X per docs/60_agents/roles/ROLE_X.md" — the role
file fixes mission, owned files, reading list, deliverable contract, and tier.
