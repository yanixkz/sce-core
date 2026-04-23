# SCE Core

[![Tests](https://img.shields.io/github/actions/workflow/status/yanixkz/sce-core/tests.yml?branch=main&label=tests)](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml)

## Build AI agents that can decide, explain, and improve

SCE Core is a decision engine for AI agents with explainability, reliability tracking, memory, and graph observability.

```text
Decide. Explain. Improve.
```

---

## Positioning in one line

**SCE Core is the decision layer for AI agents when you need auditable choices, not just generated answers.**

For Russian-speaking readers: see [docs/OVERVIEW_RU.md](docs/OVERVIEW_RU.md).

---

## Why SCE exists

Most AI agents can produce an answer.
Few can clearly show:

```text
why this choice?
which facts actually mattered?
what was ignored?
was the trajectory reliable?
did the next decision improve?
```

SCE Core provides that missing layer.

---

## What you can do right now

- Run a full end-to-end demo with one command
- Inspect why a decision was made
- Track reliability and improvement over time
- Expose the system through a versioned API
- Inspect the internal graph behind the decision process

### Start in one command

```bash
sce demo
```

---

## Who it is for

### 1) Product and platform teams building AI agents

Use SCE when your team needs a reusable, inspectable decision substrate under multiple agent workflows.

### 2) Operations and risk teams

Use SCE when decisions must be traceable over time (e.g., supply chain, incident response, policy workflows).

### 3) Research and applied AI teams

Use SCE when you want to study how decision quality evolves with memory and reliability feedback.

---

## Who gets value (ICP)

### Primary users

- AI/ML engineers building agent backends
- Platform engineers responsible for agent reliability
- Applied researchers in explainable/adaptive decision systems

### Business stakeholders

- Risk and compliance leaders
- Operations managers
- CTO/Head of AI evaluating production-readiness of agent decisions

---

## Core capabilities

### Decide

Rank candidate plans and choose the best next action.

### Explain

Use decision backbone extraction to separate decision-carrying facts from dangling context.

### Improve

Track local prediction error, compute reliability, remember the outcome, and influence the next decision.

### Observe

Export and inspect the system graph through CLI and API.

---

## Product loop

```text
State
↓
Candidate plans
↓
Score with memory + reliability
↓
Select
↓
Explain
↓
Execute / observe
↓
Track prediction error
↓
Remember reliability
↓
Improve next choice
```

---

## Why SCE is different

### Decision backbone extraction

SCE identifies which nodes actually carried the decision.

```text
forward  = nodes reachable from evidence
backward = nodes that can reach the target decision
backbone = forward ∩ backward
dangling = forward - backbone
```

### Reliability-aware planning

SCE does not stop at plan selection. It measures how reliable the trajectory was and feeds that back into future scoring.

### Memory-aware evolution

SCE remembers outcomes and uses them to change later behavior.

### Graph observability

SCE can export a real graph representation of system state for debugging, visualization, and product integration.

---

## Use cases

- Explainable AI copilots
- Operations and workflow agents
- Supplier risk systems
- Research agents
- Auditable autonomous systems
- Internal decision infrastructure for agent platforms

---

## Run the product story

Dual packaging:

- `supplier-risk` = practical product-facing demo
- `hypothesis` = research-facing flagship demo

### Canonical entrypoints

```bash
sce demo
sce demo supplier-risk
sce demo hypothesis
sce demo list
```

### Graph inspection entrypoints

```bash
sce export-graph
sce visualize-graph
```

`sce demo` defaults to `supplier-risk` and shows the complete loop:

```text
supplier risk → plan choice → backbone → reliability → memory → improved next choice
```

### Hypothesis demo

```bash
sce demo hypothesis
```

Research showcase for:
- competing hypotheses and ranking,
- decision-carrying evidence vs dangling context,
- concrete next research actions.

### JSON output

```bash
sce demo supplier-risk --json
```

---

## API endpoints

```text
POST /ask
POST /decide
POST /demo
POST /demo/explain
GET  /graph
```

`/decide` is the generalized decision-facing API surface (goal + context -> ranked
decision response). Demo endpoints remain intact as showcase/product-story routes.

Responses keep existing contracts and include additive UI-readiness metadata for
minimal web integration (for example `meta.ui` panel hints on demo endpoints and
graph schema/count hints on `/graph`).

### Run API locally

```bash
uvicorn sce.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/ui
```

`/ui` is a minimal web skeleton that lets you run `supplier-risk` and `hypothesis` demos and inspect `/graph` payloads in-browser.

### Example

```bash
curl -X POST http://127.0.0.1:8000/decide \
  -H "Content-Type: application/json" \
  -d '{
    "goal":"assess supplier risk",
    "context":{"supplier_id":"supplier A","claim":"supplier may be unreliable"},
    "execute":true
  }'
```

### Demo run (showcase endpoints)

```bash
curl -X POST http://127.0.0.1:8000/demo \
  -H "Content-Type: application/json" \
  -d '{"name":"supplier-risk","format":"pretty"}'
```

### Explainability only

```bash
curl -X POST http://127.0.0.1:8000/demo/explain \
  -H "Content-Type: application/json" \
  -d '{"name":"hypothesis"}'
```

### Graph inspection

```bash
curl http://127.0.0.1:8000/graph
```

---

## Adoption path (practical)

### Day 1

Run demos and inspect backbone + reliability outputs.

### Week 1

Integrate `/ask` or `/demo` in a staging workflow and log explanations.

### Month 1

Use reliability and memory feedback to tune decision policies and compare trajectories over time.

---

## When not to use SCE

SCE may be unnecessary if your use case only needs one-shot text generation and does not require:

- decision traceability,
- reliability monitoring,
- memory-aware policy improvement,
- or graph-level observability.

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

## Tests

```bash
pytest
```

---

## Status

SCE Core is an early product/research system for explainable, memory-aware, reliability-aware AI decisions.

---

## License

Apache 2.0
