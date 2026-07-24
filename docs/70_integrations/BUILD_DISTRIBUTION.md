# BUILD_DISTRIBUTION.md — Build Pipeline, Versioning, Patching & Storefront Targets

References: docs/00_vision/GLOSSARY.md, docs/00_vision/SCOPE.md, docs/VALIDATION.md,
docs/10_systems/PERSISTENCE.md, docs/30_engineering/ENGINEERING_STANDARDS.md,
docs/60_agents/roles/ROLE_INTEGRATION_ENGINEER.md, README.md

Owner doc for **how a future Godot build of Rebillion gets from this design tree's committed
content to a signed, patchable artifact on a player's machine**. This run ships no code and no
CI (`docs/00_vision/SCOPE.md`); everything below is a design the coding-pass engineer estimates
and implements against a real game project repo that does not exist yet. It does not re-derive
save data ownership (`docs/10_systems/PERSISTENCE.md` owns that) or content validity
(`docs/VALIDATION.md` owns that) — it only says how those pieces get built, versioned, and
delivered.

## 1. Build pipeline concept

Source of truth for the pipeline is a **future game project repo** (not this one), which vendors
or submodules this design tree read-only and layers `20_schemas/*` Resource classes,
`30_engineering/ENGINEERING_STANDARDS.md` project structure, and engine code on top. This repo
is never built directly; it is an input.

Pipeline shape, high level:

1. **Content ingest** — `50_content/*.yaml` is validated against the full `docs/VALIDATION.md`
   contract (checks 1–6) by a CI-run content validator — the same rules this doc's owning role
   cites as the implementation target for that validator (`docs/30_engineering/
   ENGINEERING_STANDARDS.md`'s "Testing/validation" clause). A failing batch blocks the build;
   there is no "build with warnings" path for validation failures.
2. **Content conversion** — validated YAML is converted to `.tres` Resource files (a build-time
   tool script per ENGINEERING_STANDARDS.md's data layer, not a runtime step).
3. **Design-tree version pin** — the build records the exact commit hash of this design-doc tree
   that its packed content was generated from, alongside the game project repo's own commit. This
   pin is metadata only (embedded in the build manifest, not gameplay-readable) so any bug report
   or content discrepancy can be traced to an exact doc-tree state, even after this tree moves on.
4. **Engine export** — CI runs Godot's export pipeline per platform using export presets
   maintained in the game project repo (out of this tree's scope to author).
5. **Signing** — each platform artifact is signed with the appropriate platform credential
   (code-signing certificate for Windows/macOS; storefront-managed signing where the storefront
   requires it) before upload.
6. **Artifact publish** — signed, versioned artifacts are pushed to the target release channel
   (§5) on each configured storefront/distribution target (§4).

**Platform priority (decision, pending owner sign-off):** Windows first (largest expected
platform-agnostic 2D-platformer audience and simplest signing story), then macOS, then Linux,
built in that order per milestone rather than all three from day one. This ordering is a proposed
default, not a commitment — see Open Questions.

## 2. Versioning — three distinct numbers

Three version numbers exist, deliberately kept separate because they change at different rates
and for different reasons:

| Version | Format | What it tracks | Who bumps it, and when |
|---|---|---|---|
| `client_version` | semantic (`MAJOR.MINOR.PATCH`) | The engine build/executable: code, scenes, UI | The coding-pass engineer, on every release-channel promotion (§5); `PATCH` for hotfixes, `MINOR` for feature/content-batch releases, `MAJOR` for save-breaking or system-breaking changes |
| `content_version` | monotonic integer | The packed `50_content/*` snapshot baked into a given `client_version` build, plus its design-tree commit pin (§1.3) | Bumped automatically by the build pipeline every time content is re-ingested and re-packed, whether or not `client_version` changes |
| `save_version` | monotonic integer | The on-disk save file shape (`docs/10_systems/PERSISTENCE.md` §8) | Bumped by the coding-pass engineer only when a save-file field is added, removed, or reinterpreted — independent of both numbers above |

`client_version` and `content_version` can and will diverge often (a hotfix bumps
`client_version` without touching content; a content-only balance patch can, in principle, bump
`content_version` without a new executable if the engine supports hot-reloadable data — a
capability this doc does not assume exists and does not design). `save_version` is the
conservative one: most releases do not touch it at all.

**Compatibility rules:**
- **Solo build (current design target):** a save with a `save_version` lower than the running
  build's runs the migration step defined in `docs/10_systems/PERSISTENCE.md` §8 before any
  system reads it; a save with a *higher* `save_version` than the running build refuses to load
  (PERSISTENCE.md's rule — restated here only to anchor it against `client_version`, not
  re-derived). A save's `content_version` is recorded for diagnostics but does not itself gate
  load; a referenced ID that no longer exists in the current `content_version` is a migration
  concern, not a build-pipeline concern.
- **Future online build:** once a server exists, it becomes the arbiter of minimum acceptable
  `client_version` (§3) — the solo build's local-only compatibility rules above stop being
  sufficient and the server-driven gate in §3 takes over.

## 3. Patching

The interim solo build ships **storefront-native, launcher-less delta patching** — the target
storefront's own client (Steam-style: download only the changed bytes between two builds) is the
update mechanism; this doc does not design a custom launcher or patcher, because the storefronts
under consideration (§4) already provide one and duplicating it would be scope creep against
`docs/00_vision/SCOPE.md`.

- **Patch cadence stance:** content/balance patches follow the phase-batch cadence this design
  tree already produces content in (region-scoped batches); no fixed calendar cadence is
  committed here. Hotfixes (crash, save-corruption, exploit) ship out-of-cadence as soon as they
  clear the dev→stable path (§5), bypassing the normal batch rhythm but not the validation gate.
- **Hotfix path:** a hotfix is a `PATCH`-level `client_version` bump that skips playtest soak time
  when the fix addresses data loss, a crash, or an economy exploit; it still passes the full
  VALIDATION.md-implementing CI gate — "urgent" never means "unvalidated."
- **Future online build addition:** once a server exists, it adds a **server-driven version
  gate** on top of storefront patching — the server refuses connections from a `client_version`
  it has deprecated, forcing the storefront client to fetch the update before play resumes. This
  is additive to, not a replacement for, the storefront delta-patch mechanism above.

## 4. Storefront targets

No storefront commitment is made in this design tree — storefront fees, revenue share, and
review timelines are owner-priced decisions (Open Questions). Candidates and their tradeoffs, for
the owner to weigh:

| Storefront | Tradeoff sketch |
|---|---|
| Steam | Largest reach and best-known delta-patch/branch tooling (playtest branches fit §4's demo need directly); highest review-process overhead and a revenue cut |
| itch.io | Fastest to publish, friendliest for a solo/interim build and demo distribution, weakest built-in patch-delta tooling (uploads are closer to full-replace) |
| Epic Games Store | Strong terms for smaller studios historically; smaller player-discovery surface than Steam for a niche 2D platformer |
| Direct download (own site) | Full control, no storefront gate at all; the team owns patching, signing distribution, and payment infrastructure outright — the highest engineering burden of the options |

**Demo/playtest distribution for the interim solo build:** ship a playtest build via whichever
storefront's playtest-branch feature is cheapest to stand up first (Steam playtest branches, or
an itch.io devlog/demo page as a lower-friction fallback) — this is separate from the eventual
full-release storefront choice and can precede it.

## 5. Release channels

Three channels, each a `client_version` + `content_version` pairing, gated by promotion rules:

| Channel | Audience | Promotion gate to reach it |
|---|---|---|
| `dev` | Internal only | Passes the VALIDATION.md-implementing CI gate (content) and compiles/exports cleanly (client) |
| `playtest` | Opted-in external testers, via the storefront playtest branch (§4) | `dev` green for N consecutive builds (N owner-set) plus a manual smoke run: launch, create a character, reach the first town, take one hit, save/reload |
| `stable` | General release | `playtest` soak with no open crash/save-corruption reports, plus the same smoke run re-run on the exact artifact being promoted (not a re-build) |

Promotion is one-directional (`dev` → `playtest` → `stable`); a stable-channel regression is
fixed forward as a new hotfix build re-entering at `dev`, never by demoting the channel pointer
backward onto an older artifact.

## 6. External dependency failure modes

Per this role's deliverable contract, every external dependency below states its failure mode and
an "implemented when" trigger — none of these exist yet; this section is what the coding pass
must design operational fallbacks for, not a working runbook itself.

| Dependency | Failure mode if unavailable | Implemented when |
|---|---|---|
| CI provider (build/export runner) | No new artifacts can be produced or validated; last-known-good artifact on each channel keeps serving players unaffected | The game project repo exists and a CI provider is chosen (Open Question) |
| Code-signing authority/certificate | Unsigned builds may trigger OS/storefront security warnings or be rejected outright at upload; existing signed artifacts are unaffected | A signing certificate is procured for the platform(s) in active use |
| Storefront upload/review API | New builds cannot reach players on that storefront until the outage/review clears; other channels/storefronts unaffected if multi-target | A storefront is selected and its publishing API/tooling is integrated (§4 Open Question) |
| Design-tree repo (this repo, as a build input) | Content ingest (§1.1) cannot pull a newer pin; the build continues against its last successful pin | Always available today; risk is process (wrong commit pinned), not infrastructure |

## Open Questions
- Platform export priority (§1: Windows → macOS → Linux) is a proposed default, not confirmed —
  owner sign-off needed, including whether Linux ships at all for v1.
- Storefront selection (§4) is entirely owner-priced (fees, revenue share, review overhead) —
  no candidate is committed; needs an owner decision before any CI export-preset work begins.
- CI provider and code-signing certificate vendor are unselected — both gate the failure-mode
  rows in §6 and should be chosen together with the storefront decision, since some storefronts
  bundle signing/build tooling.
- Whether `content_version` can ever bump without a paired `client_version` bump (i.e., true
  hot-reloadable data at runtime) is unresolved; this doc assumes no for now and treats every
  content change as riding along with a client build.
- Exact playtest soak length (`N` builds in §5) and the smoke-run script's full step list are
  unspecified pending the coding pass; a single-paragraph sketch is given here as a placeholder,
  not a full QA procedure.
