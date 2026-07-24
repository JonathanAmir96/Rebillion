#!/usr/bin/env python3
"""Markdown connectivity graph for Rebillion docs.

Builds an undirected graph over all *.md files. An edge A—B exists when file A
references file B (by markdown link or inline path/filename), or vice-versa.
Runs BFS to find connected components and reports orphans / islands.

Usage: python3 tools/md_graph.py [--json out.json] [--dot out.dot]
Stdlib only.
"""
import os
import re
import sys
import json
from collections import deque, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_md_files():
    out = []
    for root, dirs, files in os.walk(REPO):
        if ".git" in root.split(os.sep):
            continue
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.relpath(os.path.join(root, f), REPO))
    return sorted(out)

MD_LINK = re.compile(r'\]\(([^)]+)\)')           # markdown link targets
# inline references: a path ending in .md, or a bare FILENAME.md, possibly in backticks
PATH_REF = re.compile(r'([A-Za-z0-9_./\-]+\.md)')

def resolve(src_rel, target):
    """Resolve a link/reference target from src file to a repo-relative path."""
    target = target.split('#')[0].strip()
    if not target or not target.endswith('.md'):
        return None
    if target.startswith('/'):
        cand = os.path.normpath(target.lstrip('/'))
    else:
        # try relative to source dir, then relative to repo root
        srcdir = os.path.dirname(src_rel)
        cand = os.path.normpath(os.path.join(srcdir, target))
    return cand

def main():
    files = find_md_files()
    fileset = set(files)
    # basename index for bare-filename references (e.g. "WORLD_PLAN.md")
    by_base = defaultdict(list)
    for f in files:
        by_base[os.path.basename(f)].append(f)

    adj = defaultdict(set)          # undirected
    directed = defaultdict(set)     # A -> B (A references B)
    for f in files:
        adj[f]  # ensure node exists
        with open(os.path.join(REPO, f), encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        targets = set()
        for m in MD_LINK.finditer(text):
            targets.add(m.group(1))
        for m in PATH_REF.finditer(text):
            targets.add(m.group(1))
        for t in targets:
            resolved = resolve(f, t)
            hit = None
            if resolved and resolved in fileset:
                hit = resolved
            else:
                base = os.path.basename(t.split('#')[0].strip())
                cands = by_base.get(base, [])
                if len(cands) == 1:
                    hit = cands[0]
                elif len(cands) > 1 and resolved in cands:
                    hit = resolved
            if hit and hit != f:
                directed[f].add(hit)
                adj[f].add(hit)
                adj[hit].add(f)

    # BFS components on undirected graph
    seen = set()
    comps = []
    for f in files:
        if f in seen:
            continue
        comp = []
        q = deque([f])
        seen.add(f)
        while q:
            n = q.popleft()
            comp.append(n)
            for nb in sorted(adj[n]):
                if nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        comps.append(sorted(comp))
    comps.sort(key=len, reverse=True)

    orphans = [f for f in files if not adj[f]]
    indeg = defaultdict(int)
    outdeg = {f: len(directed[f]) for f in files}
    for a, bs in directed.items():
        for b in bs:
            indeg[b] += 1
    unreferenced = [f for f in files if indeg[f] == 0]  # nobody links TO it
    deadend = [f for f in files if outdeg[f] == 0]      # links to nobody

    print(f"# Markdown Connectivity Graph")
    print(f"Files: {len(files)}   Edges (undirected): {sum(len(v) for v in adj.values())//2}")
    print(f"Connected components: {len(comps)}")
    for i, c in enumerate(comps):
        head = c[0] if len(c) <= 3 else f"{c[0]} ... ({len(c)} files)"
        print(f"  [{i}] size={len(c)}: {head}")
        if len(c) < len(files) and len(c) <= 8:
            for x in c:
                print(f"        - {x}")
    print(f"\nOrphans (0 edges): {len(orphans)}")
    for o in orphans:
        print(f"  - {o}")
    print(f"\nUnreferenced (nobody links TO, but may link out): {len(unreferenced)}")
    for u in unreferenced:
        print(f"  - {u}  (out={outdeg[u]})")
    print(f"\nDead-ends (links to nobody): {len(deadend)}")
    for d in deadend:
        print(f"  - {d}  (in={indeg[d]})")

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json")+1]
        data = {
            "files": files,
            "edges": sorted([sorted([a,b]) for a in adj for b in adj[a] if a < b]),
            "directed": {a: sorted(bs) for a, bs in directed.items()},
            "components": comps,
            "orphans": orphans,
            "unreferenced": unreferenced,
            "deadend": deadend,
            "indegree": dict(indeg),
            "outdegree": outdeg,
        }
        with open(out, "w") as fh:
            json.dump(data, fh, indent=2)
        print(f"\nWrote {out}")

    if "--dot" in sys.argv:
        out = sys.argv[sys.argv.index("--dot")+1]
        with open(out, "w") as fh:
            fh.write("digraph docs {\n  rankdir=LR;\n  node [shape=box,fontsize=9];\n")
            for a, bs in directed.items():
                for b in bs:
                    fh.write(f'  "{a}" -> "{b}";\n')
            fh.write("}\n")
        print(f"Wrote {out}")

if __name__ == "__main__":
    main()
