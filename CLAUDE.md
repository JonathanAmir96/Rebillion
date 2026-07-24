# CLAUDE.md — Working Rules for This Repository

Rebillion is a **design-documentation tree** for a 2D side-scrolling MMORPG platformer
(Godot 4.3+ target). This run produces docs + machine-loadable YAML content only — no game
code, no generated art. Read `README.md` for the tree map and
`docs/phase_reports/`, `memory.md`, and the `memory/` Memory Bank for current generation state.

## Laws (apply to every edit, human or agent)

1. **Tokens are law.** Use only `docs/00_vision/GLOSSARY.md` tokens for stats, resources,
   currency, and shared enums. The banned legacy-genre terms are listed in
   `docs/VALIDATION.md` §1 — that file is the only place they may appear.
2. **Single source of truth.** Rules live in one system doc; entity shapes in one schema;
   content files hold values + references only. Link, never restate.
3. **IDs are immutable** and must sit inside their `docs/ID_REGISTRY.md` block. Extend
   ranges in a new commit if needed; never renumber.
4. **Flag, don't guess.** Unknown token/rule/number → add to the owning doc's
   `## Open Questions` (every doc ends with that section).
5. **Change-controlled files:** `docs/40_assets/ART_BIBLE.yaml`,
   `docs/40_assets/UI_ART_SPEC.md`, `docs/30_engineering/ENGINEERING_STANDARDS.md`
   (owner Agent-3 / master brief). Agents do not edit them on their own initiative —
   proposals go through the Open-Questions channels. Edits land only on **explicit owner
   direction** and every such edit is recorded in the file's `amendments` log
   (`AB-`/`UA-`/`ES-` ids) with date + directive (precedents: AB-001, UA-001, ES-001).
6. **Validate before landing:** the checks in `docs/VALIDATION.md` run on every content
   batch (see `tools/` once the validator lands). US spelling everywhere.

## Current design state

- Five islands, two authored arcs (Lv 1–82; game cap 300, initial design). **Arc 1:**
  Emberfoot Isle (training, maps 001–016) → Harborwind Ferry (paid) → Harthmoor Isle, a
  Victoria-style **ring** (Millbrook south hub ↔ Verdant ↔ Gloomwood ↔ Ashfall ↔ Tidewatch ↔
  Millbrook) around the Clockwork Ruins center, with Sunken Depths as a coastal spur.
  **Arc 2 (Lv 40–80):** the Deepway — a 3-map underground passage from Cindershelf,
  level-gated Lv 40 — surfaces on Frostpeak Isle (40–55); Arcane Reach (53–68) and
  Voidshore (66–80) complete the far isles, linked by the paid, scheduled **longship**
  network from Tidewatch Port (2–3 min real-time sails). Totals: 333 maps, 234 monsters
  (178/45/11), 11 bosses, 5 **raids** (`raid_undervault`/`raid_mainspring`/`raid_deepfrost`/
  `raid_orrery`/`raid_voidtide` — the instanced co-op runs; owner doc
  `docs/10_systems/social/RAID.md`; bands 15–22 · 32–40 · 45–55 · 56–69 · 70–80, the arc-2
  three tiling Lv 45–80 with no gap since `raid_orrery` landed 2026-07-24 reusing R10's
  Shattered Orrery maps and boss — only its bonus room `map_329` is a new ID).
  Town travel is the paid Harthmoor Coachworks (shards) — no free warps. Each job line has a
  home ring town with its instructor (Bulwark→Cindershelf, Keeneye→Tidewatch Port,
  Weaver→Mossmere, Flicker→Millbrook); maps follow the WORLD_PLAN monster-gradient law.
  Terrain is Maple-style footholds + painted terrain chunks (ART_BIBLE amendment AB-001;
  movement rules in MAP_TRAVERSAL.md).
- Wide **junction fields** (owner directive 2026-07-25): four extra-wide crossroads `field` maps
  (`map_330`–`map_333`, ~7–8 screens), one hung additively off the Millbrook / Verdant / Tidewatch /
  Ashfall ring roads (three existing maps each); no existing edge moved. Width is the recorded
  MAPS_SYSTEM §2 junction sub-case; IDs sit in a second ID_REGISTRY map extension range.
