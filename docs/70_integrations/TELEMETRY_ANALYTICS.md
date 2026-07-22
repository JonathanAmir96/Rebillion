# TELEMETRY_ANALYTICS.md — Balance Telemetry Event Taxonomy & Privacy Stance

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/VALIDATION.md,
10_systems/PERSISTENCE.md, 10_systems/LEVELING.md, 10_systems/ECONOMY.md, 10_systems/DROPS.md,
10_systems/ENHANCEMENT.md, 10_systems/DEATH_PENALTY.md, 10_systems/QUESTS.md, docs/WORLD_PLAN.md,
30_engineering/ENGINEERING_STANDARDS.md (locked, cited only), 60_agents/roles/ROLE_INTEGRATION_ENGINEER.md.
Sibling docs authored this same wave: 10_systems/ONBOARDING_FTUE.md (FTUE beat
catalog), 70_integrations/ACCOUNTS_AUTH.md (identity + deletion posture).

Owner doc for **what the game measures about play, and what it deliberately does not**. This is
the event taxonomy a future analytics pipeline emits so balance owners (LEVELING, ECONOMY, DROPS,
ENHANCEMENT) can check their first-pass numbers against real play, plus the privacy stance that
bounds the whole system. Design only — no schema-as-code, no vendor, no pipeline implementation;
that is coding-pass territory per `ROLE_INTEGRATION_ENGINEER.md`. This doc does not restate any
system's *rules* or *numbers* — it only names the event that would observe them.

## 1. Purpose & principles

Telemetry exists to **tune balance**, not to surveil players. Every event in §3 answers a
specific balance question (§6) already implied by an owning doc's first-pass numbers — this doc
adds no new game rules, it only instruments existing ones. Four principles:

1. **Aggregate-first.** Dashboards are built from cohort aggregates (by level band, region,
   session), never a per-player feed reviewed as a default workflow. Per-player drill-down is an
   exception path (e.g. a reported exploit), not the normal analysis loop.
