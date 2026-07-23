# SKILL_EFFECTS.md — Effect-Op Registry (the 14 Skill Primitives)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md,
10_systems/ELEMENTS.md, 10_systems/STATUS_EFFECTS.md, 10_systems/COMBAT_FORMULA.md,
10_systems/SKILL_SYSTEM.md, 10_systems/JOBS.md, 10_systems/AI_BEHAVIOR.md,
10_systems/social/PARTY.md, 10_systems/PERSISTENCE.md, 20_schemas/monster.schema.md

Owner doc for the **14 skill effect ops** in `00_vision/GLOSSARY.md`. A skill (and a monster
ability, §17) is data: a targeting shape (`10_systems/SKILL_SYSTEM.md` §6) plus an **ordered list
of effects**, each effect one op below with parameters. This doc defines each op's parameter
schema, valid targets, stacking/composition, and which stat scales it. It does **not** define
element multipliers (`10_systems/ELEMENTS.md`), status behavior (`10_systems/STATUS_EFFECTS.md`),
the damage/hit/crit pipeline or size/i-frame rules (`10_systems/COMBAT_FORMULA.md`), stat formulas
(`10_systems/STATS.md`), `level_data` interpolation or targeting geometry
(`10_systems/SKILL_SYSTEM.md`). The op set is fixed at 14; adding one requires a GLOSSARY
Provisional entry.

## 1. The scaling rule (stated once — offense & support)

Every magnitude that reads an offensive rating uses **one** of `power` or `spellpower`, chosen by
the skill, defaulting to the caster's line weapon:

| Line / weapon (`10_systems/JOBS.md`) | Default scaling |
|---|---|
| `bulwark`/`blade`, `keeneye`/`bow`, `flicker`/`dirk` | `power` |
| `weaver`/`staff` (and any spell skill) | `spellpower` |

A skill may override with `scaling: power \| spellpower`. This is identical to
`10_systems/COMBAT_FORMULA.md` §5's offense selection and `10_systems/STATUS_EFFECTS.md` §1's
`source_power` — the same value, named once here for content. **Support** magnitudes (`heal`,
`grant_shield`) default to `spellpower` but may use `max_life` %-scaling for martial self-sustain
(§4). Monster abilities substitute the monster's equivalent rating
(`20_schemas/monster.schema.md`). Content and monster files **never restate** this rule.

## 2. Composition rules (how a skill's effects combine)

- **Ordered execution.** A skill's `effects: [...]` list runs **top to bottom** on activation.
  Order matters for reads: a `pull` before an `aoe_circle` `deal_damage` gathers targets first; a
  `deal_damage` before an `apply_status` lets the hit register before the debuff.
- **Per-effect target class.** The skill's targeting shape (`10_systems/SKILL_SYSTEM.md` §6)
  produces a candidate set; each effect applies to the candidates **of its class** — offensive ops
  (`deal_damage`, `knockback`, `pull`, `taunt`, hostile `apply_status`) hit hostiles; support ops
  (`heal`, `restore_essence`, `grant_shield`, buff `apply_status`, `cleanse_status`) affect
  self/allies; mover ops (`dash`, `leap`) affect the caster. So one skill may damage enemies in an
  arc **and** heal the caster — each effect filters the shape's candidates by class.
- **Conditionals only via `on_hit_proc`.** There is no `if/else` in skill data. Any triggered or
  conditional behavior is expressed as an `on_hit_proc` effect (§16) wrapping another op. This keeps
  skills declarative (`00_vision/PILLARS.md` P4/P5).
- **Snapshot timing.** Damage-dealt multipliers and DoT snapshots follow
  `10_systems/STATUS_EFFECTS.md` §1 and `10_systems/COMBAT_FORMULA.md` §4 — a scaling status
  snapshots `source_power`/`crit_power` at apply time.
- **Multiple same-op effects are allowed** (e.g., a two-element composite nuke listing a `fire`
  and a `frost` `deal_damage` back to back, extending the `deal_damage` · `apply_status` pattern
  of `skill_weaver_008 Frost Nova`, `10_systems/JOBS.md`); each resolves independently in order.

