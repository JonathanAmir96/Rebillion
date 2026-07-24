# techContext.md — Stack, Protocols, Schemas, Constraints

> Memory Bank file 3/5. Every decision below is gated canon from the Phase I backend
> suite (`docs/70_integrations/`) unless marked open. Numbers are load-bearing — cite
> the owning doc before changing any of them.

## Tech stack (decided)

| Layer | Decision | Owning doc |
|---|---|---|
| Client engine | Godot 4.3+, statically-typed GDScript, 60 Hz physics, `WebSocketPeer` + TLS | ENGINEERING_STANDARDS, BACKEND_ARCHITECTURE §2 |
| Server | **Elixir/OTP on the BEAM**, engine-independent (no headless Godot); Phoenix for sockets/presence/channels | BACKEND_ARCHITECTURE §2 |
| Hot paths | Rust NIF/port escape hatch (coding-pass optimization only) | BACKEND_ARCHITECTURE §2 |
| Transactional DB | **PostgreSQL via Supabase (managed)** — one database, schemas `char`/`wallet`/`social`, least-privilege role each; vendor owner-ratified 2026-07-24 | DATABASE_PERSISTENCE §2 |
| Audit store | Append-only log store, **off Postgres** (RNG/drop/combat records) | DATABASE_PERSISTENCE §3.4 |
| Cache | Redis (cross-node) + ETS/Phoenix.Presence (in-node); never source of truth | BACKEND_ARCHITECTURE §3 |
| Transport | Single persistent **WSS** (port 443), fail-closed TLS, no plaintext | NETWORK_PROTOCOL §1 |
| Serialization | **MessagePack** both directions; per-message DEFLATE above ~512 B | NETWORK_PROTOCOL §2, §5 |
| Passwords | **Argon2id** (m≥19 MiB, t≥2, p≥1; ~250–500 ms tuned) | ACCOUNTS_AUTH §3.2 |
| Sessions | Opaque ≥256-bit server-stored tokens, 60 min + 30-day rotating refresh; JWTs rejected | ACCOUNTS_AUTH §3.4 |
| Build/distribution | CI Godot export, YAML→.tres at build, storefront-native delta patching | BUILD_DISTRIBUTION §1–§3 |

Rejected (do not relitigate without owner amendment): headless-Godot server, Go,
Node/Colyseus-style room layer, separate databases + 2PC, Mongo/Dynamo, CockroachDB,
raw TCP/UDP, QUIC (reserved), Protobuf/CBOR, JWTs. **Owner-ratified 2026-07-24:
Supabase is the managed-Postgres vendor** (database tier only; Colyseus remains
illustrative). The Elixir/OTP + Phoenix decision stands — rationale includes the
autonomous-maintenance end-state (OTP crash reports as agent triggers,
`docs/60_agents/AUTONOMOUS_MAINTENANCE.md`).

## Networking protocol (`NETWORK_PROTOCOL.md`)

- Envelope: MessagePack array `[op, seq, ack, t, flags, payload]` (~10–14 B).
  `op` uint16 dispatch key; `seq` per-connection monotonic (idempotency dedup on
  `(session, seq)` — mutating replays fail closed); `flags` bit0 COMPRESSED,
  bit1 RESUMED.
- Opcodes: `op_0001`–`op_9999` reserved in `docs/ID_REGISTRY.md`; **13 domain blocks,
  103 minted** (§9): system 0001–0099, auth 0100–0199, channel/instance 0200–0299,
  movement 0300–0399, snapshot 0400–0499, combat 0500–0599, skill 0600–0699, loot
  0700–0799, inventory 0800–0899, shards/enhance 0900–0999, quest 1000–1099, chat
  1100–1199, party/social 1200–1299. Immutable, never reused.
- Cadence: client→server movement 20 Hz; server snapshot `op_0400` 10 Hz,
  whole-visible-state per broadcast (delta/interest-filtering = open flag S4/P2);
  results/events pushed immediately.
- Liveness: heartbeat 15 s → socket-dead 30 s → session grace 90 s (resume via
  HMAC-signed ticket, `op_0002`); invariant 30 < 90.
- Versioning: `protocol_version` handshake (`op_0100 client_hello`) before auth;
  below-floor = hard reject to storefront update. `content_version` never gates wire.
