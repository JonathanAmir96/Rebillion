# JOBS.md — Job Lines, Advancement & Skill Rosters

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/STATS.md, 10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/SKILL_EFFECTS.md, 10_systems/LEVELING.md,
10_systems/COMBAT_FORMULA.md, 10_systems/QUESTS.md, 20_schemas/monster.schema.md,
docs/ID_REGISTRY.md, docs/WORLD_PLAN.md

Owner doc for the four job lines, the `novice` starting class, the twelve advancement jobs, and
the per-line **skill roster** (which `skill_<line>_NNN` IDs exist, their tier, and their shape).
This doc **names** the lines/jobs and lists the rosters; it does not define how skills are learned
or how their effect ops work — acquisition/targeting/level_data are `10_systems/SKILL_SYSTEM.md`,
effect-op parameters are `10_systems/SKILL_EFFECTS.md`, stat growth is `10_systems/STATS.md`,
elements are `10_systems/ELEMENTS.md`, statuses are `10_systems/STATUS_EFFECTS.md`. Job
advancement is **linear** (no branching, `00_vision/SCOPE.md`).

## 0. Token proposals (GLOSSARY Provisional → promote at the B gate)

The four line tokens, `novice`, and the twelve advancement job names are proposed here for
promotion into `00_vision/GLOSSARY.md` (`00_vision/GLOSSARY.md` Provisional; `docs/ID_REGISTRY.md`
reserves `skill_<line>_001`–`030` per line). Line tokens are `snake_case`, one word, and used
verbatim in skill IDs.

| Line token | Primary (`10_systems/STATS.md`) | Weapon (GLOSSARY) | Playstyle | `novice` | 1st job (Lv 8) | 2nd job (Lv 40) | 3rd job (future arcs, name reserved) |
|---|---|---|---|---|---|---|---|
| `bulwark` | `might` | `blade` | frontline brawler | Novice | Bulwark | Ironbrand | Aegis |
| `keeneye` | `finesse` | `bow` | ranged precision | Novice | Keeneye | Pathstalker | Skypiercer |
| `weaver` | `focus` | `staff` | elemental caster | Novice | Weaver | Runeweaver | Highweaver |
| `flicker` | `fortune` | `dirk` | crit / mobility skirmisher | Novice | Flicker | Duskstep | Nightdancer |

`novice` (Lv 1–7) is the shared pre-advancement class for **all** players; its display name is
"Novice" (§6). One weapon type is fixed per line by GLOSSARY; equip-restriction enforcement is
`10_systems/ITEMS.md`'s (this doc only asserts the line→weapon pairing).

## 1. Shared advancement rules

- **Bands (v2).** `novice` Lv 1–7 (shared kit, §6) → **1st** advancement at **Lv 8** → **2nd** at
  **Lv 40**. The game cap is 300 (initial design, `00_vision/SCOPE.md`); **3rd jobs are
  named-and-reserved only** — their skills, quests, and level gate ship with future arcs.
- **Line is chosen at the 1st advancement (Lv 8)** and is permanent — a character is one line for
  life (linear model, `00_vision/SCOPE.md`). Stat identity is undifferentiated during `novice`
  (`10_systems/STATS.md` §4.1–4.2: 5/5/5/5, +1 to all on each novice level), so no build is locked
  before Lv 8.
- **Advancement requirement = level gate + a trainer quest.** Each advancement needs (a) the
  level above **and** (b) completing that line's **job-trainer quest** given by a town job-trainer
  NPC. Trainer NPCs live in town NPC blocks and their quests in the trainer-town quest block
  (`docs/ID_REGISTRY.md`; concrete `npc_NNN`/`quest_NNN` IDs are authored in Phase D —
  `10_systems/QUESTS.md`). Pattern only, not concrete IDs:

  | Advancement | Level | Trainer location (v2.3 pattern) | Quest (pattern) |
  |---|---|---|---|
  | 1st | 8 | the line's **home-town instructor** (`docs/WORLD_PLAN.md` "Job instructors": Bulwark→Cindershelf, Keeneye→Tidewatch Port, Weaver→Mossmere, Flicker→Millbrook Central), reached via the advancement pilgrimage (one free coach ride from Rosen Harbor) | a Lv 8 trainer quest in the instructor's town |
  | 2nd | 40 | the **same instructor**, routing the candidate through a trial in the Clockwork Ruins | a Lv 40 trainer quest, Clockwork trial |

  Per-line home towns (v2.3, classic-style) replace v1's centralized Millbrook trainers; the
  pilgrimage is the deliberate first journey (`00_vision/PILLARS.md` P3). Trainer-quest `exp`
  counts toward the region quest budget (`10_systems/LEVELING.md` §4 / `10_systems/QUESTS.md`).
