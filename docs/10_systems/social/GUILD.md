# GUILD.md — Guilds: Creation, Ranks, Roster & Crest

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/JOBS.md,
10_systems/ECONOMY.md, 10_systems/HUD.md, 10_systems/CONTROLS.md, 10_systems/social/CHAT.md,
10_systems/social/PARTY.md, 10_systems/social/RAID.md, 10_systems/LEVELING.md,
10_systems/DROPS.md, 10_systems/MONETIZATION.md, 40_assets/ART_BIBLE.yaml,
40_assets/UI_ART_SPEC.md, 10_systems/PERSISTENCE.md, docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the **guild**: creation, name rules, the three-rank permission model, roster cap
growth, and the crest **data** contract. The crest's rendering, symbol art, and palette are
`40_assets/UI_ART_SPEC.md`'s; `shards` fee amounts default to `10_systems/ECONOMY.md`'s sink
budget except where that doc explicitly reserves the number here (§1). Guild chat is a channel
hook into `10_systems/social/CHAT.md`, not redefined here. The interim solo build's **live surfaces
are roster, chat, crest, and MOTD only**; the owner-directed social-package guild incentives —
`guild_contribution` & guild levels (§9), the grouping buff (§10), and the weekly guild goal
(§11) — are designed here but server-deferred and dormant in solo, and there is still no guild bank
(§8).

## 1. Creation

- **Requirement: founder `level` ≥ 40** — the 2nd job advancement (`10_systems/JOBS.md` §1), a
  meaningful but not endgame milestone.
- **Fee: 100,000 `shards`**, paid by the founder alone (no guild bank exists to split it, §8).
  This adopts `10_systems/ECONOMY.md` §6's placeholder as authoritative — that doc reserves the
  exact number to this one.
- Creation happens at the **guild hall** interior, Millbrook Central (`map_022`,
  `docs/WORLD_PLAN.md` R2) — the only guild hall in the world, matching Millbrook's role as the
  social heart (`00_vision/PILLARS.md` P3). The panel is toggled with `G`
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

Base cap **20**. The leader may purchase **+10** per step at the guild hall (`map_022`), up to
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
  a `guild.schema` doc (proposed, not yet in the §2 tree) at Phase C (Open Questions).

## 6. MOTD

One guild-wide text field, ≤200 characters, editable by `leader`/`officer` (§3), shown wherever
`10_systems/HUD.md` surfaces the guild panel or roster.

## 7. Guild chat

Membership in a guild grants access to the `guild` channel of `10_systems/social/CHAT.md` — the
channel's behavior (bubbles, log, whisper) is entirely that doc's; this doc only supplies the
roster that defines who is in the channel.

## 8. Launch scope

The interim solo build ships only **roster, chat, crest, and MOTD** as live surfaces (§Server
Dependency). The owner-directed social-package incentives — **`guild_contribution` & guild levels
(§9), the grouping buff (§10), and the weekly guild goal (§11)** — are designed here but, like all
guild state, server-deferred and dormant in that solo build (`memory.md`, 2026-07-24). They are the
"guild activity" layer this section previously deferred, now designed at the owner's direction;
they never gate content for solo or non-guild players (§9–§11, `00_vision/PILLARS.md` P2/P3).

**Still deferred: the guild bank (a shared guild purse) and a per-member guild-quest board** — both
remain flagged future additions (Open Questions), not designed in this pass. Because no purse
exists, every fee in this doc (§1, §4, §5) is paid by an individual member, and the §11 weekly-goal
`shards`-to-guild reward variant is contingent on the guild bank landing. The §11 weekly goal is a
guild-**wide** objective, not the per-member quest board, and is not blocked by that deferral.

## 9. Guild contribution & levels

`guild_contribution` (`00_vision/GLOSSARY.md`) is a **guild-owned** point total — earned by members'
grouped play, credited to the *guild*, never to the character — that drives a **guild level** and the
perks below. It is the owner-directed social package's guild carrot (`memory.md`, 2026-07-24): a
reason to log in *with* the guild, layered on the launch surfaces (§1–§7) and, like all guild state,
server-deferred (§Server Dependency).

**Earning (first-pass, flagged).** Contribution accrues from the two grouped activities the package
rewards, both consumed by reference — this doc mints no new play mechanic:

- **Raid clears** — each successful finale-boss clear (`10_systems/social/RAID.md` §5–§6) by a
  member grants the guild a first-pass contribution amount. Reuses RAID's existing clear event; no
  new raid state.
