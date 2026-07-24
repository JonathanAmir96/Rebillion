# memory.md — Generation State & Decisions Log

Read after `README.md` → `GLOSSARY.md` → `WORLD_PLAN.md`. Newest entries first.
Companion Memory Bank (distilled current state, coding-pass context):
`memory/projectbrief.md` → `memory/systemPatterns.md` → `memory/techContext.md` →
`memory/activeContext.md` → `memory/progress.md`.

## 2026-07-24 — md-audit wave merged; the six audit calls ruled (owner-directed)

Owner approved: the audit branch merged to `main` (merge `4bba402`, 217 files) and all six
flag-don't-guess calls from `MD_AUDIT_REPORT_2026-07-24.md` §8 ruled the same day (branch
`claude/md-audit-followups-2026-07-24`): **(C3)** the `icon` field is **derived-implicit** —
never stored in content; asset id derives 1:1 from the entity `id` (item.schema rule 16 /
skill.schema rule 10 / VALIDATION §6; validate.py's unknown-field gate now enforces it, no tool
change needed). **(C15)** SPAWN §1 adopts map.schema's **absolute-count** spawn model
(`{mob, count}`, `target_count` = sum) — the shape all minted maps use. **(C20)** MAPS_SYSTEM §1
declares optional **`trigger_zones`** (named SPAWN-style rects) for quest `reach` steps;
validator wiring + map backfill deferred to Phase E. **(C26)** Agent-3 operates **all three**
amendment channels (AB-/UA-/ES-), coordinating with the engineering roles on substantive ES-
entries. **(C29)** ECONOMY §7.1's 3+-segment coach tier stays as **explicit future headroom**
(no current pair spans 3+; 2-segment row carries the real longest hop, Mossmere ↔ Tidewatch
Port). Shield/overall (call 4) stays tracked debt for its integration wave. Gates clean.

## 2026-07-24 — repo-wide md audit, cleanup & consistency pass (owner-directed)

Branch `claude/md-audit-2026-07-24` — **presented for owner review; nothing merged to `main`
per the audit's merge policy.** Full report (the authoritative record of this wave):
`docs/phase_reports/MD_AUDIT_REPORT_2026-07-24.md`. Method: 8 read-only reviewer sub-agents
over all 117 md files (grill evidence contract) + producer adjudication; 6 mock-up authors;
validator + md_graph gated every commit (0/0 throughout).

- **Relevance pass:** dated supersession banners on 4 phase reports + the executed
  BACKEND_KICKOFF_PROMPT; ~10 stale already-landed Open Questions closed (ITEMS registry
  re-block, JOBS skill re-block + spec tokens, SPAWN filename, PARTY_FINDER tokens, PARTY HUD
  region, SKILL_SYSTEM bar count…); Law-2 restatement trims (ACCOUNT name law, README rules,
  PARTY drop-bonus ladder); this file's misplaced gameplay-loop entry relocated to
  newest-first order; GLOSSARY `coach_station`/`coach_clerk`/`pier_officer` promoted
  (C-gate condition met) + `from_ferry` formalized; last "(v2.3)/(v3)" vintage tags dropped.
- **Contradiction sweep:** ~27 rulings, owner doc wins every time — headline: ORG.md's
  "locked files touched by no one" → CLAUDE.md Law 5 change-controlled wording (swept through
  5 role files + 6 other docs); memory/techContext slots 3→4; TELEMETRY ≤3→≤4; NETWORK_PROTOCOL
  opcode count 103→106; BACKEND_ARCHITECTURE/CHAT_SOCIAL gain `party_finder` (§7 row + §3.7
  stub); DATABASE_PERSISTENCE gains the PERSISTENCE §2.1 time-gate table; RAID §5 wipe list
  gains the COMBAT_FORMULA §13.3 enrage trigger; SCOPE↔COSMETICS §3.1 reconciled;
  MAP_TRAVERSAL finally defines footholds (AB-001) + MAP_LAYERS bridge; WIKI_EXPORT
  acknowledges the landed wiki_gen.py; schema exemplars disclaimed/synced; FTUE §2 gap
  arithmetic fixed. **Flagged-not-fixed owner calls (5):** the schema `icon` law (required by
  item/skill schemas, absent from all minted rows, validator would reject it), SPAWN
  mob_pool weight-vs-count model, MAPS_SYSTEM reach-step trigger zones, ITEMS shield/overall
  integration pointer, the ES- amendment channel operator.
