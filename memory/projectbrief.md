# projectbrief.md — What Rebillion Is and What We Are Building

> Memory Bank file 1/5. Read first, then `systemPatterns.md` → `techContext.md` →
> `activeContext.md` → `progress.md`. Root `memory.md` is the generation-history log
> (newest-first decisions); this directory is the distilled persistent context for the
> coding pass. On any conflict: the owning doc under `docs/` wins — link, never restate —
> except where a dated owner ruling in root `memory.md` supersedes a stale doc; those
> patches are queued in `activeContext.md` (§Owner rulings, 2026-07-24).

## Core vision

**Rebillion** is a 2D side-scrolling MMORPG platformer (MapleStory-inspired
"hunt-and-hangout", deliberately *not* a clone — original vocabulary, look, and world).
Target engine: **Godot 4.3+** client, **server-authoritative** backend
(Elixir/OTP + Phoenix + Supabase-managed PostgreSQL, owner-confirmed 2026-07-24). This repository is the
**design-documentation tree**: prose rules, entity schemas, and machine-loadable YAML
content that a later coding pass implements. The end-state is an **autonomously
maintained live game** — production incidents trigger agent repair sessions
(`docs/60_agents/AUTONOMOUS_MAINTENANCE.md`).

Design pillars (`docs/00_vision/PILLARS.md` — a pillar wins any conflict):

- **P1** Readable, snappy, fair combat — visible telegraphs, hit-frame honesty.
- **P2** The grind is cozy, not cruel — legible progression, no trap builds.
- **P3** One world, a walkable ring — geography connects; **no free warps**.
- **P4** Compose, don't enumerate — new content is new *data*, not new rules.
- **P5** Data is the game — every entity is a validated, machine-loadable file.
- **P6** Multiplayer-shaped from day one — the server-authoritative boundary is drawn
  now, even while the interim build is solo.
- **P7** Original identity everywhere.
- Anti-pillars: no pay-to-win (cosmetic-only monetization), no rule text in content
  files, no silent invention (unknown anything → `## Open Questions`).

## Target scope

- **Authored/implementation scope is hard-capped at Level 80 content**: two authored
  arcs, Lv 1–42 (arc 1) and Lv 40–80 (arc 2; elite overshoot to Lv 82). Normal fields
  top out at Lv 80; past ~82 the authored world simply runs out
  (`docs/00_vision/SCOPE.md`, `docs/WORLD_PLAN.md`, `docs/10_systems/LEVELING.md` §6).
- The world level cap is a **hard Lv 80** (owner-ratified 2026-07-24; the former
  Lv-300 reserve is retired — patch wave queued in `activeContext.md`).
  **No content, curve rows, or systems beyond the Lv-80 cap may be generated**;
  the LEVELING §6 Lv 100–300 softcap sketch is queued for removal. 3rd-tier jobs are
  named-and-reserved, gate Lv 80, future arcs.
- World: **5 islands / 11 regions (r01–r11) / 324 maps / 234 monsters (178 normal,
  45 elite, 11 boss) / 4 raids / 120 NPCs / 120 quests / 98 skills**. Arc 1: Emberfoot
  Isle (1–8) → paid ferry → Harthmoor Isle Victoria-style ring (Millbrook ↔ Verdant ↔
  Gloomwood ↔ Ashfall ↔ Tidewatch) around Clockwork Ruins, Sunken Depths spur. Arc 2:
  Deepway (free, Lv-40 gate) → Frostpeak (40–55), Arcane Reach (53–68), Voidshore
  (66–80) linked by the paid scheduled longship network.
- Out of scope for this repo: game code, generated art, localization (US English only),
  monetization implementation. Social/economy systems are fully designed but
  **server-deferred**; interim build is solo behind the authoritative boundary.

## High-level mechanics

- **Stats** (`docs/10_systems/STATS.md`): 4 primaries — `might`/`finesse`/`focus`/
  `fortune` — one per job line; 11 derived (`life`, `essence`, `power`, `spellpower`,
  `armor`, `warding`, `precision`, `evasion`, `crit_rate`, `crit_power`, `haste`).
- **Combat** (`docs/10_systems/COMBAT_FORMULA.md`): pure stateless
  `CombatMath.resolve(attacker, defender, skill, rng)`; mitigation `K(L)/(K(L)+def)`,
  K(L)=50+20·L; 6 elements; ±8% variance; level-diff dampener; monster stat *budget*
  formulas are load-bearing for all 234 monsters.