2. **Instrument the doubt, not everything.** An event exists because an owning doc flagged a
   first-pass number as "retune at the D/E gate" (LEVELING §1's `/played` estimate, ECONOMY §5's
   income-vs-sink model, DROPS/ENHANCEMENT's rate assumptions) — not because it is easy to log.
3. **Never gameplay-blocking.** Telemetry is a side channel; see §7.
4. **Cite, don't restate.** An event's dimensions borrow tokens verbatim from GLOSSARY/WORLD_PLAN;
   this doc never re-derives a curve, a fee, or a drop rate to decide what "normal" looks like —
   that comparison is the dashboard's job (§6), reading the owning doc's published numbers.

## 2. Naming convention & envelope

Every event name is **snake_case**, prefixed `evt_`, shaped `evt_<family>_<action>` (e.g.
`evt_level_up`, `evt_shard_faucet`). This prefix is this doc's own convention — no other doc in
the tree names events; do not invent a second scheme.

Every event carries a common envelope plus its own fields (§3):

| Envelope field | Meaning |
|---|---|
| `event` | The `evt_*` name |
| `ts` | Client wall-clock timestamp at emit (server may re-stamp on ingest) |
| `player_id` | Pseudonymous ID (§5) — never an email, account name, or IP |
| `character_id` | Which of the account's ≤3 save slots (`10_systems/PERSISTENCE.md` §6) |
| `level` | Character `level` at emit time |
| `job_line` | GLOSSARY job-line token (`novice`/`bulwark`/`keeneye`/`weaver`/`flicker`) |
| `region` | GLOSSARY/WORLD_PLAN region slug (`emberfoot`…`clockwork`) |
| `map_id` | `map_NNN` (`docs/ID_REGISTRY.md`) |
| `authority` | `server` \| `client` (§4 — who may treat this event's payload as fact) |
| `unverified` | `true` in the interim solo build (§4); dropped once a real server exists |

Level *bands* (novice/1st/2nd job, etc.) are not computed by this doc — a dashboard buckets the
raw `level`/`job_line` fields against whatever band a given owning doc (LEVELING, DEATH_PENALTY)
currently defines, so this taxonomy never goes stale when a band boundary is retuned.

## 3. Event taxonomy

### 3.1 Progression family

| Event | Trigger | Key fields (beyond envelope) | Emits from |
|---|---|---|---|
| `evt_level_up` | `level` increases (`10_systems/LEVELING.md` §5) | `new_level`, `exp_source_hint` (hunting/quest/other, best-effort) | server (once live) |
| `evt_job_advance` | 1st/2nd job advancement granted (`10_systems/JOBS.md`) | `job_line`, `tier` (`1st`/`2nd`) | server |
| `evt_quest_accept` | Quest accepted (`10_systems/QUESTS.md` §2/§6 gates pass) | `quest_id`, `quest_type` (`main`/`side`) | server |
| `evt_quest_complete` | Quest turned in (`10_systems/QUESTS.md` §9) | `quest_id`, `quest_type`, `exp_reward`, `shards_reward` | server |
| `evt_ftue_beat` | A first-time-experience milestone fires | `beat_id` | client |

`evt_ftue_beat`'s concrete `beat_id` catalog (first move, first kill, first level-up, first
death, first job pilgrimage, etc.) is owned by the sibling `10_systems/ONBOARDING_FTUE.md`, not
yet authored — this doc only reserves the event and its shape; the beat list is that doc's Open
Question to resolve, not this one's to guess.

### 3.2 Death family

| Event | Trigger | Key fields | Emits from |
|---|---|---|---|
| `evt_death` | `life` reaches 0 (`10_systems/DEATH_PENALTY.md` §1) | `cause` (`mob_NNN` or `environmental`), `mob_tier` (`normal`/`elite`/`boss`), `context` (`field`/`dungeon`/`arena`/`raid`, §5.1–5.3), `level`, `exp_lost` | server |
| `evt_release` | Rift raid fallen character releases (`DEATH_PENALTY.md` §5.3) | `raid_id`, `staging_map_id` | server |

`exp_lost` and `pct` are already computed per `10_systems/DEATH_PENALTY.md` §2 by the time this
event fires; this doc never restates that formula.

### 3.3 Economy family

One faucet/sink event per row of `10_systems/ECONOMY.md` §1/§2 — this doc does not re-enumerate
those tables, only names the two events that log against whichever row fired:

| Event | Trigger | Key fields | Emits from |
|---|---|---|---|
| `evt_shard_faucet` | Any `shards` gain | `faucet_type` (`drop`/`quest`/`vendor_sell`, per ECONOMY §1) | server |
| `evt_shard_sink` | Any `shards` spend | `sink_type` (`consumable`/`enhance_fee`/`stat_realloc`/`guild_create`/`market_fee`, per ECONOMY §2), `amount` | server |

### 3.4 Drops & enhancement family

| Event | Trigger | Key fields | Emits from |
|---|---|---|---|
| `evt_drop_roll` | A drop-table row resolves (`10_systems/DROPS.md` §1) | `mob_id`, `mob_tier`, `chance_bucket` (§2 named bucket or `raw`), `hit` (bool), `ref_kind` (`item`/`pool`/`shards`) | server |
| `evt_loot_pool_roll` | A pool roll instantiates a rarity (`DROPS.md` §5.5/§6) | `pool_id`, `rarity_source`, `rarity` (GLOSSARY rarity token), `fortune_mult_applied` | server |
| `evt_enhance_attempt` | An enhancement attempt resolves (`10_systems/ENHANCEMENT.md` §2) | `target_plus`, `success` (bool), `soft_pity_stacks`, `hard_pity_triggered` (bool), `fee_paid` | server |

Drop/enhancement events log the **outcome already rolled** by their owning system; this taxonomy
never implies telemetry re-rolls, previews, or influences an outcome.

### 3.5 Session family

| Event | Trigger | Key fields | Emits from |
|---|---|---|---|
| `evt_session_start` | Character enters the world (load or character-select) | `platform` (coarse: `windows`/`mac`/`linux`) | client |
| `evt_session_end` | Clean quit or timeout | `duration_s` | client |

### 3.6 Performance family (coarse only)

| Event | Trigger | Key fields | Emits from |
|---|---|---|---|
| `evt_client_perf` | Periodic sample (e.g. once/minute), never per-frame | `fps_bucket` (`<30`/`30-59`/`60+`) | client |
| `evt_client_disconnect` | Client loses/ends its session unexpectedly | `reason` (coarse: `crash`/`network`/`unknown`) | client |

Performance telemetry is intentionally coarse (bucketed, not raw per-frame traces) — it exists to
spot systemic stutter regions, not to profile an individual machine.

## 4. Client/server emitting split

`10_systems/PERSISTENCE.md` §1's three-way authority tag (`server`/`client`/`shared`) is the
contract this doc satisfies, not a new one: an event may only claim a fact for the side that owns
it.

- **Once a real server exists:** every event in §3.1–§3.4 (progression, deaths, economy, drops,
  enhancement — all `authority: server` data per `PERSISTENCE.md` §2) is emitted **server-side
  only**. Any client-side copy is advisory/predictive (identical to how the client predicts
  position, `PERSISTENCE.md` §4) and is never the record analysts trust — a client cannot be
  allowed to self-report a drop rarity or an `exp` grant it wasn't actually authoritatively given.
  Session (§3.5) and performance (§3.6) events are genuinely client-local facts and always emit
  client-side, live build or not.
- **The interim solo build has no server** (`PERSISTENCE.md` §5 — the `GameState` facade over a
  local save). Every event, including the §3.1–§3.4 families, is emitted **client-side** during
  this run, with the envelope's `unverified: true` flag set. This is the telemetry-side mirror of
  `PERSISTENCE.md` §7 ("what is never trusted from the client"): the same events will exist
  unchanged once a server lands, they simply carry a trust flag until then rather than a different
  shape — no event is redesigned at that transition, only re-homed and un-flagged.

## 5. Privacy stance

- **No PII in any event payload.** No email, real name, IP address, device serial, or free-text
  chat content ever appears in a §3 event. `platform` (§3.5) is the only device-adjacent field,
  and it is a coarse OS bucket, not a fingerprint.
- **Pseudonymous `player_id`.** An opaque, non-reversible-by-analysts identifier tied to the save
  slot, not the real account. Minting/deletion/rotation belongs to the sibling
  `70_integrations/ACCOUNTS_AUTH.md` (authored this wave); this doc only requires the ID be
  purgeable on that doc's account-deletion trigger (Open Questions).
- **Retention window.** Raw per-event records are kept for a bounded window (proposed 90 days),
  enough to compute the §6 dashboards over a full playtest wave, then rolled up into aggregate-
  only cohort tables and discarded. Exact length is owner-priced, not fixed here.
- **Aggregation before analysis.** The default (and pre-launch, only) consumption path is cohort
  dashboards (level band, region, session length) — never a routine raw per-`player_id` timeline.
  Per-player drill-down (e.g. an exploit report) is an explicit exception, not the normal use.
- **Opt-out.** Session (§3.5) and performance (§3.6) — the non-essential families — are player-
  toggleable off. Progression/death/economy/drop/enhancement (§3.1–§3.4) is the only pre-launch
  feedback loop for validating LEVELING/ECONOMY/DROPS/ENHANCEMENT's first-pass numbers, so it is
  **not** independently opt-outable during this design/playtest phase; a full account-level
  opt-out is deferred to `ACCOUNTS_AUTH.md`'s privacy controls once that doc exists.

## 6. Balance dashboards — questions this taxonomy must answer

1. **Pacing:** where do players actually stall relative to `10_systems/LEVELING.md` §1's
   `/played`-by-band table — is the modeled 480-kills/hour, 70/25/5 hunting/quest/other split
   (§4) holding, or does real `evt_level_up` cadence diverge from a level band onward?
2. **The Verdant→Gloomwood gap:** does `docs/WORLD_PLAN.md`'s Open Question (Verdant ends Lv 16,
   Gloomwood starts Lv 20) show up as a stall or a region-abandonment spike in `evt_level_up` /
   `evt_session_end` around that boundary, or do players route through Tidewatch cleanly as
   intended?
