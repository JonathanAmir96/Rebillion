# tools/

`validate.py` — the batch validator `docs/VALIDATION.md`'s batch protocol requires. Implements
checks 1–4 (forbidden tokens, referential integrity for doc links + content front-matter, schema
conformance, ID uniqueness/range) plus the phase-gate doc-structure check (H1 + `## Open
Questions`). Checks 5–6 (world-graph soundness, asset contract) land with the Phase D
world-graph reconciler.

Usage:

```
python3 tools/validate.py                    # whole tree
python3 tools/validate.py docs/50_content/monsters   # one content batch
```

Exit 0 = pass; exit 1 = at least one FAIL (a failing batch is fixed or reverted, never landed —
VALIDATION.md batch protocol). The forbidden-token list and ID blocks mirror their canonical
owners (`docs/VALIDATION.md` §1, `docs/ID_REGISTRY.md`); update them together in one commit.
