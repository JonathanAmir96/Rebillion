# PARTY_FINDER.md — Party-Finder / LFG Board

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/LEVELING.md, 10_systems/JOBS.md, 10_systems/HUD.md, 10_systems/CONTROLS.md,
10_systems/QUESTS.md, 10_systems/PERSISTENCE.md, 10_systems/social/PARTY.md,
10_systems/social/RAID.md, 10_systems/social/CHAT.md, 15_maps_system/MAPS_SYSTEM.md,
docs/WORLD_PLAN.md, docs/ID_REGISTRY.md

Owner doc for the **`party_finder`** board: the one cross-map listing board where players advertise
and find groups so that party hunting and raids actually happen — the connective tissue of the
owner-directed "encourage grouping" social package (`memory.md`, 2026-07-24). Party membership,
leadership, exp/loot share, and the size cap are entirely `10_systems/social/PARTY.md`'s; the raid
itself (entry, herald, stage chain) is `10_systems/social/RAID.md`'s; the panel frame is
`10_systems/HUD.md`'s; the input map is `10_systems/CONTROLS.md`'s; who owns the truth is
`10_systems/PERSISTENCE.md`'s. This doc consumes all of those and restates none — it owns only the
board, its listings, and the browse-and-request flow that turns a solo player into a party member.

## 1. Purpose

The board exists to solve the **matching** problem the rest of the social package assumes but does
not itself provide: `10_systems/social/PARTY.md`'s exp bonus and `party_drop_bonus`, and
`10_systems/social/RAID.md`'s party-required entry, all reward grouping, but a player has to *find*
the group first. `party_finder` is that finding step — carrots, not solo penalties: it makes
grouping the easy path without making solo the punished one (`00_vision/PILLARS.md` P2/P3, a
hunt-and-hangout world). It is **one board, cross-map** — a player anywhere in the world sees the
same global listing set, so a group forming in Millbrook can recruit someone still on Emberfoot.

The board never forms a party by itself. It surfaces intent and routes a **request to join**; the
actual party — invite, accept, roster, leadership — is created and owned by
`10_systems/social/PARTY.md` §1–§2 the instant a request is accepted. `party_finder` is the
bulletin board, not the party.

## 2. Listings

A player who is not in a party, or a **party leader** (`10_systems/social/PARTY.md` §2) recruiting
for an existing party, posts one listing. A listing carries:

| Field | Meaning |
|---|---|
| `activity` | One of the enum in §2.1 — what the group is forming *to do* |
| target | A region slug or `map_NNN` (`docs/WORLD_PLAN.md`), or a `level` band, naming where/what — for a `raid` listing this is the `raid_<name>` (`10_systems/social/RAID.md` §2) |
| open slots | How many members are still wanted, `1`–`6` (see below) |
| note | Optional short free-text line (e.g. "need one more, ranged pref") |
| poster | The poster's (or party's) `level` and job line (`10_systems/JOBS.md`), shown so browsers can judge fit |

**Open slots are bounded by the party size cap of 6** (`10_systems/social/PARTY.md` §1): a solo
poster may seek up to 5 more (the 6-member ceiling minus themselves); a leader recruiting for a
partly-filled party may seek only up to the seats actually left. A `raid` listing additionally
respects the raid's **3–6** legal party size (`10_systems/social/RAID.md` §3) — the board does not
mint a new size rule, it reflects PARTY/RAID's.

### 2.1 The `activity` enum

| Value | Forms a group for |
|---|---|
| `field_hunt` | Open-field party hunting on a region or `map_NNN` (the `10_systems/social/PARTY.md` §4 exp/`party_drop_bonus` loop) |
| `raid` | A specific `raid_<name>` run (`10_systems/social/RAID.md`) — the target field names the raid |
| `quest` | Clearing a shared or `kill`-credit quest step together (`10_systems/QUESTS.md`) |
| `boss` | A region/open-arena boss kill (`10_systems/social/RAID.md` §7's open, non-raid entry) |
| `social` | Non-combat grouping — hanging out at a hub (§6), no objective |

The `raid` value's target is a `raid_<name>` token, which is real and registry-minted
(`10_systems/social/RAID.md` §1, `docs/ID_REGISTRY.md`). The other four values classify a listing's
purpose but are **not yet `00_vision/GLOSSARY.md` tokens** — see Open Questions.

## 3. Browsing, filtering & joining

- **Browse & filter.** Any player opens the board (§5) and browses the global listing set,
  filterable by `activity`, `level` band, and region/`map_NNN`. Each row shows the §2 fields so a
  browser can judge fit before requesting.
- **Auto-suggest.** The board highlights listings that match the viewer's own `level`
  (`10_systems/LEVELING.md`) and current region — the "here are groups you could join right now"
  default view — so a player who just wants company does not have to hand-filter. This is a sort/
  surface convenience only; it never auto-joins.
- **Request to join.** A browser sends a **request to join** a listing; the listing's poster (the
  party **leader**, or the solo poster who becomes leader on the first accept) **accepts or
  declines**. Acceptance hands off to `10_systems/social/PARTY.md` §2's invite/accept flow, which
  is the sole authority on roster changes — the board cannot add a member directly. Leader authority
  over who joins is PARTY.md's and is not overridden here.
- **No auto-teleport.** Accepting a request does **not** move the joining player. Grouping still
  respects the world graph (`docs/WORLD_PLAN.md`, `15_maps_system/MAPS_SYSTEM.md`): the new member
  travels to the group the ordinary way (coach, longship, on foot). The board advertises *where* a
  group is; getting there is still play. Whether a convenience "summon to leader" or "travel-to-
  listing" shortcut should ever exist is deliberately left open (Open Questions) — the default is
  the honest world graph.

## 4. Anti-abuse & limits