Ranges below are **first-pass authoring bounds**, not hard limits; per-rank numbers live in
`level_data` (`10_systems/SKILL_SYSTEM.md` §4). "tiles" = `40_assets/ART_BIBLE.yaml` grid unit.

## 3. `deal_damage`

Applies one damage instance through the full `10_systems/COMBAT_FORMULA.md` §2 pipeline.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `element` | enum | yes | GLOSSARY element | Picks `armor` vs `warding` mitigation & the affinity multiplier (`10_systems/ELEMENTS.md` §2–3). |
| `mult` | float | yes | 0.3–4.0 (basic attack = 1.0) | This is `skill.coefficient` in `10_systems/COMBAT_FORMULA.md` §2. |
| `hits` | int | no | 1–10, default 1 | Multi-hit; **each** hit is a separate pipeline call (own crit/variance roll). |
| `scaling` | enum | no | `power`\|`spellpower` (default §1) | Override the line default. |
| `can_crit` | bool | no | default true | false for fixed-damage utility hits. |

**Targets:** hostiles in the shape. **Stacking/composition:** independent per hit and per effect;
never self-inflicts. **Scales:** `power`/`spellpower` (§1). Element ×0 immunity short-circuits to 0
(`10_systems/COMBAT_FORMULA.md` §2 step 2); a landed non-immune hit is always ≥ 1.

## 4. `heal`

Restores `life` (`10_systems/STATS.md` §2). Distinct from the `regen` status (that is
`apply_status regen`).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `scaling` | enum | no | `spellpower`\|`power`\|`max_life`\|`flat` (default `spellpower`) | `max_life` = % of receiver's max `life` (martial self-heal). |
| `mult` | float | yes* | 0.2–4.0 (or 0.02–0.30 if `max_life`) | Heal = `scaling_stat × mult`; *`flat` uses `amount` instead. |
| `amount` | int | no | flat top-up | Used with `scaling: flat`. |
| `can_crit` | bool | no | default false | Crit heals off by default (P1 legibility). |

**Targets:** `self` / `party` allies. **Stacking:** additive with other heals; cannot exceed max
`life`. **Scales:** `spellpower` by default (caster identity); `max_life`% for non-casters.
Healer-output-vs-`spellpower` is flagged in `10_systems/STATUS_EFFECTS.md`'s heal-scaling Open
Question — this op supports both modes so that resolution needs no schema change.

## 5. `restore_essence`

Restores the `essence` pool (`10_systems/STATS.md` §2).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `amount` | int | no | flat | One of `amount`/`pct` required. |
| `pct` | float | no | 0.02–0.30 of max `essence` | Percentage restore. |
| `target` | enum | no | `self`\|`party` (default `self`) | |

**Targets:** `self`/`party`. **Stacking:** additive; capped at max `essence`. **Scales:** flat/%
(not an offense stat). Common as an `on_hit_proc` payload (crit → refund, `10_systems/JOBS.md`
`skill_keeneye_013`, `skill_weaver_006`).

## 6. `grant_shield`

Grants a temporary absorb pool that soaks incoming damage **after** it is fully computed
(post-mitigation, post-element) by `10_systems/COMBAT_FORMULA.md` §2, before it reduces `life`.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `scaling` | enum | no | `spellpower`\|`max_life`\|`flat` (default `spellpower`) | |
| `mult` | float | yes* | 0.5–6.0 (or 0.05–0.40 if `max_life`) | Shield amount = `scaling_stat × mult`; *`flat` uses `amount`. |
| `amount` | int | no | flat | With `scaling: flat`. |
| `dur` | float s | yes | 3–20 | Unabsorbed shield expires. |

**Targets:** `self`/`party`. **Stacking:** multiple shields coexist and are consumed
**oldest-first**; each has its own `dur`. Shields absorb any element (no per-element shields —
`10_systems/ELEMENTS.md` §3 keeps defense to `armor`/`warding`). **Scales:** `spellpower`/`max_life`.

## 7. `knockback`

Displaces a hostile away. `10_systems/COMBAT_FORMULA.md` §11 owns the heavy-hit class, the
size-class scaling table, and hitstun; this op declares **intent + base displacement** only.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `distance` | float tiles | yes | 0.5–5 | Base horizontal impulse before size scaling (`10_systems/COMBAT_FORMULA.md` §11). |
| `vertical` | float tiles | no | 0–3, default 0 | Pop-up component. |
| `direction` | enum | no | `away_from_source`\|`facing`\|`toward_point` (default `away_from_source`) | |

