# SCE Core Research Program

This document defines the open-problems layer for SCE Core.

It is intentionally compact: the goal is to connect implemented mechanisms to current limitations and research priorities, without turning product docs into a manifesto.

Related layers:
- origin and motivation: [`docs/origin.md`](origin.md)
- CDS → SCE bridge (operational mapping): [`docs/constraint_driven_stability.md`](constraint_driven_stability.md)
- product entrypoints: [`README.md`](../README.md)

---

## Why a research program exists

SCE Core already implements a **partial operationalization of CDS for decision systems**.

Once constraints, selection, reliability, and memory are coupled in a running engine, open questions become concrete and testable:
- which structures are truly decision-carrying,
- how stability signals should evolve over time,
- and how adaptation should be measured across trajectories and domains.

This is why SCE needs a research-program layer: to make future work coherent, cumulative, and grounded in the existing loop.

---

## Current implemented core (baseline)

SCE Core currently provides:
- constrained decision selection (candidate generation, scoring, ranking),
- decision backbone extraction for explainability,
- prediction-error-based reliability tracking,
- episodic memory of executed episodes,
- adaptive reselection influenced by memory/reliability,
- graph/API/UI inspection surfaces,
- product-facing (`supplier-risk`) and research-facing (`hypothesis`) demos on the same engine.

The research agenda below starts from this implemented baseline.

---

## Research tracks and open problems

### Track A — Structural explainability under constraints

#### 1) Critical decision nodes and edges
Why it matters: backbone output is useful, but high-stakes settings also need sensitivity to *criticality* (which nodes/edges would most change the decision if perturbed).
What is missing now: current explainability isolates decision-carrying vs dangling structure, but does not rank causal leverage.
CDS/SCE link: in CDS terms, critical elements are local control points of trajectory stability under constraints.

#### 2) Constraint-aware backbone extraction
Why it matters: explanations should reflect not only graph reachability but also admissibility constraints that governed selection.
What is missing now: backbone computation is mostly structural; explicit constraint impact attribution remains limited.
CDS/SCE link: CDS treats constraints as first-class selectors of viable trajectories, so explainability should expose that role directly.

#### 3) Memory-aware backbone extraction
Why it matters: if remembered outcomes influence scoring, explanation should show when memory changed the chosen path.
What is missing now: memory affects decisions, but backbone outputs do not fully annotate memory-mediated influence on structural choice.
CDS/SCE link: retained trace is part of stability formation; explainability should include trace-to-selection pathways.

### Track B — Adaptive reliability and memory dynamics

#### 4) Reliability decay and temporal calibration
Why it matters: reliability that never decays can overfit stale episodes; reliability that decays incorrectly can erase useful signal.
What is missing now: reliability is tracked from local prediction error, but richer temporal decay/calibration models are not formalized.
CDS/SCE link: CDS is explicitly temporal; stability signals must be time-aware to remain meaningful under evolving constraints.

#### 5) Reliability-aware exploration triggers
Why it matters: adaptation requires switching between exploitation and exploration when reliability degrades or uncertainty rises.
What is missing now: exploration logic exists, but principled trigger policies tied to reliability dynamics are still limited.
CDS/SCE link: trajectory reselection is the mechanism of constrained evolution; trigger design controls when reselection pressure changes.

#### 6) Reliability-aware memory pruning
Why it matters: memory growth needs selective retention to preserve useful traces and remove misleading or obsolete ones.
What is missing now: episodic storage exists, but pruning strategies coupled to reliability quality and recency are open.
CDS/SCE link: retained trace is not just storage; it is the adaptive substrate shaping future admissible choices.

### Track C — Trajectory and graph-level analysis

#### 7) Trajectory replay and audit-grade reconstruction
Why it matters: practical governance and scientific evaluation both need reproducible reconstruction of why a path was selected.
What is missing now: inspectability surfaces exist, but complete replay/audit artifacts across decision cycles are limited.
CDS/SCE link: CDS frames stability as trajectory persistence, so trajectory-level evidence should be reconstructible end-to-end.

#### 8) Advanced abstraction and causal rule layers
Why it matters: larger decision spaces require compressed abstractions that remain faithful to constrained dynamics.
What is missing now: abstraction/rule capabilities are present in parts of the system but are not yet a mature causal layer.
CDS/SCE link: abstractions define effective constraints and state partitions; better abstractions improve tractable constrained evolution.

#### 9) Topological reasoning over decision graphs
Why it matters: graph topology can reveal bottlenecks, fragility, and stable motifs not visible from local path metrics alone.
What is missing now: graph export/inspection is implemented, but topology-aware decision analytics are still early.
CDS/SCE link: CDS concerns stability of trajectories in structured spaces; topology offers a language for global structure of those spaces.

### Track D — Generalization and scientific evaluation

#### 10) Multi-agent constrained coordination
Why it matters: many real systems involve interacting decision-makers with partially shared constraints.
What is missing now: current demos center on single-agent loops; coordination primitives are not yet formalized.
CDS/SCE link: constrained evolution in multi-agent settings introduces coupled trajectories and negotiated admissibility.

#### 11) Scientific hypothesis evaluation workflows
Why it matters: the hypothesis demo indicates a reusable pattern for evidence ranking, competing explanations, and adaptive updates.
What is missing now: the pattern is demonstrated but not yet benchmarked as a robust scientific workflow protocol.
CDS/SCE link: hypothesis evaluation is a concrete domain where constraints, reliability, memory, and reselection naturally couple.

#### 12) Generalized constrained-evolution benchmarks
Why it matters: progress requires comparable tasks, metrics, and failure modes beyond one domain demo.
What is missing now: current examples prove viability, but benchmark suites for cross-domain constrained adaptation are limited.
CDS/SCE link: CDS claims should be evaluated empirically across environments where admissibility and feedback differ.

---

## Near-term research priorities (grounded)

The next most grounded steps, given current implementation maturity:

1. **Constraint- and memory-aware backbone attribution**
   - extend explanation outputs to show how constraints and remembered episodes changed selection.
2. **Temporal reliability dynamics**
   - add explicit decay/calibration policies and evaluate impact on reselection quality.
3. **Replayable decision trajectories**
   - standardize audit artifacts from current API/graph/reliability surfaces for reproducible analysis.
4. **Focused benchmark expansion**
   - evolve `supplier-risk` and `hypothesis` into a small benchmark pair with shared metrics.

These priorities stay close to current code paths and interfaces; they do not require speculative architecture jumps.

---

## Relationship to the product surface

The two flagship demos are not isolated use cases.

- `supplier-risk` is a product-facing window into constrained selection, explainability, reliability, and memory loops.
- `hypothesis` is a research-facing window into the same loop under a different evidence/decision structure.

Together they are practical probes of one research program: computational CDS for auditable adaptive decision systems.
