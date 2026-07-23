# GAMEPLAY_SIMULATION.md — Server-Side Game-Logic Layer & Tick Model

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/PERSISTENCE.md, 10_systems/COMBAT_FORMULA.md, 10_systems/SKILL_SYSTEM.md,
10_systems/SKILL_EFFECTS.md, 10_systems/STATS.md, 10_systems/LEVELING.md,
10_systems/STATUS_EFFECTS.md, 10_systems/ENHANCEMENT.md, 10_systems/DROPS.md,
10_systems/INVENTORY.md, 10_systems/DEATH_PENALTY.md, 10_systems/SPAWN.md, 10_systems/AI_BEHAVIOR.md,
30_engineering/ENGINEERING_STANDARDS.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/NETWORK_PROTOCOL.md,
70_integrations/WORLD_CHANNELS.md, 70_integrations/DATABASE_PERSISTENCE.md,
70_integrations/CHAT_SOCIAL_BACKEND.md, 70_integrations/ACCOUNTS_AUTH.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md

The **server-side game-logic layer**: where each `authority: server` rule
(`10_systems/PERSISTENCE.md` §2) actually *executes* on the live topology. `10_systems/PERSISTENCE.md`
owns which data is `server`-truth; `70_integrations/BACKEND_ARCHITECTURE.md` (gated first, §9 of that
doc delegates here) owns *which component* runs it. This doc owns the third question those two leave
open: **when** it runs — the concrete tick model (§1), the movement-reconciliation cadence
`10_systems/PERSISTENCE.md` §4 deferred (§2), the client/server `CombatMath` test-vector parity
requirement `70_integrations/BACKEND_ARCHITECTURE.md` §2 flagged (§3), and, per domain (§5–§13),
where each server rule executes, what triggers it, and what it validates — citing the owning system
doc for every formula rather than restating it. It never re-derives a value: combat math stays
`10_systems/COMBAT_FORMULA.md`'s, drop odds `10_systems/DROPS.md`'s, exp curve `10_systems/LEVELING.md`'s.

Sibling boundaries (all cited in place): `70_integrations/NETWORK_PROTOCOL.md` owns the wire — every
packet named here (`hit_event`, snapshot, correction, request/response) is that doc's to serialize and
opcode; this doc owns only the *cadence and validation* behind each. `70_integrations/WORLD_CHANNELS.md`
owns occupancy caps — this doc's per-map tick cost (§1) is an input to its capacity math.
`70_integrations/DATABASE_PERSISTENCE.md` owns transaction boundaries and write cadence — this doc only
names the `10_systems/PERSISTENCE.md` §6 triggers that fire a commit. `70_integrations/CHAT_SOCIAL_BACKEND.md`
owns party exp/loot *distribution* — this doc rolls the drop and computes the exp, that tier splits it.
`70_integrations/ACCOUNTS_AUTH.md` §4 owns the gateway session bind — every request this layer trusts has
already been proven to come from the authenticated character before simulation sees it.

**Implemented when:** a live authoritative server exists (`70_integrations/BACKEND_ARCHITECTURE.md` §6/§10);
until then the interim solo build runs this same logic *client-side* through the `GameState` facade
(`10_systems/PERSISTENCE.md` §5) as a rehearsal for the boundary. The rates below become the server's
authoritative cadence when networked; the solo client simulates at its own frame rate against the same
rules, so the request→validate→apply shape (§14) is identical whether the "server" is in-process or real.

---

## 1. The execution model & the tick decision (headline)

`70_integrations/BACKEND_ARCHITECTURE.md` §1/§4 fixed the placement: the **map is the unit of
simulation**, one OTP-supervised process per live map/channel/instance on a world node (or instance
worker), holding its spawn zones, live mobs, and status timers; combat is triggered by the hit-frame
signal; only `authority: shared` position/velocity crosses the prediction boundary. It deliberately
left the rates, the per-tick-vs-event split, the scheduling, and the timer resolution to this doc.
Those are decided here — numbers, not options.

### 1.1 Two rates: simulation 20 Hz, network snapshot 10 Hz