- **Connectivity:** true directed BFS exposed the 5-file `memory/` Memory Bank as unreachable
  (the CLI degree check reads 0) — linked from README/CLAUDE.md/memory.md; counts 98/98 →
  **117/117**; MD_CONNECTIVITY_REPORT regenerated with the BFS caveat.
- **Change-controlled amendments (owner-authorized for this audit):** UA-002 + ES-002
  (structural `## Open Questions` conformance), UA-003 (mock-ups referenced as non-binding).
  ART_BIBLE.yaml verified clean, untouched.
- **Quest-`exp` regen (the flagged Phase-D handoff) landed:** `tools/regen_quest_exp.py`,
  120/120 mechanically regenerated on the ratified curve, authored pcts preserved
  (0 out-of-band), two Phase-D authoring slips healed (quest_058 mis-computed integer;
  quest_097 e(54)=716 slip), comments refreshed. **FTUE §2 verified: Emberfoot quest sum
  3,804 ≥ 3,800 — the 60-min Lv-8 promise closes before one-time grants.** QUESTS/LEVELING
  stale-exp OQs closed; `shards` + monster `stats.exp` untouched.
- **Content hygiene:** grey→gray (31 flavor strings, the only US-spelling family tree-wide);
  banned-token sweep zero hits outside VALIDATION.md.
- **Mock-ups:** `gameplay_scene_mockup.html` refreshed to exact ART_BIBLE tokens; 5 new
  wireframes (entry/roster/creation · Millbrook hub · inventory+character windows · world
  map/travel · raid boss HUD) — all self-contained, palette-locked, README-linked.

## 2026-07-24 — unlogged waves, reconstructed by the md audit (retroactive entry)

Two landed waves carried no memory entry (found via `git log` during the audit; placement
here is approximate — times from git): the **`memory/` Memory Bank** (5-file distilled
context: projectbrief/systemPatterns/techContext/activeContext/progress, commit `1b28149`
@ ~07:24 UTC) and **`docs/70_integrations/SERVER_LOGGING_SPEC.md` + the ID_REGISTRY
log-event-code blocks** (commits `ec5e839`/`6370a72` @ ~10:57 UTC). Both were audited and
reconciled by the md-audit wave above (the Memory Bank was also unreachable + partly stale —
fixed there).

## 2026-07-24 — wiki generator + per-monster animation notes (owner-directed)

Branch `claude/monster-maps-design-review-d0sytf` (rebased onto main). Owner directives: (1) a
hiddenstreet-style reference wiki generated from the YAML; (2) per-monster animation
descriptions (attack/jump/etc., dodge visuals, boss multi-attack tells). Checked first: the
27-finding contradiction report (`DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md`) was already
fully resolved on main (§5 log) — nothing to fix; both gates clean before starting.

- **New tool `tools/wiki_gen.py`** — static HTML wiki from `docs/50_content/` (805 pages,
  cross-linked, zero broken links): per-monster pages (stats incl. `evasion` as dodge %,
  abilities + telegraphs + status effects, boss phases, animation notes, drops resolved to
  item names, spawn-map reverse index), per-map pages (portals, spawn zones, NPCs, layout
  brief), NPC/quest pages, item/skill catalogs, region indexes. Stdlib-only (reuses
  `validate.load_yaml`); output `wiki/` is gitignored build output. Asserts nothing of its own
  (law 2) — every number is read from the minted files.
- **`animation_notes` contract** — `20_schemas/monster.schema.md` gains optional
  `animation_notes` (map state → ≤1-sentence visual brief; keys ⊆ `animation_states`; motion/
  silhouette only — palette stays ART_BIBLE's, timing stays ANIMATION_TIMING's; new rule 11)
  and `abilities[].animation_note` (wind-up tell + release read). Enforced in
  `docs/VALIDATION.md` §6 + `tools/validate.py` (subset + non-empty). Worked example re-synced
  to minted `mob_011` in full (C-07 lesson).
