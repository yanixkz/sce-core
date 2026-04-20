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

---

## LLM integration (experimental)

SCE Core can be used as a reasoning layer on top of LLMs:

```text
LLM → generates candidate states
SCE → filters, scores, selects, explains
```

In other words:

```text
LLMs propose. SCE decides.
```

Run demo:

```bash
sce run-llm-demo
```

---

## Architecture

```text
Current state
    ↓
CandidateGenerator (rules / LLM / events / graph)
    ↓
Candidate states
    ↓
Constraint filtering
    ↓
Stability scoring
    ↓
Selected transition
    ↓
Next state / attractor
```

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

---

## Demos

### Conflict demo

```bash
sce run-conflict-demo
```

### LLM demo

```bash
sce run-llm-demo
```

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

---

## Run tests

```bash
pytest
```

---

## Status

Research prototype.

Not production-ready.

---

## License

Apache License 2.0