| Rate | Value | Runs |
|---|---|---|
| **Simulation tick** | **20 Hz (50 ms)** | AI advancement, status/cooldown timer resolution, spawn maintenance, movement-reconciliation check, buff/debuff expiry, the per-tick combat-event drain (§1.2) |
| **Network snapshot** | **10 Hz (100 ms)** | Broadcast of continuous entity state (visible entities' position/velocity/animation-state/status-icon set) to each client for interpolation |

**Simulation at 20 Hz — rationale.** Side-scroller combat is hit-frame-*event*-driven, not a heavy
fixed-rate numeric integration (`70_integrations/BACKEND_ARCHITECTURE.md` §2): the tick only has to
advance AI state machines (`10_systems/AI_BEHAVIOR.md` §1), fire status ticks whose finest real cadence
is 1 s (`10_systems/STATUS_EFFECTS.md` §4.1 DoT / §4.2 `regen`), and sample reconciliation. 50 ms granularity
is imperceptible against those and keeps a busy map's loop cheap while an empty map's costs nothing
(§1.3). *Rejected:* **60 Hz** (matching the Godot 4.3 client physics rate) — the client already predicts
its own movement at 60 Hz locally; the server gains no authority by matching it and triples per-map
wakeups for nothing. *Rejected:* **10 Hz** — too coarse for cooldown/status-window feel and lets
reconciliation drift a full 100 ms before a speed-hack is caught. 20 Hz is the smallest rate that keeps
all timers within one perceptual frame.

**Snapshot at 10 Hz — rationale.** Continuous state is smoothed by client-side interpolation of remote
entities plus prediction of the local player, so the wire only needs enough keyframes to interpolate
between; 10 Hz is the proven band for dozens of entities in a population channel
(`70_integrations/WORLD_CHANNELS.md` sets the occupancy cap). *Rejected:* **20 Hz** (snapshot = sim) —
doubles per-channel bandwidth for smoothness the interpolation already supplies. *Rejected:* **30/60 Hz** —
bandwidth blowout this genre never needs. Discrete authoritative outcomes do **not** wait for a snapshot
(§1.2).

### 1.2 Per-tick vs event-driven, and the inline-vs-queued combat call

**Event-driven, pushed immediately (never wait for the snapshot):** every discrete authoritative
outcome — a resolved hit (`10_systems/COMBAT_FORMULA.md`), a status applied/expired, a death, a loot
spawn, a level-up, an enhancement result. These are emitted as events the instant they resolve so the
client can confirm/correct its optimistic prediction with minimal latency
(`70_integrations/NETWORK_PROTOCOL.md` owns the event packets).

**Per simulation tick (20 Hz):** AI state advancement and aggro scans, status/cooldown/CC-window
timer resolution (§1.4), spawn respawn-timer and off-screen-hold checks (`10_systems/SPAWN.md` §3/§5),
buff/debuff expiry, one movement-reconciliation pass per occupant (§2), and **the combat-event drain**.

**The combat call — queued, drained once per tick in deterministic order.** A validated hit-frame
event (§5.1) is *enqueued* on arrival and the queue is drained at a fixed point each simulation tick,
resolving each hit through `CombatMath.resolve(...)` (`10_systems/COMBAT_FORMULA.md` §1) in a
deterministic arrival-sequence order. **Chosen over inline resolution** because every roll draws from
the one seeded RNG service and writes the append-only audit log
(`70_integrations/BACKEND_ARCHITECTURE.md` §2/§3), and audit-log replay must be bit-reproducible: a
fixed drain order makes the RNG-draw sequence on a busy map deterministic, so a result is
server-verifiable later. It also bounds per-tick combat work (a burst of hits cannot starve the loop)
and batches naturally into the next snapshot. The cost is ≤ 50 ms of added resolution latency, which is
imperceptible and fully hidden by client-side hit prediction (the client shows an advisory number
immediately; §3 explains why that is safe). *Rejected:* **inline** resolution the moment each event
validates — nondeterministic RNG-draw interleaving across concurrent hits breaks audit-log replay, and
unbounded per-event work can starve a busy map's tick.

### 1.3 Scheduling — per-map self-scheduled, not a per-node scheduler

Each map/channel/instance process **owns its own tick loop** (a self-rescheduled 50 ms BEAM timer),
independent of every other map's. **Chosen over** a single per-node scheduler ticking all maps: a
global scheduler reintroduces exactly the coupling the OTP-process-per-map model
(`70_integrations/BACKEND_ARCHITECTURE.md` §1/§2) exists to avoid — one slow map would delay all, and
the "empty map costs nothing" invariant would be lost. Population channels are independent map processes
with independent loops, so a busy channel never stalls a sibling (fault isolation,
`70_integrations/BACKEND_ARCHITECTURE.md` §8). Concretely: a map process **parks its simulation tick
while it has zero occupants** and resumes on entry — this is the "empty map is near-free" property made
literal (initial zone population still spawns at load/transition per `10_systems/SPAWN.md` §5, before
the loop parks). A shared open-entry arena's reset-when-empty grace (`10_systems/SPAWN.md` §3,
`15_maps_system/MAPS_SYSTEM.md` §8) is a **one-shot scheduled message the map process arms as it
parks** — independent of the recurring tick loop, so the reset fires on schedule without waking the
full simulation.

### 1.4 Timer resolution — absolute timestamps, checked per tick (±50 ms)

All durations — status timers, DoT/`regen` 1 s ticks, cooldowns, hard-CC DR (10 s) and CC-immunity
(8 s) windows (`10_systems/STATUS_EFFECTS.md` §1), i-frame windows (`10_systems/COMBAT_FORMULA.md` §12),
loot ownership windows (`10_systems/DROPS.md` §7) — are stored as **absolute expiry timestamps on a
monotonic server clock**, never as decremented counters. Each simulation tick fires every *actively
swept* timer whose timestamp is now due — status expiry, DoT/`regen` boundaries, i-frame and loot
windows. **Cooldowns are the one lazily-checked exception**: stored as the same absolute timestamps but
never swept by the tick — validity is checked on demand at cast time against the ETS/Redis cooldown
table (`70_integrations/BACKEND_ARCHITECTURE.md` §5), since nothing needs to *happen* when a cooldown
lapses. **Chosen** because timestamps are robust to tick jitter and to a process being
briefly descheduled (a counter would drift; a timestamp is exact). Effective resolution is one sim tick (±50 ms), imperceptible against the finest 1 s cadence
in the design. *Failure mode:* if the monotonic clock source is unavailable the map process fails loud
in dev and, in prod, refuses to advance timers rather than firing them on a guessed interval
(`30_engineering/ENGINEERING_STANDARDS.md` directive 7 fail-safe).

