# WIKI_EXPORT.md — Auto-Generated Player Wiki from 50_content

References: README.md, docs/00_vision/GLOSSARY.md, docs/VALIDATION.md, docs/WORLD_PLAN.md,
docs/ID_REGISTRY.md, docs/20_schemas/monster.schema.md, docs/20_schemas/item.schema.md,
docs/20_schemas/map.schema.md, docs/20_schemas/quest.schema.md, docs/20_schemas/npc.schema.md,
docs/20_schemas/skill.schema.md, docs/20_schemas/drop_table.schema.md,
docs/20_schemas/job.schema.md, docs/10_systems/DROPS.md, docs/10_systems/JOBS.md,
docs/10_systems/COLLECTIONS.md, docs/70_integrations/BUILD_DISTRIBUTION.md

## 1. Concept

The design tree's `50_content/` YAML is already machine-loadable and validated against the schemas and rules in `docs/VALIDATION.md`. A static wiki generator can transform this content into a player-facing reference site with **zero hand-written wiki pages**: each entity (monster, item, map, quest, npc, skill, job) maps to one canonical page, rendered directly from its schema-defined fields and the system docs that own their semantics. This approach has two key benefits: (1) the wiki is guaranteed to stay synchronized with the game's actual content — no risk of stale or missing pages; (2) updates to game balance (drop rates, stat scaling, loot sources) automatically propagate to the wiki on the next build, eliminating the common problem of patch notes diverging from documentation.

The wiki is a **build artifact**, regenerated on every content release alongside the game binary (see `docs/70_integrations/BUILD_DISTRIBUTION.md` for versioning and release integration). Wiki pages are never hand-edited; truth lives only in content YAML and the owning system docs that define field semantics. This single-source-of-truth model mirrors the validation contract: if content passes `docs/VALIDATION.md` checks, the wiki renders correctly. The generator is a thin layer that performs lookups and template rendering, not interpretation — all game logic and semantics stay in the docs and schemas where designers and engineers can reason about them.

Because every wiki page is derived from validated YAML, the wiki is a guaranteed accurate snapshot of the shipped game state. This is especially valuable for complex interconnected data: a monster's loot table must reference existing items and drop pools, and the wiki automatically reflects those links without duplication. If a balance patch changes a drop rate from `rare` to `uncommon`, the YAML is updated once; the wiki regenerates and players see the new rate on the next release.

A static wiki is also operationally simple: it requires no database, no authentication layer, no server-side logic, and no runtime dependencies beyond HTTP serving. This means it is trivially cacheable, presents a minimal attack surface, and places zero operational load on the game's account/server infrastructure. The wiki can be hosted on a CDN or a simple static file server anywhere in the world with low latency and cost. Accessibility is built-in: static HTML with semantic markup, no JavaScript required for reading (progressive enhancement for search/navigation).

## 2. Page types

One generated page per content entity, typed by schema (see `docs/20_schemas/` for authoritative field definitions):

- **Monster pages**: `level`, tier, `element`, `exp` reward, all maps where it spawns, loot table with bucketed drop chances and item links (see §3 for bucketing), AI profile, animation states — every field read from `docs/20_schemas/monster.schema.md` and the paired drop table.
- **Item pages**: equipment slot or use category, stat bonuses (`power`, `armor`, `precision`, etc. — semantics owned by the system docs), `rarity` and enhancement caps. A sources section lists which monsters drop it (bucketed by drop tier), which quests reward it, whether it is a boss-unique, and vendor availability; if an item is a quest `collect` target, that quest is linked.
- **Map pages**: region slug and level band (per `docs/WORLD_PLAN.md`), map type (`field`, `dungeon`, `town`, `secret`, etc.), full portal/connection list with linked map names and spawn-point targets for safe navigation, spawn density table (monster ID → count range per play session), coach stops and NPC locations if applicable. Map pages include a "quests started here" section for quest-giver locations.
- **Quest pages**: giver NPC with location link, multi-step objectives, `exp` and `shards` rewards, prerequisite quests or level locks, completion requirement.
- **Skill and job pages**: stat requirements (`might`, `finesse`, `focus`, `fortune` per `docs/00_vision/GLOSSARY.md`), rank progression, `essence` cost, cooldown timer, effect descriptions with damage/healing/status references. Job pages also show each advancement's `level` requirement and home-town instructor (per `docs/10_systems/JOBS.md` and `docs/WORLD_PLAN.md`'s instructor table — cited, not restated).
- **Region indexes**: per-`WORLD_PLAN.md` region slug, listing all maps in order, regional boss locations, quest hubs (towns with quest-giver NPCs), level band for the region, and a quick-reference table of monsters by tier and `element` found in that region.