**Targets:** hostiles. **Composition:** carrying this op flags the hit **heavy**
(`10_systems/COMBAT_FORMULA.md` §11); `boss`-size targets are knockback-immune there. **Scales:**
displacement by target size class (that doc), not by an offense stat.

## 8. `pull`

Mirror of `knockback`: draws a hostile toward the caster/point, **or** pulls the **caster** to a
point (gap-closer / grapple, e.g. `skill_flicker_011`).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `distance` | float tiles | no | 1–8 | Displacement; omit if `to_point`. |
| `to_point` | bool | no | default false | Pull fully to the caster (enemy mode) or to the target point (self mode). |
| `target_mode` | enum | no | `enemy`\|`self` (default `enemy`) | `self` = pull the caster (mobility). |
| `vertical` | float tiles | no | 0–3 | |

**Targets:** hostiles (`enemy`) or caster (`self`). **Composition:** size-scaled like `knockback`
(`10_systems/COMBAT_FORMULA.md` §11); pairs before `aoe_circle` `deal_damage` to gather. **Scales:**
by size class.

## 9. `dash`

A fast, mostly-horizontal caster reposition (ground or air).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `distance` | float tiles | yes | 2–8 | |
| `direction` | enum | no | `facing`\|`input`\|`toward_target`\|`backward` (default `facing`) | |
| `iframes` | bool | no | default false | If true, grants i-frames for the dash (`10_systems/COMBAT_FORMULA.md` §12). |
| `iframe_dur` | float s | no | default = §12 window (0.40 s) | Override i-frame length. |
| `through_enemies` | bool | no | default false | Pass through hostiles (e.g. `skill_flicker_002` behind-target). |

**Targets:** `self`. **Composition:** may chain into a `deal_damage` (blink-strike). **Scales:**
distance is flat (not stat-scaled). i-frame rules are `10_systems/COMBAT_FORMULA.md` §12's.

## 10. `leap`

A ballistic arc to a location — the vertical mover (platformer jumps/slams), distinct from ground
`dash`.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `distance` | float tiles | yes | 3–10 | Horizontal reach to the landing point. |
| `height` | float tiles | no | 2–6 | Arc apex. |
| `target` | enum | no | `point`\|`self_arc` (default `point`) | `point` = ground-targeted landing. |
| `iframes` | bool | no | default false | Airborne i-frames if true (`10_systems/COMBAT_FORMULA.md` §12). |

**Targets:** `self`. **Composition:** landing effects are the *next* effects in the list (a
`leap` then `aoe_circle` `deal_damage` = slam — the airborne cousin of
`skill_bulwark_008 Ground Slam`, `10_systems/JOBS.md`). **Scales:** flat.

## 11. `taunt`

Forces AI-driven monsters to target the caster (`10_systems/AI_BEHAVIOR.md` owns aggro; this op
sets a forced-target override for a duration).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `dur` | float s | yes | 2–8 | Forced-target duration. |
| `radius` | float tiles | no | for `aoe_circle` taunts (0 = single target) | Area taunt (e.g. `skill_bulwark_002`). |

**Targets:** hostiles (AI monsters only). **Composition:** honored per `10_systems/AI_BEHAVIOR.md`;
`boss`/`boss_scripted` entities may flag **taunt-immune** in `20_schemas/monster.schema.md`
(consistent with their CC immunity, `10_systems/STATUS_EFFECTS.md` §3). No PvP in scope, so `taunt`
never targets players. **Scales:** none (duration is flat/`level_data`).

## 12. `summon_entity`

Spawns a temporary ally that is itself a **monster-schema entity** (`20_schemas/monster.schema.md`)
tagged with an `owner`.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `entity_ref` | id | yes | a summon template / `mob_NNN` (`20_schemas/monster.schema.md`) | The summoned entity's data. |
| `count` | int | no | **1–2**, default 1 | Concurrent cap per summoning skill. |
| `dur` | float s | no | 8–60, or `until_death` | Despawn timer. |
| `inherit_scaling` | enum | no | `spellpower`\|`power`\|`level` (default per §1) | How the summon's offense scales off the summoner. |

