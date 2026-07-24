# MD_AUDIT_REPORT_2026-07-24 — Repo-Wide Markdown Audit, Cleanup & Consistency Pass

Status: **complete** (owner-directed audit, 2026-07-24; branch `claude/md-audit-2026-07-24`,
presented for owner review — **nothing merged to `main`**). Scope: every markdown file in the
repo (117) plus `docs/40_assets/ART_BIBLE.yaml` and targeted `docs/50_content/` YAML where md
claims required value checks; the 120 quest files for the owner-flagged `exp` regen; the
`docs/mockups/` wireframe set. Method: 8 region-scoped read-only reviewer sub-agents
(ORG.md medium/Sonnet routing) under a grill-style evidence contract (verbatim quote + real
line numbers + severity + owner-doc ruling per finding), findings adjudicated and applied
centrally by the producer; 6 more sub-agents authored the mock-up wave. Gates ran before every
commit: `tools/validate.py` **0 failures / 0 warnings** at every step; `tools/md_graph.py`
1 component / 0 orphans throughout.

References: `CLAUDE.md`, `README.md`, `memory.md`, `docs/VALIDATION.md`,
`docs/phase_reports/MD_CONNECTIVITY_REPORT.md`, `tools/regen_quest_exp.py`,
`docs/phase_reports/DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md`

## 1. Coverage

| Bucket | Count | Notes |
|---|---|---|
| md files reviewed | **117/117** | 8 reviewer clusters: root+memory · vision+systems×2 · social+maps · schemas/registry · engineering+integrations · assets+agents · phase reports |
| md files edited | 60 | commits 1, 2, 5 below |
| md files verified clean (untouched) | 57 | incl. PILLARS, ELEMENTS, COMBO_SYSTEM, ENHANCEMENT, INVENTORY, STATS, STATUS_EFFECTS, SKILL_EFFECTS, WRITING_STYLE, CHAT/MAIL/MARKET/TRADING, MAP_INTERACTABLES, job.schema, monster.schema, drop_table.schema, ANIMATION_TIMING, SKILL_ANIMATION, SPRITESHEET_SPEC, 6 role files, PHASE_A/D/G/I + SYNC_AUDIT + BACKEND_CHECKLIST reports |
| content YAML edited | 143 | 120 quest files (mechanical regen) + 23 files (grey→gray flavor strings) |
| change-controlled files amended (owner-authorized this run) | 2 | `UI_ART_SPEC.md` **UA-002**, `ENGINEERING_STANDARDS.md` **ES-002** — both structural conformance (the `## Open Questions` law), logged in each file's amendments ledger; `ART_BIBLE.yaml` needed **no** edit (verified clean: AB-001/AB-002 intact, palette/sizing/biome keys all check out) |
| tools added | 1 | `tools/regen_quest_exp.py` (+ `tools/README.md` section) |
| mock-ups | 1 refreshed + 5 new | §7 |

Commit ledger (one concern each, oldest first):
`f98350c` relevance pass (15 files, +66/−59) · `1967000` contradiction + link/connectivity
fixes (48 files, +284/−126) · `d8360e7` US-spelling content sweep (23 files, ±31) ·
`1731daf` quest-exp regen content + tool (121 files, +401/−120) · `14da263` stale-exp OQ
closures + FTUE verification (4 files) · then the mock-ups commit and this report's commit.

## 2. Relevance pass — every removal / supersession marker (Task 1)

Phase reports and amendment logs were **never rewritten** — supersession is marked by dated
additive banners (the pattern `PHASE_D_ARC2_REPORT.md` and `BACKEND_CHECKLIST_AUDIT` already
model). Deletions elsewhere were surgical, each replacing stale text with the owner-doc link.

| File | What | Why |
|---|---|---|
| `phase_reports/ARC2_PLAN_REPORT.md` | + status banner | its "arc-2 ≈ 90 played hours" superseded by the 2026-07-24 retune (LEVELING §1: arc-2 span ≈ 136.6 h) |
| `phase_reports/PHASE_B_REPORT.md` | + status banner | "~201h to cap" superseded by ratified anchors 30/166/300 h |
| `phase_reports/PHASE_F_INTEGRATIONS_REPORT.md` | + status banner | "3-slot symmetry" superseded by the 3→4 slot ruling |
| `phase_reports/PHASE_H_CONSISTENCY_REPORT.md` | + status banner | its v2 re-anchor target (two islands / 2 PQs) itself superseded same-day by v3 |
| `phase_reports/DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md` | + status line under the H1 | resolution lives 280 lines down in §5; readers took §1–§2 as open |
| `60_agents/BACKEND_KICKOFF_PROMPT.md` | + EXECUTED banner | prompt was run 2026-07-23 (Phase I complete); read as live and re-runnable |
| `10_systems/ACCOUNT.md` | name-law enumeration → bare §5 pointer | Law 2: restated ACCOUNTS_AUTH §5's five sub-rules while claiming not to |
| `README.md` | closing rules paragraph → CLAUDE.md Laws pointer | Law 2 restatement |
| `10_systems/ITEMS.md` | stale OQ bullet closed (registry re-block/tonics/SCOPE counts all landed); stale ENHANCEMENT worked-example clause dropped | verified against ID_REGISTRY, consumables.yaml, SCOPE (~170 equip), ENHANCEMENT §4 (T6 W=151 already correct) |
| `10_systems/JOBS.md` | two stale OQ bullets closed | skill re-block landed in ID_REGISTRY exactly as specified; all six spec tokens already in GLOSSARY |
| `10_systems/SPAWN.md` | filename OQ removed | `20_schemas/map.schema.md` exists and cites SPAWN |
| `10_systems/SCROLLS.md` | "lands in a companion commit" → landed (past tense) | registry extension is in ID_REGISTRY |
| `10_systems/social/PARTY_FINDER.md` | stale token OQ → dated resolved note | all five `activity` values are canonical GLOSSARY tokens |
| `10_systems/social/PARTY.md` | stale HUD OQ → dated resolved note; `party_drop_bonus` ladder restatement trimmed to a DROPS §4.1 citation | HUD §4.1/§11 landed the region; Law 2 (the doc restated the table right after saying "never restated here") |
| `memory.md` | tail paragraph relocated | the 2026-07-24 gameplay-loop entry sat unheaded at the file tail inside the 2026-07-23 section, violating the file's own newest-first law; content preserved verbatim with a relocation note |
| `00_vision/GLOSSARY.md` | Provisional `coach_station`/`coach_clerk`/`pier_officer` promoted into Transport | their stated condition ("promote at the C gate") long met — consumed by minted maps (017/018/043/071/125) and NPCs (011/016/034/042/043/063/085/097/109) |
| `docs/WORLD_PLAN.md` + `MAP_CONNECTIONS.md` + `ROLE_NARRATIVE_WRITER.md` | stray "(v2.3)"/"(v3)"/"v2.3" vintage tags dropped | 2026-07-24 de-label ruling (tree reads as one design; dated history remains) |

