# DEATH_PENALTY.md — Player Defeat & Recovery

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, 10_systems/STATS.md,
10_systems/STATUS_EFFECTS.md, 10_systems/SPAWN.md, 10_systems/SKILL_EFFECTS.md,
10_systems/social/PARTY.md, 10_systems/social/PARTY_QUEST.md, 10_systems/LEVELING.md,
10_systems/ECONOMY.md,
15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_CONNECTIONS.md, 40_assets/ANIMATION_STATES.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for what happens when a player character is defeated: the exp cost, what is (and is
deliberately not) lost, where the character respawns, how context (field/dungeon/arena/party
quest) changes that flow, and the current boundary around revival. Nothing here redefines combat,
status, or travel rules owned elsewhere — it only defines the *consequence* of `life` reaching 0.

## 1. Defeat trigger

Defeat occurs when a character's `life` reaches 0 (`10_systems/STATS.md` §2). The `die` animation
state plays (`40_assets/ANIMATION_STATES.md`), and all active statuses — buffs and debuffs alike
— clear immediately, with no post-mortem ticks (`10_systems/STATUS_EFFECTS.md` §1; not restated).
Control returns to the player only after the respawn flow below resolves. There is **no**
temporary post-respawn debuff (no "weakened on return" status) — deliberately excluded so a death
never compounds into a second, smaller death (`00_vision/PILLARS.md` P2).

## 2. Experience loss on defeat

Defeat costs a percentage of the character's **current-level exp progress** — never total
accumulated exp, and never enough to push the character below the floor of its current level.
This makes de-leveling structurally impossible rather than a rule to remember.

**Formula:** `exp_lost = floor(pct * exp_into_level)`; the character's new `exp_into_level` is
`exp_into_level - exp_lost`, which is always ≥ 0 since `pct ≤ 1`. The exp curve and per-level
threshold are owned by `10_systems/LEVELING.md`; this doc defines only `pct` and the clamp.

| Job tier (`10_systems/JOBS.md`) | Levels | `pct` lost | Feel |
|---|---|---|---|
| Novice | 1–7 | 0% | Grace band — tutorial safety |
| 1st job | 8–39 | 1% | Barely noticeable |
| 2nd job | 40+ | 3% | A real but small setback |

Exp loss never reduces `level` (the clamp above), and at the cap (300) there is no exp progress
to lose; finer brackets for future-arc bands (3rd jobs and beyond) are deferred until those arcs
land.

Cause of defeat (monster tier, `field` vs `dungeon`, environmental) never changes `pct` — only the
victim's own level bracket does. One rule, no hidden cases (`00_vision/PILLARS.md` P1).

## 3. Durability and currency — decision: no durability, shards always intact

- **No item durability system exists anywhere in this tree.** Equipment never degrades, breaks,
  or requires repair, whether from defeat or ordinary use. There is no `durability` field on any
  item schema.
- **`shards` are never lost, dropped, or reduced on defeat.** Currency is earned in-world only
  (`00_vision/PILLARS.md` anti-pillars) — defeat is not a currency sink.
- **Rationale:** P2 ("death stings but never deletes an evening") and the anti-pillar against
  pay-style economy design. A durability/repair loop would also demand a `shards`-sink repair
  vendor and a wear field on every equip item — new surface area no pillar asks for.

## 4. Respawn location — decision: bind point via inn

Every character carries one **bind point**, set by resting at an inn interior in a town. Default
bind for a new character is the starting town, **Emberfoot Village** (`map_001`). Binding changes
only when the player deliberately rests at a different town's inn — never automatically on death,
travel, or level-up.

**Valid bind towns** (the 6 towns, `docs/WORLD_PLAN.md`): Emberfoot Village (`map_001`),
Rosen Harbor (`map_017`), Millbrook Central (`map_018`), Mossmere (`map_043`), Tidewatch Port
(`map_071`), Cindershelf (`map_125`).

On defeat, the character respawns at its bound town's `main` spawn point (`docs/WORLD_PLAN.md`
"Spawn-point convention"). Getting from the bind town back to wherever the character died is
ordinary travel — walking the ring, the paid Harthmoor Coachworks network (rules and fares belong
to `15_maps_system/MAP_CONNECTIONS.md`), or the Millbrook Return Scroll (`item_use_0013`); this
doc names only the respawn destination, never the route back.

Regions without their own town (Gloomwood, Sunken Depths, Clockwork Ruins) have no local bind
option — a character leveling there simply respawns at whichever town it last rested in, then
travels back in via the normal network (nearest ring bind towns: Gloomwood → Mossmere or
Cindershelf; Sunken Depths → Tidewatch Port; Clockwork Ruins → Cindershelf via the char-ridge
gate).

## 5. Death by context

### 5.1 Field and dungeon deaths
Standard flow: `die` plays, statuses clear, §2/§3 penalties apply, character respawns per §4.
Whether cleared trash mobs or other zone state reset on a death is a zone-reset rule owned by
`15_maps_system/MAPS_SYSTEM.md` — this doc governs only the player's own respawn point and
stat/currency/exp consequences, never zone content state.

### 5.2 Boss arena deaths (the 8 regional bosses)
Same flow as §5.1. The boss encounter itself resets on the player's exit/respawn — re-entering the
arena starts a fresh attempt at full boss life. Boss respawn/instancing mechanics are owned by
`10_systems/SPAWN.md` (timer policy) and `15_maps_system/MAPS_SYSTEM.md` (arena scripting); this
doc does not redefine them, only that the player's own consequence is the standard §2/§3/§4 flow.

### 5.3 Party-quest deaths (`pq_undervault`, `pq_mainspring`)
Death handling inside the two party quests is owned by `10_systems/social/PARTY_QUEST.md`; the
standard §2/§3/§4 exp-loss and respawn flow applies.

## 6. Revive — reserved for a future skill op

None of the 14 skill effect ops in `00_vision/GLOSSARY.md` (owner `10_systems/SKILL_EFFECTS.md`)
revive a fallen character — `heal` and the `regen` status (`10_systems/STATUS_EFFECTS.md`) only
affect entities still standing. Mid-encounter revival (a party member picking up a fallen ally) is
intentionally **not implemented** in this pass and requires a new effect op proposed by
`10_systems/SKILL_EFFECTS.md` — and promoted through the `00_vision/GLOSSARY.md` Provisional
process — before any skill can grant it. Until that lands, respawn is the only recovery path for
field/dungeon/arena deaths, and party-quest death flow follows
`10_systems/social/PARTY_QUEST.md` (§5.3).

## Open Questions
- Exact `pct` values (§2) are first-pass balance; owner for retuning is this doc, informed by
  `10_systems/LEVELING.md`'s exp curve.
- Rebind cost: is resting at a new inn free, or does it cost `shards`/carry a cooldown? Default
  assumed **free**; owner `10_systems/ECONOMY.md` may add a fee.
- A revive skill effect op (§6) is proposed for `10_systems/SKILL_EFFECTS.md` to pick up as
  Provisional; it is not defined here and no op name is assumed.
- Dungeon/zone content-reset-on-death behavior (§5.1) is flagged for
  `15_maps_system/MAPS_SYSTEM.md` to confirm, not assumed here.
- Exp-loss brackets for future arcs (the Lv 42+ bands on the road to cap 300, including the
  reserved 3rd jobs) are deferred; the 2nd-job 40+ bracket (§2) holds until those arcs land.
