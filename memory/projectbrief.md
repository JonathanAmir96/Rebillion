# projectbrief.md — What Rebillion Is and What We Are Building

> Memory Bank file 1/5. Read first, then `systemPatterns.md` → `techContext.md` →
> `activeContext.md` → `progress.md`. Root `memory.md` is the generation-history log
> (newest-first decisions); this directory is the distilled persistent context for the
> coding pass. On any conflict: the owning doc under `docs/` wins — link, never restate.

## Core vision

**Rebillion** is a 2D side-scrolling MMORPG platformer (MapleStory-inspired
"hunt-and-hangout", deliberately *not* a clone — original vocabulary, look, and world).
Target engine: **Godot 4.3+** client, **server-authoritative** backend
(Elixir/OTP + Phoenix, owner-confirmed 2026-07-24). This repository is the
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
- The *game* level cap is **300 (initial design, reserved)** — a future-arcs number.
  **No content, curve rows, or systems beyond the Lv-80 arc boundary may be generated**;
  Lv 100–300 leveling is a provisional softcap sketch only. 3rd-tier jobs are
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
  (lines `bulwark`/`keeneye`/`weaver`/`flicker`) → branching 2nd-job specialization
  Lv 40 (10 specs). Anchors: Lv 40 ≈ 30 h, Lv 80 ≈ 166 h `/played`.
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
- **Combo** (`docs/10_systems/COMBO_SYSTEM.md`): `combo_momentum`/`combo_burst`
  skill-chaining layer, tier-gated by job tier, consumed inside COMBAT_FORMULA §15's
  damage envelope; HUD §7.1 draws the counter.
- **Appearance & entry** (`docs/40_assets/CHARACTER_COMPOSITING.md`,
  `docs/10_systems/ACCOUNT.md`, `docs/10_systems/DISPLAY.md`): composited paper-doll
  player sprite (never one baked sheet), 4-slot roster with Maple-style check-name
  creation, borderless-fullscreen integer-scale 640x360 display.

## Fundamental constraints (laws — every edit, human or agent)

The six laws live in `CLAUDE.md` ("Laws") — the single source; headline recall only:
tokens are law · single source of truth · IDs immutable · flag-don't-guess ·
change-controlled files (owner-directed amendments only) · validate before landing
(US spelling). On any doubt, read `CLAUDE.md`, not this summary.

## Reading order for a fresh session

`README.md` → `docs/00_vision/GLOSSARY.md` → `docs/WORLD_PLAN.md` → root `memory.md` →
this directory. For code work: `docs/30_engineering/ENGINEERING_STANDARDS.md` (locked)
and the `docs/70_integrations/` backend suite (see `techContext.md`).

## Open Questions

- None owned here — this file summarizes; every open item lives in its owning doc and
  is indexed in `activeContext.md`.
