# COSMETICS.md — Cosmetics: Categories, Earning, and the Appearance Layer

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 00_vision/SCOPE.md,
10_systems/MONETIZATION.md, 10_systems/ITEMS.md, 10_systems/INVENTORY.md, 10_systems/HUD.md,
10_systems/COLLECTIONS.md, 10_systems/ECONOMY.md, 10_systems/social/GUILD.md,
10_systems/social/RAID.md, 10_systems/PERSISTENCE.md, 20_schemas/item.schema.md,
40_assets/ART_BIBLE.yaml, 40_assets/UI_ART_SPEC.md, docs/ID_REGISTRY.md, docs/VALIDATION.md

Owner doc for **cosmetics** — the game's prestige/social-flex layer: what a cosmetic is (the four
categories), the `item_cosmetic_NNNN` content shape, how each cosmetic is **earned**, and how it is
**equipped and displayed** (the appearance loadout). The no-pay-to-win charter that binds every
cosmetic is `10_systems/MONETIZATION.md`'s (MON-001) and `00_vision/PILLARS.md`'s anti-pillar —
cited, never restated: **a cosmetic carries no stats, ever.** Raid-cosmetic prices are
`10_systems/ITEMS.md` §13's; guild-level unlock pacing is `10_systems/social/GUILD.md` §9's;
collection-title grants are `10_systems/COLLECTIONS.md` §7's; ID ranges are
`docs/ID_REGISTRY.md`'s. This doc consumes all of those and owns only the cosmetic system itself.

## 1. Scope & the zero-stat law

- Everything in this doc is **earned in-world**. The future real-money store
  (`10_systems/MONETIZATION.md`, server-deferred) sells into the **same appearance layer** (§5)
  but mints none of this doc's IDs and is governed entirely by MON-001; nothing here creates a
  purchase path.
- **Zero stats, zero mechanics.** A cosmetic row may carry no GLOSSARY stat token, no effect op,
  no combat- or economy-relevant field. Wearing, removing, or owning any cosmetic changes
  rendering and display text only. (Proposed as a hard validator check — see Open Questions;
  `docs/VALIDATION.md` is producer-owned, so the rule is proposed there, not written here.)
- **Never currency.** Cosmetics are character-bound: no vendor `buy`/`sell`, no trade, no market
  listing, no `shards` value — the `10_systems/ECONOMY.md` §1 closed faucet list is untouched by
  this system.

## 2. Categories (four)

