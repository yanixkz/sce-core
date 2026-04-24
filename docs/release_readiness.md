# Release Readiness (Alpha)

Compact checklist for external-facing alpha releases.

## Version and naming

- Keep package version in PEP 440 alpha form (e.g., `0.1.0a0`).
- Use release tag naming `v0.1-alpha` for human-facing release notes.
- Keep README, package metadata, and API/version wording aligned.

## Release notes minimum

Each alpha release note should include:

1. Fastest quickstart path (`install -> sce demo -> scientific demos -> API -> /ui`).
2. Implemented reusable API surface (`/decide`, `/compare`, `/memory`, `/reliability`, `/graph`, `/ui`).
3. Flagship demos and what each demonstrates.
4. Explicit alpha caveat (no stable production contract yet).

## Quality gate (minimal)

- Run test suite: `pytest`.
- Confirm CLI entrypoints:
  - `sce demo`
  - `sce demo hypothesis`
  - `sce demo resource-stability`
  - `sce demo epidemic-regime`
- Confirm API docs/UI routes are reachable in local run:
  - `/docs`
  - `/ui`
