# SERVER_LOGGING_SPEC.md — Server Logging & Anti-Cheat Audit

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/VALIDATION.md, docs/ID_REGISTRY.md,
10_systems/PERSISTENCE.md, 10_systems/LEVELING.md, 10_systems/ECONOMY.md, 10_systems/DROPS.md,
10_systems/ENHANCEMENT.md, 10_systems/DEATH_PENALTY.md, 10_systems/INVENTORY.md,
10_systems/social/CHAT.md, 10_systems/social/TRADING.md, 10_systems/social/MARKET.md,
10_systems/social/MAIL.md,
70_integrations/BACKEND_ARCHITECTURE.md, 70_integrations/NETWORK_PROTOCOL.md,
70_integrations/GAMEPLAY_SIMULATION.md, 70_integrations/ACCOUNTS_AUTH.md,
70_integrations/CHAT_SOCIAL_BACKEND.md, 70_integrations/DATABASE_PERSISTENCE.md,
70_integrations/TELEMETRY_ANALYTICS.md, 30_engineering/ENGINEERING_STANDARDS.md (locked, cited only)

Owner doc for the **server-side operational log**: what the live server writes to disk about play,
in what format, at what cost, and which written facts trigger a human anti-cheat review. It is the
manual-forensics companion to three existing records it must never duplicate:

| Record | Owner | Purpose | This doc's relationship |
|---|---|---|---|
| Balance telemetry (`evt_*`) | `70_integrations/TELEMETRY_ANALYTICS.md` | Aggregate balance tuning; PII-free by design | Different domain — this log is per-event audit, not cohort analytics; the two taxonomies stay separate on purpose (§2.4) |
| Seeded-RNG audit log | `70_integrations/BACKEND_ARCHITECTURE.md` §3, `70_integrations/DATABASE_PERSISTENCE.md` | Forensic replay of every gated roll | Cited, never restated — a §5 reviewer *joins against* it; this doc never re-logs roll internals |
| Truth ledger (Postgres) | `70_integrations/DATABASE_PERSISTENCE.md` | The authoritative state itself | Logs are observability **about** the ledger, never a second source of truth |

Everything here is design; the writer/decoder implementation is coding-pass territory
(`docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md`). **Implemented when:** a live authoritative
server exists (`70_integrations/BACKEND_ARCHITECTURE.md` §6/§10). The interim solo build may reuse
the §3 encoder for local debug logs, but no channel below is a solo-build requirement.

**Prime constraint (owner directive): log size is optimized as far as possible.** The canonical
JSON schemas in §2/§4 are the *logical* contract — what a record means. The *physical* format on
disk and on internal sockets is the compact single-line string encoding of §3; JSON is a decoder
projection produced on demand, never written in the hot path. World processes emit the already-
encoded line bytes internally and the writer appends them verbatim — one encode, zero
re-serialization (§7).

---

## 1. Log channels & verbosity hierarchy

Five channels, each its own file family (§6). A record belongs to exactly one channel; detectors
that *derive* a suspicion from another channel's facts write to `SECURITY_ALERTS`, so factual
channels stay clean records and the alerts channel stays reviewable in one place.

| Channel | Contents | Prod level | Dev level |
|---|---|---|---|
| `CHAT` | Every relayed chat message, filter hits, throttles, mutes, reports (`10_systems/social/CHAT.md` channels; relay internals `70_integrations/CHAT_SOCIAL_BACKEND.md` §2/§4) | INFO | DEBUG |
| `PLAYER_PROGRESSION` | `exp`/`level` movement, job advancement, quest turn-ins, stat allocation, map-enter context | INFO | DEBUG |
| `ECONOMY` | Every `shards` wallet delta, item instance lifecycle (grant/remove), trades, market, mail COD, enhancement attempts | INFO | DEBUG |
| `COMBAT` | Per-minute combat summaries, deaths, boss kills, validation-reject summaries; per-hit detail at DEBUG only | INFO | DEBUG |
| `SECURITY_ALERTS` | Session identity records, movement/action validation failures, detector flags (§5), GM action audit | INFO | DEBUG |

Verbosity levels, lowest to highest:

| Level | Meaning | Written when |
|---|---|---|
| `DEBUG` | Per-event firehose detail (e.g. every hit, every accepted movement report summary) | Dev/staging builds, or a per-account tap a GM enables during an active investigation |
| `INFO` | The durable factual record — every row a §5 detector or a human reviewer joins against | Always |
| `WARN` | A validation failure or detector flag worth a human's eventual attention | Always |
| `CRITICAL` | An invariant is broken (duplication, wallet discontinuity) — page-worthy, review queue jumps | Always; also fanned out to the alert stream (§7) |

A record's level is a fixed property of its event code (§3.2) — it is **not** stored per line,
which saves a field on every row. Escalation never rewrites a record; it emits a new
`SECURITY_ALERTS` record referencing the old one.

## 2. Canonical JSON log schema (logical contract)

### 2.1 Envelope

Every log record, fully projected by the decoder (§3.5), is this JSON object:

```json
{
  "timestamp_utc": "2026-07-24T13:45:12.048Z",
  "channel": "ECONOMY",
  "level": "INFO",
  "event_type": "log_shard_delta",
  "session_id": "k3",
  "user_id": "acct_9f2c",
  "character_id": "char_2",
  "ip_address": null,
  "node": "world-01",
  "map_id": "map_042",
  "payload": { }
}
```

| Field | Type | Notes |
|---|---|---|
| `timestamp_utc` | RFC3339 string, ms precision | Server clock only; clients never stamp a log record (`10_systems/PERSISTENCE.md` §1 — a client claim is not a fact) |
| `channel` | enum §1 | Implied by the file the line lives in (§3.1) — never stored per line |
| `level` | enum §1 | Implied by `event_type` (§1) |
| `event_type` | `log_*` token | From the §3.2 registry; the `log_` prefix is this doc's namespace, deliberately distinct from telemetry's `evt_` (§2.4) |
| `session_id` | string | Short per-node session ordinal (§3.3), the join key for everything |
| `user_id` | `acct_*` string | Account id (`70_integrations/ACCOUNTS_AUTH.md` §2). **Stored once per session** in the session-open record; every other row resolves it via `session_id` (§3.3) |
| `character_id` | string | Same resolution rule as `user_id` |
| `ip_address` | string or null | **Only ever stored on `log_session_open` and `log_auth_anomaly`** (§4.5); null in every other projected record. See §8 |
| `node` | string | Emitting node; implied by the file path (§6.1) |
| `map_id` | `map_NNN` or null | Stored inline only where it is analytically primary (deaths, drops); otherwise resolved from the session's `log_map_enter` timeline |
| `payload` | object | Event-specific fields, §4 |

### 2.2 Payload typing rules

- Field names use `00_vision/GLOSSARY.md` tokens verbatim where they carry stats/resources/
  currency (`exp`, `level`, `shards`, `rarity`, `enhance_level`, …) — the log never re-spells a
  canonical token, same rule as the wire (`70_integrations/NETWORK_PROTOCOL.md` §2).
- Quantities are integers; `shards` deltas are signed integers; durations are integer seconds
  unless the field name ends `_ms`.
- Every reference field holds a registry id (`mob_NNN`, `item_equip_NNNN`, `quest_NNN`,
  `skill_<line>_NNN`, `op_NNNN`) — resolvable against `docs/ID_REGISTRY.md`, never a display name.

### 2.3 Item instance identity — `item_uid`

The duplication checks in §4.3/§5 need to follow a *specific* item, not a species. The server
mints an **`item_uid`** (opaque, unique, base36) for every non-stackable `item_equip_*` instance
at creation (drop instantiation, quest grant, vendor buy) and logs it at every custody change.
Stackable `use`/`etc` items are tracked by `item_id` + `qty` only. The `item_uid` is a **logging/
audit identity**: whether the live inventory schema also persists it is
`70_integrations/DATABASE_PERSISTENCE.md`'s call (flagged, Open Questions) — this doc only
requires that the *log* carries it consistently from mint to destruction.

### 2.4 Why this is not telemetry

`70_integrations/TELEMETRY_ANALYTICS.md` §2 fixes that no other doc names `evt_*` events; this doc
therefore mints a **separate `log_*` namespace** rather than extending that one, because the two
records have opposite postures: telemetry is aggregate-first, PII-free, lossy-by-design, opt-out-
bearing; the audit log is per-event, identity-bearing (§8), and the record a human trusts during
an investigation. Where both observe the same fact (a level-up, a `shards` faucet), each writes
its own record to its own pipeline — they are never merged, deduplicated, or derived from one
another.

## 3. Physical format — compact line encoding (the size optimization)

### 3.1 File header

Each log file is UTF-8 text, one record per `\n`-terminated line. The first line is a file
header carrying everything constant for the whole file, so no line repeats it:

```
#RLOG 1 SECURITY_ALERTS world-01 2026-07-24
```

Fields: format version (`1`), channel, node, UTC date. The header is what lets every data line
drop its `channel`, `node`, format version, and date.

### 3.2 Line grammar

```
<code>|<ts>|<sid>|<payload fields...>
```

| Position | Field | Encoding | Why it is cheap |
|---|---|---|---|
| 1 | `code` | Decimal event code from the §3.2 registry table (2–3 digits) | Replaces the `event_type` string *and* the `level` string |
| 2 | `ts` | Milliseconds since the header date's 00:00 UTC (≤8 digits) | Daily rotation (§6.2) is anchored to the same 00:00 UTC boundary as the game's day reset (`10_systems/PERSISTENCE.md` §2.1), so an offset always reconstructs to a full `timestamp_utc` |
| 3 | `sid` | Per-node base36 session ordinal (§3.3); `0` for node-scope records | Replaces `user_id` + `character_id` + `ip_address` on every line |
| 4+ | payload | Positional, pipe-delimited, per-code field order fixed in §4 | No key names on disk — the §4 tables *are* the key names |

Escaping: `|` and `\n` may appear only in free-text fields (chat bodies, names), which are always
the **final** field of their record; the parser splits `n−1` pipes and takes the rest verbatim,
with only `\n` → `\\n` escaped. Empty optional fields are zero-width (`||`).

Worked size example — one `shards` faucet record:

```json
{"timestamp_utc":"2026-07-24T12:00:12.048Z","channel":"ECONOMY","level":"INFO",
 "event_type":"log_shard_delta","session_id":"k3","user_id":"acct_9f2c",
 "character_id":"char_2","node":"world-01","payload":
 {"delta":45,"reason":"drop","ref":"mob_031","balance_after":1287}}
```
≈ 300 bytes as JSON. The same record on disk:

```
300|43212048|k3|45|d|mob_031|1287
```
33 bytes — a ~9× reduction before compression, and rotated files compress a further ~8–12×
(§6.3) because positional lines are highly repetitive. JSON is only ever materialized by the
decoder (§3.5).

### 3.3 The session dictionary — identity written once

At gateway bind (`70_integrations/ACCOUNTS_AUTH.md` §4.1/§4.2) the node assigns the connection a
short **`sid`** and writes one `log_session_open` record — the *only* place `user_id`,
`character_id`, and `ip_address` appear (§8). Every subsequent record on any channel carries only
the `sid`. This is simultaneously:

- the **size** win — 2–3 bytes instead of ~40 bytes of identity per line;
- the **packet** win — internal emitters ship lines that never contain identity (§7);
- the **privacy** win — IP and account identity live in exactly one restricted place (§8).

`sid` ordinals reset per node per UTC day (the file-header date scopes them), so the
`(date, node, sid)` triple is globally unique. The daily `sessions.idx` manifest (§6.4) is the
decoder's join table.

### 3.4 Dictionaries for enum fields

Single-character codes for the highest-frequency enums; each dictionary's *semantics* stay with
the owning doc — this table only fixes the byte:

| Dictionary | Codes | Owner of the token set |
|---|---|---|
| Chat channel | `0`=`normal` `1`=`party` `2`=`guild` `3`=`whisper` `4`=`world` (provisional, pending promotion — `70_integrations/CHAT_SOCIAL_BACKEND.md` §1) | `10_systems/social/CHAT.md` |
| `shards` faucet reason | `d`=drop `q`=quest `v`=vendor_sell | `10_systems/ECONOMY.md` §1 |
| `shards` sink reason | `c`=consumable `e`=enhance_fee `r`=stat_realloc `g`=guild_create `m`=market_fee `f`=coach_fare `y`=ferry_fare `l`=longship_fare | `10_systems/ECONOMY.md` §2 |
| Item grant source | `d`=drop_pickup `q`=quest `v`=vendor `t`=trade_in `m`=market `p`=mail `a`=auto_route | `10_systems/DROPS.md` §7, `10_systems/INVENTORY.md` |
| Item removal reason | `c`=consume `v`=vendor_sell `t`=trade_out `m`=market_listed `p`=mail_attached `x`=destroyed | `10_systems/INVENTORY.md` |
| Death cause kind | `m`=mob (followed by `mob_NNN`) `e`=environmental | `10_systems/DEATH_PENALTY.md` |

A dictionary is **append-only**: codes are immutable once minted; a retired meaning keeps its
letter reserved. New codes are added here in a new commit, mirror-imaging the opcode-mint rule
(`docs/ID_REGISTRY.md`).

### 3.5 Event-code registry

Codes are minted **only** in this doc's §4 tables and are **immutable**; gaps are reserved; a new
event takes the next free slot in its block in a new commit — never a renumber
(`docs/ID_REGISTRY.md` law; the registry block reservation for this family is
`docs/ID_REGISTRY.md` "Log event codes"). Block layout:

| Block | Channel |
|---|---|
| `010`–`099` | Session/context records (written to `SECURITY_ALERTS` and `PLAYER_PROGRESSION`, §4.5/§4.1) |
| `100`–`199` | `CHAT` |
| `200`–`299` | `PLAYER_PROGRESSION` |
| `300`–`399` | `ECONOMY` |
| `400`–`499` | `COMBAT` |
| `500`–`599` | `SECURITY_ALERTS` |

### 3.6 Decoder projection

A coding-pass tool (proposed `tools/logcat.py`, beside `tools/validate.py`) projects any line — or
a grep result — to the §2 canonical JSON, resolving `sid` via `sessions.idx`, `ts` via the file
header, codes via §4, and `map_id` via the session's `log_map_enter` timeline. Manual review is
expected to work mostly on the raw lines (they are deliberately grep-friendly, §6.5); the JSON
projection exists for tooling and for exporting evidence.

## 4. Tracked events & payloads (the registry)

Format per row: **code · `event_type` · level — positional payload fields** (which are also the
JSON payload key names, in order). Behavior cited is owned elsewhere; a row only records it.

### 4.0 Session & context — codes 010–019

| Code | `event_type` | Level | Payload fields (positional) |
|---|---|---|---|
| `010` | `log_session_open` | INFO | `user_id`, `character_id`, `ip_address`, `client_version`, `channel_index` — the §3.3 dictionary record; written to `SECURITY_ALERTS` |
| `011` | `log_session_close` | INFO | `reason` (`quit`/`idle_timeout`/`kicked_duplicate_login`/`grace_expired`/`server_shutdown` — `70_integrations/NETWORK_PROTOCOL.md` §9.1, `70_integrations/ACCOUNTS_AUTH.md` §4), `duration_s` — `SECURITY_ALERTS` |
| `012` | `log_map_enter` | INFO | `map_id`, `channel_index`, `via` (`portal`/`coach`/`respawn`/`login`/`channel_switch`/`raid`) — written to `PLAYER_PROGRESSION`; the decoder's map-context source (§2.1) |