| Category token | What it is | Renders where |
|---|---|---|
| `title` | A short display string shown with the character's name | Nameplate/profile (§6) |
| `dye` | A recolor of the worn armor set (or active `skin`), selecting among ART_BIBLE-approved palette ramps | Character sprite |
| `skin` | An appearance override for the `weapon` or the armor set (an outfit) — the worn gear keeps supplying all stats | Character sprite |
| `crest_flourish` | A decorative border/ornament layer on the guild crest | Crest render contexts (`40_assets/UI_ART_SPEC.md`'s sizes) |

The four tokens are proposed in `00_vision/GLOSSARY.md` **Provisional** (owner: this doc). `title`
was already Provisional via `10_systems/COLLECTIONS.md` §7; this doc is the character-display
consumer that entry's promotion condition waits on — promotion of all four is a phase-gate call
(Open Questions).

**Titles come in two grant forms, one display system.** Raid titles are `item_cosmetic` SKUs
(bought with `raid_token`s, §4); the 23 collection titles are server-side grant flags
(`10_systems/COLLECTIONS.md` §7–§8, not items). Both feed the same owned-title set and the same
single equipped-`title` slot (§5) — a player never sees two title systems.

## 3. Content shape (`item_cosmetic_NNNN`)

Cosmetic content is authored as one batch table, `50_content/items/cosmetics.yaml`
(`id: item_table_cosmetics`), following `10_systems/ITEMS.md` §12's table convention;
`20_schemas/item.schema.md` formalizes the row when the first cosmetic batch is authored (flagged
there). Row shape owned here:

```yaml
items:
  - id: item_cosmetic_0001          # docs/ID_REGISTRY.md cosmetic block, immutable
    name: ...                       # US spelling; client
    category: title                 # title | dye | skin | crest_flourish (§2)
    applies_to: nameplate           # skin: weapon | outfit; dye: outfit; title: nameplate;
                                    # crest_flourish: crest — the render target, one per category
    source: raid                    # raid | guild | event (§4; informational, cross-checked
                                    # against the ID sub-block)
    flavor: "..."                   # ≤2 sentences, optional
```

No `price`, no `stats`, no `effects`, no `stack` — a cosmetic is an **unlock entry**, not an
inventory object: owning one sets a flag in the character's cosmetic set (§7); it occupies no
`10_systems/INVENTORY.md` tab slot and that doc needs no change for this system.

## 4. Earning (the only mints)

ID sub-blocks per `docs/ID_REGISTRY.md` (cosmetics block, owner this doc):

| Channel | IDs | Rule owner |
|---|---|---|
| **Raid** — Raid Quartermaster, `raid_token`-bought; one `title` + one cosmetic effect (`skin`-family) per raid | `item_cosmetic_0001`–`0008` (first four raids) + `0065`–`0066` (`raid_orrery`, appended 2026-07-24 — the channel is deliberately discontiguous, `docs/ID_REGISTRY.md`) | Prices `10_systems/ITEMS.md` §13; token faucet `10_systems/social/RAID.md` §6 |
| **Guild** — guild-level unlocks (levels 3–5) and crest options | `item_cosmetic_0009`–`0032` | Pacing `10_systems/social/GUILD.md` §9; crest data rules `GUILD` §5 |
| **Event / charter** — live-ops/seasonal grants; assigned 2026-07-24 to the Wayfarer's Charter season lanes (up to 6 per season: free capstone + gilt pieces) | `item_cosmetic_0033`–`0048` | Lane rules `10_systems/BATTLE_PASS.md` §5 |
| **Capsule** — Cogwork Capsule gacha exclusives (tickets earnable free + PA-001 real-money packs) | `item_cosmetic_0049`–`0064` | Pool/odds `10_systems/GACHAPON.md` §5; PA-001 caps §1 there |

The capsule channel is the one place cosmetic *ownership* can trace to a real-money purchase
(a PA-001-capped ticket, `10_systems/MONETIZATION.md` amendment log); the cosmetics themselves
still obey every rule here — zero stats, character-bound, no vendor/trade/market value (§1).

Collection titles (`10_systems/COLLECTIONS.md` §7's 23) are grant flags, not IDs, and sit outside
these blocks by design (§2). Guild-unlocked cosmetics unlock for **members of the qualifying
guild**: the unlock is held by the character once earned and — decision, P2's no-clawback posture,
matching `guild_contribution`'s monotonicity — is **kept if the member later leaves**, except
`crest_flourish` items, which only *render* while the character is in a guild (there is no crest
to decorate otherwise).

## 5. The appearance loadout (equip rules)

The appearance layer reserved by `10_systems/MONETIZATION.md` §3.1 lands here for the earned side:
a set of zero-stat display slots rendered **above** the `10_systems/ITEMS.md` §2 equipment slots in
the paper-doll order. Loadout slots, one item each, all optional:

| Loadout slot | Accepts | Note |
|---|---|---|
| `title` | one owned title (either grant form, §2) | exactly one shown; swapping is free and instant |
| `skin` (weapon) | `skin` with `applies_to: weapon` | must match the worn weapon's type family for silhouette honesty (P1) — flagged detail, Open Questions |
| `skin` (outfit) | `skin` with `applies_to: outfit` | overrides the armor set's look as one outfit |
| `dye` | one `dye` | recolors the armor set or active outfit skin |
| `crest_flourish` | one `crest_flourish` | renders only while guilded (§4) |

Equipping/unequipping is free, instant, anywhere (a cosmetic is never a build decision — P2).
The worn equipment keeps supplying every stat; a cosmetic slot left empty simply shows the gear.
Paper-doll layer ordering must be fixed before the Phase E coding pass locks the character render
stack (`10_systems/MONETIZATION.md` §3.1's standing seam — now anchored to this doc's slot list;
Open Questions).

## 6. Display surfaces

- **Nameplate/profile:** the equipped `title` renders with the character name; layout is
  `10_systems/HUD.md`'s (which does not yet reserve a nameplate/title region — flagged there
  by reference, Open Questions here).
- **Character sprite:** `skin`/`dye` render in place of / over the worn gear's look; sprite
  conventions are `40_assets/SPRITESHEET_SPEC.md`'s and palette legality is
  `40_assets/ART_BIBLE.yaml`'s (locked — dye ramp lists go through its amendment channel,
  Open Questions).