---

## 2. Movement reconciliation cadence (resolving PERSISTENCE §4)

`10_systems/PERSISTENCE.md` §4 defines position/velocity as the one `authority: shared` pairing — the
client predicts locally for snappy input (P1), the server reconciles — and explicitly defers the
**algorithm** (tolerance window, correction method) and cadence out of its own scope.
`70_integrations/BACKEND_ARCHITECTURE.md` §4 fixed only that reconciliation runs on the map's own world
process against that map's own simulation. **This section resolves that deferred flag.**

**Client side (Godot 4.3, 60 Hz physics).** The client integrates the local player's movement every
physics frame on input, using the locked `base_move_speed` = 128 px/s and its active
`haste`/`swiftness`/`chill` speed modifiers (`10_systems/COMBAT_FORMULA.md` §10, `10_systems/STATS.md`
§5) — so movement is instantaneous locally. It reports position + velocity (or the input that produced
them) to the server at **20 Hz**. Remote entities are shown by interpolating the 10 Hz snapshots (§1.1).

**Server side — cadence.** The map's world process maintains its own authoritative estimate of each
occupant's position from validated inputs and the same movement constants, and runs **one
reconciliation check per occupant per simulation tick (20 Hz / 50 ms)** against that occupant's latest
report — a tick sooner than the snapshot rate, catching a divergence at negligible marginal cost since
the tick already runs.

**Tolerance envelope (accept-if-plausible, per PERSISTENCE §4).** The report is accepted as the shared
truth — the server adopts the client's position with **no correction sent** — when it lies within an
envelope of the server's own estimate: **± ½ tile (8 px at the locked 16 px grid) of positional slack,
plus a per-interval displacement margin** equal to the maximum plausible travel over the elapsed time at
the occupant's current speed cap (base × capped `haste`/`swiftness`, `10_systems/STATS.md` §6), with a
velocity-direction sanity check. A report inside the envelope is the common case and costs one
comparison. A report outside it is **rejected**: the server keeps its own authoritative position and
emits a correction.

**Correction method — forward soft-correct, no world rollback.** A small overshoot rides the next 10 Hz
snapshot as an authoritative position/velocity the client **error-blends** over 2–3 frames (no visible
teleport). A gross divergence (teleport-scale — the speed-hack / hard-desync case) is pushed as an
**immediate out-of-band correction event** the client **hard-snaps** to. The server never rewinds world
state to reconcile position: combat already resolves authoritatively on hit events (§5), so a mover's
positional divergence affects only that mover's own coordinates and is corrected *forward*, never by
replaying the map. *Rejected:* **deterministic lockstep / server-side rollback** (fighting-game style) —
overkill that would force the client to run bit-identical deterministic physics and the server to rewind,
for a genre whose combat is event-resolved, not position-resolved. *Rejected:* **server-authoritative
movement with no prediction** — violates `10_systems/PERSISTENCE.md` §4's `shared` tag and P1 snappiness.
*Rejected:* **reconciling only on the 10 Hz snapshot** — 100 ms of undetected divergence versus 50 ms,
for no saving since the sim tick is already running.

Position/velocity are **not persisted mid-run** (`70_integrations/BACKEND_ARCHITECTURE.md` §5); a map
crash re-routes the player to their last *persisted* point (`10_systems/PERSISTENCE.md` §6), and unsaved
position is disposable by design.

---

## 3. CombatMath test-vector parity (owned here per BACKEND §2/§9)

`70_integrations/BACKEND_ARCHITECTURE.md` §2 requires the server's Elixir port of `CombatMath` to be
validated against the **same** test vectors as the client's GDScript `CombatMath`
(`30_engineering/ENGINEERING_STANDARDS.md` GUT tests) so client prediction and server authority can
never diverge, and §9 flags the requirement to this doc. This section owns it.

**Mechanism — one language-neutral fixture set, two test suites.** A single version-controlled table of
vectors — `(attacker_final_block, defender_final_block, skill_descriptor, rng_stream_seed) → expected
HitResult` — is loaded by **both** the GDScript GUT suite and the server's Elixir ExUnit suite, each
asserting bit-for-bit. `CombatMath.resolve` is pure and stateless (`10_systems/COMBAT_FORMULA.md` §1)
and all randomness flows through the one seeded RNG service
(`70_integrations/BACKEND_ARCHITECTURE.md` §2), so pinning the seed/stream makes every pipeline step
deterministic and cross-language-comparable.

