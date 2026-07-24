# SYNC_AUDIT — Full-Tree Markdown Consistency Check vs v3.1 Canon (2026-07-23)

Audit + same-pass remediation of every markdown doc against the current canon (v3.1, owner
revision 2026-07-23: `CLAUDE.md`, `docs/00_vision/SCOPE.md`, `docs/WORLD_PLAN.md`,
`memory.md`). Run on branch `claude/markdown-sync-check-tq9i0g` after the v3/v3.1 merges
(phases F–I) landed. Baseline before fixes: `tools/validate.py` strict pass, 0 failures /
0 warnings — the content layer (`50_content/`) was already fully v3; every finding below is
markdown-layer drift.

## Verdict

The successive merge waves (Phase H consistency pass, v3 owner revision, F/G/H reconciliation,
Phase I backend) caught most of the tree, but three families of stragglers survived:

1. **Untouched v1/v2 docs** — `DEATH_PENALTY.md` (old Lv-100 brackets, wrong bind towns incl.
   the nonexistent "Arcane Sanctum", Rift/R12 staging-shard death flow) and parts of
   `STATUS_EFFECTS.md` (references to the deleted `social/PARTY_QUEST.md`, "no raid tier
   exists this arc" contradicting COMBAT_FORMULA §13.2's live raid-boss row).
2. **Schemas behind the content they govern** — `job.schema.md` still encoded the
   non-branching 2nd-job model; `quest`/`drop_table`/`npc`/`monster`/`item`/`map` schemas
   carried v2 counts (90 quests, 84 NPCs, 150 monsters, 200 maps, 12 regions/pools, T1–T10)
   and the invented "Rift raid bosses `mob_147`–`150`" quartet, while `tools/validate.py`
   and `50_content/` were already v3.
3. **v2-era imports and world-shape roll-ups** — `COLLECTIONS.md` (150/150 capstone, 17
   titles, R1–R8), `AUDIO_DESIGN.md` (8-region table, two raids, no Deepway/longship),
   `WORLD_LORE.md` §7 (arc-2 isles listed as unbuilt future), `WIKI_EXPORT.md` (would have
   excluded the three live arc-2 isles from export), `ART_GENERATION_RUNBOOK.md` (art pass
   would skip R9–R11), `MAP_LAYERS.md` (8 tilesets, arc-2 biomes "reserved"),
   `MAPS_SYSTEM.md`/`MAP_CONNECTIONS.md` (200-map counts, "Rift raid arenas
   `map_197`–`200`", stale Frostpeak drop-chutes), plus stale counts/markers in
   `CAMERA.md`, `WRITING_STYLE.md`, `TRADING.md`, `ENHANCEMENT.md`, `ECONOMY.md`,
   `PILLARS.md` P3, `SCOPE.md` (×2), `ANIMATION_STATES.md`, `SPRITESHEET_SPEC.md`,
   `BACKEND_ARCHITECTURE.md`, three role charters, and `RAID.md`'s own Open Questions
   (describing a pre-Phase-D registry state).

Verified clean with no action needed: `ID_REGISTRY.md` (every block sum re-checked against
WORLD_PLAN/SCOPE — maps 324, mobs 178/45/11, uniques 0201–0222, equip re-blocks
non-overlapping, quests 120, pools r01–r11, opcode block), `GLOSSARY.md` (all v3 tokens
present; retirements correct; one Deepway parity entry added), `COMBAT_FORMULA`, `LEVELING`,
`SPAWN`, `QUESTS`, `DROPS`, `ITEMS`, `ELEMENTS`, `PARTY`, `GUILD`, `PERSISTENCE`,
`CONTROLS`, `HUD`, `MAP_TRAVERSAL`, `MAP_INTERACTABLES`, `ONBOARDING_FTUE`, `SCROLLS`,
`SKILL_ANIMATION`, `ANIMATION_TIMING`, the locked files, `ORG.md`, and 7 of the 11 backend
docs (`WORLD_CHANNELS`, `NETWORK_PROTOCOL`, `DATABASE_PERSISTENCE`, `GAMEPLAY_SIMULATION`,
`ACCOUNTS_AUTH`, `CHAT_SOCIAL_BACKEND`, `BUILD_DISTRIBUTION`).

## Remediation applied (this pass, this branch)

- **R1 — 10_systems combat/economy:** DEATH_PENALTY rebuilt to v3 (brackets 1–7/8–39/40+,
  canon bind towns, raid deaths → social/RAID.md, `social/PARTY.md` paths); STATUS_EFFECTS
  and AI_BEHAVIOR re-pointed from PARTY_QUEST to RAID + the live raid-boss tier;
  SKILL_EFFECTS examples re-anchored to real v3 roster skills; STATS/JOBS/SKILL_SYSTEM
  arc framing → two arcs Lv 1–82; ENHANCEMENT emberstone bands re-derived on the T1–T12
  ladder; ECONOMY fee/buy/tonic tables extended to T12 and the 7-tonic ladder;
  INVENTORY/CAMERA count fixes.
- **R2 — social + v2-era imports:** RAID.md stale Open Questions resolved; TRADING unique
  range 0201–0222; WRITING_STYLE 120/120; AUDIO_DESIGN extended to 11 regions, 4 raids,
  Deepway/longship beats; WORLD_LORE §7 corrected (only `rift` reserved) with arc-2 lore
  flagged as open; COLLECTIONS roll-ups to 234/178/45/11/23 titles; ONBOARDING_FTUE raid
  phrasing.
- **R3 — maps + schemas:** MAPS_SYSTEM/MAP_CONNECTIONS/MAP_LAYERS to the 324-map,
  11-region, 4-raid world (drop-chutes retired; raid instancing per RAID.md);
  job.schema rebuilt to the branching 15-job model; monster/item/quest/npc/drop_table/map
  schemas re-counted to v3 with the Rift-raid quartet removed.
- **R4 — assets/roles/backend/canon:** ANIMATION_STATES 11-boss budgets; SPRITESHEET_SPEC
  marker; three role-charter "once it exists" markers resolved; BACKEND_ARCHITECTURE
  terminology; WIKI_EXPORT export scope (arc-2 isles live); ART_GENERATION_RUNBOOK region
  order R1–R11; TELEMETRY slug range; VALIDATION §5 edge-set wording + the monotonic
  spawn-gradient warn promised by WORLD_PLAN; README validator-checks count; PILLARS P3
  five-island framing; SCOPE 234-designs + this tracking pointer; GLOSSARY Deepway entry.

## Known accepted debts (unchanged by design — tracked elsewhere)

- Shields/overalls/scrolls (`0181`–`0200` reserve, `item_use_0061`–`0100`) + COLLECTIONS/
  AUDIO/FTUE deep hooks: authored against v2, integration with v3 systems tracked in
  `ID_REGISTRY.md` Open Questions.
- `WORLD_CHANNELS.md` §7 capacity targets deliberately kept at v2 sizing as launch targets
  (memory.md, Phase I entry).
- `raid_undervault` band 15–22 vs Millbrook ceiling 14; `spec_trial_gate` zone token
  (memory.md known reconciliations).
- `tools/validate.py` `item_use` ID ceiling (0060) predates the scroll block — raise when
  scroll content mints (flagged in VALIDATION.md Open Questions).
- No Phase C or Phase E report exists although `20_schemas/`/`40_assets/` and the
  `60_agents/` role charter are on disk; Phase C landed via checkpoint commits pre-v3 and
  Phase E (coding-pass briefs) has not run. Left unreported rather than fabricating
  retroactive reports; noted here as the tracking record.

## Open Questions
- Arc-2 lore for WORLD_LORE.md (Frostpeak/Arcane Reach/Voidshore, Deepway, longship line)
  is flagged open in that doc — owner ROLE_NARRATIVE_WRITER.
- Emberstone coverage of T11–T12 (possible Emberstone VI at `item_etc_0198`) — owner
  ENHANCEMENT.md with ITEMS.md.
- Whether the retired MAP_CONNECTIONS §7 drop-chutes should be replaced by a v3 terminus
  shortcut is folded back into WORLD_PLAN's terminus Open Question.