- **Crest contexts:** `crest_flourish` renders wherever the crest does, at
  `40_assets/UI_ART_SPEC.md`'s four sizes (locked — flourish art slots go through its amendment
  channel).

## 7. Server Dependency

Cosmetic **ownership** (the owned set), the **appearance loadout**, and all grant events (raid
purchase, guild-level unlock, event grant, collection-title flag) are `authority: server`
(`10_systems/PERSISTENCE.md` §1–§2; `00_vision/PILLARS.md` P6) — a client cannot self-grant a
cosmetic or equip one it does not own. **Rendering** the loadout is `client`. In the interim solo
build the system ships live-but-narrow: collection titles work fully offline
(`10_systems/COLLECTIONS.md` is solo-live), while raid and guild cosmetics are dormant with their
source systems (`10_systems/social/RAID.md` §8, `10_systems/social/GUILD.md` §Server Dependency).
The `GameState` facade (`10_systems/PERSISTENCE.md` §5) carries the owned-cosmetic set and the
loadout so the live-server swap changes no calling code.

## Open Questions

- **GLOSSARY promotion:** `title` · `dye` · `skin` · `crest_flourish` are Provisional (§2);
  promote (or rename) at the next phase gate once the first cosmetic content batch consumes them.
  `title`'s original promotion condition (`10_systems/COLLECTIONS.md` §7 — "a character-sheet or
  social-display doc consumes it") is now met by this doc. Owner: GLOSSARY gatekeeper.
- **VALIDATION rule proposal (producer-owned — proposed, not edited):** add a check that any
  `item_cosmetic_*` row (and the future `cosmetics.yaml` table) contains no stat token, no effect
  op, and no price field — the §1 zero-stat law as a build failure, per P5. Owner:
  producer / `docs/VALIDATION.md`.
- **Dye technical model:** whether a `dye` is a palette-ramp swap (cheap, ART_BIBLE-native) or a
  hue shift, and the approved ramp list per armor family — needs an `40_assets/ART_BIBLE.yaml`
  amendment (locked file; Agent-3 channel). No dye content can be authored before that lands.
  Owner: ROLE_ART_DIRECTOR.
- **Nameplate/title region:** `10_systems/HUD.md` reserves no nameplate/title layout yet (same
  standing gap as party plates, its Open Questions); this doc supplies only the data contract
  (equipped `title` string). Owner: HUD.md.
- **Weapon-skin type gating (§5):** default requires a weapon `skin` to match the worn weapon's
  type (a `blade` skin never renders over a `staff`) for silhouette honesty (P1); whether
  cross-type skins are ever acceptable is open. Owner: this doc with
  `40_assets/SPRITESHEET_SPEC.md`.
- **Event block policy (`0033`–`0048`):** grant mechanics for seasonal/live-ops cosmetics are
  deferred to the live-service arc (no live-ops calendar exists in this run). Owner: this doc at
  that arc.
- **Premium separation:** the future `gleam` store never mints from this doc's earned blocks —
  a premium cosmetic would claim a new reserved block in `docs/ID_REGISTRY.md` in a new commit,
  keeping earned prestige legible (you can trust a Voidtide title was cleared, not bought).
  Confirm at the arc where MONETIZATION goes live. Owner: this doc with
  `10_systems/MONETIZATION.md`.
- **Character-bound vs account-bound:** launch default is character-bound (matches every other
  unlock; `10_systems/PERSISTENCE.md` per-character posture). An account-wide cosmetic wardrobe is
  a floated future nicety, deferred with the account system. Owner: this doc with PERSISTENCE.