### 4.1 `CHAT` — codes 100–199

| Code | `event_type` | Level | Payload fields |
|---|---|---|---|
| `100` | `log_chat_message` | INFO | `chat_channel` (§3.4 dict), `recipient_sid` (whisper only, else empty; cross-node whisper falls back to `character_id`), `msg_ord` (per-session message counter — with `sid` it forms the stable message reference for reports), `body` (verbatim, final field) |
| `101` | `log_chat_filter_trigger` | WARN | `chat_channel`, `rule_id` (opaque live-ops wordlist rule ref — the wordlist itself is deliberately not in this tree, `70_integrations/CHAT_SOCIAL_BACKEND.md` §2), `action` (`blocked`/`masked`/`flag_only`), `body` |
| `102` | `log_chat_throttle` | WARN | `chat_channel`, `hits_in_window` — a soft-throttle rate-limit hit (`70_integrations/CHAT_SOCIAL_BACKEND.md` §2 limits; this row is the durable trace of the cache-side counter) |
| `103` | `log_chat_report` | INFO | `reporter_sid`, `reported_sid`, `msg_ord` (of the reported message), `reason_code` — the report-flow record (`70_integrations/CHAT_SOCIAL_BACKEND.md` §2.3) |
| `104` | `log_chat_mute` | WARN | `target_sid`, `scope` (chat-channel dict code or `*` for cross-channel), `source` (`auto`/`gm`), `duration_s` |

Chat bodies are logged **verbatim** (a GM must review what was said, not a paraphrase — same
stance as the report flow) and are the main reason `CHAT` gets the shortest retention (§6.3).
Whisper bodies are included; whisper *routing* metadata never leaves this channel.

### 4.2 `PLAYER_PROGRESSION` — codes 200–299

Per-kill `exp` records would dominate total log volume (LEVELING §4 models ~480 kills/hour/
character), so kill-grain `exp` is **aggregated per minute** — the ~8-kills-per-line summary keeps
rate-over-time analysis (§5 R-1) fully possible at ~1/8 the rows.

| Code | `event_type` | Level | Payload fields |
|---|---|---|---|
| `200` | `log_exp_summary` | INFO | `exp_hunt`, `exp_quest`, `exp_other`, `kill_count`, `level`, `exp_into_level` (end-of-window snapshot) — one line per character per minute *in which any `exp` moved* |
| `201` | `log_level_up` | INFO | `new_level`, `s_since_last_level` (precomputed so a reviewer greps rate anomalies without a join), `map_id` |
| `202` | `log_job_advance` | INFO | `job_line` (GLOSSARY token), `tier` (`1`/`2`) |
| `203` | `log_quest_complete` | INFO | `quest_id`, `exp_reward`, `shards_reward` (the wallet movement itself is the `ECONOMY` `300` record — this row is the progression fact) |
| `204` | `log_stat_alloc` | INFO | `might`, `finesse`, `focus`, `fortune` (points allocated this action), `respec` (`0`/`1`) |

### 4.3 `ECONOMY` — codes 300–399

The forensics backbone. Two invariants make duplication detectable from this channel alone:
every wallet movement carries `balance_after`, and every non-stackable item movement carries its
`item_uid` (§2.3) — so both value families form per-character chains a §5 detector can walk.

| Code | `event_type` | Level | Payload fields |
|---|---|---|---|
| `300` | `log_shard_delta` | INFO | `delta` (signed), `reason` (§3.4 faucet/sink dict), `ref` (contextual id: `mob_NNN`, `quest_NNN`, `item_id`, `trade_id`, listing id, …), `balance_after` |
| `301` | `log_item_grant` | INFO | `item_uid` (empty for stackables), `item_id`, `qty`, `rarity` (equip pool instantiations only, `10_systems/DROPS.md` §5.5), `source` (§3.4 dict), `source_ref` (`mob_NNN` / `drop_instance_id` / `quest_NNN` / `trade_id` / …) |
| `302` | `log_item_remove` | INFO | `item_uid`, `item_id`, `qty`, `reason` (§3.4 dict), `ref` |
| `303` | `log_trade_commit` | INFO | `trade_id` (server-minted per escrow session, `10_systems/social/TRADING.md`), `counterpart_sid`, `items_out` (`item_uid:qty` comma list), `shards_out`, `items_in`, `shards_in` — one line, written from the perspective of the lower `sid`; the escrow swap itself is one Postgres transaction (`70_integrations/DATABASE_PERSISTENCE.md` §4), this row is its audit shadow |
| `304` | `log_market_list` | INFO | `listing_id`, `item_uid`, `item_id`, `qty`, `ask_shards` |
| `305` | `log_market_buy` | INFO | `listing_id`, `seller_character_id`, `price_shards`, `fee_shards` (fee row: `10_systems/ECONOMY.md` §2) |
| `306` | `log_mail_send` | INFO | `mail_id`, `recipient_character_id`, `attached_items` (`item_uid:qty` list), `attached_shards`, `cod_shards` |
| `307` | `log_enhance_attempt` | INFO | `item_uid`, `target_plus`, `success` (`0`/`1`), `fee_shards`, `soft_pity_stacks`, `hard_pity` (`0`/`1`) — outcome already rolled by `70_integrations/GAMEPLAY_SIMULATION.md` §10; roll internals stay in the RNG audit log |

