# PARTY.md — Party System, Exp Share & Raids

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/STATS.md, 10_systems/JOBS.md,
10_systems/LEVELING.md, 10_systems/COMBAT_FORMULA.md, 10_systems/DROPS.md, 10_systems/INVENTORY.md,
10_systems/ECONOMY.md, 10_systems/QUESTS.md, 10_systems/DEATH_PENALTY.md,
10_systems/STATUS_EFFECTS.md, 10_systems/SPAWN.md, 10_systems/HUD.md, 10_systems/CONTROLS.md,
10_systems/social/CHAT.md, 10_systems/social/RAID.md, 15_maps_system/MAPS_SYSTEM.md,
10_systems/PERSISTENCE.md, docs/WORLD_PLAN.md

Owner doc for the **party**: membership and roster, invite/kick/leave and leader powers, the
exp-share split, loot-share modes, the HUD data contract, and the raid party rules. The **raid**
itself (entry, stage chain, lockout, rewards policy) is `10_systems/social/RAID.md`'s; kill/`exp`
math is `10_systems/LEVELING.md`/`10_systems/COMBAT_FORMULA.md`; drop tagging and table shape are
`10_systems/DROPS.md`; death/release-and-reenter is `10_systems/DEATH_PENALTY.md`; raid boss
scaling math is `10_systems/COMBAT_FORMULA.md` §13.3. This doc consumes all of those and never
restates them — it owns only who is in a party, how shared rewards split among them, and the raid
party gate.

## 1. Membership & roster

- **Size cap: 6.** Flat cap, no tiers — every party (field, dungeon, or raid) shares the same
  ceiling.
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
state (`10_systems/DEATH_PENALTY.md` §5.3, §6 below). See Open Questions — `10_systems/HUD.md`'s
current layout has no reserved region for this yet.

## 4. Exp share

**Eligibility.** A party member shares in a kill's `exp` only if they are on the **same `map_NNN`**
as the kill when the monster dies. Off-map members earn nothing from that kill.

**Level-range falloff.** Let `anchor_level` be the highest character `level` among same-map
eligible members. Each eligible member's share is scaled by their `level` gap from the anchor:

| `level` gap from anchor (`abs(member.level − anchor_level)`) | `range_mult` |
|---|---|
| 0–15 | 1.00 |
| 16–20 | 0.66 |
| 21–25 | 0.33 |
| 26+ | 0 (ineligible — excluded from the pool and its `n_eligible` count below) |

The full-credit band is deliberately **wide** (a 15-level gap still earns full share) so a veteran
can hunt with lower-level friends without dragging either party member's earnings — grouping across
levels is a social pull, not a tax (`00_vision/PILLARS.md` P2/P3). It stays **bounded**, though:
this is a party-specific anti-power-leveling gate distinct from `10_systems/COMBAT_FORMULA.md`
§9's own solo level-difference dampener (which still applies once inside the pool, via
`exp_diff_mult` below) — without the outer band, a low-level character parked beside a far
higher-level partner would draw that dampener's flat "killing up" bonus indefinitely.

