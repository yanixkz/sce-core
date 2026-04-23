# Governance and Workstream Alignment

This document keeps repository workflow lightweight while aligning issues, PRs, docs, and roadmap language with the current SCE Core shape.

## Why this exists

SCE Core is one engine with coupled surfaces:

- product-facing demos and UX/API surfaces,
- reusable API/platform contracts,
- core decision mechanisms,
- theory bridge (CDS → SCE),
- research program.

Governance should help contributors route work clearly without adding bureaucracy.

## Compact workstream model

Use one primary workstream label per issue/PR:

- `product` — flagship demos and operator-facing behavior
- `research` — open problems, theory-grounded experiments, evaluation questions
- `api` — endpoint contracts, payloads, platform integration surface
- `core` — constraint/selection/backbone/memory/reliability mechanisms
- `docs` — positioning, documentation quality, workflow clarity
- `tests` — regression coverage, hardening, reproducibility checks
- `governance` — templates, repo process, contribution flow

Optional secondary labels (when relevant):

- `roadmap` — directly tied to `ROADMAP.md` staged priorities
- `ui` — UI-specific behavior under product/API surfaces
- `good first issue` — clear starter task with bounded scope
- `breaking-change` — explicit compatibility risk requiring migration notes

## Issue and PR framing expectations

Keep framing explicit and compact:

1. State current behavior/problem.
2. State target behavior/outcome.
3. Add acceptance criteria (observable checks).
4. Mark product and/or research impact.
5. If roadmap-linked, cite the stage from `ROADMAP.md`.

Prefer focused issues and small PRs that map to one dominant workstream.

## How docs, roadmap, and issues connect

- `README.md`: project identity and main surfaces.
- `ROADMAP.md`: implementation and delivery priorities.
- `docs/research_program.md`: open research questions.
- Issues/PRs: executable units mapped to one or more of the above.

If an issue reads like a disconnected feature request, rewrite it so it references the relevant surface (product/api/core/research/docs/tests) and expected outcome.

## Contribution flow (minimal)

1. Open or select a focused issue.
2. Label by workstream (+ optional secondary labels).
3. Submit a small PR with motivation, impact, tests, and compatibility statement.
4. Avoid closing valid issues for cleanup; instead relabel/reframe surgically.

This keeps SCE Core coherent as a managed product/research program while preserving contribution simplicity.
