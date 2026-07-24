# UI_WINDOWS.md — Toggle-Window Layouts: Inventory, Character/Equipment, Party, Guild

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/HUD.md,
10_systems/CONTROLS.md, 10_systems/INVENTORY.md, 10_systems/ITEMS.md, 10_systems/STATS.md,
10_systems/SKILL_SYSTEM.md, 10_systems/ENHANCEMENT.md, 10_systems/QUESTS.md,
10_systems/COSMETICS.md, 10_systems/social/PARTY.md, 10_systems/social/PARTY_FINDER.md,
10_systems/social/GUILD.md, 10_systems/PERSISTENCE.md, 40_assets/UI_ART_SPEC.md,
40_assets/ART_BIBLE.yaml

Owner doc for the **layout and anatomy of the framed toggle windows** — what each window shows,
how its content is arranged, and which locked `40_assets/UI_ART_SPEC.md` frame/font tokens it is
built from. It owns *layout only*: every rule, number, and datum displayed here is owned by the
cited system doc and never restated. The always-on HUD shell is `10_systems/HUD.md`'s; input
bindings and controller navigation are `10_systems/CONTROLS.md`'s; the Quest Log window is
already specified by `10_systems/QUESTS.md` §8 and is not re-specified here. Interface identity
is the locked framed-box family (`40_assets/UI_ART_SPEC.md`) — the same classic-2D-MMO lineage as
the genre's best-known windows, **original in vocabulary, art, and arrangement** (P7: homage yes,
clone never).

## 1. Shared window chrome

Every window here renders in `frame_window` (`10_systems/HUD.md` §1) using the standard panel
construction (`40_assets/UI_ART_SPEC.md`: title-bar strip, 8 px-inset content, footer buttons):

- **Title bar**: window name in `ui_title`, a close glyph at the right (`Escape` also closes the
  topmost window, `10_systems/CONTROLS.md` §1).
- **One instance each**; reopening focuses the existing window. Multiple different windows may be
  open at once; the topmost captures controller focus (`10_systems/CONTROLS.md` §6).
- **Placement is fixed per window at launch** (draggability is `40_assets/UI_ART_SPEC.md`'s open
  question; until it resolves, each window opens at its anchored default and windows never
  overlap the bottom bar).
- **Tabs** inside a window use `frame_button` chips under the title bar; `LB`/`RB` cycle them on
  gamepad (`10_systems/CONTROLS.md` §6).
- All displayed state is the same server-authoritative data every system doc already defines
  (`10_systems/PERSISTENCE.md`); windows are pure views — no window-side rules.

## 2. Inventory window (`I`, `10_systems/CONTROLS.md` §1)

Anchored center-right. The classic grid-bag window, one tab per item category
(`10_systems/INVENTORY.md` §1):

```
┌─ Inventory ────────────────── ✕ ┐
│ [equip] [use] [etc]              │   ← tab strip (frame_button; LB/RB on pad)
│ ┌──┬──┬──┬──┬──┬──┐             │
│ │  │  │  │  │  │  │  6 × 4      │   ← frame_slot grid, base 24 slots/tab
│ ├──┼──┼──┼──┼──┼──┤             │     (rows appended +8 to max 48,
│ │  │  │  │  │  │  │             │      INVENTORY §1 expansion policy)
│ └──┴──┴──┴──┴──┴──┘             │
│ ◇ 12,480 shards   [Sort] [Sell] │   ← footer
└──────────────────────────────────┘
```

- **Grid**: `frame_slot` cells, **6 columns**; base 24 slots = 4 rows, expansion appends rows
  (+8 = ~1.3 rows) to the 48 max — slot counts, stacking, and expansion are
  `10_systems/INVENTORY.md` §1–§2's. Slot states (empty/filled/selected/locked), rarity ring,
  quantity badge, and tooltips-on-hover are all the locked `40_assets/UI_ART_SPEC.md`
  constructions.
