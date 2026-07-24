# DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md — Cross-Doc Contradiction Sweep of `main`

**Status (2026-07-24): all 27 findings below are resolved — 25 fixed same-day on `main`, 2 landed
as owner amendments (UA-001 / ES-001). See §5 Resolution log.**

Scope: a full-tree contradiction sweep of `main` as of 2026-07-24 (post social-package /
cosmetics merge, commit `0b1a632`). Six parallel reviewers covered the tree in clusters —
combat/stats, economy/items, social, world/maps, UI/assets, cross-cutting/GLOSSARY — and every
finding below was then re-verified against the files by hand. Mechanical gates ran first and
were clean: `tools/validate.py` 0 failures / 0 warnings; `tools/md_graph.py` 1 component,
0 orphans, 0 dead-ends. Everything here is therefore *semantic* — two committed statements that
cannot both be true.

Per CLAUDE.md law 4, this report proposes nothing into owning docs: each finding names its
owner(s) and the conflicting statements; resolution (which side wins) is owner-directed, except
where one side is objectively a miscitation of an immutable fact (ID slots, minted content,
section numbers), noted inline as *(objective)*.

Items already carried in a doc's `## Open Questions` were excluded by rule. Two candidate
findings were **discarded during verification**: a claimed stale-v2 `CLAUDE.md` (the on-disk
file is current v3) and a claimed clean guild-cosmetic citation (the overreach is real; kept as
C-24).

---

## 1. High severity — numbers/rules conflicts that would break implementation

**C-01. ECONOMY.md carries two live, conflicting travel-fare tables.**
- `10_systems/ECONOMY.md` §4.3 (lines 138–143): ferry per crossing **25** shards
  (`map_001` ↔ `map_017`), coach **`100 × hops`** (100–400).
- `10_systems/ECONOMY.md` §7.1 (lines 233–238): ferry **40** flat (`map_015`), coach per ring
  segment **120 / 220 / 320**.
- §7's Open Question claims §7.1 "fills WORLD_PLAN's previously-unwritten fare delegation" —
  unaware §4.3 had already written different numbers. §4.3 also mislocates the ferry on
  `map_001` ↔ `map_017`; the ferry door is `map_015` *(objective — WORLD_PLAN edge table,
  `map_015.yaml`)*. Owner: ECONOMY. One table must win and the other become a pointer.

**C-02. Sovereign/Mythic tonic prices: ECONOMY vs minted content — and ECONOMY's §5 spend model
is built on the losing side of its own claim.**
- `10_systems/ECONOMY.md` §4.1 (lines 111–112): Sovereign buy **1,200** / Mythic **1,500**,
  described (lines 120–124) as "deliberately flatter than the arc-1 doubling"; §5 (lines
  187–189) computes arc-2 potion spend from 1,200/1,500.
- `50_content/items/use/consumables.yaml` (`item_use_0017`–`0020`): Sovereign buy **2,000** /
  Mythic **4,000**, commented as "continuing the same doubling step" — the exact curve ECONOMY
  says it rejected. Owner: ECONOMY (prices) + a content re-mint on whichever side loses.

**C-03. T11/T12 equipment `base_buy`: ECONOMY tabulates values minted content contradicts.**
- `10_systems/ECONOMY.md` §4.2 (lines 165–168): T12 = **13,000**; interpolation prose gives
  T11 = **10,500**.
