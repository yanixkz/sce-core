# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is an experimental cognitive architecture for building decision-making AI systems.

```text
LLM → Planning → Validation → Scoring → Execution → Learning → Memory → Abstraction
```

---

## What is SCE Core

SCE Core is not just a reasoning engine.

It is a **self-improving decision system** where:

- states evolve
- constraints define valid actions
- plans are generated
- plans are validated
- plans are scored and selected
- actions are executed
- outcomes are learned
- experiences are stored
- rules are extracted

---

## Full Cognitive Loop

```text
State
↓
Planner (LLM / rules)
↓
Validator
↓
Scorer (learning + memory + rules)
↓
Selector
↓
Executor
↓
Outcome
↓
Learning
↓
Memory
↓
Abstraction (rules)
↓
Next decision is improved
```

---

## Core Components

- **Planning** — deterministic and LLM-based planners
- **Validation** — constraint checking
- **Scoring** — heuristic + learning-based evaluation
- **Execution** — tool interaction layer
- **Learning** — adaptive weight updates
- **Memory** — episodic experience storage
- **Abstraction** — rule extraction from experience
- **Agent** — full closed-loop system

---

## Demos

### Core reasoning
```bash
sce run-demo
```

### Planning
```bash
sce run-planning-demo
```

### LLM planning
```bash
sce run-llm-planning-demo
```

### Plan scoring
```bash
sce run-plan-scoring-demo
```

### Learning
```bash
sce run-learning-demo
```

### Learning + planning
```bash
sce run-learning-planning-demo
```

### Cognitive agent (full loop)
```bash
sce run-cognitive-agent-demo
```

### Tools
```bash
sce run-tools-demo
```

### Multi-agent
```bash
sce run-multi-agent-demo
```

---

## Stability formula

```text
Stab(x) = a·Coh(x) − b·Cost(x) − c·Conf(x) − d·Ent(x) + e·Support(x)
```

---

## Status

Prototype of a cognitive AI system with self-improving behavior.

---

## License

Apache 2.0
