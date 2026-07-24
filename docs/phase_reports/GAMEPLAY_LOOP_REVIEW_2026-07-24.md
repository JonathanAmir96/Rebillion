# GAMEPLAY_LOOP_REVIEW_2026-07-24.md — Critical Review of the Core Gameplay Loop

Scope: a critical read of the core loop and its mechanics as authored on `main` as of
2026-07-24 — the hunt → loot → level → advance → travel cycle and the moment-to-moment combat
contract. Sources read in full: `00_vision/*`, `10_systems/LEVELING.md`, `COMBAT_FORMULA.md`,
`SKILL_SYSTEM.md`, `STATS.md`, `JOBS.md`, `DROPS.md`, `ECONOMY.md`, `QUESTS.md`,
`DEATH_PENALTY.md`, `SPAWN.md`, `HUD.md`, `CONTROLS.md`, `CAMERA.md`, `ONBOARDING_FTUE.md`,
`15_maps_system/MAP_TRAVERSAL.md`, `MAP_LAYERS.md`, `40_assets/UI_ART_SPEC.md`,
`docs/WORLD_PLAN.md`, `docs/VALIDATION.md`. This report proposes nothing into owning docs — every
finding names its owner and lands there via that doc's Open Questions channel, per CLAUDE.md law 4.

A companion visual mock-up of the main gameplay scene (field play + HUD, plus the boss-arena
variant and the depth-layer stack) is at `docs/mockups/gameplay_scene_mockup.html`.

## 1. What holds up well

Credit first, because the tree earns it:

- **Ownership discipline is real.** Rules genuinely live in one place; consumers cite instead of
  restating. The `exp_to_next = exp_per_kill × kills_per_level` coupling (LEVELING §1) tied to the
  TTK contract (COMBAT_FORMULA §14) is the strongest piece of design in the tree — pacing, reward,
  and combat feel are one system, not three.
- **Checksums pass.** Spot-checks: `exp_to_next(1) = 108` ✓; skill totals (27+20+27+20+4 = 98) ✓
  against SCOPE; mob/boss counts consistent across SCOPE / WORLD_PLAN / COMBAT_FORMULA §13.3.
- **Deliberate simplifications are the right ones.** No durability, no fall damage, one climb
  state, no global cooldown, hazard damage as flat %-of-max-`life` — each removes a whole class of
  edge cases and each is justified against a pillar in its owning doc.
- **Fairness plumbing is thought through.** The 0.40 s i-frame window bounding touch-stack deaths
  (COMBAT_FORMULA §12), the graduated death `pct` with a structural no-de-level clamp
  (DEATH_PENALTY §2), off-screen-only respawns (SPAWN §5), and spawn-state invulnerability for
  elites (SPAWN §6) all convert P1/P2 from slogans into mechanics.
- **The Open Questions culture works** — most of what this review found was already flagged
  somewhere. The problem is that several flags are load-bearing and still unresolved (§2).

## 2. Contradictions and stale cross-references (fix before any coding pass)

These are not judgment calls; the tree currently disagrees with itself.

- **2.1 `base_move_speed` is contradicted between two owner docs.**
  `COMBAT_FORMULA.md` §10 still states `base_move_speed = 200 px/s` (and its Open Questions still
  call it a placeholder), while `MAP_TRAVERSAL.md` (Open Questions, "resolved at the C gate")
  states COMBAT_FORMULA *adopted* 8 tiles/s = **128 px/s** at the locked 16 px grid. An
  implementer reading only COMBAT_FORMULA ships a character moving 1.56× the speed every authored
  gap (5-tile jump distance, 3.5-tile apex) was validated against. **Owner: COMBAT_FORMULA.md —
  update §10 to 128 px/s / 8 tiles·s⁻¹ and close its stale OQ.**

