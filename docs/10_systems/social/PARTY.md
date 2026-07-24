# PARTY.md — Party System, Exp Share & Loot

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md, 10_systems/JOBS.md,
10_systems/LEVELING.md, 10_systems/COMBAT_FORMULA.md, 10_systems/DROPS.md, 10_systems/INVENTORY.md,
10_systems/ECONOMY.md, 10_systems/QUESTS.md, 10_systems/DEATH_PENALTY.md,
10_systems/STATUS_EFFECTS.md, 10_systems/SPAWN.md, 10_systems/HUD.md, 10_systems/CONTROLS.md,
10_systems/social/CHAT.md, 10_systems/social/PARTY_QUEST.md, 15_maps_system/MAPS_SYSTEM.md,
10_systems/PERSISTENCE.md, docs/WORLD_PLAN.md

Owner doc for the **party**: membership and roster, invite/kick/leave and leader powers, the
exp-share split, loot-share modes, and the HUD data contract. Kill/`exp`
math is `10_systems/LEVELING.md`/`10_systems/COMBAT_FORMULA.md`; drop tagging and table shape are
`10_systems/DROPS.md`; death/release-and-reenter is `10_systems/DEATH_PENALTY.md`. The two
party quests (`pq_undervault`, `pq_mainspring`) — their party-size gates, stage flow, and
instanced rewards — are owned by `10_systems/social/PARTY_QUEST.md`, which consumes this doc's
share rules. This doc consumes all of those and never restates them — it owns only who is in a
party and how shared rewards split among them.

## 1. Membership & roster

- **Size cap: 6.** Flat cap, no tiers — every party (field, dungeon, or party quest) shares the
  same ceiling.
- One party per character. A pending invite (§2) does not count as membership.
- Roster fields: member list in join order, each member's `level`, job line
  (`10_systems/JOBS.md`), and current `map_NNN` (drives §4/§5's same-map gate).
- A party of 1 (every other member left/kicked) auto-disbands — a solo character is not a party.

## 2. Invite / kick / leave / leadership

| Action | Who | Notes |
|---|---|---|
| Invite | any current member | targets a player by in-world target or roster/whisper entry (`10_systems/social/CHAT.md`); no proximity or same-map requirement to send |
| Accept / decline | the invited player | declining or a 30 s timeout cancels with no state change |
| Kick | **leader only** | removes a member immediately; no penalty beyond removal |
| Leave | any member (incl. leader) | self-service, any time, including mid-combat |
| Promote (transfer leadership) | **leader only** | hands leadership to a chosen member |
| Set loot mode (§5) | **leader only** | `free_for_all` / `round_robin` |
| Disband | **leader only** | dissolves the party immediately |

**Leader succession.** If the leader leaves or disconnects without transferring leadership first,
leadership passes automatically to the next member by join order (oldest remaining member) — a
deterministic rule, no vote, no hidden tie-break (`00_vision/PILLARS.md` P1).

## 3. Party HUD plates

Each party member (including fallen ones, §6) renders a HUD plate for every other member; the
plate's visual design, layout, and animation are entirely `10_systems/HUD.md`'s. This doc fixes
only the **data** a plate consumes: member name, `level`, job line icon token, current `life`/
`essence` as a percentage of max (`10_systems/STATS.md` §2), same-map indicator, and alive/fallen
state (`10_systems/DEATH_PENALTY.md`; party-quest fallen bookkeeping in
`10_systems/social/PARTY_QUEST.md` §7). See Open Questions — `10_systems/HUD.md`'s current
layout has no reserved region for this yet.

## 4. Exp share

**Eligibility.** A party member shares in a kill's `exp` only if they are on the **same `map_NNN`**
as the kill when the monster dies. Off-map members earn nothing from that kill.

**Level-range falloff.** Let `anchor_level` be the highest character `level` among same-map
eligible members. Each eligible member's share is scaled by their `level` gap from the anchor:

| `level` gap from anchor (`abs(member.level − anchor_level)`) | `range_mult` |
|---|---|
| 0–10 | 1.00 |
| 11–15 | 0.66 |
| 16–20 | 0.33 |
| 21+ | 0 (ineligible — excluded from the pool and its `n_eligible` count below) |

This is a party-specific anti-power-leveling gate distinct from `10_systems/COMBAT_FORMULA.md`
§9's own solo level-difference dampener (which still applies once inside the pool, via
`exp_diff_mult` below) — without it, a low-level character parked beside a far higher-level
partner would draw that dampener's flat "killing up" bonus indefinitely.

**Split — contribution-weighted base + presence bonus.**

