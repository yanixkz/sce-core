# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is an experimental state-evolution engine for explainable AI memory, constraint-based reasoning, and adaptive decision systems.

Most AI systems remember facts. SCE Core remembers how facts become stable, unstable, constrained, contradicted, and transformed.

It treats data not as static records, but as evolving states under constraints.

```text
LLMs propose. SCE decides.
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

SCE Core explores a different layer: **state-evolution memory**.

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
```

Core components:

- `State`, `Transition`, `Constraint`, `Link`, `Event`, `Attractor`, `Rule`
- `SCEScoringEngine`
- `SCEEvolver`
- `CandidateGenerator`
- `AttractorDetector`
- `GraphQueryLayer`
- `SCEExplainer`
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

## v0.2 features

Current experimental v0.2 direction includes:

- Constraint DSL
- Graph Query Layer
- Contract Risk demo
- Real LLM adapter
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

---

## Status

Research prototype.

Not production-ready.

All claims are exploratory.

---

## License

Apache License 2.0
