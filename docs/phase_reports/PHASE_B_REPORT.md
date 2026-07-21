# PHASE_REPORT — Phase B (Systems)

Status: **complete**. 8 sub-agents (3 Opus, 4 Sonnet groups + Opus core), 32 docs, ~5,550
lines. All files passed: forbidden-token scan, H1 + References header, Open Questions ending.

## Files created (by dispatch group)
- **B-core (Opus):** STATS, ELEMENTS, STATUS_EFFECTS
- **B-combat (Opus):** COMBAT_FORMULA (incl. the load-bearing monster stat budget §13 and
  raid party-scaling), LEVELING (exp curve bound to TTK contract; ~201h to cap)
- **B-behavior (Sonnet):** DEATH_PENALTY, AI_BEHAVIOR (12 profiles + boss phase contract),
  SPAWN
- **B-skill (Opus):** JOBS (4 lines + full 84-skill roster plan), SKILL_SYSTEM (level_data
  rows at 1/4/7/10), SKILL_EFFECTS (14-op registry)
- **B-items (Opus):** ITEMS (rarity × band stat budgets), ENHANCEMENT (+1..+9, no
  destruction, pity), DROPS (chance tiers + pool_equip_rNN), ECONOMY, INVENTORY
- **B-world (Sonnet):** MAPS_SYSTEM, MAP_TRAVERSAL, MAP_INTERACTABLES, MAP_LAYERS,
  MAP_CONNECTIONS (map-level edge table deferred to Phase D reconciler by design)
- **B-shell (Sonnet):** QUESTS, CONTROLS, CAMERA, HUD, PERSISTENCE (authority taxonomy)
- **B-social (Sonnet):** TRADING, PARTY, GUILD + stubs CHAT, MAIL, MARKET

## Gate actions taken (orchestrator)
- Promoted into GLOSSARY: job lines `bulwark`/`keeneye`/`weaver`/`flicker` (+12 job names,
  `novice`), status cleanse tags (`burn_type` etc.), guild crest shapes.
- ID_REGISTRY skill ranges bound to concrete line tokens.
- GLOSSARY `haste` open question closed (kept combined, per STATS §5).
- Declined without prejudice: GUILD.md's proposed `guild.schema.md` (not in the §2 tree;
  guild record is server-owned — deferred to the backend pass, tracked below).

## Open Questions rollup (extracted verbatim from each doc)

### docs/10_systems/AI_BEHAVIOR.md
- Boss/monster ability IDs (§15 `added_abilities`) have no reserved prefix in
  `docs/ID_REGISTRY.md` today (only `skill_<line>_NNN` for player job-line skills). Needs an
  ID_REGISTRY decision before Phase D authors boss kits — proposing a
  `mob_ability_<mob_NNN>_NN` convention or similar; flagged, not decided here.
- An on-death-detonate variant of `kamikaze_burster` (explodes even if killed before its windup
  completes) is not defined; if a later design wants it, it should be a monster-authored
  `on_hit_proc`/death effect (`10_systems/SKILL_EFFECTS.md`), not a change to this profile's base
  rule.
- `pack_max_size` (4) and `pack_call_radius` (8) are first-pass; may need per-region tuning once
  pack rosters are authored (Phase D).
- Whether a non-boss monster may ever combine two profiles (a "hybrid elite") outside the
  `boss_scripted` phase mechanism is out of scope here — default is exactly one profile per
  non-boss monster.
- Exact tile-to-pixel size for `aggro_radius`/`aggro_vertical_band` units is owned by
  `40_assets/ART_BIBLE.yaml`; not fixed here.
- `phase_shift_duration_s` and whether it should scale by boss tier (regional vs Rift raid) is a
  first-pass default; owner `10_systems/COMBAT_FORMULA.md`/`10_systems/PARTY.md` may retune for
  raids.

### docs/10_systems/CAMERA.md
- Deadzone size, lookahead distance/timing, and the vertical re-center lerp (§1–§3) are first-pass
  values chosen for a readable, non-nauseating feel; retune after playtesting once the tile→pixel
  scale locks (`40_assets/ART_BIBLE.yaml`). The §7 shake-amplitude px values are placeholders for
  the same reason and should be revisited alongside them.
- Default integer zoom multiplier (§5) is not chosen here — it is downstream of the
  `40_assets/ART_BIBLE.yaml` tile-scale lock referenced across this tree
  (e.g. `10_systems/COMBAT_FORMULA.md` §10).
- The "boss slam" screen-shake flag's exact field name/location is not yet defined in
  `10_systems/SKILL_EFFECTS.md` or `10_systems/AI_BEHAVIOR.md`; flagged for whichever doc adds
  ability-presentation metadata.
- Whether non-arena "mini-lock" zones (e.g., a tough elite pack in a dungeon corridor) are used in
  Phase D content, beyond the 15 boss arenas, is undecided — the mechanism (§6) supports it either
  way.
- Ultrawide/uncommon aspect ratios and any camera safe-area guarantee are not addressed; likely an
  `40_assets/ART_BIBLE.yaml`/engineering concern once a target resolution is fixed.

### docs/10_systems/COMBAT_FORMULA.md
- `base_move_speed` (200 px/s) and `base_attack_interval` (0.90 s) are placeholders until the tile
  scale is locked in `40_assets/ART_BIBLE.yaml`; the `haste` percentages (STATS §5) are scale-free,
  but the px value is not. Owner: COMBAT_FORMULA at the C gate.