- `50_content/items/equip/weapons.yaml` (header + lines 511–512, 592) and
  `50_content/items/equip/armor.yaml`: T11/T12 extrapolated at **10,000 / 12,000** (so T12
  uncommon 30,000 where ECONOMY's 13,000 × 2.5 = 32,500). T7–T10 agree everywhere. Owner:
  ECONOMY + equip content files.

**C-04. Monster-ID collision: summon-template block sits inside the Frostpeak roster.**
- `10_systems/AI_BEHAVIOR.md` line 287 (a *resolved* note, i.e. committed): "ID_REGISTRY.md now
  reserves … `mob_151`–`mob_160` for summon templates."
- `docs/ID_REGISTRY.md` line 43 and `docs/WORLD_PLAN.md` R9: `mob_151`–`mob_178` = Frostpeak
  (normals 151–170, elites 171–177, boss 178). *(objective — the registry is the immutable
  side; AI_BEHAVIOR's note is stale. PHASE_D_ARC2_REPORT already uses `summon_tmpl_*`
  placeholders "real-ID pending".)* Owner: AI_BEHAVIOR + ID_REGISTRY (mint a real block).

**C-05. COMBAT_FORMULA's `life` formula and its own checksum table disagree at most levels.**
- `10_systems/COMBAT_FORMULA.md` line 218: `life = 4 · (level + 3)²`, with §13's preamble "the
  formulas are authoritative; the table is the checksum."
- Same doc, §13 table (lines 226–254): Lv 1 = 65 (formula 64), Lv 3 = 145 (144), Lv 4 = 195
  (196), Lv 5 = 255 (256), Lv 10 = 675 (676), Lv 40 = 7,395 (7,396)… The table is the formula
  rounded to the nearest multiple of 5, but no rounding rule is stated. §15, the
  `monster.schema.md` example (`life: 4050 # 675 × 6`), and LEVELING's DPS math all propagate
  the *table* values. Owner: COMBAT_FORMULA — either state the round-to-5 rule or regenerate
  the table.

**C-06. `skill.schema.md` enum forbids `scaling` values the owning doc requires.**
- `20_schemas/skill.schema.md` line 90: `effects[].scaling` enum = `power`·`spellpower` only.
- `10_systems/SKILL_EFFECTS.md` lines 81, 112: `heal` scaling =
  `spellpower|power|max_life|flat`; `grant_shield` = `spellpower|max_life|flat` — and §4 calls
  `max_life` load-bearing for the martial self-heal resolution. A validator built from the
  schema rejects legal content. *(objective — SKILL_EFFECTS owns effect params.)* Owner:
  skill.schema.

**C-07. All three schema worked examples mis-slot the Emberfoot elite/boss IDs.**
- `docs/ID_REGISTRY.md` line 35 + minted content: `mob_010` normal ("Coalback Brute"),
  `mob_011` elite ("Embermane Alpha"), `mob_012` boss ("Cindermaw", uniques via
  `drop_mob_012`).
- `20_schemas/monster.schema.md` lines 111–116: example `mob_010` = "Cinder Houndmaster",
  `tier: elite`. `20_schemas/drop_table.schema.md` lines 91–114: `drop_mob_010` as an elite
  table and **Cindermaw at `drop_mob_011`** — which would fail that schema's own rule 6.
  `20_schemas/item.schema.md` line 194: "`source_hint: mob_010` # Cinder Houndmaster (elite)".
  *(objective — registry + minted content are immutable.)* Owner: the three schemas. Dangerous
  as-is: Phase D batches are exemplar-first.

**C-08. `item.schema.md`'s worked example contradicts ITEMS §7, the schema's own rule 7, and
the minted `item_equip_0002`.**
- `20_schemas/item.schema.md` lines 147–163: example `item_equip_0002` "Verdant Fang", T2,
  **`req_level: 10`**, `power: 30` "# ITEMS §7 T2 blade W = 30", affix 4.
- `10_systems/ITEMS.md` §7 (line 190): T2 = req_level **8**, W = **26**; schema rule 7 itself
  says T2 = 8; minted `weapons.yaml` `item_equip_0002` = "Harborwind Cutlass", req 8, power 26,
  affix 3. *(objective.)* Owner: item.schema.

**C-09. `quest.schema.md`'s worked example uses a retired exp curve and fails its own rule 8.**
- `20_schemas/quest.schema.md` lines 88–89, 109: "Lv10 exp_to_next = **3,200**", `exp: 640`.
- `10_systems/LEVELING.md` line 58 and `10_systems/QUESTS.md` §4 table: exp_to_next(10) =
  **8,480** (main-band 15–30% = 1,272–2,544, so 640 is out of band). Adjunct: the example is a
  `level_requirement: 10` quest placed in `emberfoot` (region band Lv 1–8). *(objective.)*
  Owner: quest.schema.

**C-10. GUILD's weekly-goal buff breaks DROPS' "hard ceiling" arithmetic — both sides stamped
"locked at the 2026-07-24 balance pass".**
- `10_systems/DROPS.md` §4.1 (lines 122–126): `guild_drop_buff` max **1.05**; combined
  `m · party · guild` ≤ 2.00 × 1.30 × 1.05 = **×2.73 hard ceiling** (clamp math worked from
  it).
- `10_systems/social/GUILD.md` §11 (line 210): weekly goal met → grouping buff runs at
  **+10% / +10%** for a week → 2.00 × 1.30 × **1.10** = ×2.86, above the stated hard ceiling.
  Owner: DROPS (restate ceiling incl. the weekly lift) or GUILD (cap the lift) — owner's call.

**C-11. GUILD.md puts the guild hall on the Smithy's map.**
- `10_systems/social/GUILD.md` lines 26, 57: guild hall = `map_022`.
- `50_content/maps/map_022.yaml` = "Millbrook Smithy" (blacksmith `npc_019` lives there);
  `map_024.yaml` = "Millbrook Guild Hall". *(objective.)* Owner: GUILD — both references →
  `map_024`.

**C-12. RAID/GUILD claim PERSISTENCE has no day/week boundary; PERSISTENCE §2.1 defines it —
naming these exact consumers.**
- `10_systems/social/RAID.md` line 251: PERSISTENCE "does not yet define one … must land the
  day-boundary rule before §6.D can resolve." `10_systems/social/GUILD.md` lines 285–287
  presents the rollover as undecided.
- `10_systems/PERSISTENCE.md` §2.1 (lines 61–66): daily reset **00:00 UTC**, weekly anchor
  **Monday 00:00 UTC**, explicitly citing the raid first-clear flag and the weekly guild goal.
  *(objective — the blocker premise is stale.)* Owner: RAID + GUILD — consume §2.1.

**C-13. ITEMS §4's arc-1 weapon ID layout contradicts the minted (immutable) layout.**
- `10_systems/ITEMS.md` lines 131–132: blade 0001–0006, **bow 0011–0016, staff 0021–0026, dirk
  0031–0036**, with 0007–0010/0017–0020/… as reserved tails.
- `50_content/items/equip/weapons.yaml` header (lines 11–13, which itself flags the clash) +
  `pools.yaml` references: contiguous **bow 0007–0012, staff 0013–0018, dirk 0019–0024** — and
  ITEMS' own §3 (line 56) already treats `item_use_0011`-family correctly elsewhere.
  *(objective — minted IDs are immutable; ITEMS §4 prose must move, and its Open Questions
  never picked up the yaml's reconcile flag.)* Owner: ITEMS.

**C-14. Content spawn-target defects vs the spawn-naming law (ferry + Millbrook batch).**
- Law: `docs/WORLD_PLAN.md` lines 119–121 / `15_maps_system/MAP_CONNECTIONS.md` §2 — ferry
  doors target `from_ferry`; cross-region walk portals target `from_<origin_slug>`.
- `50_content/maps/map_015.yaml` lines 20–27: both ferry doors target `main` (and
  `map_001.yaml` has no `from_ferry` spawn at all, while `map_017.yaml` authored one that
  nothing targets).
- `50_content/maps/map_027.yaml` lines 27–28 (`→ map_043`) and `map_028.yaml` lines 27–28
  (`→ map_076`): target `main` although `from_millbrook` sits authored and waiting on both
  destinations. Every other checked region batch complies — a Millbrook/ferry batch defect,
  not an alternative convention. *(objective.)* Owner: map content re-mint (+ `map_001` spawn).

**C-15. Three docs still call the tile→pixel scale "not yet locked"; it locked 2026-07-24.**
- `10_systems/CAMERA.md` lines 12–14, 70; `10_systems/INVENTORY.md` §4 (lines 69–71);
  `10_systems/SKILL_SYSTEM.md` lines 131–132 + its Open Questions — all citing
  "COMBAT_FORMULA §10's open scale lock".
- `10_systems/COMBAT_FORMULA.md` §10 (lines 169–175) + resolution note (lines 357–359): **16 px
  grid locked** by `40_assets/ART_BIBLE.yaml` (`base_unit_px: 16`), 8 tiles/s = 128 px/s, the
  200 px/s placeholder retired. *(objective — the cited Open Question is resolved; only the
  default zoom multiplier remains genuinely open.)* Owner: CAMERA, INVENTORY, SKILL_SYSTEM.

---

## 2. Low severity — wording drift, stale citations, mislabeled examples

**C-16. Authored-arc top level: "Lv 1–82" vs "Lv 1–80".** GLOSSARY line 109 and JOBS line 20
say the run authors "Lv 1–82 arcs"; LEVELING lines 16–17, SKILL_SYSTEM lines 21–22,
ID_REGISTRY line 6, and ITEMS line 102 say Lv 1–80. Reconcilable (players cap 80; Voidshore
*elites* overshoot to 82) but the two phrasings read as different facts. Owner: GLOSSARY to pick
one formula; consumers follow.

**C-17. Locked-vs-locked icon grids.** `40_assets/UI_ART_SPEC.md` line 33 allows icons on
**16/24/32** grids; `40_assets/ART_BIBLE.yaml` line 66 allows **16×16 or 24×24** only. Both
files are locked (law 5) — one needs an amendment; neither flags it. Owner: Agent-3 amendment
channel.

**C-18. The Party window is missing from HUD's authoritative window tables, and its name
drifts.** HUD §1 (line 22) lists `frame_window` toggles as "Inventory, Skills/Character, full
Map, Guild" and §11 (line 193) repeats the set — no Party window, although CONTROLS line 32
binds `P` and UI_WINDOWS §4 (lines 118–120) defines the window and claims HUD §1 backs it.
CONTROLS also calls the `P` window "Party-finder" where UI_WINDOWS titles it "Party" (Board
tab inside). Adjunct: CONTROLS §gamepad (lines 55–63) says the hub cycles "**five** panels" /
"five dedicated buttons" while listing and binding **six** (`I K L M G P`). Owner: HUD +
CONTROLS.

**C-19. Party-frame field lists: three docs, three sets, two false "same as" claims.**
PARTY §3 (lines 48–49) includes a job-line icon; HUD §4.1 (lines 88–92) enumerates "what
PARTY §3 specifies" minus that icon; UI_WINDOWS §4 (lines 120–122) claims "the same fields the
HUD party frames show" but lists job title without `life`/`essence` bars. Owner: PARTY (data
contract), HUD/UI_WINDOWS to cite it without restating (law 2).

**C-20. skill.schema exemplar-ID misfires.** (a) Line 219–220 names `skill_weaver_017` /
`skill_flicker_015` as `summon_entity` skills — JOBS says those are Overload
(`apply_status`) and Riposte; the actual summons are `skill_keeneye_010` and
`skill_bulwark_022`. (b) Line 167–168 cites `skill_bulwark_019` for `party_aura` — JOBS and
SKILL_EFFECTS line 226 say `skill_bulwark_020`. (c) Lines 143–144 reference
`skill_flicker_021`, which doesn't exist (flicker authors 001–020; the matching hybrid is
`skill_flicker_019`). (d) OQ lines 211–214 call the `condition` vocabulary "open-ended" while
SKILL_EFFECTS §16 declares it a frozen four-value set that VALIDATION enum-checks.
*(objective set.)* Owner: skill.schema.

