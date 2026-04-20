# SCE Core

**State–Constraint–Evolution Core** is an experimental state-evolution engine for explainable AI memory, constraint-based reasoning, and adaptive decision systems.

It treats data not as static records, but as evolving states under constraints.

## Core idea

Traditional computation:

```text
data + algorithm -> result
```

SCE computation:

```text
state space + constraints + scoring -> stable admissible state
```

## Stability formula

```text
stability =
    a * coherence
  - b * cost
  - c * conflict
  - d * entropy
  + e * support
```

## What this prototype includes

- in-memory repository
- states, links, constraints, transitions, events, attractors, rules
- scoring engine
- evolution engine
- explainability layer
- supplier reliability demo
- pytest tests
- PostgreSQL migration draft

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

## Run demo

```bash
sce run-demo
```

or:

```bash
python -m sce.cli run-demo
```

## Explain demo

```bash
sce explain-demo
```

## Print PostgreSQL migration

```bash
sce print-migration
```

## Run tests

```bash
pytest
```

## Current status

Research prototype / MVP draft. Not production-ready.

## Positioning

Not a database of facts, but a database of evolving states.