## 3. Contradiction sweep — ruling ledger (Task 2)

Every row: the docs in conflict → which owner doc won → the landed fix. Severities are the
reviewer-cluster ratings, verified before edit.

| # | Sev | Conflict | Ruling (winner) | Fix |
|---|---|---|---|---|
| C1 | CRITICAL | `ORG.md` "Locked files … touched by no one" vs CLAUDE.md Law 5 (change-controlled, owner-directed amendments — AB/UA/ES precedents exist) | CLAUDE.md Law 5 | ORG standing law rewritten; "locked"→"change-controlled" swept through ROLE_PRODUCER/ART_DIRECTOR/INTEGRATION/BACKEND/SECURITY, COLLECTIONS, README, ART_GENERATION_RUNBOOK, DATABASE_PERSISTENCE, memory/systemPatterns, memory/projectbrief |
| C2 | CRITICAL | `memory/techContext.md` "Character slots: 3" vs ACCOUNTS_AUTH §2.2 = 4 | ACCOUNTS_AUTH §2.2 | fixed with citation (a coding pass reading only the Memory Bank would have built the wrong quota) |
| C3 | CRITICAL | `item.schema.md`/`skill.schema.md` hard-require `icon`; **zero** minted item/skill rows carry it; `validate.py` doesn't check it and its `ALLOWED["skill"]` would **reject** it | undecided — genuine owner design call | **flagged, not fixed**: VALIDATION.md Open Questions now carries the gap with the two legal resolutions (backfill batch + validator enforcement, or amend schemas to derived-implicit since `icon` is 100% derivable from `id`) |
| C4 | HIGH | `BACKEND_ARCHITECTURE.md` §7 "All six" social systems vs `PARTY_FINDER.md` (a seventh, equally server-deferred) | PARTY_FINDER.md exists | §7 row added ("All seven"); `CHAT_SOCIAL_BACKEND.md` §3.7 stub added (shape/store/failure mode from PARTY_FINDER's own §7; internals stay flagged there) |
| C5 | HIGH | `DATABASE_PERSISTENCE.md` §3 claims every PERSISTENCE §2 row lands, but §2.1 time-gated counters (raid daily/cooldown, guild weekly) had no table | PERSISTENCE §2.1 | `character_time_gate` sketch added to §3.1; guild-scoped counters routed to §3.3 |
| C6 | HIGH | `TELEMETRY_ANALYTICS.md` "≤3 save slots" | ACCOUNTS_AUTH §2.2 | ≤4, citation corrected |
| C7 | HIGH | `WIKI_EXPORT.md` frames the generator as unbuilt future work vs landed `tools/wiki_gen.py` (805 pages) | reality | landed-tool note added to §4; remaining future scope delineated. Residue: the doc lists 7 page types incl. **job**; the tool generates no job pages yet — noted here, not a doc defect |
| C8 | HIGH | `50_content/README.md` "all 12 `pool_equip_rNN`" vs 11 regions everywhere (ID_REGISTRY, drop_table.schema, the real pools.yaml) | ID_REGISTRY / schema | 12→11 |
| C9 | HIGH | `50_content/README.md` lists quest→NPC refs under "bidirectional (both sides must exist)" vs npc.schema's single-source rule (NPC files carry **no** reverse quest field; listing one fails conformance) | npc.schema.md | quest refs re-classed as one-way (VALIDATION §2) |
| C10 | HIGH | `MAP_TRAVERSAL.md` — GLOSSARY names it the `foothold` model owner (AB-001) but the word "foothold" appeared nowhere; whole contract read as axis-aligned tiles | GLOSSARY + AB-001 | foothold block added to §1 (segments = ground truth; tile grid = measurement/validation lens; geometry deferred to Phase E per SCOPE) |
| C11 | HIGH | `PARTY_FINDER.md`/`PARTY.md` stale OQs contradicted GLOSSARY (tokens live) and HUD §4.1 (region reserved) | GLOSSARY / HUD | resolved notes (see §2) |
| C12 | MEDIUM | `SCOPE.md` "§3.1 layer stays reserved" vs `COSMETICS.md` "lands here for the earned side" | COSMETICS.md (owner, newer) | SCOPE bullet reworded: system design in scope, store content still unauthored/unsold |
| C13 | MEDIUM | `COMBAT_FORMULA.md` §13.3 enrage-wipes-party vs `RAID.md` §5's exhaustive two-condition wipe list | RAID.md owns wipe handling | enrage expiry added as third trigger, citing §13.3 for the 12-min value |
| C14 | MEDIUM | `NETWORK_PROTOCOL.md` "103 opcodes minted" vs 106 by row count (op_0105/0194/0406 minted 2026-07-24) | the catalog itself | count corrected with provenance; **no opcode renumbered** |
| C15 | MEDIUM | `SPAWN.md` `mob_pool` = `{mob_id, weight}` relative odds vs landed `map.schema.md` `mobs:[{mob, count}]` absolute populations (different runtime algorithm; 150+ minted maps use the schema shape) | undecided — SPAWN is the system owner | **flagged, not fixed**: reciprocal OQ added to SPAWN (adopt or dispute); schema's own OQ already asked for this confirmation |
| C16 | MEDIUM | `SKILL_SYSTEM.md` treats the 8-slot bar as open vs HUD §3 fixing 8 + Dodge | HUD.md (named co-owner) | OQ closed with citation |
| C17 | MEDIUM | `UI_WINDOWS.md` paper-doll cites COSMETICS **§4** (earning) for display order; never cites CHARACTER_COMPOSITING at all | COMPOSITING §2 owns layering; COSMETICS §5–§6 own overrides | citation fixed + References updated |
| C18 | MEDIUM | `ONBOARDING_FTUE.md` "≈10-minute gap" vs its own arithmetic (1.1 h − 60 min ≈ 6 min; 3,800 exp = the full Lv 7→8 level ≈ 13.7 min) | the doc's own numbers | reworded: ≈6-min overage, closed with margin by budgeting a full Lv 7→8 level (≥ 3,800) |
| C19 | MEDIUM | `MAP_LAYERS.md` `terrain` = "standard solid collision" with no foothold/AB-001 bridge | AB-001 | cell reconciled (chunks on footholds; 16 px grid still governs built structures) |
| C20 | MEDIUM | `MAPS_SYSTEM.md` owes QUESTS §3 the `reach`-step trigger-zone declaration; neither field nor OQ existed on its side | QUESTS' handoff stands | reciprocal OQ added (shape + validator question), field not invented |
| C21 | MEDIUM | stale connectivity counts ("98/98") in CLAUDE.md and memory/progress.md; MD_CONNECTIVITY_REPORT still described the 97-file tree | live tree (117) | counts fixed; report regenerated (§5) |
| C22 | MEDIUM | `npc.schema.md`/`map.schema.md` examples drift from the minted rows they appear to depict, with stale "land in Phase D" tense (quest.schema discloses its non-mirror; monster/drop_table verified byte-exact) | minted content | explicit non-mirror disclaimers + tense fixed; `item.schema.md` heal example synced 120→60 to the minted item_use_0001 |
| C23 | LOW | `DISPLAY.md` Alt+Enter pointed at CONTROLS §5 (rebinding policy); §1's map lacked the binding | CONTROLS owns bindings | §1 row added; DISPLAY pointer retargeted |
| C24 | LOW | `CAMERA.md`/`HUD.md` OQs still "waiting on a target resolution" | DISPLAY.md landed it | OQs updated to cite DISPLAY §2 (both docs now link the previously inbound-linkless DISPLAY.md) |
| C25 | LOW | `WORLD_CHANNELS.md` §7 lacked the v2-sizing provenance memory/PHASE_I attribute to it | phase-report record | provenance clause added to the existing OQ |
| C26 | LOW | `ROLE_ART_DIRECTOR.md` never mentions ENGINEERING_STANDARDS/ES- channel though Law 5 groups all three under "Agent-3 / master brief" | ambiguous | **flagged, not fixed**: OQ added to the role file (who operates ES-) |
| C27 | LOW | `ANIMATION_STATES.md` References line omitted TIMING/SKILL_ANIMATION (cited in body) | — | References completed |
| C28 | MEDIUM | `WORLD_PLAN.md` §R2's positional interior list put the guild hall at `map_022` vs GUILD.md + minted content = `map_024` (022 is the smithy) — found by the mock-up wave | minted IDs win over prose (the July-24 sweep's own precedent) | §R2 parenthetical reordered to the minted ID order, guild hall pinned `map_024` |
| C29 | MEDIUM | `ECONOMY.md` §7.1's 3+-segment coach tier example ("longest ring hop — Cindershelf ↔ Tidewatch Port") is topologically impossible: WORLD_PLAN's ring-closure edge makes that pair adjacent; no station pair appears to reach 3+ segments — found by the mock-up wave | undecided — fare design is ECONOMY's call | **flagged, not fixed**: ECONOMY.md Open Question raised (re-example + keep as headroom, or drop the 320-shard row). The §7.2 longship route→fare-class gap is already self-flagged in ECONOMY's existing OQ |
| C30 | LOW | `DEATH_PENALTY.md` OQ still lists fallen-member party-frame handling as fully open vs HUD §4.1's landed rendering resolution — found by the mock-up wave | HUD.md §4.1 | OQ marked partially resolved (render half settled; loot-eligibility half stays PARTY §6's) |

