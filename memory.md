# memory.md — Generation State & Decisions Log

Read after `README.md` → `GLOSSARY.md` → `WORLD_PLAN.md`. Newest entries first.

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
