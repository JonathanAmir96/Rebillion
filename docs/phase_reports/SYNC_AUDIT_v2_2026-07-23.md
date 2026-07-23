# SYNC_AUDIT — Full-Tree Consistency Check vs v2 Canon (2026-07-23)

Audit of every markdown doc in the tree against the current canon (v2, owner revision
2026-07-21: `CLAUDE.md`, `docs/00_vision/SCOPE.md`, `docs/WORLD_PLAN.md`). Run on branch
`claude/markdown-sync-check-tq9i0g`. **No design docs were edited** — per Law 4
(flag, don't guess), this report is the flag; fixes are batched below for the owner-directed
B-revision wave that `SCOPE.md`'s Open Question already promises ("v2 revision arrived after
Phase B … patched by the B-revision wave (tracked in docs/phase_reports/)"). This file is
that tracking doc.

## Verdict

The v2 / v2.1–v2.4 revision commits touched **only** the vision/world layer (CLAUDE.md,
SCOPE, GLOSSARY, PILLARS, WORLD_PLAN, ID_REGISTRY, ART_BIBLE amendment) plus the schemas
created afterward. **The B-revision wave never ran**: all 32 Phase B docs
(`10_systems/*`, `15_maps_system/*`) and most Phase C schemas still encode the pre-v2
world — level cap 100, 12 regions, 15 bosses, Rift raids, the free waygate network, and
job gates 8/30/60. The canon layer itself (GLOSSARY, ID_REGISTRY, PILLARS, WORLD_PLAN,
SCOPE) is internally consistent and verified correct, but it makes three promises about
other files that are unfulfilled (§4).

## 1 · Cross-cutting stale families (each spans many files)

| # | Stale (pre-v2) | Canon (v2) | Affected files |
|---|---|---|---|
| F1 | Level cap 100; monsters to Lv 105; "~201 h to cap" | Cap **300** (initial design); authored arc **Lv 1–42** | STATS, COMBAT_FORMULA, LEVELING, SKILL_SYSTEM, JOBS, DEATH_PENALTY, ECONOMY, DROPS, ITEMS, ENHANCEMENT, QUESTS, MAP_CONNECTIONS, monster/job/item/quest schemas |
| F2 | Job gates 8/**30**/**60**, authored 3rd-job rosters | 1st **Lv 8** → 2nd **Lv 40**; 3rd jobs **named-and-reserved only** | JOBS, SKILL_SYSTEM, DEATH_PENALTY, GUILD (founder gate "Lv 30 = 2nd advancement"), QUESTS, job.schema, skill.schema |
| F3 | 84 line skills (21/line, 3rd tier authored) | **56 total** = 13/line (6 first + 7 second) + 4 novice | JOBS, SKILL_SYSTEM, LEVELING, skill.schema |
| F4 | Rift raid layer: R12, raid bosses `mob_147`–`150`, raid arenas `map_197`–`200`, staging shards `map_183`–`188`, raid tokens `item_etc_0177`–`0192`, `rarity_source: raid` | **No Rift, no raids.** `mob_147`–`149` = Clockwork elites, `mob_150` = The Custodian; `map_195`–`197`+`200` = `pq_mainspring` PQ maps; `183`–`188` = ordinary Clockwork fields; endgame co-op = the **2 party quests** (party 3–6) | COMBAT_FORMULA §13.3/§14, LEVELING, STATUS_EFFECTS, AI_BEHAVIOR, SPAWN §7, DEATH_PENALTY §5.3, DROPS §5.4/§5.5, ITEMS, ENHANCEMENT, QUESTS §4, social/PARTY §6, MAPS_SYSTEM, MAP_CONNECTIONS, monster/npc/item/quest/drop_table/map schemas |
| F5 | Free **waygate** network (touch-once, free forever; `waygate` portal kind, `waygate_console`, `waygate_keeper`) | Paid **Harthmoor Coachworks** (`coach`/`coach_stop` tokens, shard fares, stations at maps 017/018/043/125/071) + paid ferry; **no free warps** | MAPS_SYSTEM, MAP_INTERACTABLES §2/§9, MAP_CONNECTIONS §3/§4, DEATH_PENALTY §4, map.schema, npc.schema |
| F6 | 12-region world: 15 bosses, boss uniques `0201`–`0230`, pools `r01`–`r12`, Frostpeak / Arcane Reach (Sanctum) / Voidshore / Rift as active regions | **8 regions, 8 bosses**, uniques `0201`–`0216`, pools `r01`–`r08`; the 4 extra biomes are **reserved-future**, never content | ITEMS, DROPS, TRADING, DEATH_PENALTY, INVENTORY, MAP_LAYERS §4, MAP_CONNECTIONS §7, item/quest/drop_table/map/npc schemas |
| F7 | Old counts: monsters 112/23/15; items ~144/36/197; 4 towns / 17 interiors / 94 fields / 54 dungeons / 15 arenas / 16 secrets | **118/24/8**; **~86/~30/~133**; **6 towns · 20 interiors · 99 fields · 53 dungeons · 14 secrets · 8 arenas** | monster.schema, item.schema, MAPS_SYSTEM §counts, CAMERA ("15 boss arenas"), ANIMATION_STATES (correctly flags the monster-split clash already) |
| F8 | Broken doc path `10_systems/PARTY.md` | Correct path `10_systems/social/PARTY.md` | STATUS_EFFECTS, AI_BEHAVIOR, SPAWN, DEATH_PENALTY |

## 2 · Per-file severity map

**Major revision needed** (structurally built on the old world):
- `10_systems/LEVELING.md` — cap-100 curve table, 201 h total, §6 post-cap-at-100 + Rift endgame, 150× raid rows.
- `10_systems/JOBS.md` — gates 8/30/60; full 3rd-job skill tables (`014`–`021`); "84 line skills"; 1st advancement placed at an Emberfoot trainer, contradicting the v2.3 pilgrimage to the line's ring town; 2nd/3rd advancement at a "Millbrook-hub trainer" vs canon home-town instructor + Clockwork trial.
- `10_systems/DEATH_PENALTY.md` — exp-loss brackets by 8/30/60 tiers; §4 bind towns "4 towns" with wrong map IDs (`map_029`/`map_041`) and the nonexistent "Arcane Sanctum `map_145`"; waygate routing; 12-region no-town list; §5.3 Rift deaths + staging shards.
- `10_systems/social/PARTY.md` — titled "…& Rift Raids"; §6 is entirely the raid design (party 4–6 vs canon PQ 3–6); never mentions `pq_undervault`/`pq_mainspring`.
- `10_systems/DROPS.md` — raid §5.4 (tokens, Rift etc block), `rarity_source: raid`, pools `r01`–`r12`, Lv 100/105 faucet rows.
- `10_systems/ITEMS.md` — "15 bosses (11 region + 4 raid)", uniques `0201`–`0230`, tier table mapping T6/T9/T10 to Frostpeak/Arcane Reach/Voidshore-Rift; 10-tier grid implies 40 weapons/40 accessories vs SCOPE's 24/16.
- `15_maps_system/MAP_CONNECTIONS.md` — references a WORLD_PLAN "Waygate network" table that no longer exists; §3 free-forever waygate unlock rule; §7 "Frostpeak & Clockwork drop chutes" with map IDs (`073`/`108`/`109`/`144`) that now collide with different canon maps; Rift OQ.
- `15_maps_system/MAP_INTERACTABLES.md` — portal kind enum `edge/door/waygate`; §9 `waygate_console` object; never uses GLOSSARY's `coach`/`coach_stop`.
- `20_schemas/` — **job.schema** (gates 30/60, third tier generated, trainer towns emberfoot/millbrook vs v2.3 instructor towns), **skill.schema** (84 skills, authored `014`–`021`), **item.schema** (~144/36/197, uniques to `0230`, pools `r12`, Rift order 12–15), **drop_table.schema** (12 pools, raid tier, Rift tokens, 15 boss pairs), **map.schema** (12 regions, waygate portal kind + console, Rift `party_min`, Frostpeak chute, tile/tileset terrain unreconciled with AB-001), **quest.schema** ("Rift-band `quest_085`–`090`, region 12" vs canon Clockwork `079`–`086` + PQ handlers `087`–`090`), **monster.schema** (split 112/23/15, level 1–105, raid rule), **npc.schema** (`waygate_keeper`, Rift-camp handler, Arcane Sanctum OQs).

**Moderate / targeted fixes:**
- `10_systems/COMBAT_FORMULA.md` — delete §13.3 raid scaling + raid/Rift rows; trim Lv-45–105 table tails (pipeline itself is clean).
- `10_systems/SKILL_SYSTEM.md` — 99 points at Lv 100, 21-skill math, 3rd-tier gate rows.
- `10_systems/SPAWN.md` — remove §7 Rift arena rules + raid respawn row; **add the v2.3 map-order/monster-gradient law WORLD_PLAN claims is encoded here** (it is not — see §4).
- `10_systems/QUESTS.md` — §4 Rift/region-12 paragraph; 3rd-tier trainer-quest mention.
- `10_systems/social/GUILD.md` — founder gate "Lv 30 = 2nd advancement" (canon 2nd = 40); guild hall cited as `map_033` in "Millbrook Township, R3" (canon: an interior in `019`–`026`, Millbrook Central, R2).
- `15_maps_system/MAPS_SYSTEM.md` — map-type count row (94/54/4/17/15/16), "4 towns", Rift-raid party-min rules, waygate vocabulary.
- `15_maps_system/MAP_LAYERS.md` — §4 "one tileset per biome (12 total)" table presents the 4 reserved-future biomes as active regions; stale region display names (Emberfoot Grounds / Millbrook Township / Ashfall Wastes).
- `15_maps_system/MAP_TRAVERSAL.md` — **owed the AB-001 foothold model** (see §4); "Sunken Depths R5" → R7.

**Minor line fixes:**
- `10_systems/STATS.md` (growth "stops at 100", 198 points, to-100 sample rows) · `STATUS_EFFECTS.md` (Rift CC rows + `PARTY.md` path) · `AI_BEHAVIOR.md` (Rift mentions + path) · `ELEMENTS.md` (one Rift OQ line) · `ECONOMY.md` (Lv-100 anchors) · `ENHANCEMENT.md` (raid drops, R12 OQ, Lv-100 band) · `INVENTORY.md` (bind-town list copied from DEATH_PENALTY §4, wrong IDs + Arcane Sanctum) · `CAMERA.md` ("15 boss arenas") · `social/TRADING.md` (uniques `0201`–`0230` → `0216`) · `SKILL_EFFECTS.md` (3rd-job skill used as an example) · `40_assets/ANIMATION_STATES.md` (OQ claims ANIMATION_TIMING doesn't exist — it now does; light raid phrasing).

**Verified clean (no action):**
`GLOSSARY.md` (coach + foothold tokens present, waygate correctly retired), `ID_REGISTRY.md`
(every block re-verified against WORLD_PLAN/SCOPE — maps, mob split 118/24/8, uniques
`0201`–`0216`, skills 13/line + novice, NPCs 84, quests 86+4 PQ, pools r01–r08, emberstones,
`item_use_0013`), `PILLARS.md`, `VALIDATION.md` §1–§4 (see §4 for §5/§6), `PERSISTENCE.md`,
`CONTROLS.md`, `HUD.md`, `social/CHAT.md`/`MAIL.md`/`MARKET.md`, `ANIMATION_TIMING.md`,
`SPRITESHEET_SPEC.md`, the three locked files (no other doc contradicts a locked value),
`60_agents/roles/ORG.md` model routing.

## 3 · Missing files & broken references

| Reference | Cited by | Status |
|---|---|---|
| `10_systems/social/PARTY_QUEST.md` | WORLD_PLAN (PQ concept owner), SCOPE.md, ID_REGISTRY L123 | **Does not exist.** The PQ system currently has no owner doc; social/PARTY.md covers raids instead. |
| `40_assets/SKILL_ANIMATION.md` | VALIDATION.md §6, skill.schema | **Does not exist** (skill.schema says "lands this phase" — never authored). |
| `40_assets/SPRITE_PIPELINE.md` | ART_BIBLE AB-001 followup ("covers chunk QA"), ROLE_ART_DIRECTOR (asserted as existing) | **Does not exist**; terrain-chunk QA is unowned. |
| `10_systems/PARTY.md` | STATUS_EFFECTS, AI_BEHAVIOR, SPAWN, DEATH_PENALTY | Wrong path — file lives at `10_systems/social/PARTY.md`. |
| `WORLD_PLAN.md` "R12" / "Waygate network" table | 6+ system docs / MAP_CONNECTIONS | Neither exists in current WORLD_PLAN (8 regions; Coachworks section). |
| `docs/60_agents/` phase briefs | README L16, ROLE_GAMEPLAY_DEVELOPER | Only `roles/` exists; briefs are Phase E (README asserts them as present). |
| `docs/50_content/` | README L14, role charters | Phase D — not yet started (expected-future; README asserts it as present). |
| `memory.md`, `docs/70_integrations/`, `WRITING_STYLE.md` | CLAUDE.md, role charters | Declared "once it exists" — acceptable future refs, except ROLE_NARRATIVE_WRITER also cites `WORLD_LORE.md` unconditionally (missing). |

## 4 · Canon-side promises that are unfulfilled (the canon docs themselves need follow-through)

1. **Gradient law not encoded.** WORLD_PLAN v2.3 states the map-order/monster-gradient law
   is "encoded in `10_systems/SPAWN.md` at the B-revision" and that "the validator warns when
   spawn levels are non-monotonic along ID order (VALIDATION.md §5 scope)". **Neither doc
   contains any of it.** Either land the encodings or correct WORLD_PLAN's pointer.
2. **AB-001 foothold model not landed.** ART_BIBLE amendment AB-001 (plus CLAUDE.md, SCOPE
   v2.4, GLOSSARY tokens) points at "the `MAP_TRAVERSAL.md` foothold model" — MAP_TRAVERSAL
   still describes tile-grid terrain only, with no foothold/terrain-chunk content; map.schema
   likewise still models seamless tilesets. The promised movement/terrain rules exist nowhere.
3. **Phase-report tracking gap.** SCOPE's OQ says the v2 patch wave is "tracked in
   docs/phase_reports/" — no B-revision report existed before this audit (this file now serves
   that role), and **no Phase C report exists** despite Phase C deliverables
   (schemas + animation/spritesheet specs) being on disk from two "Phase C checkpoint" commits.

## 5 · Recommended remediation order (B-revision wave batches)

1. **Batch R1 — transport & world vocabulary** (F5, F6-map side): MAPS_SYSTEM,
   MAP_INTERACTABLES, MAP_CONNECTIONS, MAP_LAYERS, map.schema, npc.schema — waygate → coach,
   drop §7 chutes, fix counts (6 towns/8 arenas). GLOSSARY already has every needed token.
2. **Batch R2 — cap & jobs** (F1–F3): JOBS, SKILL_SYSTEM, LEVELING, STATS, DEATH_PENALTY,
   job.schema, skill.schema, GUILD founder gate — gates 8/40, 3rd tier to named-reserved,
   56-skill roster, cap-300/arc-42 framing.
3. **Batch R3 — de-raid** (F4): COMBAT_FORMULA §13.3/§14, SPAWN §7, STATUS_EFFECTS,
   AI_BEHAVIOR, DROPS §5.4/§5.5, ENHANCEMENT, QUESTS §4, ITEMS, TRADING, monster/quest/
   drop_table/item schemas — replace the raid layer with the two PQs (party 3–6);
   **author `social/PARTY_QUEST.md`** as the owner doc.
4. **Batch R4 — terrain follow-through** (§4.2): MAP_TRAVERSAL foothold model,
   map.schema terrain fields, decide SPRITE_PIPELINE.md ownership (or amend AB-001's followup).
5. **Batch R5 — validator & bookkeeping** (§4.1, §4.3): SPAWN gradient law + VALIDATION §5
   monotonic warning, fix VALIDATION §6's `SKILL_ANIMATION.md` ref, `PARTY.md` path fixes,
   Phase C report, README future-dir phrasing, minor line fixes from §2.

## Remediation status (2026-07-23)

Batches R1–R5 applied on branch `claude/markdown-sync-check-tq9i0g` in this same pass:
transport/waygate→coach sweep (R1), cap/job-gate/skill-roster sync (R2), de-raid sweep (R3,
incl. `social/PARTY_QUEST.md` authored as the PQ owner doc), MAP_TRAVERSAL foothold model
landed (R4), VALIDATION §5 gradient warn + §6 repoint plus schema re-count (R5).
Still open: `SPRITE_PIPELINE.md` unauthored (terrain-chunk-QA owner), Phase C report
pending (phase still in progress), locked-file amendments untouched by design.

## Open Questions
- Should the four schemas keep *reserved* old-world ID space (e.g. uniques `0217`–`0230`,
  skill `014`–`030`) documented as reserved-future, or strip all mention? Default: keep as
  explicitly-reserved ranges (matches ID_REGISTRY's extend-never-renumber law).
- MAP_CONNECTIONS §7 drop-chutes: retire entirely, or re-derive an equivalent terminus
  shortcut for canon Sunken Depths (WORLD_PLAN OQ "terminus return shortcut" is still open)?
  Owner: MAP_CONNECTIONS at the R1 batch.
- Does the owner want `social/PARTY.md` rewritten to absorb PQ rules, or a new
  `social/PARTY_QUEST.md` (as WORLD_PLAN/SCOPE currently cite)? Default: new file, matching
  the canon references.