- Mid-party size for the §14 raid target is assumed `N ≈ 4–6` (mid 5) pending
  `10_systems/social/PARTY.md`; the §13.3 formula is `N`-agnostic, but the legal party range and
  `N` counting must be confirmed there. Flagged.
- `power_ref`/`mult m` (§15) assume typical gear budgets from `10_systems/ITEMS.md` and skill
  coefficients from `10_systems/SKILL_SYSTEM.md` that are not yet authored; if those land far from
  the reference, retune `mult m` (never `normal_life`). Owner: balance pass, C/D gates.
- Whether the `dirk`/`fortune` double-dip (`10_systems/STATS.md` OQ) needs a `power`-coefficient
  cut is a joint ITEMS/COMBAT_FORMULA call; default keeps STATS's uniform `2·G_phys`.
- Heavy-hit cast interruption versus `normal`/`elite` super-armor flags needs the flag vocabulary
  from `10_systems/AI_BEHAVIOR.md`; default is "interruptible unless flagged."
- Out-of-combat `life`/`essence` regen (resting) inherited from `10_systems/STATS.md` OQ is still
  unowned; propose a short rest rule here or in a dedicated doc. Flagged, not resolved.

### docs/10_systems/CONTROLS.md
- `LT`/`RT` and `Back`/`View` are reserved, unassigned gamepad inputs; candidates raised but not
  decided: a future targeting-cycle, a block/parry mechanic, or a quick-map toggle. Flag for a
  playtesting pass.
- Gamepad chat entry (on-screen keyboard, quick-phrase wheel, or none at launch) is undecided;
  owner `10_systems/social/CHAT.md` once authored.
- Dodge-slot skill eligibility (which skills may be assigned there) and whether re-slotting it
  costs anything are `10_systems/SKILL_SYSTEM.md`'s open call (§3 above); this doc assumes free
  re-slotting matching that doc's §7 general skill-bar policy.
- Exact jump-buffer/coyote-time values (§4) are first-pass, chosen at the high end of typical
  platformer feel; retune after playtesting against `10_systems/COMBAT_FORMULA.md` §10's cadence
  once real frame timing is measured.
- Whether keyboard-only players (no mouse) get a fixed-facing-range aim fallback beyond "last
  move direction" is not specified; flag if playtesting shows aiming `aoe_circle`/`projectile`
  skills without a mouse feels imprecise.
- Mouse-and-keyboard vs. gamepad simultaneous hot-swap mid-session (common in PC action games) is
  assumed supported (last-used device drives on-screen prompts) but not detailed here.

### docs/10_systems/DEATH_PENALTY.md
- Exact `pct` values (§2) are first-pass balance; owner for retuning is this doc, informed by
  `10_systems/LEVELING.md`'s eventual exp curve.
- Whether a fallen character (§5.3) still shows on party frames or counts for loot eligibility is
  `10_systems/PARTY.md`'s call — flagged for confirmation.
- Rebind cost: is resting at a new inn free, or does it cost `shards`/carry a cooldown? Default
  assumed **free**; owner `10_systems/ECONOMY.md` may add a fee.
- A revive skill effect op (§6) is proposed for `10_systems/SKILL_EFFECTS.md` to pick up as
  Provisional; it is not defined here and no op name is assumed.
- Dungeon/zone content-reset-on-death behavior (§5.1) is flagged for
  `15_maps_system/MAPS_SYSTEM.md` to confirm, not assumed here.
- Which specific staging-shard field (of `map_183`–`188`) each raid arena releases its fallen
  players to is a 1:1 mapping that `docs/WORLD_PLAN.md`/`15_maps_system/MAP_CONNECTIONS.md` will
  need to assign when the Rift is authored; not fixed here.
- Post-cap (Lv 100+) exp loss, once post-cap progression is defined, inherits
  `00_vision/SCOPE.md`'s open question; the 0% default here assumes gear-only post-cap holds.

### docs/10_systems/DROPS.md
- Chance-bucket anchors (§2), the §3 `shards` formula, and §5.5 rarity weights are first-pass;
  balance against `10_systems/ECONOMY.md` §5 (income vs sinks) and `10_systems/COMBAT_FORMULA.md`
  §14 (kills/hour) at the D gate. If income drifts, tune §3, not the item budgets.
- The `fortune` cap (+100%, §4) and whether it should also nudge `shards` slightly are open;
  default keeps `shards` `fortune`-free for steady income. Owner: this doc with
  `10_systems/ECONOMY.md`.
- Raid-token → raid-gear exchange (§5.4) and the token IDs within Rift `item_etc` `0177`–`0192` are
  a Phase D / endgame design; this doc fixes only that a `guaranteed` token row exists. Flagged for
  `10_systems/social/PARTY.md` + the R12 content batch.
- Ownership-timer values (60 s / 120 s) and whether dungeons/arenas shorten them are first-pass;
  confirm against `10_systems/social/PARTY.md` loot rules and `15_maps_system/MAPS_SYSTEM.md` zone
  behavior.
- Per-slot pool weighting (§6) — uniform vs weighting toward the player's line's weapon — is a
  `pools.yaml` authoring choice; default uniform-across-slots so all lines share a pool. Flag if
  weapon drops feel too diluted across four types.

