# memory.md — Generation State & Decisions Log

State file for future sessions. Read after `README.md` → `docs/00_vision/GLOSSARY.md` →
`docs/WORLD_PLAN.md` (per CLAUDE.md). Newest entries last. This file records *state and
decisions*; rules live in their owner docs — never restate them here.

## Current state (as of 2026-07-23)

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
- **G (equipment v2) ✅** — see `docs/phase_reports/PHASE_G_EQUIPMENT_REPORT.md`. Slot roster
  is now eleven tokens / ten worn positions (`shield`, `overall` added); `10_systems/SCROLLS.md`
  (new) owns affix-line gear modification; ITEMS §8 weights rebalanced to six armor slots;
  ID_REGISTRY extended (equip `0231`–`0250`, use → `0100`).
- **H (consistency wave) ✅** — see `docs/phase_reports/PHASE_H_CONSISTENCY_REPORT.md`. The
  v2 straggler (B-revision) wave finally ran: Rift/raid → future arcs (PQ finales carry the
  party-instance machinery), waygates → paid Coachworks end-to-end, v2 numbers propagated
  (job gates 8/40, 56 skills, T1–T6, 5 bind towns, 8 pools). New docs:
  `10_systems/social/PARTY_QUEST.md`, `40_assets/SKILL_ANIMATION.md`. C-gate closed:
  `base_move_speed` 128 px/s, `mob_ability_*`/summon-template ID blocks, frozen `condition`
  enum, VALIDATION §5 edge-set wording. **`tools/validate.py` exists and the tree validates
  clean (80 files, 0 fails)** — run it on every batch per VALIDATION's protocol.
- **GLOSSARY Provisional:** `title` (from COLLECTIONS §7); `shield` / `overall` / `req_line`
  and the scroll vocabulary (`aspect`/`temper`, `steady`/`bold`/`perilous`,
  `scroll_kind`/`scroll_tier`/`slot_family`) from the G wave — all pending promotion.
- **I (backend-design suite) ✅** — see `docs/phase_reports/PHASE_I_BACKEND_REPORT.md`. The
  full `70_integrations/` authoritative-server suite is authored and gated: BACKEND_ARCHITECTURE
  (revised), ACCOUNTS_AUTH (revised), WORLD_CHANNELS, DATABASE_PERSISTENCE, NETWORK_PROTOCOL,
  GAMEPLAY_SIMULATION, CHAT_SOCIAL_BACKEND (new). ID_REGISTRY gained the engineering-side
  packet-opcode block (`op_0001`–`op_9999`, 13 domain ranges; 103 opcodes minted in
  NETWORK_PROTOCOL §9). Tree validates clean (88 files, 0 fails).

## Decisions log