- **2.2 SPAWN density budgets assume a screen width the locked viewport contradicts.**
  `SPAWN.md` §2 budgets density on "1 screen-width ≈ 20 tiles," flagged provisional. But
  `MAP_TRAVERSAL.md` records the locked render base: **640×360 = 40×22.5 tiles per screen**.
  20 tiles/screen is only true at 2× camera zoom — and `CAMERA.md` §5 explicitly leaves the
  default integer zoom multiplier unchosen. Until zoom locks, every density number ("3 normals
  per screen-width"), `max_concurrent` default, and the off-screen spawn buffer is ambiguous by a
  factor of 2. **Owner: CAMERA.md (pick the default zoom) → SPAWN.md (re-anchor §2 to tiles, not
  "screens").** Recommendation: restate SPAWN budgets directly in tiles (e.g. "3 normals per
  20 tiles of walkable extent") so they stop depending on a camera decision at all.

- **2.3 The FTUE's central promise is broken by the ratified curve, and no one has picked the
  fix.** ONBOARDING_FTUE targets Lv 8 + ferry in ~60 min; the 2026-07-24 ratified curve makes
  Lv 8 ≈ 1.1 h of at-level pacing. Both docs flag it (LEVELING OQ, ONBOARDING OQ) and both defer
  to "the owner must pick the lever." This is the single most-played hour of the game;
  Phase D cannot author `quest_001`–`010` `exp` values until the lever is picked. Recommendation:
  front-load scripted grants (the §4 "other" 5% budget is the designed home for exactly this) —
  it preserves the Lv-8 ferry gate as a clean graduation beat, whereas "≈first hour" softens the
  one promise the FTUE makes. **Owner: ONBOARDING_FTUE.md + LEVELING.md.**

- **2.4 Raid handler quests are simultaneously repeatable and one-time.** `QUESTS.md` §7 sets
  launch policy at strictly one-time-per-character; `social/RAID.md` §3 describes the handler as
  a repeatable clear turn-in wrapper. Already flagged in QUESTS' OQ, unresolved, and it blocks
  authoring 8 of the 120 quests. Recommendation: route repeat clears through RAID's own
  clear/cooldown grant mechanics and keep the handler quest one-time (an intro, not a wrapper) —
  no exception to §7 needed. **Owner: QUESTS.md + social/RAID.md.**

## 3. Core-loop design flaws

- **3.1 Out-of-combat recovery is unowned, and everything downstream leans on it.** (Biggest
  hole in the tree.) STATS and COMBAT_FORMULA both flag out-of-combat `life`/`essence` regen as
  "flagged, not resolved," with no owner. But the moment-to-moment loop cannot be evaluated
  without it: between-pull downtime (and therefore the real kills/hour behind the 480/h pacing
  anchor), tonic demand (ECONOMY's consumable sink sizing), and death recovery all hinge on this
  one rule. The failure modes bracket it: **no/slow free regen** makes tonics a mandatory
  per-hour tax — exactly the "pay-style" pressure the anti-pillars forbid, just in `shards`;
  **fast free regen** collapses the tonic sink ECONOMY §4 prices against. Recommendation: give
  the rule a home now (COMBAT_FORMULA, or a small REST.md) with a shape like "out of combat
  X s → strong regen ramp; in combat none" — the classic hunt-rhythm compromise — then let
  ECONOMY re-check tonic pricing against it. **Owner: COMBAT_FORMULA.md (proposed).**

- **3.2 The `essence` economy cannot yet support the DPS contract.** COMBAT_FORMULA §15 requires
  the rotation multiplier `m` to mature to ≈4–5 by Lv 50+, i.e. sustained skill-casting, not
  basic attacks. Worked check: a Lv 50 `bulwark` (off-primary `focus` ≈ 22, STATS §4.2) has
  `essence ≈ 40 + 200 + 66 ≈ 306` before gear. Specialization skills cost 12–28 `essence`
  (SKILL_SYSTEM §5); a rotation dense enough to reach `m ≈ 4` drains that pool in roughly
  15–25 casts — well under a minute — and **no doc defines any `essence` recovery during
  hunting** (see 3.1; `restore_essence` ops and `clarity` exist but are not budgeted as sustain).
  As authored, either rotations degrade to basic attacks (and the §14 TTK contract silently
  fails for non-`focus` lines) or players chug tonics as a DPS requirement. This needs a
  sustain budget — `essence`/min from regen + expected `restore_essence` uptime — sized against
  §15's implied cast cadence, before Phase D authors skill costs. **Owner: SKILL_SYSTEM.md +
  COMBAT_FORMULA.md, with STATS.md.**

- **3.3 The permanent Lv-40 specialization contradicts the tree's own reversibility
  philosophy.** Skill respec: free, unlimited (SKILL_SYSTEM §3, explicitly "no build is a
  trap"). Stat free points: reallocatable for a fee. Then the Lv-40 branch: **permanent, sibling
  rosters "never accessible"** (JOBS §1). JOBS softens it correctly (same primary, same weapon —
  a kit choice, not a stat re-class), but P4 says kits *are* the depth; a mis-chosen kit at
  ~30 h `/played` has exactly one remedy — reroll the character. That is the trap build P2
  promises not to sell. Recommendation: keep the choice weighty but not absolute — a paid,
  cooldown-gated spec re-choice at the same instructor (a strong `shards` sink ECONOMY would
  welcome), or a trial-window mechanic inside the Clockwork trial quest that lets the player
  sample each roster before committing. **Owner: JOBS.md, with ECONOMY.md.**

- **3.4 Everything hard lands on the same level: the Lv-40 seam pileup.** At Lv 40, within a
  session or two, a player hits: per-level cost first exceeding one hour (LEVELING §1.1), the
  permanent branch choice (3.3), the trainer quest + Clockwork Ruins trial pilgrimage (JOBS §1)
  through a region with **no bind town** (DEATH_PENALTY §4), the Deepway level gate, and
  onboarding onto a new island whose bands immediately out-level Harthmoor. Each is individually
  fine; stacked, they are a churn cliff at the exact moment the grind steepens. LEVELING's OQ
  already asks whether advancement should carry a pacing beat — this review's answer is
  **yes, strongly**: a one-time advancement `exp`/`shards` grant (budgeted from §4 "other") plus
  a guided arc-2 entry chain that fronts Frostpeak's first quests. **Owner: JOBS.md + LEVELING.md.**

- **3.5 P2's "20-minute session" has no designed beat in the arc-2 band.** The pillar promises
  rewarding 20-minute sessions; arc-2 levels cost 1.8–5.4 h each (owner-directed, fine as a
  climb), so a short session advances a level by ~5–15%. What else closes the loop in
  20 minutes? Quests are strictly one-time and run out (QUESTS §7 — no dailies/weeklies by
  explicit decision); collections/bestiary grants are one-time (§4 "other"); rested-`exp`
  doesn't exist; the **only recurring designed beat is the raid first-clear-of-day** (LEVELING
  §3.1) — which is group-gated behind a 3-member floor. A solo player's short session at Lv 60+
  is a thin slice of a bar plus drop RNG. That's a genre-classic shape, but it's also the exact
  thing P2 claims to reject. Recommendation: one small solo-viable recurring beat in the
  long-grind band (a first-kill-of-day bonus, a rotating hunt bounty, or rested-`exp`) — pick
  the cheapest, but pick one. **Owner: LEVELING.md (§4 budget) with QUESTS.md.**

- **3.6 The real death penalty is unbudgeted travel time.** The `exp` cost is well-tuned
  (0/1/3%, no de-level); the actual sting is the walk back: respawn at bind town, no free or
  discounted transit (DEATH_PENALTY §4), coach fares in `shards`, and three regions — Gloomwood,
  Sunken Depths, Clockwork Ruins — with **no bind town at all**. A death deep in Sunken Depths
  costs minutes-to-tens-of-minutes of re-travel, uncosted anywhere. Since time is the currency
  P2 actually protects, recommend a stated recovery budget — e.g. "any authored hunting map must
  be ≤ N minutes from a valid bind town via the paid network" — as a WORLD_PLAN/VALIDATION
  warn-rule, tuned per band. **Owner: DEATH_PENALTY.md + docs/WORLD_PLAN.md.**

- **3.7 Fixed-`N` raid instances turn a disconnect into a scripted wipe.** `raid_life` scales
  linearly with `N` **fixed at instance creation**, never re-scaled (COMBAT_FORMULA §13.3), with
  a 12-min enrage. TTK at full strength ≈ 7.9 min; lose one member of an `N`=4 run early and
  surviving DPS puts projected TTK ≈ 10.5 min — salvageable; lose one from `N`=3 and it's
  ≈ 11.9 min against a 12-min enrage: a coin-flip at best, before mechanics downtime. The doc
  frames non-rescaling as the party-requirement enforcer, but it also means an involuntary DC in
  a floor-size party ends the run by math ~10 minutes later. Cozy games forgive disconnects.
  Recommendation: a narrow grace — re-scale (or extend enrage) only when a member *disconnects*
  rather than releases/leaves, or allow mid-run refill from the party finder. **Owner:
  COMBAT_FORMULA.md §13.3 + social/RAID.md.**

- **3.8 In-band party power-leveling is stronger than the anti-boost design implies.** The
  anti-boost `exp` dampener craters over-leveled kills, but grouped play composes: a ±15-level
  full-credit band (PARTY §4), a killing-up bonus (×1.10 for d ≤ −6), the party pool bonus (up
  to 2× at `N`=6), and the guild buff. A Lv 25 in a Lv 40 party on Lv 40 mobs draws full share
  ×1.10 on kills the Lv 40s make trivially. LEVELING already flags grouped pace as unreconciled;
  this review adds: the reconciliation should include a worked carry scenario at the band edge,
  because the current numbers make "get pulled 15 levels" the objectively fastest path — a
  social pull by design, but one that will set the *de facto* leveling meta. **Owner:
  LEVELING.md + social/PARTY.md (already jointly flagged).**

- **3.9 One unmeasured constant carries the whole pacing edifice.** 480 kills/h × 0.70
  duty-cycle backs: every `/played` anchor (30/166/300 h), the raid-grant sizing (10–15% of a
  band level), `shards`/hour and therefore every ECONOMY fee ("≈16 min of income"), and the FTUE
  hour. LEVELING flags it as unmeasured; what's missing is a **falsification plan** — the tree
  should name the first thing the coding pass measures (kills/hour on a real Emberfoot map at
  authored density) and which knob turns if it misses (spawn `target_count` first, curve never).
  One paragraph in LEVELING would de-risk every number above. **Owner: LEVELING.md + SPAWN.md.**

## 4. Missing specifications the mock-up exposed

Building the scene mock-up (`docs/mockups/gameplay_scene_mockup.html`) forced concrete answers
the docs don't give:

- **4.1 Monster `life` feedback is unspecified — not even an Open Question.** HUD.md defines the
  `boss_bar` and damage numbers, and nothing for `normal`/`elite` health. Can a player see that
  an elite is at half `life`? P1's "a player who dies should know why" and the elite 20–40 s TTK
  band argue for *some* feedback (overhead sliver on recent-hit, hit-flash tiers, or a
  deliberate "no bars, read the damage numbers" decision). Any of the three is fine; the doc
  must pick. **Owner: HUD.md.** (Mock-up assumes: no overhead bars for normals, thin
  recent-hit sliver on elites — clearly marked as this review's placeholder.)
- **4.2 The wallet has no home.** ONBOARDING Beat 3 teaches "the wallet display" at first
  vendor spend; HUD.md never places a `shards` readout (only the inventory-full/cap toasts).
  Inventory-window-only is a defensible answer — but currently it's an accidental one. **Owner:
  HUD.md.**
- **4.3 Minimap content is undefined.** Position and frame are locked; contents are not — player
  dot, portals, NPC/quest markers, party members, explored-area fog are all unstated
  (UI_ART_SPEC waves at "a marker icon set"). This is a real implementation blocker for the
  shell. **Owner: HUD.md, with UI_ART_SPEC.md for icon art.**
- **4.4 No party-frame region is reserved.** P6 demands multiplayer-shaped-from-day-one and
  DEATH_PENALTY's OQ already asks whether fallen members show "on party frames" — frames HUD.md
  never defines. Reserve the region (left edge, below plate, is free) even if it ships stubbed.
  **Owner: HUD.md + social/PARTY.md.**
- **4.5 Gamepad reticle skills are ergonomically contradictory.** `aoe_circle`/ground-target
  aiming is Right Stick; skills 5–8 are `LB`+D-Pad — aiming with the right thumb while chording
  with the left thumb *and* moving on Left Stick is three jobs for two thumbs. Keyboard-only
  aim fallback is flagged in CONTROLS' OQ; the gamepad case is worse and unflagged. Recommend:
  on gamepad, reticle skills default to a smart-snap/nearest-target placement, hold-to-fine-aim.
  **Owner: CONTROLS.md + SKILL_SYSTEM.md §6.**
- **4.6 Climbing is a defenseless state with undefined interactions.** Attack and the skill bar
  are disabled in `climb` (MAP_TRAVERSAL §4) — including, presumably, the Dodge slot. Can a
  `ranged_skirmisher` volley or a Heavy knockback hit a climbing player, and does knockback
  detach them from the rope? A rope over a hazard pit + a skirmisher is currently an authored
  death sentence with no counterplay. Define knockback-while-climbing (suggest: immune to
  displacement, takes damage, may drop-input out voluntarily). **Owner: MAP_TRAVERSAL.md +
  COMBAT_FORMULA.md §11.**
- **4.7 Elite aggro → `boss_bar`?** HUD §6 says the bar appears on "boss/flagged-elite aggro,"
  but no doc defines which elites are flagged or what field flags them (AI_BEHAVIOR presumably;
  the flag vocabulary is also missing for CAMERA's "boss slam" shake). Same missing
  ability-presentation metadata home, twice. **Owner: AI_BEHAVIOR.md.**

## 5. Priority summary

| # | Finding | Severity | Owner(s) |
|---|---|---|---|
| 2.1 | `base_move_speed` 200 vs 128 px/s contradiction | **Blocker (coding pass)** | COMBAT_FORMULA.md |
| 2.2 | Screen-width density vs unlocked zoom | **Blocker (Phase D density)** | CAMERA.md → SPAWN.md |
| 3.1 | Out-of-combat regen unowned | **Blocker (loop feel + economy)** | COMBAT_FORMULA.md |
| 3.2 | `essence` sustain vs DPS contract | **Blocker (Phase D skill costs)** | SKILL_SYSTEM.md |
| 2.3 | FTUE hour vs ratified curve | High | ONBOARDING_FTUE.md |
| 3.3 | Permanent spec vs no-trap-builds | High | JOBS.md |
| 3.4 | Lv-40 seam pileup | High | JOBS.md + LEVELING.md |
| 4.1 | Monster `life` feedback unspecified | High | HUD.md |
| 3.5 | No 20-min session beat in arc 2 | Medium | LEVELING.md |
| 3.6 | Death travel-time unbudgeted | Medium | DEATH_PENALTY.md + WORLD_PLAN.md |
| 3.7 | Fixed-`N` raids vs disconnects | Medium | COMBAT_FORMULA.md + RAID.md |
| 2.4 | Handler-quest repeatability conflict | Medium | QUESTS.md + RAID.md |
| 3.8 | In-band carry meta | Medium | LEVELING.md + PARTY.md |
| 3.9 | Kills/hour falsification plan | Medium | LEVELING.md + SPAWN.md |
| 4.2–4.7 | HUD/controls/climb spec gaps | Low–Medium | HUD.md, CONTROLS.md, MAP_TRAVERSAL.md, AI_BEHAVIOR.md |

## Open Questions

- None owned here — this is a review report. Every finding above is addressed to its owning
  doc's Open Questions channel per CLAUDE.md law 4; the owning docs adopt or reject them at the
  next gate.
