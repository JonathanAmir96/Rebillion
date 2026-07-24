# memory.md — Generation State & Decisions Log

State + decisions log for future Claude sessions (per CLAUDE.md's reading order:
`README.md` → `docs/00_vision/GLOSSARY.md` → `docs/WORLD_PLAN.md` → this file). Append,
never rewrite history; newest entries last within each section.

## Tree state (as of 2026-07-24)

- **Phases A–B complete** (reports in `docs/phase_reports/`), Phase C (schemas + asset
  specs) authored: `20_schemas/*`, `40_assets/*` all exist. **Phase D not started** — no
  `50_content/` tree yet, no content IDs minted (ID_REGISTRY blocks are all still free).
  `60_agents/roles/` charter exists; Phase E briefs pending.
- Locked files (Agent-3 / master brief): `docs/40_assets/ART_BIBLE.yaml` (2 amendments:
  AB-001 terrain, AB-002 compositing/palette), `docs/40_assets/UI_ART_SPEC.md`,
  `docs/30_engineering/ENGINEERING_STANDARDS.md`.
- Known cross-doc reconciliations still open: monster tier-count discrepancy
  (118/24/8 vs `monster.schema.md`'s 112/23/15); `telegraph`/`phase_shift`/`spawn` frame
  budgets proposed in `ANIMATION_STATES.md` §2.2 but not yet blessed into ART_BIBLE;
  `npc.schema.md` lacks `animation_states`. See each doc's Open Questions.

## Decisions log

- **2026-07-21 — v2 world revision (owner).** Two islands, 200 maps, first arc Lv 1–42,
  cap 300, paid coach travel, 8 bosses. See CLAUDE.md "Current design state" + WORLD_PLAN.
- **2026-07-22 — AB-001 (owner).** Maple-style foothold terrain + hand-painted terrain
  chunks; 16px grid stays for structures/measurement. `ART_BIBLE.yaml` `amendments[]`.
- **2026-07-24 — Composited player sprites (owner directive).** Player = paper-doll layer
  stack, never one baked sheet: `docs/40_assets/CHARACTER_COMPOSITING.md` (layer registry,
  animated-vs-anchored part classes, anchor map, per-part export via SPRITESHEET_SPEC).
  Motivation: PixelLab generation cost linear in parts (~1k frames for the first-arc
  wardrobe) instead of multiplicative in looks. New GLOSSARY "Player sprite layers" tokens +
  `style_<category>_NN` prefix; ID_REGISTRY "Appearance styles" block; SCOPE narrowed
  (creation appearance in scope; vanity shop/monetization stays out).
- **2026-07-24 — AB-002 (owner-authorized).** Appearance palette: 5 skin ramps (only new
  colors) + 6 hair swatches reusing existing palette hexes; layer-restricted; composited
  export blessed; `part_layer`/`pose_ref` PixelLab injects.
- **2026-07-24 — Account layer (owner directive).** `docs/10_systems/ACCOUNT.md`: one
  install = one account (interim), **4 character slots** (supersedes PERSISTENCE's old 3 —
  §6 there now mirrors ACCOUNT), creation flow nickname → appearance → confirm, nickname
  law `^[A-Za-z][A-Za-z0-9]{3,11}$`, case-insensitive **global uniqueness checked through
  the GameState facade** (local roster now, server database later — Maple-style "check
  name"). `nickname` added to GLOSSARY meta tokens.
- **2026-07-24 — Display policy (owner directive).** `docs/10_systems/DISPLAY.md`: launches
  **borderless fullscreen** by default, largest-integer-factor scaling of the locked
  640x360 render base, `ink` letterbox, `display_mode` client setting (frame_system +
  Alt+Enter).

## Pointers for the next session

- Continuing content generation → follow the phase-report batch pattern (region-scoped
  sub-agents, exemplar-first, validator-gated) and `docs/60_agents/roles/ORG.md` routing.
- Before Phase D touches player-facing art: run the compositing spike flagged in
  CHARACTER_COMPOSITING §9 discussion (base body + 1 outfit + 2 hairs) to validate
  pose-guided part generation before committing wardrobe counts.
- Validator (`tools/`) still unauthored; VALIDATION.md checks run manually per batch until
  it lands.
