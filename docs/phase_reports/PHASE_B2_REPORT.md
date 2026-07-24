# PHASE_B2_REPORT — v2 Reconciliation + Pacing Retune (2026-07-24)

Executed by the producer session on `claude/game-design-org-review-dispatch-wq01tp`, per the
§6 dispatch plan in `DESIGN_ORG_REVIEW_2026-07-24.md` (the driving audit). Companion to
`PHASE_A_REPORT.md` / `PHASE_B_REPORT.md`. Decisions are logged in `memory.md`; this report
records what changed and what remains open.

## 1. What this run fixed (TLDR)

The tree was split-brain after the 2026-07-21 v2 owner revision: vision/world/registry docs
were v2, but ~20 systems/maps docs, all 5 entity schemas, and parts of the org charter were
still v1 (cap 100, gates 8/30/60, Rift/raid tier, free waygates, 12 regions, 4 towns). This
run reconciled every live doc to the owner-ratified Decision Contract **C1–C9** (recorded
verbatim in `memory.md`) and then applied the same-day pacing amendment **C3′**.

## 2. Waves executed

- **Wave 0 (producer, serial):** imported the audit; aligned SCOPE + PILLARS (Lv-80 gate,
  pacing anchors, paid-coach P3); added the C7 Lv-40 gear tier to ID_REGISTRY (tier 7,
  28 weapons / 35 armor inside existing blocks); created `memory.md`.
- **Wave 1 (four parallel lanes, disjoint files):**
  - *Systems (Lane A):* full balance-surface retune of `10_systems/` — curve, gates,
    skill/stat budgets, combat budgets/TTK, quest/fee/tonic/drop tables, death bands
    (8–39 / 40–79 / 80+), six v2 bind/bank towns, raid/Rift deletions.
  - *Maps (Lane B):* `15_maps_system/` — waygate network → paid Harthmoor Coachworks
    (+ free novice pilgrimage ride), v2 counts, 8 biomes (+4 reserved), PQ-finale
    party-instancing, run_speed discrepancy flagged (not guessed).
  - *Social (Lane C):* created `social/PARTY_QUEST.md` (C8); PARTY dropped Rift raids;
    GUILD founder gate → Lv 40.
  - *Org (Lane D):* architect owns `15_maps_system/` + `social/` (producer sign-off);
    added `ROLE_MONSTER_DESIGNER.md`; resolved ART_GENERATION_RUNBOOK double-claim
    (integration engineer owns, art director QA veto); VALIDATION declared producer-owned.
  - *Producer:* applied Lane B's VALIDATION §5 rewording (ring edges legal, `dead_end`
    carve-out, coach portals excluded from walk-edge checks).
- **Wave 2 (parallel):** all 8 schema docs rewritten to v2 (no third-tier or raid
  emissions; 9 JobData; 56 skill files; coach tokens; PQ finales `map_042`/`map_200`);
  read-only QA sweep of the whole tree.
- **QA outcome: PASS-WITH-FLAGS.** All residue patterns clean or legitimate; fixes applied:
  CAMERA "15 boss arenas" → 8; ANIMATION_STATES boss/raid super-armor wording; stale
  MAP_CONNECTIONS OQ resolved; `drop_table.schema` 12-pool残 → 8 (producer sweep). The two
  substantive findings — ECONOMY's missing coach-fare table and the Return Scroll
  free-vs-paid contradiction — were resolved in the C3′ pass (below).
- **C3′ pacing amendment (owner directive, same day):** see §3.

## 3. Final progression contract (as landed)

- Cap **300**; arc 1 authors **Lv 1–42**. Gates: 1st **Lv 8** · 2nd **Lv 40** · 3rd
  **Lv 80** (gate canonized; content reserved for future arcs).
- Curve (LEVELING.md §1): `exp_per_kill_normal(L) = round(4·L^1.3)`;
  `kills_per_level(L) = round(20 + 6.6·L + 0.2·L²)` (C3′ — supersedes C3's `20 + 0.26·L²`);
  played model `kills_per_level / (480 × 0.70)`.
- Anchors: Lv 8 ≈ 1 h · **Lv 40 ≈ 30 h** · Lv 42 ≈ 33.5 h · Lv 60 ≈ 80 h ·
  **Lv 80 ≈ 166 h (≈5–6 weeks at 4–5 h/day)** · **Lv 100 ≈ 300 h**. The C3 target
  "3rd job in ≈1 month" was superseded by the owner's 30 h/300 h directive.
- Counts: 200 maps (6/20/99/53/14/8) · 150 monsters (118/24/8) · 8 bosses / 16 uniques
  (`0201`–`0216`) · 56 skills (13×4 + 4; `014`–`021` reserved) · 7 gear tiers
  (Lv 1/8/15/22/29/36/40).
- Travel: paid coach network (fares published in ECONOMY §7: 300 / 1,000 / 1,800 shards by
  ring hop; ferry 150; Return Scroll `item_use_0013` repriced to 2,500 as a paid recall).

## 4. Open Questions rollup (owner/next-session attention)

Live copies sit in each owning doc; the load-bearing ones:

1. **Lv 100–300 curve tail** — segment law deferred (C3/C3′ fix anchors ≤100 only).
2. **480 kills/h and 70%-hunting constants** — unmeasured; Phase D spawn/TTK data
   re-verifies (LEVELING).
3. **run_speed 128 px/s vs base_move_speed 200 px/s** — AB-001 locks the grid, not the
   speed; unresolved at the C gate (MAP_TRAVERSAL ↔ COMBAT_FORMULA).
4. **ART_BIBLE.yaml `biome_identity`** lists the 4 reserved biomes with no "reserved"
   marker — locked file; route an annotation through the art director's amendments channel.
5. **ITEMS accessory grid (21) vs SCOPE count (16)** — Phase D authors accessories at
   fewer bands within the reserved range (ITEMS OQ).
6. **Clockwork 2nd-advancement trial** needs a map/quest allocation in the Clockwork
   blocks at Phase D (JOBS OQ).
7. **Fare first-pass balance** — flat fares shrink as income grows; D-gate check that
   1,800 shards isn't punishing at Lv 8–14 (ECONOMY OQ).
8. **PQ details** — reward lockout, solo reduced-reward factor, level-band edge rules
   (PARTY_QUEST/DROPS/ECONOMY OQs).
9. **Referenced-but-missing files** — `40_assets/SKILL_ANIMATION.md` (cited by
   skill.schema, ANIMATION_STATES, SPRITESHEET_SPEC, VALIDATION §6): author at Phase C
   follow-up or re-point citations; `WRITING_STYLE.md` (defensive citation, fine);
   `tools/` validator (checks remain manual until it lands); `70_integrations/`
   (future, correctly marked). `GENERATE.md` is intentionally out-of-repo (README).
10. **Suggested VALIDATION check** (producer sign-off pending): no live doc may cite the
    retired anchors/constants (0.26 coefficient, 18/21/58/134/260 h, exp 211,024/247,164).

## 5. For Phase D

Staff per `60_agents/roles/ORG.md` including the new ROLE_MONSTER_DESIGNER; region-scoped
batches, exemplar-first, validator-gated (manual until `tools/` exists). The four trainer
home towns are canonical in `job.schema.md`; PQ finale arenas are the only party-instanced
maps. All balance tables now trace to LEVELING §1 (C3′) — do not re-derive from old reports.

## Open Questions

- None owned by this report itself; see §4 for the rollup of owning-doc entries.