The board is server-owned (§7), so listing hygiene is enforced server-side. First-pass rules, kept
deliberately light (specifics flagged in Open Questions):

- **Listing lifetime.** A listing **expires** after an inactivity/age window rather than lingering
  forever; the poster may refresh or re-post.
- **One active listing per party.** A party (or solo poster) holds at most one live listing at a
  time — no flooding the board with duplicates.
- **Rate / spam limits.** Post and request actions are rate-limited server-side, and the optional
  note is subject to the same moderation channel as chat (`10_systems/social/CHAT.md`, a stub) so
  the note field is not a moderation bypass.

Exact windows, counts, and the moderation hookup are first-pass and unsettled — Open Questions.

## 5. HUD / UX hook

The board is presented through a **party-finder panel** — a toggle window drawn in
`10_systems/HUD.md`'s `frame_window` (the same variant as Inventory/Skills/Guild); its layout,
metrics, and art are `10_systems/HUD.md`'s and `40_assets/UI_ART_SPEC.md`'s, not restated here.
This doc fixes only that the panel exists and what it shows (§2–§3): the filterable listing set, the
post-a-listing form, and the request/accept controls. Filter and note text-entry use
`10_systems/HUD.md`'s `frame_input`.

The panel is openable **from any town** and via a **hotkey**. `10_systems/CONTROLS.md` §1's keybind
table does not yet reserve a key for it (Inventory `I`, Skills `K`, Quest Log `L`, Map `M`, Guild
`G` are taken) — the party-finder toggle needs a key minted there; flagged as a handoff in Open
Questions rather than invented here.

## 6. Hangout hubs

The board is designed to be *most used* in a handful of town **social spaces** — the places idle
players congregate between hunts (`00_vision/PILLARS.md` P3, hunt-and-hangout). These are existing
towns already placed by `docs/WORLD_PLAN.md`; this section only designates their social role and
authors no new maps:

- **Millbrook Central** (`map_018`, Harthmoor ring south hub) — the **primary social plaza**, the
  game's default gathering town and the busiest board.
- The three arc-2 **port towns** — **Frosthaven** (`map_204`, Frostpeak Isle), **Spirehaven**
  (`map_245`, Arcane Reach), and **Duskwatch Landing** (`map_285`, Voidshore) — as the far-isle
  gathering points where longship travelers cluster (`docs/WORLD_PLAN.md`).

These are hangout *designations*, not mechanics: the board is global (§1) and works from anywhere;
the hubs are simply where the population — and therefore the live listings — naturally concentrate.
Whether a hub should get any in-world affordance (a visible board object, a matchmaker NPC) beyond
the panel is left open (Open Questions).

## 7. Server Dependency

The board, every listing, the request/accept routing, and all match state are `authority: server`
end to end (`10_systems/PERSISTENCE.md` §1–§2, `00_vision/PILLARS.md` P6): a client may not mint a
listing other players see, self-accept into a party, or self-certify a match. Listings live in the
same server-owned social state as party/guild/market (`10_systems/PERSISTENCE.md` §2).

**In the interim solo build the board ships present but dormant** — exactly as the other social
systems are stubbed (`10_systems/social/PARTY.md` §Server Dependency,
`10_systems/social/RAID.md` §8). The panel (§5) opens and renders, but with no other player online
there are no listings to show and no request can be routed: the board is **empty and its post/
request actions are no-ops**. The `GameState` facade (`10_systems/PERSISTENCE.md` §5) carries the
board's fields so the live-server swap changes no calling code (P6). This is the honest
designed-now / stubbed-now shape, not a missing feature.

## Open Questions

- **Resolved (2026-07-24 md audit): `activity` enum tokenization.** All five §2.1 values
  (`field_hunt` · `raid` · `quest` · `boss` · `social`) are canonical GLOSSARY tokens — see
  `00_vision/GLOSSARY.md` "Party-finder activity" (owner: this doc). No Provisional entries needed.
- **Party-finder keybind.** `10_systems/CONTROLS.md` §1 reserves no key or gamepad button for the
  §5 panel toggle. A key must be minted there (its "Open Questions" already tracks an undecided
  spare key). Handoff to `10_systems/CONTROLS.md`; until then the panel is town-menu-openable only.
- **Anti-abuse specifics (§4).** Listing lifetime/expiry window, the exact post/request rate limits,
  and whether the note field routes through `10_systems/social/CHAT.md`'s moderation are all
  first-pass and unsettled. Owner: this doc with the backend social suite
  (`70_integrations/CHAT_SOCIAL_BACKEND.md`) once the balance/backend pass reaches it.
- **Travel convenience.** Whether accepting a request should ever offer a teleport/summon shortcut
  to the group (vs. §3's default of honoring the world graph — coach/longship/on-foot travel) is
  deliberately unresolved. Default: **no** auto-teleport; grouping still costs travel. Owner: this
  doc with `docs/WORLD_PLAN.md`'s travel-economy owners (`10_systems/ECONOMY.md`).
- **Hub affordances (§6).** Whether the hangout hubs should carry an in-world board object or a
  matchmaker NPC beyond the global panel is not designed this pass; default is panel-only, hubs are
  designation-only. Owner: this doc with `docs/WORLD_PLAN.md`.
- **README reachability handoff.** This doc is reachable from `README.md` through
  `00_vision/GLOSSARY.md`'s `party_finder` owner reference (per the connectivity law and
  `tools/md_graph.py`), and through its sibling social docs. `README.md`'s "Start here" indexes
  `docs/10_systems/` as a directory, not individual social docs, so there is **no per-doc social
  index line to extend** — README was intentionally not edited. If the producer later adds an
  enumerated social-docs index line, link this doc from it and re-run `tools/md_graph.py`.
