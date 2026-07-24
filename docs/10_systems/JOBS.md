# JOBS.md — Job Lines, Advancement, Specializations & Skill Rosters

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md, 10_systems/LEVELING.md,
10_systems/COMBAT_FORMULA.md, 10_systems/QUESTS.md, 20_schemas/monster.schema.md,
docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

Owner doc for the four job lines, the `novice` starting class, the **branched** advancement
(1st job → one of a line's **specializations**), and the per-line **skill roster** (which
`skill_<line>_NNN` IDs exist, their tier, and their shape). This doc **names** the lines/jobs/specs
and lists the rosters; it does not define how skills are learned or how their effect ops work —
acquisition/targeting/level_data are `10_systems/SKILL_SYSTEM.md`, effect-op parameters are
`10_systems/SKILL_EFFECTS.md`, stat growth is `10_systems/STATS.md`, elements are
`10_systems/ELEMENTS.md`, statuses are `10_systems/STATUS_EFFECTS.md`.

**v3 owner revision (2026-07-23):** the 2nd advancement (Lv 40) now **branches** into per-line
specializations — a character picks **one** and keeps it for life. This repeals the earlier
"linear, no branching" model (repealed in `00_vision/SCOPE.md` at the v3 revision). Level cap is
**300** (`00_vision/SCOPE.md`); this run authors two arcs, Lv 1–82.

## 0. Token proposals (GLOSSARY Provisional → promote at the gate)

The four line tokens, `novice`, and the advancement names are proposed here for promotion into
`00_vision/GLOSSARY.md`. Line tokens are `snake_case`, one word, used verbatim in skill IDs.
Specialization tokens are `snake_case`, one or two words joined, one per spec.

| Line token | Primary (`10_systems/STATS.md`) | Weapon (GLOSSARY) | Playstyle | `novice` | 1st job (Lv 8) | 2nd-job specializations (Lv 40, choose one) | 3rd tier (future arc) |
|---|---|---|---|---|---|---|---|
| `bulwark` | `might` | `blade` | frontline brawler | Novice | Bulwark | Ironbrand · Stoneguard · Warcaller | Aegis (reserved) |
| `keeneye` | `finesse` | `bow` | ranged precision | Novice | Keeneye | Pathstalker · Sureshot | Skypiercer (reserved) |
| `weaver` | `focus` | `staff` | elemental caster | Novice | Weaver | Runeweaver · Cindercall · Frostbind | Highweaver (reserved) |
| `flicker` | `fortune` | `dirk` | crit / mobility skirmisher | Novice | Flicker | Duskstep · Wildcard | Nightdancer (reserved) |

Specialization tokens (10 total; spec #1 tokens are already GLOSSARY-promoted as the v2 second-job
names, spec #2/#3 are **new** and proposed for promotion):

| Line | Spec #1 (token) | Spec #2 (token) | Spec #3 (token) |
|---|---|---|---|
| `bulwark` | Ironbrand (`ironbrand`) | Stoneguard (`stoneguard`) | Warcaller (`warcaller`) |
| `keeneye` | Pathstalker (`pathstalker`) | Sureshot (`sureshot`) | — |
| `weaver` | Runeweaver (`runeweaver`) | Cindercall (`cindercall`) | Frostbind (`frostbind`) |
| `flicker` | Duskstep (`duskstep`) | Wildcard (`wildcard`) | — |

`novice` (Lv 1–7) is the shared pre-advancement class for **all** players; its display name is
"Novice" (§6). One weapon type is fixed per line by GLOSSARY; equip-restriction enforcement is
`10_systems/ITEMS.md`'s (this doc only asserts the line→weapon pairing).

## 1. Shared advancement rules

- **Bands.** `novice` Lv 1–7 (shared kit, §6) → **1st** advancement at **Lv 8** (choose a line,
  permanent) → **2nd** advancement at **Lv 40** (choose a **specialization** of that line,
  permanent) → **3rd** tier reserved for a **future arc** (default gate Lv 80, Open Questions).
  Level cap **300** (`00_vision/SCOPE.md`); this run authors two arcs, Lv 1–82.
- **Two permanent choices.** The **line** is chosen at the 1st advancement (Lv 8) and is permanent;
  the **specialization** is chosen at the 2nd advancement (Lv 40) and is likewise permanent — a
  character is one line + one spec for life. Stat identity is undifferentiated during `novice`
  (`10_systems/STATS.md` §4.1–4.2: 5/5/5/5, +1 to all on each novice level), so no build is locked
  before Lv 8, and every spec of a line shares the same main primary and weapon, so the Lv 40
  branch is a **skill-kit** choice, not a stat re-class.
- **Branching choice rule.** At Lv 40 a character picks exactly **one** of its line's specs (2 for
  `keeneye`/`flicker`, 3 for `bulwark`/`weaver`). That spec's 7-skill roster (§1 budget) becomes
  learnable; the sibling specs' rosters are **permanently locked** for that character. The specs of
  a line exist as line content but are **mutually exclusive per character** — the sibling rosters
  are never accessible, not merely unlearned (`10_systems/SKILL_SYSTEM.md` §2 line/spec gate).
