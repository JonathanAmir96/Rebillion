# DESIGN_ORG_REVIEW — 2026-07-24 (owner-requested design + org audit)

Reviewer: Claude Code session on `claude/game-design-org-review-oqto97`. Read-only audit —
no design files were changed. Companion to `PHASE_A_REPORT.md` / `PHASE_B_REPORT.md`.

Owner's pacing target under review: **3rd job advancement at Lv 80, reached after ≈ 1 month
of 4–5 h/day play (≈ 120–150 played hours).**

---

## 1. Verdict (TLDR)

1. **The tree is split-brain.** GLOSSARY, SCOPE, WORLD_PLAN, ID_REGISTRY, VALIDATION and
   README are v2 (cap 300, 8 regions, 8 bosses, paid coach travel, 3rd job reserved).
   Roughly **20 systems/maps docs and all 5 entity schemas are still v1** (cap 100, job
   gates 8/30/60, authored 3rd-job skills, Rift/R12 raid bosses `mob_147`–`150`, free
   waygate network, 4 bind towns incl. the invalid "Arcane Sanctum", 12-region pools).
   If Phase D ran today it would generate deferred 3rd-tier skills, mis-gate 2nd jobs at
   Lv 30, and mint Rift content that no longer exists.
2. **The pacing target is not met and is not even defined.** No doc puts 3rd job at Lv 80
   (JOBS.md v1 says Lv 60; CLAUDE.md v2 reserves it with no level). The LEVELING curve is
   the v1 cap-100 curve **and is internally contradictory**: its prose formula gives
   ≈ 51 h to Lv 80, its published table gives ≈ 104 h (see §2). Either way it undershoots
   the ≈ 135 h target.
