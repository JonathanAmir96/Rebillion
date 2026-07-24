# MD_CONNECTIVITY_REPORT — Markdown Connectivity Graph & BFS Audit (2026-07-24)

Status: **complete** (session: markdown-connectivity-graph). Built a link graph over every
`*.md` in the tree, ran BFS for connectivity, and closed the discoverability gaps it found.
Tooling: `tools/md_graph.py` (stdlib-only; reproduces this audit on demand).

References: `README.md`, `CLAUDE.md`, `memory.md`, `docs/60_agents/roles/ORG.md`,
`tools/md_graph.py`, `tools/README.md`

## What the tool does

`tools/md_graph.py` walks all 97 markdown files, extracts every cross-doc reference (markdown
`[..](..)` links **and** inline `path/FILE.md` / bare-`FILE.md` mentions — the tree's docs
reference each other mostly by inline path, not link syntax), resolves each to a real file,
and builds two graphs:

- **Undirected** — an edge A—B whenever either file references the other. BFS over this graph
  answers "is the corpus one connected body of docs?"
- **Directed** — A→B when A references B. Reachability from the entry points (`README.md`,
  `CLAUDE.md`, `memory.md`) answers the stronger question "can a reader actually *navigate to*
  every doc by following links?"

Run it: `python3 tools/md_graph.py` (add `--json out.json` / `--dot out.dot` for the raw
graph or a Graphviz render).

## Findings (before)

- **Undirected: fully connected.** 97 files, ~1,185 undirected edges, **1 connected
  component**, **0 orphans**, **0 dead-ends**. BFS reaches every file from every file — the
  corpus was already a single web, not islands.
- **Directed: 10 files unreachable** from `README`/`CLAUDE`/`memory`. They link *out* but
  nothing linked *to* them, so a reader following links top-down would never land on them:
  - `docs/50_content/README.md`
  - `docs/60_agents/roles/ROLE_PRODUCER.md`, `ROLE_WORLD_BUILDER.md`,
    `ROLE_CONTENT_AUTHOR.md`, `ROLE_GAMEPLAY_DEVELOPER.md`, `ROLE_ART_QUARTERMASTER.md`
    (the other five role files were already referenced from phase reports / the backend kickoff)
  - `docs/phase_reports/PHASE_F_INTEGRATIONS_REPORT.md`, `PHASE_G_EQUIPMENT_REPORT.md`,
    `PHASE_H_CONSISTENCY_REPORT.md` (F/G/H came in via a parallel-session merge and were never
    added to any index)
  - `tools/README.md`

## Fixes applied

Every gap was closed by adding a link from the doc's natural parent/index — no content
restated (law §2):

- **`docs/60_agents/roles/ORG.md`** — added a "Role files (index)" section listing all ten
  role charters by path. Makes the whole `roles/` directory reachable from ORG (itself reached
  from CLAUDE.md's staffing note).
- **`README.md`** — the `docs/50_content/` bullet now names `README.md`; the
  `docs/phase_reports/` bullet now enumerates every report (incl. F/G/H and this one); the
  `tools/` bullet now names `tools/README.md` and `tools/md_graph.py`.

## Findings (after)

`python3 tools/md_graph.py`: **1 connected component, 0 orphans, 0 directed-unreachable**
from the entry points. The tree is now both fully connected *and* fully navigable top-down.

## Notes for future sessions

- Re-run `tools/md_graph.py` after any wave that adds docs (especially parallel-session merges
  — that is exactly how F/G/H slipped in unreferenced). A new file that nothing links to will
  show up as "Unreferenced" / directed-unreachable even while the undirected graph stays
  connected.
- The tool is intentionally reference-tolerant (inline paths count as edges) to match how this
  tree actually cross-links. It does **not** validate that a referenced anchor (`#section`)
  exists — that is out of scope; `tools/validate.py` owns content-level reference checks.

## Open Questions

- Should a lightweight `md_graph.py --check` mode (exit 1 on any directed-unreachable file) be
  wired into the same gate as `tools/validate.py`, so future merges can't reintroduce
  unreferenced docs? Default: keep it advisory (a report, run at gates) until it earns a place
  in the batch pipeline.
