# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is an experimental state-evolution engine for explainable AI memory, constraint-based reasoning, adaptive agents, planning systems, and tool-using AI.

```text
LLM → Reasoning → Planning → Validation → Scoring → Action → Tools → Learning
```

---

## What is SCE Core

SCE Core is not just a reasoning engine.

It is a **decision-making architecture** where:

- states evolve
- constraints limit possibilities
- plans are generated
- plans are validated
- plans are compared
- best strategy is executed

---

## Core Loop

```text
State
↓
LLM (candidates / plans)
↓
SCE (selection)
↓
Planner
↓
Validator
↓
Scorer
↓
Executor
↓
Tools
↓
Learning
```

---

## New capabilities (current version)

- Tool integration (ToolRegistry, ToolActionBridge)
- Deterministic planning (ToolPlanner)
- LLM-based planning (LLMPlanner)
- Plan validation (PlanValidator)
- Plan scoring and selection (PlanScorer, PlanSelector)
- Multi-step execution
- End-to-end agent loop

---

## Demos

### Basic reasoning
```bash
sce run-demo
```

### LLM reasoning
```bash
sce run-llm-demo
```

### Tools
```bash
sce run-tools-demo
```

### Planning
```bash
sce run-planning-demo
```

### LLM Planning
```bash
sce run-llm-planning-demo
```

### Plan Scoring
```bash
sce run-plan-scoring-demo
```

### Agents
```bash
sce run-agent-demo
sce run-goal-agent-demo
```

### Learning
```bash
sce run-learning-demo
```

### Multi-agent world
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

Research prototype evolving into agent system architecture.

---

## License

Apache 2.0
