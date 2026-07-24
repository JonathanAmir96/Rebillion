# WORLD_CHANNELS.md — Channel Model, Instances & Capacity Targets

References: 00_vision/GLOSSARY.md, docs/VALIDATION.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/NETWORK_PROTOCOL.md,
70_integrations/GAMEPLAY_SIMULATION.md, 70_integrations/CHAT_SOCIAL_BACKEND.md,
70_integrations/DATABASE_PERSISTENCE.md, 10_systems/SPAWN.md, 10_systems/PERSISTENCE.md,
10_systems/DROPS.md, 15_maps_system/MAPS_SYSTEM.md, 15_maps_system/MAP_CONNECTIONS.md,
10_systems/social/PARTY.md, 10_systems/social/RAID.md, 10_systems/social/CHAT.md,
10_systems/social/MARKET.md, docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

Owner doc for the **channel-model detail and capacity targets** that
`70_integrations/BACKEND_ARCHITECTURE.md` §1 delegates here (its §9 sibling table). That doc fixes
the topology **shape** — single logical world + population channels over shared social maps + true
instances for raid content — and never restates it; this doc fixes *how many* channels, on
*which* maps, selected *how*, torn down *when*, and how party/chat/market state keeps working
across them. It never restates a value owned elsewhere: respawn timers stay `10_systems/SPAWN.md`'s,
exp-share math stays `10_systems/social/PARTY.md`'s, fares stay `10_systems/ECONOMY.md`'s. It
consumes `docs/WORLD_PLAN.md`'s map allocation (v3: 324 maps across two authored arcs) and
`docs/ID_REGISTRY.md`'s ID blocks as given facts, not decisions of its own.

## 1. Channel-eligible maps

A **channel** is an additional supervised map process for the same `map_NNN`
(`70_integrations/BACKEND_ARCHITECTURE.md` §1 "Population channels are additional map processes
inside (or across) world nodes") — a second, independent copy of that map's spawner, live-mob set,
and player occupancy, sharing nothing with its sibling copies except the one truth ledger (character
DB, wallet, social/market DB) that lives entirely off the map-process tier.

**Eligible: every shared world-graph map — `town`, `field`, `dungeon`, `interior`, `secret`
(`00_vision/GLOSSARY.md` map types) — except the two exemptions below.** The mechanism is uniform
and demand-driven (§7's occupancy cap decides when channel 2 spins up, not a per-map whitelist
authored in `docs/ID_REGISTRY.md`) — a channel-eligibility flag is not a new authored map field, so
nothing here contradicts `15_maps_system/MAPS_SYSTEM.md` §1's anatomy table. In practice this reads
exactly as "towns/popular fields vs quiet field maps," but as an emergent property of the world
graph rather than a hand-authored list: `docs/WORLD_PLAN.md`'s "Map order & monster gradient law"
already funnels population through each region's entrance (its town and the field map(s) directly
off it — e.g. `map_005` off Emberfoot Village, `map_027`/`map_028` off Millbrook, `map_046` off
Mossmere, `map_076` off Tidewatch Port, `map_098` off Verdant's deep hollow, `map_128` off
Cindershelf, `map_152` off Tidewatch's sea cave, `map_177`/`map_188` at Clockwork's two gates) and
thins it monotonically along each path. Those chokepoint maps are the ones expected to cross the
§7 occupancy cap and run multiple channels under normal load; a quiet deep-path field, a dungeon
corridor, or a secret pocket is channel-*eligible* by the same mechanism but in practice almost
never spins up a second channel, because too few players are ever there at once to cross the cap.

**Exemption 1 — `arena` maps never channel.** `15_maps_system/MAPS_SYSTEM.md` §8 already decides a
regional arena is a single **shared** map instance that resets to phase 1 once empty for
`arena_reset_grace_s` (30 s) — not per-party, not per-channel. Running the same boss fight as N
independent channel copies would fork that shared-reset design for no benefit this genre needs;
this doc adds no occupancy cap to arenas and spawns no second channel for one, full stop. `boss`-tier
respawn is `10_systems/SPAWN.md` §3's, restated nowhere here.

**Exemption 2 — raid stage/finale maps are true instances, not channels.** Covered in §2.