**Targets:** `self` (spawns near caster). **Constraints:** summons are full monster-schema entities
with an `owner` tag and an AI profile (`10_systems/AI_BEHAVIOR.md`); the **cap is 1–2** concurrent
per summoning skill — casting again beyond the cap **replaces the oldest**. Summons persist off the
skill bar (`10_systems/SKILL_SYSTEM.md` §7). Their own abilities use this same op registry (§17).
**Scales:** the summon inherits an offense rating from the summoner (`inherit_scaling`).

## 13. `passive_stat_bonus`

An always-on stat modifier from a learned **passive** (`10_systems/JOBS.md` marks passives;
`10_systems/SKILL_SYSTEM.md` §7 — passives are never slotted).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `stats` | map | yes | `{<GLOSSARY stat>: value}` | Each value flat or `pct` (see `mode`). Stat tokens from `10_systems/STATS.md`. |
| `mode` | enum | no | `flat`\|`pct` (default `flat`) | Per-entry mode may be given as `{value, mode}`. |
| `scope` | enum | no | `self`\|`party_aura` (default `self`) | `party_aura` grants to nearby party (`10_systems/social/PARTY.md`). |
| `condition` | enum | no | e.g. `while_veiled`, `below_life_pct:X`, `while_stance` | Optional gate; the bonus applies only while true. |

**Targets:** `self` (or party for auras). **Stacking:** multiple passives **add**; folded into the
`10_systems/STATS.md` §7 compute order exactly like gear — flat primary bonuses at step 1, flat/pct
derived at step 2/3, then §6 soft/hard caps apply. **Scales:** it *is* the stat source; it does not
scale on another stat. Conditional passives evaluate live each recompute.

## 14. `apply_status`

Applies a GLOSSARY status (`10_systems/STATUS_EFFECTS.md`, which owns duration, stacking, DR, tier
scaling, cleanse tag, `source_power` snapshot). This op only **applies** — it invents no behavior.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `status` | enum | yes | GLOSSARY status | Debuff → hostiles; buff → self/allies. |
| `chance` | float | yes | 0.0–1.0 | Application probability (per target, per hit). |
| `dur` | float s | no | override; default = `10_systems/STATUS_EFFECTS.md` §4 base | Tier scaling still applies (that doc §3). |
| `magnitude` | float | no | for scaling statuses (`sunder` stacks, DoT %) | Default = `10_systems/STATUS_EFFECTS.md` base; snapshots per §1 there. |
| `element` | enum | no | flavor for pairing/mitigation of the *status's* damage | Default = the §5 guideline element; may differ (`10_systems/ELEMENTS.md` §5 loose). |
| `stacks` | int | no | for `stack`-type statuses (`burn`/`poison`/`sunder`) | Bounded by that status's cap. |

**Targets:** hostiles (debuffs) / self/allies (buffs), per the status. **Stacking/DR/caps:** owned
entirely by `10_systems/STATUS_EFFECTS.md` (§1 hard-CC DR, §3 tier scaling, per-status stacking).
**Scales:** magnitudes that read `source_power` use §1's rating; snapshot at apply time.

## 15. `cleanse_status`

Removes active **debuffs** carrying a cleanse tag (`10_systems/STATUS_EFFECTS.md` §2 owns the tag
set; tags are GLOSSARY Provisional).

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `tag` | enum | yes | `burn_type`\|`poison_type`\|`chill_type`\|`control_type`\|`sense_type`\|`curse_type` | Removes every active status with the tag. |
| `count` | int | no | default `all` | Cap how many are removed. |
| `target` | enum | no | `self`\|`party` (default `self`) | Allies only. |