Every field is sourced directly from its owning schema; cross-links follow entity IDs validated in `docs/VALIDATION.md` §2. If a schema field is not meant to be public (e.g., internal tuning flags or developer notes), it is omitted from the wiki template. Optional fields that are missing from an entity are handled gracefully (e.g., if an NPC has no quest, the quest section is hidden; if an item has no drop sources, it says "Quest only" or "Unique reward"). This keeps pages clean without requiring separate wiki edits for every edge case.

Pages link to each other via cross-references: a monster page links to items it drops, which link back to the monster; a map page links to monsters that spawn there and NPCs with quest starts; quest pages link to their giver NPC and reward items. The wiki generator builds these bidirectional links automatically by resolving ID references. A full-text search index (built during static-site generation) makes these connections discoverable for players ("What drops this item?" → search the item, see all monsters in its drop pool).

The wiki does not include deleted or deprecated content from prior patches — it reflects the current patch only. If a monster is removed or an item is rebalanced, its page either vanishes (removal) or updates (rebalancing). Patch notes external to the wiki document these changes; the wiki itself is always the single current source of truth.

## 3. Spoiler and disclosure policy

**Spoiler gate:** `secret` map-type pages and boss drop tables are hidden behind a toggled spoiler section (off by default). Players who toggle spoilers see the full loot tables and secret-map locations inline; those who do not see only the flavor text and layout descriptions. This respects players who want to discover content organically while providing reference data to experienced players. Non-secret dungeons and normal maps are always visible. Unreleased content — future-arc region slugs (`frostpeak`, `arcane_reach`, `voidshore`, `rift` per `docs/00_vision/GLOSSARY.md`), 3rd jobs, and any ID sitting in a block `docs/ID_REGISTRY.md` reserves for future arcs — is never exported to the wiki, not even behind a spoiler toggle.

**Drop percentages and balance tuning:** the default display buckets drop chances using the named tiers from `docs/10_systems/DROPS.md` §2 (`guaranteed`, `common`, `uncommon`, `rare`, `epic`, `legendary`) rather than raw percentages. This mirrors designer tuning language and avoids prematurely locking in exact percentages that may be tuned during balance passes. For example, a player sees an item listed as a `rare` drop rather than its raw probability. This also keeps the wiki useful across minor balance patches where percentages shift within a tier but the design intent (drop rarity) stays the same. The alternative — showing raw percentages or a different bucketing scheme — is filed as an Open Question below.

## 4. Pipeline sketch

Prose only: each Phase D content batch passes through the validators in `docs/VALIDATION.md` before landing on the feature branch. When a release is ready, the build system (see `docs/70_integrations/BUILD_DISTRIBUTION.md` for the full pipeline) invokes a static-site generator (implementation language TBD at engineering phase) that reads the validated `50_content/` YAML, resolves cross-references to system docs and schemas, and outputs HTML and/or Markdown files using wiki-page templates. Each page is named by entity ID and includes generated metadata (last-updated timestamp, content version).

The generated wiki is published to static hosting (CDN or GitHub Pages; choice deferred) and versioned by the content version string (see `docs/70_integrations/BUILD_DISTRIBUTION.md`), ensuring players always see the wiki matching their installed game build. A version banner in the wiki footer says "You are reading content for version X.Y"; updating the game updates this banner automatically.