- **Footer**: the `shards` wallet readout (`shards` icon + balance in `ui_number`) — the same
  single value as the bottom-bar wallet (`10_systems/HUD.md` §3; wallet semantics
  `10_systems/INVENTORY.md` §3) — plus **Sort** (auto-sort, `10_systems/INVENTORY.md` §8) and,
  only while a vendor dialog is open, **Sell/quick-vendor** (`10_systems/INVENTORY.md` §8).
- **Drag interactions**: drag equip → paper-doll slot to equip (§3); drag `use` item → quickslot
  (`10_systems/HUD.md` §3); drag stack → empty slot to split (`10_systems/INVENTORY.md` §2);
  slot-lock via context action (`10_systems/CONTROLS.md` §6 `Y`).
- The **bank** (`10_systems/INVENTORY.md` §7) reuses this exact window anatomy side-by-side with
  the inventory when open at an inn — same grid construction, 32-slot base, transfer by drag; no
  separate layout is designed.

## 3. Character window (`K`, `10_systems/CONTROLS.md` §1 "Skills/Character") — Equipment tab

The `K` window carries two tabs: **Character** (equipment paper-doll + stats, this section) and
**Skills** (the skill list/ranks view, `10_systems/SKILL_SYSTEM.md`; its layout is a thin list —
learn/rank buttons per that doc's rules — not elaborated further here). Anchored center-left —
open `K` + `I` together and the classic loop (bag on the right, doll on the left, drag between)
just works.

```
┌─ Character ───────────────────── ✕ ┐
│ [Character] [Skills]                │
│        ┌────────┐      ┌─ stats ─┐ │
│ [head] │        │ [amulet]        │ │
│ [cape] │ idle   │ [ring ]  might  │ │
│ [weap] │ preview│ [body ]  finesse│ │
│ [glove]│        │ [legs ]  focus  │ │
│        └────────┘ [boots]  fortune│ │
│  Lv NN · Job · exp ▓▓░ NN%        │ │
└─────────────────────────────────────┘
```

- **Paper-doll**: the character's idle animation renders center (same sprite/cosmetic layering
  rules as in-world, `10_systems/COSMETICS.md` §4 display order), ringed by one `frame_slot` per
  GLOSSARY equipment slot — `weapon` · `head` · `body` · `legs` · `boots` · `gloves` · `cape` ·
  `ring` · `amulet` (`10_systems/ITEMS.md` owns slot semantics and equip legality; empty slots
  show the slot-type glyph per `40_assets/UI_ART_SPEC.md`). The provisional `shield` / `overall`
  slots (`00_vision/GLOSSARY.md` Provisional) get doll positions when their integration wave
  lands — the doll reserves the space, nothing more.
- **Equip/unequip**: drag between doll and inventory grid, or context-action equip from the
  inventory (`10_systems/CONTROLS.md` §6). Equip legality (level, `req_line`) is
  `10_systems/ITEMS.md`'s; an illegal drag shows the deny cursor (`40_assets/UI_ART_SPEC.md`),
  never a silent fail.
- **Stats column**: the four primaries with the free-allocation `[+]` buttons while unspent
  points exist, then the derived block — `life`/`essence` pools, `power`/`spellpower`,
  `armor`/`warding`, `precision`/`evasion`, `crit_rate`/`crit_power`, `haste` — all values
  straight from `10_systems/STATS.md` §2–§7 (numbers in `ui_number`; soft-capped values show
  their effective figure with the raw value in the tooltip). Free-point spending/reallocation
  rules and fees are `10_systems/STATS.md` §4.3 / `10_systems/ECONOMY.md` §3.1's.
- **Footer strip**: `level`, job title (`10_systems/JOBS.md` §0 display names), and a compact
  `exp` fraction mirroring the bottom-edge strip (`10_systems/HUD.md` §3).
- An equipped item's tooltip includes its enhancement `+n` state (`10_systems/ENHANCEMENT.md`);
  the enhancement *process* happens at its own NPC flow, not in this window.

## 4. Party panel (`P`, shared window with the party finder)

