# AUDIO_DESIGN.md — Music, Ambience & SFX Identity

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md, docs/WORLD_PLAN.md,
docs/VALIDATION.md, 15_maps_system/MAPS_SYSTEM.md, 20_schemas/map.schema.md,
40_assets/ART_BIBLE.yaml, 10_systems/HUD.md, 10_systems/PERSISTENCE.md,
10_systems/DEATH_PENALTY.md, 10_systems/ELEMENTS.md, 10_systems/SKILL_EFFECTS.md,
10_systems/STATUS_EFFECTS.md, 10_systems/ITEMS.md, docs/60_agents/roles/ORG.md

Owner doc for **audio design**: the musical identity bound to every `bgm`/`ambience` tag shape
`15_maps_system/MAPS_SYSTEM.md` §5 already defines, the combat/UI SFX family vocabulary, the
conceptual mix (bus layout, ducking, boss-fight behavior), and loop/transition policy. This doc
never redefines the `bgm`/`ambience` tag *shapes* (freeform `snake_case`, no asset paths, one
`bgm` + 0+ `ambience` per map) — those stay MAPS_SYSTEM §5's and `20_schemas/map.schema.md`'s.
It binds **identity** to those shapes and adds a parallel `sfx_` family namespace for combat/UI
sound. The concrete audio asset catalog (actual sample files, licensing, PixelLab-adjacent
sourcing) is a later `40_assets/` pass at Phase C/D — this doc is design prose, not that catalog.

## 1. Scope & non-goals

In scope: per-region music/ambience identity, SFX family naming policy, mix rules, loop/transition
policy, and tag-catalog governance. Out of scope: concrete file names, sample libraries, voice-over,
engine implementation (buses, `AudioStreamPlayer` nodes, etc. — `30_engineering/` territory once a
coding-pass brief exists). No code appears in this doc.

## 2. Bus layout & volume authority

