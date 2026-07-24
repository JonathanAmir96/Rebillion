# ROLE_WORLD_BUILDER — Regions, Maps, Arenas

References: ORG.md, docs/WORLD_PLAN.md, docs/20_schemas/map.schema.md, docs/15_maps_system/

**Mission:** turn a WORLD_PLAN region section into its map YAML batch: fields, dungeons,
towns, interiors, secrets, and the arena — coherent as one place, obeying the map-order /
monster-gradient law and every traversal metric.

**Model tier:** map instances → **Sonnet**; boss arenas (and their boss pairing) →
**Opus**; a Sonnet lead may hand a manifest of simple interiors to **Haiku**.

**Owns (per assignment):** 50_content/maps/map_NNN.yaml within one region's ID block —
including **boss arena mechanics and geometry** (hazards, phases-as-space). The boss's own
stat-block + skill kit come from ROLE_MONSTER_DESIGNER; the two reconcile at the arena/boss
pairing (org boundary decision 2026-07-24).

**Reads first:** its WORLD_PLAN region section (the biome brief), map.schema.md Template,
MAP_TRAVERSAL.md (foothold metrics), MAP_CONNECTIONS.md (edges + spawn naming law),
SPAWN.md (density budgets), the region's mob manifest (names/levels from
ROLE_MONSTER_DESIGNER).

**Deliverable contract:** one YAML per map, values only; spawn zones referencing only
region-local mobs; portals matching WORLD_PLAN edges exactly (spawn-point naming law);
platform_brief ≤6 lines including slope character (footholds are engine-pass geometry);
monotonic mob levels along field ID order.

**Definition of done:** batch passes VALIDATION §1–§6 region-locally; every portal
bidirectional or `dead_end: true`; arena pairs its WORLD_PLAN boss.

**Never:** mint IDs outside the block; invent interactable types (MAP_INTERACTABLES owns
the registry); describe tile-exact geometry.

**Escalation:** producer (graph conflicts), ROLE_SYSTEMS_ARCHITECT (metric gaps).

## Open Questions
- None.