- Combat carries a skill-chaining combo layer (owner-directed 2026-07-24,
  `docs/10_systems/COMBO_SYSTEM.md`): `combo_momentum`/`combo_burst`, tier-gated by job tier,
  consumed at COMBAT_FORMULA §2 step 8 inside §15's damage envelope; HUD §7.1 draws the counter.
- Jobs: novice → 1st at Lv 8 → 2nd at Lv 40 **branches** into a permanent specialization —
  bulwark: Ironbrand/Stoneguard/Warcaller · keeneye: Pathstalker/Sureshot · weaver:
  Runeweaver/Cindercall/Frostbind · flicker: Duskstep/Wildcard (rosters in
  `docs/10_systems/JOBS.md`); 3rd-tier jobs named-and-reserved for future arcs.
- Pacing (owner ruling 2026-07-24, `docs/10_systems/LEVELING.md`): Lv 40 ≈ 30 h · Lv 80 ≈
  166 h · Lv 100 ≈ 300 h of `/played`; curve `kills_per_level(L) = round(20 + 6.6·L + 0.2·L²)`.
- Social/economy systems are designed but server-deferred; the interim build is solo with a
  server-authoritative boundary (`docs/10_systems/PERSISTENCE.md`).
- Raids are staged co-op runs (owner-directed 2026-07-24,
  `docs/10_systems/social/RAID.md`): three stages → finale arena → **bonus room**, each raid
  carrying a distinct *signature* mechanic (haul/beat/thaw/orbit/tide) and three different stage
  patterns. One **30-min run clock** covers the whole run with the boss's 12-min enrage nested
  inside it; the bonus room runs a separate 90-s clock over one-shot `reactor` nodes rolling a
  chance table (gear-mod scrolls, consumables, an extra `raid_token`). **One party per raid per
  channel** — a claim on `(channel, raid_token)`, MapleStory-style channel-hopping, but each
  party still gets a private instance (`docs/70_integrations/WORLD_CHANNELS.md` §2.1).
