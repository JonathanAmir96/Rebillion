# STATUS_EFFECTS.md — Status Effect Registry

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md,
10_systems/ELEMENTS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/SKILL_EFFECTS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/social/PARTY.md,
20_schemas/monster.schema.md, 40_assets/ANIMATION_STATES.md, docs/ID_REGISTRY.md,
docs/WORLD_PLAN.md

Owner doc for the 16 statuses in `00_vision/GLOSSARY.md` (10 debuffs, 6 buffs). Defines each
one's effect, magnitude, duration, stacking, cleanse tag, and boss handling, plus the global
rules that apply to all of them. Statuses are applied/removed by the `apply_status` /
`cleanse_status` effect ops (`10_systems/SKILL_EFFECTS.md`). The set is fixed at these 16; adding
or renaming requires a GLOSSARY Provisional entry.

## 1. Global rules (stated once)

**`source_power`.** Magnitudes written as "% of `source_power`" read the offensive rating the
applying skill scales on — `power` for physical/`neutral` skills, `spellpower` for magic skills
(the skill declares which; `10_systems/SKILL_SYSTEM.md`). Monster-applied statuses use the
monster's equivalent rating (`20_schemas/monster.schema.md`).

**Damage-over-time is snapshot, not dynamic.** When a scaling status (any DoT, and any
magnitude that reads `source_power`) is applied, it **snapshots** the applier's `source_power`
and `crit_power` at application time; every tick uses that snapshot even if the applier's stats,
buffs, or weapon change afterward. Refreshing a status re-snapshots. Each independent stack
carries its own snapshot. Exception: `regen` reads the **receiver's** current max `life` live
(§4), since it is a heal, not a snapshotted hit.

**Max simultaneous statuses per entity: 12** (buffs + debuffs combined; tuned to the HUD icon
budget, `40_assets/UI_ART_SPEC.md`). If a 13th would apply, the active status with the least
remaining duration is dropped to admit it (ties: oldest applied). Scripted boss statuses may be
flagged non-displaceable in the monster/AI data.

**Reapplication.** Governed per status by its stacking rule (below): `unique` (refresh
duration), `stack` (independent stacks up to a cap), or `refresh` (extend/replace). On top of
that, **hard control has diminishing returns (DR)** on a single target: the 1st `stun`/`freeze`
lands full, a 2nd within 10 s lands at 50% duration, and a 3rd within the window grants
**CC-immunity for 8 s** (no further hard CC). Soft CC (`chill`, `root`, `silence`, `blind`) has
no immunity DR — it simply refreshes and is duration-limited by tier (§3).

**`die` / `phase_shift` interaction** (`40_assets/ANIMATION_STATES.md`):
- On entering `die`, **all** statuses (buffs and debuffs) are cleared immediately; a queued DoT
  tick may not fire after death — no post-mortem ticks, no kill-then-tick.
- While a boss is in `phase_shift`, it accepts **no new** status applications and all existing
  DoT timers and CC are **suspended** (timers pause, no ticks) until the state ends. Bosses are
  invulnerable/untargetable during `phase_shift` by convention, so this prevents free damage or
  control through a transition (`00_vision/PILLARS.md` P1 fairness).

## 2. Cleanse tags

Each debuff carries one or two **cleanse tags**. A `cleanse_status(tag)` op
(`10_systems/SKILL_EFFECTS.md`) or a cleanse item removes every active status carrying that tag.
Buffs carry no cleanse tag (they are not player-cleansable; see §4). Tags are proposed GLOSSARY
Provisional tokens — see Open Questions.

| Cleanse tag | Statuses carrying it | Canonical remover |
|---|---|---|
| `burn_type` | `burn` | fire-cleanse skills |
| `poison_type` | `poison` | Antidote (`item_use_0011`, `docs/ID_REGISTRY.md`) |
| `chill_type` | `chill`, `freeze` | Thaw Salve (`item_use_0012`) |
| `control_type` | `stun`, `root`, `freeze` | break-control skills |
| `sense_type` | `blind`, `silence` | `clarity` buff (§4), cleanse skills |
| `curse_type` | `sunder`, `weaken` | dispel skills |

