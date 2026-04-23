# SCE Core Roadmap

## North Star

```text
Decide. Explain. Improve.
```

SCE Core is a decision engine for AI agents, with a product surface and a research program built on the same runtime loop.

## Scope of this roadmap

This document tracks implementation and delivery priorities.
For theory mapping, see [`docs/constraint_driven_stability.md`](docs/constraint_driven_stability.md).
For open research problems, see [`docs/research_program.md`](docs/research_program.md).
For historical context, see [`docs/origin.md`](docs/origin.md).
For issue/PR workstream routing, see [`docs/governance.md`](docs/governance.md).

---

## Current implemented baseline

SCE Core already includes:

- flagship demos: `supplier-risk` (product-facing), `hypothesis` (research-facing),
- decision selection over candidate plans,
- constraint filtering/validation,
- decision backbone extraction,
- prediction-error-based reliability tracking,
- episodic memory with optional PostgreSQL persistence,
- adaptive reselection influenced by memory/reliability,
- inspectable API/graph/UI surfaces (`/decide`, `/memory`, `/reliability`, `/graph`, `/ui`),
- CLI entrypoints (`sce demo`, `sce export-graph`, `sce visualize-graph`).

The demos are windows into one engine, not isolated subsystems.

---

## Practical vs research-facing layers

### Practical layer (near-term product utility)

- stable decision API contracts,
- reliable inspection outputs (memory/reliability/graph),
- predictable demo behavior for onboarding and integration,
- better operator-facing clarity in outputs and docs.

### Research-facing layer (grounded by implementation)

- constraint- and memory-aware explainability attribution,
- richer temporal reliability policies,
- replayable trajectory/audit artifacts,
- benchmark growth across multiple constrained decision scenarios.

These tracks are intentionally coupled: product surfaces expose the same mechanisms that research work extends.

---

## Staged priorities

### Stage 1 — Product clarity and inspectability hardening

- keep `/decide`, `/memory`, `/reliability`, `/graph`, `/ui` coherent and easy to integrate,
- improve inspectability contracts without API breakage,
- continue using `supplier-risk` as the most concrete onboarding path.

### Stage 2 — Replayable adaptive loop

- standardize trajectory replay/audit artifacts,
- improve continuity between decision outputs and graph/backbone evidence,
- strengthen reliability + episodic memory observability over multi-step runs.

### Stage 3 — Benchmark pair maturity

- evolve `supplier-risk` and `hypothesis` into a small shared-metrics benchmark pair,
- track where the same mechanisms transfer and where they fail,
- document comparable evaluation signals.

### Stage 4 — Broader robustness

- additional integration tests and failure-mode coverage,
- API hardening and deployment ergonomics,
- optional operational features (e.g., auth/config hardening) without changing core loop semantics.

---

## How flagship demos map to the system

### `supplier-risk`

Product-facing probe of:
- constrained selection,
- explanation of decision-carrying structure,
- reliability signal from outcomes,
- memory influence on next selection.

### `hypothesis`

Research-facing probe of the same mechanisms under different evidence/goal topology:
- competing trajectory ranking,
- inspectable evidence vs dangling context,
- explicit next-step research actions.

---

## Status summary

SCE Core has moved past a pure prototype phase into a coherent early product/research system.

Current emphasis:

```text
One engine
↓
Two flagship windows (supplier-risk, hypothesis)
↓
Reusable inspectable API/UI/graph surfaces
↓
Theory-anchored research expansion
```
