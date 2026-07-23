# memory.md — Generation State & Decisions Log

Read after `README.md` → `GLOSSARY.md` → `WORLD_PLAN.md`. Newest entries first.

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