`freeze` intentionally carries both `chill_type` and `control_type`, so Thaw Salve (ice) and a
generic break-control both free it.

## 3. Control resistance by entity tier (boss rule)

Every debuff has an **effect class** (column in §5). Duration/magnitude is scaled by the target's
tier (`normal` · `elite` · `boss`, `20_schemas/monster.schema.md`):

| Effect class | `normal` | `elite` | `boss` |
|---|---|---|---|
| Hard CC (`stun`, `freeze`) | 100% | 50% duration | **immune** |
| Soft CC (`chill`, `root`, `silence`, `blind`) | 100% | 75% duration | 30% duration |
| Damage debuff (`sunder`, `weaken`) | 100% | 100% | 50% magnitude |
| DoT (`burn`, `poison`) | 100% | 100% | 100% |

The 8 region bosses and the two party-quest finale bosses (`docs/WORLD_PLAN.md`;
`10_systems/social/PARTY_QUEST.md`) may flag **immune to all CC**, hard and soft, in their
`20_schemas/monster.schema.md` data (a per-boss/per-phase choice, e.g. an enrage phase); DoTs and
damage debuffs still apply at the `boss` row. There is no raid tier (Decision Contract C9).
`10_systems/COMBAT_FORMULA.md` may override per-boss values.

## 4. Registry — the 16 statuses

Durations/cadences are first-pass balance defaults (base, pre-tier-scaling). "Class" maps to §3.

### 4.1 Debuffs (10)

| Status | Element | Class | Effect & magnitude | Duration · cadence | Stacking | Cleanse |
|---|---|---|---|---|---|---|
| `burn` | `fire` | DoT | Deals **8% of `source_power`** as `fire` damage per tick | 6 s · tick 1 s | `stack`, cap 5 (own snapshot each) | `burn_type` |
| `poison` | `nature` | DoT | Deals **6% of `source_power`** as `nature` damage per tick | 10 s · tick 1 s | `stack`, cap 5 | `poison_type` |
| `chill` | `frost` | Soft CC | Slow: **−30%** move-speed and **−15%** attack-speed output | 4 s · continuous | `unique` (refresh) | `chill_type` |
| `freeze` | `frost` | Hard CC | Frozen solid — cannot act or move | 2 s | `unique` (+ hard-CC DR, §1) | `chill_type`, `control_type` |
| `stun` | `neutral` | Hard CC | Staggered — cannot act or move | 1.5 s | `unique` (+ hard-CC DR) | `control_type` |
| `root` | `nature` | Soft CC | Cannot move; may still act (cast/attack in place) | 3 s | `unique` (refresh) | `control_type` |
| `silence` | `shadow` | Soft CC | Cannot use skills; may move and basic-attack | 3 s | `unique` (refresh) | `sense_type` |
| `blind` | `arcane` | Soft CC | The blinded entity's attacks suffer **+50% miss** (accuracy loss) | 4 s | `unique` (refresh) | `sense_type` |
| `sunder` | `neutral` | Damage debuff | Target `armor` **−20% per stack** | 8 s · refresh all on apply | `stack`, cap 3 (−60% max) | `curse_type` |
| `weaken` | `shadow` | Damage debuff | Target deals **−25%** damage | 6 s | `unique` (refresh) | `curse_type` |

Notes:
- `blind`'s "+50% miss" is expressed to `10_systems/COMBAT_FORMULA.md` as an accuracy penalty on
  the blinded entity's hit resolution; this doc owns the magnitude, COMBAT_FORMULA owns the roll.
- `chill` modifies the target's `haste` outputs (`10_systems/STATS.md` §5); `sunder` modifies
  `armor` (STATS §2). Both feed back through the normal compute order (STATS §7 step 4).
- `chill` → `freeze` is a thematic escalation, not an automatic combo; a skill must apply
  `freeze` explicitly (no hidden state, P1).
- Element column is the **typical** element per `10_systems/ELEMENTS.md` §5 pairing (guideline);
  a skill may apply a debuff under a different element.