Also verified **consistent** (no action, reviewer-confirmed with recomputation where numeric):
world totals 324/234 (178/45/11)/11/4 and every WORLD_PLAN table sum; the full LEVELING §1
table and QUESTS §4 table on the ratified curve (every row independently recomputed, incl.
Lv 90/99); LEVELING §3.1's raid grant percentages (all 12 denominators recomputed); ECONOMY
§7.1 single fare table + tonic/T11/T12 prices; DROPS ×2.73/×2.86 ceiling + party_drop_bonus
ladder; GUILD numbers incl. hall = map_024 (checked against minted map files); RAID roster
(bands/maps/bosses/15-min cooldown); DEATH_PENALTY arc-2 bind ports; COMBAT_FORMULA life
checksum table (every row) and the §14/§15 TTK-vs-combo envelope; ITEMS §4 weapon layout
vs minted weapons.yaml id-for-id and §13 Quartermaster math; SCROLLS §5 vs ID_REGISTRY;
ID_REGISTRY block integrity (no overlaps; style/opcode/cosmetic blocks exact);
CHARACTER_COMPOSITING ~34-frame math vs ANIMATION_STATES budgets (33.5 ≈ 34; §9's 974-frame
sum re-added); AB-001/AB-002/UA-001/ES-001 amendment logs intact; ACCOUNTS_AUTH slot
consistency; NETWORK_PROTOCOL op_0191=4 slots, name-check pair + appearance delta in-range,
zero pq_* opcodes; STATS §4.2 already cap-300-aware; AUTONOMOUS_MAINTENANCE already on the
current Law-5 wording; tools/README.md accurate against all three (now four) scripts;
banned-token sweep: **zero hits** outside VALIDATION.md across all 117 files.