Four conceptual buses feed one `master`: **`music`** (all `bgm_*` tags), **`ambience`** (all
`amb_*` tags, additive/layered), **`combat`** (all combat `sfx_*` families, §5), **`ui`** (all
`sfx_ui_*` families, §6). Each bus exposes one player-facing volume slider plus a master slider;
per `10_systems/PERSISTENCE.md` §3, every one of these sliders is `authority: client` — purely
local presentation preference, never synced to or corrected by a server, even once one exists.
Muting a bus never mutes gameplay-relevant HUD state (e.g., a `boss_bar` still updates with sound
off — `10_systems/HUD.md` §1's `frame_system` chrome is a visual contract independent of audio).

## 3. Per-region music & ambience identity

One `bgm_<biome_key>` identity per region (shared across its field/dungeon/secret maps, P3 biome
identity), one `bgm_town_<region_slug>` where a region has a town, one `bgm_boss_<region_slug>`
per regional arena, and a short list of `amb_<texture>` tags a region's maps draw from. Biome keys
and motifs are `docs/WORLD_PLAN.md`'s and `40_assets/ART_BIBLE.yaml`'s `biome_identity` (locked,
cited not restated); ambience textures are reused verbatim across regions that share a texture
(MAPS_SYSTEM §5) rather than re-invented per region.

| Region (slug) | `biome_key` | `bgm` tags (field · town · boss) | `amb_` examples | Musical identity |
|---|---|---|---|---|
| Emberfoot Isle (`emberfoot`) | `emberfoot` | `bgm_emberfoot` · `bgm_town_emberfoot` · `bgm_boss_emberfoot` | `amb_wind`, `amb_embers` | Warm pastoral: acoustic strings/pipes, unhurried major-key motif — matches WORLD_PLAN's "warm, safe, first-steps" and ART_BIBLE's cinders/cracked-basalt/warm-haze motif. |
| Millbrook & Rosen Harbor (`millbrook`) | `old_town` | `bgm_old_town` · `bgm_town_millbrook` · `bgm_boss_millbrook` | `amb_crowd`, `amb_wind` | Cozy market theme: accordion/lantern-lit strings, a lived-in, unhurried tempo — matches "cozy, lantern-lit" and old_town's timber/thatch/cobble/lantern motif. |
| Verdant Hollow (`verdant`) | `verdant_hollow` | `bgm_verdant_hollow` · `bgm_town_verdant` · `bgm_boss_verdant` | `amb_canopy`, `amb_drip` | Lush woodwind theme, dappled arpeggios with a minor undertone creeping in — matches "lush, dappled, first real danger" and verdant_hollow's mossy-stone/roots motif. |
| Tidewatch Coast (`tidewatch`) | `tidewatch` | `bgm_tidewatch` · `bgm_town_tidewatch` · `bgm_boss_tidewatch` | `amb_surf`, `amb_gulls` | Bright brine theme: rolling arpeggios over a tidal low end, a chime motif for bioluminescence — matches "bright brine, undertow" and tidewatch's wet-stone/kelp motif. |
| Gloomwood (`gloomwood`) | `gloomwood` | `bgm_gloomwood` · *(no town)* · `bgm_boss_gloomwood` | `amb_canopy`, `amb_wind` | Sparse, hushed theme: long sustained tones, near-silence between phrases so the player feels watched — matches "hush, being watched"; shares the verdant ramp with R3, pitched darker and slower. |
| Ashfall Barrens (`ashfall`) | `ashfall` | `bgm_ashfall` · `bgm_town_ashfall` · `bgm_boss_ashfall` | `amb_wind`, `amb_embers` | Oppressive-heat theme: a droning low-brass/percussion ostinato, steady and unrelenting — matches "oppressive heat, endurance"; shares the ember ramp with R1, harsher timbre. |
| Sunken Depths (`sunken`) | `tidewatch_dark` | `bgm_tidewatch_dark` · *(no town)* · `bgm_boss_sunken` | `amb_drip`, `amb_surf` | Drowned-terminus theme: submerged and reverberant, a slow descending motif with bioluminescent chime accents — matches the region's bioluminescent-gloom description; shares the tide ramp with R4, darker and slower. |
| Clockwork Ruins (`clockwork`) | `clockwork` | `bgm_clockwork` · *(no town)* · `bgm_boss_clockwork` | `amb_gears`, `amb_wind` | Awe-and-precision theme: a ticking mechanical ostinato under brass swells, tension tightening toward the endgame — matches "awe, trespass, precision" and clockwork's gears/brass motif. |

`bgm_town_*`/`bgm_boss_*` use the region **slug**; field/dungeon/secret `bgm` uses the region's
**`biome_key`** — the two differ for Millbrook (`old_town`) and Sunken (`tidewatch_dark`), per
MAPS_SYSTEM §5's own note. Gloomwood, Sunken, and Clockwork have no town map in WORLD_PLAN's
region layout, so they carry no `bgm_town_*` identity.

## 4. Town/interior mood variants

`bgm_interior_<mood>` (MAPS_SYSTEM §5) is the hushed-variant escape hatch for an interior that
should not simply inherit its town's `bgm_town_*` track. This doc recommends a small, reusable
mood vocabulary rather than one-off moods per building: `bgm_interior_hearth` (inn — warm, sparse,
a single instrument) and `bgm_interior_hush` (guild hall/library-type rooms — near-silent,
ambience-forward). Ordinary shops and halls default to inheriting `bgm_town_<region_slug>`
unmodified; a `bgm_interior_<mood>` tag is the exception, not the rule.

## 5. Combat SFX families

A new `sfx_` tag namespace, same `snake_case` shape as `bgm_`/`amb_`, no asset paths — families
only, not a concrete asset list (that is `40_assets/`'s later catalog pass).

| Family | Trigger | Notes |
|---|---|---|
| `sfx_hit_normal` / `sfx_hit_crit` | Any `deal_damage` resolution (`10_systems/SKILL_EFFECTS.md`) | Crit variant is louder/brighter, never later — timed to the same animation `hit` frame as the damage number (P1 hit-frame honesty). |
| `sfx_cast_<element>` | Skill cast per `10_systems/ELEMENTS.md` element (`neutral`/`fire`/`frost`/`nature`/`arcane`/`shadow`) | One family per element, reused by every skill of that element regardless of job line. |
| `sfx_status_apply` / `sfx_status_cleanse` | `apply_status` / `cleanse_status` ops (`10_systems/SKILL_EFFECTS.md`) | Generic chime pair, not one family per individual status token — status *type* nuance (burn vs. stun) is a volume/tone note for the later catalog, not a new family here. |
| `sfx_pickup_<rarity>` | Item pickup, keyed to `10_systems/ITEMS.md` rarity tiers (`common`…`legendary`) | Escalating chime richness up the rarity ladder. |
| `sfx_levelup` | Level-up (`10_systems/LEVELING.md`) | One fanfare family, no per-job variant. |
| `sfx_death` | `die` animation state (`40_assets/ANIMATION_STATES.md`, `10_systems/DEATH_PENALTY.md` §1) | Single stinger, see §10. |

## 6. UI SFX families

| Family | Trigger |
|---|---|
| `sfx_ui_confirm` | Accepting a `frame_dialog` modal, turning in a quest, vendor confirm (`10_systems/HUD.md` §1) |
| `sfx_ui_cancel` | Closing/backing out of any `frame_window`/`frame_dialog` |
| `sfx_ui_navigate` | Cursor/focus movement across `frame_slot` grids (inventory, skill bar, quickslots) |
| `sfx_ui_error` | Invalid action (can't-afford, wrong slot, on-cooldown) |
| `sfx_ui_toast` | Toast-stack notifications (`10_systems/HUD.md` §2) |

## 7. Mix rules — bus priority and ducking

The `combat` bus is never ducked by `music` or `ambience` — P1's hit-frame honesty requires
`sfx_hit_*` to be perceptible at the exact animation frame the damage lands, so nothing may mask
it, ever. Above that: `ui` transiently ducks `music` + `ambience` (not `combat`) for the short
duration of an `sfx_ui_confirm`/`sfx_ui_error` cue, so a modal reads clearly over background music.
`sfx_death` (§10) is the one cue allowed to duck `combat` itself, briefly, since combat has already
ended for that character. Priority order, highest first: `combat` > `sfx_death` > `ui` >
`ambience` > `music`.

## 8. Boss-fight mix behavior

On arena entry, `bgm_boss_<region_slug>` replaces the field/dungeon `bgm` outright (no layering
of the two); the `ambience` bus thins to zero or one `amb_` tag so the `combat` bus reads clearly
against a denser boss encounter. A `phase_shift` animation state (`40_assets/ANIMATION_STATES.md`)
triggers a one-shot stinger layered over the still-looping `bgm_boss_*` track rather than a tag
change — bosses keep one `bgm_boss_*` identity across every phase, not one per phase.

## 9. Loop & transition policy

Every `bgm`/`amb` tag loops seamlessly (no audible seam or hard restart). Crossing a portal:

- **Same `bgm` tag on both maps** (the common case along a field chain, P3): the track keeps
  playing uninterrupted, no fade at all.
- **Different `bgm` tag** (region boundary, town entry/exit, arena entry/exit): a short crossfade
  (on the order of one to two seconds) between old and new track. Arena entry additionally allows
  the boss stinger (§8) to play over the crossfade's tail rather than waiting for it to finish.
- **`ambience` tags are independent and additive**: comparing the departure map's `amb_` list to
  the arrival map's, shared tags keep playing through the transition uninterrupted, tags absent
  from the new map fade out, and tags newly present fade in — never a blanket ambience cut.
- **Island crossing** (the paid Harborwind Ferry, `docs/WORLD_PLAN.md`): treated as a town-grade
  `bgm` change like any other region boundary, with its own brief ambience texture during the
  crossing itself (e.g., a gulls/surf texture) rather than either island's field `bgm`.

## 10. Death & respawn audio

On the `die` animation state (`10_systems/DEATH_PENALTY.md` §1), `sfx_death` plays once, `combat`
ducks briefly per §7, and `music`/`ambience` hold their current tag rather than cutting to silence
— death is a sting, not a mix reset (P2, "death stings but never deletes an evening"). No
recurring post-death audio motif exists, matching DEATH_PENALTY.md's explicit rejection of any
"weakened on return" state: a death never leaves an audio residue into the next few minutes of
play. On respawn at the character's bound town (DEATH_PENALTY.md §4), the town's `bgm_town_*`
identity resumes or crossfades in exactly as any ordinary arrival would (§9) — respawn is not a
special-cased transition.

## 11. Tag-catalog governance — resolves MAPS_SYSTEM.md's open item

MAPS_SYSTEM.md's Open Questions flags `bgm`/`ambience` tag-catalog governance ("who prevents
duplicate near-synonym tags, e.g. `amb_wind` vs. `amb_windy`") as unowned, pending `40_assets/` at
the C gate. **Decision: this doc is that governor**, for `bgm_`/`amb_`/`sfx_` alike. §3's table is
the canonical per-region `bgm`/`amb` identity list; any new tag proposed during Phase D content
authoring is checked against it first — a near-synonym is folded into the existing tag, not added
alongside it. Genuinely new tags (a texture or family §3/§5/§6 don't cover) are proposed here via
an Open Question, not invented silently in a content file (`docs/VALIDATION.md` §1's spirit, same
enforcement shape as GLOSSARY tokens even though `bgm`/`amb`/`sfx` tags are not GLOSSARY entries).
`40_assets/` still owns turning a governed tag into a concrete sample/license, per MAPS_SYSTEM §5.

## Open Questions

- Footstep/movement SFX (material-dependent, tied to `terrain_chunk`/foothold surface) is not
  scoped in this pass — flag for a future revision once `15_maps_system/MAP_TRAVERSAL.md`'s
  foothold-material vocabulary is finalized; no family name is assumed here.
- Do the two party quests (`pq_undervault`, `pq_mainspring`) need bespoke instance `bgm` distinct
  from their host region's dungeon/arena tags, or do they simply reuse the host region's identity
  per §3/§8? Default assumed here: reuse host-region tags; flag for
  `10_systems/social/PARTY_QUEST.md` to confirm or override.
- Per-status SFX granularity (§5's `sfx_status_apply`/`cleanse` pair vs. a richer set split by
  `10_systems/STATUS_EFFECTS.md`'s cleanse-tag families) is deferred to the 40_assets catalog pass;
  default here is the generic two-family policy unless that pass finds it insufficient.
- Whether `sfx_ui_navigate` needs a distinct cue per `10_systems/HUD.md` frame variant (e.g.
  `frame_slot` grid nav vs. chat input) or one shared cue for all UI navigation — default assumed
  here is one shared cue; flag for a HUD.md-side confirmation if playtesting disagrees.