### docs/10_systems/ECONOMY.md
- Every number here (starting `shards`, fee coefficients, tonic prices, `base_buy`, the 18
  drinks/hour assumption) is first-pass, balanced against `10_systems/DROPS.md` §3 and
  `10_systems/LEVELING.md` §1. Retune at the D gate once real spawn density and potion restore
  values land; adjust **prices/fees**, never the `10_systems/DROPS.md` faucet or
  `10_systems/COMBAT_FORMULA.md` `normal_life`.
- Quest `shards` reward budgets (§1) depend on `10_systems/QUESTS.md` honoring a per-region share;
  the split of the total faucet between hunting-drops and quests is unfixed here (default: drops
  dominant, quests supplementary). Confirm with `10_systems/QUESTS.md` at the D gate.
- Market transaction-fee rate and guild-creation fee are stubs owned by the `social/` docs; if
  those systems change the sink budget materially, revisit §6. Flagged, server-dependent.
- A "mastery `exp` → `shards`" post-cap soft sink is floated by `10_systems/LEVELING.md` §6 OQ but
  **not** adopted here (default: cap `exp` discarded). If wanted it is a faucet and belongs in §1,
  balanced against §2.
- Whether stat reallocation should be cheaper/free below some level (to lower the early
  experimentation barrier) is open; default is the flat `50·L` curve (§3.1).

### docs/10_systems/ELEMENTS.md
- Should any player-facing per-element resistance ever exist (e.g., a `legendary` gear affix or
  a region-attunement consumable)? Default **no** — `warding` + status only. Flag for possible
  `10_systems/ITEMS.md` affix consideration; would require a GLOSSARY note if it introduces
  per-element tokens.
- Mitigation routing when a **physical** weapon carries an **elemental** skill (e.g., a `blade`
  skill dealing `fire`): default is that the damage instance uses its skill-declared element to
  pick `armor` vs `warding` (so that `fire` blade hit → `warding`). Confirm with
  `10_systems/SKILL_SYSTEM.md` / `10_systems/COMBAT_FORMULA.md`.
- "True"/unmitigated damage that bypasses both `armor` and `warding` is **not** in scope; flag if
  a Rift raid boss (`docs/WORLD_PLAN.md` R12) needs it. Default: no such damage type.
- The element→status pairing (§5) is a guideline; if content authoring needs it mechanically
  enforced, promote it to a rule. Owner call: keep as guideline for now.

### docs/10_systems/ENHANCEMENT.md
- Success rates (§2) and per-level stat gains (§4) are first-pass balance. If the +6..+9 band
  proves too swingy or too safe against the §5 fee, tune the odds and the soft-pity step (§3)
  before touching the stat-gain %s. Owner: this doc with `10_systems/ECONOMY.md`.
- Should a **transfer** exist to move an `enhance_level` (or its cost) from an outgrown item to its
  tier-up replacement, so the enhancement grind is not fully repeated each tier? Default: no
  transfer at launch (each item enhanced from +0). Flag as a possible cozy addition; would need an
  op in the enhancement NPC UI and a rule here.
- Emberstone vendor purchase / crafting from region materials (`item_etc` per region) is deferred;
  if added it belongs to `10_systems/ECONOMY.md` (a `shards`/material sink) referencing this doc's
  tier mapping (§1), not a new drop rule.
- Whether raid bosses drop a distinct high-tier emberstone or reuse Emberstone V is a
  `10_systems/DROPS.md` R12 call; default reuses V (§1 covers T9–T10 and the Rift is out-gear, not
  out-tier, per `10_systems/LEVELING.md` §6).
- Enhancement above +9 (e.g., a +10..+12 "starforce" extension) is explicitly **not** in scope this
  pass; if ever added it must not break the `10_systems/COMBAT_FORMULA.md` §13/§15 balance surface
  (the anti-power-creep concern of `00_vision/PILLARS.md`).

### docs/10_systems/HUD.md
- Whether `boss_bar` should optionally show an exact `life` percentage (accessibility option) vs.
  staying bar-only is undecided; default is bar + pips only, no number.
- Whether toasts should get a "reduce frequency"/mute-by-category player preference beyond the
  fixed 3-stack/4 s timing is unresolved.
- Fully hiding the chat dock (vs. always-collapsed-visible) is not offered at launch; flag if
  `10_systems/social/CHAT.md` wants a hide option once authored.
- HUD scaling for uncommon aspect ratios / safe-area guarantees is not addressed here; likely an
  engineering/`40_assets/ART_BIBLE.yaml` concern once a target resolution locks.
- Exact pixel sizes, hex values, and icon art for every element above are
  `40_assets/UI_ART_SPEC.md`'s (Phase C); this doc fixes layout and token usage only.
- Whether the player plate should ever show a portrait/character-icon is not modeled; default is
  text-only (name/level/job).

### docs/10_systems/INVENTORY.md
- Base slot count (24/tab) and the +8→48 expansion cap are first-pass; if the solo pass should ship
  more generous (no purchasable gating without a server), default to the 48 max unlocked in solo
  and gate expansion purchases only on the live server. Owner: this doc with
  `10_systems/PERSISTENCE.md`.
- `shards` wallet scope (per-character vs account-shared) and whether the bank ever holds `shards`
  are `10_systems/PERSISTENCE.md` calls; §3/§7 assume per-character wallet, item-only bank.
