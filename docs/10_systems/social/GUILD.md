# GUILD.md — Guilds: Creation, Ranks, Roster & Crest

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/JOBS.md,
10_systems/ECONOMY.md, 10_systems/HUD.md, 10_systems/CONTROLS.md, 10_systems/social/CHAT.md,
10_systems/social/PARTY.md, 40_assets/ART_BIBLE.yaml, 40_assets/UI_ART_SPEC.md,
20_schemas/guild.schema.md, 10_systems/PERSISTENCE.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the **guild**: creation, name rules, the three-rank permission model, roster cap
growth, and the crest **data** contract. The crest's rendering, symbol art, and palette are
`40_assets/UI_ART_SPEC.md`'s; `shards` fee amounts default to `10_systems/ECONOMY.md`'s sink
budget except where that doc explicitly reserves the number here (§1). Guild chat is a channel
hook into `10_systems/social/CHAT.md`, not redefined here. **Launch scope is roster, chat, crest,
and MOTD only** — no guild bank, no guild quests (§8).

## 1. Creation

- **Requirement: founder `level` ≥ 40** — the 2nd job advancement (`10_systems/JOBS.md` §1), a
  meaningful but not endgame milestone.
- **Fee: 100,000 `shards`**, paid by the founder alone (no guild bank exists to split it, §8).
  This adopts `10_systems/ECONOMY.md` §6's placeholder as authoritative — that doc reserves the
  exact number to this one.
- Creation happens at the **guild hall** interior in Millbrook Central's interior block
  (`map_019`–`026`, `docs/WORLD_PLAN.md` R2; the exact interior ID is a Phase D allocation, Open
  Questions) — the only guild hall in the world, matching Millbrook's role as the social heart
  (`00_vision/PILLARS.md` P3). The panel is toggled with `G`
  (`10_systems/CONTROLS.md` §1) and rendered in `frame_window` (`10_systems/HUD.md` §1), both
  already reserved for Guild by those docs.
- One guild membership per character. The fee is only charged once the chosen name (§2) is
  confirmed available.
- The founder becomes the sole **leader** (§3); no minimum founding roster beyond the founder.

## 2. Name rules

3–16 characters, letters/spaces/a single apostrophe, no leading/trailing space, globally unique
across every guild (server-enforced at creation time). Profanity/reserved-word filtering is a
live-ops policy applied server-side, not designed here (Open Questions).

## 3. Ranks & permissions

Three fixed permission tiers; **custom labels** let the leader rename each tier's *display* string
(≤16 characters) without changing what it can do:

| Rank | Count | Invite | Kick member | Kick officer | Edit MOTD | Edit crest | Promote/demote | Disband |
|---|---|---|---|---|---|---|---|---|
| `leader` | 1 | yes | yes | yes | yes | yes | yes | yes |
| `officer` | 0–5 | yes | yes | no | yes | no | no | no |
| `member` | remaining roster | no | no | no | no | no | no | no |

Leadership transfer is leader-initiated only (no auto-succession like
`10_systems/social/PARTY.md` §2 — a guild persists whether or not its leader is online).

## 4. Roster cap & growth

Base cap **20**. The leader may purchase **+10** per step at the guild hall (§1), up to
**4 purchases** (cap **60**), paid personally (§8 — no guild bank). The `shards` cost per step is
reserved to `10_systems/ECONOMY.md`, mirroring how that doc reserves the creation fee here (§1);
not fixed in this doc (Open Questions).

## 5. Crest

A guild crest is **composable data**, not authored art: `{ shape, symbol, primary, accent }`.

```yaml
crest:
  shape: banner        # heater | round | banner | diamond | crest_ornate  (5)
  symbol: sym_014       # 1 of 24; id list and art owned by 40_assets/UI_ART_SPEC.md
  primary: palette_03   # color slot; palette owner TBD (Open Questions)
  accent: palette_11
```

- **Rendered sizes**: 12/24/32/64 px — `40_assets/UI_ART_SPEC.md`'s to define per-context (chat
  icon, roster row, guild panel, profile); this doc only requires all four remain legible.
- **Uniqueness — decision: not required.** Only the guild name (§2) is globally unique; the
  5 × 24 × palette² combination space is large enough that visual collision is a social matter,
  not a fairness one (`00_vision/PILLARS.md` P4 — crests are data, not a scarce allocator).
- **Edit — leader only.** Costs a flat **5,000 `shards`** and is throttled to **once per 7 days**
  per guild (server-tracked). Both numbers are this doc's first-pass proposal; the `shards`
  magnitude is still `10_systems/ECONOMY.md`'s sink budget to confirm (Open Questions).
- The guild record (roster/ranks/crest/MOTD fields) has no schema doc yet; proposed as
  `20_schemas/guild.schema.md` at Phase C (Open Questions).

## 6. MOTD

One guild-wide text field, ≤200 characters, editable by `leader`/`officer` (§3), shown wherever
`10_systems/HUD.md` surfaces the guild panel or roster.

## 7. Guild chat

Membership in a guild grants access to the `guild` channel of `10_systems/social/CHAT.md` — the
channel's behavior (bubbles, log, whisper) is entirely that doc's; this doc only supplies the
roster that defines who is in the channel.

## 8. Launch scope

Roster, chat, crest, and MOTD only. **No guild bank and no guild quests at launch** — both are
flagged future additions (Open Questions), not designed in this pass. This is also why every fee
in this doc (§1, §4, §5) is paid by an individual member, never a shared guild purse.

## Server Dependency

Global name uniqueness, roster membership, rank assignments, the crest, and the MOTD are all
`authority: server` (`10_systems/PERSISTENCE.md` §1–§2, which already lists guild state in its own
authority table) — shared state no single client may hold as truth (`00_vision/PILLARS.md` P6).
**The interim solo build ships guild creation/roster/crest/chat UI present but dormant**: a solo
character has no one else to recruit, so no guild ever meaningfully forms.

## Open Questions

- Which Millbrook Central interior (`map_019`–`026`, §1) is the guild hall is a Phase D map
  allocation — `docs/WORLD_PLAN.md` R2 lists a guild hall among the interiors; pin the exact
  `map_NNN` when the R2 map batch is authored.
- Roster-expansion (§4) and crest-edit (§5) `shards` amounts are this doc's first-pass proposals;
  `10_systems/ECONOMY.md` needs to fold them into its sink budget (its own Open Questions already
  flags this exact reconciliation for the `social/` docs' fee stubs).
- Guild records have no ID scheme in `docs/ID_REGISTRY.md` (guilds are runtime player-created data,
  not Phase D authored content) — proposes server-assigned `guild_<NNNNNN>` IDs; needs
  `10_systems/PERSISTENCE.md` to confirm the format.
- No schema doc yet exists for the guild record; proposes `20_schemas/guild.schema.md` at Phase C.
- The crest shape enum (`heater`/`round`/`banner`/`diamond`/`crest_ornate`, §5) is new vocabulary
  not yet in `00_vision/GLOSSARY.md` — propose promoting it to GLOSSARY Provisional at the B/C
  gate, alongside the 24-symbol list owned by `40_assets/UI_ART_SPEC.md`.
- Which 40_assets doc owns the crest color palette (`40_assets/ART_BIBLE.yaml` vs
  `40_assets/UI_ART_SPEC.md`) is undecided.
- Officer cap (5, §3) and the roster growth steps (§4) are first-pass; may need retuning once
  post-launch guild-activity data exists.
- Guild-hop cooldown: none at launch (§1) since there is no bank/reward to farm by hopping (§8);
  revisit if that changes.
- Guild bank and guild quests (§8) are deferred future features, not designed here.
