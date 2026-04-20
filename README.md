# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is an experimental state-evolution engine for explainable AI memory, constraint-based reasoning, adaptive agents, and decision systems.

Most AI systems remember facts. SCE Core remembers how facts become stable, unstable, constrained, contradicted, transformed, selected, acted on, and learned from.

```text
LLMs propose. SCE decides. Agents act. Feedback adapts.
```

---

## Concept

SCE Core is based on **Constraint-Driven Stability (CDS)**:

```text
Stable structures emerge when information and energy pass through constraints over time and settle into self-reinforcing regimes.
```

For AI systems, this becomes:

```text
state + constraints + scoring → stable admissible state
```

Read more:

- [Short origin](docs/origin_short.md)
- [Full origin](docs/origin.md)

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
- goal-directed action
- adaptation from feedback

SCE Core explores a different layer: **state-evolution memory and reasoning**.

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

Agentic SCE loop:

```text
LLM → candidate states
SCE → stability selection
Goal → stopping condition
Action → world update
Feedback → learning
World → shared multi-agent state
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
    ↓
Explanation
    ↓
Goal check
    ↓
Action execution
    ↓
Feedback / learning
    ↓
World state
```

Core components:

- `State`, `Transition`, `Constraint`, `Link`, `Event`, `Attractor`, `Rule`
- `SCEScoringEngine`
- `SCEEvolver`
- `CandidateGenerator`
- `AttractorDetector`
- `GraphQueryLayer`
- `SCEExplainer`
- `GoalDrivenAgent`
- `ActionExecutor`
- `StabilityWeightLearner`
- `MultiAgentWorld`
- `MemoryRepository`
- `PostgresRepository` (Phase 1)

---

## LLM integration (experimental)

SCE Core can be used as a reasoning layer on top of LLMs:

```text
LLM → generates candidate states
SCE → filters, scores, selects, explains
```

Run demo:

```bash
sce run-llm-demo
```

Real OpenAI mode:

```bash
export OPENAI_API_KEY=your_key
export SCE_USE_OPENAI=true
sce run-llm-demo
```

If OpenAI is not configured, the demo falls back to a deterministic fake LLM.

---

## Stability formula

```text
Stab(x) = a·Coh(x) − b·Cost(x) − c·Conf(x) − d·Ent(x) + e·Support(x)
```

Where:

- `Coh` = coherence
- `Cost` = transition / maintenance cost
- `Conf` = conflict
- `Ent` = entropy / uncertainty
- `Support` = evidence, links, history

---

## Current experimental features

- Constraint DSL
- Graph Query Layer
- Real LLM adapter
- Agent loop
- Goal-driven agent
- Action layer
- Learning layer
- Multi-agent world
- PostgreSQL persistence (Phase 1)
- Origin documentation

Graph queries:

```text
TopStable(k)
Fragile(new_constraint)
NearestAttractor(state_id)
PathTo(source_id, target_id)
```

---

## Demos

### Supplier reliability

```bash
sce run-demo
```

### Conflicting memory

```bash
sce run-conflict-demo
```

### LLM memory

```bash
sce run-llm-demo
```

### Contract risk

```bash
sce run-contract-demo
```

### Agent loop

```bash
sce run-agent-demo
```

### Goal-driven agent

```bash
sce run-goal-agent-demo
```

### Action layer

```bash
sce run-action-demo
```

### Learning layer

```bash
sce run-learning-demo
```

### Multi-agent world

```bash
sce run-multi-agent-demo
```

---

## PostgreSQL backend

See:

```text
docs/postgres.md
```

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Optional OpenAI integration:

```bash
pip install openai
```

---

## Run tests

```bash
pytest
```

The test suite includes unit and smoke tests for candidate generation, attractor detection, graph queries, action execution, goal agents, learning, multi-agent world execution, and an end-to-end reasoning/action/learning flow.

---

## Example use cases

SCE Core may be useful where multiple possible states exist and the system must select the most stable one under constraints:

- AI agent memory
- LLM reasoning layers
- knowledge graphs
- decision systems
- supplier risk
- contract risk
- adaptive workflows
- explainable business logic
- multi-agent simulations

---

## Status

Research prototype.

Not production-ready.

All claims are exploratory.

---

## License

Apache License 2.0