- Auto-loot radius (64 px) and vacuum speed inherit `10_systems/COMBAT_FORMULA.md` §10's tile-scale
  Open Question; finalize when `40_assets/ART_BIBLE.yaml` locks the scale.
- Whether a full `equip` tab should offer an **auto-vendor-`common`-on-pickup** opt-in (to avoid
  ground-clutter at high kill rates) is floated but **off by default** (§5's never-take-without-
  input rule). Flag if high-level farming proves too slot-pressured.
- Account-shared vault tab and cross-character mail-based item transfer are deferred to the social
  pass; if added, mail item-attachment limits belong to a future `10_systems/social/MAIL.md`, not
  here.

### docs/10_systems/ITEMS.md
- SCOPE (`00_vision/SCOPE.md`) lists "~80 armor" and "~24 accessories"; the §4 clean grid yields 50
  core armor (5 slots × 10 tiers) + reserved growth and 30 core accessories. Phase D fills toward
  the SCOPE counts using the reserved `item_equip` ranges (intermediate/region-variant pieces on
  the same §8/§9 value curve, interpolated by `req_level`); exact per-slot SKU count is a Phase D
  call bounded by `docs/ID_REGISTRY.md`. Flagged for the content pass.
- `W` and the §10 affix budgets assume the `power_ref`/`mult m` reference of
  `10_systems/COMBAT_FORMULA.md` §15; if the balance pass finds an at-level geared character lands
  far off `power_ref`, retune `mult m` there (never `normal_life`), and revisit the staff +10%
  `W` lever here. Joint ITEMS/COMBAT_FORMULA call at the C/D gates.
- The `dirk`/`fortune` double-dip (`10_systems/STATS.md` §2.1 OQ) may want a lower `dirk` `W` or a
  capped `power` affix on `dirk` weapons; default keeps the uniform table. Owner: joint
  `10_systems/STATS.md` / `10_systems/COMBAT_FORMULA.md`.
- pe weights (§6) are first-pass balance; if `crit_rate`/`haste` prove over/under-valued after the
  §15 rotation is authored (`10_systems/SKILL_SYSTEM.md`), retune the weight, not the base tables.
- Whether a `legendary` gear affix should ever grant a per-element defense (currently forbidden,
  `10_systems/ELEMENTS.md` OQ) — default no; would require a GLOSSARY Provisional token.
- Set bonuses (wearing N pieces of a themed group) are **not** in this pass; if wanted they attach
  to boss-unique groups (§11) via `passive_stat_bonus` and need a `set_id` field in
  `20_schemas/item.schema.md`. Flagged, not designed.

### docs/10_systems/JOBS.md
- The four line tokens (`bulwark`/`keeneye`/`weaver`/`flicker`), `novice`, and the twelve job
  names are proposed for `00_vision/GLOSSARY.md` promotion at the B gate (§0); until promoted they
  live here as their sole definition. Flag if any collides with a later-authored token.
- Job-trainer NPC IDs and the three advancement quest IDs per line are **Phase D** content
  (`10_systems/QUESTS.md`, `docs/ID_REGISTRY.md`); §1 fixes only the level gates (8/30/60) and the
  town pattern. Confirm the Millbrook trainer NPC allocation fits the Millbrook `npc` block when
  quests are authored.
- Whether a small `shards` cost or item gate should accompany the trainer quests (beyond the quest
  itself) is an `10_systems/ECONOMY.md`/`10_systems/QUESTS.md` call; default is quest-only.
- Prerequisite chains among a line's skills (e.g., an ultimate feeding off an earlier skill's rank)
  are owned by `10_systems/SKILL_SYSTEM.md`; the concrete prereq edges per skill are authored in
  Phase D skill YAML. This roster fixes tier order only.
- Summon caps here (`Falcon` 1, `Summon Elemental` 1, `Shadow Clone` 2) assume the
  `10_systems/SKILL_EFFECTS.md` / `20_schemas/monster.schema.md` cap of 1–2; confirm at the C gate.
- Balance of the `flicker`/`dirk` `fortune` double-dip inherits the open `10_systems/STATS.md` §2.1
  question; if a `power`-coefficient cut lands there, no name/roster change is needed here.

### docs/10_systems/LEVELING.md
- **Post-launch** paragon/prestige track (deferred, §6): if ever pursued, it must not touch the
  §1 base curve or the primary model; a bounded, mostly-horizontal system (cosmetic/`shards`/
  account-wide unlocks) is the only shape compatible with the fixed balance surface. Owner:
  LEVELING.md, post-launch — **not** an in-scope launch item.
- Raid `exp` split mechanics (even vs contribution-weighted) and the party `exp`-share radius are
  owned by `10_systems/social/PARTY.md`; the 150× total here assumes an even split among a mid
  party. Confirm at the B gate.
- The ≈ 480 kills/hour pacing assumption folds in travel/aggro downtime that has not been measured;
  if real spawn density (`docs/WORLD_PLAN.md`, map spawn data) diverges, the `/played` estimates
  shift while the `exp_to_next` curve stays fixed. Flagged for the Phase D content pass.
