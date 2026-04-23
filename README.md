# SCE Core

[![Tests](https://img.shields.io/github/actions/workflow/status/yanixkz/sce-core/tests.yml?branch=main&label=tests)](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml)

## Build AI agents that can decide, explain, and improve

SCE Core is a decision engine for AI agents with explainability, reliability tracking, memory, and graph observability.

```text
Decide. Explain. Improve.
```

### What you can do right now

- Run a full end-to-end demo with one command
- Inspect why a decision was made
- Track reliability and improvement over time
- Expose the system through a versioned API
- Inspect the internal graph behind the decision process

### Start in one command

```bash
sce demo
```

### API endpoints

```text
POST /ask
POST /demo
POST /demo/explain
GET  /graph
```

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

## Run the product story

### Main demo

```bash
sce demo
```

This shows the complete loop:

```text
supplier risk → plan choice → backbone → reliability → memory → improved next choice
```

### Hypothesis demo

```bash
sce demo hypothesis
```

### JSON output

```bash
sce demo supplier-risk --json
```

---

## API

Run locally:

```bash
uvicorn sce.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### Example

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

## Use cases

- Explainable AI copilots
- Operations and workflow agents
- Supplier risk systems
- Research agents
- Auditable autonomous systems
- Internal decision infrastructure for agent platforms

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