**Vectors must cover the whole pipeline** (`10_systems/COMBAT_FORMULA.md` §2 canonical order): the hit
roll and its `BASE_HIT`/`HIT_FLOOR`/`HIT_CEIL` clamps and `blind` penalty (§3); the element ×0 immunity
short-circuit (§2 step 2); the mitigation curve `K(L)/(K(L)+defense)` (§5); the element multiplier (§6);
the crit multiply (§4); the **±8 % variance and the rounding** — the subtle one, since
`rng.uniform(0.92, 1.08)`, `round()`, and the `max(1, round(raw))` floor must match exactly, so the
vectors pin the RNG algorithm and a rounding convention — `10_systems/COMBAT_FORMULA.md` does not yet
fix one for `round(raw)` (`10_systems/SKILL_SYSTEM.md` §4 fixes round-half-up only for rank
interpolation), so the vectors pin **round-half-up** pending that doc's owner confirming it (Open
Questions); the
`empower`/`weaken` damage-dealt multiplier (§8); and the level-difference dampener (§9). Snapshotted DoT
ticks (`10_systems/STATUS_EFFECTS.md` §1) are vectors too — a DoT tick is an ordinary `CombatMath` call
on the application-time snapshot (`10_systems/COMBAT_FORMULA.md` §4).

**Why prediction + authority coexist safely.** Parity means *given identical inputs including the RNG
draw sequence, outputs are bit-identical*. For the deterministic steps (mitigation, element, dampener,
rounding, floor) the client can and does compute the exact server answer, so its predicted number is
already correct. For the RNG-bearing steps (hit roll, crit, variance, and all of §10/§11's drop and
enhancement rolls) the client does **not** hold the server's seed, so it shows an *optimistic plausible*
prediction and always accepts the authoritative event (§14) — the parity guarantee is that the
*algorithm* is identical, so the moment the real draw is known the two agree. The fixtures feed a fixed
stream to prove the algorithm; runtime authority handles the unknowable draws. *Failure mode:* a
divergence on any vector fails CI; the server is authority, so the client is corrected to the server's
result at runtime and the GDScript is fixed to match the fixtures before the divergent build ships.

**Same fixture discipline extends** to the two other seeded rollers that move server-side unchanged
(`70_integrations/BACKEND_ARCHITECTURE.md` §2): the drop roller (§11) and the enhancement roller (§10)
each carry their own seeded vector set for the same reason — no client may reproduce or pre-empt a roll
it cannot seed.

---

## 4. Domain execution — reading guide

Sections §5–§13 are the nine `authority: server` domains. Each states, in one shape: **executes on**
(the `70_integrations/BACKEND_ARCHITECTURE.md` §1 component) · **triggered by** · **validates** ·
**owning doc** (cited, never restated). The seeded RNG service and append-only audit log are shared
dependencies; their unavailable-stance is fixed once in `70_integrations/BACKEND_ARCHITECTURE.md` §8
(block the gated roll, never fabricate) and cited, not repeated, per domain.

---

## 5. Combat resolution — `10_systems/COMBAT_FORMULA.md`

**Executes on:** `CombatMath` in the map's **world process** (`70_integrations/BACKEND_ARCHITECTURE.md`
§4/§5), pure and stateless (`10_systems/COMBAT_FORMULA.md` §1), all rolls through the seeded RNG
service writing the audit log.

**Triggered by:** the **hit-frame signal**. The client's attack/skill animation reaching its damage
frame emits a `hit_event` naming attacker, candidate targets, and the skill descriptor; the server
enqueues it and drains the queue once per simulation tick in deterministic order (§1.2). "Damage never
on a duplicate timer" (`30_engineering/ENGINEERING_STANDARDS.md`) is honored: one resolution per hit
event, no second timer.

### 5.1 What the server validates before resolving

- **Actor & authenticity** — the `hit_event` comes from the gateway-bound session for that character
  (`70_integrations/ACCOUNTS_AUTH.md` §4); the client never resolves damage, it only *requests* by
  reporting the hit frame (§14).
- **Range/geometry** — the named targets actually fall in the skill's targeting shape
  (`10_systems/SKILL_SYSTEM.md` §6) from the attacker's server-side position; out-of-shape targets are
  dropped. Facing/aim are advisory client input, re-checked here.
- **Legality of the strike** — the skill is learned and off cooldown with `essence` paid (§6), or it is
  a basic attack within `base_attack_interval` cadence (`10_systems/COMBAT_FORMULA.md` §10); an
  i-framed target takes 0 (`10_systems/COMBAT_FORMULA.md` §12), and monsters get no i-frames so player
  combos land fully.
- **Final stat blocks** — attacker and defender blocks are the server's own recomputed values (§7), with
  transient statuses already folded per `10_systems/STATS.md` §7; the client's stat numbers are never
  trusted as input (§14).

### 5.2 What it computes (cited, not restated)

The full `10_systems/COMBAT_FORMULA.md` §2 pipeline: hit/miss (§3), immunity short-circuit, base
offense × coefficient, mitigation curve (§5), element multiplier (§6), crit (§4), ±8 % variance (§7),
`empower`/`weaken` (§8), level-difference dampener (§9), `max(1, round(raw))` floor. Hit classing,
hitstun, knockback impulse, and size-class scaling are `10_systems/COMBAT_FORMULA.md` §11; a heavy hit's
cast-interrupt and boss super-armor / `phase_shift` invulnerability are §11 and
`10_systems/STATUS_EFFECTS.md` §1. The resolved `HitResult` and any death (§12) are pushed as immediate
events (§1.2). Every roll is server-verifiable against the audit log; if the RNG service or audit log is
unavailable the hit is blocked, not rolled unverifiably (`70_integrations/BACKEND_ARCHITECTURE.md` §8).

---

## 6. Skill use — `10_systems/SKILL_SYSTEM.md` / `10_systems/SKILL_EFFECTS.md`

