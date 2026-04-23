# Changelog

All notable changes to SCE Core are documented in this file.

The project is currently in **alpha**; compatibility may evolve between alpha releases.

## v0.1-alpha (package `0.1.0a0`) — 2026-04-23

Initial external-facing alpha surface centered on a reusable decision engine.

### Included in this alpha

- Flagship demos through CLI:
  - `sce demo` (defaults to `supplier-risk`)
  - `sce demo hypothesis`
- Reusable API endpoints:
  - `POST /decide`
  - `GET /memory`
  - `GET /reliability`
  - `GET /graph`
  - `GET /ui`
- Graph inspection commands:
  - `sce export-graph`
  - `sce visualize-graph`
- Product/theory/research bridge docs:
  - CDS → SCE mapping
  - research program framing
  - governance and roadmap context

### Notes

- This release documents and aligns the current implemented surface.
- It does **not** introduce a stable production guarantee.
