# SCE Core Roadmap

## North Star

```text
Possibility Space
↓
Constraints
↓
Dynamics
↓
Selection
↓
Persistence
```

SCE Core is a computational framework for studying Constraint-Driven Stability (CDS): how constraints and dynamics select persistent structures from larger possibility spaces. Its decision engine, API, memory, and reliability features are applied surfaces on the same runtime loop.

## Scope of this roadmap

This document tracks implementation and delivery priorities.
For theory mapping, see [`docs/constraint_driven_stability.md`](docs/constraint_driven_stability.md).
For open research problems, see [`docs/research_program.md`](docs/research_program.md).
For historical context, see [`docs/origin.md`](docs/origin.md).
For issue/PR workstream routing, see [`docs/governance.md`](docs/governance.md).

---

## Current implemented baseline

SCE Core already includes:

- applied demo: `supplier-risk`,
- research-facing demo: `hypothesis`,
- scientific toy models: `resource-stability`, `epidemic-regime`, `cyrillic-babel`, and `selection-landscape`,
- decision selection over candidate plans,
- constraint filtering/validation,
- decision backbone extraction,
- prediction-error-based reliability tracking,
- episodic memory with optional PostgreSQL persistence,
- adaptive reselection influenced by memory/reliability,
- inspectable API/graph/UI surfaces (`/decide`, `/compare`, `/memory`, `/reliability`, `/graph`, `/ui`),
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
- benchmark growth across constrained decision and scientific toy scenarios.

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

### Stage 3 — Scientific example maturity

- maintain implemented scientific examples: Resource Stability, Epidemic Regime, Cyrillic Babel, and Selection Landscape,
- evolve applied, research-facing, and scientific toy examples into a small shared-metrics benchmark set,
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

### `resource-stability`

Scientific toy probe of:
- population/resource regime viability under explicit constraints,
- deterministic scoring/ranking of candidate regimes,
- selected carrying regime and non-carrying trajectories,
- reproducible baseline for notebook-based comparative modeling.

### `epidemic-regime`

Scientific toy probe of:
- deterministic epidemic regime candidates under explicit constraints,
- stability ranking under spread/capacity/intervention-cost pressures,
- selected regime with transparent non-selected alternatives,
- explicit toy-model disclaimer to avoid epidemiological overclaiming.

### `cyrillic-babel`

Scientific toy probe of:
- finite Cyrillic alphabet possibility space,
- deterministic normalization and selection address,
- transparent toy selection pressure over sampled candidates,
- reproducible persistent pattern without language-understanding claims.

### `selection-landscape`

Scientific toy probe of:
- deterministic candidate population sampled from a toy possibility space,
- explicit scoring dimensions and weighted stability distribution,
- best, median, and worst candidates for ranking context,
- bridge toward future Constraint Sweep Explorer experiments.

---

## Status summary

SCE Core has moved past a pure prototype phase into a coherent early product/research system.

Current emphasis:

```text
One engine
↓
Applied: supplier-risk
↓
Research-facing: hypothesis
↓
Scientific toy models: resource-stability, epidemic-regime, cyrillic-babel, selection-landscape
↓
Reusable inspectable API/UI/graph surfaces
↓
Theory-anchored research expansion
↓
Planned scientific examples: Constraint Sweep Explorer, Persistence Over Time, Stability Basin Explorer
```

## Planned scientific examples

- **Constraint Sweep Explorer:** vary constraint strength and inspect how selection changes across a candidate population.
- **Persistence Over Time:** replay or rerun toy systems to inspect persistence signals beyond one-step selection.
- **Stability Basin Explorer:** map local neighborhoods around selected candidates to study robustness under perturbation.

## Documentation audit note

Top-level roadmap documentation was synchronized after PRs #73–#75 to include `cyrillic-babel`, Cyrillic Babel v2 selection pressure, and `selection-landscape`; to list planned Constraint Sweep Explorer, Persistence Over Time, and Stability Basin Explorer work; and to preserve conservative toy-model and non-claim language.