3. **Economy health:** do observed `evt_shard_faucet`/`evt_shard_sink` totals per level band match
   `10_systems/ECONOMY.md` §5's modeled net-positive session (the "bite" rising into the 50–70
   band, easing by 90), or is some band actually net-negative in practice?
4. **Drop feel:** do `evt_drop_roll`/`evt_loot_pool_roll` outcome rates track `10_systems/DROPS.md`
   §2/§5.5's named buckets and rarity weights, or does a region's real hit rate feel worse/better
   than the modeled anchors?
5. **Enhancement swinginess:** does `evt_enhance_attempt`'s observed attempts-to-success cluster
   near `10_systems/ENHANCEMENT.md` §3's modeled ≈2.6-expected/5-worst-case at each `+`, or are
   players hitting hard pity (5th-attempt guarantee) far more than the 25%-base math predicts?
6. **Death clustering & sting:** which `evt_death` `cause`/`map_id` pairs cluster hardest per
   region, and does `exp_lost` (`DEATH_PENALTY.md` §2) correlate with `evt_session_end` spikes
   immediately after (a proxy for "death soured the session," the thing P2 explicitly guards
   against)?

## 7. Failure modes — fire-and-forget, never gameplay-blocking

Telemetry is a side channel, not part of the authoritative save path (`10_systems/PERSISTENCE.md`
owns that separately). Concretely:

- Every emit is **fire-and-forget**: the calling system never awaits an ack, retries
  synchronously, or blocks a frame, combat resolution, or save on a telemetry send succeeding.
- **Lossy transport is acceptable.** A dropped batch (crash before flush, a network blip)
  degrades dashboard sample size, not gameplay or the save file — the deliberate trade that keeps
  telemetry off the critical path.
- A telemetry outage or full send-queue must **never** surface as a player-facing error, block an
  action, or gate a reward — a reward conditioned on a successful telemetry send is a design bug
  against this doc, not a valid pattern.

## Open Questions

- Exact raw-retention window (§5, proposed 90 days) is owner-priced (storage/vendor cost), not
  fixed here — flagged for the owner alongside `ACCOUNTS_AUTH.md`'s cost decisions.
- The pseudonymous `player_id`'s minting/rotation/deletion mechanism is jointly owned with the
  not-yet-authored `70_integrations/ACCOUNTS_AUTH.md`; this doc assumes it will be purgeable on
  account deletion but does not itself design that trigger.
- `10_systems/ONBOARDING_FTUE.md`'s concrete `beat_id` catalog for `evt_ftue_beat` (§3.1) is not
  yet authored; this doc reserves the event shape only, not the beat list.
- Whether a full account-level analytics opt-out (beyond session/performance, §5) is offered pre-
  launch or only once `ACCOUNTS_AUTH.md` lands is unresolved; default here is opt-out limited to
  the non-essential families until that doc exists.
- The concrete transport/vendor (self-hosted event log vs a third-party analytics SDK) is
  explicitly out of scope for this design doc — a coding-pass decision once
  `30_engineering/ENGINEERING_STANDARDS.md`'s CI/build tooling is scoped; this doc fixes only the
  event contract it must satisfy.
- Whether `evt_drop_roll` should log **every** rolled row (including misses) or only hits is
  unresolved; misses give a truer hit-rate denominator but roughly triple event volume at
  `elite`/`boss` tables (§3.4) — default **log both**, revisit if volume is a cost concern.
