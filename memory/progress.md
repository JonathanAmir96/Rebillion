# progress.md — Status Matrix & Milestones

> Memory Bank file 5/5. Status as of **2026-07-24, post md-audit** (branch
> `claude/md-audit-2026-07-24`, awaiting owner merge review). Validator
> state: `python3 tools/validate.py` strict → **0 failures / 0 warnings**.
> Legend: ✅ Fully Defined · 🟡 Partially Defined (usable, flagged gaps) · ⬜ Not Started.

## Design systems (`docs/10_systems/`, `15_maps_system/`)

| System | Status | Notes |
|---|---|---|
| Stats / Combat formula | ✅ | Monster budget load-bearing; move/attack cadence placeholders await tile-scale lock |
| Leveling / pacing | ✅ | Curve frozen ≤ Lv 100; quest `exp` content regenerated against it 2026-07-24 (`tools/regen_quest_exp.py`) |
| Jobs (novice→1st→2nd branching) | ✅ | 3rd tier named-and-reserved only (future arcs) |
| Skill system + effects | ✅ | Heal/shield scaling + summon-cap details flagged |
| Death penalty / Enhancement / Scrolls | ✅ / ✅ / 🟡 | Scrolls designed; content not minted (blocks reserved) |
| Drops / Economy / Items / Inventory | 🟡 | Complete rules; all numbers first-pass, retune at balance pass |
| Mob AI / Spawn / Status effects / Elements | ✅ | 12 profiles, boss phase contract, telegraph law |
| Maps system (footholds, traversal, layers, connections) | ✅ | AB-001 foothold model; minor `map_109` residue |
| Social suite (party/raid/guild/chat/mail/market/trading/party-finder) | ✅ (design) | **Server-deferred**; fees/limits jointly owed with ECONOMY |
| Combo system (`COMBO_SYSTEM.md`) | ✅ | Momentum/burst chaining; magnitudes to balance pass; HUD §7.1 counter |
| Appearance / entry / display (`CHARACTER_COMPOSITING.md`, `ACCOUNT.md`, `DISPLAY.md`) | ✅ | Paper-doll composite law (AB-002), 4-slot roster + check-name, 640x360 integer-scale fullscreen |
| Persistence boundary (authority tags) | ✅ | §4 resolved by delegation to GAMEPLAY_SIMULATION §2 |
| Monetization / Collections / Audio / FTUE / Lore / Camera / HUD / Controls | 🟡 | Designed; tile-scale-dependent values + deep hooks open |

## Backend design (`docs/70_integrations/`, Phase I — all landed & gated)

| Doc | Status | Notes |
|---|---|---|
| BACKEND_ARCHITECTURE | ✅ | Stack owner-confirmed; hosting/vendor owner-priced |
| GAMEPLAY_SIMULATION | ✅ | Tick/reconciliation/combat pipeline; tolerances want playtest |
| NETWORK_PROTOCOL | ✅ | 106 opcodes minted (103 + 2026-07-24 entry-flow trio); interest-filtering/delta OQ (flag S4/P2) |
| DATABASE_PERSISTENCE | ✅ | Row-lock + SQL discipline OQ (flag S6/S9); moderation table pending |
| ACCOUNTS_AUTH | ✅ | Import pipeline fully specified; vendor OQs |
| WORLD_CHANNELS | ✅ | Capacity targets sized pre-v3 — re-check at balance pass |
| CHAT_SOCIAL_BACKEND | ✅ | Rate ladders first-pass |
| TELEMETRY_ANALYTICS | 🟡 | Balance telemetry done; **APM/ops unowned (flag P9)** |
| BUILD_DISTRIBUTION | 🟡 | Pipeline designed; storefront/CI/signing/platform sign-off open |

## Content (`docs/50_content/` — Phase D complete, validator-clean)

| Type | Count | Type | Count |
|---|---|---|---|
| Maps | 324 | NPCs | 120 |
| Monsters | 234 (178N/45E/11B) | Quests | 120 (exp regenerated 2026-07-24) |
| Drop tables | 235 (+11 pools) | Skills | 98 (5 line files) |
| Items | T1–T12 ladder, uniques, consumables, raid gear | Schemas | 8, all authored |

Not minted (reserved blocks): shields/overalls `item_equip_0181`–`0200`, scrolls
`item_use_0061`–`0100`, Emberstone VI `item_etc_0198`, raid cosmetics/titles.

## Phases & milestones

| Phase | Scope | Status |
|---|---|---|
| A — Vision | Pillars, scope, glossary | ✅ 2026-07 |
| B — Systems | All system docs | ✅ |
| C — Schemas/assets | 8 schemas, spritesheet/animation specs | ✅ (gate resolutions logged) |
| D — Content | Full-world content, both arcs | ✅ strict-validated 0/0 |
| F/G/H — Integrations, equipment, consistency | Merged from parallel sessions | ✅ |
| I — Backend design suite | 70_integrations + opcode registry | ✅ 2026-07-23, audited 07-24 |
| Sync audits | v3.1 full-tree sync; MD connectivity (117/117 BFS-reachable); backend checklist; **repo-wide md audit** (`MD_AUDIT_REPORT_2026-07-24.md`) | ✅ |
| **Memory Bank** | `memory/` persistent context (this directory; linked from README/CLAUDE/memory.md since the md audit) | ✅ |
| **Quest-exp regen** | Mechanical regen vs retuned curve (`tools/regen_quest_exp.py`, 120/120, FTUE budget verified) | ✅ 2026-07-24 (md audit) |
| **E — Coding-pass briefs** | Implementation briefs + OQ rollup index | ⬜ |
| **Balance pass** | Economy/tonics/drops/capacity retune | ⬜ after E |
| **Art pass** | PixelLab generation per runbook (compositing spike gate first) | ⬜ unblocked — tile-scale + resolution laws locked |
| **Backend coding pass** | Elixir/OTP server, resolve flags S4/S6/S9/P9 | ⬜ after E |
| **Client coding pass** | Godot per ENGINEERING_STANDARDS | ⬜ after E |
| Live ops / autonomous maintenance | LIVE_OPS.md + agent repair loop wiring | ⬜ deferred to coding pass |

## What "done" means for the next milestones

- **Phase E:** per-feature briefs referencing (never restating) owning docs; VALIDATION
  §7 rollup built; each brief names its ORG.md tier route.
- **Balance pass:** first-pass numbers replaced with ratified ones in owning docs only;
  content untouched except regenerated values.

## Open Questions

- None owned here — see `activeContext.md` for the consolidated decision queue.
