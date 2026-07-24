Godot 4.3+; GDScript statically typed. Prime directives: (1) **data-driven always** — content is
Resources loaded at runtime, a new monster needs zero code; (2) **composition over inheritance** —
entities are scenes of small components; (3) **scenes are prefabs**; (4) **signals up, calls down**
via an EventBus; (5) **server-authoritative boundary drawn now** (tag every field client/server per
PERSISTENCE.md; combat math, drops, currency written to move server-side later); (6) **no magic
numbers/strings** (tunables in data, ids as `const`/`StringName`, stat names from GLOSSARY);
(7) **fail loud in dev** (`assert`, `push_error`), safe in prod.

**Project structure:** `autoload/` (EventBus, GameState, Database, SceneManager — few singletons);
`resources/` (Resource classes = schemas as code); `data/` (.tres converted from 50_content YAML);
`entities/` (one base scene per type, data-driven); `systems/` (combat, spawn, loot, skills);
`components/` (Life, Hurtbox, Hitbox, StateMachine, StatusStack); `ui/`, `maps/`, `assets/`,
`tests/`. Naming: snake_case files/vars, PascalCase classes/nodes, SCREAMING_SNAKE consts, `_`
private. Every referenced script declares `class_name`. One folder = one feature.

**Data layer:** `20_schemas/*` map 1:1 to Resource classes; `50_content/*.yaml` → `.tres` at
build time (a tool script, not runtime). Runtime loads `.tres` only. Content Resources are
immutable at runtime — a live entity holds a *reference* to its data + separate mutable state. A
central `Database` autoload owns all lookups and validates references on load (broken ref = hard
error, mirrors VALIDATION.md).

**Entity pattern:** one `monster.tscn` + `monster.gd` driven by injected `MonsterData`; spawner
calls `setup(data)` before adding to tree. Shared behavior in components, not entity scripts.
Player and Monster share components but are separate scenes.

**State machines:** explicit hierarchical SM node; states are separate scripts named with
`StringName` consts. **Climbing (ropes/ladders) is a first-class state implemented once** per
MAP_TRAVERSAL.md — no per-map reimplementation. Logic state requests animation; the animation's
**hit-frame** (ANIMATION_TIMING) emits the signal combat listens for — damage never on a duplicate timer.

**Autoloads (sparingly):** EventBus (pure signal declarations, no logic), GameState (save facade,
client/server tags), Database (content lookups), SceneManager (transitions), optional Audio/Input.
Scene-local systems (spawn, loot) are nodes in the map scene so they reset on map change.

**Combat:** all damage math in a pure stateless `CombatMath` class (numbers in, numbers out, no
node access) implementing COMBAT_FORMULA.md — the only place the formula exists, so it can move
server-side untouched. Hurtbox/Hitbox are Area2D; nodes decide *when* (frame events), CombatMath
decides *how much*. All randomness through one seeded RNG service (server-verifiable later).

**Performance:** object-pool monsters/projectiles (no instantiate/queue_free in hot paths);
`preload()` parse-time refs, `load()` only deferred content, never in `_process`; prefer signals
over polling; gameplay in `_physics_process`, visuals in `_process`; sleep off-screen mobs with
VisibleOnScreenEnabler2D; one TileMapLayer stack per map per MAP_LAYERS.

**Pixel rendering (match SPRITE_PIPELINE/SPRITESHEET_SPEC):** Default Texture Filter = Nearest;
per-texture Filter OFF / Mipmaps OFF / Fix Alpha Border ON; enable 2D pixel snapping; integer
window scaling; **pivot = feet-center**; pixel-snapped camera.

**Collision layers (canonical, expose as a `Layers` enum — no raw bits in scripts):** 1 world,
2 one_way, 3 player_body, 4 monster_body, 5 player_hit, 6 monster_hit, 7 pickups, 8 climbable,
9 interactable. One-way platforms + climbables implemented once in components.

**GDScript style:** static typing everywhere (`:=` for inferred locals); script order class_name→
extends→doc→signals→enums→consts→@export→public→private(`_`)→@onready→lifecycle→public methods→
private; `StringName` for frequent identifiers; guard clauses; functions <~30 lines; no deep node
paths (use `@onready`+`%UniqueName` or injection); disconnect signals on teardown; `##` doc every
public method + Resource field.

**Testing/validation:** GUT tests for CombatMath, drop rolls, leveling curve, status stacking,
content-load integrity. A content validator implements VALIDATION.md (token scan, referential
integrity, schema conformance, ID uniqueness, world-graph) and blocks merges in CI.

**VCS/agent hygiene:** gitignore `.godot/`; one concern per commit; content commits separate from
code; a schema change updates Resource class + validator + content + doc together, or files an
Open Question; never edit ART_BIBLE (Agent-3 only) or read-only docs (copy locally).

**Amendments:** ES-001 (2026-07-24, owner-directed contradiction fix C-27c,
`docs/phase_reports/DESIGN_REVIEW_CONTRADICTIONS_2026-07-24.md`): the survival-pool component is
named `Life` (was `Health`), per prime directive 6's stat-names-from-GLOSSARY rule and the `life`
token. · ES-002 (2026-07-24, owner-directed md audit): added the closing `## Open Questions`
section required of every doc (CLAUDE.md Law 4 / `docs/VALIDATION.md` §7) — structural
conformance only, no standard changed.

**Definition of Done:** data-driven, typed, tested, validates, respects client/server boundary,
uses only GLOSSARY tokens, no `push_error` on load, Open Questions resolved or logged.

## Open Questions

- None currently. Standards questions route through this file's amendment channel
  (CLAUDE.md Law 5); every landed change is logged above as an `ES-` amendment.