### 4.4 `COMBAT` — codes 400–499

Per-hit rows at INFO would be the single largest write source in the system (multiple hits/second/
character), for near-zero forensic value per row — so combat is **summarized per minute** at INFO
and per-hit only at DEBUG (investigation tap, §1).

| Code | `event_type` | Level | Payload fields |
|---|---|---|---|
| `400` | `log_combat_summary` | INFO | `hits`, `max_hit`, `total_damage_dealt`, `total_damage_taken`, `kills`, `essence_spent` — per character per active-combat minute; `max_hit` is what §5 R-6 checks against plausible damage bounds |
| `401` | `log_death` | INFO | `cause_kind` (§3.4 dict), `cause_ref` (`mob_NNN` or empty), `map_id`, `exp_lost` (already computed per `10_systems/DEATH_PENALTY.md` §2) |
| `402` | `log_boss_kill` | INFO | `mob_id`, `map_id`, `party_size`, `fight_duration_s` |
| `403` | `log_hit_debug` | DEBUG | `skill_id`, `target_entity_id`, `damage`, `is_crit`, `outcome` (`hit`/`miss`/`immune`) — mirrors the `op_0590` result shape (`70_integrations/NETWORK_PROTOCOL.md` §9.6) without re-deriving it |
| `404` | `log_action_reject_summary` | INFO | `skill_rejects` (`reason:count` comma list over `not_learned`/`on_cooldown`/`insufficient_essence`/`prereq_unmet`/`out_of_range` — the `op_0690` reject enum), `inventory_rejects` (same shape over the `op_0892` enum) — per character per minute in which any request was rejected; the raw material for §5 R-5 |

### 4.5 `SECURITY_ALERTS` — codes 500–599

Factual validation outcomes (500–506), detector flags (507–519, produced by the §5 rules), and
the GM audit trail (520). Every flag row names the `rule_id` it fired under, so the §5 table is
the single legend for the whole block.

| Code | `event_type` | Level | Payload fields |
|---|---|---|---|
| `500` | `log_move_hard_snap` | WARN | `claimed_x`, `claimed_y`, `server_x`, `server_y`, `delta_px`, `speed_cap_px_s` — one row per gross-divergence hard snap (`70_integrations/GAMEPLAY_SIMULATION.md` §2); the envelope math itself is that doc's, this row only records the miss |
| `501` | `log_move_reject_summary` | INFO | `rejects`, `max_delta_px`, `window_s` — per character per minute containing any rejection (soft-correct-scale misses; the common case writes nothing) |
| `502` | `log_speed_flag` | WARN | `rule_id`, `observed_ratio` (sustained displacement ÷ speed-cap displacement), `window_s` |
| `503` | `log_cooldown_flag` | WARN | `rule_id`, `skill_id`, `violations_in_window`, `window_s` |
| `504` | `log_rate_limit_breach` | WARN | `domain` (`chat`/`packet`/`login`), `limit_ref` (which configured limit), `hits_in_window` |
| `505` | `log_malformed_packet` | WARN | `op` (`op_NNNN` or `unknown`), `error_class` (`bad_envelope`/`bad_payload`/`bad_state`), `count` (coalesced per minute per connection) |
| `506` | `log_replay_mismatch` | WARN | `op`, `seq` — an idempotency-dedup hit whose replayed payload did **not** match the original (`70_integrations/NETWORK_PROTOCOL.md` §8; an honest reconnect replays identical bytes) |
| `507` | `log_exp_rate_flag` | WARN | `rule_id`, `exp_per_min_observed`, `exp_per_min_ceiling`, `window_min` |
| `508` | `log_shard_flow_flag` | WARN | `rule_id`, `net_shards_per_min`, `ceiling`, `window_min` |
| `509` | `log_trade_velocity_flag` | WARN | `rule_id`, `trades_in_window`, `distinct_counterparts`, `net_value_in` |
| `510` | `log_dupe_item_uid` | CRITICAL | `item_uid`, `holder_a_character_id`, `holder_b_character_id`, `first_seen_ts` — the same non-stackable instance observed in two custodies (§2.3) |
| `511` | `log_wallet_discontinuity` | CRITICAL | `expected_balance`, `observed_balance`, `last_delta_ref` — a `300`-chain break: `balance_after` + next `delta` ≠ next `balance_after` |
| `512` | `log_auth_anomaly` | WARN | `user_id`, `ip_address`, `kind` (`fail_streak`/`lockout`/`new_ip_hop`/`concurrent_bind`), `detail` — sign-in throttle/lockout behavior itself is `70_integrations/ACCOUNTS_AUTH.md` §3's |
| `513` | `log_multi_session_ip` | INFO | `ip_session_count`, `sid_list` — many live sessions from one address; context row, not an accusation (shared households/cafés exist) |
| `514` | `log_enhance_streak_flag` | WARN | `rule_id`, `consecutive_successes`, `binomial_p` (precomputed tail probability under the base rates, `10_systems/ENHANCEMENT.md` §3) |
| `520` | `log_gm_audit` | INFO | `gm_account_id`, `action` (`mute`/`kick`/`freeze`/`unfreeze`/`item_adjust`/`shard_adjust`/`review_close`), `target_character_id`, `reason_text` (final field) — every GM/live-ops action lands here without exception; the watchers are themselves watched |

