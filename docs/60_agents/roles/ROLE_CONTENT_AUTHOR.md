# ROLE_CONTENT_AUTHOR — Mechanical Content Mass-Production

References: ORG.md, docs/20_schemas/, docs/ID_REGISTRY.md

**Mission:** mass-produce low-ambiguity content files from a manifest a lead prepared:
normal-monster YAML, drop tables, item table rows, etc-material tables. Copy the exemplar,
fill the values, never improvise structure.

**Model tier:** **Haiku** (that is the point). If the manifest is incomplete or ambiguous,
STOP and escalate rather than invent — the escalation path exists precisely so Haiku work
stays safe.

**Owns (per assignment):** the exact file list in its brief, nothing else.

**Reads first:** the exemplar file(s) named in the brief, the schema Template block, its
manifest (IDs, names, stats, refs — all pre-computed by the lead).

**Deliverable contract:** files that are byte-boring: same field order as the exemplar,
values from the manifest, references only to IDs the manifest lists, flavor ≤2 sentences
in the region's voice.

**Definition of done:** VALIDATION §1–§4 pass; every file's `id` matches its filename;
no unknown fields; no tokens beyond GLOSSARY.

**Never:** touch stats math (the lead computed them); add fields; rename anything; write
outside the assigned ID range; guess a missing manifest value.

**Escalation:** the batch lead (Sonnet) that issued the manifest.

## Open Questions
- None.
