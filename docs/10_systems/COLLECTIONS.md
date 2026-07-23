# COLLECTIONS.md — Bestiary / Collection Log (Owner Doc)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, docs/VALIDATION.md, 20_schemas/monster.schema.md,
20_schemas/drop_table.schema.md, 10_systems/DROPS.md, 10_systems/LEVELING.md,
10_systems/ECONOMY.md, 10_systems/QUESTS.md, 10_systems/PERSISTENCE.md, 10_systems/HUD.md,
40_assets/UI_ART_SPEC.md

Owner doc for the **bestiary / collection log**: what unlocks an entry, what a completed entry
shows, how region/tier completion is measured, and what a milestone pays out. This doc invents
no monster data, no drop data, and no new content IDs — it is a **read model** over
`50_content/monsters/mob_NNN.yaml` and `50_content/drop_tables/drop_mob_NNN.yaml`, plus a small
slice of new **per-character progress state** (discovery flags, revealed-drop flags, claimed
rewards) that this doc defines and `10_systems/PERSISTENCE.md` tags for authority. Reward
*sizes* are cited from `10_systems/LEVELING.md`/`10_systems/QUESTS.md`, never re-derived here.

## 1. Core rule — a derived view, zero new content

The collection log has **no schema of its own** and mints **no new IDs**. Every entry is keyed
by an existing `mob_NNN`; every field the log displays — `name`, `tier`, `element`, `level`,
region (from the `mob_NNN`'s slot in `docs/ID_REGISTRY.md` Monsters, per
`20_schemas/monster.schema.md` File conventions), `flavor`, and the row list of its paired
`drop_mob_NNN` — is read straight off `20_schemas/monster.schema.md` and
`20_schemas/drop_table.schema.md` fields that already exist. Nothing here duplicates or
restates those fields (P5, CLAUDE.md Law 2).

**Consequence:** landing a monster in `50_content/monsters/` (with its paired drop table)
**automatically adds its bestiary entry** — no separate authoring step, no `bestiary_NNN` file,
no entry to keep in sync. A Phase D region batch that lands `mob_028`–`047` gets Verdant
Hollow's 20-entry set "for free" the moment those files pass `docs/VALIDATION.md`. If a monster
is ever renumbered or reslotted (it cannot be, per CLAUDE.md Law 3 / ID_REGISTRY immutability),
its bestiary entry moves with it automatically — there is nothing to renumber on this doc's
side.

What this doc *does* add: three small pieces of **per-character progress state** not expressible
as a static content field (discovery state, per-row drop-reveal, claimed-reward flags — §3–§6).
None of it is a schema, a content file, or an ID; all of it is save data under
`10_systems/PERSISTENCE.md`'s facade (§7).

## 2. Entry identity & fields (all cited, none restated)

| Log field | Source | Owner |
|---|---|---|
| Key | `mob_NNN` | `docs/ID_REGISTRY.md` Monsters |
| `name`, `flavor` | monster file | `20_schemas/monster.schema.md` |
| `tier` | monster file | `20_schemas/monster.schema.md` (tier enum owner) |
| `element`, `weak_to`/`resists`/`immune_to` | monster file | `10_systems/ELEMENTS.md` |
| `level` | monster file | `20_schemas/monster.schema.md` |
| Region | `mob_NNN`'s ID-block slot | `docs/ID_REGISTRY.md`, `docs/WORLD_PLAN.md` region sections |
| Drop rows | paired `drop_mob_NNN` | `20_schemas/drop_table.schema.md`, `10_systems/DROPS.md` §1 |

No field in this table is edited or overridden by this doc; a validator change to either schema
propagates to the log with no COLLECTIONS.md edit required.

## 3. Discovery model — unseen / sighted / logged

Three states per `mob_NNN`, per character, strictly one-way (never regresses):

- **`unseen`** — default. The entry does not appear by name in the log; only its tier/region
  are counted toward the "undiscovered" tally (§5) so a player can see *how much* of a region is
  still unknown without spoiling *what*.
- **`sighted`** — set the first time the monster enters the player's aggro/render range, whether
  or not the player deals or takes damage. Reveals `name`, `tier`, `element`, and `level` only —
  a silhouette-and-label preview, not the full card. Sighting a species does not require combat
  and is not gated by kill credit; it exists so exploring a region ahead of hunting it still
  feels like progress (P2).