### 4.2 Buffs (6)

| Status | Effect & magnitude | Duration · cadence | Stacking |
|---|---|---|---|
| `empower` | **+20%** damage dealt | 10 s | `unique` (refresh) |
| `fortify` | **+25%** `armor` and `warding` | 10 s | `unique` (refresh) |
| `swiftness` | **+20%** move-speed and **+15%** attack-speed output (re-clamped to STATS §6 hard caps) | 10 s | `unique` (refresh) |
| `regen` | Heals **3% of receiver max `life`** per tick | 10 s · tick 1 s | `unique` (refresh) |
| `clarity` | Cleanses `sense_type` on apply and grants **immunity to `sense_type`** (`blind`/`silence`) for the duration; **−15%** `essence` skill costs | 8 s | `unique` (refresh) |
| `veil` | Stealth: untargetable by monster AI and hidden until the veiled entity takes an offensive action or the duration ends | 6 s | `unique` |

Notes:
- Buffs are **not** player-cleansable and carry no cleanse tag; they expire on their timer or are
  removed by a monster **dispel/purge** mechanic (whether such an op exists is an Open Question).
- `swiftness` adds to the `haste`-derived percentages and is re-clamped by the STATS §6 hard caps
  (it cannot push attack-speed past +75%).
- `regen` is the one dynamic (non-snapshot) status — it reads the receiver's live max `life` each
  tick (§1), so it scales correctly if max `life` changes mid-effect.
- `veil` is pierced by `arcane` sources (`10_systems/ELEMENTS.md` §5): an `arcane` attack or an
  `arcane`-flagged monster senses and can target a veiled entity; taking any offensive action
  also breaks `veil`.
- `clarity`'s `essence`-cost reduction applies to `restore_essence`-relevant skill costs at cast
  time (`10_systems/SKILL_SYSTEM.md` owns cost resolution).

## 5. Application & authority

Statuses are applied only via `apply_status` and removed via `cleanse_status`
(`10_systems/SKILL_EFFECTS.md`); no other system invents status transitions. All timers, ticks,
stacking, DR, and tier scaling are **server-authoritative** in the live build
(`00_vision/PILLARS.md` P6; contract in `10_systems/PERSISTENCE.md`) — the solo client simulates
them but the server is the source of truth on sync. Damage from DoTs and the effect of stat
debuffs flow through the normal damage/compute pipeline (`10_systems/COMBAT_FORMULA.md`,
`10_systems/STATS.md`), so element multipliers (`10_systems/ELEMENTS.md` §2) and mitigation
apply to DoT ticks exactly as to direct hits.

## Open Questions

- Cleanse-group tags (`burn_type`, `poison_type`, `chill_type`, `control_type`, `sense_type`,
  `curse_type`) are **new classification tokens** referenced by the `cleanse_status` op, item
  files, and skill data. Propose promoting them to `00_vision/GLOSSARY.md` Provisional at the B
  gate; until then they live here as the sole definition.
- Buff removal: is a monster **dispel/purge** op needed? `00_vision/GLOSSARY.md`'s skill-effect
  ops have no `purge`. Default: buffs only expire (no purge); flag if a boss design needs to strip
  player buffs. Owner: `10_systems/SKILL_EFFECTS.md`.
- Hard-CC DR window (10 s) and immunity duration (8 s) are first-pass; may need tuning against real
  boss encounters. Owner: `10_systems/COMBAT_FORMULA.md`.
- Whether a given boss/phase uses full CC-immunity or the `boss` soft-CC row is a per-boss
  `20_schemas/monster.schema.md` flag; confirm the finale-boss choices with
  `10_systems/social/PARTY_QUEST.md` (Agent C).
- Max simultaneous statuses (12) is tied to the HUD icon budget; confirm against
  `40_assets/UI_ART_SPEC.md` when the HUD is specced.
- `regen` and healing scaling: currently % of receiver max `life`; if healer output should scale
  on the applier's `spellpower` instead, that is a `10_systems/COMBAT_FORMULA.md` decision.