- **Advancement requirement = level gate + a trainer quest.** Each advancement needs (a) the level
  above **and** (b) completing that line's **job-trainer quest** from the line's home-town
  instructor. Trainer geography is owned by `docs/WORLD_PLAN.md` (§Job instructors, v2.3): each
  line has a home ring-town instructor who issues **both** advancements, and the Lv 40 trial routes
  through the Clockwork Ruins. Pattern only, not concrete IDs (authored Phase D,
  `10_systems/QUESTS.md`, `docs/ID_REGISTRY.md`):

  | Advancement | Level | Instructor (`docs/WORLD_PLAN.md` §Job instructors) | Quest (pattern) |
  |---|---|---|---|
  | 1st (line) | 8 | the line's home-town instructor (the "advancement pilgrimage") | a Lv 8 line-town trainer quest |
  | 2nd (specialization) | 40 | the **same** home-town instructor; trial routes through the Clockwork Ruins | a Lv 40 trainer quest + a Clockwork Ruins trial |
  | 3rd | future arc (default 80) | reserved — future arc | reserved (Open Questions) |

  Trainer-quest `exp` counts toward the region quest budget (`10_systems/LEVELING.md` §4 /
  `10_systems/QUESTS.md`).
- **What an advancement unlocks.** The **1st** unlocks the first-job skill tier (`001`–`006`,
  shared by every spec of the line) and the auto-growth switch to +3 main primary
  (`10_systems/STATS.md` §4.2, already at Lv 9); it grants no stat swap — the line's main primary
  was implicit from Lv 8. The **2nd** unlocks the **chosen** spec's roster (`10_systems/SKILL_SYSTEM.md`
  gates skill tiers/specs on advancement); it grants no extra skill points and no stat swap.
- **Skill budget per line: `skill_<line>_001`–`060`** (re-blocked v3; content YAML was never
  minted, so re-blocking is legal — proposed for `docs/ID_REGISTRY.md`, Open Questions):
  - `001`–`006` — **first-job**, shared by all of the line's specs (**6**).
  - `007`–`013` — **spec #1** roster (**7**; the verbatim v2 second-job tables).
  - `014`–`020` — **spec #2** roster (**7**).
  - `021`–`027` — **spec #3** roster (**7**; `bulwark`/`weaver` only — reserved for the others).
  - `028`–`045` — reserved **3rd tier** (future arc).
  - `046`–`060` — reserved growth.

  Authored per line: `bulwark` 27, `keeneye` 20, `weaver` 27, `flicker` 20 (+ 4 novice = 98).
  Counts checked in §7. A single **character** ranks at most the 6 first-job + its one spec's 7 = 13
  line skills; the other specs are line content it can never reach.

## 2. Bulwark line (`bulwark` · `might` · `blade`)

**Identity.** The town's shield made flesh: a **frontline brawler** who plants their feet between
danger and everyone behind them. Bulwarks open with a taunt, drag stragglers into reach, and turn
incoming punishment into staying power — a warm-hearted wall that only hits harder the longer it
stands. Playstyle is melee, sticky, and control-heavy: `taunt`, `pull`, `knockback`, and
short-radius `aoe_circle` slams anchor a fight while party shields keep allies alive.

**Stat growth.** Main primary `might` (auto +3/level from Lv 9, `10_systems/STATS.md` §4.2),
which drives `power` and lends the minor `life`/`armor` bruiser lean (`10_systems/STATS.md` §1).
Recommended free-pool (`10_systems/STATS.md` §4.3) deepens `might`; a `fortune` splash adds crit
without abandoning toughness. Bulwark relies on high `life`/`armor` rather than `evasion`.

**Element leaning.** Predominantly `neutral` (physical impact), mitigated by the target's `armor`
(`10_systems/ELEMENTS.md` §3); its stagger/armor-break kit pairs `neutral` with `stun`/`sunder`
(`10_systems/ELEMENTS.md` §5 guideline). No dedicated attuned element — leanings kept loose.

### 2.1 First-job kit (`001`–`006`, shared by all bulwark specs)

| ID | Skill | Tier | T | Elem | Primary ops (`10_systems/SKILL_EFFECTS.md`) | Target |
|---|---|---|---|---|---|---|
| skill_bulwark_001 | Shield Bash | 1 | A | `neutral` | `deal_damage` · `apply_status`(`stun`) | `melee_arc` |
| skill_bulwark_002 | Taunting Roar | 1 | A | — | `taunt` | `aoe_circle` |
| skill_bulwark_003 | Bulwark Stance | 1 | A | — | `apply_status`(`fortify`) | `self` |
| skill_bulwark_004 | Iron Grip | 1 | A | `neutral` | `pull` · `deal_damage` | `line` |
| skill_bulwark_005 | Toughened | 1 | P | — | `passive_stat_bonus`(`life`) | `self` |
| skill_bulwark_006 | Sure Footing | 1 | P | — | `passive_stat_bonus`(`armor`) | `self` |

