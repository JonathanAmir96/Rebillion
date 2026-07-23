# MAP_CONNECTIONS.md — Portal Rules, Spawn Naming & the World Graph

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md, docs/VALIDATION.md,
docs/ID_REGISTRY.md, 10_systems/DEATH_PENALTY.md, 10_systems/COMBAT_FORMULA.md,
10_systems/LEVELING.md, 10_systems/PERSISTENCE.md, 10_systems/ECONOMY.md,
10_systems/HUD.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_INTERACTABLES.md

Owner doc for the **rules** portals, spawns, and waygates follow between maps.
`docs/WORLD_PLAN.md`'s "Cross-region walk edges" and "Waygate network" tables are the sole
authoritative source for *which* `map_NNN` pairs connect — they are cited, never reproduced, here.
This doc formalizes the spawn-naming convention `docs/WORLD_PLAN.md` previews, the waygate unlock
rule, death-return routing, `dead_end` marking, the region-progression gate policy, and resolves
`docs/WORLD_PLAN.md`'s terminus open question. Portal object params are
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

> **v2.2 doc-debt (not resolved in this v3 pass):** §§1–4 below still describe the town network
> under its retired pre-v2.2 name, the free-forever "waygate" mechanism. `docs/WORLD_PLAN.md` v2.2
> and `docs/00_vision/GLOSSARY.md` replaced that with the **paid** Harthmoor Coachworks (`coach`),
> so §3's free-travel model and §4's waygate-endpoint death routing no longer match the shipped
> town network. Reconciling §§1–4 (waygate→coach rename, re-derive death routing off coach stations,
> paid-per-ride not free) is a standing debt flagged in Open Questions — out of scope for this
> arc-2 transport task, which only *adds* longship, `level_gate`, fares, and this taxonomy.

## 1. Portal kind semantics between regions