3. **The fix is small and closed-form:** canonize gates 8/40/**80** and change one
   coefficient — `kills_per_level(L) = round(20 + 0.26·L²)` — which puts **Lv 80 at
   ≈ 134 h**, almost exactly 30 days × 4.5 h (§2.3).
4. **The org is dispatch-ready with four patches:** `15_maps_system/` has no owning role;
   elite/boss monster content has no owner ("mob lead" is referenced but no such role
   exists); `ART_GENERATION_RUNBOOK.md` is claimed by two roles; VALIDATION §5 would
   falsely fail legitimate v2 map edges (§4).
5. §6 is a **copy-paste dispatch prompt** for a fresh session: one serial producer wave,
   then four parallel Opus lanes with disjoint file ownership, then a schema + QA wave.

---

## 2. Pacing audit — "Lv 80 (3rd job) in ~1 month at 4–5 h/day"

### 2.1 The gate itself is undefined

| Source | 1st | 2nd | 3rd | Cap |
|---|---|---|---|---|
| JOBS.md / SKILL_SYSTEM.md / DEATH_PENALTY.md (v1) | 8 | **30** | **60 (authored)** | 100 |
| CLAUDE.md / GLOSSARY / WORLD_PLAN (v2) | 8 | **40** | reserved, no level | 300 |
| **Owner target (this review)** | 8 | 40 | **80 (gate canonized; content stays future-arc)** | 300 |

Setting the 3rd gate at Lv 80 is compatible with v2: arc 1 ends at Lv 42, so the 3rd-job
*content* stays reserved — only the number is canonized now so the curve, death-penalty
bands, skill-point budget, and future arc planning can anchor to it.

### 2.2 LEVELING.md has an internal ×2 contradiction

- **Prose model** (§1: "pure-hunting kills = 0.70 · kills_per_level" at 480 kills/h):
  time-to-Lv 80 ≈ **51 h**, cap-100 total ≈ **99 h**.
- **Table model** (the published `/played` column = `kills_per_level / (480 × 0.70)`,
  i.e. hunting occupies ~70% of playtime): time-to-Lv 80 ≈ **104 h**, total ≈ **201 h** —
  this is what reproduces the doc's own "≈ 201 h to cap" claim.

The two readings differ by a factor of 2 (0.70² ). The table model is the one the doc's
headline number is built on → **canonize the table model** and rewrite the prose sentence.

### 2.3 Retune: one coefficient hits the target

Keeping `exp_per_kill_normal(L) = round(4·L^1.3)` and the coupling contract, and using the
table model, cumulative played hours to reach each level:

| `kills_per_level` | Lv 8 | Lv 40 | Lv 42 (arc 1 end) | Lv 60 | **Lv 80** | Lv 100 |
|---|---|---|---|---|---|---|
| `20 + 0.20·L²` (current) | 0.5 h | 14.5 h | 16.6 h | 45 h | **104 h** | 201 h |
| **`20 + 0.26·L²` (proposed)** | 0.5 h | 18.2 h | 20.9 h | 58 h | **134 h** | 260 h |

**134 h ≈ 30 days × 4.5 h/day — on target.** Side effects to accept: arc 1 (Lv 1–42)
becomes ≈ 21 h (≈ 4–5 sessions-days), Lv 100 ≈ 260 h. The Lv 100–300 tail needs its own
segment law (a steeper piecewise segment or exponent change) — that is a future-arc
decision; only the anchors above must be fixed this run because every economy/quest/TTK
table cites the curve.

Caveats that stay flagged (already in LEVELING Open Questions): the 480 kills/h and 70%
figures are unmeasured assumptions; Phase D spawn density can shift `/played` without
touching the curve.

### 2.4 Knock-on gap

ID_REGISTRY weapon/armor tiers stop at **Lv 36** while the arc runs to Lv 42 (Clockwork
boss Lv 40, elites Lv 42) — no gear band covers 40–42. Needs one more tier or an explicit
"boss-unique-only band" ruling.

---

## 3. What to fix — design docs (prioritized)

**P0 — owner decisions (block everything else):**
- D1. Canonize progression contract: cap 300; arc 1 = Lv 1–42; gates 8 / 40 / **80**
  (3rd content future-arc).
- D2. Canonize pacing anchors + `c = 0.26` + the ÷0.70 table model (§2.2–2.3).
- D3. Canonize counts: 8 bosses / 16 uniques; 150 monsters = 118/24/8; 200 maps =
  6 towns / 20 interiors / 99 fields / 53 dungeons / 14 secrets / 8 arenas (SCOPE +
  WORLD_PLAN numbers; MAPS_SYSTEM's six numbers are all wrong); skills authored =
  13/line + 4 novice = 56 (`014`–`021` reserved).
- D4. Gear band for Lv 40–42 (§2.4).
- D5. Owner for the two party quests: create `social/PARTY_QUEST.md` (GLOSSARY + SCOPE
  already point at it) or repoint them to PARTY.md.

**P1 — systems re-tune (single writer; the balance surface is one interdependent web):**
- LEVELING.md ★: cap-300 header, retabled curve (c = 0.26), fix prose/table model
  contradiction, delete §6 Rift/post-cap-100 policy (re-resolve SCOPE's OQ for arc-1
  scope), delete raid-boss 150× row.
- JOBS.md ★: gates 8/40 (+"3rd at Lv 80, future arc"); move `skill_*_014`–`021` rows to a
  clearly-marked reserved appendix (ID_REGISTRY says only `001`–`013` are authored);
  replace Millbrook-only trainer table with the four home-town instructors
  (Cindershelf / Tidewatch Port / Mossmere / Millbrook, per WORLD_PLAN v2.3).
- SKILL_SYSTEM.md: skill-point totals re-derived for cap/arc; tier gates 8/40/(80);
  drop 3rd-tier cost band from in-scope text.
- STATS.md: growth table bands to the new cap model; §4.3/§4.4 retable.
- COMBAT_FORMULA.md ★: §13 budget table re-scoped to Lv 1–42 (+ reference rows beyond);
  delete §13.3 raid scaling (`mob_147`–`150` are Clockwork elites/boss in v2); §14 TTK
  and §15 `power_ref` re-derived against the new curve.
- QUESTS.md: §4 retable from new curve; delete Rift-band (`quest_085`–`090` are
  Clockwork/PQ quests and must pay exp); §5 shards retable.
- ECONOMY.md: fees/tonics/potion-bite retabled to the new curve and arc bands; rename
  "Millbrook Return Scroll" concept to fit paid-coach travel or delete.
- DROPS.md: pools `r01`–`r08` only; shard-faucet table re-scoped; delete raid/Rift
  token blocks (`0177`–`0192` block gets re-purposed or reserved).
- DEATH_PENALTY.md ★: exp-loss bands re-cut to 8–39 / 40–79 / 80+ (per D1); bind towns →
  the 6 v2 towns (drop "Arcane Sanctum", fix map IDs); delete §5.3 Rift raids; waygate
  language → coach; fix `10_systems/PARTY.md` → `social/PARTY.md` path (also in SPAWN,
  AI_BEHAVIOR).
- ENHANCEMENT.md / ITEMS.md ★: tier grid re-mapped to real v2 regions (no Frostpeak/
  Arcane Reach/Voidshore/Rift rows in-scope); **15 bosses/30 uniques → 8/16**; add the
  D4 gear band; affix/W tables re-anchored.
- INVENTORY.md: §7 bank towns → same 6-town list as DEATH_PENALTY.
- SPAWN.md: delete §7 Rift arenas + raid respawn row.
- STATUS_EFFECTS / AI_BEHAVIOR / ELEMENTS / SKILL_EFFECTS: scrub raid/Rift nouns
  (CC-immunity rules re-homed to the 8 region bosses / PQ finale bosses).
- PILLARS.md: P3 "warp home" → paid-coach loop phrasing.

**P2 — schemas (after P1 lands):**
- job.schema.md ★★ (worst file): gates enum `{1,8,40}` + reserved-80 note; trainer-town
  enum → the four home towns; drop Lv-100 growth rows; stop emitting third-tier JobData.
- skill.schema.md: 13 authored per line; `014`–`021` reserved (52 + 4 files, not 84 + 4).
- monster.schema.md: split 118/24/8; level range 1–42; delete "raid bosses `mob_147`–`150`"
  validation rule (it would mis-scale real v2 elites).
- quest.schema.md: 8 region ranges; Emberfoot `001`–`010` (not `001`–`008`); delete
  Rift no-exp rule; level ints re-capped.
- map.schema.md: 8 region/biome enums; `party_min` re-pointed from "Rift arenas
  `197`–`200`" to the real PQ finales `map_042`/`map_200`; drop Frostpeak chute rule.

**P3 — maps-system docs (parallel-safe with P1, disjoint files):**
- MAP_CONNECTIONS.md ★: replace the free waygate network with Harthmoor Coachworks rules
  (paid, shards, coach stops; Harborwind Ferry unchanged); resolve §7 terminus edges vs
  WORLD_PLAN edge table (feed VALIDATION §5 fix); drop `from_frostpeak`.
- MAP_INTERACTABLES.md: `waygate`/`waygate_console` → `coach_stop` (GLOSSARY already
  defines the tokens).
- MAPS_SYSTEM.md: §2 counts → D3 numbers; "4 towns" → 6; delete §8 Rift arenas; spawn
  vocabulary `waygate` → coach.
- MAP_LAYERS.md: 12-biome tileset table → 8 (reserved biomes moved to a future-arcs note).
- MAP_TRAVERSAL.md: "R5" → `sunken` (r07); reconcile `run_speed` 128 px/s vs
  COMBAT_FORMULA `base_move_speed` 200 px/s (flag, don't guess, if unresolvable).
- GUILD.md: founder gate "Lv 30 = 2nd job" → Lv 40; "Millbrook Township (R3)" region ref.
- PARTY.md: delete §6 Rift raids; PQ party rules per D5.

**P4 — bookkeeping:** phase-report v2 addendum; write `memory.md`; decide fates of
referenced-but-missing `SKILL_ANIMATION.md`, `WRITING_STYLE.md`, `tools/` validator.

---

## 4. What to fix — org charter (`docs/60_agents/roles/`)

1. **Ownership hole:** `docs/15_maps_system/*` is owned by no role (architect stops at
   `10_systems` + `20_schemas`; world-builder owns only future `50_content/maps`). Assign
   to ROLE_SYSTEMS_ARCHITECT (or a new systems-scoped map role).
2. **Missing role:** elite/boss monster stat-blocks + kits and `50_content/monsters|skills`
   have no producer; WORLD_BUILDER/NARRATIVE reading lists cite a "mob lead" that doesn't
   exist. Add **ROLE_MONSTER_DESIGNER** (Opus for bosses, Sonnet elites, manifests down to
   Haiku) before Phase D.
3. **Ownership collisions:** `ART_GENERATION_RUNBOOK.md` is claimed by both
   ROLE_ART_DIRECTOR and ROLE_INTEGRATION_ENGINEER (and its path is ambiguous:
   `40_assets/` vs `70_integrations/`) — pick one. `VALIDATION.md` is producer-owned but
   the architect's Definition-of-Done edits it — route VALIDATION edits through one of them.
4. **Stale references:** ART_DIRECTOR cites nonexistent `SPRITE_PIPELINE.md` (real file:
   `SPRITESHEET_SPEC.md`); GAMEPLAY_DEVELOPER cites a nonexistent phase-briefs dir;
   `social/` docs are "handled with the producer" but appear on neither owned list.
5. **Validation runnability:** no `tools/` validator exists (checks are manual); VALIDATION
   §5 ("edges must match WORLD_PLAN exactly") **falsely fails** MAP_CONNECTIONS §7's
   legitimate terminus edges — reword after P3 settles the edge table. Checks 2/5/6 can't
   run until `50_content/` exists.
6. **Routing table itself is sound** (matches CLAUDE.md; escalation/demotion rules
   coherent). The critical dispatch law it implies: **the P1 balance surface is one
   logical writer** — never split "fix leveling" and "fix economy" into parallel agents;
   they share one interdependent budget web.

---

## 5. Parallelization map (who can run concurrently)

```
Wave 0 (serial, producer):   D1–D5 decisions → SCOPE/CLAUDE/PILLARS/WORLD_PLAN touch-ups
Wave 1 (parallel, 4 lanes, disjoint files):
  Lane A  ROLE_SYSTEMS_ARCHITECT   docs/10_systems/*.md  (P1; ONE agent)
  Lane B  maps-system              docs/15_maps_system/*.md  (P3)
  Lane C  social                   docs/10_systems/social/PARTY.md, GUILD.md (+PARTY_QUEST.md)
  Lane D  org + validation         docs/60_agents/roles/*, docs/VALIDATION.md §5 (P4/org)
Wave 2 (parallel, after Lane A lands):
  Lane E  schemas                  docs/20_schemas/*.md  (P2)
  Lane F  QA sweep                 read-only v1-token grep + cross-doc number check
Wave 3 (serial, producer):   phase-report addendum, memory.md, commit per concern, push
```

---

## 6. APPENDIX — copy-paste dispatch prompt for a new session

Everything between the fences is self-contained; paste it as the first message of a fresh
session on this repo. Edit the Decision Contract first if any ruling differs.

````text
You are acting as ROLE_PRODUCER per docs/60_agents/roles/ROLE_PRODUCER.md for a
"v2 reconciliation + pacing retune" fix run on this repo. Read CLAUDE.md, README.md,
docs/phase_reports/DESIGN_ORG_REVIEW_2026-07-24.md (the audit driving this run),
docs/00_vision/GLOSSARY.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md first.

Work on branch claude/v2-reconciliation-fixes (create from the current default/content
branch). One concern per commit. Push with git push -u origin <branch>.

════════ DECISION CONTRACT (owner-ratified; overrides any stale doc text) ════════
C1. Level cap 300. Arc 1 authors Lv 1–42 only.
C2. Job gates: 1st Lv 8 · 2nd Lv 40 · 3rd Lv 80. The Lv-80 gate is canonized NOW but
    3rd-job content (skills 014–021, quests, instructors) stays reserved for future arcs.
C3. Leveling curve: exp_per_kill_normal(L) = round(4·L^1.3) unchanged;
    kills_per_level(L) = round(20 + 0.26·L²);
    exp_to_next(L) = exp_per_kill_normal(L) × kills_per_level(L).
    Played-time model (canonical): /played per level = kills_per_level(L) / (480 × 0.70)
    — hunting occupies ≈70% of playtime at ≈480 at-level kills/h. Anchors to publish:
    Lv 40 ≈ 18 h · Lv 42 ≈ 21 h · Lv 60 ≈ 58 h · Lv 80 ≈ 134 h (≈1 month @ 4–5 h/day)
    · Lv 100 ≈ 260 h. Lv 100–300 tail: leave as an explicit Open Question with these
    anchors fixed (future-arc segment law), do not invent it.
C4. Counts (canonical): 8 bosses / 16 boss uniques; 150 monsters = 118 normal / 24
    elite / 8 boss; 200 maps = 6 towns / 20 interiors / 99 fields / 53 dungeons /
    14 secrets / 8 arenas; skills authored this run = 13 per line + 4 novice = 56
    (skill_<line>_014–021 reserved). Regions r01–r08 only; frostpeak / arcane_reach /
    voidshore / rift are reserved future biomes and must not drive any active rule.
C5. Travel: paid Harthmoor Coachworks (shards) + Harborwind Ferry. waygate /
    waygate_console are retired tokens — replace with coach / coach_stop per GLOSSARY.
C6. Bind/bank towns = the 6 v2 towns (Millbrook Central, Cindershelf, Mossmere,
    Tidewatch Port, + the remaining ring towns per WORLD_PLAN). "Arcane Sanctum" is
    invalid. Job trainers = each line's home-town instructor (Bulwark→Cindershelf,
    Keeneye→Tidewatch Port, Weaver→Mossmere, Flicker→Millbrook), 2nd advancement via
    the same instructor + Clockwork trial per WORLD_PLAN v2.3 — not Millbrook-only.
C7. Gear band gap: extend weapon/armor tiers with one Lv-40 tier so the Lv 40–42 band
    is covered (new ID range in a new commit — never renumber existing blocks).
C8. Party quests: pq_undervault / pq_mainspring rules live in a new
    docs/10_systems/social/PARTY_QUEST.md (GLOSSARY and SCOPE already point there);
    PARTY.md drops its Rift-raid section and references it.
C9. Rift / R12 / raid bosses (mob_147–150 as raid tier) / 150× raid exp / 12-region
    pools (r09–r12) / Lv-105 monsters: all v1 content — delete or move to explicitly
    marked "reserved for future arcs" notes. mob_145–150 are Clockwork elites + the
    Custodian boss per ID_REGISTRY.
Repo laws still apply: GLOSSARY tokens only; reference-never-restate; IDs immutable;
flag-don't-guess (## Open Questions); locked files (ART_BIBLE.yaml, UI_ART_SPEC.md,
ENGINEERING_STANDARDS.md) untouched; US spelling; VALIDATION.md checks before landing.

════════ EXECUTION PLAN ════════
WAVE 0 — do yourself (serial, small):
  0a. docs/00_vision/SCOPE.md: confirm/align cap-300 + arc language, 56-skill and
      map/monster count rows with C3–C4 anchors; resolve its post-cap OQ pointer.
  0b. docs/00_vision/PILLARS.md P3: "warp home" → paid-coach loop phrasing (one line).
  0c. Record the Decision Contract verbatim in memory.md (create it; state + decisions
      log per CLAUDE.md).
  Commit wave 0 before dispatching agents.

WAVE 1 — dispatch these FOUR subagents IN PARALLEL (all Opus; owned files are
disjoint — each agent edits ONLY its listed files and files an Open Question rather
than touching anything else. Each ends its report with: files written, numbers
changed, open questions):

  ── Agent A (Opus) — "Act as ROLE_SYSTEMS_ARCHITECT per
     docs/60_agents/roles/ROLE_SYSTEMS_ARCHITECT.md."
     Owns this wave: docs/10_systems/*.md EXCEPT the social/ subfolder.
     Task: retune the balance surface to the Decision Contract, in this order:
     (1) LEVELING.md — cap-300 header (arc 1–42), retable §1 with C3 (recompute all
         rows + band table), rewrite the prose/table 70% contradiction using the C3
         canonical model, delete §6 gear-only-at-100/Rift policy and re-resolve the
         post-cap OQ as "arc-1 scope; Lv 100–300 segment law = Open Question with C3
         anchors", delete the raid-boss 150× row.
     (2) JOBS.md — gates 8/40 with "3rd job Lv 80, reserved future arc"; move
         skill_*_014–021 tables to a marked RESERVED appendix; four home-town trainer
         table per C6; fix §7 budget check to 13/line = 52+4.
     (3) SKILL_SYSTEM.md + STATS.md — re-derive skill-point totals, tier gates, growth
         bands and sample tables for C1/C2 (arc tables to 42; reference anchors beyond).
     (4) COMBAT_FORMULA.md — §13 budget table re-scoped 1–42 (+reference rows), delete
         §13.3 raid scaling, re-derive §14 TTK + §15 power_ref against the C3 curve.
     (5) QUESTS.md, ECONOMY.md, DROPS.md, DEATH_PENALTY.md, ENHANCEMENT.md, ITEMS.md,
         INVENTORY.md, SPAWN.md — propagate: quest-exp 25% retables; fee/tonic/potion
         retables; pools r01–r08; shard faucet re-scope; death bands 8–39/40–79/80+;
         6 bind towns (C6); 8 bosses/16 uniques (ITEMS §11); C7 gear tier; delete all
         Rift/raid sections (C9); fix 10_systems/PARTY.md path refs → social/PARTY.md.
     (6) STATUS_EFFECTS.md, AI_BEHAVIOR.md, ELEMENTS.md, SKILL_EFFECTS.md — scrub
         raid/Rift nouns; re-home boss CC-immunity rules to the 8 region bosses.
     Consistency law: every number must trace to C3/C4 or an existing owner doc; list
     every consumer doc you touched per change.

  ── Agent B (Opus) — maps-system reconciliation (assign ownership of
     docs/15_maps_system/ to ROLE_SYSTEMS_ARCHITECT scope for this run).
     Owns: docs/15_maps_system/*.md only.
     Task: (1) MAP_CONNECTIONS.md — replace the waygate network with Harthmoor
     Coachworks rules per C5 (paid shards fares, coach stops in the 6 towns, Millbrook
     hub pricing model — pull fare law from ECONOMY if present, else flag); keep
     Harborwind Ferry; reconcile §7 terminus edges against WORLD_PLAN's edge table and
     output the exact §5-rule rewording VALIDATION needs (hand to Agent D via report).
     (2) MAP_INTERACTABLES.md — waygate/waygate_console → coach_stop. (3) MAPS_SYSTEM.md
     — §2 counts per C4, 6 towns, delete Rift arenas §8, spawn-point vocabulary.
     (4) MAP_LAYERS.md — 8 tilesets, reserved-biome note. (5) MAP_TRAVERSAL.md — region
     slug fixes; reconcile run_speed 128 px/s vs COMBAT_FORMULA base_move_speed
     200 px/s: if not decidable from ART_BIBLE AB-001 foothold amendment, file an Open
     Question — do not guess.

  ── Agent C (Opus) — social systems.
     Owns: docs/10_systems/social/*.md (+ creates social/PARTY_QUEST.md).
     Task: (1) create PARTY_QUEST.md per C8 — party-size gates, entry, reward split for
     pq_undervault (finale map_042) and pq_mainspring (finale map_200), citing PARTY.md
     share rules and the existing bosses (no new boss slots). (2) PARTY.md — delete §6
     Rift raids, reference PARTY_QUEST.md. (3) GUILD.md — founder gate Lv 40 (= 2nd
     advancement per C2), fix region refs. (4) sweep CHAT/MAIL/MARKET/TRADING for v1
     residue (expected minimal).

  ── Agent D (Opus) — org charter + validation.
     Owns: docs/60_agents/roles/*.md, docs/VALIDATION.md.
     Task: (1) ORG.md + ROLE_SYSTEMS_ARCHITECT.md — extend architect ownership to
     docs/15_maps_system/; crisply assign social/ (architect with producer sign-off).
     (2) add ROLE_MONSTER_DESIGNER.md (mission: elite/boss stat-blocks + kits +
     mob manifests for content authors; Opus bosses / Sonnet elites / manifests down to
     Haiku; owned: future 50_content/monsters, 50_content/skills values) and add it to
     the ORG chart. (3) resolve ART_GENERATION_RUNBOOK.md ownership (recommend:
     INTEGRATION_ENGINEER owns the file in 70_integrations/, ART_DIRECTOR holds QA veto
     — record in both role files). (4) fix stale refs: SPRITE_PIPELINE.md →
     SPRITESHEET_SPEC.md; note phase-briefs dir as future. (5) VALIDATION.md — reword
     §5 per Agent B's edge-table output (apply after B reports; if sequencing is
     awkward, land the §5 rewording as the final Wave-2 commit); confirm §1 banned-token
     list needs no change.

WAVE 2 — after Agent A lands, dispatch IN PARALLEL:

  ── Agent E (Opus) — schemas to v2.
     Owns: docs/20_schemas/*.md.
     Task: job.schema (gates {1,8,40}+reserved-80 note; four trainer towns enum; drop
     Lv-100 rows; emit 9 JobData not 13 — no third tier); skill.schema (13 authored/line,
     52+4 files, 014–021 reserved); monster.schema (118/24/8; level 1–42; delete
     raid-boss mob_147–150 rule); quest.schema (8 region ranges; Emberfoot 001–010;
     delete Rift no-exp rule; level bounds per arc); map.schema (8 region/biome enums;
     party_min → PQ finales map_042/map_200; drop Frostpeak-chute rule). Every enum and
     constant must cite its owner doc as revised by Wave 1.

  ── Agent F (Sonnet) — QA sweep (read-only, ROLE_QA_VALIDATOR).
     Task: grep the whole tree for v1 residue and report file:line lists — patterns:
     "Rift", "R12", "raid", "waygate", "Lv 60"/"level 60" job contexts, "Lv 30" 2nd-job
     contexts, "cap 100"/"Lv 100"/"105", "Arcane Sanctum", "Frostpeak", "r09"–"r12",
     "15 boss", "84 line skills", "201 h". Cross-check that SCOPE / WORLD_PLAN /
     ID_REGISTRY / LEVELING / JOBS / MAPS_SYSTEM now agree on every C3/C4 number.
     Verdict per VALIDATION.md; report violations, edit nothing.

WAVE 3 — do yourself (serial): fix anything Agent F flagged (route to the owning
lane's files), append a v2-reconciliation addendum to docs/phase_reports/ (new file
PHASE_B2_REPORT.md: what changed, decisions C1–C9, open questions rollup), update
memory.md, verify one-concern-per-commit history, push the branch. Do NOT open a PR
unless I ask.
````

## Open Questions

- The Lv 100–300 curve tail (segment law) is deliberately deferred by C3 — owner call in
  a future arc; only the ≤100 anchors are ratified here.
- The 480 kills/h and 70%-hunting-time constants remain unmeasured assumptions; Phase D
  spawn/TTK data should re-verify (existing LEVELING OQ stands).
- Whether ROLE_MONSTER_DESIGNER should also own boss *arena* mechanics or leave them with
  ROLE_WORLD_BUILDER (recommended: monsters/kits vs arena geometry split) — settle when
  the role file is authored.