**Targets:** `self`/`party`. **Composition:** buffs carry no cleanse tag and are **not** removable
by this op (`10_systems/STATUS_EFFECTS.md` §2/§4 — no player buff-purge; a monster purge is that
doc's Open Question). **Scales:** none.

## 16. `on_hit_proc`

The **only** conditional primitive: wraps another op that fires when a trigger condition is met.
Used by passives (thorns, lifesteal, crit-refund) and by actives that grant a proc for a duration.

| Param | Type | Req | Range / default | Notes |
|---|---|---|---|---|
| `trigger` | enum | yes | `on_deal`\|`on_take`\|`on_crit`\|`on_kill`\|`on_dodge`\|`on_cast` | The hook event. |
| `chance` | float | no | 0.0–1.0, default 1.0 | Proc probability. |
| `effect` | op | yes | any of §3–§15 (**not** another `on_hit_proc`) | The payload; nesting depth = 1 (no recursion). |
| `icd` | float s | no | internal cooldown | Rate-limits high-frequency triggers (`10_systems/SKILL_SYSTEM.md` §5). |
| `condition` | enum | no | e.g. `below_life_pct:X`, `vs_marked`, `while_veiled` | Optional gate on top of the trigger. |

**Targets:** inherited from the wrapped `effect`'s class (payload `deal_damage` → the triggering
hostile; payload `heal`/`restore_essence` → the caster). **Composition:** the sole branching
mechanism (§2); `on_deal` = the payload fires when the owner lands a hit (lifesteal, e.g.
`skill_bulwark_012`), `on_take` = when the owner is hit (thorns),
`on_crit`/`on_kill`/`on_dodge`/`on_cast` as named.
**Scales:** the wrapped op's rule (§1 if it deals damage).

## 17. Monster abilities reuse this registry

Elite and boss abilities in `20_schemas/monster.schema.md` are authored with the **same shape** —
a targeting shape plus an ordered `effects: [...]` list drawn from these 14 ops — substituting the
monster's offense rating (§1) and its `ai_profile` (`10_systems/AI_BEHAVIOR.md`) for pacing/
telegraphs. A boss's scripted slam is a `leap`+`aoe_circle` `deal_damage`+`apply_status(stun)`, an
airborne `skill_bulwark_008 Ground Slam`; a caster mob's nuke is a `projectile` `deal_damage` like
`skill_weaver_001`. There is **no separate monster-ability op set** (`00_vision/PILLARS.md` P4,
compose-don't-enumerate). Tier-based CC/knockback resistance and `phase_shift`/`die` interactions
apply to monster-applied effects exactly as authored in `10_systems/STATUS_EFFECTS.md` §1/§3 and
`10_systems/COMBAT_FORMULA.md` §11.

## 18. Authority

All op resolution — damage, status application, summon spawning, proc evaluation — is
**server-authoritative** in the live build (`00_vision/PILLARS.md` P6; `10_systems/PERSISTENCE.md`).
The solo client simulates effects and may be corrected on sync; no content file recomputes op math,
it only declares ops and parameters.

## Open Questions

- **Heal/shield scaling default** (`spellpower`) intersects `10_systems/STATUS_EFFECTS.md`'s
  heal-scaling Open Question (should healer output scale on applier `spellpower`?). This op already
  supports `spellpower`/`max_life`/`flat`, so either resolution is expressible; owner call sits with
  `10_systems/COMBAT_FORMULA.md`.
- **`grant_shield` absorb ordering** (oldest-first, post-mitigation) is first-pass; if a
  largest-first or pre-mitigation model is wanted for a specific boss mechanic, flag to
  `10_systems/COMBAT_FORMULA.md`. Default holds.
- **`summon_entity` cap (1–2)** and whether summons count against the caster's status/aggro budgets
  are joint calls with `20_schemas/monster.schema.md` / `10_systems/AI_BEHAVIOR.md`; confirm at the
  C gate.
- **`on_hit_proc` trigger set** (`on_deal`/`on_take`/`on_crit`/`on_kill`/`on_dodge`/`on_cast`) is
  the current vocabulary; if a passive design needs another hook (e.g. `on_status_applied`), add it
  here rather than inventing a new op. Flagged.
- **`taunt` immunity flag** for `boss` entities lives in `20_schemas/monster.schema.md`;
  confirm the flag name when that schema is authored (default: bosses taunt-immune, matching CC
  immunity).
- **`condition` enum** for `passive_stat_bonus`/`on_hit_proc` (`below_life_pct`, `while_veiled`,
  `vs_marked`, …) is open-ended; the concrete list should be frozen at the C gate so
  `docs/VALIDATION.md` can enum-check it. Until then, authors use only the examples named here.