**Executes on:** the world process (skills), with cooldown timers in the ETS/Redis cache
(`70_integrations/BACKEND_ARCHITECTURE.md` §5). Op application (§6.2) runs inline in the same process.

**Triggered by:** a client **cast request** naming the skill, chosen rank, and aim/reticle input.

### 6.1 Gate validation (the request→validate shape)

The server checks, in order, all `10_systems/SKILL_SYSTEM.md` gates — never the client:
- **Learned & ranked** — the skill is in the character's learned set at the claimed rank; tier gate
  (Lv 8 / Lv 40) and line gate satisfied (`10_systems/SKILL_SYSTEM.md` §2).
- **Prerequisite chain** met (`10_systems/SKILL_SYSTEM.md` §2 policy; edges in the skill's Phase D YAML).
- **`cooldown`** elapsed for this skill instance (per-skill, no GCD; `10_systems/SKILL_SYSTEM.md` §5),
  read from the timestamp table (§1.4).
- **`essence_cost`** payable from the current pool, after `clarity`'s cost reduction
  (`10_systems/STATUS_EFFECTS.md` §4.2) — resolved via `10_systems/SKILL_SYSTEM.md` §5, per-rank value
  interpolated from `level_data` (`10_systems/SKILL_SYSTEM.md` §4). Insufficient `essence` fails the cast.
- **Targeting shape** resolved server-side (`10_systems/SKILL_SYSTEM.md` §6); `party` resolves to `self`
  when solo.

On pass: deduct `essence`, stamp the cooldown timestamp, and run the effect list. Any skipped
`essence_cost`/cooldown/prereq gate is exactly the `10_systems/PERSISTENCE.md` §7 never-trust item this
section enforces (§14).

### 6.2 Effect-op application

The skill's ordered `effects: [...]` (`10_systems/SKILL_EFFECTS.md` §2) run top-to-bottom, each filtered
to its target class: `deal_damage` routes each hit through §5's pipeline; `apply_status` hands off to §9;
`heal`/`grant_shield`/`restore_essence` adjust pools with the §7 caps; `knockback`/`pull`/`dash`/`leap`
apply displacement/i-frames (`10_systems/COMBAT_FORMULA.md` §11/§12); `summon_entity` spawns an
owner-tagged monster-schema entity that then ticks under §13; `taunt` sets an AI forced-target
(§13); `on_hit_proc` is the only conditional, evaluated server-side with its `icd`
(`10_systems/SKILL_EFFECTS.md` §16). Op resolution is server-authoritative
(`10_systems/SKILL_EFFECTS.md` §18); the client predicts and reconciles. Cooldowns run authoritatively
server-side when live (`10_systems/SKILL_SYSTEM.md` §5).

---

## 7. Stats — `10_systems/STATS.md`

**Executes on:** the world process (`70_integrations/BACKEND_ARCHITECTURE.md` §5); the recomputed block
is the **single truth** every other section (§5 combat, §6 skills, §9 statuses) reads.

**Triggered by:** any input to the compute order — level-up (§8-here / `10_systems/LEVELING.md`),
a free-point allocation or reallocation request, an equipment/enhancement change, or a transient status
apply/expire (`10_systems/STATUS_EFFECTS.md`).

**Validates:**
- **Free-point allocation** — a spend/reallocate request is checked against the available pool
  (+2/level, `10_systems/STATS.md` §4.3); the reallocation `shards` fee is charged via the wallet
  (`10_systems/LEVELING.md` / `10_systems/ECONOMY.md`). The client requests a distribution; the server
  applies it only if the pool covers it.
- **Derived recompute as the sole truth** — the server runs the `10_systems/STATS.md` §7 compute order
  (primaries → derived formulas → soft/hard caps §6 → transient status fold, re-clamped) and stores the
  result. A **client-recomputed derived stat is never treated as truth over this stored value**
  (`10_systems/STATS.md` §8, `10_systems/PERSISTENCE.md` §7 — enforced at §14). The `10_systems/STATS.md`
  §6 soft caps on `crit_rate`/`evasion`/`haste` are applied here, so no client can present an
  over-cap block. The recomputed block feeds §5's final attacker/defender blocks.

The recompute is pure given its inputs, so it shares the §3 parity discipline where it feeds combat.
Changes commit to the character DB on the `10_systems/PERSISTENCE.md` §6 triggers
(`70_integrations/DATABASE_PERSISTENCE.md` owns the write).

---

## 8. Exp gain & level-up — `10_systems/LEVELING.md`

**Executes on:** the world process (leveling; `70_integrations/BACKEND_ARCHITECTURE.md` §5).

**Triggered by:** a monster death the character is eligible for (tag rule, §11 / `10_systems/DROPS.md`
§7), a quest turn-in (quest logic, `10_systems/QUESTS.md`), or a one-time first-clear/bestiary grant
(`10_systems/DROPS.md` §8).

**Validates & computes (cited):** the exp award is computed by `10_systems/LEVELING.md` §2's formula
(its level-difference multiplier is `10_systems/COMBAT_FORMULA.md` §9's exp column; its tier
multipliers `10_systems/LEVELING.md` §3's) — the server
derives the reward from the *server's* record of the mob level and killer level; the client never
reports an exp amount, only that a kill/turn-in occurred (§14). Crossing `exp_to_next(L)`
(`10_systems/LEVELING.md` §1) triggers the atomic level-up: `life`/`essence` refill, primary
auto-growth (`10_systems/STATS.md` §4.2), +2 free points (`10_systems/STATS.md` §4.3), and +1 skill
point (`10_systems/SKILL_SYSTEM.md` §1) — all owned there, applied here as one transaction, then a §7
recompute. Level-up is a `10_systems/PERSISTENCE.md` §6 autosave trigger, so it commits immediately
(`70_integrations/DATABASE_PERSISTENCE.md`). For party kills, this section computes the total reward;
the **party split** is `70_integrations/CHAT_SOCIAL_BACKEND.md`'s reward-arbitration
(`10_systems/social/PARTY.md` §4), not decided here. Over-leveled ("gray") kills crater toward ×0.05 by
the same §9 curve — the anti-boost is server-enforced, not client-honored.

---

## 9. Status effects — `10_systems/STATUS_EFFECTS.md`

**Executes on:** the **per-map simulation** (`70_integrations/BACKEND_ARCHITECTURE.md` §4/§5) — timers
and stacks live on the map process holding the affected entity.

**Triggered by:** an `apply_status` / `cleanse_status` op resolving (§6.2); ticked every simulation tick
(§1.4).

**Validates & ticks (cited):** application obeys the `10_systems/STATUS_EFFECTS.md` global rules — the
`source_power`/`crit_power` **snapshot at apply time** (§1), per-status stacking (`unique`/`stack`/
`refresh`) and the per-entity status ceiling with least-remaining-duration displacement,
hard-CC **diminishing returns** and the escalation-to-immunity window (§1), and tier scaling by target
(`normal`/`elite`/`boss`, §3 — bosses immune to hard CC). DoT ticks (`burn`/`poison`, percentages
owned by §4.1) and `regen` (§4.2, read live against max `life`) fire on the first sim tick at/after
each 1 s boundary and route through §5 as ordinary snapshot `CombatMath` calls, so element and
mitigation apply exactly as to direct hits (`10_systems/STATUS_EFFECTS.md` §5). Entering `die` clears
all statuses with **no post-mortem tick**; a boss `phase_shift` suspends timers and blocks new
applications (§1) — both enforced on the tick. Stat-fold debuffs (`chill`/`sunder`/`weaken`/`fortify`/
`swiftness`/`empower`) feed back through the §7 recompute (`10_systems/STATS.md` §7 step 4), not a
separate path. All timers/ticks/stacks are server-authoritative (`10_systems/STATUS_EFFECTS.md` §5); the
client animates advisory copies and is corrected on sync. Active statuses persist to the character DB on
save (`70_integrations/BACKEND_ARCHITECTURE.md` §5).

---

## 10. Enhancement attempts & soft-pity — `10_systems/ENHANCEMENT.md`

**Executes on:** the **enhancement resolver** via the seeded RNG service
(`70_integrations/BACKEND_ARCHITECTURE.md` §5), writing the audit log.

**Triggered by:** a client **attempt request** at a town smith interior naming the target equip.

**Validates & rolls (cited):** the server checks the matching-tier `emberstone` is held and the
`shards` fee is payable (`10_systems/ENHANCEMENT.md` §1/§5, fee schedule `10_systems/ECONOMY.md`),
**consumes both whether the roll succeeds or fails**, then rolls the target `+` against
`10_systems/ENHANCEMENT.md` §2's success table adjusted by the **soft-pity** state
(`10_systems/ENHANCEMENT.md` §3: +10 pp per consecutive same-`+` failure, hard pity = guaranteed on the
5th attempt). The **soft-pity counter is server-held persisted state** (`10_systems/ENHANCEMENT.md` §6),
so it survives logout and is not farmable by re-equipping. There is **no "reroll until success"** — the
client cannot re-request a fresh roll on the same seed; each attempt is one gated, audited roll, and the
per-`+` counter only ever moves forward. This is the `10_systems/PERSISTENCE.md` §7 enhancement
never-trust item (§14). On success `enhance_level` increments (never destroys/downgrades,
`10_systems/ENHANCEMENT.md` §2); the result commits to the character DB. If the RNG service or audit log
is unavailable the attempt is blocked, not rolled (`70_integrations/BACKEND_ARCHITECTURE.md` §8).

---

## 11. Drop rolls & loot ownership — `10_systems/DROPS.md`

**Executes on:** the **loot roller** (seeded RNG service, `70_integrations/BACKEND_ARCHITECTURE.md` §5),
writing the audit log; ownership timers on the map process (§1.4).

**Triggered by:** a monster death (server-detected in §5), which rolls that mob's `drop_mob_NNN` table.

**Validates & rolls (cited):** each table row rolls **independently** on the monster's death
(`10_systems/DROPS.md` §1), using the `10_systems/DROPS.md` §2 chance buckets, §5 per-tier table shapes,
§5.5 pool rarity weights, and the §3 `shards` faucet (guaranteed per kill, level-scaled, tier-multiplied,
**not** `fortune`-affected). The `fortune` loot bias reads `10_systems/STATS.md` §3's
`fortune_drop_bonus` hook and applies `10_systems/DROPS.md` §4's `m` multiplier (capped +100 %, adjusted
chance clamped ≤ 0.95). The first-ever region-boss clear guarantees one unique (`10_systems/DROPS.md`
§5.3 bad-luck protection). No client may re-roll a table or self-assign `rarity`/`qty`/pool result
(`10_systems/DROPS.md` §9, `10_systems/PERSISTENCE.md` §7 — §14).

**Loot ownership tags (cited):** on death, drops spawn **tagged** to whoever dealt or took damage to/from
the monster (`10_systems/DROPS.md` §7 anyone-who-tagged rule) — an **exclusive 60 s** window for
eligible players, **free 60–120 s**, **despawn at 120 s**; `shards` and quest items auto-route to the
tagger and never lie on the ground. The window timers are timestamp-based (§1.4). Solo, the single tagger
owns everything; in a party, eligibility is shared and the **per-drop split is
`70_integrations/CHAT_SOCIAL_BACKEND.md`'s** reward arbitration (`10_systems/social/PARTY.md` §5),
not decided here — this section owns the roll and the tag, that tier owns the distribution. No minted
items/`shards` and no self-assigned untagged drop (`10_systems/PERSISTENCE.md` §7 → §14).

**Inventory & bank operations (the remaining PERSISTENCE §2 ledger row).** Pickup requests against
the tag window above, item move/equip/use, stack merges, and bank deposits/withdrawals execute in
the world process's inventory logic (`70_integrations/BACKEND_ARCHITECTURE.md` §5's "Inventory logic
in world process" row); every rule they validate — tab/slot legality, stack caps, the anti-dupe and
no-minted-items laws — is `10_systems/INVENTORY.md`'s (§9 for the never-trust items), cited not
restated, and each is an ordinary §14 request→validate→delta flow. Storage is
`70_integrations/DATABASE_PERSISTENCE.md`'s; the wire packets are `70_integrations/NETWORK_PROTOCOL.md`'s.

---

## 12. Death & bind point — `10_systems/DEATH_PENALTY.md`

**Executes on:** the world process (defeat consequence, bind point;
`70_integrations/BACKEND_ARCHITECTURE.md` §5); the bind point is character-DB truth.

**Triggered by:** a character's `life` reaching 0 (server-detected in §5).

**Validates & applies (cited):** on defeat the server plays out `10_systems/DEATH_PENALTY.md`'s flow —
clear all statuses with no post-mortem tick (§1, shared with §9), apply the exp cost by
`10_systems/DEATH_PENALTY.md` §2's bracket formula (clamped there so de-leveling is structurally
impossible), and apply **no durability loss and no `shards`
loss** (`10_systems/DEATH_PENALTY.md` §3 — there is no durability field to touch). Respawn is at the
character's stored **bind point** (`10_systems/DEATH_PENALTY.md` §4), set only by deliberately resting at
a valid bind-town inn — never automatically on death. **Bind changes are validated server-side**: a rest
request is honored only from a valid bind town's inn interior (roster `10_systems/DEATH_PENALTY.md` §4's); the client cannot self-assign a
bind. Party-instance deaths use the `10_systems/DEATH_PENALTY.md` §5.3 fallen/Release/re-enter override
(the instance persists across member deaths, `10_systems/SPAWN.md` §7) rather than §4; a full-party wipe
resets the instance (§13-here spawn ownership). Revive is reserved (`10_systems/DEATH_PENALTY.md` §6) —
no op grants it this arc, so the server offers no revive path. The exp change and any bind update commit
on the `10_systems/PERSISTENCE.md` §6 triggers.

