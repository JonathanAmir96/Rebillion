# MAP_CONNECTIONS.md — Portal Rules, Spawn Naming & the World Graph

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
docs/ID_REGISTRY.md, 10_systems/DEATH_PENALTY.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md,
10_systems/HUD.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md

Owner doc for the **rules** portals, spawns, and the transport network follow between maps.
`docs/WORLD_PLAN.md`'s "Cross-region walk edges," "Harthmoor Coachworks," and arc-2 longship
tables are the sole authoritative source for *which* `map_NNN` pairs connect — they are cited,
never reproduced, here. This doc formalizes the spawn-naming convention `docs/WORLD_PLAN.md`
previews, the paid coach-network rule, death-return routing, `dead_end` marking, the
region-progression gate policy, the arc-2 longship and `level_gate` primitives (§§8–9), and
resolves `docs/WORLD_PLAN.md`'s terminus open question. Portal object params are
`15_maps_system/MAP_INTERACTABLES.md` §2's; this doc owns only the rules governing them.

## Transport taxonomy (v3)

Every way a character moves between maps, and where each mode is owned. The kinds are fixed by two
axes — **paid vs free** and **instant vs scheduled**:

| Mode | Cost / timing | Scope | Rules / fare owner |
|---|---|---|---|
| **Walk edges** (`edge` portals) | free · instant | intra-region + the authorized cross-region walk edges (`docs/WORLD_PLAN.md` edge table, + §7) | this doc §§1–2, §5 |
| **Coach** (Harthmoor Coachworks) | paid · **instant** | Harthmoor town↔town network | `docs/WORLD_PLAN.md` (Coachworks); fares `10_systems/ECONOMY.md` §7.1 |
| **Harborwind Ferry** | paid · **instant** | Emberfoot ↔ Harthmoor island crossing (`map_015`) | `docs/WORLD_PLAN.md`; fare `10_systems/ECONOMY.md` §7.1 |
| **Longship** (v3) | paid · **scheduled** | arc-2 inter-island network (Harthmoor pier ↔ new islands; `docs/WORLD_PLAN.md` arc-2 edge table) | this doc **§8**; fares `10_systems/ECONOMY.md` §7.2 |
| **Millbrook Return Scroll** (`item_use_0013`) | consumable item | escape to bound home town | `10_systems/ITEMS.md`; price `10_systems/ECONOMY.md` §4.1 |