**C-21. Small combat-doc drifts.** (a) COMBAT_FORMULA line 202–203 says i-frames "attach to
`dash`/`leap`" unconditionally; SKILL_EFFECTS makes `iframes` opt-in, default **false**, and
JOBS annotates per-skill. (b) COMBAT_FORMULA line 131 pairs "`fortify`/`sunder` via
`armor`/`warding`"; STATUS_EFFECTS line 102 scopes `sunder` to `armor` only. (c) LEVELING
lines 43–44 attribute "one kill per ≈ 7.5 s" to COMBAT_FORMULA §14, which gives a 3–6 s TTK
band (midpoint 4.5 s; the ~3 s repositioning overhead is unstated). (d) STATUS_EFFECTS
line 136–137 narrows `clarity` to "`restore_essence`-relevant" costs against its own
table's unqualified "−15% essence skill costs" (and SKILL_SYSTEM's cost-multiplier rule).
Owners: COMBAT_FORMULA / LEVELING / STATUS_EFFECTS.

**C-22. SCOPE.md "authoritative counts" drift.** (a) Line 24: `arcane` mobs "only in
Clockwork" — WORLD_PLAN R10 (lines 386, 425): Clockwork Ruins **and Arcane Reach** (12 arcane
mobs there). (b) Equip row (line 19) omits the 8 raid-exclusive equips (`0223`–`0230`); etc
row (line 21) omits the 4 raid tokens (`0177`–`0180`), both minted in ID_REGISTRY. Owner:
SCOPE.