- **What an advancement unlocks:** the next skill tier (`10_systems/SKILL_SYSTEM.md` gates skill
  tiers on job tier) and the auto-growth switch to +3 main primary (`10_systems/STATS.md` §4.2,
  already at Lv 9). It does **not** grant a stat swap — the line's main primary was implicit from
  Lv 8.
- **Skill budget per line (v2): 13 authored this arc**, `skill_<line>_001`–`013` in tier order —
  **6** first-job (`001`–`006`), **7** second-job (`007`–`013`) — including the line's passives
  (`docs/ID_REGISTRY.md`). The third-job tier (`014`–`021`) is **named-and-reserved**: its skill
  concepts below are future-arc plans, not Phase D content; `022`–`030` stays reserved growth.
  Counts checked in §7.

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

| ID | Skill | Tier | T | Elem | Primary ops (`10_systems/SKILL_EFFECTS.md`) | Target |
|---|---|---|---|---|---|---|
| skill_bulwark_001 | Shield Bash | 1 | A | `neutral` | `deal_damage` · `apply_status`(`stun`) | `melee_arc` |
| skill_bulwark_002 | Taunting Roar | 1 | A | — | `taunt` | `aoe_circle` |
| skill_bulwark_003 | Bulwark Stance | 1 | A | — | `apply_status`(`fortify`) | `self` |
| skill_bulwark_004 | Iron Grip | 1 | A | `neutral` | `pull` · `deal_damage` | `line` |
| skill_bulwark_005 | Toughened | 1 | P | — | `passive_stat_bonus`(`life`) | `self` |
| skill_bulwark_006 | Sure Footing | 1 | P | — | `passive_stat_bonus`(`armor`) | `self` |
| skill_bulwark_007 | Charge | 2 | A | `neutral` | `dash` · `deal_damage` · `knockback` | `line` |
| skill_bulwark_008 | Ground Slam | 2 | A | `neutral` | `deal_damage` · `apply_status`(`stun`) · `knockback` | `aoe_circle` |
| skill_bulwark_009 | Aegis Wall | 2 | A | — | `grant_shield` | `party` |
| skill_bulwark_010 | Last Stand | 2 | A | — | `apply_status`(`fortify`) · `heal` | `self` |
| skill_bulwark_011 | Rallying Strike | 2 | A | `neutral` | `deal_damage` · `on_hit_proc`(→`empower`) | `melee_arc` |
| skill_bulwark_012 | Bloodied Resolve | 2 | P | — | `on_hit_proc`(`on_deal`→`heal`) | `self` |
| skill_bulwark_013 | Immovable | 2 | P | — | `passive_stat_bonus`(`armor`,`warding`) | `self` |
| skill_bulwark_014 | Seismic Leap | 3 | A | `neutral` | `leap` · `deal_damage` · `apply_status`(`stun`) · `knockback` | `aoe_circle` |
| skill_bulwark_015 | Colossus Smash | 3 | A | `neutral` | `deal_damage` · `apply_status`(`sunder`) | `melee_arc` |
| skill_bulwark_016 | Bulwark's Bastion | 3 | A | — | `grant_shield` · `apply_status`(`fortify`) | `party` |
| skill_bulwark_017 | Retribution | 3 | A | `neutral` | `apply_status`(`fortify`) · `on_hit_proc`(`on_take`→`deal_damage`) | `self` |
| skill_bulwark_018 | Unbreakable | 3 | P | — | `passive_stat_bonus`(`life`) · `on_hit_proc`(low-`life`→`fortify`) | `self` |
| skill_bulwark_019 | Warlord's Presence | 3 | P | — | `passive_stat_bonus`(party aura) | `party` |
| skill_bulwark_020 | Earthshaker | 3 | A | `neutral` | `deal_damage` · `pull` · `apply_status`(`stun`) | `aoe_circle` |
| skill_bulwark_021 | Aegis Eternal | 3 | A | — | `grant_shield` · `cleanse_status`(`control_type`) · `apply_status`(`fortify`) | `party` |