- **Content: all 234 monsters authored** — R1 exemplar batch first (mob_001–012), then 10
  region-scoped author sub-agents (R2–R11, Phase D batch pattern) for mob_013–234. Machine-
  verified: 234/234 files, notes keys == declared states everywhere, all 143 elite/boss
  abilities carry `animation_note`, boss `phase_shift` notes sell each phase transition.
  Gates after landing: `validate.py` 0/0; `md_graph.py` 1 component / 0 orphans.
- **Open (owner calls, flagged not guessed):** (a) no evade/dodge visual exists — the 12-state
  set is closed, so a successful `evasion` roll is presentation-only; logged in
  `ANIMATION_STATES.md` Open Questions (13th `evade` state vs. reuse rule, frame budget needs
  Agent-3/ART_BIBLE blessing). (b) Owner's MapleStory-style 30 s skill-lock idea vs. the
  current `silence` framework (soft CC, authored ≤3 s on bosses) — a balance-pass call, not
  authored. (c) Batch agents noted pre-existing `animation_states` declarations that don't
  match some `ai_profile` expectations (e.g. two `kamikaze_burster` normals without
  `telegraph`: mob_079, mob_216) — pre-existing, untouched, for the schema/AI_BEHAVIOR owners.

## 2026-07-24 — composited character sprites + entry flow + display (owner-directed)

Branch `claude/customizable-character-sprites-gq2eq3` (merged origin/main mid-session — it had
moved to the v3 five-island world, so all of the below is reconciled against that state). Owner
directives: (1) MapleStory-style customizable player sprites motivated by PixelLab token economy;
(2) up to 4 characters per account; (3) Maple-style "check name" nickname-taken check at creation;
(4) game launches fullscreen.