## 4. Validation (Task 4)

- `tools/validate.py` (VALIDATION §1–§6): **0 failures / 0 warnings** before the audit, after
  every commit, and at the end.
- Banned legacy tokens (§1): zero occurrences outside `docs/VALIDATION.md` (mechanical
  whole-word sweep + all 8 clusters).
- US spelling: the only violation family tree-wide was `grey` → `gray` — 31 flavor-string
  hits across 23 content YAMLs (monsters/maps/materials), fixed in the dedicated content
  commit `d8360e7`. All md files clean.
- ID ranges: no violations; **no ID renumbered anywhere** in this audit.
- `## Open Questions` structural law: two violations found and fixed via owner-authorized
  amendments (UA-002, ES-002) + one plain fix (`50_content/README.md`). Every doc now ends
  with the section.

## 5. Connectivity — before / after (Task 3)

| Metric | Before | After |
|---|---|---|
| md files | 117 | 117 (this report +1 at its commit) |
| Undirected | 1 component, 0 orphans, ~1,546 edges | 1 component, 0 orphans, ~1,566 edges |
| CLI degree check ("unreferenced") | 0 — **misleading** | 0 |
| **True directed BFS** from README/CLAUDE/memory | **112/117 — the 5 `memory/*.md` Memory-Bank files were unreachable** (self-linking cluster; nothing outside `memory/` linked in) | **117/117** |
| Stale counts | CLAUDE.md + memory/progress.md said "98/98" | 117/117 everywhere |

Fixes: `memory.md` header now chains to the Memory Bank; README gained `memory.md`/`memory/`,
`docs/mockups/`, `tools/wiki_gen.py`, and the two missing phase-report entries
(`DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md`, `GAMEPLAY_LOOP_REVIEW_2026-07-24.md`);
CLAUDE.md's reading path extends through `memory/`. `MD_CONNECTIVITY_REPORT.md` was
regenerated (117-file state, the degree-check-vs-BFS caveat, first-audit history preserved).

**Reading-path check (newcomer completeness):** README → GLOSSARY → WORLD_PLAN → systems now
reaches every subsystem: design+gameplay via `10_systems/`+`15_maps_system/`, art via
`40_assets/` (compositing included via the runbook + UI_WINDOWS fixes), backend via
`70_integrations/` (party_finder now wired), live state via `memory.md`+`memory/`, tooling via
`tools/README.md`, visuals via `docs/mockups/`. The previously context-free docs — DISPLAY.md
(zero inbound links in docs/), the Memory Bank, the two 2026-07-24 review reports — all have
natural inbound pointers now.

## 6. Quest-`exp` regen (Task 5)

- **Script:** `tools/regen_quest_exp.py` (stdlib; dry-run default; `--apply`;
  `--table-out`). Parses each quest's authored `pct` from the `exp:` line comment across all
  ~8 region-author comment formats (explicit `pct=`, `round(pct*V)` args, or derived
  `exp/V_old`), derives/cross-checks the quest level via the old curve
  (`kills_per_level_old(L) = round(20 + 0.2·L²)`, reconstructed and verified), round-trip
  verifies `round(pct·V_old) == stored`, then writes `round(pct · exp_to_next_new(L))` with
  `kills_per_level(L) = round(20 + 6.6·L + 0.2·L²)` and refreshes every stale number inside
  the comment (round args, `exp_to_next(L)=V`, arrow arithmetic, factor breakdowns, one
  embedded old-curve formula). Self-test: refuses to run unless its arithmetic reproduces
  every LEVELING §1 + QUESTS §4 table row exactly (round-half-up confirmed as the tree's
  convention).
