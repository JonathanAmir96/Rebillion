# DEATH_PENALTY.md — Player Defeat & Recovery

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, 10_systems/STATS.md,
10_systems/STATUS_EFFECTS.md, 10_systems/SPAWN.md, 10_systems/SKILL_EFFECTS.md,
10_systems/social/PARTY.md, 10_systems/social/RAID.md, 10_systems/LEVELING.md, 10_systems/ECONOMY.md,
15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_CONNECTIONS.md, 40_assets/ANIMATION_STATES.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for what happens when a player character is defeated: the exp cost, what is (and is
deliberately not) lost, where the character respawns, how context (field/dungeon/arena/raid)
changes that flow, and the current boundary around revival. Nothing here redefines combat,
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
| 2nd job (specialization) | 40+ | 3% | A real but small setback |

Exp loss never de-levels (the clamp above). The game cap is **300** (`00_vision/SCOPE.md`); the
authored arcs top out at Lv 82, and brackets for the future arcs above that (3rd-tier jobs, the
climb to cap) are deferred until those arcs are designed (Open Questions).

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

**Valid bind towns** (the towns with an inn interior, `docs/WORLD_PLAN.md` v3) — arc 1:
Emberfoot Village (`map_001`), Millbrook Central (`map_018`), Mossmere (`map_043`), Tidewatch
Port (`map_071`), Cindershelf (`map_125`); arc 2: Frosthaven (`map_204`), Spirehaven
(`map_245`), Duskwatch Landing (`map_285`). The remaining towns (Rosen Harbor, Wyrmcrag Hold,
Highrune Sanctum, Lastlight Redoubt) carry no inn interior in `docs/WORLD_PLAN.md`'s map lists
and are not bind towns. `10_systems/INVENTORY.md` §7 cites this same list for bank access.

On defeat, the character respawns at its bound town's `main` spawn point (`docs/WORLD_PLAN.md`
"Spawn-point convention"). Getting from the bind town back to wherever the character died is
ordinary travel — the transport network (the paid Harthmoor Coachworks, the Harborwind Ferry,
arc-2 longships) and its fares belong to `15_maps_system/MAP_CONNECTIONS.md` and are not redefined
here; death grants no free or discounted transit (`15_maps_system/MAP_CONNECTIONS.md` §4). This doc
names only the respawn destination, never the route back.

Regions without a bind town — Gloomwood, Sunken Depths, and the Clockwork Ruins
(`docs/WORLD_PLAN.md`) — have no local bind option: a character leveling there simply respawns at
whichever town it last rested in, then travels back in via the normal network. Nearest binds by
the world graph: Mossmere or Cindershelf for Gloomwood (entered from Verdant or Ashfall),
Tidewatch Port for the Sunken Depths, Cindershelf for the Clockwork Ruins.

## 5. Death by context

### 5.1 Field and dungeon deaths
Standard flow: `die` plays, statuses clear, §2/§3 penalties apply, character respawns per §4.
Whether cleared trash mobs or other zone state reset on a death is a zone-reset rule owned by
`15_maps_system/MAPS_SYSTEM.md` — this doc governs only the player's own respawn point and
stat/currency/exp consequences, never zone content state.

### 5.2 Boss arena deaths (regional, non-raid)
Same flow as §5.1. The boss encounter itself resets on the player's exit/respawn — re-entering the
arena starts a fresh attempt at full boss life. Boss respawn/instancing mechanics are owned by
`10_systems/SPAWN.md` (timer policy) and `15_maps_system/MAPS_SYSTEM.md` (arena scripting); this
doc does not redefine them, only that the player's own consequence is the standard §2/§3/§4 flow.

