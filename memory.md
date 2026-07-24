# memory.md — State + Decisions Log

Written by the v2-reconciliation producer run (2026-07-24), per CLAUDE.md ("For future
Claude sessions"). Read this after README.md → GLOSSARY.md → WORLD_PLAN.md.

## Current state (2026-07-24)

- **Phases A–C complete; Phase D (content) not started — no content IDs minted.**
- The tree was split-brain after the v2 owner revision (2026-07-21): vision/world/registry
  docs were v2, but `10_systems/`, `15_maps_system/`, `20_schemas/`, and parts of the org
  charter were still v1 (cap 100, gates 8/30/60, Rift/raid content, free waygates).
- Audit: `docs/phase_reports/DESIGN_ORG_REVIEW_2026-07-24.md`. This run executes its §6
  dispatch plan; results in `docs/phase_reports/PHASE_B2_REPORT.md`.
- Branch note: the review's dispatch prompt named `claude/v2-reconciliation-fixes`; the
  work actually landed on `claude/game-design-org-review-dispatch-wq01tp` (the session's
  designated branch).

## Decision Contract (owner-ratified 2026-07-24; overrides any stale doc text)

Recorded verbatim from DESIGN_ORG_REVIEW_2026-07-24.md §6:

> C1. Level cap 300. Arc 1 authors Lv 1–42 only.
> C2. Job gates: 1st Lv 8 · 2nd Lv 40 · 3rd Lv 80. The Lv-80 gate is canonized NOW but
>     3rd-job content (skills 014–021, quests, instructors) stays reserved for future arcs.
> C3. Leveling curve: exp_per_kill_normal(L) = round(4·L^1.3) unchanged;
>     kills_per_level(L) = round(20 + 0.26·L²);
>     exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L).
>     Played-time model (canonical): /played per level = kills_per_level(L) / (480 × 0.70)
>     — hunting occupies ≈70% of playtime at ≈480 at-level kills/h. Anchors to publish:
>     Lv 40 ≈ 18 h · Lv 42 ≈ 21 h · Lv 60 ≈ 58 h · Lv 80 ≈ 134 h (≈1 month @ 4–5 h/day)
>     · Lv 100 ≈ 260 h. Lv 100–300 tail: leave as an explicit Open Question with these
>     anchors fixed (future-arc segment law), do not invent it.
> C4. Counts (canonical): 8 bosses / 16 boss uniques; 150 monsters = 118 normal / 24
>     elite / 8 boss; 200 maps = 6 towns / 20 interiors / 99 fields / 53 dungeons /
>     14 secrets / 8 arenas; skills authored this run = 13 per line + 4 novice = 56
>     (skill_<line>_014–021 reserved). Regions r01–r08 only; frostpeak / arcane_reach /
>     voidshore / rift are reserved future biomes and must not drive any active rule.
> C5. Travel: paid Harthmoor Coachworks (shards) + Harborwind Ferry. waygate /
>     waygate_console are retired tokens — replace with coach / coach_stop per GLOSSARY.
> C6. Bind/bank towns = the 6 v2 towns (Millbrook Central, Cindershelf, Mossmere,
>     Tidewatch Port, + the remaining ring towns per WORLD_PLAN). "Arcane Sanctum" is
>     invalid. Job trainers = each line's home-town instructor (Bulwark→Cindershelf,
>     Keeneye→Tidewatch Port, Weaver→Mossmere, Flicker→Millbrook), 2nd advancement via
>     the same instructor + Clockwork trial per WORLD_PLAN v2.3 — not Millbrook-only.
> C7. Gear band gap: extend weapon/armor tiers with one Lv-40 tier so the Lv 40–42 band
>     is covered (new ID range in a new commit — never renumber existing blocks).
> C8. Party quests: pq_undervault / pq_mainspring rules live in a new
>     docs/10_systems/social/PARTY_QUEST.md (GLOSSARY and SCOPE already point there);
>     PARTY.md drops its Rift-raid section and references it.
> C9. Rift / R12 / raid bosses (mob_147–150 as raid tier) / 150× raid exp / 12-region
>     pools (r09–r12) / Lv-105 monsters: all v1 content — delete or move to explicitly
>     marked "reserved for future arcs" notes. mob_145–150 are Clockwork elites + the
>     Custodian boss per ID_REGISTRY.

### C3′ — pacing amendment (owner directive, 2026-07-24, later same day)

The owner reviewed the C3 anchors mid-run and ruled the pace too fast: **"is too quick to
level 40 I think need 30hours... lvl 100 for now 300hours."** Amended curve (same
exp-per-kill formula, same ÷(480 × 0.70) played-time model):