- **Result:** 120/120 regenerated, 0 parse failures, **0 out-of-band pcts** (main 15–30%,
  side 5–10% — nothing clamped, nothing to clamp). `shards` rewards and monster `stats.exp`
  untouched (never stale). `validate.py` 0/0 after apply.
- **Two Phase-D authoring slips healed** (documented, mechanical, authored intent kept):
  `quest_058` — comment states `pct=0.30 (chain finale, top of band)` twice but the stored
  integer 15,066 was computed at 0.28; authored 0.30 kept → 33,014. `quest_097` — author's
  `exp_per_kill(54)` was 716 (true value 715), so its stored old `exp_to_next` 431,748 was
  off-curve; authored pct 0.09/L 54 kept, true curve used → 61,776 (comment's embedded
  formula updated to the ratified curve, factors `=715*960`).
- **FTUE §2 budget check (Task 5e): CLOSES.** Emberfoot `quest_001`–`010` sum = **3,804**
  `exp` ≥ the 3,800 target (= `exp_to_next(7)`, the full Lv 7→8 level §2 budgets) — the
  60-minute Lv-8 promise holds on quest `exp` alone, before the one-time first-clear grants.
  Quest share of Lv 1→8 cumulative (10,765) = 35%, deliberately above the open-world 25%
  target per §2's grace-band front-loading. Authored pcts: mains 0.20 (finale quest_010 at
  band-top 0.30), sides 0.08 — the "top-of-band" §2 lever is only partially pulled, and the
  budget still closes; noted for the balance pass, no change made.
- **OQs closed (Task 5f):** LEVELING.md and QUESTS.md stale-exp entries marked resolved
  (dated, pointing here); ONBOARDING_FTUE.md's resolved entry gained the mechanical
  verification. Full 120-row before/after table: **Appendix A**.

## 7. Mock-ups (Task 6)

All non-binding wireframes: single-file HTML, inline CSS/SVG only, no external assets, no
generated art; ART_BIBLE palette tokens exactly; 640x360 render base drawn at 2× integer
(1280×720) on an `ink` letterbox; GLOSSARY tokens only (no banned strings anywhere); every
region captioned with its owning doc/§. Linked from README and referenced from
`UI_ART_SPEC.md` as non-binding (amendment UA-003).

| File | Shows | Primary specs |
|---|---|---|
| `docs/mockups/gameplay_scene_mockup.html` (refreshed) | field HUD scene + boss variant + depth stack | HUD.md, ART_BIBLE, UI_ART_SPEC — palette normalized to exact tokens, layout re-synced (wallet right, exp strip, party frames, §6.1 monster bars, combo counter) |
| `docs/mockups/entry_roster_creation_mockup.html` (new) | title/login → 4-slot roster → 3-step creation (check-name, AB-002 swatch pickers, live composite preview) | ACCOUNT.md, CHARACTER_COMPOSITING §7, DISPLAY.md |
| `docs/mockups/town_hub_millbrook_mockup.html` (new) | Millbrook Central cross-section: inn/smithy/market/bank/guild hall (map_024)/coach station + clerk/Raid Quartermaster/undervault quarter, NPC dialog, map-name card | WORLD_PLAN §R2, UI_ART_SPEC, MAP_INTERACTABLES §9, ITEMS §13 |
| `docs/mockups/inventory_character_windows_mockup.html` (new) | Inventory (6-col grid, tabs, wallet footer) + Character (paper-doll ring, GLOSSARY stat column, exp footer) + item tooltip | UI_WINDOWS §2–§3, UI_ART_SPEC, STATS §2 |
| `docs/mockups/world_travel_mockup.html` (new) | five isles, Harthmoor ring + Clockwork center, ferry/coach/longship overlays, Deepway (level_gate 40), longship schedule board | WORLD_PLAN, MAP_CONNECTIONS §8, ECONOMY §7 |
| `docs/mockups/raid_boss_hud_mockup.html` (new) | raid_deepfrost finale (Skoldir, map_244): boss_bar + phase pips (real threshold from minted `mob_178.yaml`), party frames incl. fallen, combo counter, status rings, damage numbers, full bottom bar | HUD.md, RAID.md, WORLD_PLAN §R9 |

The mock-up wave doubled as a lived-in consistency probe: building the screens surfaced three
more findings (C28–C30 above — the guild-hall interior order, the impossible coach-fare
example, the half-stale DEATH_PENALTY flag) that the reading-only clusters had no reason to
compute. The entry mock-up also correctly depicts **no login form** (ACCOUNTS_AUTH §7's solo
build has none — annotated in-file), and the travel mock-up marks its longship fare-tier
placements as illustrative pending ECONOMY's already-flagged route→class mapping.

## 8. Open Questions raised / closed by this audit

**Closed (10):** LEVELING stale-exp regen · QUESTS stale-exp regen · SPAWN schema filename ·
SKILL_SYSTEM skill-bar count · PARTY_FINDER activity tokens · PARTY HUD party-frame region ·
ITEMS registry re-block bullet · JOBS skill re-block · JOBS spec-token promotion · GLOSSARY
Provisional transport-token entry (promoted).