**C-23. Maps-cluster stale citations.** (a) MAPS_SYSTEM §4 (lines 78–79) quotes Millbrook's
band as "~15"; WORLD_PLAN fixes 8–14 (content uses 8–9) — 15 isn't even inside the band its
own rule requires. (b) MAPS_SYSTEM §6 and SPAWN line 66 both cite a WORLD_PLAN Open Question
("interiors combat-free — confirm") that WORLD_PLAN no longer carries; the decision itself is
consistent everywhere. (c) npc.schema lines 172–173 cite "Arcane Reach's
athenaeum/observatory interiors" — R10 has an inn, the *Runewake* deck, and a sanctum hall;
the only athenaeum is Verdant's. Owners: MAPS_SYSTEM / SPAWN / npc.schema.

**C-24. Social/eco pointer drift.** (a) GUILD §9 (line 144) cites the guild cosmetic block as
`item_cosmetic_0009`–`0064`; the guild sub-block is `0009`–`0032` (ID_REGISTRY line 139,
COSMETICS §4, GUILD's own OQ). (b) RAID lines 149–151 say the token grant is "authored in the
raid-finale drop table"; drop_table.schema rule 4 (and minted finale tables) make it a
runtime-context grant, "never authored as extra static rows". (c) DROPS OQ lines 265–268
still calls the concrete token IDs "a Phase D / endgame design" — its own §5.4 names all
four. (d) drop_table.schema line 248 says "15 boss-order pairs"; every other source (incl.
its own rule 6) says **11**. Owners: GUILD / RAID / DROPS / drop_table.schema.

**C-25. Worked-example labels.** (a) SCROLLS line 195 labels a `req_level` 50 body piece
"T6" — ITEMS §4: T6 = Lv 36; Lv 50 = T8 (all other numbers in the example are correct for
T8). (b) job.schema line 69 says base primaries are "identical across all **9** authored
jobs" — same file says 15 (novice + 4 + 10). Owners: SCROLLS / job.schema.

**C-26. Authority/persistence pointer drift.** (a) MONETIZATION §2 rule 1 (lines 27–30):
premium goods are "purely presentational — `client`-authority fields only" vs its own §5
(lines 85–87) and PERSISTENCE/COSMETICS: entitlements are **server**-authoritative (rendering
is the client part). (b) PERSISTENCE §2 line 35 assigns `exp_into_level` to LEVELING, which
never defines the term (it defines `exp_to_next`/`cumulative_total`; DEATH_PENALTY and the
backend docs use `exp_into_level` operationally). (c) PERSISTENCE §2's ledger has no row for
COLLECTIONS' server-tagged progress state (discovery/reveal/claim flags) although COLLECTIONS
says PERSISTENCE tags it — and the same table row (line 46) labels the social owner docs
"(stubs)" and omits TRADING/MAIL as the trade/mail owners. (d) COLLECTIONS §7 body (lines
155–158) says "no GLOSSARY token exists yet for 'title'" — GLOSSARY's Provisional block lists
`title` (owner COSMETICS §2); COLLECTIONS' own OQ already states this correctly. Owners:
MONETIZATION / PERSISTENCE / COLLECTIONS.

**C-27. Misc citation/presentation nits.** (a) AUDIO_DESIGN line 94 cites toasts at "HUD §2";
toasts are HUD §9. (b) The gameplay mockup renders the crit damage number in UI emphasis gold
(`#f6c34b`) where HUD §7 (line 150) says "same element tint" — the locked UI_ART_SPEC's "crit
larger+tinted" is ambiguous between the two readings; worth pinning before Phase C metrics.
(c) ENGINEERING_STANDARDS (locked) line 12 names a "Health" component against the `life`
token and its own stat-naming rule — amendment-channel item, not a validation failure
("health" isn't on VALIDATION §1's ban list). (d) Two minted YAML headers assert doc conflicts
that have since been fixed and are now false: `weapons.yaml` lines 5–7 (item.schema's
file-conventions row *does* list `0231`–`0254` now) and `items/etc/enhancement.yaml` lines
16–18 (ENHANCEMENT §1 *does* carry v3 bands now). Owners: AUDIO_DESIGN / HUD+UI_ART_SPEC
amendment / ENGINEERING_STANDARDS amendment / content headers at next re-mint.

---

## 3. Verified consistent (checked, no conflict)

So the next sweep doesn't re-plow it, these were explicitly cross-checked and hold:

- **Social balance pass numbers** — raid stage/clear exp (500/2,500 · 3,000/15,000 ·
  8,000/40,000 · 25,000/125,000; the superseded first-pass set survives nowhere), 15-min clear
  cooldown, `party_drop_bonus` table, exp-share bands 0–15/16–20/21–25/26+, party ×2.00 and
  stacked exp ceiling ×2.10, guild contribution/levels/roster/goal numbers, Quartermaster
  prices (55-token catalog arithmetic), raid tokens `0177`–`0180` and raid gear `0223`–`0230`.
- **Cosmetics** — `item_cosmetic_0001`–`0064` sub-blocks and the zero-stat rule agree across
  COSMETICS / ITEMS / MONETIZATION / item.schema / ID_REGISTRY (modulo C-24a's citation).
- **World arithmetic** — 324 maps (per-type counts recomputed from per-region allocations),
  234 monsters (178/45/11, rosters re-summed), 120 quests + 120 NPCs + 98 skills, raid
  arenas/bosses, coach network, Deepway gate, biome/tileset table, MAP_CONNECTIONS' 8 arc-1
  cross-region edges.
- **Curves** — LEVELING's exp tables reproduce their formulas (~15 rows re-derived incl.
  boundary values and §3.1 raid percentages); STATS growth arithmetic; enhancement fees =
  `3 · mean_shards_normal`; DROPS §3 shard formula vs ECONOMY §3/§5/§7.2 back-solves;
  spot-checked drop tables match formula + tier slots exactly.
- **Vocabulary** — VALIDATION §1 banned-term grep across docs + content: clean (only
  VALIDATION itself and the validator's constant). Retired families (`party quest`, `pq_*`,
  `waygate`) live only in retirement notices. Server-deferred boundary claims agree across
  PERSISTENCE and all eight social docs (modulo C-26's labeling).
- **UI/animation numbers** — 640×360 / 16 px, keybindings across five docs, frame budgets
  and hit-frame defaults across ANIMATION_STATES / ANIMATION_TIMING / SPRITESHEET_SPEC /
  ART_BIBLE, HUD caps vs owning docs (status row 12, tracker ≤3, 8 skill slots, plates ≤5),
  inventory tabs/slots, monster life-bar rules vs the mockup.

## 4. Suggested landing order

1. **Registry/ID facts first** (C-04, C-07, C-11, C-13 — objective, exemplar-poisoning).
2. **Schema worked examples** (C-06, C-08, C-09, C-20 — Phase D is exemplar-first; wrong
   exemplars replicate).
3. **ECONOMY reconciliation** (C-01, C-02, C-03 — one commit, one price truth).
4. **Balance-ceiling call** (C-10) and **stale-lock sweep** (C-12, C-15).
5. Low-severity drift (C-16…C-27) batched per owning doc.

## 5. Resolution log (applied 2026-07-24, owner-directed)

The owner directed a fix pass the same day. **All 27 findings are resolved** on this branch —
the two change-controlled-file findings landed as owner-directed amendments (UA-001, ES-001),
and CLAUDE.md law 5 was updated (owner-directed) from a hard lock to a change-controlled rule:
agent edits still forbidden without explicit owner direction, every directed edit logged in the
file's `amendments` section. Resolutions chosen:

- **C-01 fixed** — §7.1's fares won (newer, anchored to the §5 income model); ECONOMY §4.3 is
  now a pointer, the §2 sink index points at §7, and the §7 OQ records the supersession.
- **C-02 fixed** — ECONOMY §4.1's 1,200/1,500 won (its "deliberately flatter" rationale + the §5
  spend model); `consumables.yaml` `item_use_0017`–`0020` re-minted to 1,200/300 and 1,500/375.
- **C-03 fixed** — ECONOMY §4.2's 10,500/13,000 bases won; all 18 T11/T12 rows in
  `weapons.yaml`/`armor.yaml` re-priced (uncommon 26,250/6,563 and 32,500/8,125), headers
  updated.
- **C-04 fixed** — registry won; AI_BEHAVIOR now describes the `summon_tmpl_*` placeholder
  scheme and carries an OQ requesting a real ID block (none minted).
- **C-05 fixed** — the round-to-nearest-5 rule is stated beside the formula (verified against
  all 29 table rows); table values canonical for content; the two ≈ products made exact.
- **C-06 fixed** — skill.schema's `scaling` enum expanded to SKILL_EFFECTS' legal set with
  per-effect constraints by pointer.
- **C-07/C-08 fixed** — all schema worked examples now mirror minted content: monster.schema →
  `mob_011` (Embermane Alpha), drop_table.schema → `drop_mob_011`/`drop_mob_012`, item.schema →
  minted `item_equip_0002` (Harborwind Cutlass) and `item_etc_0011`.
- **C-09 fixed** — quest.schema example recomputed on the frozen curve (exp_to_next(10) = 8,480,
  `exp: 1696`) and re-slotted to a Millbrook quest ID (band 8–14).
- **C-10 fixed** — GUILD's weekly +10 %/+10 % lift kept; DROPS §4.1 restates `guild_drop_buff`
  1.05 baseline / 1.10 lift week, ceiling ×2.73 / ×2.86, clamp + aggregate arithmetic
  recomputed.
- **C-11 fixed** — guild hall → `map_024` (both references).
- **C-12 fixed** — RAID §6.D and GUILD §11 consume PERSISTENCE §2.1 (00:00 UTC daily / Monday
  weekly); the stale blocker OQs are marked resolved.
- **C-13 fixed** — ITEMS §4 rewritten to the minted contiguous layout (bow 0007–0012, staff
  0013–0018, dirk 0019–0024; reserve = 0025–0040).
- **C-14 fixed** — `map_015` ferry doors target `from_ferry` (spawn added to `map_001` beside
  its ferry door); `map_027`→`map_043` and `map_028`→`map_076` target `from_millbrook`.
- **C-15 fixed** — CAMERA/INVENTORY/SKILL_SYSTEM consume the 16 px lock (px equivalents given,
  tile-first convention kept); the genuinely-open default-zoom question stays open.
- **C-16 fixed** — standardized phrasing "two arcs to Lv 80 (Voidshore elites overshoot to 82)"
  in GLOSSARY and JOBS.
- **C-17 fixed (amendment UA-001, owner-directed)** — ART_BIBLE's 16/24 won (no authored asset
  or doc used a 32 px icon grid); UI_ART_SPEC narrowed to 16/24 with the amendment logged in the
  file.