> kills_per_level(L) = round(20 + 6.6·L + 0.2·L²)

Ratified anchors (supersede C3's): **Lv 40 ≈ 30 h · Lv 100 ≈ 300 h** ("for now").
Derived anchors: Lv 8 ≈ 1 h · Lv 42 ≈ 33.5 h · Lv 60 ≈ 80 h · **Lv 80 ≈ 166 h** — the
3rd-job gate moves from ≈1 month to ≈5–6 weeks at 4–5 h/day; flagged to the owner at
amendment time, not objected to. The Lv 100–300 tail stays an Open Question per C3.

C7 implementation note: the six v2 towns are Emberfoot Village, Rosen Harbor, Millbrook
Central, Mossmere, Tidewatch Port, Cindershelf (WORLD_PLAN v2.3). The Lv-40 gear tier
minted inside existing `item_equip` sub-block slack (28 weapons / 35 armor authored) —
see ID_REGISTRY.md tier-7 note.

## Run outcome (2026-07-24, end of reconciliation run)

All waves complete; QA verdict PASS-WITH-FLAGS and every flag resolved in-run except the
locked-file item (ART_BIBLE reserved-biome annotation — routed to the art director's
amendments channel). Full record: `docs/phase_reports/PHASE_B2_REPORT.md` (§4 has the
open-questions rollup). Travel economy now published in ECONOMY §7 (coach 300/1,000/1,800
by ring hop · ferry 150 · Return Scroll 2,500 as a paid recall).

## Decisions log

- 2026-07-21 (owner) — v2 world revision: cap 300, two islands, 8 regions/bosses, paid
  coach travel, 3rd jobs reserved. Recorded in CLAUDE.md, GLOSSARY, WORLD_PLAN, SCOPE.
- 2026-07-24 (owner, via DESIGN_ORG_REVIEW) — Decision Contract C1–C9 above: 3rd-job gate
  Lv 80; leveling coefficient 0.26; canonical ÷0.70 played-time table model; tier-7 gear;
  PARTY_QUEST.md created; Rift/raid v1 content deleted or explicitly reserved.
- 2026-07-24 (org) — `docs/15_maps_system/` ownership assigned to ROLE_SYSTEMS_ARCHITECT;
  ROLE_MONSTER_DESIGNER added before Phase D; ART_GENERATION_RUNBOOK ownership resolved
  (integration engineer owns, art director holds QA veto).
- 2026-07-24 (owner, mid-run) — **C3′ pacing amendment** (section above): Lv 40 ≈ 30 h,
  Lv 100 ≈ 300 h; curve `20 + 6.6·L + 0.2·L²`; Lv 80 lands ≈ 166 h (supersedes the
  "1 month to 3rd job" target).
- 2026-07-24 (producer) — Millbrook Return Scroll kept as `item_use_0013` but ruled a
  shard-priced vendor consumable (2,500) — no free warps of any kind (C5); coach/ferry
  fares published in ECONOMY §7.
- 2026-07-24 (owner, post-merge) — **Raid convention ruling:** "raid" replaces the
  "party quest"/"PQ" phrasing tree-wide (MapleStory-notation avoidance; the mode itself
  stays MapleStory-inspired). Amends C8's naming only — the world stays v2: two raids
  (`raid_undervault`, `raid_mainspring`) reusing the 8 region bosses; **no separate raid
  monster tier** (C9 unchanged). `social/PARTY_QUEST.md` → `social/RAID.md` (v2-scoped,
  replacing the v3 4-raid doc); `pq_*` retired and added to VALIDATION §1's banned list.
- 2026-07-24 (producer, post-merge sweep) — the merge had silently kept v3 versions of
  files our branch never edited: GLOSSARY.md (v3), CLAUDE.md (v3), WORLD_PLAN.md (v2/v3
  auto-merge chimera), TRADING.md (0201–0222). All restored/rewritten to v2 canon + raid
  convention; README/HUD/PERSISTENCE/MAIL/MARKET/SPRITESHEET_SPEC kept (main's edits were
  benign).

## Open questions rollup (live copies live in each doc's own section)

- Lv 100–300 curve tail segment law — future-arc owner call (C3 fixes anchors ≤100 only).
- 480 kills/h and 70%-hunting constants are unmeasured; Phase D spawn/TTK data re-verifies.
- run_speed 128 px/s (MAP_TRAVERSAL) vs base_move_speed 200 px/s (COMBAT_FORMULA) — see
  the owning docs' Open Questions if not resolved by this run.

## For the next session

Phase D (content generation) is next: region-scoped sub-agents, exemplar-first,
validator-gated, staffed per `docs/60_agents/roles/ORG.md` (including the new
ROLE_MONSTER_DESIGNER). The `tools/` validator still does not exist — VALIDATION.md checks
are manual until it lands.

---

## MERGE NOTE — 2026-07-24: v2 reconciliation merged over the v3 lineage (owner-directed)

The owner directed this reconciliation run's branch to merge into `main`. `main` carried a
parallel **v3 lineage** (owner revision 2026-07-23: 5 islands / 11 regions / 324 maps /
234 monsters / 4 raids / branching 2nd-job specializations / T1–T12 gear / arcs 1–2 to
Lv 82, plus phases D–I including a full `70_integrations/` backend suite, `50_content/`
minted content, and `tools/validate.py`).

**Resolution (this merge):** the v2-reconciled design docs above are canon — they overwrote
the v3 versions of all 45 overlapping design/schema/org files. v3-only material was NOT
deleted: `50_content/` (v3 content), `70_integrations/`, `social/RAID.md`, MONETIZATION /
SCROLLS / COLLECTIONS / AUDIO_DESIGN / WORLD_LORE / ONBOARDING_FTUE / WRITING_STYLE, arc-2
phase reports, and `tools/` all remain in-tree but are **non-canonical where they contradict
the v2 world** (raids, regions r09–r11, maps 201–324, mobs 151–234, T8–T12, branching
specs). ID_REGISTRY carries the authoritative repeal note; VALIDATION flags that
`tools/validate.py` must be re-aimed before gating. Orthogonal v3 additions were kept as
canon: PILLARS MON-001 (no pay-to-win + MONETIZATION.md), the packet-opcode registry block,
the `item_use_0061`–`0100` scroll block, VALIDATION's warn-only gradient check.

**Owner follow-up needed:** prune or re-ratify the v3-only material (especially
`50_content/` and `social/RAID.md` vs `social/PARTY_QUEST.md`) — everything is preserved in
git history either way.

---

# ARCHIVED — pre-merge main-lineage log (v3 generation, superseded as design canon)

## 2026-07-24 — markdown connectivity graph + BFS audit (session: markdown-connectivity-graph)

New tool `tools/md_graph.py` (stdlib) builds the whole-tree link graph — edges from markdown
links *and* inline `path/FILE.md` mentions (how this tree actually cross-links) — and BFS-checks
it. Report: `docs/phase_reports/MD_CONNECTIVITY_REPORT.md`. **Undirected graph was already one
connected component, 0 orphans** (98 files after adding the report; ~1,208 edges). The real gap
was **directed reachability**: 10 files linked out but nothing linked *to* them, so a reader
following links from `README`/`CLAUDE`/`memory` could never reach them — the 5 role charters
`ROLE_PRODUCER/WORLD_BUILDER/CONTENT_AUTHOR/GAMEPLAY_DEVELOPER/ART_QUARTERMASTER`, the F/G/H phase
reports (merged in from parallel sessions, never indexed), `50_content/README.md`, and
`tools/README.md`. Closed by adding a "Role files (index)" to `ORG.md` and enumerating the
phase-reports / tools / content-README paths in `README.md` — no content restated (law §2). After:
**1 component, 0 orphans, 98/98 directed-reachable.** Also refreshed `CLAUDE.md` with a phase-status
line and a re-run-`md_graph.py`-after-merges note. **Phase check (owner asked "need re-run?"):**
A/B/C/D + F/G/H/I are all complete and reconciled to v3.1 (SYNC_AUDIT 0/0) — nothing to re-run;
only forward work remains — Phase E (coding-pass briefs), the art pass, and the balance pass.

## 2026-07-23 — full-tree markdown sync vs v3.1 (session: markdown-sync-check)

Audited every markdown doc against v3.1 canon and fixed the stragglers the merge waves
missed — report: `docs/phase_reports/SYNC_AUDIT_v3_2026-07-23.md`. Headlines: DEATH_PENALTY
rebuilt from its untouched v1 state (brackets, canon bind towns incl. the three arc-2
ports, raid deaths via social/RAID.md); STATUS_EFFECTS/AI_BEHAVIOR off the deleted
PARTY_QUEST.md; job.schema rebuilt to the branching 15-job model and the other schemas
re-counted to v3 (324/234/120/120, pools r01–r11, T1–T12, no Rift-raid quartet);
COLLECTIONS/AUDIO_DESIGN/WORLD_LORE/MAP_LAYERS/WIKI_EXPORT/ART_GENERATION_RUNBOOK extended
to the 11-region world; ENHANCEMENT/ECONOMY re-banded to the T1–T12 ladder + seven-tonic
table; VALIDATION §5 gained the WORLD_PLAN-promised monotonic-gradient warn; PILLARS P3 and
SCOPE counts to five islands/234; GLOSSARY gained a Deepway entry. `tools/validate.py`
strict: 0/0 before and after. Known debts left by design (shields/overalls/scrolls +
COLLECTIONS/AUDIO/FTUE deep hooks; WORLD_CHANNELS capacity targets; validate.py item_use
ceiling — flagged in VALIDATION OQs). New OQs: arc-2 WORLD_LORE expansion; Emberstone
VI for T11–T12; ECONOMY §5 tonic-bite retune past Superior.

## 2026-07-23 — Phase I: backend-design suite (session: backend-kickoff-prompt) + v3 merge

**I (backend-design suite) ✅** — see `docs/phase_reports/PHASE_I_BACKEND_REPORT.md`. Executed
`docs/60_agents/BACKEND_KICKOFF_PROMPT.md`: the full `70_integrations/` authoritative-server
suite authored and gated (14 architect/QA passes) — BACKEND_ARCHITECTURE + ACCOUNTS_AUTH
(revised), WORLD_CHANNELS, DATABASE_PERSISTENCE, NETWORK_PROTOCOL, GAMEPLAY_SIMULATION,
CHAT_SOCIAL_BACKEND (new). ID_REGISTRY gained the engineering-side packet-opcode block
(`op_0001`–`op_9999`, 13 domain ranges; 103 opcodes minted in NETWORK_PROTOCOL §9).

**Decisions (owner-delegated to the session by the kickoff — decided, not open):** server stack =
engine-independent Elixir/OTP + Phoenix (headless Godot, Go rejected); storage = one PostgreSQL
database with `char`/`wallet`/`social` schemas + least-privilege roles (separate databases
rejected — value transfers must commit without 2PC), append-only off-Postgres RNG audit log,
Redis/ETS never truth; tick model = 20 Hz sim / 10 Hz snapshot, per-map parked loops, queued
deterministic combat drain, timestamp timers, 20 Hz accept-if-plausible reconciliation (resolves
PERSISTENCE §4's deferred flag by delegation); wire = WSS + MessagePack, positional envelope,
protocol_version handshake, 15 s heartbeat inside ACCOUNTS_AUTH's 90 s reconnect grace; auth =
Argon2id, opaque 60-min tokens + 30-day rotating refresh, fail-closed re-derive+range-check
import (answers PERSISTENCE §9); channels = demand-driven, cap 5/map, 150/60 occupancy caps,
2,000/node; boss arenas are shared reset-when-empty maps — only raid gates allocate per-party
instances; `intent` is a NETWORK_PROTOCOL wire-role annotation, deliberately NOT a fourth
PERSISTENCE tag. Open-questions rollup: PHASE_I_BACKEND_REPORT.md §4.

**v3 merge at landing:** the suite was authored against the v2 world and merged into the v3.1
line at PR time. Same policy as the prior reconciliation: v3 wins world facts; the suite is
net-new and kept, **retargeted** — `pq_*` → `raid_*` (stage/finale map IDs unchanged for arc 1),
`PARTY_QUEST.md` → `social/RAID.md` (party-size floor now RAID §2/§3), world-shape claims updated
to five islands / 324 maps / four raids (the two arc-2 raids ride the same instance-worker and
opcode machinery; no new opcodes needed). Residue: the suite's capacity targets (§ WORLD_CHANNELS
§7) were sized against the v2 two-island world — still valid as launch targets since world nodes
scale horizontally, but re-check at the balance pass; ACCOUNTS_AUTH's import bounds now cite the
authored-arc cap via SCOPE/WORLD_PLAN rather than a hardcoded level.

## 2026-07-23 — main merge reconciliation (after Phase D completion)

Merged `origin/main` (phases F/G/H from parallel sessions: 70_integrations backend/
accounts/telemetry docs, AUDIO_DESIGN/COLLECTIONS/ONBOARDING_FTUE/WORLD_LORE/
WRITING_STYLE/SCROLLS/SKILL_ANIMATION, ROLE_ART_QUARTERMASTER, phase reports F/G/H) into
the v3 line. Policy: **v3 wins co-modified design files** (it is the owner's latest
directive, backed by the minted 50_content tree); main's net-new docs all kept. Semantic
fixes at the merge: PARTY_QUEST.md deleted (superseded by social/RAID.md), pq_*/party-
quest/waygate refs in the incoming docs retargeted to raid_*/coach; equipment-v2's
shield/overall ID blocks **re-homed** from 0231–0250 (collides with minted arc-2 equips)
to the never-minted 0181–0200 reserve; scroll block item_use_0061–0100 ported; new
provisional tokens (title, shield, overall, req_line, scroll vocabulary) carried in
GLOSSARY. **Open debt:** integrating shields/overalls/scrolls + COLLECTIONS/AUDIO/FTUE
hooks with the v3 systems docs and content (they were written against the v2 world) —
see ID_REGISTRY Open Questions; main's variant of tools/validate.py was dropped in favor
of the v3-aware one (diff it from git history if its extra checks are wanted).

## 2026-07-23 — v3 owner revision + Arc-2 Phase D (session: maps-levels-40-80)

**State now:** design tree is at **v3.1** (five islands, two authored arcs Lv 1–82, cap
300, backtracking law + reserved cross-arc boss-connectivity hook). **Phase D is COMPLETE
for the whole world:** `docs/50_content/` holds every content file — 324 maps, 234
monsters, 234 drop tables + 11 pools, 120 NPCs, 120 quests, 98 skills, all item tables
(T1–T12, uniques 0201–0222, consumables 0001–0020, Emberstone I–V) — and the **strict**
`tools/validate.py` run (no allow-missing, entry map_001, global reachability) passes
with 0 failures, 0 warnings. Remaining known reconciliations: raid_undervault band 15–22
vs Millbrook ceiling 14; `spec_trial_gate` zone token; the Open Questions rollups in the
phase reports. Next phases: art pass (PixelLab briefs), Phase E coding-pass briefs
review, arc-1/arc-2 balance pass.

**v3 decisions (owner + producer):**
- Arc 2 = Frostpeak Isle (40–55) / Arcane Reach (53–68) / Voidshore (66–80); `rift`
  still reserved. Access: the Deepway (Cindershelf `map_125` → `map_201`–`203`,
  `level_gate: 40`) + the paid scheduled `longship` network from Tidewatch Port.
- 2nd job (Lv 40) **branches**: bulwark Ironbrand/Stoneguard/Warcaller · keeneye
  Pathstalker/Sureshot · weaver Runeweaver/Cindercall/Frostbind · flicker
  Duskstep/Wildcard. Skill re-block `skill_<line>_001`–`060` (specs at 007/014/021).
- "Raid" replaced "party quest" everywhere: `raid_undervault`/`raid_mainspring`/
  `raid_deepfrost`(45–55)/`raid_voidtide`(70–80); owner `10_systems/social/RAID.md`;
  party 3–6; solo open-arena fallback kept.
- Items: 12-tier equip ladder (T7–T12 = Lv 43–78, `item_equip_0231`–`0300`), uniques
  0201–0222 (11 bosses), Sovereign/Mythic tonics (`item_use_0017`–`0020`).
- LEVELING: Lv 1–80 rows frozen; provisional linear softcap continuation past 80;
  arc-2 ≈ 90 played hours. Debt cleaned: v1 Rift-raid model (PARTY/SPAWN/DROPS/
  COMBAT_FORMULA/QUESTS) and the retired `waygate` (now `coach`/`longship` everywhere;
  new tokens `coach_station`, `coach_clerk`, `pier_officer` in GLOSSARY Provisional).

**Batch pattern that worked (reuse for arc-1):** producer fixes ID/token decisions →
exemplar-first (one real file per schema, conventions in `50_content/README.md`) →
per-region parallel agents (maps+npcs+quests / mobs+drops+materials) + horizontal
item/skill batches → each batch runs `python3 tools/validate.py --allow-missing` and
fixes its own failures → producer commits per batch, one concern each → final full-tree
gate expecting only cross-arc boundary warnings. Route bosses/formulas to Opus-tier,
map/quest/NPC batches to Sonnet-tier, per `docs/60_agents/roles/ORG.md`.

**Known dangling (closed by the arc-1 batch):** `map_071`/`map_125` reciprocal portals,
`item_use_0011`, `item_etc_0193`–`0197` (enhancement.yaml), arc-1 equip rows 0001–0216,
pools r01–r08, novice/first-job/spec-#1-era skills 001–006. Open Questions live in the
owning docs; rollups in `docs/phase_reports/ARC2_PLAN_REPORT.md` and
`PHASE_D_ARC2_REPORT.md`.