- Live-ops (owner addition 2026-07-24): the **Wayfarer's Charter** battle pass
  (`docs/10_systems/BATTLE_PASS.md`) — 30-day seasons (`season_NNN`), free + gilt reward
  lanes, gilt bought with **shards** on a **level-banded price ladder** (2,500 at Lv 1–9 →
  60,000 at Lv 62+, ECONOMY §4.4, charged once at purchase against `level` at that moment;
  owner directive 2026-07-24 replacing the earlier flat 6,000 — a flat fee decayed to ≈14 min
  of income by Lv 70 and left the free/gilt split with no decision in it, contradicting
  ECONOMY §6's own "sinks scale with level" guardrail); real money never touches the
  charter; **cosmetics are the gilt lane's headline offer**, minted from the
  `item_cosmetic` Event/charter sub-block via the COSMETICS.md appearance layer. Charter
  tokens provisional in GLOSSARY pending the next gate.
- Monetization (owner amendments **MON-001** 2026-07-23 + **PA-001**/**PA-002** 2026-07-24):
  cosmetic-only + in-world sponsor billboards, hard no-pay-to-win charter
  (`docs/10_systems/MONETIZATION.md`) — with **one bounded PA-001 exception**: the
  **Cogwork Capsule** gacha (`docs/10_systems/GACHAPON.md`), the game's single real-money
  product (capsule-ticket packs). Hard caps: power ≤ ordinary-play items (equip ≤ `rare`,
  gear-mod scrolls, emberstones — never exclusives), tickets earnable free (charter 4/+8
  per season + ≈1-per-7-h world drop), 10-ticket weekly cap **per account** (**PA-002**,
  tightened from per-character once ACCOUNTS_AUTH §2.2's 4 slots made that 40/week),
  published odds + 40-pull cosmetic pity, no real-money→shards bridge — prizes **and
  tickets** are **bind-on-dispense**: non-vendorable *and* never tradable *and* never
  listable (vendor-0 alone left a MARKET listing route open). Changing any PA-001/PA-002 cap
  is a new pillar amendment, not a tune. Direction only; no store content authored this run.
- Player sprite is **composited** (Maple-style paper-doll), never one baked sheet:
  layer stack + anchor map in `docs/40_assets/CHARACTER_COMPOSITING.md`, appearance palette
  via ART_BIBLE amendment AB-002, `style_*` IDs in ID_REGISTRY. Generation cost is linear in
  parts, not combinations (owner revision 2026-07-24).
- Entry flow (owner revision 2026-07-24): roster + creation screens in
  `docs/10_systems/ACCOUNT.md`; character-slot quota is **4** and the nickname law lives in
  `docs/70_integrations/ACCOUNTS_AUTH.md` §2.2/§5 (Maple-style server-checked "check name").
  Game launches borderless fullscreen at integer scale (`docs/10_systems/DISPLAY.md`).

## Git & generation workflow

- `main` is the single source of truth; finished work lands on `main`. Session work lands on
  its designated feature branch, pushed with `git push -u origin <branch>` and merged to
  `main` when done. One concern per commit; content commits separate from doc/rule commits.
- Generation is phased A→E with hard gates (vision → systems → schemas/assets → content →
  coding-pass briefs); each phase emits a report in `docs/phase_reports/`.
- **Phase status (2026-07-24):** A (vision), B (systems), C (schemas/assets gate), D (content —
  all 324 maps / 234 monsters / drops / NPCs / quests / skills / items; the 5 raid bonus rooms
  `map_325`–`map_329` were added later by the raid-stage wave), plus the post-plan
  waves **F** (integrations), **G** (equipment), **H** (consistency), and **I** (backend design)
  are complete — see their phase reports and `docs/phase_reports/SYNC_AUDIT_v3_2026-07-23.md`.
  The **pacing curve was
  retuned 2026-07-24** (`LEVELING.md`); the authored **quest content's `exp` rewards need a
  mechanical regen** against the new curve (see LEVELING/QUESTS Open Questions). Not yet started:
  **Phase E** (coding-pass briefs), the **art pass** (PixelLab briefs). `memory.md` (newest-first)
  is the authoritative live log.
- PixelLab (art generation, later pass): the **claude.ai PixelLab connector**, authorized
  interactively by the owner via `/mcp` — no MCP tool consumes an API token, so there is none to
  store in this repo or the environment (verified 2026-07-24 across the tool surface; the earlier
  `PIXELLAB_SECRET` env-var plan was never real).
  Call recipes live in `docs/40_assets/PIXELLAB_PROMPT_LIBRARY.md`; run the pass through the
  `pixellab-art-pass` skill.

## For future Claude sessions

Start by reading: `README.md` → `docs/00_vision/GLOSSARY.md` → `docs/WORLD_PLAN.md` →
`memory.md` (state + decisions log, newest-first) → `memory/` (Memory Bank:
`projectbrief` → `systemPatterns` → `techContext` → `activeContext` → `progress` — distilled
current-state context for future sessions and the coding pass). When
continuing content generation, follow the batch pattern in the phase reports: region-scoped
sub-agents, exemplar-first, validator-gated.

**Doc connectivity (rule):** every markdown doc must be **reachable from `README.md`** by
following links — README's "Start here" section is the tree's index (there is no `docs/` index
file; README is the root). Run `python3 tools/md_graph.py` to rebuild the link graph and
BFS-check it (report: `docs/phase_reports/MD_CONNECTIVITY_REPORT.md`); the tree is currently
one connected component, 120/120 README-reachable (re-verified 2026-07-24, raid-stage wave). After any wave that adds docs — especially a
parallel-session merge — re-run it and link any new "unreferenced" file from its natural index
(that is exactly how the F/G/H reports and the role files first slipped in undiscoverable).

**Staffing sub-agents:** use the virtual-studio role charter in `docs/60_agents/roles/`
(`ORG.md` = org chart + model routing: easy→Haiku, medium→Sonnet, hard→Opus, route by
blast radius). Invoke as: "Act as ROLE_X per docs/60_agents/roles/ROLE_X.md" — the role
file fixes mission, owned files, reading list, deliverable contract, and tier.