- **New owner doc `40_assets/CHARACTER_COMPOSITING.md`** — player = paper-doll layer stack (10
  layers, fixed z-order), never one baked sheet. Animated parts (base body + body/legs/boots/gloves
  equips, full ~34-frame sets) vs **anchored parts** (hair/face/hat/cape/weapon: 1–3 stills placed
  per frame by the base body's anchor map; `grip_pose` selects among 3 weapon orientation rows).
  Per-part export reuses SPRITESHEET_SPEC verbatim (part ID in the `{entity_id}` position —
  resolves the export-naming half of the old player-`entity_id` question). Generation cost linear
  in parts: arc-1 wardrobe ≈ 1k frames vs ~34/look baked. **Spike before Phase D wardrobe
  authoring:** base body + 1 outfit + 2 hairs to validate pose-guided part alignment.
- **AB-002 (ART_BIBLE amendments[], owner-authorized)** — 5 skin ramps (only new colors) + 6 hair
  swatches reusing existing palette hexes; layer-restricted; composited export blessed;
  `part_layer`/`pose_ref` PixelLab injects. GLOSSARY: "Player sprite layers" section +
  `style_<category>_NN` prefix; ID_REGISTRY: "Appearance styles" block (base 1 / hair 12 / face 8
  / 5+6 swatches, growth reserved). SCOPE cosmetics line narrowed: creation appearance in scope;
  MONETIZATION §3.1's reserved cosmetic layer untouched. Distinct from `item_cosmetic`
  skins/dyes (COSMETICS.md) — relation flagged in the compositing doc's Open Questions, incl.
  pending `shield`/`overall` slot-integration wave (overall maps onto the `covers: [legs]`
  mechanism).
- **Entry flow** — new `10_systems/ACCOUNT.md` (player-facing roster + 3-step creation:
  check-name → appearance → confirm; always `novice`; availability answered through the
  `GameState` facade so solo/live share one code path). Quota **raised 3→4** in its owner
  `70_integrations/ACCOUNTS_AUTH.md` §2.2 (+ §2.4/§4.1/OQ mirrors) and PERSISTENCE §6; nickname
  law stays ACCOUNTS_AUTH §5's (not restated). `nickname` meta token added to GLOSSARY.
- **New `10_systems/DISPLAY.md`** — borderless fullscreen default, largest-integer-factor scaling
  of the locked 640x360 base, `ink` letterbox, `display_mode` client setting (frame_system +
  Alt+Enter). Resolves CAMERA/HUD's "once a target resolution is fixed" flags.
- **Backend wiring (follow-up, same directive):** DATABASE_PERSISTENCE §3.1 `character` gains the
  four appearance columns (style ids, range-checked on write). NETWORK_PROTOCOL mints: §9.2
  `op_0105`/`op_0194` name-check pair (full §5 gate, session-scoped reservation), `op_0103/0193`
  extended with appearance picks + `invalid_appearance`, `op_0191` roster corrected 3→4 slots +
  per-entry appearance descriptor for roster-screen compositing; §9.5 `op_0401` player spawns
  carry the appearance descriptor (`style_*` + `worn_visible` ids only — clients resolve to local
  atlases, no pixels on the wire), new `op_0406 appearance_delta` re-broadcast on visible-slot
  equip change (§9.9 rows cross-cite). COMPOSITING §10 documents the peer-render path.

## 2026-07-24 — combo layer + HUD stance + advancement quest lines (owner-directed)

Branch `claude/game-hud-combo-system-9n1wim` (rebased onto main). Owner directives: (1) HUD is
MapleStory-*inspired*, never a copy; (2) add a skill-chaining combo system (basic attack + distinct
offensive skills → higher sustained damage); (3) confirm passives + multi-target offensive
coverage (deliberately not every spec); (4) real quest lines for the 2nd and 3rd advancements.

- **New owner doc `10_systems/COMBO_SYSTEM.md`** — `combo_momentum` (chain counter; links grow
  only on source *change*, 3.0 s window; tiers ×1.05/×1.10/×1.15 at 3/6/10 links, tier cap gated
  by job tier: novice I / 1st job II / 2nd job III / 3rd reserved) and `combo_burst` (three
  distinct consecutive sources incl. ≥2 actives → ×1.25 on the bursting cast + 5% max `essence`
  refund, 8 s ICD). Not a status (no 12-cap slot, uncleansable), player-only, per-instance (AoE
  finishers burst on every target). Consumed at COMBAT_FORMULA §2 step 8 (`damage_dealt_mult` =
  `empower` × `weaken` × `combo_momentum`); the whole ≈+15% envelope lives **inside** §15's
  `mult m`, so §14 TTK bands are untouched (non-comboer ≈5.2 s, still in band). Input model =
  sequences on existing bindings, no chords (CONTROLS §3.1; owner's `Ctrl+X+V` chord idea mapped
  deliberately to sequenced presses for gamepad/rebind parity). HUD §7.1 owns the counter
  drawing. New GLOSSARY Provisional tokens `combo_momentum`/`combo_burst`. Backend citations
  synced (GAMEPLAY_SIMULATION §5.1/§5.2).
- **HUD §0 design stance** — classic side-scroller shell grammar (bottom bar, exp strip, minimap)
  as *inspiration*; zero copied layout/art; everything resolves through the locked
  UI_ART_SPEC/ART_BIBLE tokens; named deliberate divergences (Dodge slot, phase pips, combo
  counter, party column). Mirrors UI_WINDOWS's original-identity stance.
- **JOBS §7.1 roster coverage law** — every kit keeps 2 passives; every *line* keeps ≥1
  multi-target offensive active per authored tier, but multi-target depth is a spec identity
  axis (Sureshot and Duskstep are the deliberate single-target outliers). 3rd-tier rosters
  inherit both invariants.
- **Advancement quest lines (JOBS §1.1)** — 1st = the four minted First Rites (011/025/037/059).
  2nd = the two-quest Second Rite chain (First Rite prereq → minted 012/036/038/060), now with a
  canonical per-line **trial ground** in the Clockwork Ruins (`<line>_trial_ground` zones;
  chambers fixed in WORLD_PLAN §Job instructors: bulwark map_186 · keeneye map_190 · weaver
  map_177 · flicker map_180) and a designed solo gauntlet (3 waves of Lv 38–40 constructs + one
  6-link tier-II chain; death-free retry). Content fixes: quest_012/036 zones standardized;
  **quest_060 gained its missing Clockwork `reach` leg** (was Ashfall-only — contradiction with
  JOBS §1's "trial routes through the Clockwork Ruins"). 3rd = reserved three-quest line
  `quest_121`–`132` (ID_REGISTRY extension, 3/line: Calling → Pilgrimage → Naming rite),
  unauthored until the 3rd-tier arc (with `skill_<line>_028`–`045`).
- Gates clean after all edits: `validate.py` 0/0; `md_graph.py` 1 component / 0 orphans
  (114 files). Open: gauntlet scripting mechanism owner (MAP_INTERACTABLES/AI_BEHAVIOR/SPAWN),
  combo magnitudes to the balance pass, 3rd-tier momentum cap with the future arc.

## 2026-07-24 — gameplay-loop review + owner-directed fix pass

Branch `claude/game-design-review-mockup-yemsgl`. (Relocated here 2026-07-24 by the md audit —
this entry sat unheaded at the file tail, violating the newest-first law; content unchanged.)
Critical review in `docs/phase_reports/GAMEPLAY_LOOP_REVIEW_2026-07-24.md`; visual mock-up
(field HUD, boss variant, depth stack, windows) in `docs/mockups/gameplay_scene_mockup.html`.
Owner decisions landed: COMBAT_FORMULA §10 move speed synced to 8 tiles/s (128 px/s); SPAWN §2
density re-anchored to per-20-walkable-tiles (zoom-independent, dynamic map sizes); FTUE keeps
the 60-min Lv-8 promise via front-loaded scripted grants; raid handler quests are one-time
(repeat rewards via RAID's clear mechanics); new HUD §6.1 non-boss life bars beneath the
sprite; HUD wallet placed bottom-bar-right; HUD §4.1 party-frame region reserved; new
`10_systems/UI_WINDOWS.md` (Inventory / Character paper-doll / Party / Guild window
layouts, classic framed-window family, original identity). Still-open design items are
listed in the review's §6 resolution log.

## 2026-07-24 — full-tree contradiction sweep (post social/cosmetics merge)

Six-cluster parallel review of `main` (commit `0b1a632`), every finding hand-verified; report:
`docs/phase_reports/DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md`. Mechanical gates clean
(`validate.py` 0/0, `md_graph.py` 1 component / 0 orphans); **27 semantic contradictions found**
(C-01…C-27): 15 high (two live ECONOMY fare tables; tonic + T11/T12 prices vs minted content;
`mob_151`–`160` summon-template claim colliding with the Frostpeak block; COMBAT_FORMULA `life`
formula vs its checksum table; schema worked examples off-registry/off-curve in all four schemas;
GUILD weekly +10% vs DROPS ×2.73 hard ceiling; guild hall `map_022`→`map_024`; stale
day-boundary and tile-scale-lock claims; ITEMS §4 weapon-ID layout vs minted; ferry/Millbrook
spawn-target defects) + 12 low (citation/label/pointer drift). Resolutions are **owner-directed**
(law 4) — nothing was changed in owning docs; the report routes each finding and proposes a
landing order (registry facts → schema exemplars → ECONOMY → ceiling call → drift batches).
Also confirmed consistent: all 2026-07-24 social-balance numbers, cosmetics blocks, world
arithmetic, LEVELING curves, banned-term sweep, UI/animation numbers (report §3).

**Fix pass (same day, owner-directed "fix"):** 25/27 resolved on the branch — resolution log in
the report's §5. Sides chosen: ECONOMY §7.1 fares win (§4.3 → pointer); ECONOMY prices win over
minted content (tonics 1,200/1,500; T11/T12 bases 10,500/13,000 — 26 content rows re-minted);
registry/minted IDs win over prose and schema exemplars everywhere (all four schemas' worked
examples now mirror minted rows); GUILD's weekly +10% lift kept, DROPS ceiling restated ×2.73
baseline / ×2.86 lift week; `life` checksum table's round-to-5 rule stated; 16 px tile-scale lock
consumed by CAMERA/INVENTORY/SKILL_SYSTEM; arc phrasing standardized ("two arcs to Lv 80,
Voidshore elites overshoot to 82"); ferry/Millbrook spawn targets re-minted per MAP_CONNECTIONS
§2 (`from_ferry` spawn added to map_001). The two change-controlled-file findings landed as
**owner-directed amendments**: UA-001 (UI_ART_SPEC icon grids 16/24/32 → 16/24, matching
ART_BIBLE; nothing used 32 px) and ES-001 (ENGINEERING_STANDARDS component `Health` → `Life` per
the `life` token). **CLAUDE.md law 5 updated (owner-directed):** "Locked files — do not edit" →
"Change-controlled files" — agent-initiated edits still forbidden; edits land only on explicit
owner direction and are logged in the file's `amendments` section (`AB-`/`UA-`/`ES-` ids).
Post-fix gates clean (`validate.py` 0/0; `md_graph.py` 1 component / 0 orphans).

## 2026-07-24 — social-package balance pass + cosmetics system (owner-directed follow-ups)

The two follow-ups left open by the social package (below) are done; all first-pass magnitudes are
now **balanced numbers with the arithmetic shown in the owning docs**, and the cosmetics ID block
has an owner doc.

**A — Balance pass (magnitudes locked against the retuned curve):**
- **Raid `exp` retuned** (`LEVELING.md` §3.1): the first-pass values missed the 10–15%-of-a-band-
  level target badly (undervault full clear ≈ 83% of a mid-band level; voidtide ≈ 8%). New
  structure `raid_clear_exp = 5 · raid_stage_exp` (full clear = 8 × stage ≈ 11% of band-midpoint
  `exp_to_next`): undervault 500/2,500 · mainspring 3,000/15,000 · deepfrost 8,000/40,000 ·
  voidtide 25,000/125,000 (9–18% across each band). First-clear-of-the-day 2× + bonus token
  unchanged. **15-min clear cooldown confirmed** (`RAID.md` §5): even back-to-back chaining pays
  less `exp`/h than at-level hunting.
- **`party_drop_bonus` locked** (`DROPS.md` §4.1): 1.00/1.05/1.10/1.16/1.22/1.30 final. Combined
  ceiling `m·party·guild` = ×2.73 theoretical / ×1.77 realistic; 0.95 clamp binds only on `common`
  rows at the theoretical max; aggregate item supply +30% over six solos (shards untouched).
- **Widened exp-share band confirmed** (`PARTY.md` §4): 0–15/16–20/21–25/26+ is safe — the pool's
  anchor-keyed `exp_diff_mult` craters down-farming, and a max-gap passenger earns ≈ 47%/h vs
  ≈ 108%/h self-hunting.
- **Guild numbers set** (`GUILD.md`): raid clear +10 / party-hunt milestone (100 kills) +5
  `guild_contribution` (≈ 24 pts/h/member either way); guild levels 1–5 at 0/2k/6k/15k/30k
  (modeled active guild → L5 in ≈ 4–5 months); levels 2–5 unlock further **paid** +10 roster steps
  to a ceiling of **100**; grouping buff locked flat **+5%/+5%** (no guild-level scaling; stacked
  exp ceiling ×2.10); weekly goal alternates 25 raid clears / 60 milestones, reward = next week's
  buff at +10%/+10%.
- **Raid Quartermaster prices locked** (`ITEMS.md` §13): equip **10** · title **15** · cosmetic
  effect **20** `raid_token`s (full per-raid catalog 55 ≈ 4 weeks of daily first-clears).
- Open Questions in each doc resolved or narrowed to telemetry-only retunes. VALIDATION untouched
  (producer-owned).

**B — Cosmetics system authored:** new owner doc **`10_systems/COSMETICS.md`** — categories
`title`/`dye`/`skin`/`crest_flourish` (GLOSSARY Provisional, owner COSMETICS), the
`item_cosmetic_NNNN` row shape (unlock entries: no price/stats/effects/stack), earn channels
(raid Quartermaster / guild levels / events), the 5-slot zero-stat appearance loadout
(MON-001 §3.1's reserved seam now anchored), and the server-deferred boundary (collection titles
solo-live; raid/guild cosmetics dormant with their sources). `ID_REGISTRY.md` cosmetic block now
owner-assigned and sub-blocked (0001–0008 raid / 0009–0032 guild / 0033–0048 event / 0049–0064
growth); pointers updated in ITEMS/GUILD/COLLECTIONS/MONETIZATION/RAID/PERSISTENCE/item.schema.
Ownership falls under ROLE_SYSTEMS_ARCHITECT's blanket `10_systems/*` charter (no ORG.md change
needed). A VALIDATION zero-stat check on `item_cosmetic_*` rows is **proposed** in COSMETICS
Open Questions. `md_graph.py`: 1 component, 0 orphans; `validate.py`: clean.

## 2026-07-24 — social package: encourage party hunting + raids (owner-directed)

Owner goal: **encourage grouping (party hunting + raids) to build in-game social play** —
carrots, not solo penalties (the design keeps solo viable; grouping is the *better*, not the
*only*, path — P2/P3). Builds on the existing 2× party exp bonus (`PARTY.md` §4). Spec (all
first-pass, tunable; flagged in each doc's Open Questions):

**A — Raids as the social centerpiece** (`social/RAID.md`, `LEVELING.md` §3.1, `ITEMS.md`,
`DROPS.md`, `ID_REGISTRY.md`):
- Raid tokens `item_etc_0177`–`0180` (undervault/mainspring/deepfrost/voidtide), guaranteed to
  each eligible member on finale clear; spent at a **Raid Quartermaster** vendor.
- Raid-exclusive gear `item_equip_0223`–`0230` (2 per raid, token-bought, aspirational
  side-grades) + a raid-exclusive **cosmetic/title** per raid (reserved cosmetic note).
- Clear exp ≈ doubled: stage/clear = undervault 3k/20k · mainspring 6k/40k · deepfrost
  10k/60k · voidtide 16k/100k (a full clear ≈ 10–12% of a band-level).
- **First-clear-of-the-day 2× bonus** (per character, per raid) + a bonus token — daily social
  rhythm, no weekly lockout. Clear cooldown 30 → 15 min.

**B — Party-hunting sweeteners** (`PARTY.md` §4, `DROPS.md`):
- **`party_drop_bonus`** (same-map eligible members): 1/2/3/4/5/6 → 1.00/1.05/1.10/1.16/1.22/
  1.30× on drop *chances* (owned by DROPS; stacks with `fortune`'s multiplier, both capped).
- Widen full-credit exp-share band: 0–15 gap = 1.00 (was 0–10); 16–20 = 0.66; 21–25 = 0.33;
  26+ = 0. Mixed-level friends hunt at full credit.

**C — Party-finder / LFG + hubs** (new `social/PARTY_FINDER.md`): server-authoritative board;
post/browse listings by activity (field_hunt/raid/quest), region, level band, open slots;
request-join → leader accept; town hangout hubs (Millbrook plaza + port towns). Server-deferred
like the other social systems.

**D — Guild incentives** (`social/GUILD.md`): `guild_contribution` from raids/party hunts →
guild level/unlocks; a small **guild grouping buff** (+exp/+drop) when 2+ guildmates same-map
party; a rotating **weekly guild goal** → guild-wide reward.

New GLOSSARY tokens: `party_drop_bonus`, `guild_contribution` (derived quantities); raid-token
item names; `party_finder` mechanism. IDs use existing reserved blocks (no renumbering).

## 2026-07-24 — single-canon consolidation + pacing retune (owner-directed)

`main` is the single source of truth: the **five-island / two-arc world** (11 regions,
324 maps, 234 monsters, 11 bosses, 4 raids, branching 2nd-job specializations, cap 300) is
the one design. A parallel two-island reconciliation had briefly been merged in and is now
**reverted** — its docs, decision-contract framing, and phase report were removed so the
tree no longer carries competing "versions." Owner rulings this session:

1. **Pacing retune.** Too fast before. New ratified `/played` anchors: **Lv 40 ≈ 30 h ·
   Lv 80 ≈ 166 h · Lv 100 ≈ 300 h**. Curve: `exp_per_kill_normal(L) = round(4·L^1.3)`
   (unchanged) · `kills_per_level(L) = round(20 + 6.6·L + 0.20·L²)` frozen through Lv 100,
   provisional linear softcap past 100 · `/played = kills_per_level / (480×0.70)`. Owner doc
   `10_systems/LEVELING.md`. Per-kill exp, monster stats, economy, drops, and TTK are
   curve-invariant. **Follow-up owed:** the authored `50_content/quests/*.yaml` `exp` rewards
   (pct × exp_to_next) are now stale and need a mechanical regen pass (Phase D); FTUE Lv-8
   gate now lands ≈1.1 h, flagged for the intro owner.
2. **Raid naming** stays as the tree already had it: "raid" / `raid_<name>` / `social/RAID.md`
   for the instanced co-op runs; "party quest" / `pq_*` is retired notation. (The mode remains
   MapleStory-inspired; only the term differs.)
3. **De-labeled** the version-soup: stripped "(v2)/(v3)/(v2.2)/(v3.1)" tags from doc
   titles/headers and the WORLD_PLAN/ID_REGISTRY version intros so the tree reads as one
   design. Dated amendment logs and this history remain.

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

