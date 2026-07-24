# COMBO_SYSTEM.md — Combo Momentum & Combo Burst (Skill-Chaining Layer)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/SKILL_SYSTEM.md,
10_systems/SKILL_EFFECTS.md, 10_systems/COMBAT_FORMULA.md, 10_systems/STATUS_EFFECTS.md,
10_systems/STATS.md, 10_systems/JOBS.md, 10_systems/CONTROLS.md, 10_systems/HUD.md,
10_systems/PERSISTENCE.md

Owner doc for the **combo layer**: the chain state machine (`combo_momentum`), its sustained
damage bonus, and the `combo_burst` finisher reward for weaving the basic attack together with
distinct offensive skills. This is the "play the kit, not one button" system: alternating your
damage sources within a rhythm window pays measurably more sustained damage than mashing a
single input. It does **not** own skill acquisition/targeting (`10_systems/SKILL_SYSTEM.md`),
effect ops (`10_systems/SKILL_EFFECTS.md`), the damage pipeline (`10_systems/COMBAT_FORMULA.md` —
which consumes this doc's multiplier at its step 8), status semantics
(`10_systems/STATUS_EFFECTS.md`), or input bindings (`10_systems/CONTROLS.md` §3.1). It consumes
those and never restates them.

## 1. Design intent (`00_vision/PILLARS.md` P1/P4)

- **Depth without new buttons.** A combo is nothing but the inputs the player already has —
  basic attack and the slotted actives — pressed in *sequence* within a window
  (`10_systems/CONTROLS.md` §3.1). No chord bindings, no separate combo resource, no new ops.
- **Reward variety, don't punish simplicity.** A player who ignores combos still clears at-level
  content inside the `10_systems/COMBAT_FORMULA.md` §14 TTK bands; an active chainer earns up to
  ≈15% more sustained damage (§4) — a meaningful damage-per-minute edge, never a hard gate.
- **Asymmetric, player-only.** Monsters have no combo layer (the same asymmetry as i-frames,
  `10_systems/COMBAT_FORMULA.md` §12). `combo_momentum` is **not a status**: it never occupies
  the `10_systems/STATUS_EFFECTS.md` §1 12-slot cap, has no icon in the HUD status row, and
  cannot be cleansed or dispelled — it is combat-rhythm state, not a buff.

## 2. Chain state machine (`combo_momentum`)

Every player character carries one chain counter (**links**). A **source** is either the basic
attack (one source) or one specific active skill; only actives that carry a `deal_damage` op
(`10_systems/SKILL_EFFECTS.md` §3) are chain-eligible.

1. **A link lands** when a chain-eligible source deals a landed, non-`immune` damage instance
   (`10_systems/COMBAT_FORMULA.md` §2 steps 1–2). For a multi-hit or multi-target cast, only the
   **first** landed instance of that cast counts toward the chain; the rest refresh the window
   (rule 3) but add nothing — an `aoe_circle` clearing a pack is one link, not eight.
2. **The counter grows only on a source change.** A link whose source differs from the
   immediately previous link's source adds +1; a same-source link refreshes the window but does
   not grow the chain. Mashing basic attack or one skill therefore holds the chain at 1 link
   forever — alternation is the whole game.
3. **Chain window: 3.0 s.** Measured from the last landed damage instance (any chain-eligible
   source, growing or not). If it expires, the chain resets to 0. Support/mobility casts, item
   use, dodging, and *taking* damage are neutral — they neither grow, refresh, nor break the
   chain. Death and map transfer reset it (`10_systems/PERSISTENCE.md` — chain state is
   transient, never persisted).
4. **What never links:** DoT ticks (`burn`/`poison` — they also carry the momentum snapshotted at
   application, per `10_systems/STATUS_EFFECTS.md` §1's snapshot rule), `on_hit_proc` extra
   damage, summoned entities' damage (`summon_entity` acts independently, first-pass — Open
   Questions), and touch/reflect damage. Misses and immunes neither grow nor refresh.

## 3. `combo_momentum` — the sustained bonus

The chain length maps to a **damage-dealt multiplier** on the player's outgoing damage,
consumed by `10_systems/COMBAT_FORMULA.md` §2 step 8 alongside `empower`/`weaken` (its §8 owns
the fold; this doc owns the magnitudes):

| Links | Momentum tier | `combo_momentum` mult |
|---|---|---|
| 0–2 | — | ×1.00 |
| 3–5 | I | ×1.05 |
| 6–9 | II | ×1.10 |
| 10+ | III | ×1.15 (cap) |

- **Job-tier gate (advancement matters).** The chain *counts* links without limit at any job,
  but the reachable momentum tier is capped by advancement (`10_systems/JOBS.md` §1): `novice`
  caps at tier I, a 1st-job character at tier II, a specialized (2nd-advancement) character at
  tier III. The 3rd tier's cap is reserved with the rest of that arc (Open Questions).
- Applies to every outgoing damage instance while active — basic attacks, actives, and (via the
  snapshot rule, §2.4) DoTs applied while it was up. It multiplies **per instance**, so
  multi-target skills benefit on every target they hit — chaining into an `aoe_circle` or
  `melee_arc` sweep is the payoff moment for the lines that carry them
  (`10_systems/JOBS.md` §7.1 coverage — deliberately not every spec).

## 4. `combo_burst` — the finisher reward

When **three consecutive links** are three **distinct** sources of which at least two are
active skills — the canonical read: basic attack → offensive skill A → offensive skill B, one
fluid sequence (`10_systems/CONTROLS.md` §3.1's example) — the third link **bursts**:

- **Every damage instance of the bursting cast** is multiplied ×**1.25** (a burst on an
  `aoe_circle` finisher bursts on every target — the multi-target finisher fantasy where the
  roster supports it).
- The caster refunds **5% of max `essence`** (a flat resource kickback, not an effect op — no
  `restore_essence` skill line is involved and nothing here touches
  `10_systems/SKILL_EFFECTS.md`'s op table).
- **Internal cooldown: 8 s.** A burst is a rhythm reward roughly once per rotation, not a
  constant multiplier; the chain keeps growing normally while the burst is on cooldown.
- Burst requires two distinct offensive actives, so it is naturally unreachable during `novice`
  (whose kit carries one damage active, `10_systems/JOBS.md` §6) and unlocks organically with
  the 1st-job kit — no separate gate needed.

Worked sustained math (design envelope, not a formula content copies): tier III momentum
(×1.15) plus an amortized burst (×1.25 on ≈1 cast per 8 s ≈ +3% sustained) lands the full combo
layer at ≈**+15–18% sustained damage** versus a non-chaining player. That whole envelope is
budgeted **inside** `10_systems/COMBAT_FORMULA.md` §15's rotation factor `mult m` — a
non-comboer at-level clears a normal mob in ≈5.2 s, still inside the §14 3–6 s band; combos are
the edge, never the entry fee (P2).

## 5. Feedback & authority

- **HUD.** The link counter, momentum tier, and burst flash are drawn by `10_systems/HUD.md`
  §7.1 (that doc owns what is drawn and where; this doc owns the state it reflects).
- **Server-authoritative.** Chain state, momentum tier, burst eligibility, and the `essence`
  refund resolve server-side in the live build and are client-predicted like the rest of combat
  (`00_vision/PILLARS.md` P6; `10_systems/PERSISTENCE.md`;
  `70_integrations/GAMEPLAY_SIMULATION.md` §5 consumes the multiplier through the ordinary
  step-8 fold). The solo client simulates identically.

## Open Questions

- **Numbers are first-pass.** The 3.0 s window, tier thresholds (3/6/10), tier multipliers
  (×1.05/1.10/1.15), burst ×1.25, 5% `essence` refund, and 8 s burst ICD are design-envelope
  values; the balance pass retunes them against `10_systems/COMBAT_FORMULA.md` §15's `mult m`
  (which now names the combo layer as one of its components) — retune magnitudes, never the §14
  TTK bands.
- **3rd-tier momentum cap** (a tier IV, e.g. ×1.20, or simply tier III retained) is reserved
  for the future 3rd-job arc alongside `skill_<line>_028`–`045`; decide with that arc's kit
  design (`10_systems/JOBS.md` Open Questions).
- **Summon interaction** (§2.4): summoned entities currently neither grow nor benefit from the
  owner's chain. If playtesting makes summon specs (Pathstalker's Falcon, Warcaller's Standard)
  feel excluded, revisit jointly with `10_systems/SKILL_EFFECTS.md` §11.
- **Party visibility:** whether other party members' combo counters are ever shown (or a future
  co-op combo mechanic exists) is deferred with the rest of the server-deferred social layer
  (`10_systems/social/PARTY.md`); the layer is strictly personal at launch.
- Whether the Lv 40 specialization trial's gauntlet keeps its tier-II demonstration requirement
  (`10_systems/JOBS.md` §1.1) after the balance pass tunes the thresholds above — the trial must
  stay clearable by any 1st-job kit.
- Combo-counter accessibility (reduced motion / disable flash) belongs with
  `40_assets/UI_ART_SPEC.md`'s Phase C amendment channel; flagged, not specified here.