- **Same-map party-hunt milestones** — grouped hunting (`10_systems/social/PARTY.md` §4's same-map
  eligibility) accrues contribution in milestone batches (e.g., every **N** same-map party-eligible
  kills logs one milestone's worth). The milestone unit is keyed off `10_systems/social/PARTY.md`
  §4's eligibility; this doc only credits the guild when one lands. N and the per-event amounts are
  first-pass (Open Questions).

Contribution is **monotonic** — it accrues and never decays; a member leaving or being kicked does
not claw back what their play earned (`00_vision/PILLARS.md` P1, no hidden state) — and rolls into a
**guild level** at first-pass thresholds (flagged). Guild-level unlocks are **additive perks only**,
never anything that gates content for solo or non-guild players (P2/P3):

| Guild-level perk | What it grants | Ties into |
|---|---|---|
| Roster headroom | Unlocks **further** paid roster-growth steps above §4's launch ceiling of 60 (each still a `shards` purchase at the guild hall, `map_022`) — **extends** the §4 ladder, does not replace it | §4 |
| Crest / cosmetic options | Additional crest symbols and shapes (§5) and guild cosmetics drawn from the reserved `item_cosmetic_0009`–`0064` guild block (`docs/ID_REGISTRY.md`; cosmetic-only, carry no stats — `10_systems/MONETIZATION.md`, `00_vision/PILLARS.md` anti-pay-to-win) | §5 |
| Buff scale | May raise the §10 grouping-buff magnitude and/or the §11 weekly-goal reward tier at higher guild levels (flagged) | §10, §11 |

The roster-headroom perk **extends** §4 rather than contradicting it: §4's base **20** and its four
paid **+10** steps to **60** stand unchanged as the launch ladder; guild levels only unlock
additional steps above that, still paid per step (amounts reserved to `10_systems/ECONOMY.md`
exactly as §4's are). Whether a guild level should instead raise the ceiling directly (no purchase)
is flagged (Open Questions).

## 10. Guild grouping buff

When **2+ members of the same guild sit among the same-map eligible members of one party**
(`10_systems/social/PARTY.md` §4's same-map eligibility rule, consumed unchanged), a small guild
buff applies to those guildmates while they stay grouped together — first-pass **+5% `exp` and +5%
drop-chance**. It rewards guildmates *grouping together*, not merely sharing a guild tag: a lone
guild member, or two guildmates on different maps, gets nothing.

- **`exp` side.** The +5% is a **new `exp` source** that behaves exactly like the party exp bonus
  (`10_systems/social/PARTY.md` §4): an **elective accelerator sitting outside
  `10_systems/LEVELING.md` §4's mandatory 70/25/5 source split**, never touching the
  `10_systems/LEVELING.md` §1 curve — a grouped guild simply travels the same curve a little faster.
  Applied to the grouped pool, it stacks with the party exp bonus (which keys on party size, not
  guild). `10_systems/LEVELING.md` §4 owns the source-accounting; see Handoffs.
- **Drop side.** The +5% is a drop-chance multiplier that **composes with `fortune`'s `m`
  (`10_systems/DROPS.md` §4) and the same-map `party_drop_bonus` (`10_systems/DROPS.md`, keyed by
  `10_systems/social/PARTY.md` §4)**, and falls under `10_systems/DROPS.md` §4's `≤ 0.95` chance
  clamp exactly like those — grouping, a `fortune` build, and a full guild party compound, but none
  makes a drop certain. The exact composition order and any combined cap are `10_systems/DROPS.md`'s
  to own (reference, never restated); this doc supplies only the +5% factor and the "2+ same-guild,
  same-map" trigger. See Handoffs.

Magnitude (+5% / +5%), and whether it scales with guild level (§9), are first-pass and tunable
(Open Questions). Encourage-not-mandate: solo and non-guild players are never blocked from any
content by this — it is an additive carrot on grouped guild play (`00_vision/PILLARS.md` P2/P3).

## 11. Weekly guild goal

A **rotating weekly guild objective** — the guild's recurring coordination beat, the social
heartbeat that gives the roster a shared reason to log in each week. Each week the guild is set one
first-pass objective drawn from the same grouped activities §9 counts, for example:

- "Guild members clear **N** raids this week" (`10_systems/social/RAID.md` clears), or
- "Guild logs **N** same-map party-hunt milestones this week" (`10_systems/social/PARTY.md` §4).

Meeting the objective grants a **guild-wide reward**, first-pass one of: a **temporary guild-wide
buff** (a time-boxed lift to the §10 grouping buff or a small flat party lift), a **cosmetic
unlock** (a guild cosmetic from the `item_cosmetic_0009`–`0064` block, `docs/ID_REGISTRY.md` — no
stats, `00_vision/PILLARS.md` anti-pay-to-win), or **`shards` to the guild** — the last of which
requires the guild purse deferred by §8 and is therefore contingent on that feature landing (Open
Questions). Default reward at this pass is the temporary buff or the cosmetic unlock, neither of
which needs a purse.

- **Week boundary.** The week rolls on a fixed weekday anchored to `10_systems/PERSISTENCE.md`'s
  **day boundary** — the same boundary `10_systems/social/RAID.md` §6.D defers to PERSISTENCE for
  its first-clear-of-the-day bonus (that entry already notes the boundary should serve any other
  periodic social feature). This doc adds no second clock; the exact day boundary and weekday anchor
  are `10_systems/PERSISTENCE.md`'s (Open Questions).
- **N, the objective rotation, and the reward table are first-pass** and flagged (Open Questions).
  The objective is a **guild-wide goal, not a per-member quest** — distinct from the per-member
  guild-quest board §8 still leaves undesigned.

Encourage-not-mandate: missing a weekly goal costs the guild nothing it had (contribution is
monotonic, §9); the goal only ever adds a carrot (`00_vision/PILLARS.md` P2/P3).

## Server Dependency

Global name uniqueness, roster membership, rank assignments, the crest, and the MOTD are all
`authority: server` (`10_systems/PERSISTENCE.md` §1–§2, which already lists guild state in its own
authority table) — shared state no single client may hold as truth (`00_vision/PILLARS.md` P6). The
incentive layer is the same: `guild_contribution` and guild level (§9), the §10 grouping buff's
same-guild/same-map check and its `exp`/drop application, and the §11 weekly-goal counters, rewards,
and week rollover are all `authority: server` (a client cannot self-award contribution, self-grant a
buff, or self-certify a goal met). **The interim solo build ships guild creation/roster/crest/chat
UI present but dormant**: a solo character has no one else to recruit, so no guild ever meaningfully
forms — no contribution accrues, no 2+-guildmate grouping buff can trigger, and no weekly goal
resolves.

## Open Questions

- Roster-expansion (§4) and crest-edit (§5) `shards` amounts are this doc's first-pass proposals;
  `10_systems/ECONOMY.md` needs to fold them into its sink budget (its own Open Questions already
  flags this exact reconciliation for the `social/` docs' fee stubs).
- Guild records have no ID scheme in `docs/ID_REGISTRY.md` (guilds are runtime player-created data,
  not Phase D authored content) — proposes server-assigned `guild_<NNNNNN>` IDs; needs
  `10_systems/PERSISTENCE.md` to confirm the format.
- No schema doc yet exists for the guild record; proposes a `guild.schema` doc (proposed, not yet in the §2 tree) at Phase C.
- **Crest shape enum vocabulary — resolved:** the enum
  (`heater`/`round`/`banner`/`diamond`/`crest_ornate`, §5) is canonical in
  `00_vision/GLOSSARY.md` under "Guild crest shapes"; the 24-symbol list remains owned by
  `40_assets/UI_ART_SPEC.md`.
- Which 40_assets doc owns the crest color palette (`40_assets/ART_BIBLE.yaml` vs
  `40_assets/UI_ART_SPEC.md`) is undecided.
- Officer cap (5, §3) and the roster growth steps (§4) are first-pass; may need retuning once
  post-launch guild-activity data exists.
- Guild-hop cooldown: none at launch (§1) since there is no bank/reward to farm by hopping (§8);
  revisit if that changes.
- Guild bank and a per-member guild-quest board (§8) are deferred future features, not designed here.
- **`guild_contribution` earn rates and guild-level thresholds (§9) are first-pass.** The raid-clear
  amount, the same-map party-hunt milestone size **N** and per-event amount, and the contribution →
  guild-level curve all need a balance pass (they pace guild-level unlocks, including the paid roster
  headroom). Owner: this doc with `10_systems/ECONOMY.md` at the arc-1/arc-2 balance pass.
- **`guild_level` needs a `00_vision/GLOSSARY.md` Provisional entry** — it is a derived guild
  quantity like `guild_contribution` (already canonical) but is only described in prose here.
  Whether the §10 grouping buff and §11 weekly-goal reward also need their own tokens is open. Owner:
  GLOSSARY gatekeeper at the next phase gate (this doc cannot mint tokens).
- **Roster headroom above 60 via guild level (§9/§4):** whether guild levels unlock further **paid**
  +10 steps (default) or raise the ceiling directly; step `shards` amounts are reserved to
  `10_systems/ECONOMY.md` exactly as §4's are. Owner: this doc with `10_systems/ECONOMY.md`.
- **Grouping-buff magnitude (+5% `exp` / +5% drop, §10) is first-pass.** The drop side's composition
  order with `fortune`'s `m` and the same-map `party_drop_bonus`, and the combined `≤ 0.95` cap, are
  `10_systems/DROPS.md`'s to own and tune (see Handoffs); the `exp` side is a source
  `10_systems/LEVELING.md` §4 must acknowledge (see Handoffs). Whether the buff scales with guild
  level is open. Owner: this doc, consumed by DROPS / LEVELING.
- **Weekly guild goal (§11) is first-pass:** the objective rotation, the target **N**, the reward
  table, and the `shards`-to-guild reward's dependency on the deferred guild bank (§8) all need
  tuning. Owner: this doc with `10_systems/ECONOMY.md`.
- **Week/day boundary (§11)** is owned by `10_systems/PERSISTENCE.md` — the weekly goal anchors to
  the same day boundary `10_systems/social/RAID.md` §6.D already defers there (fixed UTC rollover vs
  per-account local vs rolling window). Owner: `10_systems/PERSISTENCE.md`; this doc consumes.
- **Guild cosmetics** draw on the `item_cosmetic_0009`–`0064` guild reserve (`docs/ID_REGISTRY.md`);
  that block's cosmetic-system owner and earn/equip rules are unassigned until cosmetic content is
  authored (`10_systems/MONETIZATION.md` holds the charter). Owner: TBD at the cosmetic-content pass.