- Quest `exp` totalling exactly 25% per region depends on `10_systems/QUESTS.md` honoring this
  budget; if quest counts per region (`docs/ID_REGISTRY.md`) can't hit 25% cleanly at a given band,
  the residual shifts to hunting (higher `kills_per_level` in practice). Owner: QUESTS.md.
- `exp` at cap is currently discarded (§6); if a "mastery `exp` → `shards`/material" conversion is
  ever wanted as a soft sink, it belongs to `10_systems/ECONOMY.md`, not here. Default: discarded.

### docs/10_systems/PERSISTENCE.md
- The offline→online import's validation pass is the most important open item here: does it (a)
  re-derive `level` from raw cumulative `exp` and re-simulate stat growth rather than trusting
  stored derived values, (b) range-check every item ID/`enhance_level`/`rarity` against
  `docs/ID_REGISTRY.md` and `10_systems/ITEMS.md`/`10_systems/ENHANCEMENT.md` legal bounds, or (c)
  restrict import to a subset (e.g., cosmetic/account state only, character re-leveled live)?
  Not decided — owner: this doc, jointly with whatever future server-onboarding doc exists.
- Position/velocity reconciliation algorithm (§4) is explicitly deferred — out of this run's scope
  per `00_vision/SCOPE.md`; do not design it prematurely here.