- **`logged`** — set on the character's **first kill-credited** death of that species. Kill
  credit is exactly `10_systems/DROPS.md` §7's tag-eligibility rule (dealt or took damage before
  the monster died); this doc adds no separate "bestiary kill" definition. A `logged` entry shows
  the full card: `flavor`, full drop-row list (subject to §4's per-row reveal), and unlocks the
  one-time first-kill grant (§6).

Only `logged` counts toward the completion percentages in §5; `sighted` is a preview state, not
partial credit.

## 4. Drop-line reveal — one flag per row, not per item

A `logged` entry's drop-row list starts with every row **masked** except the `guaranteed`
`shards` row (every kill drops it, so there is nothing to discover there). Each other row —
material, use item, emberstone, pool roll, boss unique — flips from masked to **revealed**
the first time the character personally receives that exact `ref` from that specific
`mob_NNN`'s table (an ordinary loot grant already recorded by `10_systems/DROPS.md` §7/§9 and
`10_systems/INVENTORY.md`; this doc adds no new grant, only a per-row "have I ever gotten this"
flag keyed off the grant event). A revealed row never re-masks. Pool rows (`ref: pool_equip_r*`)
reveal as "an equipment roll exists" the first time *any* item from that roll is received from
this mob — the log does not enumerate the whole regional pool per monster (that list is
`50_content/drop_tables/pools.yaml`'s, not repeated here).

This gives the "collect every drop" texture P2 wants without a new faucet: nothing is granted
for revealing a row, it is pure bookkeeping over drops the character already earned normally.

## 5. Completion structure

Completion is measured in three nested scopes, always as **`logged` / total**, never counting
`sighted`:

- **Per-tier, per-region.** Each `docs/WORLD_PLAN.md` region block (R1 Emberfoot … R8 Clockwork)
  is split into its `normal` / `elite` / `boss` subsets exactly as `docs/ID_REGISTRY.md`'s
  Monsters table slots them (e.g., R3 Verdant: 16 `normal`, 3 `elite`, 1 `boss`). A region's
  three tier percentages are shown separately so a player can see "all bosses down, elites still
  thin" at a glance.
- **Per-region overall.** The region's three tiers combined (e.g., Verdant 20/20 once every
  `mob_028`–`047` is `logged`).
- **Global.** All 150 across both islands, further broken out by tier: 118 `normal` / 24 `elite`
  / 8 `boss` (`docs/ID_REGISTRY.md` Monsters totals, `docs/WORLD_PLAN.md` region table) — the
  same three numbers CLAUDE.md's current design state already cites, not re-derived here.

Region ordering and boundaries are `docs/WORLD_PLAN.md`'s alone; this doc never restates a
region's map/level-band details, only which `mob_NNN` range fills its bucket.

## 6. Rewards — cosmetic-first, economy-safe

Two reward kinds, deliberately unequal in how settled they are:

- **Titles (cosmetic, no economy interaction).** See §7. Safe to design and land now — a title
  has no `shards`/`exp` value and cannot be vendored, traded, or power-relevant (P2 "no trap
  builds" cuts both ways: no trap *rewards* either).
- **One-time `exp`/`shards` grants (small).** Two tiers:
  - *Per-species first `logged` kill* — this is **not a new faucet**. `10_systems/DROPS.md` §8
    and `10_systems/LEVELING.md` §4 already reserve a "first kill of each bestiary species"
    line inside the existing **Other ≈5%** `exp` bucket; this doc is simply where that grant is
    triggered (on the `unseen→logged` transition, §3) and tracked (§7) so DROPS §8's promise has
    an owner. Magnitude stays LEVELING §4's, not re-derived here.
  - *Set-completion grants* (a region's tier fully `logged`, a region fully `logged`, or the
    global 150/150 capstone) — modest one-time `shards`, styled on
    `10_systems/QUESTS.md` §5's `side`-quest budget (the `elite`-kill `shards` mean at the
    set's top level, per `10_systems/DROPS.md` §3) so a full-region clear pays roughly one good
    side quest's worth, not a windfall. **This is a genuinely new line item against
    `10_systems/ECONOMY.md` §1's closed faucet list ("Monster drops / Quest rewards /
    Vendoring... No other faucet exists.")** — flagged rather than silently added; see Open
    Questions. Until `10_systems/ECONOMY.md` blesses it, set-completion rewards ship as
    **titles only**, no `shards`.

No reward here ever grants an item, a stat point, or a repeatable payout — one-time per
character per milestone, same non-repeatable posture as `10_systems/QUESTS.md` §7.

## 7. Titles — a cosmetic concept owned by this doc

A **title** is a short cosmetic display string a character can hold and (per a future
character-sheet/social display doc — not yet authored) equip for others to see. This doc fixes
**which milestones grant a title slot and how many slots exist**; it does not fix the display
strings themselves (Phase D content/flavor pass names them, exactly as monster `flavor` text is
authored, not this doc) nor how/where a title renders (HUD/`UI_ART_SPEC.md`'s, §9).

Title slots (17 total, all one-time):
- **8 boss titles** — one per region boss, granted on that boss's first `logged` kill (e.g., a
  title tied to defeating Cindermaw). Named by Phase D alongside that boss's flavor text.
- **8 region-capstone titles** — one per region, granted when every `mob_NNN` in that region's
  block (all tiers) reaches `logged`.
- **1 global capstone title** — granted at 150/150 `logged` across both islands.

No GLOSSARY token exists yet for "title" as a shared vocabulary family (it is currently scoped
entirely to this doc); if a future doc needs to reference "the player's currently equipped
title" as a shared concept, that token should be proposed under GLOSSARY's **Provisional**
section rather than invented ad hoc — flagged in Open Questions, not resolved here.

## 8. Authority (per `10_systems/PERSISTENCE.md` §1)

| Data | Tag | Note |
|---|---|---|
| Discovery state (`unseen`/`sighted`/`logged`) per `mob_NNN` | `server` | One-way ratchet; client may not self-advance it (`10_systems/PERSISTENCE.md` §7 posture). |
| Revealed-drop-row flags per `mob_NNN` (§4) | `server` | Derived from server-authoritative loot grants (`10_systems/DROPS.md` §9); never client-set. |
| Claimed-reward flags (first-kill grant, set-completion grant, title-slot grant) | `server` | Same one-time-grant contract as `10_systems/QUESTS.md` §9 turn-ins; prevents re-claiming on relog. |
| Completion percentages shown in the log (§5) | `server` (computed) | Pure arithmetic over the rows above; not independently stored truth, but read through the same facade. |
| Log UI state: sort order, filter (by region/tier/element/completion), collapsed/expanded groups | `client` | Local presentation only, same class as `10_systems/HUD.md`/`10_systems/QUESTS.md` UI prefs (`10_systems/PERSISTENCE.md` §3). |

No field above needs a fourth tag; every one fits `server` or `client` cleanly (no shared/predicted
state here — a log is not a real-time simulation surface).

## 9. UI hook (deferred)

The log opens as a `frame_window` toggle window, the same family as Inventory/Skills/Quest Log
(`10_systems/HUD.md` §1's frame-usage table already lists `frame_window` for exactly that class
of window; this doc does not add a new frame). Visual layout, list/grid choice, per-entry card
art, and exact colors for `sighted` vs `logged` states are `40_assets/UI_ART_SPEC.md`'s —
**locked** (CLAUDE.md Law 5) — and `10_systems/HUD.md`'s toggle-window conventions; this doc
cites both and designs neither. Any new UI token the log needs (e.g., a distinct locked/masked
row treatment for §4) goes through `UI_ART_SPEC.md`'s amendment channel, not this file.

## Open Questions

- **Set-completion `shards` grants are not yet a blessed faucet.** `10_systems/ECONOMY.md` §1
  enumerates exactly three faucets and states "no other faucet exists"; §6's own rules assume a
  closed list for inflation guardrails. This doc's §6 set-completion `shards` idea needs an
  explicit `10_systems/ECONOMY.md` amendment (a fourth faucet line, one-time and capped like
  the reallocation-fee treatment) before Phase D wires it. Until then, ship titles only for set
  completion; the per-species first-kill `exp` grant is unaffected (it is already budgeted inside
  LEVELING §4's existing Other-5% bucket, not a new faucet).
- **No shared GLOSSARY token for "title" yet.** This doc scopes the concept locally (§7);
  propose `title` (or similarly-named) as a GLOSSARY Provisional entry if/when a character-sheet
  or social-display doc needs to reference "equipped title" as shared vocabulary. Not resolved
  here per CLAUDE.md Law 4/5 (this doc may propose, not silently add to GLOSSARY).
- **Boss/region/global title display strings** are unauthored placeholders (§7); Phase D names
  all 17 alongside each region's flavor-text pass. Which doc/role owns naming them (region
  content batch vs. a dedicated title-flavor pass) is unresolved.
- **Sighting range definition.** §3's `sighted` state keys off "aggro/render range," but the
  exact radius/trigger (aggro radius per `10_systems/AI_BEHAVIOR.md` vs. a separate always-on
  sight radius) is not fixed here; default assumption is the monster's own aggro radius, so no
  new per-monster field is needed, but this should be confirmed against
  `10_systems/AI_BEHAVIOR.md` before Phase D relies on it.
- **Save-data shape for the three progress flags (§8)** — discovery state, revealed-drop flags,
  and claimed-reward flags need a concrete field layout inside the `GameState` facade; that
  layout is `30_engineering/ENGINEERING_STANDARDS.md`'s once authored (per
  `10_systems/PERSISTENCE.md` §5), not designed here.
