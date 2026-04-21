# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is an experimental cognitive architecture for building decision-making AI systems.

```text
Input / Voice / API
↓
LLM Intent
↓
Planning → Validation → Scoring → Execution
↓
Learning → Memory → Abstraction
```

---

## What is SCE Core

SCE Core is a **self-improving decision system** where:

- states evolve
- constraints define valid actions
- plans are generated
- plans are validated
- plans are scored and selected
- actions are executed through tools
- outcomes update learning weights
- experiences are stored as episodes
- rules are extracted from repeated successful episodes

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
Abstraction
↓
Next decision is improved
```

---

## Core Components

- **Core state model** — State, Transition, Constraint, Link, Event, Attractor, Rule
- **Scoring** — stability formula and state scoring
- **Planning** — deterministic and LLM-based planners
- **Validation** — plan and constraint checks
- **Constraint DSL** — compile safe textual constraints into predicates
- **Execution** — action and tool layers
- **Learning** — adaptive weight updates
- **Memory** — episodic experience storage
- **Abstraction** — rule extraction from experience
- **Voice OS bridge** — text/voice intent to cognitive agent
- **FastAPI API** — `/health` and `/ask`
- **LLM providers** — OpenAI and Anthropic JSON clients
- **Graph queries + export** — structural queries and JSON graph export

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Optional extras:

```bash
pip install -e .[api,openai]
pip install -e .[api,anthropic]
```

---

## Run tests

```bash
pytest
```

---

## Run API

```bash
uvicorn sce.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"text":"check supplier risk"}'
```

With real LLM intent parsing:

```bash
export OPENAI_API_KEY=...
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"text":"check supplier risk","use_llm_intent":true,"provider":"openai"}'
```

---

## CLI demos

```bash
sce run-demo
sce run-conflict-demo
sce run-llm-demo
sce run-llm-planning-demo
sce run-contract-demo
sce run-agent-demo
sce run-goal-agent-demo
sce run-action-demo
sce run-learning-demo
sce run-learning-planning-demo
sce run-multi-agent-demo
sce run-tools-demo
sce run-planning-demo
sce run-plan-scoring-demo
sce run-cognitive-agent-demo
sce run-llm-voice-demo
sce explain-demo
sce print-migration
sce export-graph
```

---

## Stability formula

```text
Stab(x) = a·Coh(x) − b·Cost(x) − c·Conf(x) − d·Ent(x) + e·Support(x)
```

---

## Constraint DSL (safe predicates)

You can define constraints as strings and compile them without `eval`/`exec`:

```python
from sce.core.constraint_dsl import compile_constraint_dsl
from sce.core.types import Constraint, State

predicate = compile_constraint_dsl(
    '(late_delivery_rate <= 0.30 AND breach_reported == false) OR tier == "gold"'
)

constraint = Constraint(name="supplier_policy", predicate=predicate)
ok = constraint.is_satisfied(
    State("supplier", {"late_delivery_rate": 0.25, "breach_reported": False, "tier": "silver"})
)
```

Supported syntax:

- comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`
- boolean operators: `AND`, `OR`, `NOT`
- parentheses
- numbers, quoted strings, booleans (`true`, `false`)
- identifiers are read from `State.data`

---

## State graph export

Export an inspectable state graph JSON:

```bash
sce export-graph
```

The output contains:

- `nodes` with `state_id`, `stability`, `is_attractor`, and per-constraint satisfaction
- `edges` with source/target state ids, relation type, strength, and directed flag

---

## Current gaps / next work

- Persistent memory in PostgreSQL
- PostgreSQL integration tests in CI
- Advanced abstraction / causal rules
- Production API hardening

---

## Status

Prototype of a cognitive AI system with self-improving behavior.

---

## License

Apache 2.0