- Whether the `shards` wallet and bank are per-character (assumed, matching
  `10_systems/INVENTORY.md` §3/§7's default) or ever account-shared is confirmed here as
  **per-character** for the solo build and the interim server; an account-shared purse/vault is a
  later, explicitly opt-in addition, not a launch item.
- `save_version`'s migration framework (§8) has no concrete implementation yet; flagged for
  `30_engineering/ENGINEERING_STANDARDS.md`, which itself is not confirmed to exist as a Phase B
  deliverable (`00_vision/SCOPE.md`'s phase list does not explicitly enumerate
  `30_engineering/*`) — flag this gap for the orchestrator.
- Cloud-save / multi-device sync for the solo build is not addressed; assumed local-disk-only
  until a server exists.
- Whether a corrupted/unreadable save slot should attempt partial recovery or hard-fail to a
  "create new character" prompt is unresolved.

### docs/10_systems/QUESTS.md
- Party quest-credit sharing (does a party member's kill/collect count for everyone nearby?) is
  deferred to `10_systems/social/PARTY.md`, not yet authored; default until then is **unshared** —
  each member individually needs the kill tag / the collect item.
- Exact per-quest `pct` within the §4 bands, and the regional ≈25% reconciliation, is Phase D
  authoring work per `10_systems/LEVELING.md` §4's own Open Question; not resolved to the exact
  quest here.
- `quest_object` full mechanics (respawn timer, whether non-questers can see/interact with it) are
  owned by `15_maps_system/MAP_INTERACTABLES.md`, not yet authored; this doc only fixes the
  grant-on-interact contract (§3.1).
- The `reach`-step trigger-zone declaration (map-side schema shape) is pending
  `15_maps_system/MAPS_SYSTEM.md`; assumed analogous to `10_systems/SPAWN.md` §1's `spawn_zones`
  rect pattern but not confirmed.
- Daily/weekly/repeatable quests are explicitly **not** a launch feature (§7); if added later it
  is a new system referencing this doc's anatomy, not a change to it.
- Whether a quest may ever require an equipped item level / job line beyond `level_requirement`
  (e.g., a line-specific side quest) is not modeled; default is any character meeting the level +
  prereqs may accept any quest.

### docs/10_systems/SKILL_EFFECTS.md
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
- **`taunt` immunity flag** for `boss`/raid entities lives in `20_schemas/monster.schema.md`;
  confirm the flag name when that schema is authored (default: bosses taunt-immune, matching CC
  immunity).
- **`condition` enum** for `passive_stat_bonus`/`on_hit_proc` (`below_life_pct`, `while_veiled`,
  `vs_marked`, …) is open-ended; the concrete list should be frozen at the C gate so
  `docs/VALIDATION.md` can enum-check it. Until then, authors use only the examples named here.

### docs/10_systems/SKILL_SYSTEM.md
- **Skill-bar slot count** (first-pass 8) and input layout are owned by `10_systems/CONTROLS.md` /
  `10_systems/HUD.md`; if the platform button budget forces fewer, content that assumes 8 usable
  actives at once may need review. Flagged for the B/C gate.
- **Skill-point total** (99 lifetime, +1/level) is first-pass; if playtesting shows characters feel
  starved or over-flush against 21 skills, `10_systems/LEVELING.md` (owner of the trigger) and this
  doc jointly retune (e.g., a small advancement lump). Default holds at flat +1/level.
- **Tile → pixel scale** for all §6 ranges inherits `10_systems/COMBAT_FORMULA.md` §10's open scale
  lock (`40_assets/ART_BIBLE.yaml`); numbers here are tile-relative and unaffected by the eventual
  px value, but reticle/aim feel can't be tuned until it lands.
- **Free skill respec with no `shards` cost** (§3) is the generous default; if `10_systems/ECONOMY.md`
  needs a nominal sink, a small fee may be added there without changing this doc's mechanics.
- **Cast/recovery windows** per skill interact with `haste` attack-speed (`10_systems/STATS.md` §5);
  whether `haste` also shortens skill cast/recovery (vs only basic attacks and `cooldown`) is a
  `10_systems/COMBAT_FORMULA.md` cadence call. Default: `haste` speeds basic attacks and movement,
  not skill cast times; flagged.

### docs/10_systems/SPAWN.md
- The `1 screen-width ≈ 20 tiles` assumption (§2) is provisional pending the real camera/viewport
  spec in `30_engineering/ENGINEERING_STANDARDS.md`; every density number in §2/§4 scales directly
  if that changes.
- The map schema's filename (§1) is assumed but not confirmed — likely
  `20_schemas/map.schema.md`, authored at Phase C.
- `target_count`/`max_concurrent` defaults (§2, §4) are first-pass and tunable per region once
  Phase D populates real zones.
- The town/interior combat-free assumption (§2) inherits `docs/WORLD_PLAN.md`'s open item; if
  `15_maps_system/MAPS_SYSTEM.md` later allows interior combat, this table needs a row.
- Whether the regional-boss "arena-entry instanced" mechanism (§3) is a true per-player instance
  or a shared arena that resets on empty is left to `15_maps_system/MAPS_SYSTEM.md`; both satisfy
  this doc's "no long timer" intent.
- Rift add-wave count/pacing is not budgeted here — it is authored per-boss in Phase D monster
  data, not a SPAWN.md rule.

### docs/10_systems/STATS.md
- `haste` split into separate move-speed and attack-speed tokens: **resolved — kept combined**
  (GLOSSARY default; no balance reason found). Reopen only if attack-speed animation breakpoints
  later require independent control; owner STATS.md.
- `dirk`/`fortune` double-dip (`power` + `crit_rate` + `crit_power` from one primary) may need a
  lower `power` coefficient or lower weapon base `W`. Owner: `10_systems/COMBAT_FORMULA.md` +
  `10_systems/ITEMS.md`; default keeps the uniform `2*G_phys` coefficient.
- Free-pool size (+2/level) and the reallocation `shards` fee are first-pass; owners
  `10_systems/LEVELING.md` / `ECONOMY.md` may tune.
- Passive out-of-combat `life`/`essence` regeneration (resting) is not defined here; propose
  ownership by `10_systems/COMBAT_FORMULA.md` or a dedicated rest rule. Flagged.
- Exact `armor`/`warding` → damage-reduction curve and `precision`-vs-`evasion` hit resolution
  are `10_systems/COMBAT_FORMULA.md`'s; confirm the boundary at the B gate.
- Post-cap (Lv 100+) primary growth interaction once auto-growth stops (inherits
  `00_vision/SCOPE.md` OQ; default gear-only). Owner: `10_systems/LEVELING.md`.

### docs/10_systems/STATUS_EFFECTS.md
- Cleanse-group tags (`burn_type`, `poison_type`, `chill_type`, `control_type`, `sense_type`,
  `curse_type`) are **new classification tokens** referenced by the `cleanse_status` op, item
  files, and skill data. Propose promoting them to `00_vision/GLOSSARY.md` Provisional at the B
  gate; until then they live here as the sole definition.
- Buff removal: is a monster **dispel/purge** op needed? `00_vision/GLOSSARY.md`'s skill-effect
  ops have no `purge`. Default: buffs only expire (no purge); flag if a boss design needs to strip
  player buffs. Owner: `10_systems/SKILL_EFFECTS.md`.
- Hard-CC DR window (10 s) and immunity duration (8 s) are first-pass; may need PvE-vs-raid tuning.
  Owner: `10_systems/COMBAT_FORMULA.md` / `10_systems/PARTY.md`.
- Whether Rift raid bosses use full CC-immunity (current default) or the `boss` soft-CC row;
  confirm with `10_systems/PARTY.md`.
- Max simultaneous statuses (12) is tied to the HUD icon budget; confirm against
  `40_assets/UI_ART_SPEC.md` when the HUD is specced.
- `regen` and healing scaling: currently % of receiver max `life`; if healer output should scale
  on the applier's `spellpower` instead, that is a `10_systems/COMBAT_FORMULA.md` decision.

### docs/10_systems/social/CHAT.md
- Bubble duration/truncation, scrollback size, and spam/rate limits are unset — owner
  `10_systems/HUD.md` jointly with this doc.
- Moderation policy and whether `party`/`guild` history persists across relogin
  (`10_systems/PERSISTENCE.md`) are undecided.
- Gamepad chat entry is undecided, inherited from `10_systems/CONTROLS.md`'s own open item.

### docs/10_systems/social/GUILD.md
- Roster-expansion (§4) and crest-edit (§5) `shards` amounts are this doc's first-pass proposals;
  `10_systems/ECONOMY.md` needs to fold them into its sink budget (its own Open Questions already
  flags this exact reconciliation for the `social/` docs' fee stubs).
- Guild records have no ID scheme in `docs/ID_REGISTRY.md` (guilds are runtime player-created data,
  not Phase D authored content) — proposes server-assigned `guild_<NNNNNN>` IDs; needs
  `10_systems/PERSISTENCE.md` to confirm the format.
- No schema doc yet exists for the guild record; proposes `20_schemas/guild.schema.md` at Phase C.
- The crest shape enum (`heater`/`round`/`banner`/`diamond`/`crest_ornate`, §5) is new vocabulary
  not yet in `00_vision/GLOSSARY.md` — propose promoting it to GLOSSARY Provisional at the B/C
  gate, alongside the 24-symbol list owned by `40_assets/UI_ART_SPEC.md`.
- Which 40_assets doc owns the crest color palette (`40_assets/ART_BIBLE.yaml` vs
  `40_assets/UI_ART_SPEC.md`) is undecided.
- Officer cap (5, §3) and the roster growth steps (§4) are first-pass; may need retuning once
  post-launch guild-activity data exists.
- Guild-hop cooldown: none at launch (§1) since there is no bank/reward to farm by hopping (§8);
  revisit if that changes.
- Guild bank and guild quests (§8) are deferred future features, not designed here.

### docs/10_systems/social/MAIL.md
- Send fee, mailbox capacity, and expiry window are unset — owner `10_systems/ECONOMY.md` jointly
  with this doc.
- Whether an attachment may ever hold more than one item/stack is undecided; default is one.
- Whether `10_systems/social/MARKET.md` proceeds deliver via mail is flagged in both stubs, not
  resolved.
- No HUD frame or keybind is reserved yet for a mailbox panel.

### docs/10_systems/social/MARKET.md
- Listing fee rate, duration, and max concurrent listings per character are unset — owner
  `10_systems/ECONOMY.md` jointly with this doc.
- Whether `legendary`/boss-unique listings need a price floor/ceiling is flagged for
  `10_systems/ECONOMY.md`.
- Proceeds delivery (wallet credit vs `10_systems/social/MAIL.md`) is undecided.

### docs/10_systems/social/PARTY.md
- The 70/30 contribution/presence split and the range_mult bands (§4) are first-pass balance;
  retune once real damage-share telemetry exists. Owner: this doc with `10_systems/ECONOMY.md`.
- This doc's split refines `10_systems/LEVELING.md` §3's "assumes an even split among a mid party"
  note for the raid 150× total; the two should reconcile at the next gate — the actual split is
  not strictly even, only approximately so for a balanced-damage party.
- Whether "same-map" (§4/§5) should tighten to a same-screen/zone radius on very large field maps
  is flagged, not resolved; default keeps the literal same-map gate.
- Whether material/use-item/`shards` rows duplicate per eligible member or are split (§5) is
  `10_systems/DROPS.md`/`10_systems/ECONOMY.md`'s faucet-balance call; this doc assumes
  duplication.
- Need/greed as a third loot mode (floated by `10_systems/DROPS.md`'s own wording) is not designed
  in this pass; only `free_for_all`/`round_robin` exist.
- Exact invite-decline timeout (30 s) is first-pass UX, not load-bearing.
- Neither `10_systems/HUD.md`'s layout (§2/§4, local-player-plate only) nor
  `10_systems/CONTROLS.md`'s input map yet reserves a screen region or panel-toggle keybind for
  other party members' plates (§3) — this doc supplies only the data contract for when they do.

### docs/10_systems/social/TRADING.md
- Level floor (Lv 8), proximity (4 tiles), offer slot count (8), and every timeout/rate-limit
  number in §3/§5 are first-pass; retune once live-server telemetry exists. Owner: this doc with
  `10_systems/ECONOMY.md`.
- The `tradeable`/`untradeable` field's exact name/type has no schema home yet (§4); proposed for
  `20_schemas/item.schema.md` at Phase C.
- Phase D needs a concrete way to mark a one-off quest-minted `etc` item as untradeable (§4) — no
  ID sub-range distinguishes it from an ordinary regional material (`docs/ID_REGISTRY.md`,
  `10_systems/QUESTS.md` §3.1); it must be a per-item authoring flag, not an ID-range rule.
- Whether enhancement level and soft-pity counters (`10_systems/ENHANCEMENT.md`) travel with a
  traded item is assumed **yes** (persisted item state) but not explicitly confirmed by that doc.
- Whether a per-trade `shards` ceiling beyond the receiving wallet cap is needed as an extra
  anti-laundering guard is open; default relies on the wallet cap alone.
- Trade log retention length and any further player-facing exposure beyond a short recent-history
  list is a live-ops / `10_systems/PERSISTENCE.md` policy call, not fixed here.
- Neither `10_systems/HUD.md`'s frame-variant table nor `10_systems/CONTROLS.md`'s input map yet
  assigns a frame type or an open-trade trigger/keybind — flagged for those docs, not designed
  here.

### docs/15_maps_system/MAPS_SYSTEM.md
- `arena_reset_grace_s` (30 s) is a first-pass default; may need per-boss tuning once Phase D
  content exists (e.g., a longer grace for encounters with a long walk-in).
- The render-base lock (screen ≈ 40×22.5 tiles, cited above) resolves `10_systems/SPAWN.md` §2's
  provisional "1 screen-width ≈ 20 tiles" assumption — the real figure is double. SPAWN.md's
  density numbers are authored per-screen (not per-tile) so they do not need renumbering, but its
  owner should update that citation once this doc lands.
- Per-arena quest-flag gates (§8) are left fully to Phase D map authoring; no catalog of which
  arenas use one is proposed here.
- `bgm`/`ambience` tag catalog governance (who prevents duplicate near-synonym tags, e.g.
  `amb_wind` vs. `amb_windy`) is unowned; flag for `40_assets/` at the C gate.
- Whether `interior` should ever allow a scripted, non-zone-spawned combat beat (a forced NPC
  fight) is out of scope here; default holds strictly combat-free per §6.
- Secret-map size guidance (§2) has no WORLD_PLAN precedent to anchor against; first-pass only.

### docs/15_maps_system/MAP_CONNECTIONS.md
- `docs/VALIDATION.md` §5 states cross-region edges "must match `docs/WORLD_PLAN.md`'s edge table
  exactly." `docs/WORLD_PLAN.md` itself delegates the §7 terminus decision to this doc, so that
  phrase should be read (or amended at a future pass) to include this doc's §7 additions as part of
  the authorized edge set. Flagged for `docs/VALIDATION.md`'s owner to confirm/reword — not
  resolved by editing that file here (out of scope for this doc).
- Whether waygate travel (§3) should ever carry a nominal `shards` sink is
  `10_systems/ECONOMY.md`'s call; default here is free, matching P3.
- Freely-authored extra spawn names on multi-entrance maps (§2) have no stricter naming
  convention yet; flag if Phase D authoring shows collisions or ambiguity in practice.
- Whether a map UI visually flags a `dead_end` portal before the player commits to it (§5) is
  `10_systems/HUD.md`'s design call, not decided here.
- The 1:1 mapping from each Rift raid arena to its staging-shard field
  (`10_systems/DEATH_PENALTY.md` §5.3's flagged open item) is still unresolved and is not settled
  by this doc either — it awaits Rift authoring.
- Whether the two new §7 drop-chutes need their own `docs/WORLD_PLAN.md` mention (beyond this
  doc) for discoverability is a light documentation question, not a design one; default is that
  this doc is the sole source for them.

### docs/15_maps_system/MAP_INTERACTABLES.md
- Whether `reactor`/`quest_object` drop references need their own `docs/ID_REGISTRY.md` prefix
  (e.g. a `reactor_drop_NNN` block) or reuse the existing `drop_mob_NNN`/pool space is unresolved —
  flagged for `docs/ID_REGISTRY.md` at the C gate, not decided here.
- `owner_window` (§5) duration and party-sharing rules are entirely `10_systems/DROPS.md`'s once
  authored; this doc only asserts the concept exists.
- `required_quest_flag`'s exact syntax (§10) depends on `10_systems/QUESTS.md`, not yet authored.
- `storage_chest` `scope` (§8) — per-character or account-wide banks — is an open design call for
  `10_systems/ECONOMY.md`/`10_systems/PERSISTENCE.md`.
- `reactor`/`quest_object` default `respawn_timer_s` (60 s) is a first-pass number; may need per-
  region tuning once Phase D populates real material nodes.
- Exact tile-local placement typing (`rect` vs `position` per type) is deferred to
  `20_schemas/map.schema.md` (Phase C); this doc only names which shape each type conceptually
  needs.

### docs/15_maps_system/MAP_LAYERS.md
- Whether one tileset per biome is visually sufficient for a region's more different sub-areas
  (e.g., Sunken Depths' ruin-halls vs. open trenches) is `40_assets/ART_BIBLE.yaml`'s call, not
  resolved here.
- `ambient_tint` values themselves (which color/strength per map) are Phase D content, not
  specified in this systems doc.
- Parallax factor ranges (§1) are first-pass guidance; exact per-map values are an authoring
  choice within the stated bands, not individually validated here.
- Whether `docs/VALIDATION.md` should mechanically check that every map's `tileset_id` matches its
  region's biome key (§4) is a proposal for that doc's owner, not decided here.

### docs/15_maps_system/MAP_TRAVERSAL.md
- `run_speed` (8 tiles/s = 128 px/s) is this doc's own figure for level design; it does not
  currently match `10_systems/COMBAT_FORMULA.md` §10's placeholder `base_move_speed` reference
  (200 px/s), which that doc explicitly flags as pending the tile-scale lock. Once
  `40_assets/ART_BIBLE.yaml` formally locks the 16 px grid, the two figures must be reconciled —
  owner call sits with `10_systems/COMBAT_FORMULA.md` at the C gate; this doc's tiles/s figures
  (and every authored gap in the tree) would need re-validation if the reconciled value changes
  `run_speed`.
- Derived gravity/`v0` (§1) are a mathematical reference, not an independently tuned feel; the
  coding pass (`30_engineering/ENGINEERING_STANDARDS.md`) may retune within the constraint that
  apex/distance/run-speed stay locked.
- `climb_speed` (4 tiles/s) and the manual-dismount hop (1.5 tiles) are first-pass; no other doc
  references them yet.
- Optional status-effect tagging on a hazard (e.g., lava applying `burn`,
  `10_systems/STATUS_EFFECTS.md`) is not specified here — left as a per-hazard-instance Phase D
  authoring choice using `apply_status`'s existing flat-magnitude option
  (`10_systems/SKILL_EFFECTS.md` §14), not a new mechanic.
- Moving-platform param shape (§5) is first-pass pending the real map schema
  (`20_schemas/map.schema.md`, Phase C).
- Whether aquatic/flying monsters ignore `water_gravity_mult` entirely (as `aerial_swooper`
  already ignores platform collision, `10_systems/AI_BEHAVIOR.md` §9) is unresolved; flag for
  `10_systems/AI_BEHAVIOR.md`.
- The drop-through input chord (§3) and climb input (§4) are `10_systems/CONTROLS.md`'s to name;
  not assumed here beyond "an input exists."