---

## 13. Spawn & AI tick ownership — `10_systems/SPAWN.md` / `10_systems/AI_BEHAVIOR.md`

**Executes on:** the **per-map simulation** (`70_integrations/BACKEND_ARCHITECTURE.md` §4) — the map
process owns its spawn zones and every live mob's AI. Instances tick identically on their instance
worker; a vacant map parks its tick (§1.3).

**Simulated on the server (per simulation tick):**
- **Spawn maintenance** — zone `target_count`/`max_concurrent` upkeep, per-tier respawn timers
  (values `10_systems/SPAWN.md` §3's), and the **off-screen hold** rule
  (`10_systems/SPAWN.md` §5: a respawn whose point is on-screen is *held*, not lost or re-timed, and
  resolves on the next tick the point is clear). The server owns which points are "off-screen" per each
  present player's viewport. Shared open-entry arena reset-when-empty (grace value
  `10_systems/SPAWN.md` §3's) and raid-instance spawn scoping (`10_systems/SPAWN.md` §7) are the same
  process's timers.
- **AI advancement** — every mob's profile state machine (`10_systems/AI_BEHAVIOR.md` §1: `idle`/
  `patrol`/`chase`/`windup`/`attack`/`recover`/`flee`/`return`), aggro scans (`sight`/`proximity`/
  `on_hit`/`on_ally_call` with the vertical band, §2), leash checks, and `boss_scripted` phase
  transitions on `life_threshold_pct` crossings (`10_systems/AI_BEHAVIOR.md` §15, interrupt-immediate).
  A monster's `windup` committing to a hit-frame is what emits the mob's own `hit_event` into §5's queue
  — monster attacks resolve through the identical pipeline (`10_systems/SKILL_EFFECTS.md` §17). The
  elite/boss `spawn`-flourish invulnerability window (`10_systems/SPAWN.md` §6) and the `telegraph`
  requirement (`10_systems/AI_BEHAVIOR.md` §2) are enforced on the tick. Summoned entities
  (`summon_entity`, §6.2) tick here under an `owner` tag.