The contrast that fixes the kinds: coaches and the ferry are **paid but instant**; the longship is
**paid and scheduled** — a real-time deck ride (§8). The ferry stays instant at launch (its
scheduled-sailing idea remains `docs/WORLD_PLAN.md`'s existing Open Question, untouched here).

## 1. Portal kind semantics between regions

The four portal kinds are `edge` · `door` · `coach` · `longship`; any kind may additionally carry
the optional `level_gate` property (§9) — that is a per-portal property, not a kind of its own.

| Kind | Typical use | Region span |
|---|---|---|
| `edge` | Most field/dungeon chain links; the cross-region walk edges (`docs/WORLD_PLAN.md`) | Usually intra-region; cross-region for the listed edges (+ §7's two additions) |
| `door` | Town↔interior; every arena's entry gate (`15_maps_system/MAPS_SYSTEM.md` §8); the Harborwind Ferry crossing (`map_015`) and the Deepway (§9.1) | Same-region for town↔interior and arena gates; the ferry and the Deepway are the authored cross-region door cases |
| `coach` | The paid Harthmoor Coachworks town↔town network (`docs/WORLD_PLAN.md` "Harthmoor Coachworks") | Cross-region within the Harthmoor ring — that is its purpose |
| `longship` (v3) | Paid **scheduled** arc-2 inter-island transport: pier→deck boarding portal and deck→destination-pier arrival portal (§8) | Cross-island (arc-2 island network) |

## 2. Spawn-point naming law

Formalizes the convention `docs/WORLD_PLAN.md`'s "Spawn-point convention" paragraph previews.
Three tokens are **reserved**; a map may also author additional freely-named spawns (e.g. a
multi-entrance dungeon's `upper_west`) as long as they never collide with the reserved set.

| Spawn name | Required on | Meaning |
|---|---|---|
| `main` | Every map, exactly one | Default arrival point — direct teleport, quest-start, and the fallback target for any portal that doesn't name another spawn |
| `from_<origin_slug>` | Every map that is the destination of an `edge` portal crossing a region boundary | `<origin_slug>` is the origin **region**'s GLOSSARY slug (not a per-map slug — maps have none). An intra-region `edge` targets plain `main` unless the destination map has multiple distinct entrances needing disambiguation |
| `coach_stop` | Every map with a `coach_station` (`15_maps_system/MAP_INTERACTABLES.md` §9) | The fixed arrival point for all Harthmoor Coachworks transits; exactly one per coach-station map (`docs/00_vision/GLOSSARY.md` Transport token) |

Each of `docs/WORLD_PLAN.md`'s 8 bidirectional cross-region edges produces exactly two
`from_<origin_slug>` spawns (one per endpoint, each named for the *other* side's region) — e.g.
the Emberfoot↔Verdant edge gives Verdant's endpoint a `from_emberfoot` spawn and Emberfoot's
endpoint a `from_verdant` spawn.

**v3 (longship transport spawns):** §8 reserves two further transport-network spawns following
this same law — `longship_deck` (the boarding point on every longship deck map) and
`longship_dock` (the arrival point on every longship destination pier) — analogous to
`docs/WORLD_PLAN.md`'s existing `coach_stop` / `from_ferry` transport spawns. They are proposed as
`docs/00_vision/GLOSSARY.md` Transport tokens alongside `coach_stop`.

## 3. Coach network — the Harthmoor Coachworks

**The ring is walked; the coach is the paid shortcut, never a free warp** (P3: travel is a
low-friction loop, but low-friction is not free). The rules live here; the concrete stations and
their edges are `docs/WORLD_PLAN.md`'s ("Harthmoor Coachworks"), cited never restated; the `shards`
fares are `10_systems/ECONOMY.md` §7.1's.

- **Stations, always open.** A `coach_station` (`15_maps_system/MAP_INTERACTABLES.md` §9) sits in
  each Harthmoor ring town `docs/WORLD_PLAN.md` names. Every station is available to every character
  from creation — there is **no per-character unlock, no unlock set, and no cooldown** (the
  free-forever unlock model this section once carried is retired with the token it belonged to).
- **Fare, paid every ride.** Interacting with a `coach_station` opens a destination menu
  (`10_systems/HUD.md`) of the other stations; selecting one charges the `shards` fare
  (`10_systems/ECONOMY.md` §7.1, scaling with ring distance) and triggers the co-located
  `portal(kind: coach)` (`15_maps_system/MAP_INTERACTABLES.md` §2) to that station's `coach_stop`
  spawn. The fare is charged **at selection**; an aborted or unaffordable choice moves no one and
  costs nothing.
- **One free novice pilgrimage.** The Rosen Harbor coach gives each character exactly one free ride
  to their job-line instructor's town (`docs/WORLD_PLAN.md`'s advancement pilgrimage) — a one-time,
  per-character, server-authoritative flag (`10_systems/PERSISTENCE.md`). Every ride after that pays
  the §7.1 fare.
- **No free warps otherwise.** Emberfoot Isle has no coach — its island crossing is the paid
  Harborwind Ferry (§1) — and the Millbrook Return Scroll (`item_use_0013`) remains the only
  item-based escape home (`10_systems/ITEMS.md`). Nothing on the map graph teleports for free.

## 4. Death-return routing

`10_systems/DEATH_PENALTY.md` owns death **policy**: §4 the bind mechanic and the respawn
destination (a bound town's `main` spawn), and §5.3 the Rift-raid release to a staging-shard field.
Neither is restated here. This doc owns only the *world-graph* consequence — where a respawned or
released character lands, and how it travels back — and fixes one rule: **the route back to the
frontier is ordinary travel, never a death-only path.**

- **Standard respawn.** A defeated character lands at its bound town's `main`
  (`10_systems/DEATH_PENALTY.md` §4) and reaches the frontier exactly as anyone does: walking the
  ring, paying a coach (§3) where the bound town carries a Coachworks station, taking the ferry (§1)
  or an arc-2 longship (§8), or spending a Millbrook Return Scroll. **Death grants no free,
  discounted, or special-cased transit** — the paid modes cost precisely what they cost in life (the
  old free-warp-home routing is gone with the retired free-warp model it belonged to). There is no world-graph
  guarantee a bound town even has a coach station: a character bound outside the Harthmoor ring
  (e.g. Emberfoot Village) simply walks, ferries, or scrolls back, uncharged for having died.
- **Rift-raid release.** A released raider lands at that raid's staging-shard field rather than its
  bound town (`10_systems/DEATH_PENALTY.md` §5.3); the 1:1 raid-arena→staging-shard assignment is an
  open item both that doc and this one flag (Open Questions).

## 5. `dead_end` marking

Per `docs/VALIDATION.md` §5: any portal with **no matching reverse portal** on its destination map
must carry `dead_end: true`, authored on the portal that *leads into* the one-way transition (not
on the destination side). This is a validator-exemption flag only — it tells the world-graph
checker "do not require a reverse portal here" — not a required visible UI marker, though a map UI
may optionally surface it (`10_systems/HUD.md`'s call, not specified here). Ordinary `edge`/`door`/
`coach` portals, which always pair with a reverse, are never marked `dead_end`.

## 6. Region-progression gate policy: none

**Decision: no authored region-to-region progression gate exists anywhere in the arc-1 portal
system** — no level lock, quest-flag lock, or item-key lock on any region boundary (contrast with
an optional *per-arena* quest-flag gate, `15_maps_system/MAPS_SYSTEM.md` §8, a narrower, different
concern). A Lv 1 character can walk into a Lv 90 region; nothing here stops them. The only gate is
the emergent difficulty curve: `10_systems/COMBAT_FORMULA.md` §9's level-difference dampener makes
a badly under-level fight genuinely hard well before it's mechanically blocked, reinforced by
`10_systems/LEVELING.md`'s exp curve (which consumes that same §9 table) cratering reward for
over-level kills, and `docs/WORLD_PLAN.md`'s world-graph spine naturally lands a region-by-region
player roughly in-band anyway. This is deliberate (P2 — no trap walls, only a hard-but-not-
impossible curve) and matches §3's coach network, which also never gates on `level`.

**v3 scope note:** the "none" policy above describes the **arc-1 Harthmoor ring**, where no boundary
is gated and every portal is ungated. Arc-2 introduces exactly one deliberate exception *primitive* —
the `level_gate` portal property (§9), debuting on the Deepway (Lv 40+). It is a **visible,
signposted** requirement (the player sees the door and the level it wants), not a hidden trap wall,
so it honors the same P2 intent this section serves; it gates a single authored arc-1→arc-2
threshold, not the emergent region curve, which §6 still governs everywhere else.

## 7. Terminus decision — Frostpeak & Clockwork drop chutes

`docs/WORLD_PLAN.md` flags an open question, explicitly delegated to this doc: should Frostpeak
and Clockwork — both deliberate branch termini — get a late-game shortcut back toward Millbrook
besides the return scroll? **Decision: yes.** Both termini get a one-way drop chute from their
region's arena back down to a re-entry field in the neighboring region, so a player who has
just finished the terminus content isn't forced to walk the whole chain back or spend a return
scroll.

| Terminus | New portal on | Kind | `target_map` | `target_spawn` (new) | `dead_end` |
|---|---|---|---|---|---|
| Frostpeak (The Hornfall Summit) | `map_108` | `edge` | `map_073` (an Ashfall re-entry field) | `from_frostpeak` | `true` |
| Clockwork (The Mainspring) | `map_144` | `edge` | `map_109` (a Gloomwood re-entry field) | `from_clockwork` | `true` |

All four IDs already fall inside their region's reserved block (`docs/ID_REGISTRY.md`) — this
decision adds a portal between existing maps, it mints no new `map_NNN`.

Both new spawns follow this doc's own §2 naming law (`from_<origin_region_slug>`) and land on maps
that currently carry no `from_*` spawn (their existing cross-region edges use different map IDs
per `docs/WORLD_PLAN.md`'s edge table), so neither collides with an existing spawn. **No reverse
portal is authored** on either destination map back up to the arena — one-way is the point of a
terminus shortcut. `docs/WORLD_PLAN.md`'s edge table plus these two additions together form the
complete authorized cross-region walk-edge set (see Open Questions re: `docs/VALIDATION.md` §5's
wording). Phase D authors these two portals directly from this table.

## 8. `longship` — paid scheduled island transport (v3)

The arc-2 inter-island network, and the taxonomy's only **scheduled** mode. Unlike the ferry (paid,
instant) and coaches (paid, instant), a longship is a real-time deck ride on a fixed cadence
(MapleStory-ferry-style). Routes at launch connect the Harthmoor pier at **Tidewatch Port**
(`map_071`) to each new-island port, plus inter-island routes; the concrete `route_id` set and its
endpoint maps live in `docs/WORLD_PLAN.md`'s arc-2 edge table (cited, never restated). Fares are
`10_systems/ECONOMY.md` §7.2.

### 8.1 Ride flow
1. **Pay & board.** A **pier officer** NPC on the origin pier takes the route fare (`10_systems/ECONOMY.md`
   §7.2 — charged *at this step*, not before); the co-located `portal(kind: longship)` then admits
   the player to the route's **deck map**, landing on spawn `longship_deck`.
2. **Deck.** The deck is a combat-free `interior` map (`docs/00_vision/GLOSSARY.md` map type).
   Players may walk, chat, and emote and share the deck for the sailing; **no combat at launch**
   (mid-sail ambush/boarding event deferred — Open Questions).
3. **Depart & sail.** The ship departs on its fixed cadence and sails for `sail_duration_s` of
   real time.
4. **Arrive.** At sail end the arrival portal opens and delivers each passenger to the destination
   pier's `longship_dock` spawn.

### 8.2 `longship` portal fields (design granularity)
Extends the `portal` object — `15_maps_system/MAP_INTERACTABLES.md` §2 owns the concrete param
shape (its kind enum + field table must add these, flagged in Open Questions); this doc owns the
rules and names the fields the kind needs:

| Field | Meaning |
|---|---|
| `kind: longship` | Selects the scheduled-ride behavior of this section |
| `route_id` | The route this portal serves; identity + endpoint maps owned by `docs/WORLD_PLAN.md` arc-2 edge table |
| `fare_ref` | Hook to the route's `10_systems/ECONOMY.md` §7.2 fare row (charged at boarding, §8.1) |
| `cadence_s` | Real-time interval between departures (default §8.3) |
| `sail_duration_s` | Real-time deck-ride length (default §8.3) |
| `target_map` / `target_spawn` | Boarding portal → deck map / `longship_deck`; deck arrival portal → destination pier / `longship_dock` |

### 8.3 Cadence, sail time & edge cases (defaults — tuning flagged)
- **Cadence:** one departure every `cadence_s` = **120 s**, the boarding portal open for the final
  **30 s** before each departure and closed during the sail. The pier officer / boarding portal
  surfaces a "next departure in N s" status (`10_systems/HUD.md` hook).
- **Sail time:** `sail_duration_s` = **150 s** (2.5 min) default; a per-route override up to
  ~**180 s** is allowed for longer inter-island crossings (producer range 120–180 s).
- **Miss departure:** **no fare is lost** — the fare is charged only at boarding (§8.1). The player
  simply waits on the pier for the next boarding window (≤ `cadence_s`).
- **Log out / disconnect mid-sail:** the crossing is **committed at boarding** (fare already
  spent), so the default is player-favorable — on next login the character arrives at the
  destination pier's `longship_dock`, exactly as if the sail had completed. No `shards` are ever
  spent for a crossing that lands nowhere. (Tuning flag: a "return to origin + refund" model is the
  alternative; destination-arrival is chosen as the low-feel-bad default — Open Questions.)
- **Spawns:** `longship_deck` (deck boarding) and `longship_dock` (destination-pier arrival) are
  reserved per §2.

### 8.4 Server authority, no combat
The sail is server-authoritative (`10_systems/PERSISTENCE.md`, matching the solo-with-server-boundary
build): departure timing, in-transit state, and arrival placement resolve server-side. The deck
carries no monster spawns and no `10_systems/SPAWN.md` zones at launch — it is a social interlude,
not a combat map.

## 9. Level-gated portals (`level_gate`) — v3

A portal may carry an optional integer property **`level_gate: N`** — the minimum character `level`
required to pass. It extends the `portal` field model (`15_maps_system/MAP_INTERACTABLES.md` §2)
uniformly across kinds (`edge` / `door` / `longship` / …); **absent = no gate**, which is the
default and the state of every arc-1 portal (§6).

**UX rule:** a `level_gate` portal is **visible and approachable** — never hidden. On an attempt to
pass with `level` < N, the transition is refused (no teleport occurs) and a message hook fires
(`10_systems/HUD.md`, e.g. *"The Deepway is sealed to you — return at Lv N."*). At `level` ≥ N it
behaves exactly as its underlying kind. This is a **soft, signposted** gate (P2 — the player sees
the door and the requirement, no invisible trap wall), and is the single deliberate exception to
§6's no-region-gate policy.

### 9.1 Debut: the Deepway (Lv 40+)
The property's first use is the **Deepway** in Cindershelf (`map_125`): a `door` into an underground
passage (`map_201`–`map_203`) surfacing at the Frostpeak port (`map_204`) — the walking route into
arc-2. The Deepway door carries `level_gate: 40`. The passage's concrete map IDs, its internal
edges, and the Frostpeak-side allocation are owned by `docs/WORLD_PLAN.md`'s arc-2 revision and
`docs/ID_REGISTRY.md`'s arc-2 block (cited, not minted here). Being a two-way walking `door` into
new content, it needs no `dead_end` marking (a reverse door returns from `map_201` to `map_125`).

### 9.2 Gates are per-portal-side — backtracking is never gated (v3.1)
A `level_gate` sits on **one portal**, i.e. one direction of a crossing; the reverse portal
carries no gate unless separately authored. Standing rule (owner directive, WORLD_PLAN
"Backtracking law"): progression gates guard **entry into higher content only** — returning
to earlier islands/regions is always ungated, at any level. Future cross-arc shortcuts
(WORLD_PLAN's reserved boss-connectivity hook: high-level boss access placed inside
low-level islands) reuse exactly this primitive — an additive gated portal on an existing
map, no new mechanism.

## Map-level edge table

Authored by the Phase D world-graph reconciler after all 200 maps exist.

## Open Questions

- `docs/VALIDATION.md` §5 states cross-region edges "must match `docs/WORLD_PLAN.md`'s edge table
  exactly." `docs/WORLD_PLAN.md` itself delegates the §7 terminus decision to this doc, so that
  phrase should be read (or amended at a future pass) to include this doc's §7 additions as part of
  the authorized edge set. Flagged for `docs/VALIDATION.md`'s owner to confirm/reword — not
  resolved by editing that file here (out of scope for this doc).
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
- **v2.2 coach reconciliation (resolved):** §§1–4 previously described the retired free-forever
  town-warp mechanism (`docs/00_vision/GLOSSARY.md`'s retired token); this pass reconciled them to
  the **paid** Harthmoor Coachworks — renamed the
  kind through §§1–3, made it paid-per-ride (fares `10_systems/ECONOMY.md` §7.1) with no unlock set,
  and re-derived §4 death-return routing off ordinary travel rather than free warp-home. The debt is
  closed; recorded here only as a change marker.
- **`from_longship` vs `longship_dock` (cross-doc) — resolved at the v3 gate:**
  `docs/WORLD_PLAN.md`'s arc-2 spawn convention now targets `longship_dock` (with
  `longship_deck` for boarding), matching this doc's §2/§8.
- **Coach/longship token promotion:** the interactable and NPC tokens this reconciliation relies on —
  `coach_station` (interactable), `coach_clerk` / `pier_officer` (NPC roles), and the `coach` /
  `longship` NPC services — are proposed for `docs/00_vision/GLOSSARY.md` promotion at the C gate
  alongside the already-flagged `longship_deck` / `longship_dock` spawns (§2). `coach` and
  `coach_stop` are already GLOSSARY Transport tokens.
- **§7 terminus vs arc-2 geography (pre-existing):** §7's Frostpeak/Clockwork drop chutes read from
  an arc-1 layout in which Frostpeak was a walk-chain terminus; the v3 arc-2 revision makes Frostpeak
  an *island* reached by the Deepway (§9.1) / longship (§8), and the §7 `target_map` region labels
  (e.g. `map_073` tagged "Ashfall") may not match `docs/WORLD_PLAN.md`'s current region blocks. This
  reconciliation only neutralized the retired free-warp "entrance-field" wording; the deeper §7 geography
  refresh is a separate debt flagged for the world-graph reconciler, not resolved here.
- **Longship mid-sail logout model (§8.3):** default is destination-arrival on relog (fare honored,
  no feel-bad). Alternative is return-to-origin + refund. Confirm at the arc-2 D gate once the
  server transit-state model (`10_systems/PERSISTENCE.md`) is concrete.
- **Longship cadence/sail tuning (§8.3):** `cadence_s` 120 s / `sail_duration_s` 150 s (per-route
  up to 180 s) are first-pass; retune against real inter-island distances and playtest wait-time
  tolerance once `docs/WORLD_PLAN.md`'s arc-2 route set lands.
- **Mid-sail ambush / boarding event (§8.1):** deferred at launch (deck is combat-free) — mirrors
  `docs/WORLD_PLAN.md`'s existing ferry on-deck-ambush Open Question. Revisit when arc-2 combat
  content is authored; would need `10_systems/SPAWN.md` deck zones + a defeat/return rule.
- **`level_gate` param registration (§9) — resolved:** `15_maps_system/MAP_INTERACTABLES.md` §2's
  portal `kind` enum and param table now carry `coach`/`longship`, the optional `level_gate` field,
  and the longship `route_id`/`fare_ref`/`cadence_s`/`sail_duration_s` params, and
  `20_schemas/map.schema.md` mirrors the enum + fields (`docs/VALIDATION.md` §3). This doc still owns
  only the rules; the param shape is registered as of this pass.
- **`level_gate` reuse (§9):** whether other arc-2 thresholds (Arcane Reach / Voidshore ports)
  also carry a `level_gate`, and at what levels, is `docs/WORLD_PLAN.md`'s arc-2 call — only the
  Deepway (Lv 40) is fixed here.
- **Reserved arc-2 map/slug promotion:** the Deepway debut references `map_201`–`map_204` and the
  `frostpeak` region slug, both currently *reserved/invalid this run* (`docs/00_vision/GLOSSARY.md`,
  `docs/ID_REGISTRY.md`). Their promotion to valid arc-2 content is owned by those registries'
  arc-2 revision — this doc cites them as forward references only, minting nothing.