## 3. Keeneye line (`keeneye` · `finesse` · `bow`)

**Identity.** A trail-wise hunter who feeds the town and never wastes a shot: **ranged precision**
built on positioning. Keeneyes open from distance, plant traps, kite with backsteps and slows, and
answer any gap-closer by making it costly to reach them. A falcon companion and a rain of arrows
turn a single archer into zone control. Playstyle rewards spacing and target priority over raw
burst — though the third-job finishers hit like a falling star.

**Stat growth.** Main primary `finesse` (auto +3/level, `10_systems/STATS.md` §4.2), driving
`power` and the `precision` accurate-striker lean (`10_systems/STATS.md` §1). Recommended free-pool
secondary is `fortune` — its `crit_rate`/`crit_power` (`10_systems/STATS.md` §2) turn high
`precision` uptime into reliable crits without a weapon-scaling change.

**Element leaning.** Mostly `neutral` (arrows are physical, mitigated by `armor`); a light `nature`
lean carries poison/thorn shots (`poison`, `root`) per the `10_systems/ELEMENTS.md` §5 guideline.
Slows are modeled with `chill` under a `neutral` flavor (a hamstring, not literal frost — element
is loose, `10_systems/ELEMENTS.md` §5). Fire and frost proper are the Weaver's domain (§4).

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_keeneye_001 | Piercing Shot | 1 | A | `neutral` | `deal_damage` | `line` |
| skill_keeneye_002 | Venom Arrow | 1 | A | `nature` | `deal_damage` · `apply_status`(`poison`) | `projectile` |
| skill_keeneye_003 | Backstep | 1 | A | — | `dash` (backward, i-frames) | `self` |
| skill_keeneye_004 | Snare Trap | 1 | A | `nature` | `apply_status`(`root`) | `aoe_circle` |
| skill_keeneye_005 | Steady Aim | 1 | P | — | `passive_stat_bonus`(`precision`,`crit_rate`) | `self` |
| skill_keeneye_006 | Fleet Feet | 1 | P | — | `passive_stat_bonus`(`haste`,`evasion`) | `self` |
| skill_keeneye_007 | Barrage | 2 | A | `neutral` | `deal_damage` (multi-`hits`) | `projectile` |
| skill_keeneye_008 | Arrow Rain | 2 | A | `neutral` | `deal_damage` | `aoe_circle` |
| skill_keeneye_009 | Hamstring Shot | 2 | A | `neutral` | `deal_damage` · `apply_status`(`chill`) | `projectile` |
| skill_keeneye_010 | Falcon | 2 | A | — | `summon_entity` (cap 1) | `self` |
| skill_keeneye_011 | Concussive Shot | 2 | A | `neutral` | `deal_damage` · `knockback` | `projectile` |
| skill_keeneye_012 | Keen Precision | 2 | P | — | `passive_stat_bonus`(`crit_power`,`precision`) | `self` |
| skill_keeneye_013 | Deadly Momentum | 2 | P | — | `on_hit_proc`(`on_crit`→`restore_essence`) | `self` |
| skill_keeneye_014 | Rapid Fire | 3 | A | `neutral` | `deal_damage` (multi-`hits`) | `projectile` |
| skill_keeneye_015 | Thornvolley | 3 | A | `nature` | `deal_damage` · `apply_status`(`poison`) | `aoe_circle` |
| skill_keeneye_016 | Mark of the Hunt | 3 | A | — | `apply_status`(`empower`) | `party` |
| skill_keeneye_017 | Evasive Roll | 3 | A | — | `dash` (i-frames) · `apply_status`(`swiftness`) | `self` |
| skill_keeneye_018 | Rain of Arrows | 3 | A | `neutral` | `deal_damage` | `aoe_circle` |
| skill_keeneye_019 | Beastmaster | 3 | P | — | `passive_stat_bonus` · `on_hit_proc` (Falcon applies `poison`) | `self` |
| skill_keeneye_020 | Deadeye Shot | 3 | A | `neutral` | `deal_damage` (guaranteed crit) | `line` |
| skill_keeneye_021 | Arrowstorm | 3 | A | `neutral` | `deal_damage` · `apply_status`(`chill`) | `aoe_circle` |

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

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_weaver_001 | Firebolt | 1 | A | `fire` | `deal_damage` | `projectile` |
| skill_weaver_002 | Frost Shard | 1 | A | `frost` | `deal_damage` · `apply_status`(`chill`) | `projectile` |
| skill_weaver_003 | Arcane Missiles | 1 | A | `arcane` | `deal_damage` (multi-`hits`) | `projectile` |
| skill_weaver_004 | Mend | 1 | A | — | `heal` | `party` |
| skill_weaver_005 | Attunement | 1 | P | — | `passive_stat_bonus`(`spellpower`,`essence`) | `self` |
| skill_weaver_006 | Essence Flow | 1 | P | — | `on_hit_proc`(`on_deal`→`restore_essence`) | `self` |
| skill_weaver_007 | Fireball | 2 | A | `fire` | `deal_damage` · `apply_status`(`burn`) | `aoe_circle` |
| skill_weaver_008 | Frost Nova | 2 | A | `frost` | `deal_damage` · `apply_status`(`freeze`) | `aoe_circle` |
| skill_weaver_009 | Arcane Beam | 2 | A | `arcane` | `deal_damage` (pierces `veil`) | `line` |
| skill_weaver_010 | Renew | 2 | A | — | `apply_status`(`regen`) | `party` |
| skill_weaver_011 | Cleansing Light | 2 | A | — | `cleanse_status` · `heal` | `party` |
| skill_weaver_012 | Elemental Harmony | 2 | P | — | `on_hit_proc` (element swap→`empower`) | `self` |
| skill_weaver_013 | Warding Weave | 2 | P | — | `passive_stat_bonus`(`warding`,`essence`) | `self` |
| skill_weaver_014 | Meteor | 3 | A | `fire` | `deal_damage` · `apply_status`(`burn`) | `aoe_circle` |
| skill_weaver_015 | Blizzard | 3 | A | `frost` | `deal_damage` · `apply_status`(`chill`) | `aoe_circle` |
| skill_weaver_016 | Singularity | 3 | A | `arcane` | `pull` · `deal_damage` | `aoe_circle` |
| skill_weaver_017 | Summon Elemental | 3 | A | — | `summon_entity` (cap 1) | `self` |
| skill_weaver_018 | Elemental Ward | 3 | A | — | `grant_shield` · `apply_status`(`fortify`) | `party` |
| skill_weaver_019 | Mind Spike | 3 | A | `arcane` | `deal_damage` · `apply_status`(`silence`) | `projectile` |
| skill_weaver_020 | Elemental Cataclysm | 3 | A | `fire`/`frost`/`arcane` | `deal_damage`×3 · `apply_status`(`burn`,`chill`) | `aoe_circle` |
| skill_weaver_021 | Archmage's Mantle | 3 | P | — | `passive_stat_bonus`(`spellpower`,`essence`,`warding`) | `self` |