```
pool            = round( base_exp(mob) · exp_diff_mult(anchor_level − mob.level) )
                  # base_exp/exp_diff_mult are 10_systems/LEVELING.md §2-3 /
                  # 10_systems/COMBAT_FORMULA.md §9 terms, keyed to the party anchor, not restated
contribution(m) = damage_dealt(m, mob) / Σ damage_dealt(all eligible, mob)   # 0 if none dealt
member_pool(m)  = pool · ( 0.70 · contribution(m) + 0.30 / n_eligible )
member_exp(m)   = round( member_pool(m) · range_mult(m) )
```

If total eligible-member damage to the monster is 0 (e.g., an unattended DoT kill), the
contribution term is skipped and the full pool splits evenly across eligible members. A lone
eligible member (everyone else off-map or out of range) draws the full pool.

**Quest kill-credit.** `10_systems/QUESTS.md`'s own Open Questions defers party kill/collect
credit-sharing to this doc. Resolution: a `kill`-type quest step's credit follows the same
same-map eligibility as `exp` above — every same-map member with that step active gets credit when
the tag lands, mirroring `10_systems/DROPS.md` §7's shared-tag model. A `collect`-type step does
**not** share — credit requires actually receiving the item (§5), since it is tied to holding the
item, not to presence.

## 5. Loot share modes

Applies to the single discrete equip drop from an elite/boss kill — a
`10_systems/DROPS.md` §5.2–§5.4 **pool roll** or **boss unique**. Materials, use items, and
`shards` are not mode-gated: every `10_systems/DROPS.md` §7-eligible same-map member receives their
own copy through the normal `10_systems/INVENTORY.md` §4 auto-loot flow regardless of mode (Open
Questions — whether this duplicates the material/`shards` faucet per member is
`10_systems/DROPS.md`/`10_systems/ECONOMY.md`'s balance call).

| Mode | Behavior |
|---|---|
| `free_for_all` | Ownership is shared across every eligible member; first to reach it in the exclusive window (`10_systems/DROPS.md` §7) claims it. |
| `round_robin` | The party holds one rotation counter. A pool/unique roll assigns ownership to the eligible member at the front, which then advances by one; ineligible members are skipped without consuming a turn. |

**Default: `round_robin`** for pool rolls and boss uniques. The leader may toggle the mode
(§2) at any time; a change applies to the next roll, never retroactively.

## 6. Party quests

The two instanced co-op party quests — `pq_undervault` (finale `map_042`, The Cellar King) and
`pq_mainspring` (finale `map_200`, The Custodian) — are owned by
`10_systems/social/PARTY_QUEST.md`. Their party-size gate (3–6), level bands, stage flow,
instance allocation, and reduced-reward solo open-arena path live there. Those runs consume
**this** doc's rules unchanged: roster/leadership (§1–§2), the exp-share split (§4), and the
loot-share modes (§5). This doc adds no party-quest-specific party rules beyond confirming the
same flat size cap of 6 (§1) applies.

## Server Dependency

Roster membership, HUD plate data, and exp/loot arbitration are all
`authority: server` (`10_systems/PERSISTENCE.md` §1–§2; `00_vision/PILLARS.md` P6) — a client
cannot self-certify who is in range or award itself a kill's exp/loot. **The interim solo build
ships the entire party system present but dormant**: the invite/roster UI exists but has no other
character to reach, so no party ever forms (and the party quests in
`10_systems/social/PARTY_QUEST.md` stay unreachable, since each requires an entering 3–6 party).

## Open Questions

- The 70/30 contribution/presence split and the range_mult bands (§4) are first-pass balance;
  retune once real damage-share telemetry exists. Owner: this doc with `10_systems/ECONOMY.md`.
- This doc's split refines `10_systems/LEVELING.md` §3's "assumes an even split among a mid party"
  note; the two should reconcile at the next gate — the actual split is not strictly even, only
  approximately so for a balanced-damage party.
- Whether "same-map" (§4/§5) should tighten to a same-screen/zone radius on very large field maps
  is flagged, not resolved; default keeps the literal same-map gate.
- Whether material/use-item/`shards` rows duplicate per eligible member or are split (§5) is
  `10_systems/DROPS.md`/`10_systems/ECONOMY.md`'s faucet-balance call; this doc assumes
  duplication.
- Need/greed as a third loot mode (floated by `10_systems/DROPS.md`'s own wording) is not designed
  in this pass; only `free_for_all`/`round_robin` exist.
- Exact invite-decline timeout (30 s) is first-pass UX, not load-bearing.
- Neither `10_systems/HUD.md`'s layout (§2/§4, local-player-plate only) nor
  `10_systems/CONTROLS.md`'s input map yet reserves a screen region or panel-toggle keybind for
  other party members' plates (§3) — this doc supplies only the data contract for when they do.
