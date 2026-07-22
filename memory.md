# memory.md — Generation State & Decisions Log

State file for future sessions. Read after `README.md` → `docs/00_vision/GLOSSARY.md` →
`docs/WORLD_PLAN.md` (per CLAUDE.md). Newest entries last. This file records *state and
decisions*; rules live in their owner docs — never restate them here.

## Current state (as of 2026-07-22)

- **World:** v2 two-island design (Emberfoot Isle Lv 1–8, Harthmoor ring Lv 8–40+2);
  200 maps / 150 monsters (118/24/8) / 8 bosses / 2 PQs; first arc Lv 1–42, cap 300.
  Authority: `docs/WORLD_PLAN.md`.
- **Phases:** A (vision) ✅ · B (systems, 32 docs) ✅ · C (schemas + asset specs) ✅
  checkpoint landed (8 schemas, spritesheet/animation specs, ART_BIBLE AB-001 terrain
  amendment) — no separate C report yet · D (50_content YAML) **not started** — the
  `50_content/` tree does not exist yet · E (coding-pass briefs) not started ·
  **F (integrations & polish) ✅** — see `docs/phase_reports/PHASE_F_INTEGRATIONS_REPORT.md`.
- **Docs added in F:** `10_systems/` AUDIO_DESIGN, ONBOARDING_FTUE, COLLECTIONS,
  WRITING_STYLE, WORLD_LORE · `70_integrations/` (new dir) BACKEND_ARCHITECTURE,
  ACCOUNTS_AUTH, TELEMETRY_ANALYTICS, BUILD_DISTRIBUTION, ART_GENERATION_RUNBOOK,
  WIKI_EXPORT.
- **Locked files** (unchanged, amendment channels only): `docs/40_assets/ART_BIBLE.yaml`,
  `docs/40_assets/UI_ART_SPEC.md`, `docs/30_engineering/ENGINEERING_STANDARDS.md`.
- **GLOSSARY Provisional:** `title` (from COLLECTIONS §7), pending promotion.

## Decisions log

- **B gate:** job lines/cleanse tags/crest shapes promoted into GLOSSARY; `haste` kept
  combined; GUILD's proposed guild.schema deferred to the backend pass.
- **v2.2–v2.4 owner revisions:** free warps retired for paid Harthmoor Coachworks + ferry;
  ring towns host job instructors; Maple-style foothold terrain (AB-001).
- **F wave (2026-07-22):**
  - Bestiary is a *derived view* — no new content files/IDs; set-completion `shards`
    withheld pending an ECONOMY faucet-list amendment (titles-only until then).
  - AUDIO_DESIGN is the bgm/ambience/sfx tag-catalog governor; MAPS_SYSTEM §5's open
    governance question should be closed to point at it on its owner's next pass.
  - Backend: single logical world + population channels + instances (no independent
    shards) to keep one economy ledger; solo build ships first, `GameState` facade is the
    migration seam.
  - Accounts: 3 character slots mirroring PERSISTENCE's 3 local save slots; one-way
    local→account import.
  - Versioning: `client_version` / `content_version` / `save_version` decoupled; every
    build pins the design-tree commit it packed content from.
  - Lore canon fixed: Kiln Age (emberstone vein), the Long Unwinding (Mainspring failure,
    orderly evacuation, Custodian never stood down), Drowned Kingdom kept *unrelated* to
    Clockwork until an owner rules otherwise; five mysteries deliberately unanswered.
  - PixelLab pass: exemplar-first per region in WORLD_PLAN order; `PIXELLAB_SECRET`
    env-only — value never committed, logged, or pasted.

## Next session pointers

- Phase D content generation: region-scoped batches per the phase-report pattern
  (exemplar-first, validator-gated), staffed via `docs/60_agents/roles/ORG.md`. Start with
  R1 Emberfoot; ONBOARDING_FTUE.md now constrains R1's quest/NPC shape, WRITING_STYLE.md +
  WORLD_LORE.md constrain all flavor text.
- Before/while landing D: resolve the F-wave cross-doc items — ECONOMY faucet amendment
  (COLLECTIONS), MAPS_SYSTEM §5 governance pointer (AUDIO_DESIGN), `sighted` radius
  confirmation (AI_BEHAVIOR).
- Owner-priced questions (hosting, storefronts, SSO, retention, signing) are collected in
  PHASE_F_INTEGRATIONS_REPORT.md's rollup — none block Phase D.

## Open Questions
- Should this file also index per-doc Open Questions between phase gates, or stay a
  state/decisions digest only (rollups live in phase reports + VALIDATION §7 at the E
  gate)? Default: digest only.