Elemental Cataclysm composes **three** `deal_damage` effects (one `fire`, one `frost`, one
`arcane`) executed in order — a single damage instance is one element
(`10_systems/SKILL_EFFECTS.md` composition), so the capstone stacks three instances, not a
multi-element instance.

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

| ID | Skill | Tier | T | Elem | Primary ops | Target |
|---|---|---|---|---|---|---|
| skill_flicker_001 | Twin Fangs | 1 | A | `neutral` | `deal_damage` (2 `hits`) | `melee_arc` |
| skill_flicker_002 | Shadowstep | 1 | A | — | `dash` (i-frames, behind target) | `self` |
| skill_flicker_003 | Throwing Dirk | 1 | A | `neutral` | `deal_damage` | `projectile` |
| skill_flicker_004 | Vanish | 1 | A | `shadow` | `apply_status`(`veil`) | `self` |
| skill_flicker_005 | Sleight | 1 | P | — | `passive_stat_bonus`(`crit_rate`,`evasion`) | `self` |
| skill_flicker_006 | Fortune's Favor | 1 | P | — | `passive_stat_bonus`(`fortune`) | `self` |
| skill_flicker_007 | Backstab | 2 | A | `neutral` | `deal_damage` (bonus vs `veil`ed/unaware) | `melee_arc` |
| skill_flicker_008 | Smoke Bomb | 2 | A | `shadow` | `apply_status`(`blind`) · `apply_status`(`veil`) | `aoe_circle` |
| skill_flicker_009 | Envenom | 2 | A | `nature` | `apply_status` (self) · `on_hit_proc`(→`poison`) | `self` |
| skill_flicker_010 | Shadow Flurry | 2 | A | `shadow` | `deal_damage` (multi-`hits`) | `melee_arc` |
| skill_flicker_011 | Shadowhook | 2 | A | `shadow` | `pull` (self→point) · `deal_damage` | `line` |
| skill_flicker_012 | Deadly Precision | 2 | P | — | `passive_stat_bonus`(`crit_power`) | `self` |
| skill_flicker_013 | Evasive Instinct | 2 | P | — | `on_hit_proc`(`on_dodge`→`swiftness`+`restore_essence`) | `self` |
| skill_flicker_014 | Assassinate | 3 | A | `neutral` | `deal_damage` (guaranteed crit, execute) | `melee_arc` |
| skill_flicker_015 | Shadow Clone | 3 | A | `shadow` | `summon_entity` (cap 2) | `self` |
| skill_flicker_016 | Bladedance | 3 | A | `neutral` | `dash` (chain) · `deal_damage` | `self` |
| skill_flicker_017 | Umbral Leap | 3 | A | `shadow` | `leap` · `deal_damage` · `apply_status`(`veil`) | `aoe_circle` |
| skill_flicker_018 | Cloak of Night | 3 | A | `shadow` | `apply_status`(`veil`) · `apply_status`(`swiftness`) | `party` |
| skill_flicker_019 | Deathmark | 3 | A | `shadow` | `apply_status`(`weaken`) · `on_hit_proc` | `projectile` |
| skill_flicker_020 | Vanishing Strike | 3 | A | `shadow` | `deal_damage` · `apply_status`(`veil`) | `melee_arc` |
| skill_flicker_021 | Lady Luck | 3 | P | — | `passive_stat_bonus`(`fortune`,`crit_power`) · `on_hit_proc`(`on_crit`→cooldown/`essence`) | `self` |

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