**Channel identity is ops/routing metadata, not a game-content ID.** A channel is addressed as
`map_NNN` + a small integer index (e.g. "map_017, channel 2") for gateway routing, telemetry, and
this doc's capacity math. It mints no `docs/ID_REGISTRY.md` block and is never player-facing content
— the on-screen channel picker's presentation is `10_systems/HUD.md`'s call, not this doc's.

## 2. Raid instances (not channels)

The four raids occupy their own scaling unit — **instance workers**
(`70_integrations/BACKEND_ARCHITECTURE.md` §1), ephemeral map processes allocated one per party on
raid-gate entry and torn down on exit (`10_systems/SPAWN.md` §7), never shared and never
occupancy-capped the way §7's channels are:

| Token | Stage maps | Finale arena | Finale boss |
|---|---|---|---|
| `raid_undervault` | `map_038`–`map_040` | `map_042` | `mob_027` (The Cellar King) |
| `raid_mainspring` | `map_195`–`map_197` | `map_200` | `mob_150` (The Custodian) |
| `raid_deepfrost` | `map_240`–`map_242` | `map_244` | `mob_178` |
| `raid_voidtide` | `map_320`–`map_322` | `map_324` | `mob_234` |

(`docs/ID_REGISTRY.md` "Maps," `10_systems/social/RAID.md` §2 — cited, not restated.) Party
size is owned split: the 3-member floor by `10_systems/social/RAID.md` §2/§3, the 6-cap by
`10_systems/social/PARTY.md` §1; instance lifecycle (leaving, the 60 s
disconnect grace, full-wipe reset, dissolution) is `10_systems/social/RAID.md` §5's. This doc
adds one fact neither states: **an active raid instance never counts against its stage/finale map's
channel occupancy**, because it isn't a channel of that map at all — `map_042` and `map_200` also
serve as ordinary open-entry arenas (§1's Exemption 1) when not hosting a raid finale, and the two are
different processes even when both are "the same `map_NNN`" from a content-authoring point of view.
### 2.1 The channel claim (one party per raid, per channel)

Instancing bounds *how* a raid runs; it does not bound *how many* run at once. This section adds
that bound. Entering a raid takes a **claim** on `(channel, raid_token)`, and while that pair is
claimed no other party on that channel may enter that raid.
`10_systems/social/RAID.md` §3 owns the player-facing law; the server-side shape is this doc's:

- **The key is `(channel, raid_token)`** — not `(channel, map_NNN)`. A claim on `raid_undervault`
  leaves `raid_mainspring` free on the same channel, and one claim covers that raid's whole stage
  chain, finale arena, and bonus room (`map_325`–`map_328`) as a single unit.
- **Held by the world node, not the instance worker.** The claim is taken at instance-creation
  request time — *before* a worker is allocated — and released when that worker is torn down. It is
  node-local state, not a distributed lock: a channel lives on exactly one world node (§7), so a
  claim never crosses nodes and needs no consensus.
- **Released on** clear, any `10_systems/social/RAID.md` §5 wipe cause (including the §4.1 run
  clock expiring), the instance emptying, and the 60 s disconnect grace elapsing for a dropped
  party. Release is driven by **worker teardown**, so a claim can neither outlive the run it guards
  nor be dropped while a live worker still holds the instance.
- **No queue, no reservation.** A blocked party is refused at the herald and told to change
  channels; this doc holds no waitlist state.

This does **not** weaken Exemption 2. Raid maps remain true instances, never channels of
themselves, and an active raid instance still counts against no map's channel occupancy. The claim
rations *entry* only; nothing past the door changes.

**Interaction with the headroom target below.** The claim puts a hard ceiling on concurrent
instances of any one raid at that node's channel count. Where the 40-per-token figure below is a
soft planning number, the claim is a real constraint, and it is the binding one unless a node runs
40+ channels — which makes the figure conservative rather than wrong. Flagged in Open Questions.

A raid instance is bounded for free by the party cap (≤6, `10_systems/social/PARTY.md` §1) — no
occupancy math is needed for it, only headroom planning: this doc sets a soft per-world-node target
of **40 concurrently active raid instances of each token** (160 total across the four tokens)
before a world node needs a
scaling look — sized at roughly 5% of the §7 per-node population target
(2,000 × 0.05 ÷ 3-member floor ≈ 33, rounded up for headroom) engaging raid content at once, which is
a generous estimate for hundreds-to-low-thousands concurrent play. This number is explicitly
first-pass (Open Questions).

## 3. Channel selection on arrival

When a character transitions onto a channel-eligible map (portal, coach, ferry, respawn, or the §4
manual switch), world routing (`70_integrations/BACKEND_ARCHITECTURE.md` §1) assigns a channel by:

1. **Fill-lowest-first.** Assign the lowest-numbered existing channel with headroom under its §7
   occupancy cap. This deliberately clusters players rather than spreading them evenly — an MMO
   channel model that spreads population thin defeats the point of a shared world (P3, one connected
   world reads as one place).
2. **Party-aware grouping.** If the arriving character is in a party (`10_systems/social/PARTY.md`)
   and other same-party members are already resident on one of this map's channels with headroom,
   route the arrival to that channel instead of the lowest-numbered one — best-effort, not a
   guarantee (a full channel still forces a split). This is a routing preference only; it changes no
   membership or reward rule (`10_systems/social/PARTY.md` §1/§4 unaffected) and requires no new
   client-facing feature (there is still no teleport-to-partymate — `15_maps_system/MAP_CONNECTIONS.md`
   v2.2's "no free warps" law holds; a party still has to travel to the same map together to land on
   the same channel).
3. **Spin-up on exhaustion.** If every existing channel (up to the §7 max) is at cap, spin up the
   next channel index fresh (an empty map process is near-free, `70_integrations/BACKEND_ARCHITECTURE.md`
   §1's scaling-unit table).
4. **Hard ceiling.** If the map is already at its max channel count (§7) and every channel is full,
   the arriving transition is **held**, not dropped or overflowed above cap — the source map/portal
   queues the character and retries as headroom frees (fail-safe, matching
   `30_engineering/ENGINEERING_STANDARDS.md` directive 7 as applied by
   `70_integrations/BACKEND_ARCHITECTURE.md` §8). This is an exceptional-load event (see §7's note on
   the 5-channel ceiling), not expected in ordinary play at this game's target scale.

**Channel_01 is always resident.** Every channel-eligible map's first channel is a permanent,
never-torn-down process — it is the map's canonical presence in the world graph and must always be
routable even at population zero (an empty map process costs nothing to keep live,
`70_integrations/BACKEND_ARCHITECTURE.md` §1). Only channels 2+ are elastic (§7).

## 4. Manual channel switching — server semantics

The channel-picker UI is `10_systems/HUD.md`'s to design; this doc fixes only what the server does
when a switch command arrives, since a manual switch is — mechanically — a same-`map_NNN` transition
to a different channel index and inherits §6's handoff rules with three additions:

- **What moves.** Every `authority: server` field (`10_systems/PERSISTENCE.md` §2 — inventory,
  stats, `shards` wallet, quest flags, skill cooldowns, loot-tag ownership timers) is
  character-scoped, not map-process-scoped, so it is untouched by which channel a character sits on.
  `authority: shared` position/velocity (`10_systems/PERSISTENCE.md` §4) does **not** carry over —
  the destination channel is a different simulation with no record of where the character stood in
  the old one, so the character resumes at that map's `main` spawn (`15_maps_system/MAP_CONNECTIONS.md`
  §2), exactly as if arriving fresh. Any live engagement with a specific mob instance is severed —
  that mob object belongs to the old channel's zone spawner (`10_systems/SPAWN.md` §1) and has no
  counterpart on the new one; this is not a bug, it is what "a different simulated copy" means.
- **Cooldown: 30 s between manual switches.** Prevents connection/state churn on the gateway and
  world-routing tier from switch-spam; long enough to be a deliberate choice, short enough not to
  read as a punishment for using an intended feature.
- **Combat lock.** A character cannot manually switch channels while flagged as recently in combat
  (having dealt or taken damage in the last 5 s, mirroring the invulnerability-window convention
  already used for elite/boss `spawn` states, `10_systems/SPAWN.md` §6) — closes the obvious
  "switch channel to drop aggro/an unfavorable fight" abuse vector even though this design's combat
  is hit-event-triggered rather than sustained-aggro (`70_integrations/BACKEND_ARCHITECTURE.md` §4).
- **Kill/loot farming across channels is accepted, not an exploit.** Each channel's zone spawner and
  mob population is an independent process (`10_systems/SPAWN.md` §1), so hopping to a fresher
  channel to find an uncleared mob pool is the ordinary, intended effect of population channels in
  this genre — no additional throttle is applied beyond the 30 s cooldown above. A character cannot
  double-claim a single kill's drop across channels regardless: drop-roll and loot-tag ownership
  timers are `authority: server`, character-scoped, and evaluated once at the kill
  (`10_systems/DROPS.md` §7/§9, `10_systems/PERSISTENCE.md` §2) — that guarantee is unaffected by
  which channel the kill happened on and is not re-derived here.

## 5. Cross-channel state (party, chat, market)

`70_integrations/BACKEND_ARCHITECTURE.md` §7 lands `PARTY`/`GUILD`/`CHAT`/`MARKET`/`MAIL`/`TRADING`
on the **social services** tier — a tier that sits entirely off the map-process tier this doc
governs. That is precisely why they transcend channels for free, architecturally, rather than by
special-casing: a channel is a concept the map-process tier has and the social-services tier simply
does not. Roster membership, guild rosters, market listings, mail, and trade escrow never need to
know which channel of which map a character currently occupies.

**One seam needs channel awareness, and this doc is where it is fixed:** `10_systems/social/PARTY.md`
§4's exp/loot eligibility gate ("same `map_NNN`") and `10_systems/social/CHAT.md`'s `normal`-channel
scoping (`map_id` in its data sketch) both predate the channel model and, read literally, would let
two party members (or two chatting strangers) on *different channel copies* of the same nominal
`map_NNN` share a kill's exp or see each other's speech bubbles despite being unable to see, fight,
or reach one another. This doc resolves both, as its channel-model territory
(`70_integrations/BACKEND_ARCHITECTURE.md` §9 assigns this doc "channel-model detail"), without
editing either owning file:

- **Party exp/loot eligibility (`10_systems/social/PARTY.md` §4/§5) is scoped to `map_NNN` +
  channel index**, not `map_NNN` alone. A member on a different channel of the nominal same map is
  exp/loot-**ineligible** for that channel's kills, identically to being on a different map entirely
  — no rule in `10_systems/social/PARTY.md` changes, this only refines what "same map" means once
  channels exist. The party service (social-services tier, channel-agnostic by default) carries one
  extra piece of routing-sourced metadata per member — their live channel index — purely to evaluate
  this gate; the metadata's source is world routing (§3/§6), not a new social-tier data model.
- **Chat's `normal` channel (`10_systems/social/CHAT.md`) is scoped to `map_NNN` + channel index**,
  not `map_NNN` alone, for the same reason: a speech bubble above a character that does not exist in
  your channel cannot render. `party`/`guild`/`whisper` need no such refinement — they are already
  roster-scoped, not presence-scoped, and roster membership is channel-agnostic by design (§this
  section, first paragraph).

Internal relay/roster/escrow mechanics for all six systems remain
`70_integrations/CHAT_SOCIAL_BACKEND.md`'s to design; this doc fixes only the channel-scoping fact
above, which that sibling's relay topology must honor for `normal` chat and the party service must
honor for exp/loot arbitration.

## 6. Handoff on map transition

Every transition — portal (`edge`/`door`/`coach`, `15_maps_system/MAP_CONNECTIONS.md` §1), the §3
arrival flow, or the §4 manual switch — is a process-to-process handoff between two independently
supervised map processes (`70_integrations/BACKEND_ARCHITECTURE.md` §1). The wire-level packet
shape for it is `70_integrations/NETWORK_PROTOCOL.md`'s; this doc fixes only the sequencing and what
blocks.

**Blocks the transition (must complete before the player acts on the destination map):**
- Portal-target validation — destination map + spawn point exist (`docs/VALIDATION.md` §5's
  world-graph soundness contract) — a cheap synchronous lookup, not a network round-trip to content.
- §3's channel-selection decision (fill-lowest-first / party-aware / spin-up-or-hold).
- The destination channel process existing and live — if it must cold-spin (§3 point 3), the player
  waits on that spin-up; this is the one place channel selection can add visible latency, bounded by
  ordinary BEAM process-start cost (not specified here — a coding-pass measurement, not a design
  number).
- The gateway re-pointing the character's live connection from the source map process's event stream
  to the destination's (`70_integrations/BACKEND_ARCHITECTURE.md` §1 "World routing") — until this
  completes the character is not receiving either map's simulation and must not be considered "in
  the world" by either process.

**Does not block (proceeds after the player is already acting on the destination map):**
- The `10_systems/PERSISTENCE.md` §6 "map/zone transition" autosave trigger — durability-guaranteed
  before the *source* process fully releases the character's presence record (a two-phase handoff:
  destination acks readiness, then source releases and the autosave commits), but the player is not
  blocked waiting on the disk/Postgres acknowledgment to see the new map.
