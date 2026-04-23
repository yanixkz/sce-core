# Constraint-Driven Stability (CDS) → SCE Core Bridge

This document defines the theory-to-implementation bridge for SCE Core.
It maps CDS concepts to mechanisms that are already implemented.

Related layers:
- Product entrypoint: [`../README.md`](../README.md)
- Historical origin: [`origin.md`](origin.md)
- Open research agenda: [`research_program.md`](research_program.md)
- Delivery roadmap: [`../ROADMAP.md`](../ROADMAP.md)

---

## CDS in compact form

Constraint-Driven Stability (CDS) treats stability as a selected trajectory under constraints over time.

Minimal decomposition:
- **Constraints** define admissible transitions.
- **Trajectory candidates** compete under scoring/feasibility.
- **Selection** chooses one trajectory now.
- **Retained trace** stores what happened.
- **Adaptive reselection** updates later choices from retained outcomes.

---

## CDS interpreted as a decision loop

For decision systems:

1. define admissible transitions,
2. generate candidate plans/actions,
3. select under constraints and available evidence,
4. observe outcomes and prediction error,
5. retain outcome/reliability traces,
6. reselect with updated memory/reliability pressure.

This is a disciplined engineering framing, not a claim of a complete intelligence theory.

---

## Operational mapping (CDS → SCE Core)

| CDS concept | SCE Core mechanism |
| --- | --- |
| Constraints / admissibility | Constraint DSL + plan validation filter infeasible transitions before selection. |
| Trajectory selection | Candidate generation + scoring + ranking choose the current plan/action. |
| Structural carrier / decision backbone | Backbone extraction identifies evidence-to-target structure that carried the selected decision. |
| Empirical stability signal | Reliability tracking from local prediction error quantifies trajectory quality. |
| Retained adaptive trace | Episodic memory stores executed episodes with outcome/reliability metadata. |
| Adaptive reselection | Later scoring incorporates remembered traces and reliability signals. |
| Inspectability | CLI/API/UI + graph export expose decision path, backbone, memory, and reliability surfaces. |

Scope note: this table covers implemented behavior and current public surfaces, not speculative future architecture.

---

## What is already implemented

SCE Core already operationalizes an end-to-end constrained adaptive loop:

- constrained candidate ranking and selection,
- structural explainability via decision backbone,
- reliability tracking from observed outcomes,
- episodic memory with optional persistence,
- memory/reliability effects on later decisions,
- inspectable graph/API/UI surfaces,
- product-facing and research-facing demos on one engine.

---

## Boundary to research layer

This bridge intentionally stops at mechanism mapping.

Open problems that follow from this mapping (and are not yet fully solved) are tracked in [`research_program.md`](research_program.md), including:
- constraint- and memory-aware backbone attribution,
- temporal reliability dynamics,
- replayable decision trajectories,
- topology-aware graph reasoning,
- broader constrained-evolution benchmarks.

---

## Why this bridge matters

It keeps terminology stable across product and research discussions:
- constraints,
- trajectory selection,
- structural carrier/backbone,
- reliability,
- episodic memory,
- adaptive reselection,
- inspectability.

With these terms fixed, README/API usage, roadmap planning, and research priorities can stay aligned without duplicate or conflicting explanations.
