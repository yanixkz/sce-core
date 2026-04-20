# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

State–Constraint–Evolution Core is an experimental state-evolution engine for explainable AI memory, constraint-based reasoning, and adaptive decision systems.

Most AI systems remember facts. SCE Core remembers how facts become stable, unstable, constrained, contradicted, and transformed.

It treats data not as static records, but as evolving states under constraints.

Not a database of facts, but a database of evolving states.

---

## Why this exists

Many AI systems follow this pattern:

```text
prompt → retrieval → LLM → answer
```

This works for generation, but lacks:

- explicit system state
- constraint awareness
- conflict tracking
- explainable transitions
- stability evaluation

SCE Core explores a different layer: state-evolution memory.

---

## Core idea

Traditional computation:

```text
data + algorithm → result
```

SCE computation:

```text
state space + constraints + scoring → stable admissible state
```

Instead of only storing facts, SCE Core represents:

- states
- transitions
- constraints
- links (support, contradiction, causality)
- events
- attractors
- explanations

---

## Stability formula

```text
stability =
    a * coherence
  - b * cost
  - c * conflict
  - d * entropy
  + e * support
```

A system selects the most stable admissible state.

---

## What this prototype includes

- in-memory repository
- state / transition / constraint / link / event / attractor / rule model
- scoring engine
- evolution engine
- explainability layer
- supplier reliability demo
- pytest tests
- PostgreSQL schema draft

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

---

## Run demo

```bash
sce run-demo
```

---

## Explain demo

```bash
sce explain-demo
```

---

## Run tests

```bash
pytest
```

---

## Example use cases

- AI agent memory
- explainable decision systems
- knowledge graph reasoning
- constraint-based planning
- business process intelligence
- supply chain systems
- contract reasoning
- adaptive workflows

---

## Roadmap

See issues:

- PostgreSQL repository
- candidate generation
- attractor detection
- constraint DSL
- LLM integration

---

## Status

Research prototype.

Not production-ready.

---

## Contributing

Contributions and criticism are welcome.

See CONTRIBUTING.md.

---

## License

Apache License 2.0
