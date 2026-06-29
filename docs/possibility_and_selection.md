# Possibility Spaces and Stability Selection

This document introduces a conservative framing layer for Constraint-Driven
Stability (CDS) and SCE Core:

```text
Possibility Space → Constraints → Dynamics → Selection → Persistence
```

The purpose is not to expand CDS into a universal theory. The purpose is to make
explicit a research perspective that is already present in the implemented toy
models: many candidate states are possible, only some are admissible under
constraints, fewer remain viable under dynamics, and a smaller subset persists
across repeated evaluation.

## The Library of Babel problem

Borges' *Library of Babel* is a useful metaphor for a maximal possibility space:
if every possible text exists somewhere, then truth, usefulness, and coherence are
not produced by possibility alone.

A maximal library contains coherent statements, false statements, contradictions,
near misses, accidental patterns, and overwhelming noise. The scientific lesson
for SCE Core is modest: generation is not enough. A system that can enumerate or
sample possibilities still needs inspectable mechanisms for filtering, ranking,
and retaining candidates.

In this framing, the central problem is selection under constraints rather than
unbounded generation.

## Possibility spaces

A **possibility space** is the set of candidate states, actions, regimes, or
hypotheses available under a given representation.

Examples in or near the current project include:

- candidate plans for an agent decision task,
- candidate hypotheses in a research workflow,
- candidate population/resource regimes in a toy ecology,
- candidate epidemic response regimes in a toy public-health model,
- candidate graph trajectories under explicit constraints.

A possibility space may be finite, continuous, generated lazily, or represented
only by a candidate sampler. SCE Core currently uses small and inspectable spaces
so that constraints, scoring, and explanations remain auditable.

## Constraints

Constraints define which parts of a possibility space are admissible or relevant
for a given experiment. They may encode resource limits, safety requirements,
capacity bounds, intervention limits, reliability thresholds, or domain-specific
rules.

In CDS-oriented work, constraints should be stated explicitly because they shape
what can be selected. A candidate that looks stable under one constraint set may
be fragile or inadmissible under another.

## Dynamics

Dynamics describe how candidate states change, compete, degrade, reinforce, or
are re-evaluated over time. In the current repository, these dynamics are
intentionally simple: deterministic toy-model updates, scoring rules,
reselection, memory effects, and reliability updates.

This simplicity is a feature of the research method. It keeps the mechanism
inspectable and avoids implying that the framework already models open-ended
physical, biological, social, or cognitive reality.

## Stability selection

**Stability selection** is the process by which constraints and dynamics reduce a
large possibility space to candidates that are viable enough to be selected,
reselected, or retained.

Operationally, SCE Core studies stability selection through mechanisms such as:

- candidate generation or enumeration,
- admissibility checks,
- stability-oriented scoring,
- ranking and choice,
- reliability updates from observed outcomes,
- episodic memory that can influence future reselection,
- decision-backbone extraction for inspectable explanations.

The current scoring functions are working approximations for constrained
experiments, not claims about universal laws.

## Persistent structures

A **persistent structure** is a candidate pattern, regime, plan, hypothesis, or
trajectory that survives relevant selection pressure beyond immediate generation.
Persistence may mean that a candidate remains viable across repeated runs,
continues to satisfy constraints after perturbation, receives stable reliability
signals, or leaves memory traces that support future reselection.

Persistence should not be equated with truth, optimality, or inevitability. In
SCE Core, it is an operational property measured within a specific model,
constraint set, and evaluation protocol.

## Relation to CDS

CDS can be framed as the study of how stable or persistent structures appear
within constrained dynamical settings. The possibility-space perspective makes
the selection problem explicit:

```text
large candidate space
→ explicit constraints
→ model dynamics and scoring
→ stability selection
→ measured persistence or failure
```

This connects directly to CDS without requiring grand claims. It asks how
constraints and dynamics alter the distribution of selected outcomes in toy
models and decision workflows.

## Relation to SCE Core

SCE Core implements small, inspectable versions of this framing.

| Framing concept | SCE Core operational counterpart |
| --- | --- |
| Possibility space | candidate actions, regimes, hypotheses, or graph paths |
| Constraints | explicit context limits, admissibility checks, and policy rules |
| Dynamics | scoring, deterministic demo updates, reselection, reliability, memory |
| Selection | ranked choices, viability checks, stability-oriented decisions |
| Persistence | repeated viability, reliability traces, memory-supported reselection |
| Explanation | decision backbone, graph export, API/UI inspection surfaces |

The repository should therefore be read as a computational framework and research
program for constrained experiments, not as a completed theory of nature.

## Research question

The guiding research question is:

> Why do some structures persist while most possibilities disappear?

A narrower operational version is:

> Under explicit constraints and toy dynamics, which candidates are selected,
> which disappear, and what measurable signals distinguish persistent structures
> from transient possibilities?

## Philosophical version

The philosophical version is:

> What selects reality from possibility?

Within this repository, that question is treated as motivation only. The
scientific work remains limited to computational frameworks, toy models,
inspectable mechanisms, and constrained experiments.

## Explicit non-claims

This document does not claim that CDS or SCE Core:

- explains reality as a whole,
- provides a theory of consciousness,
- replaces physics, biology, economics, or social science,
- discovers universal laws of selection,
- proves that persistence implies truth or value,
- validates real-world epidemiological, ecological, or market predictions from
  the current toy models.

The claim is narrower: possibility spaces, constraints, dynamics, selection, and
persistence provide a useful vocabulary for organizing SCE Core experiments and
future CDS research.

## Practical checklist for future examples

Each new CDS/SCE example should state:

1. What possibility space is being represented?
2. Which constraints shape admissibility?
3. What dynamics update or transform candidates?
4. What selection mechanism ranks or filters candidates?
5. What counts as persistence, instability, or disappearance?
6. Which claims are explicitly out of scope?
