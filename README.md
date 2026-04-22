# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is an experimental cognitive architecture for building explainable, adaptive, and controlled decision-making AI systems.

```text
Input / Voice / API
↓
LLM Intent
↓
Planning → Validation → Scoring → Execution
↓
Learning → Memory → Abstraction
↓
Decision Backbone → Controlled Evolution → Graph Observability
```

---

## Quick visual demo

SCE Core can be inspected from the terminal:

```bash
sce run-adaptive-agent-demo-pretty
sce run-decision-backbone-demo-pretty
sce run-controlled-evolution-demo-pretty
sce run-reliability-aware-planning-demo-pretty
sce visualize-graph
```

The adaptive demo shows an agent changing its plan after episodic memory shifts the decision score.

The decision backbone demo shows which reasoning nodes actually carry a decision and which branches are dangling.

The controlled evolution demo shows how local prediction errors accumulate into trajectory-level reliability.

The reliability-aware planning demo shows reliability changing the selected plan.

More visual/demo commands are documented in [`docs/VISUAL_DEMO.md`](docs/VISUAL_DEMO.md).

---

## What is SCE Core

SCE Core is a **self-improving decision system** where:

- states evolve
- constraints define valid actions
- plans are generated
- plans are validated
- plans are scored and selected
- planners can explore alternatives instead of only exploiting the current top score
- trajectory reliability can influence plan selection
- actions are executed through tools
- outcomes update learning weights
- experiences are stored as episodes
- memory biases future planning decisions
- reasoning graphs are reduced to decision-carrying backbones
- dangling branches can be exposed for audit and pruning
- local prediction errors are tracked across decision trajectories
- trajectory reliability can be estimated from accumulated step error
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
Scorer (learning + memory + reliability)
↓
Selector (exploit / explore)
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
Decision Backbone
↓
Controlled Evolution
↓
Next decision is improved, explainable, and reliability-aware
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
- **Memory** — episodic experience storage with pluggable repositories
- **Persistent memory** — EpisodeRepository, InMemoryEpisodeRepository, PostgresEpisodeRepository
- **Memory-aware planning** — remembered outcomes bias future plan selection
- **Exploration-aware selection** — optional epsilon-style exploration of non-top candidate plans
- **Reliability-aware planning** — trajectory reliability can rerank candidate plans
- **Decision backbone** — graph extraction of decision-carrying nodes vs dangling reasoning branches
- **Controlled evolution** — local prediction error tracking and trajectory reliability reports
- **Abstraction** — rule extraction from experience
- **Graph observability** — JSON graph export and ASCII visualization
- **Voice OS bridge** — text/voice intent to cognitive agent
- **FastAPI API** — `/health` and `/ask`
- **LLM providers** — OpenAI and Anthropic JSON clients

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
sce run-memory-aware-planning-demo
sce run-adaptive-agent-demo
sce run-adaptive-agent-demo-pretty
sce run-exploration-demo
sce run-exploration-demo-pretty
sce run-decision-backbone-demo
sce run-decision-backbone-demo-pretty
sce run-controlled-evolution-demo
sce run-controlled-evolution-demo-pretty
sce run-reliability-aware-planning-demo
sce run-reliability-aware-planning-demo-pretty
sce run-multi-agent-demo
sce run-tools-demo
sce run-planning-demo
sce run-plan-scoring-demo
sce run-cognitive-agent-demo
sce run-llm-voice-demo
sce explain-demo
sce print-migration
sce export-graph
sce export-graph --out graph.json
sce visualize-graph
sce visualize-graph --out graph.txt
```

---

## Adaptive agent demo

Run:

```bash
sce run-adaptive-agent-demo-pretty
```

The demo shows a complete decision loop:

```text
candidate plans → scoring → execution → memory → re-scoring → changed plan
```

It prints:

- before-learning scores
- execution trace
- learning event
- after-learning scores
- why the decision changed

This is the quickest way to see SCE Core behaving as an adaptive decision system.

---

## Decision backbone demo

Run:

```bash
sce run-decision-backbone-demo-pretty
```

The demo shows a supplier-risk reasoning graph and separates:

- nodes that carry the decision from evidence to target action
- dangling branches that are connected but do not influence the target decision

Conceptually:

```text
forward  = nodes reachable from evidence
backward = nodes that can reach the decision target
backbone = forward ∩ backward
dangling = forward - backbone
```

This adds structural explainability on top of scores and generated explanations.

More details: [`docs/DECISION_BACKBONE.md`](docs/DECISION_BACKBONE.md).

---

## Controlled evolution demo

Run:

```bash
sce run-controlled-evolution-demo-pretty
```

The demo tracks local prediction error across a decision trajectory:

```text
predicted step value → actual observed value → step error → cumulative reliability
```

This adds a practical control layer: SCE can reason not only about which decision was selected, but also how reliable the stepwise evolution was.

More details: [`docs/CONTROLLED_EVOLUTION.md`](docs/CONTROLLED_EVOLUTION.md).

---

## Reliability-aware planning demo

Run:

```bash
sce run-reliability-aware-planning-demo-pretty
```

The demo shows trajectory reliability influencing plan selection:

```text
base score + memory bias + reliability bonus → selected plan
```

This closes the loop between controlled evolution and planning: reliability is no longer only observed after the fact; it can affect the next decision.

---

## Memory-aware planning demo

Run:

```bash
sce run-memory-aware-planning-demo
```

The demo records past decision episodes, scores candidate plans with `EpisodeMemory.plan_bias(...)`, and selects the plan with the strongest positive memory signal.

Example shape:

```json
{
  "remembered_episode_count": 3,
  "candidate_scores": [
    {"plan_name": "slow_monitoring_plan", "memory_bias": -0.8},
    {"plan_name": "escalation_plan", "memory_bias": 0.9}
  ],
  "selected_plan": "escalation_plan"
}
```

---

## Exploration-aware planning

`MemoryAwarePlanner` supports optional exploration:

```python
import random
from sce.core.planning import MemoryAwarePlanner, ToolPlanner

