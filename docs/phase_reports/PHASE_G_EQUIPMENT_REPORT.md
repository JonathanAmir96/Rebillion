# PHASE_REPORT — Phase G (Equipment System v2)

Status: **complete**. 3 sub-agents (2 Opus, 1 Sonnet) + producer gate work; 1 new system doc,
4 doc revisions, 2 registry/vocabulary extensions. Design prose only — no game code, no content
YAML, no locked file touched (ART_BIBLE.yaml, UI_ART_SPEC.md, ENGINEERING_STANDARDS.md —
read-only citations only). All files passed: forbidden-token scan (VALIDATION.md §1), `## Open
Questions` ending, US spelling.

## Files changed (by dispatch group, per docs/60_agents/roles/ORG.md routing)

- **G-slots (ROLE_SYSTEMS_ARCHITECT, Opus — cross-system blast radius):**
  - `10_systems/ITEMS.md` — slot roster v2: **eleven slot tokens across ten worn positions**.
    Added class-agnostic off-hand `shield` and dual-position `overall` (fills `body`+`legs`,
    §2.1 reciprocal auto-swap; one strong two-slot base vs one item's affix budget as its
    stated balance identity). MapleStory mapping table (§2.2): cap/topwear/bottomwear/shoes/
    gloves/cape/pendant/ring map onto existing tokens; earrings, face/eye accessories, and
    extra ring slots **rejected** (silhouette per ART_BIBLE `silhouette_first` at the 32px
    player frame, UI slot/icon budget per UI_ART_SPEC, stat-budget dilution of COMBAT_FORMULA
    §15's `power_ref`) — future-arc candidates, not bans. §8 armor weights rebalanced to six
    slots (`body .24 · legs .20 · head .16 · shield .14 · boots .13 · gloves .13`, Σ = 1.0;
    `w[overall] = 0.44`) — the full-set `K(L)/3` target is unchanged, checksum table
    recomputed and verified cell-by-cell. New §3.1 general-vs-class law: weapons stay
    line-locked, all shared gear stays class-agnostic (SCOPE.md law preserved); line-themed
    gear = flavor + stat lean; optional `req_line` lock permitted **only** on job-advancement
    rewards and boss uniques. No section renumbering — external ITEMS §7–§10 citations stay
    valid.
- **G-scrolls (ROLE_SYSTEMS_ARCHITECT, Opus — ENHANCEMENT/ECONOMY/DROPS all consume it):**
  - `10_systems/SCROLLS.md` (new) — single owner of gear-modification scrolls. Ownership seam:
    ENHANCEMENT owns base-line growth (emberstone +1..+9), SCROLLS owns affix-line change;
    neither touches rarity or line count. Two kinds — `aspect` (reroll one line at §10 menu
    magnitude) and `temper` (raise one line by an anchor-based step) — both strictly inside
    ITEMS §10's per-line pe cap and rarity budget: scrolls redirect/perfect a drop toward its
    existing ceiling, never raise it. Success tiers `steady` 100% / `bold` 60% (witnessed
    reroll) / `perilous` 30% (two candidates); **failure never harms the item** (P2 stance
    matches ENHANCEMENT — no destruction/downgrade anywhere in the tree); no pity at launch
    (item is never at risk; OQ filed). Acquisition: drops per DROPS §5 shapes, quest rewards,
    and a `steady`-only vendor shelf — an explicitly sink-dominant `shards` loop. Full
    PERSISTENCE §1 authority table.
  - `10_systems/ENHANCEMENT.md` — four surgical reconciliation edits: SCROLLS seam sentence,
    References entry, de-hardcoded slot count ("every equip slot"), `shield`/`overall` rows in
    the §4 scaling table. No mechanic touched.
- **G-schema (ROLE_SYSTEMS_ARCHITECT, Sonnet — field extension inside a fixed contract):**
  - `20_schemas/item.schema.md` — slot enum → eleven tokens; optional equip `req_line` field
    (hard-gated off weapons, warn-gated to uniques/advancement rewards); use-row scroll fields
    `scroll_kind`/`scroll_tier`/`slot_family` present iff the row id is in the gear-mod block
    (`effects: []` on those rows — the mechanic is SCROLLS.md's); file-convention and
    validation-rule updates; stale "nine slots" quote fixed.
- **Producer (gate commits):**
  - `docs/ID_REGISTRY.md` — extension in its own commit, no minted ID moved: `item_equip`
    shield `0231`–`0240` + overall `0241`–`0250` (T1–T10 grids, 6 in-arc tiers authored per
    the v2 plan) carved from reserved growth; `item_use` range extended `0001`–`0100` with
    gear-mod scroll block `0061`–`0078` (18 SKUs, layout convention in SCROLLS §5) +
    `0079`–`0090` scroll growth. Boss-unique mapping `0199+2n` untouched.
  - `docs/00_vision/GLOSSARY.md` — `## Provisional` additions: `shield`, `overall`, `req_line`,
    and the scroll vocabulary (`aspect`/`temper`, `steady`/`bold`/`perilous`,
    `scroll_kind`/`scroll_tier`/`slot_family` + family values); equipment-slots line now points
    at ITEMS §2's revised roster (no silent canon change).

## Gate actions taken (orchestrator)

- Fixed the slot roster, weight table, scroll taxonomy, and ID allocations **before** dispatch
  (producer pre-computed manifest, ORG.md demotion rule) so both Opus seats worked against the
  same numbers; §8 checksum values verified against `round(w·K(L)/3)` independently.
- Commit discipline: one concern per commit — registry extension, GLOSSARY provisionals, ITEMS
  revision, scroll system + ENHANCEMENT seam, schema extension, gate bookkeeping.
- Declined without prejudice: hard class-locking beyond advancement rewards/boss uniques
  (contradicts SCOPE.md — filed as an owner Open Question, not decided); new accessory slots
  (earrings et al. — rejected with rationale, future-arc candidates).

## Open Questions rollup (headline items; full entries live in each doc)

- **ITEMS**: tenth affix-bearing slot lifts a full character's affix pe ~+11% over the
  nine-item assumption behind COMBAT_FORMULA §15 `power_ref` — flag for that doc's `mult m`
  retune OQ (never retune `W`/budgets in ITEMS). Two-handed fantasy (`bow`/`staff`) vs
  `shield` — default: all lines may equip. SCOPE.md's authoritative equip count (~86)
  predates the +12 planned SKUs — owner count bump needed. `overall` tier coverage
  (default: full grid, Phase D may thin).
- **SCROLLS**: ECONOMY §4.1 needs `steady`-scroll price rows at the D gate (sink table hook
  already exists). Soft pity for `perilous` fails — deferred. Duplicate-line rerolls —
  default allowed (cap-bounded). Directed temper — future SKU in reserved `0079`–`0090`.
  Exact drop/quest placement — Phase D content against DROPS/QUESTS shapes.
- **Schema**: `req_line`-outside-uniques check fully verifiable only once Phase D quest
  content lands; utility/return-scroll teleport mechanic remains unowned (the gear-mod half
  of that old OQ is now resolved by SCROLLS.md).
- **Owner decisions (blocking nothing this wave):** class-lock expansion; SCOPE count bumps
  (equip ~86 → ~98, use ~30 → ~48 once scroll SKUs author in Phase D).

## Validation

VALIDATION.md §1 token scan (case-sensitive whole words, repo-wide minus the exempt file):
clean. §7 ending check: every touched doc ends with `## Open Questions`. §2–§6 are
content-file checks — not applicable to this doc-only wave beyond the cross-reference
spot-checks above (ITEMS↔ENHANCEMENT↔SCROLLS↔schema↔ID_REGISTRY reconciled). US-spelling
spot scan: clean.

## Open Questions

- Phase letter: this wave continues the F precedent of lettered addendum waves past E
  (CLAUDE.md names A→E). Treated as addendum wave G; renumber only if a master-brief revision
  does.