- **Progression** (`docs/10_systems/LEVELING.md`, `JOBS.md`): novice → 1st job Lv 8
  (lines `bulwark`/`keeneye`/`weaver`/`flicker`) → branching 2nd-job specialization at
  **Lv 30** (10 specs; owner-ratified 2026-07-24, supersedes Lv 40 — doc/content patch
  queued). Curve anchors: Lv 40 ≈ 30 h, Lv 80 ≈ 166 h `/played`.
  `kills_per_level = round(20 + 6.6L + 0.20L²)`, `exp_per_kill = round(4·L^1.3)`.
- **Skills** (`docs/10_systems/SKILL_SYSTEM.md`): +1 point/level, rank cap 10, free
  respec at town trainers, no global cooldown; skills compose 14 effect primitives.
- **Death** (`DEATH_PENALTY.md`): exp loss 0/1/3% by job tier, never de-levels; no item
  or currency loss. **Enhancement** (`ENHANCEMENT.md`): emberstone +1..+9, pity ladder,
  never destroys gear. **Economy** (`ECONOMY.md`): `shards` currency, closed faucet list.
- **Maps** (`docs/15_maps_system/`): Maple-style footholds + painted terrain chunks;
  monster-gradient law (levels rise monotonically along each region's main path).
- **Mob AI** (`docs/10_systems/AI_BEHAVIOR.md`): 8 canonical states + 12 behavior
  profiles; elites/bosses must telegraph; scripted boss phase contract.
- **Social** (`docs/10_systems/social/`): party (2× exp bonus, `party_drop_bonus`),
  4 raids (3–6 players, daily first-clear 2×, raid tokens → quartermaster gear), guild,
  chat, mail, market, trading, party-finder — all designed, all server-deferred.

## Governance map (model routing — owner-ratified 2026-07-24)

- **Opus** — primary automated reasoning engine: cross-system architecture, complex
  game logic, database schemas, network protocols, math formulas, deep system audits.
- **Sonnet** — execution tier: task-bounded implementation, file generation, and diff
  application inside pre-computed manifests.
- **Haiku** — mechanical template fill from a lead's manifest (unchanged per ORG.md).
- **Fable** — **manual override only; never assigned automated roles.** Invoked solely
  on manual developer trigger for high-level producer decisions and overrides.

Full charter, escalation, and boundaries: `memory/systemPatterns.md` §2 +
`docs/60_agents/roles/ORG.md` (amendment queued to record this mapping).

## Fundamental constraints (laws — every edit, human or agent)

1. **Tokens are law**: only `docs/00_vision/GLOSSARY.md` tokens for stats/resources/
   currency/enums. Banned legacy-genre terms live only in `docs/VALIDATION.md` §1.
2. **Single source of truth**: rules in one system doc, shapes in one schema, content
   files hold values + references only. Link, never restate.
3. **IDs are immutable** and must sit inside their `docs/ID_REGISTRY.md` block.
4. **Flag, don't guess**: unknowns go to the owning doc's `## Open Questions`.
5. **Locked files**: `docs/40_assets/ART_BIBLE.yaml`, `docs/40_assets/UI_ART_SPEC.md`,
   `docs/30_engineering/ENGINEERING_STANDARDS.md` — amendment channels only.
6. **Validate before landing**: `python3 tools/validate.py` (VALIDATION checks 1–6)
   must pass 0 failures on every batch. US spelling everywhere.
7. **Backend non-negotiables** (owner-ratified 2026-07-24): server-authoritative
   physics/combat/minting; Supabase-managed PostgreSQL under strict ACID with explicit
   row-level locks (`SELECT … FOR UPDATE`) on every two-sided swap; files <250 lines,
   diff-only edits, manifest-cached static reference data (`memory/systemPatterns.md`).

## Reading order for a fresh session

`README.md` → `docs/00_vision/GLOSSARY.md` → `docs/WORLD_PLAN.md` → root `memory.md` →
this directory. For code work: `docs/30_engineering/ENGINEERING_STANDARDS.md` (locked)
and the `docs/70_integrations/` backend suite (see `techContext.md`).

## Open Questions

- None owned here — this file summarizes; every open item lives in its owning doc and
  is indexed in `activeContext.md`.
