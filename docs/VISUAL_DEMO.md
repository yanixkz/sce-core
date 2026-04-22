# Visual Demo

SCE Core can be inspected from the terminal without a separate UI.

The main demo is:

```bash
sce run-supplier-risk-demo-pretty
```

It tells the whole SCE story in one place:

```text
Decide. Explain. Improve.
```

---

## 1. Main demo: Supplier Risk Agent

Run:

```bash
sce run-supplier-risk-demo-pretty
```

The demo shows:

- initial plan selection
- decision-carrying facts
- dangling context
- trajectory reliability
- remembered reliability
- improved next choice

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
- escalation_plan
- invoice_risk
- late_delivery
- missing_certificate
- supplier_risk

Dangling context:
- context_note
- marketing_tag
- old_positive_history
- unrelated_note

3) Measure reliability
----------------------
cumulative_error: 0.27
reliability:      0.79
trend:            improving

4) Improve
----------
Remembered episodes: 3

Final selected plan: escalation_plan
Changed choice: YES
```

This is the shortest way to understand the project.

---

## 2. Focused demos

These demos isolate one mechanism at a time.

### Adaptive agent

```bash
sce run-adaptive-agent-demo-pretty
```

Shows memory changing a future plan choice.

### Decision backbone

```bash
sce run-decision-backbone-demo-pretty
```

Shows which facts carry the decision and which branches are dangling.

### Controlled evolution

```bash
sce run-controlled-evolution-demo-pretty
```

Shows prediction error becoming trajectory reliability.

### Reliability-aware planning

```bash
sce run-reliability-aware-planning-demo-pretty
```

Shows remembered reliability changing plan selection.

### Exploration

```bash
sce run-exploration-demo-pretty
```

Shows the difference between exploiting the current top-scoring plan and exploring a non-top alternative.

---

## 3. Graph tools

### ASCII graph

```bash
sce visualize-graph
sce visualize-graph --out graph.txt
```

### JSON graph export

```bash
sce export-graph
sce export-graph --out graph.json
```

The JSON export is useful for building a browser UI later.

---

## 4. API docs

Run:

```bash
uvicorn sce.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Current visual surface

SCE Core currently supports:

- main supplier-risk terminal demo
- focused terminal demos
- ASCII graph visualization
- JSON graph export
- FastAPI Swagger docs

A richer browser UI can be built on top of `sce export-graph`, decision backbone extraction, and reliability reports.