### 2.2 Spec #1 — Ironbrand (`ironbrand`, `007`–`013`)

**Identity.** The aggressive vanguard: an Ironbrand wins by *pressing*, converting momentum into a
wall that bleeds the enemy dry. Charges, staggering slams, and a rallying strike keep the pressure
on while lifesteal and a party shield turn offense into survival — the balanced brawler of the
three, offense-forward but never fragile. Leans `might`→`power` with the line's `neutral`+`stun`
stagger flavor (`10_systems/STATS.md`, `10_systems/ELEMENTS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_bulwark_007 | Charge | 2 | A | `neutral` | `dash` · `deal_damage` · `knockback` | `line` |
| skill_bulwark_008 | Ground Slam | 2 | A | `neutral` | `deal_damage` · `apply_status`(`stun`) · `knockback` | `aoe_circle` |
| skill_bulwark_009 | Aegis Wall | 2 | A | — | `grant_shield` | `party` |
| skill_bulwark_010 | Last Stand | 2 | A | — | `apply_status`(`fortify`) · `heal` | `self` |
| skill_bulwark_011 | Rallying Strike | 2 | A | `neutral` | `deal_damage` · `on_hit_proc`(→`empower`) | `melee_arc` |
| skill_bulwark_012 | Bloodied Resolve | 2 | P | — | `on_hit_proc`(`on_deal`→`heal`) | `self` |
| skill_bulwark_013 | Immovable | 2 | P | — | `passive_stat_bonus`(`armor`,`warding`) | `self` |

### 2.3 Spec #2 — Stoneguard (`stoneguard`, `014`–`020`)

**Identity.** The fortress-protector: a Bulwark who stops caring about the kill and starts caring
about the wall. Stoneguards taunt the biggest threat onto themselves, plant an unmoving stance of
`fortify` and self-cleanse, and punish attackers with `on_take` retribution while a sentinel aura
hardens the whole party's `armor`/`warding`. Leans hardest of the three on `life`/`armor`/`warding`
— pure defense, minimal offense — with the line's `neutral` flavor (`10_systems/STATS.md`,
`10_systems/ELEMENTS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_bulwark_014 | Provoke | 2 | A | `neutral` | `deal_damage` · `taunt` | `melee_arc` |
| skill_bulwark_015 | Stonewall | 2 | A | — | `apply_status`(`fortify`) · `cleanse_status`(`control_type`) | `self` |
| skill_bulwark_016 | Intercept | 2 | A | `neutral` | `pull` · `taunt` | `line` |
| skill_bulwark_017 | Retaliation | 2 | A | — | `apply_status`(`fortify`) · `on_hit_proc`(`on_take`→`deal_damage`) | `self` |
| skill_bulwark_018 | Anchored | 2 | A | — | `grant_shield` · `apply_status`(`regen`) | `self` |
| skill_bulwark_019 | Unyielding | 2 | P | — | `passive_stat_bonus`(`life`) · `on_hit_proc`(`on_take`, `below_life_pct`→`fortify`) | `self` |
| skill_bulwark_020 | Sentinel's Aura | 2 | P | — | `passive_stat_bonus`(`armor`,`warding`, `party_aura`) | `party` |

### 2.4 Spec #3 — Warcaller (`warcaller`, `021`–`027`)

**Identity.** The warband commander: a Bulwark who wins by making everyone else hit harder.
Warcallers open with a `party` war cry (`empower`), plant a battle standard, keep allies moving
with `swiftness` and topped-up `essence`, and leap into the enemy line to break it with `weaken`.
Still a `might`/`blade` frontliner, but the free-pool and passives push `party_aura` uptime and
buff support over personal bruiser stats (`10_systems/STATS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_bulwark_021 | War Cry | 2 | A | — | `apply_status`(`empower`) | `party` |
| skill_bulwark_022 | Battle Standard | 2 | A | — | `summon_entity` (cap 1) | `self` |
| skill_bulwark_023 | Rallying Horn | 2 | A | — | `apply_status`(`swiftness`) · `restore_essence` | `party` |
| skill_bulwark_024 | Second Breath | 2 | A | — | `apply_status`(`regen`) · `cleanse_status`(`control_type`) | `party` |
| skill_bulwark_025 | Break Their Line | 2 | A | `neutral` | `leap` · `deal_damage` · `apply_status`(`weaken`) | `aoe_circle` |
| skill_bulwark_026 | Commanding Presence | 2 | P | — | `passive_stat_bonus`(`might`, `party_aura`) | `party` |
| skill_bulwark_027 | Inspiring Victory | 2 | P | — | `on_hit_proc`(`on_kill`→`empower`) | `party` |

## 3. Keeneye line (`keeneye` · `finesse` · `bow`)

**Identity.** A trail-wise hunter who feeds the town and never wastes a shot: **ranged precision**
built on positioning. Keeneyes open from distance, plant traps, kite with backsteps and slows, and
answer any gap-closer by making it costly to reach them. A falcon companion and a rain of arrows
turn a single archer into zone control. Playstyle rewards spacing and target priority over raw
burst — though the specialist finishers hit like a falling star.

**Stat growth.** Main primary `finesse` (auto +3/level, `10_systems/STATS.md` §4.2), driving
`power` and the `precision` accurate-striker lean (`10_systems/STATS.md` §1). Recommended free-pool
secondary is `fortune` — its `crit_rate`/`crit_power` (`10_systems/STATS.md` §2) turn high
`precision` uptime into reliable crits without a weapon-scaling change.

**Element leaning.** Mostly `neutral` (arrows are physical, mitigated by `armor`); a light `nature`
lean carries poison/thorn shots (`poison`, `root`) per the `10_systems/ELEMENTS.md` §5 guideline.
Slows are modeled with `chill` under a `neutral` flavor (a hamstring, not literal frost — element
is loose, `10_systems/ELEMENTS.md` §5). Fire and frost proper are the Weaver's domain (§4).

### 3.1 First-job kit (`001`–`006`, shared by all keeneye specs)

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_keeneye_001 | Piercing Shot | 1 | A | `neutral` | `deal_damage` | `line` |
| skill_keeneye_002 | Venom Arrow | 1 | A | `nature` | `deal_damage` · `apply_status`(`poison`) | `projectile` |
| skill_keeneye_003 | Backstep | 1 | A | — | `dash` (backward, i-frames) | `self` |
| skill_keeneye_004 | Snare Trap | 1 | A | `nature` | `apply_status`(`root`) | `aoe_circle` |
| skill_keeneye_005 | Steady Aim | 1 | P | — | `passive_stat_bonus`(`precision`,`crit_rate`) | `self` |
| skill_keeneye_006 | Fleet Feet | 1 | P | — | `passive_stat_bonus`(`haste`,`evasion`) | `self` |

### 3.2 Spec #1 — Pathstalker (`pathstalker`, `007`–`013`)

**Identity.** The trapper-beastmaster: a Pathstalker owns the ground around them, kiting with a
falcon at their side, an arrow rain overhead, and slows/knockbacks that keep everything at arm's
length. Sustained precision and a crit-fed `essence` engine reward spacing and uptime over burst.
Leans `finesse`/`precision` with a `fortune` crit splash and the line's `neutral`+`nature`
control flavor (`10_systems/STATS.md`, `10_systems/ELEMENTS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_keeneye_007 | Barrage | 2 | A | `neutral` | `deal_damage` (multi-`hits`) | `projectile` |
| skill_keeneye_008 | Arrow Rain | 2 | A | `neutral` | `deal_damage` | `aoe_circle` |
| skill_keeneye_009 | Hamstring Shot | 2 | A | `neutral` | `deal_damage` · `apply_status`(`chill`) | `projectile` |
| skill_keeneye_010 | Falcon | 2 | A | — | `summon_entity` (cap 1) | `self` |
| skill_keeneye_011 | Concussive Shot | 2 | A | `neutral` | `deal_damage` · `knockback` | `projectile` |
| skill_keeneye_012 | Keen Precision | 2 | P | — | `passive_stat_bonus`(`crit_power`,`precision`) | `self` |
| skill_keeneye_013 | Deadly Momentum | 2 | P | — | `on_hit_proc`(`on_crit`→`restore_essence`) | `self` |

### 3.3 Spec #2 — Sureshot (`sureshot`, `014`–`020`)

**Identity.** The marksman: where Pathstalker zones and kites, the Sureshot deletes one target from
across the map. A deliberate kit of charged `line` shots, armor-`sunder`, caster-`silence`, and a
guaranteed-crit kill shot that executes the wounded — single-target burst over area control. Leans
`finesse`/`precision`/`crit_power`, firing `neutral` arrows with the line's light `nature` splash
(`10_systems/STATS.md`, `10_systems/ELEMENTS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_keeneye_014 | Aimed Shot | 2 | A | `neutral` | `deal_damage` (charged) | `line` |
| skill_keeneye_015 | Sunder Shot | 2 | A | `neutral` | `deal_damage` · `apply_status`(`sunder`) | `projectile` |
| skill_keeneye_016 | Disabling Shot | 2 | A | `neutral` | `deal_damage` · `apply_status`(`silence`) | `projectile` |
| skill_keeneye_017 | Kill Shot | 2 | A | `neutral` | `deal_damage` (guaranteed crit, execute) | `line` |
| skill_keeneye_018 | Take Aim | 2 | A | — | `apply_status`(`empower`) · `apply_status`(`clarity`) | `self` |
| skill_keeneye_019 | Deadeye Focus | 2 | P | — | `passive_stat_bonus`(`crit_power`) · `on_hit_proc`(`on_crit`→`empower`) | `self` |
| skill_keeneye_020 | Executioner's Eye | 2 | P | — | `on_hit_proc`(`on_deal`, `below_life_pct`→`deal_damage`) | `self` |

## 4. Weaver line (`weaver` · `focus` · `staff`)

**Identity.** The town's wise spellhand, weaving raw essence into the elements: an **elemental
caster** who bends fire, frost, and arcane to a fight's shape. Weavers burst with fireballs and
meteors, lock ground with frost and gravity, pierce stealth and casters with arcane, and — alone
among the lines — mend and cleanse allies. Playstyle is a resource-managed rotation: read the
encounter, pick the element, and keep `essence` flowing.

**Stat growth.** Main primary `focus` (auto +3/level, `10_systems/STATS.md` §4.2), which drives
`spellpower` and the `essence`/`warding` caster lean (`10_systems/STATS.md` §1); Weaver skills
scale on `spellpower`, not `power` (`10_systems/SKILL_EFFECTS.md` scaling rule). Recommended
free-pool secondary is more `focus` (deeper pool + burst) with an optional `fortune` splash for
spell crits.

**Element leaning.** The one line that spans attuned elements — leads with **`fire`** (burst,
`burn`), **`frost`** (`chill`/`freeze` control), and **`arcane`** (raw force; the anti-stealth
element that pierces `veil`, `10_systems/ELEMENTS.md` §5). All attuned damage is mitigated by the
target's `warding` (`10_systems/ELEMENTS.md` §3). Leanings stay loose — a Weaver skill may carry
any element it has reason to.

### 4.1 First-job kit (`001`–`006`, shared by all weaver specs)

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_weaver_001 | Firebolt | 1 | A | `fire` | `deal_damage` | `projectile` |
| skill_weaver_002 | Frost Shard | 1 | A | `frost` | `deal_damage` · `apply_status`(`chill`) | `projectile` |
| skill_weaver_003 | Arcane Missiles | 1 | A | `arcane` | `deal_damage` (multi-`hits`) | `projectile` |
| skill_weaver_004 | Mend | 1 | A | — | `heal` | `party` |
| skill_weaver_005 | Attunement | 1 | P | — | `passive_stat_bonus`(`spellpower`,`essence`) | `self` |
| skill_weaver_006 | Essence Flow | 1 | P | — | `on_hit_proc`(`on_deal`→`restore_essence`) | `self` |

### 4.2 Spec #1 — Runeweaver (`runeweaver`, `007`–`013`)

**Identity.** The versatile battlemage: a Runeweaver keeps every element and — uniquely — the
mending arts, reading the encounter to burst with fire, freeze with frost, pierce with arcane, and
still heal and cleanse the party. The generalist spec, defined by element-swap flexibility and
support (`heal`/`cleanse`/`regen`) the other two Weaver specs give up. Leans `focus`/`spellpower`
across all three attuned elements (`10_systems/STATS.md`, `10_systems/ELEMENTS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_weaver_007 | Fireball | 2 | A | `fire` | `deal_damage` · `apply_status`(`burn`) | `aoe_circle` |
| skill_weaver_008 | Frost Nova | 2 | A | `frost` | `deal_damage` · `apply_status`(`freeze`) | `aoe_circle` |
| skill_weaver_009 | Arcane Beam | 2 | A | `arcane` | `deal_damage` (pierces `veil`) | `line` |
| skill_weaver_010 | Renew | 2 | A | — | `apply_status`(`regen`) | `party` |
| skill_weaver_011 | Cleansing Light | 2 | A | — | `cleanse_status` · `heal` | `party` |
| skill_weaver_012 | Elemental Harmony | 2 | P | — | `on_hit_proc` (element swap→`empower`) | `self` |
| skill_weaver_013 | Warding Weave | 2 | P | — | `passive_stat_bonus`(`warding`,`essence`) | `self` |

### 4.3 Spec #2 — Cindercall (`cindercall`, `014`–`020`)

**Identity.** The destroyer: a Weaver who drops the mending and picks up the match. Cindercall
stacks `burn`, lances with a fire `line` beam, drops a telegraphed meteor, and overloads itself
with self-`empower`/`clarity` for uninterrupted burst — no heals, no cleanse (that stays
Runeweaver's). Leans `fire`/`arcane` and `focus`/`crit_rate`; all attuned damage still checks the
target's `warding` (`10_systems/ELEMENTS.md` §3).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_weaver_014 | Incinerate | 2 | A | `fire` | `deal_damage` · `apply_status`(`burn`, `stacks`) | `projectile` |
| skill_weaver_015 | Cinder Beam | 2 | A | `fire` | `deal_damage` (`pierce`) | `line` |
| skill_weaver_016 | Meteor Strike | 2 | A | `fire` | `deal_damage` · `apply_status`(`burn`) | `aoe_circle` |
| skill_weaver_017 | Overload | 2 | A | `arcane` | `apply_status`(`empower`) · `apply_status`(`clarity`) | `self` |
| skill_weaver_018 | Arcane Detonation | 2 | A | `arcane` | `deal_damage` · `apply_status`(`silence`) | `aoe_circle` |
| skill_weaver_019 | Pyromania | 2 | P | — | `passive_stat_bonus`(`spellpower`) · `on_hit_proc`(`on_deal`, vs `burn`→`deal_damage`) | `self` |
| skill_weaver_020 | Combustion | 2 | P | — | `passive_stat_bonus`(`crit_rate`) · `on_hit_proc`(`on_crit`→`apply_status`(`burn`)) | `self` |

### 4.4 Spec #3 — Frostbind (`frostbind`, `021`–`027`)

**Identity.** The controller: a Weaver who wins the ground before the fight starts. Frostbind chains
`chill`, locks single targets in `freeze`, paints slow-zones and gravity wells (`pull`) to herd
packs, and shelters behind an ice barrier — control and survivability over raw burst. Leans
`frost`/`arcane` and `warding`/`focus` (`10_systems/STATS.md`, `10_systems/ELEMENTS.md`).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_weaver_021 | Frost Lance | 2 | A | `frost` | `deal_damage` (`pierce`) · `apply_status`(`chill`) | `line` |
| skill_weaver_022 | Entomb | 2 | A | `frost` | `deal_damage` · `apply_status`(`freeze`) | `projectile` |
| skill_weaver_023 | Frozen Ground | 2 | A | `frost` | `apply_status`(`chill`) · `deal_damage` | `aoe_circle` |
| skill_weaver_024 | Gravity Well | 2 | A | `arcane` | `pull` · `deal_damage` | `aoe_circle` |
| skill_weaver_025 | Ice Barrier | 2 | A | `frost` | `grant_shield` · `apply_status`(`fortify`) | `self` |
| skill_weaver_026 | Permafrost | 2 | P | — | `passive_stat_bonus`(`warding`) · `on_hit_proc`(`on_deal`, vs `chill`→`deal_damage`) | `self` |
| skill_weaver_027 | Deep Freeze | 2 | P | — | `passive_stat_bonus`(`focus`) · `on_hit_proc`(`on_deal`, chance→`apply_status`(`freeze`)) | `self` |

Frozen Ground applies its `chill` zone before its `deal_damage` (`10_systems/SKILL_EFFECTS.md` §2
ordered execution); the persistent-field flavor is a `telegraph`ed `aoe_circle`
(`10_systems/SKILL_SYSTEM.md` §6), not a new op.

## 5. Flicker line (`flicker` · `fortune` · `dirk`)

**Identity.** A charming scoundrel with a good heart and quicker feet: a **crit-and-mobility
skirmisher** who flickers through shadow, opens a throat, and is gone before the body drops.
Flickers stack `crit_rate`/`evasion`, dart with dashes/leaps/blinks, vanish into `veil`, and burst
a single target with `shadow` and precision. Playstyle is hit-and-run: never stand still, punish
the unaware, and let luck (`fortune`) refund the risk.

**Stat growth.** Main primary `fortune` (auto +3/level, `10_systems/STATS.md` §4.2). Uniquely, the
`dirk` routes `power` off `fortune` (`10_systems/STATS.md` §2.1 double-dip), so a single primary
feeds `power`, `crit_rate`, `crit_power`, `evasion`, **and** drop-luck — the intended assassin
fantasy (balance caveat is `10_systems/STATS.md`/`10_systems/COMBAT_FORMULA.md`'s, not ours).
Recommended free-pool secondary is more `fortune`, with a `might`/`finesse` splash if extra `power`
is wanted.

**Element leaning.** `neutral` dirk strikes for reliable physical damage, leaning **`shadow`** for
its signature kit — curse-flavored suppression (`weaken`, `silence`) and the `veil` stealth flavor
(`10_systems/ELEMENTS.md` §5). A `nature` `poison` coats blades. Note the counter: `arcane` sources
pierce `veil` (`10_systems/ELEMENTS.md` §5), so stealth is not a safe button versus arcane enemies.

### 5.1 First-job kit (`001`–`006`, shared by all flicker specs)

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_flicker_001 | Twin Fangs | 1 | A | `neutral` | `deal_damage` (2 `hits`) | `melee_arc` |
| skill_flicker_002 | Shadowstep | 1 | A | — | `dash` (i-frames, behind target) | `self` |
| skill_flicker_003 | Throwing Dirk | 1 | A | `neutral` | `deal_damage` | `projectile` |
| skill_flicker_004 | Vanish | 1 | A | `shadow` | `apply_status`(`veil`) | `self` |
| skill_flicker_005 | Sleight | 1 | P | — | `passive_stat_bonus`(`crit_rate`,`evasion`) | `self` |
| skill_flicker_006 | Fortune's Favor | 1 | P | — | `passive_stat_bonus`(`fortune`) | `self` |

### 5.2 Spec #1 — Duskstep (`duskstep`, `007`–`013`)

**Identity.** The shadow assassin: a Duskstep vanishes into `veil`, appears behind the target, and
opens with a poisoned backstab before slipping away — positional single-target burst built on
stealth, `shadow`, and `poison`. The classic hit-and-run killer, all mobility and misdirection.
Leans `fortune` (→`power`/`crit`) with the line's `shadow`+`nature` flavor (`10_systems/STATS.md`,
`10_systems/ELEMENTS.md` §5).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_flicker_007 | Backstab | 2 | A | `neutral` | `deal_damage` (bonus vs `veil`ed/unaware) | `melee_arc` |
| skill_flicker_008 | Smoke Bomb | 2 | A | `shadow` | `apply_status`(`blind`) · `apply_status`(`veil`) | `aoe_circle` |
| skill_flicker_009 | Envenom | 2 | A | `nature` | `apply_status` (self) · `on_hit_proc`(→`poison`) | `self` |
| skill_flicker_010 | Shadow Flurry | 2 | A | `shadow` | `deal_damage` (multi-`hits`) | `melee_arc` |
| skill_flicker_011 | Shadowhook | 2 | A | `shadow` | `pull` (self→point) · `deal_damage` | `line` |
| skill_flicker_012 | Deadly Precision | 2 | P | — | `passive_stat_bonus`(`crit_power`) | `self` |
| skill_flicker_013 | Evasive Instinct | 2 | P | — | `on_hit_proc`(`on_dodge`→`swiftness`+`restore_essence`) | `self` |

### 5.3 Spec #2 — Wildcard (`wildcard`, `014`–`020`)

**Identity.** The luck-duelist: a Flicker who trades the shadows for the spotlight. Where Duskstep
vanishes and backstabs, the Wildcard stays in the open — whirling `melee_arc` blades into whole
packs, countering with `on_dodge` ripostes, and letting `fortune` refund the risk on every crit.
Leans `fortune`/`evasion`/`haste` and reliable `neutral` steel; no `veil` reliance, so `arcane`
enemies can't punish a stealth it never uses (`10_systems/STATS.md`, `10_systems/ELEMENTS.md` §5).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_flicker_014 | Whirlblade | 2 | A | `neutral` | `deal_damage` (multi-`hits`) | `melee_arc` |
| skill_flicker_015 | Riposte | 2 | A | — | `apply_status`(`fortify`) · `on_hit_proc`(`on_dodge`→`deal_damage`) | `self` |
| skill_flicker_016 | Tumbling Strike | 2 | A | `neutral` | `dash` (i-frames) · `deal_damage` | `melee_arc` |
| skill_flicker_017 | Coin Toss | 2 | A | `neutral` | `deal_damage` · `apply_status`(`blind`) | `projectile` |
| skill_flicker_018 | Gambit | 2 | A | — | `apply_status`(`empower`) · `apply_status`(`swiftness`) | `self` |
| skill_flicker_019 | Lucky Streak | 2 | P | — | `passive_stat_bonus`(`fortune`,`evasion`) · `on_hit_proc`(`on_crit`→`restore_essence`) | `self` |
| skill_flicker_020 | Untouchable | 2 | P | — | `passive_stat_bonus`(`evasion`,`haste`) | `self` |

## 6. Novice — the shared starting kit (Lv 1–7)

Every character begins as `novice` (GLOSSARY Provisional). Novices are undifferentiated
(`10_systems/STATS.md` §4.1) and wield a plain starter weapon; the kit is weapon-agnostic and
teaches the four core verbs — strike, dodge, defend, sustain — that every line builds on. Up to
four skills, `skill_novice_001`–`010` reserved (`docs/ID_REGISTRY.md`); four are authored:

| ID | Skill | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|
| skill_novice_001 | Lunge | A | `neutral` | `deal_damage` | `melee_arc` |
| skill_novice_002 | Tumble | A | — | `dash` (i-frames) | `self` |
| skill_novice_003 | Brace | A | — | `apply_status`(`fortify`) | `self` |
| skill_novice_004 | Second Wind | A | — | `apply_status`(`regen`) | `self` |

Novice skills stay known and usable after advancing, but a character pivots to its line kit at
Lv 8; because skill points are freely respec'd at any town trainer (`10_systems/SKILL_SYSTEM.md`),
points sunk into the novice kit are never stranded. Novice skills use the same `level_data` /
op rules as line skills (`10_systems/SKILL_SYSTEM.md`, `10_systems/SKILL_EFFECTS.md`).

## 7. Roster budget check (per `docs/ID_REGISTRY.md`)

| Line | 1st-job (`001`–`006`) | Spec #1 (`007`–`013`) | Spec #2 (`014`–`020`) | Spec #3 (`021`–`027`) | Passives | Actives | Authored |
|---|---|---|---|---|---|---|---|
| `bulwark` | 4A / 2P | 5A / 2P (Ironbrand) | 5A / 2P (Stoneguard) | 5A / 2P (Warcaller) | 8 | 19 | 27 |
| `keeneye` | 4A / 2P | 5A / 2P (Pathstalker) | 5A / 2P (Sureshot) | — | 6 | 14 | 20 |
| `weaver` | 4A / 2P | 5A / 2P (Runeweaver) | 5A / 2P (Cindercall) | 5A / 2P (Frostbind) | 8 | 19 | 27 |
| `flicker` | 4A / 2P | 5A / 2P (Duskstep) | 5A / 2P (Wildcard) | — | 6 | 14 | 20 |

Every first-job kit is **6** (4A/2P); every spec roster is **7** (5A/2P). Authored per line:
`bulwark` 27, `keeneye` 20, `weaver` 27, `flicker` 20 = **94** line + **4** novice = **98**. A single
character ranks the 6 first-job + its one spec's 7 = **13** line skills; the sibling specs are line
content it can never reach (§1). Across all 98 authored skills, all 14 effect ops
(`10_systems/SKILL_EFFECTS.md`) and all 6 targeting shapes (`10_systems/SKILL_SYSTEM.md`) appear at
least once, and each new spec roster carries a mechanic its line-siblings do not (Stoneguard
`taunt`/thorns vs Warcaller party-auras vs Ironbrand offense; Sureshot single-target execute vs
Pathstalker falcon/zone; Cindercall `burn`-burst vs Frostbind hard-control vs Runeweaver
swap/support; Wildcard `on_dodge` riposte vs Duskstep `veil`/stealth), so no two rosters in a line
duplicate a signature (`00_vision/PILLARS.md` P4).

## Open Questions

- **ID_REGISTRY re-block (proposed, not yet landed).** `docs/ID_REGISTRY.md` still carries the v2
  per-line budget (`001`–`030`, 13 authored). v3 needs the block widened to `skill_<line>_001`–`060`
  with the layout in §1: `001`–`006` first-job · `007`–`013` spec #1 · `014`–`020` spec #2 ·
  `021`–`027` spec #3 (`bulwark`/`weaver` only; `keeneye`/`flicker` reserve `021`–`027`) · `028`–`045`
  reserved 3rd tier · `046`–`060` reserved growth. `skill_novice_001`–`010` unchanged. Re-blocking is
  legal (no content YAML minted); ID_REGISTRY owner to land it in a new commit.
- **GLOSSARY promotion of the 6 new spec tokens** — `stoneguard`, `warcaller`, `sureshot`,
  `cindercall`, `frostbind`, `wildcard` — for the `00_vision/GLOSSARY.md` Job-lines block (the four
  spec #1 tokens are already promoted as the v2 second-job names). Flag if any collides with a
  later-authored token.
- **`00_vision/SCOPE.md` linear-advancement / 56-skills lines — resolved:** SCOPE's v3 revision
  (2026-07-23) now states branching at Lv 40 (10 specs) and 98 authored skills, matching this doc.
- **3rd-tier mapping.** The four reserved 3rd-job names (Aegis/Skypiercer/Highweaver/Nightdancer)
  stay named-and-reserved. Whether each maps as **one capstone per line** (all of a line's specs
  converge on the single reserved name) or as **per-spec capstones** (each spec earns its own,
  needing new reserved names for the sibling specs) is a **future-arc** decision — not made here.
  Default 3rd gate Lv 80; `028`–`045` reserves 18 IDs/line, enough for either model.
- **Specialization permanence.** Spec is permanent like line (§1). Whether a **paid** spec-reset
  (distinct from the free skill respec, `10_systems/SKILL_SYSTEM.md` §3) is ever offered is an
  `10_systems/ECONOMY.md` call; default is no reset (permanent). Skill-point respec **within** the
  chosen spec + first-job + novice stays free (`10_systems/SKILL_SYSTEM.md` §3).
- **Skill-point economy vs the cap-300 branch.** `10_systems/SKILL_SYSTEM.md` §1 owns the +1/level
  total; a character now accesses 13 line skills (6 first-job + one spec's 7) + 4 novice, so the
  point-vs-rank ratio changed from the v2 21-skill assumption. `10_systems/SKILL_SYSTEM.md` §1 is
  patched to reflect branching; the exact end-state (Lv 300) point budget is flagged there.
- Job-trainer NPC IDs and the advancement quest IDs per line are **Phase D** content
  (`10_systems/QUESTS.md`, `docs/ID_REGISTRY.md`); §1 fixes only the level gates (8/40) and defers
  trainer geography to `docs/WORLD_PLAN.md` §Job instructors. Confirm the home-town instructor NPC
  allocations fit each town's `npc` block when quests are authored.
- Whether a small `shards` cost or item gate should accompany the trainer quests (beyond the quest
  itself) is an `10_systems/ECONOMY.md`/`10_systems/QUESTS.md` call; default is quest-only.
- Prerequisite chains among a spec's skills (e.g., a passive feeding off an earlier skill's rank)
  are owned by `10_systems/SKILL_SYSTEM.md`; concrete prereq edges are authored in Phase D skill
  YAML. This roster fixes tier order only. Prereqs reference **same-spec** (or first-job) skills —
  never a sibling spec (`10_systems/SKILL_SYSTEM.md` §2 line/spec gate).
- Summon caps here (`Falcon` 1, `Battle Standard` 1) assume the `10_systems/SKILL_EFFECTS.md` /
  `20_schemas/monster.schema.md` cap of 1–2; confirm at the C gate.
- Balance of the `flicker`/`dirk` `fortune` double-dip inherits the open `10_systems/STATS.md` §2.1
  question; if a `power`-coefficient cut lands there, no name/roster change is needed here.