## 5. Cheater-detection rules — red flags & manual-review triggers

**Posture (fixed):** detectors **flag, humans act.** No §5 rule auto-bans, auto-rolls-back, or
auto-confiscates. The only automatic consequences in the system remain the ones owning docs
already define (movement snap-back `70_integrations/GAMEPLAY_SIMULATION.md` §2, chat auto-mute
`70_integrations/CHAT_SOCIAL_BACKEND.md` §2, sign-in lockout `70_integrations/ACCOUNTS_AUTH.md`
§3) — this doc adds observation, not punishment. The two CRITICAL invariant breaks additionally
support a GM-issued **account freeze** (`520` action; suspends the session, mutates nothing)
because an active duper is doing damage by the minute — freeze is containment pending review,
still a human's call in first pass.

All thresholds below are **first-pass numbers, live-ops-tunable configuration** (same stance as
the chat escalation ladder). Each rule states its signal, its threshold, and what a reviewer
should pull first.

| Rule | Signal (channel/code) | First-pass threshold | Flag emitted | Reviewer's first pull |
|---|---|---|---|---|
| **R-1 impossible `exp` rate** | `200` rolling rate | Sustained `exp`/min > **3×** the character's level-band ceiling implied by `10_systems/LEVELING.md` §1/§4's modeled pacing (≈480 kills/hour at full efficiency), for ≥ **10 min** | `507` | The session's `200` rows + `012` map timeline: is the character on maps whose monster levels can even pay that rate (`docs/WORLD_PLAN.md` gradient law)? |
| **R-2 teleport / speed** | `500` events; `501` density | Any **2** hard snaps in **5 min**, or sustained `observed_ratio` > **1.15** over **60 s** | `502` | `500` coordinates vs the map's foothold graph — a legal fall or `dash`/`leap` skill burst reads very differently from a straight-line wall crossing |
| **R-3 cooldown / action spam** | `404` reject counts | > **20** `on_cooldown` rejects for one `skill_id` in **60 s** (a human mashing peaks well below a macro), or any rejected-action rate > **5/s** sustained **10 s** | `503` | Whether rejects are interleaved with accepts at exactly the cooldown boundary — a timing bot signature |
| **R-4 `shards` flow spike** | `300` rolling net | Net faucet `shards`/min > **5×** the level-band model (`10_systems/ECONOMY.md` §5's income-vs-sink tables), or any single unexplained `balance_after` jump | `508` | The `ref` fields on the anomalous `300` rows, joined to the RNG audit log for the drops claimed |
| **R-5 trade funneling / RMT shape** | `303` graph | One character receiving net value from ≥ **5** distinct counterparts within **24 h** with nothing of comparable value returned; or ≥ **3** trades between the same pair inside **10 min** | `509` | Counterpart account ages + `513` IP overlap: fresh throwaway feeders funneling to one sink is the classic RMT/dupe-laundering shape |
| **R-6 implausible damage** | `400` `max_hit` | `max_hit` > the ceiling computable from the character's logged `level`/gear grants (`301`) under `10_systems/COMBAT_FORMULA.md` — any strict violation, no tolerance | `—` (direct review-queue insert; the value is either possible or it is not) | The `403` DEBUG tap turned on for the account's next session |
| **R-7 item duplication** | `301`/`302` custody chains | The same `item_uid` in two custodies with no connecting `302`→`301` transfer; or a `301` grant whose `source_ref` drop/roll has no RNG-audit counterpart | `510` CRITICAL | Freeze-eligible. Walk both custody chains to the fork; the RNG audit log arbitrates which mint was real |
| **R-8 wallet discontinuity** | `300` chain | Any break in a character's `balance_after` chain | `511` CRITICAL | Freeze-eligible. Missing-log-line vs actual mint is decided against the Postgres ledger — the ledger is truth, the log is the tripwire (§0 table) |
| **R-9 enhancement luck** | `307` streaks | ≥ **6** consecutive successes at `target_plus` ≥ **+4** (tail probability ≈ 2×10⁻⁴ under the base 25 % rate before pity, `10_systems/ENHANCEMENT.md` §3) | `514` | The RNG audit log for those attempts — seeded rolls make "lucky or forged" a lookup, not a debate (`70_integrations/BACKEND_ARCHITECTURE.md` §3) |
| **R-10 auth churn** | `512`/`513` | Lockout + success from a new address inside **1 h**; or one IP opening ≥ **4** fresh sessions in **10 min** | `512` | `70_integrations/ACCOUNTS_AUTH.md` §3's lockout history for the account; compromised-account vs bot-farm triage |
| **R-11 protocol abuse** | `505`/`506` | Any `506` payload-mismatch replay; or > **10** malformed packets/min from one connection | `—` (`505`/`506` are already WARN) | The `op` distribution: fuzzing scatters across opcodes, a targeted exploit hammers one |

**Review queue mechanics.** WARN flags enter a per-day review queue (newest CRITICAL first, then
by rule); a reviewer works from the flag row → `sid` → the session's raw lines, in the files —
which is why §6 optimizes for grep. Every disposition (cleared / actioned) is closed with a `520`
`review_close` row naming the flag it resolves, so the queue's state is itself reconstructible
from the log.

## 6. Storage, rotation & retention

### 6.1 Directory layout & naming

```
/var/log/rebillion/
  world-01/                        # one directory per node (gateway, world, social, instance)
    2026-07-24/                    # one directory per UTC day
      chat-2026-07-24.0.log        # <channel>-<date>.<seq>.log — active file
      chat-2026-07-24.0.log.zst    #   …compressed on rotation
      economy-2026-07-24.0.log.zst
      economy-2026-07-24.1.log     #   .1 = size-based rollover of the same day (§6.2)
      progression-2026-07-24.0.log
      combat-2026-07-24.0.log
      security-2026-07-24.0.log
      sessions.idx                 # sid → identity manifest (§6.4; restricted, §8)
      manifest.tsv                 # per-file line counts + code histogram (§6.4)
```

Lowercase channel short names in filenames (`chat`, `progression`, `economy`, `combat`,
`security`) — filenames sort and glob cleanly (`security-2026-07-*.log*` sweeps a month on one
node). Instance workers log through their host node's writer; the instance id appears in `012`
`via`=`raid` context rows, not in the path.

### 6.2 Rotation

- **Daily at 00:00 UTC** — the same boundary as the game-day reset (`10_systems/PERSISTENCE.md`
  §2.1) and the §3.2 `ts` offset anchor, so one file never spans two dates and a day's
  investigation is a closed set of files.
- **Size-based at 256 MB** (uncompressed) within a day — `.<seq>` increments; keeps any single
  file fast to grep and cheap to copy. Under the §3 encoding, ordinary days should not hit it
  outside `CHAT` and `ECONOMY` on peak nodes.
- On rotation the closed file is **zstd-compressed** (`.zst`, level ~7) and its `manifest.tsv`
  row is finalized. zstd because it decompresses fast enough that `zstdgrep` over a month of
  rotated files stays an interactive operation — chosen for the manual-analysis loop, not just
  the storage bill.
- The active (unrotated) file is always plain text — the on-call path never needs a decompressor
  for *today*.

### 6.3 Retention (first-pass; owner-priced, Open Questions)

| Channel | Retention | Rationale |
|---|---|---|
| `CHAT` | **30 days** | Shortest — carries verbatim player text (§4.1); long enough for report-driven review, short enough to bound the privacy surface |
| `COMBAT` | **14 days** | Highest volume, lowest forensic half-life; §5 flags derived from it live longer than the raw rows need to |
| `PLAYER_PROGRESSION` | **90 days** | One full balance/playtest wave (matches telemetry's proposed raw window) |
| `ECONOMY` | **13 months** | The audit shadow of the value ledger; dupe/RMT investigations routinely look months back, and a year+ covers any seasonal pattern |
| `SECURITY_ALERTS` | **180 days** | Flags + session identity records; long enough that a slow-burn investigation keeps its trail, and the bound on how long IP records live (§8) |

Expiry deletes whole day-directories per channel (the layout makes retention a `rm` of old dates,
not a scan). Aggregates derived before expiry (dashboards, closed review cases) survive their
source rows.

### 6.4 Manifests — keeping manual analysis fast

Two small per-day, per-node index files make "find the needle" not start with a full scan:

- **`sessions.idx`** — one line per `sid`: `sid|open_ts|close_ts|user_id|character_id|ip_address|
  client_version`. The decoder's join table and the *only* file besides the security log holding
  identity (§8). Written by the same writer that logs `010`/`011`.
- **`manifest.tsv`** — one row per log file: line count, byte sizes (raw/compressed), and a
  `code:count` histogram. A reviewer checking "any `510` anywhere this week?" greps five tiny
  manifests, not five compressed gigabytes; it also doubles as a volume dashboard source.

### 6.5 Grep contract

The format guarantees, and the coding pass must preserve: one event per line; code is always the
first field (`grep '^510|'` finds every dupe flag); `sid` is always the third (`grep '|k3|'`
narrows to a session within a day+node); free text only ever in the final field. These three
properties are the spec's definition of "manual log analysis stays fast."

## 7. Internal emission path — the line is the packet

The size optimization extends to the wire between server components, per the owner directive:

- A map/world/social process **encodes once** — it builds the §3 line bytes itself and ships
  exactly those bytes to its node's **log writer** (one writer process per node owns all file
  appends; no cross-process file contention). The writer prepends nothing and re-serializes
  nothing: the string that travels is the string that lands on disk. There is no intermediate
  JSON, ever, in the hot path.
- Emission is **asynchronous and non-blocking**: lines batch in the emitter (flush at 64 KB or
  1 s, whichever first) and travel as one internal message. A full buffer **drops
  `DEBUG`/`INFO` lines and counts them** (a `log_lines_dropped` counter surfacing through the
  ops-metrics channel — the APM concern `70_integrations/TELEMETRY_ANALYTICS.md`'s Open
  Questions already flags as unowned); `WARN`/`CRITICAL` lines are never load-shed.
- **Logging never blocks gameplay.** Same stance as telemetry's fire-and-forget rule
  (`70_integrations/TELEMETRY_ANALYTICS.md` §7), restated here as this doc's own law because the
  emitters differ: no tick, combat resolution, save, or packet handler ever awaits a log write.
  If the writer dies, its supervisor restarts it (`70_integrations/BACKEND_ARCHITECTURE.md` §2's
  supervision model); gameplay is unaffected, and the gap is visible as a `ts` discontinuity plus
  the drop counter — never as a player-facing stall. The *ledger* and the *RNG audit log* have
  the opposite stance (block the action if unwritable, `70_integrations/BACKEND_ARCHITECTURE.md`
  §8) precisely because they are truth and this log is observability; the two postures are
  complementary, not in conflict.
- **`CRITICAL` fan-out:** `510`/`511` (and any future CRITICAL code) are written normally *and*
  pushed to a small alert stream the on-call/GM tooling subscribes to. The file is the record;
  the stream is the pager.
- Cross-node shipping to any central store is an ops choice layered on the per-node files
  (rsync/object-store upload of rotated `.zst` files is sufficient at this game's scale); nothing
  in this spec requires a live central aggregator (Open Questions).

## 8. Identity, IP & privacy boundaries

This log is an identity-bearing security record — the deliberate opposite of the PII-free
telemetry stream — and that power is caged structurally:

- **IP addresses appear in exactly three places:** `010` session-open rows, `512` auth-anomaly
  rows (both `SECURITY_ALERTS`), and `sessions.idx`. No other channel, code, or manifest may
  carry one — a payload adding an `ip_address` field elsewhere fails design review against this
  section. All three live under the `SECURITY_ALERTS` retention bound (§6.3, 180 days).
- **Access is tiered:** `CHAT`/`PLAYER_PROGRESSION`/`ECONOMY`/`COMBAT` files are readable by the
  live-ops/balance group; `SECURITY_ALERTS` files and `sessions.idx` are restricted to the
  GM/security group (concrete mechanism is ops-side, not designed here). The `520` GM-audit trail
  means access to the powerful channel is itself logged.
- **Account deletion** (`70_integrations/ACCOUNTS_AUTH.md` §6) must reach this store: on the
  unified delete signal, the account's `sessions.idx` rows and `010`/`512` rows are purged or
  irreversibly anonymized ahead of natural expiry; `ECONOMY` rows survive anonymized (the
  counterpart of a trade keeps their audit trail) — the log keeps the *transaction*, not the
  deleted party's identity. This doc joins the ACCOUNTS_AUTH↔TELEMETRY two-party delete-signal
  convergence as a third subscriber (Open Questions there and here).
- **No payment or real-world identity ever:** nothing in §4 carries email, real name, or
  payment data — `user_id` is the opaque `acct_*` id, and `70_integrations/ACCOUNTS_AUTH.md` §6's
  minimal-PII stance bounds what could even be joined to it.

## Open Questions

- **Retention windows (§6.3) are owner-priced.** The per-channel first-pass numbers set the
  *shape* (chat shortest, economy longest); actual durations and the storage tier for aged
  `.zst` files carry a real cost and stay the owner's call, alongside the RNG-audit retention
  flagged in `70_integrations/BACKEND_ARCHITECTURE.md`.
- **Whether `item_uid` is persisted in the live inventory schema** or derivable only from the
  log chain is `70_integrations/DATABASE_PERSISTENCE.md`'s to decide (§2.3 flags it). Persisting
  it makes R-7 a DB constraint as well as a log tripwire — strictly stronger, small schema cost.
- **Verbatim chat-body logging (§4.1) vs filter/report-only capture** trades investigation power
  against privacy surface and `CHAT` volume. Default here is verbatim with 30-day retention;
  revisit with the owner before launch.
- **Central aggregation** (§7) — per-node files with rotated-file upload is the launch stance;
  whether a live central store (and which) is ever warranted is deferred until real ops load
  exists, not designed here.
- **Detector placement** — whether §5 rules run inside the writer, as a per-node sidecar tailing
  the day's files, or as a periodic batch over rotated files is a coding-pass call; the rules are
  written to be computable from the log alone so all three placements work.
- **The unified delete signal** (§8) is now three-party (ACCOUNTS_AUTH, TELEMETRY_ANALYTICS,
  this doc); the converged design still lives in `70_integrations/ACCOUNTS_AUTH.md`'s Open
  Questions, this doc only registers as a subscriber.
- **`world` chat-channel promotion** — the §3.4 chat dictionary reserves code `4` for the
  provisional `world` channel; if `10_systems/social/CHAT.md` declines the promotion, the code
  stays reserved-dead per the append-only dictionary rule, never reused.
- **Threshold governance** — §5 numbers are live-ops-tunable; where the tuned values live
  (config repo vs ops console) and who signs off a change is a live-ops process question,
  matching the chat-escalation and lockout precedents.
