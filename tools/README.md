# tools/ — content validator

`validate.py` implements the `docs/VALIDATION.md` pass/fail contract (§1–§6) for
Phase D content batches. **Python 3 standard library only** — it uses PyYAML if it
is importable and otherwise falls back to a small tolerant YAML reader built into
the file, so it runs on a bare `python3` with no `pip install`.

## Usage

```
python3 tools/validate.py [--scope A-B] [--entry map_NNN] [--allow-missing] [paths...]
```

- `paths...` — files/directories to check. **Default** (no paths): scans
  `docs/`, `CLAUDE.md`, and `README.md`.
- `--scope A-B` — limit the §5 world-graph check to maps whose number is in
  `[A, B]` (region-local mode, e.g. `--scope 201-244` for Frostpeak).
- `--entry map_NNN` — declare the world-graph entry map for the §5 reachability
  check (default `map_001`). Use the batch's own entry for a region-local run,
  e.g. `--entry map_204`.
- `--allow-missing` — treat unresolved §2 references as **warnings** instead of
  failures (for staged batches whose referenced files land in a later batch).

Exit code: **0** = pass (no failures), **1** = fail. Warnings never fail the run.
Output is grouped by check number, each line as `[FAIL|WARN] file:line — message`.

Content files are auto-discovered: any `.yaml`/`.yml` under the scanned paths whose
front-matter `schema:` resolves to a known `docs/20_schemas/*.schema.md`. Everything
else (prose docs, `ART_BIBLE.yaml`, etc.) is scanned only for §1.

## Which VALIDATION.md check maps to which code

| Check | VALIDATION.md | Code |
|---|---|---|
| **§1** Forbidden tokens | Banned legacy terms may appear only in `docs/VALIDATION.md`; case-sensitive whole words | `scan_banned()` + `BANNED` / `BANNED_RE`. Runs over every text file in the scan set; exempts exactly `docs/VALIDATION.md`. |
| **§2** Referential integrity | Every `mob/map/item/npc/quest/skill/drop_mob/pool` id mentioned in a field must resolve | `REF_RE` + the `defined{}` id universe + the reference walk in `main()`. `--allow-missing` downgrades to warnings. The doc-name `references:` list and `schema:` value are excluded from the scan; the literal `shards` is not an id. |
| **§3** Schema conformance | Front-matter `id`/`schema`/`references`; `schema` resolves; required fields present; no unknown fields; enums from their owner registry | `REQUIRED{}` (per-schema required-field lists — **the one place to edit** when a schema changes), `ALLOWED{}` (unknown-field gate), `REGISTRY{}` (every enum token list, each commented with its owner doc), and the per-schema `validate_*()` functions. |
| **§4** ID uniqueness + range | Globally unique, correct prefix format, in reserved block; mob tier layout (a boss slot may not hold a normal) | `check_id()` + `ID_RANGES`, duplicate detection in the `defined{}` build, and the tier↔slot check in `validate_monster()` via `MOB_BLOCKS` / `mob_tier()`. |
| **§5** World-graph soundness | Portals target an existing map + spawn; every map reachable from the entry; `dead_end` honored | `check_world_graph()` + `--scope` / `--entry`. Runs only over the maps present in the batch. |
| **§6** Asset contract | Animated entities declare `animation_states` from ANIMATION_STATES tokens; elites/bosses include `telegraph` | `validate_monster()` (`REGISTRY["animation_state"]`, telegraph requirement) and the active-skill `animation` check in `validate_skill()`. |

Check §7 (Open-Questions rollup) is a phase-gate documentation task, not a
mechanical file check, and is not implemented here.

## Extending

- **New/changed enum token** → edit the one set in `REGISTRY` (each carries an
  owner-doc comment).
- **New/changed required field** → edit that schema's list in `REQUIRED` (and
  `ALLOWED` if a new optional field is added, or it will be reported as unknown).
- **New schema** → add it to `SCHEMA_BY_PATH`, `REQUIRED`, `ALLOWED`, and write a
  `validate_<kind>()`; register it in `VALIDATORS`.
- **ID range change** (only via a new ID_REGISTRY commit) → edit `ID_RANGES`,
  `MAP_BLOCKS`, `MOB_BLOCKS`.

## Notes on interpretation

The validator follows `docs/VALIDATION.md` and the owning schema docs where the
task brief and a doc differed; see the QA report / schema Open Questions for the
specific calls (e.g. drop-table `chance` allows a raw float per DROPS.md; the
world-graph reachability/`dead_end` semantics; scope of the §2 reference scan).
Deep budget checks (stat ±15%, price formulas, affix pe) and cross-file
world-graph reconciliation are schema-doc rules layered on top of these globals
and are intentionally out of this first-pass tool's scope.