- **I wave (2026-07-23, backend-design suite):** decision authority was owner-delegated to the
  session (kickoff prompt), so these are decided, not open: server stack = engine-independent
  Elixir/OTP + Phoenix (headless Godot and Go rejected); storage = one PostgreSQL database with
  `char`/`wallet`/`social` schemas + least-privilege roles (separate databases rejected — value
  transfers must commit without 2PC; doc 1 amended to match doc 4), append-only off-Postgres RNG
  audit log, Redis/ETS never truth; tick model = 20 Hz sim / 10 Hz snapshot, per-map parked
  loops, queued deterministic combat drain, timestamp timers, 20 Hz accept-if-plausible
  reconciliation (resolves PERSISTENCE §4's deferred flag by delegation); wire = WSS +
  MessagePack, positional envelope, protocol_version handshake, 15 s heartbeat inside
  ACCOUNTS_AUTH's 90 s reconnect grace; auth = Argon2id, opaque 60-min tokens + 30-day rotating
  refresh, fail-closed re-derive+range-check import (answers PERSISTENCE §9); channels =
  demand-driven, cap 5/map, 150/60 occupancy, 2,000/node; arenas are shared reset-when-empty
  maps — only PQ gates allocate per-party instances; `intent` is a NETWORK_PROTOCOL wire-role
  annotation, deliberately NOT a fourth PERSISTENCE tag. Open-questions rollup in
  PHASE_I_BACKEND_REPORT.md §4; telemetry/build/PixelLab runbook deliberately untouched.

- **H wave (2026-07-23, consistency):** raid tier explicitly future-arc (PQ finales own
  party-instancing; `pq_life = normal_life·70·N`, boss-row damage, 10-min enrage); coach fares
  `100×hops` + 25-shard ferry (ECONOMY §4.3); Sunken drop chute `map_176`→`map_094` replaces
  the v1 termini; `base_move_speed` 128 px/s; `mob_ability_<mob>_NN` + `mob_151`–`160` summon
  blocks; `condition` enum frozen at 4 values; `sighted` = `max(aggro_radius, 6)` tiles;
  tonic bands re-split across Lv 1–42; `steady` scroll shelf priced.

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
- **G wave (2026-07-22, equipment v2):**
  - Slot roster: added `shield` (class-agnostic off-hand, in the §8 armor budget) and
    `overall` (one piece filling `body`+`legs`, w=0.44, single affix budget); rejected
    earrings/face/eye/extra rings (silhouette, UI budget, stat dilution) as future-arc
    candidates. Full-set armor target `K(L)/3` unchanged — budget split six ways.
  - Class law preserved: weapons line-locked, everything else class-agnostic; `req_line` is
    an *optional* hard lock allowed only on advancement rewards + boss uniques; any wider
    class-locking filed as an owner question against SCOPE.md, not decided.
  - Scrolls (SCROLLS.md) never touch base lines or budgets — `aspect` rerolls / `temper`
    raises affix lines inside ITEMS §10's caps; fails consume the scroll only (no item
    destruction/downgrade anywhere in the tree, P2); `steady`-only vendor shelf keeps the
    system sink-dominant; no pity (item never at risk).
  - IDs: scroll SKUs `item_use_0061`–`0078` (3 families × 2 kinds × 3 tiers, layout in
    SCROLLS §5); shield/overall `item_equip_0231`–`0250`; boss-unique `0199+2n` untouched.

## Next session pointers

- Phase D content generation is **unblocked**: region-scoped batches per the phase-report
  pattern (exemplar-first, validator-gated — `python3 tools/validate.py <batch>`), staffed via
  `docs/60_agents/roles/ORG.md`. Start with R1 Emberfoot; ONBOARDING_FTUE.md constrains R1's
  quest/NPC shape, WRITING_STYLE.md + WORLD_LORE.md constrain all flavor text,
  PARTY_QUEST.md constrains the R2/R8 PQ maps + handler quests.
- Remaining pre-D owner items: COLLECTIONS set-completion `shards` faucet amendment (ECONOMY —
  titles-only until then); COMBAT_FORMULA §15 `mult m` retune check (tenth affix slot,
  ~+11% affix pe, flagged in PHASE_G_EQUIPMENT_REPORT.md).
- Owner-priced questions (hosting, storefronts, SSO, retention, signing) are collected in
  PHASE_F_INTEGRATIONS_REPORT.md's rollup, extended by PHASE_I_BACKEND_REPORT.md §4 (pooling
  layer, audit retention, vendor picks) — none block Phase D.
- The backend suite (`70_integrations/`, I wave) is design-complete; its cross-doc residue
  (world-channel promotion, report-table schema, listing-fee ownership, rounding convention)
  is indexed in PHASE_I_BACKEND_REPORT.md §4 for the owning docs' next passes. A LIVE_OPS.md
  successor doc is proposed-but-deferred (report §5).
- Phase E (coding-pass briefs in `60_agents/`, VALIDATION Open-Questions rollup) is still
  unstarted; validator checks 5–6 land with the Phase D world-graph reconciler.

## Open Questions
- Should this file also index per-doc Open Questions between phase gates, or stay a
  state/decisions digest only (rollups live in phase reports + VALIDATION §7 at the E
  gate)? Default: digest only.
