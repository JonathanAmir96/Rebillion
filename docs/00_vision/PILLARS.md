# PILLARS.md — Design Pillars

Working title: **Rebillion** — a 2D side-scrolling MMORPG-style platformer. Inspired by the
classic hunt-and-hangout genre, deliberately **not a clone**: original vocabulary (GLOSSARY.md),
original world (WORLD_PLAN.md), original art identity (40_assets/ART_BIBLE.yaml).

Every design decision in this tree must be defensible against these pillars. When two docs
conflict, the pillar wins; file an Open Question if the pillar itself seems wrong.

## P1 — Readable, snappy, fair combat
Combat is platforming plus timing. Few animation frames done well, visible telegraphs, hit-frame
honesty (damage lands on the animation frame, never on a hidden timer). A player who dies should
know why. Depth comes from positioning, element/status interplay, and skill composition — not
from hidden math.

## P2 — The grind is cozy, not cruel
Progression is steady and legible: clear level bands per region, drop tables you can reason
about, no trap builds. Sessions of 20 minutes must feel rewarding. Death stings but never
deletes an evening (10_systems/DEATH_PENALTY.md). Idle moments in towns are part of the game, not waste.

## P3 — One world, a walkable ring
Five islands, one world: a sheltered training isle, a ferry to the great ringed island where
Millbrook is the social heart, and the far isles beyond — reached by deep passage or
longship. Regions have strong biome identity (one palette ramp, one
motif), maps connect like real geography, and travel is a legible loop: hunt outward, return
home by the Millbrook Return Scroll or a paid coach — there are no free warps
(WORLD_PLAN.md §Harthmoor Coachworks). The world map should be drawable from memory.

## P4 — Compose, don't enumerate
Skills are compositions of effect primitives. Monsters are stats plus a named behavior profile.
Guild crests are data. New content is new *data*, not new *rules*. If a design needs bespoke
logic, it is either generalized into a primitive or cut.

## P5 — Data is the game
Every entity is a machine-loadable file conforming to one schema, using only GLOSSARY tokens,
validated by VALIDATION.md. A future implementer (or agent) with only a schema doc and its
referenced system docs can implement the feature without asking questions. Broken references
are build failures, not surprises.

## P6 — Multiplayer-shaped from day one
Trading, parties, guilds, chat, mail, and the market are designed now and stubbed honestly —
the client is written against a server-authoritative boundary (10_systems/PERSISTENCE.md,
30_engineering/ENGINEERING_STANDARDS.md) even while running solo. No system may assume it owns
truth that the server will later own.

## P7 — Original identity everywhere
Names, stats, currency, art, and UI use Rebillion's own vocabulary and look. Anything that
would read as another game's asset, term, or map is out — homage yes, clone never.

## Anti-pillars (never do)
- No photoreal or HD-2D rendering; pixel identity is locked in ART_BIBLE.yaml.
- No pay-to-win (amended MON-001): real-money purchases may never grant stats, power,
  progression speed, or market-tradable advantage. Cosmetic-only monetization and in-world
  sponsor placements are permitted per 10_systems/MONETIZATION.md; shards remain earned
  in-world only (10_systems/ECONOMY.md). **Further amended by PA-001** (owner, 2026-07-24):
  one bounded exception — the Cogwork Capsule gacha SKU (10_systems/GACHAPON.md §1) may
  dispense limited, ordinary-play-obtainable power (equip rolls ≤ `rare`, gear-modification
  scrolls, emberstones) under hard caps: tickets earnable free, weekly purchase cap,
  published odds with pity, and no real-money→`shards` bridge. Everything else in MON-001
  stands, including no purchased exclusive power.
- No rule text inside content files; content holds values and references only.
- No silent invention: unknown token, rule, or number → Open Question, not a guess.

## Open Questions
- None. (Pillars locked at Phase A; changes require an orchestrator amendment. Amendment
  log: **MON-001**, owner, 2026-07-23 — anti-pillar "no pay-style economy" refined to
  "no pay-to-win"; cosmetic-only monetization direction fixed in
  10_systems/MONETIZATION.md. **PA-001**, owner, 2026-07-24 — one bounded exception to
  MON-001 §2.1/§2.3/§2.4 for the Cogwork Capsule gacha SKU; caps live in
  10_systems/GACHAPON.md §1, and changing any cap is a new amendment, not a tune.)