The wiki generation is a **pre-release step** — it runs after content validation and before the game binary ships. Generation failure prevents the release (no partial shipping); it is not on the critical path for the binary build itself. This ensures the wiki is always faithful to shipped content and never lags behind patches. The generator produces a static manifest (JSON or YAML) listing all generated pages, entity counts, and checksums; this manifest is compared against the prior release to detect stale or missing pages.

The generated HTML/Markdown is served with aggressive caching headers (content-hash-based filenames, aggressive expires headers on versioned artifacts). The wiki's version banner, deploy timestamp, and content version are injected at generation time, not runtime. This means the entire wiki is cacheable at CDN edge nodes and requires no server-side logic beyond HTTP serving. Implementation belongs to the future coding pass, not this design run.

## 5. Non-goals

- **No user editing, comments, or discussions at launch:** the wiki is read-only. A community-contribution layer (player edits, translations, strategy guides) is explicitly deferred to a future phase; this run produces wiki as static output artifact only. User-generated content requires moderation infrastructure and governance, which are out of scope for the initial release.
- **No live game-server data or player statistics:** the wiki is static truth — it does not show player activity, online counts, market prices, auction data, or individual progression stats. Real-time game statistics and economy dashboards belong on a separate live dashboard, implemented during the server phase (`docs/10_systems/PERSISTENCE.md`). The wiki is content reference only.
- **Not a replacement for the in-game Collections or achievement log:** the collection log (`docs/10_systems/COLLECTIONS.md`, authored this wave) tracks each character's personal discovery state and unlocked rewards. The wiki shows all entities and their definitions; the Collections log shows only what the player has encountered in their playthrough. These two systems are complementary — the wiki is study reference, the log is personal progress.
- **No monetization or advertising:** the wiki is a pure player reference and educational resource, not a monetization channel or advertising platform.

## 6. Inputs contract — what the generator may read

The generator's input set is closed, which doubles as its disclosure boundary:

- **May read:** `50_content/*` YAML (the only source of entity values), `docs/20_schemas/*`
  (field shapes and which fields are public), `docs/WORLD_PLAN.md` (region ordering for
  indexes), and `docs/00_vision/GLOSSARY.md` (display spellings of tokens).
- **May not read:** internal process docs — `docs/60_agents/*`, `docs/phase_reports/*`,
  `memory.md`, role charters, and any `## Open Questions` section anywhere. Design rationale,
  unresolved questions, and agent workflow never leak into player-facing pages.
- Flavor text renders verbatim from content fields; the generator never composes new prose
  (`docs/10_systems/WRITING_STYLE.md` governs the words at authoring time, not export time).

## Open Questions

- Should the wiki show raw drop percentages in an advanced/detailed toggle, or only the named tiers? If percentages, what precision (0.1%, 1%, "< 1%")?
- Timeline and scope for a community-contribution layer: user-submitted guide articles, translations, or wiki edits (vote-curated or moderated)? Should this be a separate platform or integrated into the wiki itself?
- Hosting choice and cost model: owner-operated static server, third-party CDN (Cloudflare, Netlify, AWS CloudFront), GitHub Pages, or player-hosted mirror network? What is the owner's infrastructure budget?
- Should the game client include deep-links into the wiki (e.g., right-click a monster or item to open its wiki page)? Implementation deferred pending wiki hosting decision.
- Multilingual support at launch (Spanish, French, German) or English-only with translations as a future contribution layer?
- Archive strategy for wiki versions: when new patches ship, should prior-patch wiki snapshots remain accessible at version-specific URLs for players reading old guides?
- Should the wiki homepage display a "What's new in this patch?" summary linked from the version banner, or is patch notes external to the wiki only?
- Player-facing feedback mechanism: should wiki pages include a "Report an error" or "Suggest an edit" link that opens an issue in the docs repo, or is this out of scope?