**Raised (6), all flag-don't-guess owner calls:**
1. VALIDATION.md — the `icon` law gap (C3): backfill+enforce vs derived-implicit.
2. SPAWN.md — `mob_pool` weight-vs-count model divergence (C15).
3. MAPS_SYSTEM.md — the owed `reach`-step trigger-zone declaration (C20).
4. ITEMS.md — `shield`/`overall` §2/§10 integration pointer (pre-existing debt, now
   discoverable from the owning doc).
5. ROLE_ART_DIRECTOR.md — who operates the ES- amendment channel (C26).
6. ECONOMY.md — the unreachable 3+-segment coach fare tier (C29).

**Noted, deliberately not acted on:** `combo_momentum`/`combo_burst` stay Provisional (their
stated promotion bar — schema/content field-value consumption — is not yet met, though they
are load-bearing vocabulary in three docs); `item_use_0091`–`0100` reserve has no named
owner (reads as intentional headroom); `tools/wiki_gen.py` generates no job pages while
WIKI_EXPORT lists 7 page types (tool gap, not doc defect); historical phase reports keep
their era's "locked files" wording (point-in-time accurate; only live docs were resynced);
`memory/systemPatterns.md`'s "Fable — Specs" governance tier maps cleanly onto ORG.md's
"Top tier (producer)" routing row — not drift.

## 9. Hard-nosed findings (the roast) — what this audit says about the tree

- **[GOOD] The core is genuinely sound.** Every load-bearing number that was recomputed —
  curves, raid grants, checksum tables, world arithmetic, ID blocks — reproduced exactly.
  The tree's single-source discipline mostly holds; where it broke, it broke in satellites
  (memory bank, role charters, completeness claims), not in owner docs.
- **[HIGH] Completeness claims rot fastest.** "All six systems," "103 opcodes," "98/98
  reachable," "12 pools," "≤3 slots" — five different docs asserted totals that a later wave
  silently invalidated. Every hard count in a doc is a liability unless the wave that changes
  the total greps for it. Recommendation (process, not a doc edit): add "grep the number you
  just changed" to the batch pattern in the next phase brief.
- **[HIGH] The Memory Bank was a parallel-universe risk.** Five files billed as "the distilled
  current-state context for the coding pass" were unreachable from every entry point, 53
  commits stale, and carried a wrong quota (slots: 3). Now linked, corrected, and refreshed —
  but the deeper fix is the one applied: memory/ is in the reading path, so future waves see
  it and keep it honest.
- **[MEDIUM] The validator under-enforces its own §6.** The icon law (C3) shows a "hard"
  schema rule can be 0%-complied and validator-green. When the owner rules on C3, consider
  which other §6 lines deserve mechanical teeth (the animation_notes rule got them; icons
  never did).
- **[MEDIUM] The CLI connectivity check is weaker than the report's methodology.** The
  degree scan said 0 while BFS said 5 unreachable. `md_graph.py --check` with a true BFS
  (existing Open Question, now sharpened) would make this class of drift impossible.
- **[LOW] Comment-format entropy in content.** The quest regen had to parse ~8 comment
  dialects from different region authors. It worked (120/120), but the next mechanical pass
  shouldn't have to be this clever — a one-line canonical comment format in
  `50_content/README.md` would fix it at the next content wave. Not added this run (content
  conventions change with their schema docs; flagged here instead).

**Verdict:** the tree is one design again — the 2026-07-24 wave-cluster's loose ends (pacing
retune fallout, Law-5 rename, Memory Bank isolation, completeness drift) are closed; the
remaining risk is concentrated in the five raised Open Questions, all owner calls, none
blocking Phase E. **Top 3 next actions:** rule on the icon law (C3 — it will bite the coding
pass first); rule on SPAWN's spawn-model wording (C15 — the schema and 150 maps already
voted); run the balance pass with the regenerated quest table (Appendix A) as its input.
**Confidence:** high on everything mechanically verified (curves, counts, IDs, FTUE budget);
medium on the §3.7/time-gate backend stubs (minimal by design — the backend pass should
flesh them); the scariest single find was C3 — a documented hard rule with zero compliance
*and* tooling that rejects compliance, invisible to every gate.

## Appendix A — quest `exp` before/after (120 rows, from `tools/regen_quest_exp.py --table-out`)