- **C-18/C-19 fixed** — Party window added to HUD §1/§11; CONTROLS renamed the `P` window and
  corrected five→six; party-plate fields now match PARTY §3's contract; UI_WINDOWS states its
  actual roster field set.
- **C-20 fixed** — skill.schema exemplars corrected (summons → `skill_keeneye_010` +
  `skill_bulwark_022`; party_aura → `skill_bulwark_020`; hybrid → `skill_flicker_019`;
  `condition` OQ resolved as frozen per SKILL_EFFECTS §16).
- **C-21 fixed** — i-frame opt-in wording; `sunder` → `armor` only; 7.5 s/kill split into 4.5 s
  TTK + ≈3 s repositioning; `clarity` note matches its table.
- **C-22 fixed** — SCOPE: arcane = Clockwork + Arcane Reach; equip row +8 raid exclusives
  (~170), etc row +4 raid tokens (~185).
- **C-23 fixed** — Millbrook band 8–14 in MAPS_SYSTEM §4; dangling WORLD_PLAN citations cleared
  in MAPS_SYSTEM §6 / SPAWN; npc.schema cites R10's real interiors.
- **C-24 fixed** — GUILD cosmetic citation → 0009–0032; RAID token grant → runtime entry-context
  wording per schema rule 4; DROPS token OQ resolved; "15 boss pairs" → 11.
- **C-25 fixed** — SCROLLS example relabeled T8 *(see note below)*; job.schema 9 → 15 jobs.
- **C-26 fixed** — MONETIZATION rule 1 splits rendering (client) vs entitlements (server);
  `exp_into_level` defined in LEVELING §1; PERSISTENCE social row de-stubbed with TRADING/MAIL
  owners + a COLLECTIONS progress row added; COLLECTIONS §7 title paragraph unstaled.
- **C-27 fixed** — AUDIO toast cite §9; mockup crit uses the element tint; stale
  weapons/enhancement YAML header claims dropped; (c) ENGINEERING_STANDARDS' survival-pool
  component renamed `Health` → `Life` (amendment ES-001, owner-directed) per its own
  stat-names-from-GLOSSARY rule.

Post-fix gates: `tools/validate.py` 0 failures / 0 warnings; `tools/md_graph.py` 1 component,
0 orphans, 0 unreferenced, 0 dead-ends.

## Open Questions

- None owned here — this is a review report. All 27 findings are resolved per §5's log (C-17 and
  C-27c via owner-directed amendments UA-001/ES-001).