**Client only animates (never authoritative):** the visual interpolation of mob positions between
snapshots, the `telegraph`/`spawn`/`attack` animation playback, and speech/particle flavor. The client
predicts nothing about mob AI decisions or spawns — those arrive as authoritative snapshots (continuous
state) and events (a spawn, a phase-shift, a death). A client claim about a mob's state is never trusted;
it requests only its *own* actions (§5/§6) and receives mob state as truth.

---

## 14. PERSISTENCE §7 never-trust list → validating section (the acquisition rule)

`10_systems/PERSISTENCE.md` §7 enumerates what the client may never mint, self-assign, or re-roll. The
**acquisition rule** is uniform across all of them and is the spine of this whole layer: **the client
only ever *requests*; the server rolls/validates and responds with authoritative deltas.** A client
message is a statement of *intent* ("I cast X", "I attacked Y", "I looted Z", "I attempted +7"), never a
statement of *outcome*. The server owns every outcome and pushes it back as an event the client's
optimistic prediction reconciles to (§3 explains why that is safe).

| `10_systems/PERSISTENCE.md` §7 never-trust item | Validated in | Request → validate → authoritative delta |
|---|---|---|
| No self-assigned drop `rarity`/`qty`/pool result | §11 | Client reports a kill; server rolls the table and responds with the drops |
| No minted items/`shards`; no self-assigned untagged drop | §11 (tag/faucet), §8 (exp/kill credit) | Server credits only the tagged killer; `shards`/loot are server-rolled, never client-declared |
| No client-recomputed derived stat treated as truth | §7 | Client requests an allocation; server recomputes the whole block and stores it as sole truth |
| No "reroll until success" on enhancement | §10 | Client requests one attempt; server consumes fee+stone, rolls once against server-held pity, responds |
| No skipped `essence_cost`/cooldown/prereq gate (skills) | §6 | Client requests a cast; server checks every gate before deducting `essence` and running effects |