| quest | region | type | Lv | pct | exp (old) | exp (new) |
|---|---|---|---|---|---|---|
| quest_001 | emberfoot | main | 1 | 0.2 | 16 | 22 |
| quest_002 | emberfoot | main | 2 | 0.2 | 42 | 68 |
| quest_003 | emberfoot | side | 2 | 0.08 | 17 | 27 |
| quest_004 | emberfoot | main | 3 | 0.2 | 75 | 143 |
| quest_005 | emberfoot | side | 4 | 0.08 | 44 | 96 |
| quest_006 | emberfoot | main | 5 | 0.2 | 160 | 371 |
| quest_007 | emberfoot | side | 6 | 0.08 | 89 | 220 |
| quest_008 | emberfoot | main | 6 | 0.2 | 221 | 549 |
| quest_009 | emberfoot | main | 7 | 0.2 | 300 | 760 |
| quest_010 | emberfoot | main | 8 | 0.3 | 594 | 1,548 |
| quest_011 | millbrook | main | 8 | 0.2 | 396 | 1,032 |
| quest_012 | millbrook | main | 40 | 0.2 | 32,912 | 58,467 |
| quest_013 | millbrook | side | 8 | 0.075 | 149 | 387 |
| quest_014 | millbrook | side | 9 | 0.075 | 189 | 504 |
| quest_015 | millbrook | side | 9 | 0.075 | 189 | 504 |
| quest_016 | millbrook | side | 9 | 0.075 | 189 | 504 |
| quest_017 | millbrook | side | 11 | 0.075 | 297 | 790 |
| quest_018 | millbrook | side | 11 | 0.075 | 297 | 790 |
| quest_019 | millbrook | side | 9 | 0.075 | 189 | 504 |
| quest_020 | millbrook | side | 10 | 0.075 | 240 | 636 |
| quest_021 | millbrook | main | 12 | 0.2 | 990 | 2,586 |
| quest_022 | millbrook | main | 13 | 0.2 | 1,210 | 3,136 |
| quest_023 | millbrook | main | 14 | 0.2 | 1,463 | 3,770 |
| quest_024 | millbrook | main | 14 | 0.2 | 1,463 | 3,770 |
| quest_025 | verdant | main | 8 | 0.25 | 495 | 1,290 |
| quest_026 | verdant | side | 8 | 0.07 | 139 | 361 |
| quest_027 | verdant | side | 9 | 0.08 | 202 | 538 |
| quest_028 | verdant | side | 10 | 0.06 | 192 | 509 |
| quest_029 | verdant | side | 11 | 0.07 | 277 | 737 |
| quest_030 | verdant | side | 12 | 0.06 | 297 | 776 |
| quest_031 | verdant | side | 13 | 0.07 | 423 | 1,098 |
| quest_032 | verdant | side | 14 | 0.08 | 585 | 1,508 |
| quest_033 | verdant | side | 15 | 0.06 | 527 | 1,328 |
| quest_034 | verdant | side | 15 | 0.08 | 702 | 1,771 |
| quest_035 | verdant | main | 16 | 0.2 | 2,087 | 5,204 |
| quest_036 | verdant | main | 40 | 0.2 | 32,912 | 58,467 |
| quest_037 | tidewatch | main | 8 | 0.2 | 396 | 1,032 |
| quest_038 | tidewatch | main | 40 | 0.2 | 32,912 | 58,467 |
| quest_039 | tidewatch | side | 14 | 0.08 | 585 | 1,508 |
| quest_040 | tidewatch | side | 15 | 0.07 | 614 | 1,550 |
| quest_041 | tidewatch | side | 17 | 0.09 | 1,116 | 2,719 |
| quest_042 | tidewatch | side | 17 | 0.06 | 744 | 1,813 |
| quest_043 | tidewatch | main | 18 | 0.18 | 2,616 | 6,279 |
| quest_044 | tidewatch | side | 19 | 0.1 | 1,693 | 4,011 |
| quest_045 | tidewatch | side | 19 | 0.05 | 846 | 2,006 |
| quest_046 | tidewatch | main | 20 | 0.22 | 4,334 | 10,055 |
| quest_047 | tidewatch | side | 21 | 0.1 | 2,257 | 5,162 |
| quest_048 | tidewatch | main | 22 | 0.3 | 7,792 | 17,449 |
| quest_049 | gloomwood | side | 20 | 0.08 | 1,576 | 3,656 |
| quest_050 | gloomwood | side | 21 | 0.08 | 1,806 | 4,130 |
| quest_051 | gloomwood | main | 21 | 0.25 | 5,643 | 12,906 |
| quest_052 | gloomwood | side | 22 | 0.08 | 2,078 | 4,653 |
| quest_053 | gloomwood | side | 23 | 0.08 | 2,379 | 5,249 |
| quest_054 | gloomwood | main | 24 | 0.28 | 9,412 | 20,498 |
| quest_055 | gloomwood | side | 25 | 0.08 | 3,051 | 6,522 |
| quest_056 | gloomwood | side | 26 | 0.08 | 3,422 | 7,220 |
| quest_057 | gloomwood | main | 27 | 0.28 | 13,479 | 27,933 |
| quest_058 | gloomwood | main | 28 | 0.3 | 15,066 | 33,014 |
| quest_059 | ashfall | main | 8 | 0.2 | 396 | 1,032 |
| quest_060 | ashfall | main | 40 | 0.2 | 32,912 | 58,467 |
| quest_061 | ashfall | side | 26 | 0.07 | 2,995 | 6,318 |
| quest_062 | ashfall | side | 27 | 0.07 | 3,370 | 6,983 |
| quest_063 | ashfall | side | 28 | 0.07 | 3,767 | 7,703 |
| quest_064 | ashfall | side | 29 | 0.07 | 4,198 | 8,485 |
| quest_065 | ashfall | side | 30 | 0.07 | 4,662 | 9,277 |
| quest_066 | ashfall | side | 32 | 0.07 | 5,702 | 11,048 |
| quest_067 | ashfall | side | 34 | 0.07 | 6,887 | 13,061 |
| quest_068 | ashfall | side | 34 | 0.095 | 9,347 | 17,726 |
| quest_069 | sunken | main | 30 | 0.2 | 13,320 | 26,507 |
| quest_070 | sunken | side | 30 | 0.07 | 4,662 | 9,277 |
| quest_071 | sunken | side | 31 | 0.08 | 5,885 | 11,576 |
| quest_072 | sunken | main | 32 | 0.18 | 14,661 | 28,410 |
| quest_073 | sunken | side | 33 | 0.06 | 5,384 | 10,315 |
| quest_074 | sunken | side | 34 | 0.09 | 8,855 | 16,793 |
| quest_075 | sunken | main | 35 | 0.22 | 23,728 | 44,412 |
| quest_076 | sunken | side | 36 | 0.07 | 8,242 | 15,272 |
| quest_077 | sunken | side | 37 | 0.1 | 12,848 | 23,511 |
| quest_078 | sunken | main | 38 | 0.28 | 39,194 | 71,030 |
| quest_079 | clockwork | main | 34 | 0.18 | 17,711 | 33,587 |
| quest_080 | clockwork | side | 35 | 0.07 | 7,550 | 14,131 |
| quest_081 | clockwork | main | 36 | 0.2 | 23,548 | 43,635 |
| quest_082 | clockwork | side | 37 | 0.08 | 10,278 | 18,808 |
| quest_083 | clockwork | side | 38 | 0.09 | 12,598 | 22,831 |
| quest_084 | clockwork | side | 39 | 0.09 | 13,647 | 24,514 |
| quest_085 | clockwork | main | 39 | 0.25 | 37,908 | 68,094 |
| quest_086 | clockwork | main | 40 | 0.3 | 49,368 | 87,701 |
| quest_087 | millbrook | side | 14 | 0.075 | 549 | 1,414 |
| quest_088 | millbrook | side | 14 | 0.08 | 585 | 1,508 |
| quest_089 | clockwork | side | 32 | 0.06 | 4,887 | 9,470 |
| quest_090 | clockwork | side | 32 | 0.08 | 6,516 | 12,627 |
| quest_091 | frostpeak | side | 40 | 0.075 | 12,342 | 21,925 |
| quest_092 | frostpeak | side | 42 | 0.07 | 13,473 | 23,478 |
| quest_093 | frostpeak | side | 44 | 0.08 | 17,843 | 30,600 |
| quest_094 | frostpeak | main | 48 | 0.2 | 58,971 | 97,835 |
| quest_095 | frostpeak | side | 51 | 0.07 | 25,099 | 40,763 |
| quest_096 | frostpeak | side | 52 | 0.08 | 30,563 | 49,250 |
| quest_097 | frostpeak | side | 54 | 0.09 | 38,857 | 61,776 |
| quest_098 | frostpeak | side | 55 | 0.1 | 45,750 | 72,322 |
| quest_099 | frostpeak | side | 45 | 0.06 | 14,382 | 24,432 |
| quest_100 | frostpeak | side | 45 | 0.08 | 19,176 | 32,577 |
| quest_101 | arcane_reach | side | 53 | 0.075 | 30,468 | 48,790 |
| quest_102 | arcane_reach | side | 54 | 0.075 | 32,336 | 51,480 |
| quest_103 | arcane_reach | main | 55 | 0.2 | 91,500 | 144,643 |
| quest_104 | arcane_reach | side | 58 | 0.075 | 40,748 | 63,269 |
| quest_105 | arcane_reach | side | 60 | 0.075 | 45,510 | 69,864 |
| quest_106 | arcane_reach | main | 62 | 0.2 | 134,919 | 204,858 |
| quest_107 | arcane_reach | side | 64 | 0.075 | 56,066 | 84,333 |
| quest_108 | arcane_reach | main | 66 | 0.2 | 165,370 | 246,291 |
| quest_109 | arcane_reach | side | 67 | 0.075 | 65,132 | 96,492 |
| quest_110 | arcane_reach | main | 68 | 0.2 | 182,385 | 269,042 |
| quest_111 | voidshore | side | 66 | 0.07 | 57,879 | 86,202 |
| quest_112 | voidshore | side | 68 | 0.06 | 54,716 | 80,713 |
| quest_113 | voidshore | main | 77 | 0.2 | 273,521 | 388,735 |
| quest_114 | voidshore | side | 69 | 0.06 | 57,329 | 84,223 |
| quest_115 | voidshore | side | 74 | 0.06 | 72,051 | 103,650 |
| quest_116 | voidshore | main | 76 | 0.22 | 288,228 | 411,368 |
| quest_117 | voidshore | side | 75 | 0.06 | 75,295 | 107,846 |
| quest_118 | voidshore | side | 80 | 0.08 | 123,864 | 174,172 |
| quest_119 | voidshore | main | 70 | 0.18 | 180,360 | 263,686 |
| quest_120 | voidshore | main | 70 | 0.18 | 180,360 | 263,686 |

(Emberfoot FTUE sum: quests 001–010 new `exp` = 3,804 ≥ 3,800 target — see §6.)

## Open Questions

- The five owner calls raised in §8 live in their owning docs (VALIDATION.md, SPAWN.md,
  MAPS_SYSTEM.md, ITEMS.md, ROLE_ART_DIRECTOR.md) — this report only indexes them.
- Process suggestions in §9 (count-grep discipline in the batch pattern; `md_graph.py --check`
  with true BFS; canonical content-comment format) are proposals for the next phase brief /
  tooling pass, owner's pick — none is a doc defect today.
