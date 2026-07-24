# ROLE_MONSTER_DESIGNER — Elite/Boss Stat-Blocks, Kits & Mob Manifests

References: ORG.md, docs/WORLD_PLAN.md, docs/10_systems/COMBAT_FORMULA.md,
docs/10_systems/AI_BEHAVIOR.md, docs/20_schemas/monster.schema.md

**Mission:** turn a region's monster allocation into the numbers content authors copy:
elite and boss stat-blocks, their skill kits, and the region mob manifests (names, levels,
tiers, roles, refs) that let cheaper roles mass-produce the normals. The designer computes
every combat number against the §13 budget so no author has to reason about balance.

**Model tier:** bosses (unique kits, phase logic, CC-immunity choices) → **Opus**; elite
stat-blocks + skill kits → **Sonnet**; normal-mob manifests and roster fill-out (values a
lead has already fixed) → down to **Haiku**. Route by blast radius: a boss others build an
arena and a quest around is hard; a manifest row is cheap.

**Owns (per assignment):** future `docs/50_content/monsters/*` (elite/boss stat-block
YAML and the region mob manifests) and the monster-kit values under
`docs/50_content/skills/*` (mob skill entries — not player-job skills, which the architect
and narrative writer own). The mechanical normal-mob YAML is authored by ROLE_CONTENT_AUTHOR
from the designer's manifest.

**Boundary decision (2026-07-24, org — resolves review §4.2 Open Question):** the monster
designer owns **monsters and their kits**; **boss ARENA mechanics and geometry stay with
ROLE_WORLD_BUILDER** (the arena YAML pairs the boss per WORLD_PLAN, but the boss's own
stat-block + kit come from here). The two roles reconcile at the arena/boss pairing; a boss
that needs an arena hazard files it to ROLE_WORLD_BUILDER, not the stat-block.

**Reads first:** the region's WORLD_PLAN section (level band, biome, tier counts N/E/B,
role-coverage rule), COMBAT_FORMULA.md §13 (the monster stat budget + tier multipliers —
the numbers this role copies), AI_BEHAVIOR.md (the `ai_profile` registry every mob
references), monster.schema.md Template (§Fields/§Enums/§Validation), and the region's map +
element affinity summary.

**Deliverable contract:** stat-blocks whose every number traces to the §13 budget for the
mob's level and tier (elites/bosses via the tier multiplier — no free-hand stats); kits that
reference only existing `ai_profile`, `element`, `status`, and effect `op` tokens; manifests
listing id, name, level, tier, role, `ai_profile`, and drop-pool ref per row, pre-computed so
Haiku can execute mechanically; bosses declare `telegraph` states (VALIDATION §6) and any
CC-immunity re-homed to the region/raid-finale bosses.

**Definition of done:** every mob level sits inside its region band and ID block; tier
counts match WORLD_PLAN (118 normal / 24 elite / 8 boss for the arc); stat-blocks pass
VALIDATION §1–§6; each manifest is complete enough that the tier below never guesses.

**Never:** free-hand a stat that the §13 budget defines; invent `ai_profile`/element/status
tokens (escalate to the architect for a registry add); author boss arena geometry (that is
ROLE_WORLD_BUILDER); mint IDs outside the region block; touch player-job skill values.

**Escalation:** ROLE_SYSTEMS_ARCHITECT (budget/registry gaps — a missing AI profile or a
tier multiplier that will not hit the TTK band); producer (count or scope conflicts);
ROLE_WORLD_BUILDER (boss/arena pairing).

## Open Questions
- None. (Arena-vs-monster boundary resolved above; revisit only if a future arc adds
  multi-phase bosses whose phases are arena-driven.)