| Kind | Typical use | Region span |
|---|---|---|
| `edge` | Most field/dungeon chain links; the 8 cross-region walk edges (`docs/WORLD_PLAN.md`) | Usually intra-region; cross-region for the 8 listed edges (+ §7's two additions) |
| `door` | Town↔interior; every arena's entry gate (`15_maps_system/MAPS_SYSTEM.md` §8) | Always same-region |
| `waygate` | The Millbrook-hub long-distance network (`docs/WORLD_PLAN.md` "Waygate network") | Cross-region by design — that is its purpose |
| `longship` (v3) | Paid **scheduled** arc-2 inter-island transport: pier→deck boarding portal and deck→destination-pier arrival portal (§8) | Cross-island (arc-2 island network) |

## 2. Spawn-point naming law

Formalizes the convention `docs/WORLD_PLAN.md`'s "Spawn-point convention" paragraph previews.
Three tokens are **reserved**; a map may also author additional freely-named spawns (e.g. a
multi-entrance dungeon's `upper_west`) as long as they never collide with the reserved set.

| Spawn name | Required on | Meaning |
|---|---|---|
| `main` | Every map, exactly one | Default arrival point — direct teleport, quest-start, and the fallback target for any portal that doesn't name another spawn |
| `from_<origin_slug>` | Every map that is the destination of an `edge` portal crossing a region boundary | `<origin_slug>` is the origin **region**'s GLOSSARY slug (not a per-map slug — maps have none). An intra-region `edge` targets plain `main` unless the destination map has multiple distinct entrances needing disambiguation |
| `waygate` | Every map with a `waygate_console` (`15_maps_system/MAP_INTERACTABLES.md` §9) | The fixed arrival point for all waygate-network transits; exactly one per waygate-bearing map |

Each of `docs/WORLD_PLAN.md`'s 8 bidirectional cross-region edges produces exactly two
`from_<origin_slug>` spawns (one per endpoint, each named for the *other* side's region) — e.g.
the Emberfoot↔Verdant edge gives Verdant's endpoint a `from_emberfoot` spawn and Emberfoot's
endpoint a `from_verdant` spawn.

**v3 (longship transport spawns):** §8 reserves two further transport-network spawns following
this same law — `longship_deck` (the boarding point on every longship deck map) and
`longship_dock` (the arrival point on every longship destination pier) — analogous to
`docs/WORLD_PLAN.md`'s existing `coach_stop` / `from_ferry` transport spawns. They are proposed as
`docs/00_vision/GLOSSARY.md` Transport tokens alongside `coach_stop`.

## 3. Waygate unlock rule

**Touch the console once, then free travel forever — no cost, no cooldown** (P3: travel is a
low-friction loop, hunt outward, warp home).

- Unlock state is a per-character, server-authoritative, persistent set of unlocked waygate
  `map_id`s (`10_systems/PERSISTENCE.md`).
- **Millbrook Central's waygate is pre-unlocked for every character from creation** — it is already
  in a new character's unlocked set before the console is ever touched (touching it anyway is
  harmless/idempotent).
- Interacting with any `waygate_console` (`15_maps_system/MAP_INTERACTABLES.md` §9): if this
  waygate is not yet in the character's unlocked set, it is added (permanent, no re-lock); either
  way, a destination menu (`10_systems/HUD.md`) then opens listing every currently-unlocked
  waygate, and choosing one triggers the co-located `portal(kind: waygate)`
  (`15_maps_system/MAP_INTERACTABLES.md` §2) to that destination's `waygate` spawn.
- No `shards` cost, no cooldown, on any waygate transit.

## 4. Death-return routing

`10_systems/DEATH_PENALTY.md` §4 owns the bind mechanic and respawn destination (a bound town's
`main` spawn) — not restated here. This doc owns only *getting back out*: every valid bind town
(`docs/WORLD_PLAN.md`'s 4 towns) is also a waygate-network endpoint, so a respawned character
always has immediate access to its own town's `waygate_console`, already unlocked (it must have
rested there to be bound there), and can warp back to the frontier as ordinary travel (§3) — never
a special death-only routing path.

## 5. `dead_end` marking

Per `docs/VALIDATION.md` §5: any portal with **no matching reverse portal** on its destination map
must carry `dead_end: true`, authored on the portal that *leads into* the one-way transition (not
on the destination side). This is a validator-exemption flag only — it tells the world-graph
checker "do not require a reverse portal here" — not a required visible UI marker, though a map UI
may optionally surface it (`10_systems/HUD.md`'s call, not specified here). Ordinary `edge`/`door`/
`waygate` portals, which always pair with a reverse, are never marked `dead_end`.

## 6. Region-progression gate policy: none

**Decision: no authored region-to-region progression gate exists anywhere in the portal/waygate
system** — no level lock, quest-flag lock, or item-key lock on any region boundary (contrast with
an optional *per-arena* quest-flag gate, `15_maps_system/MAPS_SYSTEM.md` §8, a narrower, different
concern). A Lv 1 character can walk into a Lv 90 region; nothing here stops them. The only gate is
the emergent difficulty curve: `10_systems/COMBAT_FORMULA.md` §9's level-difference dampener makes
a badly under-level fight genuinely hard well before it's mechanically blocked, reinforced by
`10_systems/LEVELING.md`'s exp curve (which consumes that same §9 table) cratering reward for
over-level kills, and `docs/WORLD_PLAN.md`'s world-graph spine naturally lands a region-by-region
player roughly in-band anyway. This is deliberate (P2 — no trap walls, only a hard-but-not-
impossible curve) and matches §3's waygate unlock, which also never checks level.

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
region's arena back down to the neighboring region's waygate-entrance field, so a player who has
just finished the terminus content isn't forced to walk the whole chain back or spend a return
scroll.

| Terminus | New portal on | Kind | `target_map` | `target_spawn` (new) | `dead_end` |
|---|---|---|---|---|---|
| Frostpeak (The Hornfall Summit) | `map_108` | `edge` | `map_073` (Ashfall's waygate-entrance field) | `from_frostpeak` | `true` |
| Clockwork (The Mainspring) | `map_144` | `edge` | `map_109` (Gloomwood's waygate-entrance field) | `from_clockwork` | `true` |

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

## Map-level edge table

Authored by the Phase D world-graph reconciler after all 200 maps exist.

## Open Questions

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
- **v2.2 doc-debt (blocking a future pass, not this one):** §§1–4 still describe the town network
  as the retired free-forever "waygate" mechanism, but `docs/WORLD_PLAN.md` v2.2 + `docs/00_vision/GLOSSARY.md`
  replaced it with the **paid** Harthmoor Coachworks (`coach`). A dedicated reconciliation pass
  must (a) rename waygate→coach through §§1–3, (b) make it paid-per-ride (fares `10_systems/ECONOMY.md`
  §7.1) rather than free-after-unlock, and (c) re-derive §4 death-return routing off coach stations
  instead of waygate endpoints. Flagged for the doc owner; deliberately untouched by this arc-2
  transport task to avoid a large out-of-scope rewrite.
- **Longship mid-sail logout model (§8.3):** default is destination-arrival on relog (fare honored,
  no feel-bad). Alternative is return-to-origin + refund. Confirm at the arc-2 D gate once the
  server transit-state model (`10_systems/PERSISTENCE.md`) is concrete.
- **Longship cadence/sail tuning (§8.3):** `cadence_s` 120 s / `sail_duration_s` 150 s (per-route
  up to 180 s) are first-pass; retune against real inter-island distances and playtest wait-time
  tolerance once `docs/WORLD_PLAN.md`'s arc-2 route set lands.
- **Mid-sail ambush / boarding event (§8.1):** deferred at launch (deck is combat-free) — mirrors
  `docs/WORLD_PLAN.md`'s existing ferry on-deck-ambush Open Question. Revisit when arc-2 combat
  content is authored; would need `10_systems/SPAWN.md` deck zones + a defeat/return rule.
- **`level_gate` param registration (§9):** `15_maps_system/MAP_INTERACTABLES.md` §2's portal
  param table and its `kind` enum must add `longship` and the optional `level_gate` field for
  schema conformance (`docs/VALIDATION.md` §3). Flagged for that doc's owner; this doc owns only the
  rules, not the param shape.
- **`level_gate` reuse (§9):** whether other arc-2 thresholds (Arcane Reach / Voidshore ports)
  also carry a `level_gate`, and at what levels, is `docs/WORLD_PLAN.md`'s arc-2 call — only the
  Deepway (Lv 40) is fixed here.
- **Reserved arc-2 map/slug promotion:** the Deepway debut references `map_201`–`map_204` and the
  `frostpeak` region slug, both currently *reserved/invalid this run* (`docs/00_vision/GLOSSARY.md`,
  `docs/ID_REGISTRY.md`). Their promotion to valid arc-2 content is owned by those registries'
  arc-2 revision — this doc cites them as forward references only, minting nothing.