| Line | 1st (`001`–`006`) | 2nd (`007`–`013`) | Authored total (this arc) | 3rd (`014`–`021`, reserved) |
|---|---|---|---|---|
| `bulwark` | 4A / 2P | 5A / 2P | 13 | 6A / 2P (future) |
| `keeneye` | 4A / 2P | 5A / 2P | 13 | 7A / 1P (future) |
| `weaver` | 4A / 2P | 5A / 2P | 13 | 7A / 1P (future) |
| `flicker` | 4A / 2P | 5A / 2P | 13 | 7A / 1P (future) |

Every line hits **6 / 7** by authored tier — **52 line skills + 4 novice = 56 authored**
(`00_vision/SCOPE.md` v2). The reserved 3rd-tier plans keep each line's eventual 21-skill shape.
Across the 56 authored skills, all 14 effect ops (`10_systems/SKILL_EFFECTS.md`) and all 6
targeting shapes (`10_systems/SKILL_SYSTEM.md`) must appear at least once, so the roster
exercises the full primitive set (`00_vision/PILLARS.md` P4) without the 3rd tier.

## Open Questions

- The four line tokens (`bulwark`/`keeneye`/`weaver`/`flicker`), `novice`, and the twelve job
  names are proposed for `00_vision/GLOSSARY.md` promotion at the B gate (§0); until promoted they
  live here as their sole definition. Flag if any collides with a later-authored token.
- Job-trainer NPC IDs and the two advancement quest IDs per line are **Phase D** content
  (`10_systems/QUESTS.md`, `docs/ID_REGISTRY.md`); §1 fixes only the level gates (8/40) and the
  home-town pattern. Confirm each instructor NPC fits its home town's `npc` block when quests are
  authored.
- Whether a small `shards` cost or item gate should accompany the trainer quests (beyond the quest
  itself) is an `10_systems/ECONOMY.md`/`10_systems/QUESTS.md` call; default is quest-only.
- Prerequisite chains among a line's skills (e.g., an ultimate feeding off an earlier skill's rank)
  are owned by `10_systems/SKILL_SYSTEM.md`; the concrete prereq edges per skill are authored in
  Phase D skill YAML. This roster fixes tier order only.
- Summon caps here (`Falcon` 1, `Summon Elemental` 1, `Shadow Clone` 2) assume the
  `10_systems/SKILL_EFFECTS.md` / `20_schemas/monster.schema.md` cap of 1–2; confirm at the C gate.
- Balance of the `flicker`/`dirk` `fortune` double-dip inherits the open `10_systems/STATS.md` §2.1
  question; if a `power`-coefficient cut lands there, no name/roster change is needed here.