Quest actions carry the same never-trust gate (`10_systems/PERSISTENCE.md` §7,
`10_systems/QUESTS.md` §9) and follow this identical request→validate→delta shape in the quest-logic
component (`70_integrations/BACKEND_ARCHITECTURE.md` §5); the mechanism is this section's, the quest
values are `10_systems/QUESTS.md`'s. Session authenticity behind every request is
`70_integrations/ACCOUNTS_AUTH.md` §4's gateway bind — simulation only ever sees requests already proven
to come from the acting character.

---

## Open Questions

Tick rates (§1), the reconciliation cadence and envelope (§2), the queued combat-drain call (§1.2), and
timer resolution (§1.4) are **decided** here, not open. Only game-design residue and cross-doc
confirmations remain:

- **Reconciliation tolerance tuning.** The ½-tile + speed-margin envelope and the soft-blend/hard-snap
  thresholds (§2) are first-pass and want playtest tuning against real Godot 4.3 client feel and the
  `10_systems/COMBAT_FORMULA.md` §10 `base_move_speed`; the *shape* (accept-if-plausible, forward
  correct, no rollback) is fixed, the numbers are tunable. Owner: this doc with the client movement pass.
- **Anti-cheat posture beyond reconciliation** — repeated out-of-envelope reports (§2) or gate-failing
  requests (§14) are a signal a live-ops fraud/telemetry system should consume
  (`70_integrations/TELEMETRY_ANALYTICS.md`); what threshold trips a flag or a kick is an operational
  policy, not a simulation rule, and is not decided here.
- **Out-of-combat `life`/`essence` regen (resting)** is still unowned across
  `10_systems/STATS.md`/`10_systems/COMBAT_FORMULA.md` (their shared Open Question); when a rest rule
  lands it will tick on the §1 simulation loop like any other timer, but this doc cannot site a rule that
  does not yet exist. Flagged, not resolved.
- **Snapshot interest management** — whether a busy population channel needs per-client area-of-interest
  filtering on the 10 Hz snapshot (§1.1) rather than whole-map broadcast is a capacity question owned by
  `70_integrations/WORLD_CHANNELS.md`; this doc fixes the cadence, that doc fixes who receives which
  entities. Confirm at their authoring.
- **Party reward-arbitration handoff** — §8/§11 compute the total exp reward and roll the drop, then hand
  the split to `70_integrations/CHAT_SOCIAL_BACKEND.md` (`10_systems/social/PARTY.md` §4/§5). The exact
  request/response boundary between the world process and the party service is that sibling's to finalize;
  named here, not designed.
- **`round(raw)` rounding convention** — `10_systems/COMBAT_FORMULA.md` never states a rounding
  convention for its damage-pipeline `round(raw)` step (`10_systems/SKILL_SYSTEM.md` §4's round-half-up
  covers rank interpolation only). §3's parity vectors pin **round-half-up** so the two implementations
  cannot diverge; flagged to `10_systems/COMBAT_FORMULA.md`'s owner (ROLE_SYSTEMS_ARCHITECT) to confirm
  and state it in that doc, at which point §3 cites it instead of pinning it.