- Presence/roster propagation to party and guild (social-services tier, §5) — the character's
  `current map_NNN`/channel updates there asynchronously; a party HUD plate briefly showing a stale
  location is a rendering lag, not a correctness bug (`10_systems/social/PARTY.md` §3's plate data is
  not itself gated on this).
- The source channel's occupancy-count decrement that feeds §7's spin-up/teardown math.
- Telemetry/analytics event emission (`70_integrations/TELEMETRY_ANALYTICS.md`'s territory).

**Failure mode.** If destination-process spin-up fails (§3), the transition aborts and the character
remains on the source map — never left "in transit" with no live process on either side
(`70_integrations/BACKEND_ARCHITECTURE.md` §8's fail-safe stance, applied here). If the gateway's
world-routing hop itself is unreachable, the transition is refused client-side with a retry, the same
stance §8 takes for the edge/gateway component generally.

## 7. Capacity targets

These are engineering calls made here from best practice for a 2D side-scroller MMO at
hundreds-to-low-thousands concurrent (`70_integrations/BACKEND_ARCHITECTURE.md` §2), not deferred.

| Target | Value | One-line rationale |
|---|---|---|
| Occupancy cap — `town` maps (2–4 screens wide, `15_maps_system/MAPS_SYSTEM.md` §2) | **150** concurrent players/channel | A multi-screen social hub spreads its crowd across vendors/instructors/coach station rather than one combat viewport, so it tolerates far more simultaneous bodies before it reads as cluttered (P1 readability) |
| Occupancy cap — `field` / `dungeon` / `secret` maps (`field` up to 3–6 screens wide, `15_maps_system/MAPS_SYSTEM.md` §2) | **60** concurrent players/channel | These are the maps where `10_systems/SPAWN.md` §2/§4's mob-density budget lives; past ~60 simultaneous players the shared spawn-zone pool (`target_count`/`max_concurrent`) is contested badly enough to break the "player chooses engagements" pillar (P1), even on the widest `field` maps — contention is per spawn zone, not per screen |
| Occupancy cap — `interior` maps (combat-free, 0/0 density budget, `10_systems/SPAWN.md` §2 / `15_maps_system/MAPS_SYSTEM.md` §6) | **60** concurrent players/channel | No spawn zones to contest — the cap here is room-crowding readability only (a tight vendor/instructor room reads as cluttered far sooner than a town's multi-screen spread); kept equal to the field cap for one fewer ops knob |
| Max channels per map | **5** (`channel_01`–`channel_05`) | Bounds monitoring/ops surface and prevents a viral event from fragmenting the social graph into copies too thin to feel like a shared world (P3); a map genuinely needing a 6th channel is a launch/patch-day spike ops should handle by cordoning a queue, not by unbounded spin-up |
| Channel_01 floor | Always resident, never torn down (§3) | It is the map's canonical presence in the world graph — every map must stay routable at population zero the same way any other empty, near-free map process does (`70_integrations/BACKEND_ARCHITECTURE.md` §1) |
| Extra-channel teardown grace | **5 min** empty before a channel (2+) is torn down | Long enough that ordinary population drift (a quiet minute on a busy map) doesn't thrash spin-up/teardown cycles; short enough that a launch-week spike's extra channels reclaim their world-node budget promptly once the crowd moves on |
| Target concurrent players per world node | **2,000** | A conservative per-node figure for BEAM's proven social-traffic sweet spot (`70_integrations/BACKEND_ARCHITECTURE.md` §2) given this game's light, hit-event-triggered combat and shared position/velocity sync rather than a heavy fixed-rate numeric sim — leaves headroom under typical soft-realtime BEAM node practice for this workload shape |
| World-wide concurrent target | **~10,000**, across ≈5 world nodes | Sits at the top of "hundreds-to-low-thousands concurrent" (`70_integrations/BACKEND_ARCHITECTURE.md` §2) while keeping the per-node figure above conservative; world nodes scale horizontally with no practical ceiling (`70_integrations/BACKEND_ARCHITECTURE.md` §1's scaling-unit table), so this is a launch-sizing target, not an architectural cap |
| raid instance-worker headroom target (per world node) | **40** concurrently active instances per raid token (160 total across four tokens) | Sized at ~5% of the 2,000-player node target engaging raid content at once, divided by the 3-member floor (`10_systems/social/RAID.md` §2/§3) and rounded up for headroom — generous for hundreds-to-low-thousands concurrent play (§2) |

## 8. Failure modes

| Dependency | Failure mode | Degradation / stance |
|---|---|---|
| Channel router (part of world routing, `70_integrations/BACKEND_ARCHITECTURE.md` §1) | Unreachable → cannot decide/assign a channel | New arrivals to that map hold at the source map/portal (§3 point 4's hold-not-drop stance); already-resident players on live channels are unaffected |
| Destination channel process | Crash mid-spin-up or mid-handoff | Transition aborts, character stays on the source map (§6); the channel process restarts under its world node's ordinary OTP supervision (`70_integrations/BACKEND_ARCHITECTURE.md` §1) and rejoins the channel pool once live |
| Party/chat channel-index metadata feed (§5) | World-routing → social-services propagation lags or drops | Exp/loot eligibility and `normal`-chat delivery fail closed (a member briefly reads as ineligible/unreachable) rather than fail open (never award exp or deliver a bubble across a channel boundary on stale data) — consistent with `70_integrations/BACKEND_ARCHITECTURE.md` §8's "never fabricate a `server` truth" stance |
| raid instance-worker pool nearing the §7 headroom target | Sustained demand above 40 concurrent instances of one token on a node | Self-scaling by design (`70_integrations/BACKEND_ARCHITECTURE.md` §1 — one instance worker per party, torn down on exit); the target is a capacity-planning trigger for adding world-node headroom, not a hard cap that blocks entry |

## 9. Interim solo build & implemented when

The channel model has no observable effect in the interim solo build: one player, one process, one
implicit "channel_01" that is never crossed and never spun a second copy of — this doc's mechanisms
are dormant by construction, the same stance `10_systems/social/PARTY.md`,
`10_systems/social/RAID.md`, `10_systems/social/CHAT.md`, and `10_systems/social/MARKET.md`
already take for their own server dependency.

**Implemented when:** a live authoritative server exists and world nodes run real map processes —
i.e. after the interim solo build ships and the owner greenlights it
(`70_integrations/BACKEND_ARCHITECTURE.md` §6/§10). Until then this doc is a forward contract that
blocks nothing in the solo build.

## Open Questions

Only game-design/balance calls and owner-priced or first-pass-tunable items live here; §7's
capacity numbers and §1's channel-eligibility mechanism are decided in this doc.

- **§7's numeric targets (occupancy caps, max channels, teardown grace, cooldown/combat-lock
  windows in §4, raid headroom target) are first-pass**, sized from best-practice reasoning rather than
  live telemetry (and originally sized against the pre-Arc-2 two-island world — still valid as
  launch targets since world nodes scale horizontally, per
  `docs/phase_reports/PHASE_I_BACKEND_REPORT.md` §6) — retune once real concurrency data exists, matching the precedent
  `10_systems/SPAWN.md` §2/§4 sets for its own first-pass density defaults.
- **Whether channel-hop kill/quest-target farming (§4) should ever be throttled beyond the 30 s
  switch cooldown** is a balance call, not an engineering one — this doc's default is "accepted,
  genre-standard," but the owner/economy pass may want a stricter stance once real farming behavior
  is observed.
- `10_systems/social/PARTY.md` §4 and `10_systems/social/CHAT.md`'s data sketch predate the channel
  model; §5's channel-index refinements are additive and contradict neither, but those files are
  owned elsewhere — flagged for their owners to cite this doc at the next revision, not authored
  there by this doc.
- Whether a manual channel switch should ever preserve an in-progress `collect`/`reach`-type quest
  step interaction on the source channel (e.g., mid-interactable) versus simply severing it like any
  other live engagement (§4) is unresolved; default severs it, consistent with a mob-engagement
  severance.
- Cross-region hosting, world-node count/region placement, and any autoscaling-vendor tooling to hit
  §7's targets are owner-priced, per `70_integrations/BACKEND_ARCHITECTURE.md`'s own Open Questions
  — not reopened here.