`P` opens the grouping window with two tabs: **Party** (your current party, this section) and
**Board** (the `party_finder` listings, `10_systems/social/PARTY_FINDER.md` — its listing/filters
layout is that doc's stub to elaborate). Anchored center. Dormant-but-designed in the interim
solo build, like everything party-shaped (`00_vision/PILLARS.md` P6).

- **Roster list**: up to 6 rows (`10_systems/social/PARTY.md` §1), each row = name, `level`, job
  title, same-map indicator, alive/fallen state — the HUD party plates' identity fields
  (`10_systems/HUD.md` §4.1) with the job title in place of the job-line icon; the `life`/`essence`
  percentage bars stay on the HUD plates — plus a leader crown glyph on the leader's row.
- **Leader controls** (visible to the leader only, `10_systems/social/PARTY.md` §2–§3): invite
  (opens name entry, `frame_input`), kick, promote, and the **loot mode** selector
  (`free_for_all` / `round_robin`, PARTY §5). Members see Leave.
- **Footer**: the party's active `party_drop_bonus` / exp-bonus tier at current same-map count
  (values from `10_systems/DROPS.md` §4.1 / PARTY §4 — displayed, never recomputed) — the "why
  group" carrot made visible in the window where grouping happens.
- Invites arrive as a `frame_dialog` confirm (`10_systems/HUD.md` §1) — never an auto-join.

## 5. Guild window (`G`, `10_systems/CONTROLS.md` §1)

Anchored center. Three tabs; all data and permissions are `10_systems/social/GUILD.md`'s. Live
surfaces in the interim solo build follow that doc's §0 scope (roster/chat/crest/MOTD; the
incentive tabs render dormant).

- **Roster tab**: member list — name, `level`, job, rank (the three-rank model, GUILD §3),
  last-online; rank-gated context actions (invite/kick/promote) per GUILD's permission table.
- **Crest tab**: the composable crest preview (`shield_shape + symbol + 2 palette colors`,
  rendered by the `40_assets/UI_ART_SPEC.md` crest compositor at 64 px) with rank-gated pickers
  for shape/symbol/palette (data contract GUILD §6; edit permissions GUILD §3).
- **Info tab**: guild name, MOTD (`frame_input`, rank-gated edit), member count vs roster cap,
  and — server-live only — `guild_level` + `guild_contribution` progress and the weekly guild
  goal (GUILD §9–§11), rendered but inert in solo.
- Guild creation itself is the guild-hall NPC flow (GUILD §1), not this window; an unguilded
  character's `G` window shows a pointer to Millbrook's guild hall instead of tabs.

## 6. Authority

Windows render server-authoritative state and submit intents (equip, spend a point, invite,
change loot mode) that the owning systems validate (`10_systems/PERSISTENCE.md`,
`00_vision/PILLARS.md` P6). A window never computes a value the server owns — every number shown
traces to an owning doc's formula output.

## Open Questions

- Window draggability (vs fixed anchors) inherits `40_assets/UI_ART_SPEC.md`'s open question;
  fixed anchors are the launch default here.
- The Skills tab (§3) and the party-finder Board tab (§4) are named as tabs but their internal
  layouts are thin; elaborate alongside `10_systems/SKILL_SYSTEM.md` UI needs and
  `10_systems/social/PARTY_FINDER.md` when those surfaces firm up. Owner: this doc.
- Whether the Character tab should also surface collection/bestiary progress
  (`10_systems/COLLECTIONS.md`) or that stays its own window is undecided; default: separate,
  out of this doc's scope until COLLECTIONS claims a binding.
- Gamepad grid navigation specifics beyond `10_systems/CONTROLS.md` §6 (e.g., wrap-around order
  between the doll ring and the stats column) are a coding-pass detail; flagged for the
  engineering brief, not designed here.
- Bank-open-beside-inventory sizing (§2) on the 640×360 base is tight; if both 48-slot grids
  can't fit side-by-side at 1×, the bank view may need pagination — flag for
  `40_assets/UI_ART_SPEC.md`'s Phase C metrics pass.
