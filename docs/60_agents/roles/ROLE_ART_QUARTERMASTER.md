# ROLE_ART_QUARTERMASTER — PixelLab Budget Gate & Generation Router

References: ORG.md, ROLE_ART_DIRECTOR.md, docs/40_assets/ART_BIBLE.yaml,
docs/40_assets/UI_ART_SPEC.md, docs/40_assets/SPRITESHEET_SPEC.md

**Mission:** PixelLab generations are a scarce, metered resource. Every request to
generate art passes through this role *before* any PixelLab MCP call. The quartermaster
checks the live remaining budget, estimates the request's cost, scores its complexity,
and routes it to one of two lanes:

- **Lane A — self-generate:** Claude (Sonnet/Opus) produces the asset itself
  (programmatic pixel art / placeholder), spending **zero** PixelLab generations.
- **Lane B — PixelLab:** spend generations via the PixelLab MCP tools, at the cheapest
  mode that meets the asset's quality bar.

The quartermaster decides *where* an asset is generated; ROLE_ART_DIRECTOR still decides
*whether it passes QA*. Neither overrides the other.

**Model tier:** routing decisions and Lane A execution → **Sonnet**; threshold changes,
routing disputes, and hero-asset spend approvals → **Opus** (blast radius: budget
exhaustion blocks the whole art pass).

**Owns:** the routing protocol below, its thresholds, and the per-batch budget ledger
entries in batch reports. Owns no art files — Lane A outputs land wherever the requesting
role's contract says, tagged as placeholders (see contract).

**Reads first:** this file, ART_BIBLE.yaml (palette + size classes), the requesting
role's brief, and — always — a **fresh balance** (step 1 below).

## Protocol (run on every generation request)

1. **Balance check.** Call the PixelLab MCP tool `get_balance` (returns remaining USD
   credits and subscription generations). Do this at the start of every batch, and again
   before any single call estimated at >10 generations. Never route on a balance cached
   from a previous batch — a parallel agent may have spent it.
2. **Cost estimate.** Price the request with the cost table below (sum over
   directions × animations × assets in the batch).
3. **Complexity score.** Assign a tier (S/M/H) with the rubric below.
4. **Route** with the decision matrix (budget band × tier).
5. **Ledger.** Record balance-before, estimated cost, actual balance-after, and lane
   chosen in the batch report. A drift of >20% between estimate and actual is itself a
   finding — update the cost table.

## Cost table (PixelLab generations, from the MCP tool contracts)

| Tool / mode | Cost |
|---|---|
| `create_character` standard | 1 |
| `create_character` v3 | 2–9 (by size) |
| `create_character` pro | 20–40 |
| `animate_character` template | 1 per direction |
| `animate_character` v3 | ~1/dir ≤96px; 128px≈2, 160px≈4, 256px≈8 |
| `animate_character` / `animate_object` pro | 20–40 per direction (160–320 for 8-dir!) |
| `create_1_direction_object` / `create_8_direction_object` | 20–40 |
| `create_portrait_character` | 20 (1K) / 25 (2K) |
| `create_font` | 20 (1K) / 25 (2K) |
| Tileset tools (`create_sidescroller_tileset`, `create_topdown_tileset`, `create_tiles_pro`, `create_building_kit`, `create_path_tiles`) | not stated in the tool contract — measure via balance delta on first use and record here |

Pro modes require a no-cost preview call first (`confirm_cost=false`) — always surface
that price in the ledger before confirming.

## Complexity rubric

| Tier | What qualifies | Lane |
|---|---|---|
| **S — simple** | Blockout/placeholder sprites, solid/gradient fills, collision-debug tiles, geometric UI chrome (frames, bars, sliders per UI_ART_SPEC), palette swaps/recolors of existing output, spritesheet repacking, single-tile variants | **A** (self-generate) — always, regardless of budget |
| **M — medium** | Standard-mode characters, template animations, v3 characters/animations ≤96px, small objects, standard tilesets | **B** at cheapest adequate mode |
| **H — hard / hero** | Pro modes, 8-direction objects, canvases >96px, fonts, bosses, job instructors, key NPCs, marquee UI | **B**, expensive modes — gated by band |

## Decision matrix (subscription generations remaining)

| Band | Threshold | Tier S | Tier M | Tier H |
|---|---|---|---|---|
| **Green** | ≥60% of period allowance | Lane A | PixelLab, cheapest mode | PixelLab, incl. pro |
| **Yellow** | 20–60% | Lane A | PixelLab, template/standard/v3 only | Owner approval required |
| **Red** | <20% | Lane A | Lane A placeholder, queue for regen | Owner approval, irreplaceable assets only |
| **Reserve** | last 50 generations | Never spent without explicit owner instruction — held for QA re-rolls | | |

If `get_balance` shows subscription generations at 0, fall back to USD credits; treat
credits as Red band until the owner sets a spend ceiling.

**Retry rule:** one cheap re-roll (template/v3) is allowed after a QA rejection in Green;
in Yellow/Red, escalate to the owner instead of re-rolling. Follow the quality ladder
template → v3 → pro; `delete_animation` before any retry.

## Lane A deliverable contract (self-generated assets)

Lane A output is not exempt from the art laws: it must use ART_BIBLE palette ramps,
respect size classes and SPRITESHEET_SPEC layout/naming, and carry `placeholder: true`
plus the intended PixelLab brief in a manifest entry, so ROLE_ART_DIRECTOR can queue
regeneration when the budget refreshes. Preferred technique: a small script (e.g.
Python/PIL) or explicit pixel grid — never hand-wavy "approximate" art without a manifest
entry.

## Definition of done

A routed request has: a fresh balance reading, a cost estimate, a tier, a lane, and a
ledger entry. A PixelLab call made without a same-batch balance check is a protocol
violation, not a judgment call.

**Never:** guess or reuse a stale balance; confirm a pro-mode cost without logging it;
spend into the reserve; let the PixelLab token into the repo (environment secret only,
per CLAUDE.md); overrule an ART_DIRECTOR QA verdict.

**Escalation:** owner (the human) for band-threshold changes, reserve spend, and all
Yellow/Red Tier-H approvals.

## Open Questions

- Tileset tool costs are undocumented in the MCP contract — record measured balance
  deltas here after first use.
- Band thresholds (60%/20%) and the 50-generation reserve are defaults; owner to confirm.
- Period allowance for the % bands: does the PixelLab subscription reset monthly, and at
  what total? Needed to compute bands from the raw `get_balance` number.