**Party exp bonus — MapleStory-inspired (the "Party Bonus EXP").** Being grouped **multiplies the
shared pool**, and the bonus climbs **steeply** with party size so a full party genuinely out-earns
the same players hunting alone — the core reason to party (`00_vision/PILLARS.md` P3, a
hunt-and-hangout world). It is a **fixed lookup** on the number of same-map eligible members (a flat
table, like MapleStory's own — not a smooth formula):

| same-map eligible members | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| `party_bonus` (× the pool) | 1.00 | 1.10 | 1.25 | 1.45 | 1.70 | **2.00** |

A full party of 6 **doubles** the shared `exp` pool before it is split, and each added member is
worth more than the last — so filling the party is aspirational, exactly the MapleStory party-play
pull. It scales the pool **before** the split, so every member's share rises with it; a
solo-in-party member (everyone else off-map) draws `1.00` — no bonus without company. The table is a
first-pass faucet lever `10_systems/LEVELING.md` / `10_systems/ECONOMY.md` may retune (Open
Questions); it does **not** touch the `10_systems/LEVELING.md` §1 curve, only how fast a grouped
player travels it (that doc's `/played` estimates are solo — grouped pace is faster).

**Split — party-bonus pool, contribution-weighted base + presence bonus.**

```
pool            = round( base_exp(mob) · exp_diff_mult(anchor_level − mob.level) · party_bonus(n_eligible) )
                  # base_exp/exp_diff_mult are 10_systems/LEVELING.md §2-3 /
                  # 10_systems/COMBAT_FORMULA.md §9 terms, keyed to the party anchor, not restated
                  # party_bonus is this section's table above (the grouping incentive)
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

**Party drop bonus — the loot twin of the party exp bonus.** Grouping raises **drop chances** as
well as `exp`: the same same-map eligibility rule (above) that pools a kill's `exp` also feeds a
`party_drop_bonus`, a per-kill multiplier on drop chances that climbs with same-map eligible party
size, so a fuller party loots better as well as levels faster. The two carrots are twins — the §4
party exp bonus (climbing to `×2.00` at 6) and this drop bonus are the paired reasons to hunt
together (`00_vision/PILLARS.md` P2/P3, encourage-not-mandate). **This doc owns only who is
eligible** — the same-map, in-range membership resolved by §4's eligibility rules. The
`party_drop_bonus` **table and the roll it multiplies are `10_systems/DROPS.md`'s** (reference,
never restated here): same-map eligible members `1→1.00 · 2→1.05 · 3→1.10 · 4→1.16 · 5→1.22 ·
6→1.30`, applied to the same drop `chance` roll `10_systems/DROPS.md` §4 governs. It **stacks with
`fortune`'s own drop multiplier** (`10_systems/DROPS.md` §4's `m`), and both are subject to
`10_systems/DROPS.md`'s caps (the §4 `≤ 0.95` chance clamp still binds) — grouping and a
`fortune` build compound, but neither makes a drop certain. A solo-in-party member (everyone else
off-map) draws `1.00`, exactly like the exp bonus — no loot lift without company.

## 5. Loot share modes

Applies to the single discrete equip drop from an elite/boss/raid-boss kill — a
`10_systems/DROPS.md` §5.2–§5.4 **pool roll** or **boss/raid unique**. Materials, use items, and
`shards` are not mode-gated: every `10_systems/DROPS.md` §7-eligible same-map member receives their
own copy through the normal `10_systems/INVENTORY.md` §4 auto-loot flow regardless of mode (Open
Questions — whether this duplicates the material/`shards` faucet per member is
`10_systems/DROPS.md`/`10_systems/ECONOMY.md`'s balance call).

| Mode | Behavior |
|---|---|
| `free_for_all` | Ownership is shared across every eligible member; first to reach it in the exclusive window (`10_systems/DROPS.md` §7) claims it. |
| `round_robin` | The party holds one rotation counter. A pool/unique roll assigns ownership to the eligible member at the front, which then advances by one; ineligible members are skipped without consuming a turn. |

**Default: `round_robin`** for pool rolls and boss/raid uniques. The leader may toggle the mode
(§2) at any time; a change applies to the next roll, never retroactively.

## 6. Raids

The **raid** — its concept, entry, stage chain, lockout, and rewards policy — is owned by
`10_systems/social/RAID.md`; this section owns only the **party-side** rules a raid consumes. A raid
run is **party-required and party-instanced** across the four raid finale arenas
(`map_042`/`map_200`/`map_244`/`map_324`, `10_systems/social/RAID.md` §2, `docs/WORLD_PLAN.md`):
entering allocates the stage chain and finale arena to the entering party alone
(`10_systems/SPAWN.md` §7).

- **Legal party size: 3–6.** Below 3, raid entry is refused (`10_systems/social/RAID.md` §3,
  `15_maps_system/MAPS_SYSTEM.md` §8); the cap is the same flat 6 as §1. This fixes
  `10_systems/COMBAT_FORMULA.md` §13.3's assumed `N` range at `3–6`.
- **`N` is fixed at instance creation** (`10_systems/SPAWN.md` §7) and never re-scales mid-run —
  not on a fall, a Release, a disconnect, or a late arrival (late arrivals fight but do not add to
  `N`). No hidden re-scaling (`00_vision/PILLARS.md` P1).
- **Boss scaling** (`raid_life(N, L)`, fixed `raid_damage`, the 12-minute enrage timer) is entirely
  `10_systems/COMBAT_FORMULA.md` §13.3's; not restated here.
- **CC-immunity** for raid bosses stands at `10_systems/STATUS_EFFECTS.md` §3's existing default
  (full hard+soft immunity) — confirmed, no party-side override.
- **Death, release, and re-entry** follow `10_systems/DEATH_PENALTY.md` §5.3 exactly (fallen state,
  self-service Release, walk-back re-entry while the attempt is live, full-wipe reset); not
  restated here. This doc fixes only the party bookkeeping:
  - A **fallen** member stays on the roster and on party HUD plates (§3) in a distinct fallen
    state — resolves `10_systems/DEATH_PENALTY.md` §5.3's flagged open question.
  - While fallen but not yet Released, they are still physically on the instance map, so they remain
    exp/loot-eligible (§4/§5) for kills that land before they Release.
  - Once Released to the raid's staging area (`10_systems/social/RAID.md` §3), they fail the
    same-map gate (§4) until they walk back through the entrance.

## Server Dependency

Roster membership, HUD plate data, exp/loot arbitration, and raid instance allocation are all
`authority: server` (`10_systems/PERSISTENCE.md` §1–§2; `00_vision/PILLARS.md` P6) — a client
cannot self-certify who is in range or award itself a kill's exp/loot. **The interim solo build
ships the entire party system present but dormant**: the invite/roster UI exists but has no other
character to reach, so no party ever forms, and raids stay unreachable
(`10_systems/social/RAID.md` §8; `10_systems/SPAWN.md` §7 requires an entering party).

## Open Questions

- The 70/30 contribution/presence split and the range_mult bands (§4) are first-pass balance;
  retune once real damage-share telemetry exists. Owner: this doc with `10_systems/ECONOMY.md`.
- The **party exp bonus** table (§4, climbing to `×2.00` — a doubled pool — at `N` = 6) is
  first-pass: steep enough to make a full party genuinely inspiring (MapleStory-style) while the
  same-map presence gate and the range_mult falloff keep it from becoming a power-level faucet. It
  accelerates grouped pacing past `10_systems/LEVELING.md` §1's solo `/played` estimates — reconcile
  grouped pace against the solo curve at the next gate. Owner: this doc with `10_systems/LEVELING.md`
  / `10_systems/ECONOMY.md`.
- The **party drop bonus** (§4) is the loot twin of the party exp bonus and is first-pass like it:
  the `party_drop_bonus` curve and its interaction/cap with `fortune` are `10_systems/DROPS.md`'s to
  own and tune — this doc supplies only the same-map eligibility that keys it. Reconcile the combined
  grouping+`fortune` drop ceiling against the faucet at the next gate. Owner: `10_systems/DROPS.md`
  with `10_systems/ECONOMY.md`; this doc consumes.
- This doc's §4 contribution-weighted split is the arbiter of `10_systems/LEVELING.md` §3's
  raid-boss **150× total** (`10_systems/social/RAID.md` §6 routes the finale-boss `exp` pool here);
  LEVELING §3's per-member figures assume the even-split degenerate case (`N` = 5), which this split
  only approximates for a balanced-damage party across the legal `3–6` range. Reconcile the exact
  per-member share at the next gate. Owner: this doc with `10_systems/LEVELING.md` /
  `10_systems/social/RAID.md`.
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
