#!/usr/bin/env python3
"""Rebillion tree validator — implements docs/VALIDATION.md checks 1-4.

Usage:
    python3 tools/validate.py            # validate the whole tree
    python3 tools/validate.py PATH ...   # validate specific files/dirs (a content batch)

Exit code 0 = pass, 1 = at least one FAIL. Warnings never fail the run.

Scope per docs/VALIDATION.md:
  1  No forbidden tokens (whole-word, case-sensitive; VALIDATION.md itself exempt)
  2  Referential integrity (content YAML ids must resolve; docs cross-links must exist)
  3  Schema conformance (front-matter id/schema/references present; schema file exists)
  4  ID uniqueness and range (per docs/ID_REGISTRY.md blocks)
  +  Doc structure (phase-gate check: H1 first line, `## Open Questions` ending)

Checks 5-6 (world-graph soundness, asset contract) land with the Phase D reconciler.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONTENT = DOCS / "50_content"

# ----------------------------------------------------------------------------- check 1
# The banned list is canonical in docs/VALIDATION.md §1; kept in sync by hand.
FORBIDDEN = ("STR", "DEX", "INT", "LUK", "HP", "MP", "meso", "mesos")
FORBIDDEN_RE = re.compile(r"\b(" + "|".join(FORBIDDEN) + r")\b")
FORBIDDEN_EXEMPT = {DOCS / "VALIDATION.md"}

# ----------------------------------------------------------------------------- check 4
# ID blocks mirror docs/ID_REGISTRY.md (v2 + C-gate extensions); update together.
ID_BLOCKS = {
    "map": (1, 200),
    "mob": (1, 160),          # 001-150 world monsters; 151-160 summon templates
    "drop_mob": (1, 150),
    "item_equip": (1, 300),
    "item_use": (1, 100),
    "item_etc": (1, 200),
    "npc": (1, 120),
    "quest": (1, 120),
}
ID_RE = re.compile(
    r"\b(map|mob|drop_mob|item_equip|item_use|item_etc|npc|quest)_(\d{3,4})\b"
)
SKILL_ID_RE = re.compile(r"\bskill_(bulwark|keeneye|weaver|flicker|novice)_(\d{3})\b")
SKILL_MAX = {"bulwark": 30, "keeneye": 30, "weaver": 30, "flicker": 30, "novice": 10}
POOL_RE = re.compile(r"\bpool_equip_r(\d{2})\b")

# Doc-structure exemptions: reports/state files are logs, not rule docs.
STRUCTURE_EXEMPT_DIRS = {"phase_reports"}
STRUCTURE_EXEMPT_FILES = {"README.md", "memory.md", "CLAUDE.md"}


class Findings:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)


def iter_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            out.extend(sorted(q for q in p.rglob("*") if q.suffix in {".md", ".yaml", ".yml"}))
        elif p.suffix in {".md", ".yaml", ".yml"}:
            out.append(p)
    return [p for p in out if ".git" not in p.parts]


def check_forbidden(path: Path, text: str, f: Findings) -> None:
    if path in FORBIDDEN_EXEMPT:
        return
    for i, line in enumerate(text.splitlines(), 1):
        m = FORBIDDEN_RE.search(line)
        if m:
            f.fail(f"{path.relative_to(ROOT)}:{i}: forbidden token `{m.group(1)}` (VALIDATION §1)")


def check_structure(path: Path, text: str, f: Findings) -> None:
    if path.suffix != ".md" or path.parent.name in STRUCTURE_EXEMPT_DIRS:
        return
    if path in LOCKED_FILES:
        return
    if path.name in STRUCTURE_EXEMPT_FILES or DOCS not in path.parents:
        return
    lines = text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        f.fail(f"{path.relative_to(ROOT)}: first line is not an H1 title")
    if "## Open Questions" not in text:
        f.fail(f"{path.relative_to(ROOT)}: missing `## Open Questions` section (VALIDATION §7)")


def check_id_ranges(path: Path, text: str, f: Findings) -> None:
    rel = path.relative_to(ROOT)
    for m in ID_RE.finditer(text):
        prefix, num = m.group(1), int(m.group(2))
        lo, hi = ID_BLOCKS[prefix]
        if not (lo <= num <= hi):
            f.fail(f"{rel}: `{m.group(0)}` outside the reserved `{prefix}` block {lo}-{hi} (VALIDATION §4)")
    for m in SKILL_ID_RE.finditer(text):
        line_tok, num = m.group(1), int(m.group(2))
        if not (1 <= num <= SKILL_MAX[line_tok]):
            f.fail(f"{rel}: `{m.group(0)}` outside the `skill_{line_tok}` range (VALIDATION §4)")
    for m in POOL_RE.finditer(text):
        if not (1 <= int(m.group(1)) <= 8):
            f.fail(f"{rel}: `{m.group(0)}` outside pool_equip_r01-r08 (VALIDATION §4)")


FRONT_MATTER_KEYS = ("id", "schema", "references")


def parse_front_matter(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines()[:40]:
        m = re.match(r"^(id|schema|references)\s*:\s*(.+?)\s*$", line)
        if m:
            out.setdefault(m.group(1), m.group(2))
    return out


def check_content_yaml(path: Path, text: str, f: Findings, known_ids: set[str]) -> None:
    """Checks 2-4 for a 50_content YAML file."""
    rel = path.relative_to(ROOT)
    fm = parse_front_matter(text)
    for key in FRONT_MATTER_KEYS:
        if key not in fm:
            f.fail(f"{rel}: missing front-matter `{key}` (VALIDATION §3)")
    schema = fm.get("schema")
    if schema and not (ROOT / "docs" / Path(schema).relative_to("20_schemas") if schema.startswith("20_schemas/") else ROOT / schema).exists():
        candidate = DOCS / schema if not schema.startswith("docs/") else ROOT / schema
        if not candidate.exists():
            f.fail(f"{rel}: schema `{schema}` does not resolve to a file (VALIDATION §2)")
    file_id = fm.get("id")
    if file_id:
        if file_id in known_ids:
            f.fail(f"{rel}: duplicate id `{file_id}` (VALIDATION §4)")
        known_ids.add(file_id)
        stem_ok = path.stem == file_id or file_id in ("drop_pools",) or path.stem.startswith(file_id)
        if not stem_ok:
            f.warn(f"{rel}: id `{file_id}` differs from filename stem `{path.stem}`")


# Locked files follow the master brief's own format, not the tree's doc template.
LOCKED_FILES = {
    DOCS / "40_assets" / "ART_BIBLE.yaml",
    DOCS / "40_assets" / "UI_ART_SPEC.md",
    DOCS / "30_engineering" / "ENGINEERING_STANDARDS.md",
}


def check_doc_links(path: Path, text: str, f: Findings) -> None:
    """Check 2 (docs flavor): backticked doc paths must exist."""
    if path.parent.name in STRUCTURE_EXEMPT_DIRS:
        return  # phase reports quote historical text verbatim
    rel = path.relative_to(ROOT)
    for m in re.finditer(r"`((?:docs/|00_vision/|10_systems/|15_maps_system/|20_schemas/|30_engineering/|40_assets/|50_content/|60_agents/|70_integrations/)[A-Za-z0-9_/.]+\.(?:md|yaml))`", text):
        ref = m.group(1)
        target = ROOT / ref if ref.startswith("docs/") else DOCS / ref
        if not target.exists() and not ref.startswith("50_content/"):
            f.fail(f"{rel}: broken doc reference `{ref}` (VALIDATION §2)")


def main(argv: list[str]) -> int:
    targets = [Path(a).resolve() for a in argv] or [DOCS]
    files = iter_files(targets)
    f = Findings()
    known_ids: set[str] = set()

    for path in files:
        text = path.read_text(encoding="utf-8")
        check_forbidden(path, text, f)
        if path.suffix == ".md":
            check_structure(path, text, f)
            check_doc_links(path, text, f)
        if CONTENT in path.parents:
            check_id_ranges(path, text, f)
            if path.suffix in {".yaml", ".yml"}:
                check_content_yaml(path, text, f, known_ids)

    for w in f.warns:
        print(f"WARN  {w}")
    for x in f.fails:
        print(f"FAIL  {x}")
    print(f"\nvalidate: {len(files)} files, {len(f.fails)} fail(s), {len(f.warns)} warning(s)")
    return 1 if f.fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