### 5.3 Raid deaths (every `raid_*` instance, `10_systems/social/RAID.md` §2's roster)
A death inside a raid instance does not use §4 directly — the rule is per **entry context**, not per
raid, so it covers a raid whose stage maps are shared with the open world (`raid_orrery`,
`10_systems/social/RAID.md` §4) inside the instance only; a death on the open copy of those maps is
an ordinary dungeon death (§5.1). The **run** — stage chain, full-wipe handling, retry,
and the clear cooldown — is owned by `10_systems/social/RAID.md` §5, which consumes this
section's per-character mechanics unchanged:

1. `die` plays and statuses clear as above; the character enters a **fallen** state:
   untargetable, no actions except **Release**. It remains a party member for
   `10_systems/social/PARTY.md` purposes — the run continues without it.
2. The player may **Release** at any time (no forced timer). Releasing applies the standard
   §2/§3 penalties for the character's level bracket — a raid death costs exactly what a field
   death costs — and moves the character to the raid's **staging area** (the herald's map,
   `10_systems/social/RAID.md` §3), **not** to the character's bound town. This is a deliberate
   override of §4 scoped to raid instances only; it does not change the stored bind point.
3. While the attempt is still live (the party has not wiped), the released player may **re-enter**
   the instance and rejoin; re-entry routing is `10_systems/social/RAID.md` §3/§5's. There is no
   re-entry cooldown beyond the walk back.
4. **Full wipe** ends the attempt and dissolves the instance per `10_systems/social/RAID.md` §5;
   a new entry starts at stage 1. Instance allocation is `10_systems/SPAWN.md` §7's.

On-the-spot revival of a fallen ally without releasing is not available in this pass — see §6.

## 6. Revive — reserved for a future skill op

None of the 14 skill effect ops in `00_vision/GLOSSARY.md` (owner `10_systems/SKILL_EFFECTS.md`)
revive a fallen character — `heal` and the `regen` status (`10_systems/STATUS_EFFECTS.md`) only
affect entities still standing. Mid-encounter revival (a party member picking up a fallen ally, as
opposed to the self-service Release in §5.3) is intentionally **not implemented** in this pass and
requires a new effect op proposed by `10_systems/SKILL_EFFECTS.md` — and promoted through the
`00_vision/GLOSSARY.md` Provisional process — before any skill can grant it. Until that lands,
§5.3's release-and-reenter is the only recovery path in raid content, and field/dungeon/arena
deaths have no revive option at all (respawn is the only path).

## Open Questions
- Exact `pct` values (§2) are first-pass balance; owner for retuning is this doc, informed by
  `10_systems/LEVELING.md`'s eventual exp curve.
- **Partially resolved (2026-07-24 md audit):** the party-frame half is settled —
  `10_systems/HUD.md` §4.1 renders fallen members (desaturated plate + fallen glyph, resolving
  this doc's flag on the HUD side). Loot eligibility while fallen remains
  `10_systems/social/PARTY.md` §6's call — still flagged there.
- Rebind cost: is resting at a new inn free, or does it cost `shards`/carry a cooldown? Default
  assumed **free**; owner `10_systems/ECONOMY.md` may add a fee.
- A revive skill effect op (§6) is proposed for `10_systems/SKILL_EFFECTS.md` to pick up as
  Provisional; it is not defined here and no op name is assumed.
- Dungeon/zone content-reset-on-death behavior (§5.1) is flagged for
  `15_maps_system/MAPS_SYSTEM.md` to confirm, not assumed here.
- §5.3's Release destination (the raid's staging area / herald's map) is a v3 first-pass; the
  concrete instance-door wiring per raid is `10_systems/social/RAID.md` §3 +
  `15_maps_system/MAP_CONNECTIONS.md`'s to confirm when raid maps are authored.
- Exp-loss brackets between the authored Lv 82 top and the Lv 300 cap (3rd-tier jobs, future
  arcs), and behavior at cap itself, are deferred with those arcs (§2); they inherit
  `00_vision/SCOPE.md`'s post-arc progression question. The 2nd-job 3% row holds provisionally
  across the authored 40–82 range.
