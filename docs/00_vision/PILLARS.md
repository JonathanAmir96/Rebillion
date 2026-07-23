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
Two islands, one world: a sheltered training isle, then a ferry to the great island where
Millbrook is the social heart. Regions have strong biome identity (one palette ramp, one
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
- No pay-style economy design (shards are earned in-world; 10_systems/ECONOMY.md).
- No rule text inside content files; content holds values and references only.
- No silent invention: unknown token, rule, or number → Open Question, not a guess.

## Open Questions
- None. (Pillars locked at Phase A; changes require an orchestrator amendment.)
