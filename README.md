# SCE Core

![Tests](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml/badge.svg)

**State–Constraint–Evolution Core** is a decision engine for AI agents.

```text
Decide. Explain. Improve.
```

SCE helps an agent choose a plan, explain which facts carried the decision, remember what happened, and improve the next choice.

---

## Quick demo

Run the main story:

```bash
sce run-supplier-risk-demo-pretty
```

It shows one complete loop:

```text
supplier risk → plan choice → decision backbone → reliability → memory → improved next choice
```

In plain terms:

- **Decide** — choose the best plan
- **Explain** — show which facts actually led to the decision
- **Improve** — remember reliability and use it in the next decision

---

## What problem does SCE solve?

Many AI agents can produce an answer, but they often cannot clearly show:

```text
why this plan?
which facts mattered?
what was ignored?
was the trajectory reliable?
will the next decision improve?
```

SCE Core adds that missing decision layer.

---

## Core loop

```text
State
↓
Candidate plans
↓
Score with memory + reliability
↓
Select plan
↓
Explain decision path
↓
Execute / observe outcome
↓
Track prediction error
↓
Remember reliability
↓
Improve next choice
```

---

## Main demo: Supplier Risk Agent

```bash
sce run-supplier-risk-demo-pretty
```

The demo shows:

```text
1. Decide
   supplier_risk_plan is selected first by base score

2. Explain
   late_delivery + invoice_risk + missing_certificate carry the decision
   marketing_tag and old_positive_history are dangling context

3. Measure reliability
   prediction errors become a reliability score

4. Improve
   remembered reliability changes the next selected plan
```

Expected shape:

```text
SCE Supplier Risk Demo
======================

Decide. Explain. Improve.

1) Decide
---------
plan                         base    memory   total
------------------------------------------------------
supplier_risk_plan           0.60     0.00    0.60
escalation_plan              0.40     0.00    0.40
monitor_plan                 0.10     0.00    0.10

Initial selected plan: supplier_risk_plan

2) Explain
----------
Decision-carrying facts:
- late_delivery
- invoice_risk
- missing_certificate
- supplier_risk
- escalation_plan

Dangling context:
- marketing_tag
- old_positive_history

3) Measure reliability
----------------------
cumulative_error: 0.27
reliability:      0.79
trend:            improving

4) Improve
----------
Final selected plan: escalation_plan
Changed choice: YES
```

---

## Key ideas

### Decision backbone

SCE shows which facts actually carry the decision.

```text
forward  = nodes reachable from evidence
backward = nodes that can reach the target decision
backbone = forward ∩ backward
dangling = forward - backbone
```

Details: [`docs/DECISION_BACKBONE.md`](docs/DECISION_BACKBONE.md)

### Reliability tracking

SCE tracks local prediction error:

```text
predicted value → actual value → step error → reliability
```

Details: [`docs/CONTROLLED_EVOLUTION.md`](docs/CONTROLLED_EVOLUTION.md)

### Reliability-aware planning

SCE can use remembered reliability in future scoring:

```text
base score + memory bias + remembered reliability bonus → selected plan
```

Details: [`docs/RELIABILITY_AWARE_PLANNING.md`](docs/RELIABILITY_AWARE_PLANNING.md)

---

## Core components

- **Planning** — generate candidate plans
- **Scoring** — rank plans with base score, memory, and reliability
- **Memory** — store outcomes and reliability as episodes
- **Decision backbone** — identify decision-carrying facts vs dangling context
- **Reliability tracking** — convert prediction error into trajectory reliability
- **Exploration** — optionally try non-top plans
- **Constraint DSL** — safe human-readable constraints without `eval`/`exec`
- **Graph observability** — JSON export and ASCII visualization
- **Persistence** — in-memory and PostgreSQL episodic memory
- **API** — FastAPI `/health` and `/ask`
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

---

## Advanced demos

```bash
sce run-adaptive-agent-demo-pretty
sce run-decision-backbone-demo-pretty
sce run-controlled-evolution-demo-pretty
sce run-reliability-aware-planning-demo-pretty
sce run-exploration-demo-pretty
sce run-memory-aware-planning-demo
sce visualize-graph
sce export-graph
```

All visual/demo commands are documented in [`docs/VISUAL_DEMO.md`](docs/VISUAL_DEMO.md).

---

## Current gaps / next work

- Critical decision nodes and edges
- Constraint-aware decision backbone extraction
- Reliability decay over time
- Reliability-aware exploration triggers
- Supplier risk product demo with real business inputs
- Browser-based graph UI

---

## Status

Early product/research system for explainable, memory-aware, reliability-aware AI decisions.

---

## License

Apache 2.0