- Rate limits at gateway: chat 5–15/10 s by channel; login 5 fails/15 min →
  doubling lockout; account creation 5/hr/source.

## Database schemas (`DATABASE_PERSISTENCE.md` §3 — design granularity)

- `char`: `character` (server-minted PK, unique name, job_line, bind point,
  save_version) · `character_progress` (level, exp) · `character_stats` (**free-point
  inputs only — derived stats are never stored**, recomputed on load) ·
  `inventory_slot` (composite PK character+container+tab+slot) · `item_instance`
  (enhance_level 0–9, soft-pity count, immutable rolled_affixes jsonb) ·
  `equipment_worn` · `quest_state` · `skill_rank` · `session_snapshot`
  (life/essence/cooldowns/status — checkpoint only).
- `wallet`: `wallet` (bigint balance, cap 2,000,000,000) + append-only
  `wallet_ledger` (signed delta, balance_after, reason enum); over-cap credit rejected
  pre-commit.
- `social`: `guild`, `guild_member`, `market_listing`, `mail`, append-only `trade_log`.
- Transaction rules (§4 + owner law 2026-07-24): every mutating op = one ACID
  transaction or refused whole; explicit `SELECT … FOR UPDATE` row locks in
  deterministic lock order on every multi-row swap (pattern: `systemPatterns.md`);
  audit-before-commit ordering; two-party trade commits across all three schemas or not
  at all; enhancement consumes stone+fee on success *and* failure.
- Runtime keys vs authored IDs: authored content (`item_*`, `mob_*`, `map_*`, …) ships
  with the build and is **not in the runtime DB**; player-created rows use server-minted
  surrogate keys outside authored ID ranges.
- Deliberately not persisted: position/velocity, derived stats, party roster, live
  trade escrow, chat history, in-flight cooldowns (snapshot only).
- Write cadence (§5): value/milestone moves synchronous; life/exp-into-level/timers
  checkpoint every 60 s + map transition + clean quit. Migrations: forward-only,
  additive-by-default, `save_version` per row, unknown field = reject.

## Framework dependencies & content pipeline

- Content: YAML in `docs/50_content/` on the `docs/20_schemas/*.schema.md` shapes →
  build-time conversion to Godot `.tres` Resources (never parsed at runtime).
- Validator: `python3 tools/validate.py` (stdlib-only; PyYAML optional) enforces
  VALIDATION checks 1–6; CI-blocking. `tools/md_graph.py` audits doc connectivity.
- Client autoloads: EventBus, GameState (save facade + authority tags), Database,
  SceneManager. Testing: GUT (client) + ExUnit (server) sharing language-neutral
  `CombatMath`/drop/enhancement fixture vectors (GAMEPLAY_SIMULATION §3).
- Art pass: PixelLab MCP tools; API token is **not in the repo** (env secret, e.g.
  `PIXELLAB_SECRET`); every generation batch pairs with `get_balance` via
  ART_QUARTERMASTER.

## Runtime constraints (load-bearing numbers)

- Sim 20 Hz / snapshot 10 Hz / client physics 60 Hz; per-map 50 ms self-rescheduled
  timers; parked when empty; combat queue drained once per tick (≤50 ms added latency).
- Movement: `base_move_speed` 128 px/s (8 tiles/s, 16 px grid); reconciliation
  envelope ±½ tile + speed-cap displacement margin.
- Capacity (launch targets, sized pre-v3 — re-check at balance pass): channel caps 5
  per map, 150 town / 60 field occupancy, ~2,000 players/node.
- Daily reset 00:00 UTC, weekly Monday 00:00 UTC. Character slots: 3.
- Authored-content ceiling: import/validation clamps re-derived level at the **hard
  Lv 80 world cap** (owner-ratified 2026-07-24; `ACCOUNTS_AUTH.md` §2.4 patch queued —
  doc still reads 82/300; the Lv 81–82 elite-overshoot fate is an open ruling).
- Telemetry: pseudonymous player_id, no PII, fire-and-forget, 90-day proposed
  retention; **no APM/operational telemetry owner yet — filed gap P9.**

## Open Questions

- None owned here — open technical decisions are consolidated in `activeContext.md`;
  each resolves in its owning `70_integrations/` doc.
