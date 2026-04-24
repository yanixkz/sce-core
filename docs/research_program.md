# SCE Core Research Program

This document defines the open-problems layer for SCE Core.

It starts from implemented mechanisms and identifies what remains unresolved.
It is not a product guide and not a manifesto.

Related layers:
- Product entrypoint: [`../README.md`](../README.md)
- Theory bridge (CDS → SCE): [`constraint_driven_stability.md`](constraint_driven_stability.md)
- Historical origin: [`origin.md`](origin.md)
- Delivery sequencing: [`../ROADMAP.md`](../ROADMAP.md)

---

## Implemented baseline (starting point)

SCE Core already provides:

- constrained decision selection (candidates, scoring, ranking),
- decision backbone extraction for explainability,
- prediction-error-based reliability tracking,
- episodic memory over executed episodes,
- adaptive reselection influenced by memory/reliability,
- inspectable API/graph/UI surfaces,
- three flagship demos (`supplier-risk`, `hypothesis`, `resource-stability`) on one engine.

The research agenda below extends this baseline.

First concrete scientific scenario in-repo:
- `resource-stability` — deterministic toy population/resource regime selection under explicit constraints.

---

## Track A — Structural explainability under constraints

### 1) Critical decision nodes and edges

- **Need:** sensitivity beyond backbone membership (which elements most change the decision if perturbed).
- **Gap now:** current outputs separate carrying vs dangling structure, but not leverage ranking.
- **CDS link:** local control points of trajectory stability.

### 2) Constraint-aware backbone attribution

- **Need:** explanations should expose which active constraints shaped selection.
- **Gap now:** backbone is mostly structural; explicit constraint influence attribution is limited.
- **CDS link:** constraints are first-class trajectory selectors.

### 3) Memory-aware backbone attribution

- **Need:** explanations should show when remembered outcomes changed chosen trajectory.
- **Gap now:** memory affects scoring, but explanation does not fully annotate memory-mediated structural changes.
- **CDS link:** retained trace is part of stability formation.

---

## Track B — Reliability and episodic memory dynamics

### 4) Temporal reliability calibration/decay

- **Need:** avoid both stale overconfidence and premature forgetting.
- **Gap now:** reliability exists, but richer time-aware calibration policies are not yet formalized.
- **CDS link:** stability signals must remain meaningful across time-varying conditions.

### 5) Reliability-aware exploration triggers

- **Need:** principled exploitation/exploration switching when reliability degrades or uncertainty rises.
- **Gap now:** exploration exists, but trigger policy quality is limited.
- **CDS link:** reselection pressure control.

### 6) Reliability-aware memory pruning

- **Need:** selective retention/removal of traces as memory grows.
- **Gap now:** episodic storage exists, pruning coupled to reliability and recency remains open.
- **CDS link:** retained trace is an adaptive mechanism, not passive storage.

---

## Track C — Trajectory and graph-level analysis

### 7) Replayable trajectory reconstruction

- **Need:** reproducible path reconstruction for audits and experiments.
- **Gap now:** inspectability surfaces exist, but full replay artifacts across cycles are limited.
- **CDS link:** stability claims should be evidenced at trajectory level.

### 8) Stronger abstraction/causal rule layers

- **Need:** tractable reasoning in larger decision spaces.
- **Gap now:** abstraction/rule parts exist but are not yet a mature causal layer.
- **CDS link:** abstractions define effective constraint sets and state partitions.

### 9) Topology-aware decision graph analysis

- **Need:** detect bottlenecks/fragility/stable motifs beyond local path metrics.
- **Gap now:** graph export is available; topology-level analytics are early.
- **CDS link:** global structure of constrained trajectory spaces.

---

## Track D — Generalization and scientific evaluation

### 10) Multi-agent constrained coordination

- **Need:** many real systems involve interacting agents with partially shared constraints.
- **Gap now:** core demos are single-agent-centered.
- **CDS link:** coupled trajectories and negotiated admissibility.

### 11) Hypothesis-evaluation workflow maturity

- **Need:** move from demonstration to robust research workflow patterns.
- **Gap now:** `hypothesis` is useful but not yet a benchmark-grade protocol.
- **CDS link:** explicit coupling of constraints, reliability, memory, reselection.

### 12) General constrained-evolution benchmarks

- **Need:** comparable cross-domain metrics and failure-mode reporting.
- **Gap now:** examples prove feasibility, but benchmark suite breadth is limited.
- **CDS link:** empirical evaluation across differing admissibility/feedback environments.

---

## Near-term grounded research priorities

1. **Constraint- and memory-aware explanation outputs**
2. **Temporal reliability policy evaluation**
3. **Replay/audit artifact standardization + transparent notebook path**
4. **Shared-metric benchmark set (`supplier-risk`, `hypothesis`, `resource-stability`)**
5. **Reproducible toy-model comparisons against known dynamics where feasible**

These steps stay close to current interfaces and avoid speculative architecture jumps.

---

## Product relationship

The research program is intentionally coupled to product surfaces:

- `supplier-risk` is the product-facing window into the adaptive decision loop.
- `hypothesis` is the research-facing window into the same loop.
- `resource-stability` is the first scientific toy-model window for CDS-oriented regime viability analysis.
  - sensitivity extension: [`resource_stability_sensitivity.md`](resource_stability_sensitivity.md) for reproducible parameter-grid inspection.

Roadmap sequencing of these priorities is tracked in [`../ROADMAP.md`](../ROADMAP.md).