planner = MemoryAwarePlanner(
    ToolPlanner(),
    memory,
    exploration_rate=0.1,
    rng=random.Random(42),
)
```

When exploration is enabled, the planner can occasionally try a non-top plan. This helps the agent discover useful alternatives instead of always exploiting the current highest-scoring plan.

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

## Persistent episodic memory

SCE Core supports pluggable episodic memory repositories:

- `EpisodeRepository` protocol
- `InMemoryEpisodeRepository`
- `PostgresEpisodeRepository`
- `Episode.to_dict()` / `Episode.from_dict()` JSON serialization
- optional persistence through `EpisodeMemory(repository=...)`

Example:

```python
from sce.core import EpisodeMemory, InMemoryEpisodeRepository

repo = InMemoryEpisodeRepository()
memory = EpisodeMemory(repository=repo)
```

PostgreSQL support includes an `episodes` migration table and JSONB storage for episode payloads. Print the migration SQL with:

```bash
sce print-migration
```

---

## State graph export

Export the current state graph to JSON from the CLI:

```bash
sce export-graph
sce export-graph --out graph.json
```

## ASCII graph visualization

Render a terminal-friendly ASCII view of the current state graph:

```bash
sce visualize-graph
sce visualize-graph --out graph.txt
```

## Current gaps / next work

- Constraint-aware decision backbone extraction
- Memory-aware decision backbone extraction
- Reliability-aware memory updates
- Rule persistence
- Replay / audit tooling
- Advanced abstraction / causal rules
- Production API hardening
- Browser-based graph UI

---

## Status

Prototype of a cognitive AI system with self-improving behavior, graph observability, exploration-aware memory planning, reliability-aware planning, decision backbone extraction, controlled evolution tracking, and pluggable persistent episodic memory.

---

## License

Apache 2.0
