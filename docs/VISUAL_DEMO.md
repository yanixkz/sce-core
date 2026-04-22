# Visual Demo

SCE Core can be inspected from the terminal without a separate UI.

The four quickest demos are:

```bash
sce run-adaptive-agent-demo-pretty
sce run-decision-backbone-demo-pretty
sce run-controlled-evolution-demo-pretty
sce run-reliability-aware-planning-demo-pretty
```

The adaptive demo shows an agent generating candidate plans, scoring them, executing a plan, writing the outcome to memory, re-scoring, and changing its future decision.

The decision backbone demo shows which reasoning nodes carry the decision from evidence to target action, and which branches are dangling.

The controlled evolution demo shows how local prediction errors accumulate into a reliability score for the trajectory.

The reliability-aware planning demo shows reliability affecting the next plan choice.

---

## 1. Adaptive agent demo

Run:

```bash
sce run-adaptive-agent-demo-pretty
```

The output is a readable terminal story:

```text
SCE Adaptive Agent Demo
=======================

Goal:  assess supplier risk
State: {'entity': 'supplier A', 'risk': 'high'}

1) Before learning
------------------
plan                         base    memory   total
------------------------------------------------------
supplier_risk_plan           0.60     0.00    0.60
escalation_plan              0.40     0.00    0.40
monitor_plan                 0.10     0.00    0.10

Selected plan: supplier_risk_plan
Execution success: True

2) Execution trace
------------------
- Generated 3 candidate plans.
- Selected supplier_risk_plan using base scores and current memory.
- Executed supplier_risk_plan; success=True.
- Stored the execution result as an episode.
- Stored an additional successful escalation episode.
- Re-scored candidates and selected escalation_plan.

3) Learning event
-----------------
A successful escalation episode is stored in episodic memory.
Episodes in memory: 2

4) After learning
-----------------
plan                         base    memory   total
------------------------------------------------------
escalation_plan              0.40     0.75    1.15
supplier_risk_plan           0.60     0.50    1.10
monitor_plan                 0.10     0.00    0.10

Selected plan: escalation_plan
Changed choice: YES

Why the decision changed
------------------------
escalation_plan received a memory boost.
The decision changed because remembered outcomes shifted the ranking.
```

This is the best entry point for seeing the core idea: remembered outcomes can change future decisions.

---

## 2. Decision backbone demo

Run:

```bash
sce run-decision-backbone-demo-pretty
```

The output separates decision-carrying nodes from dangling reasoning branches:

```text
SCE Decision Backbone Demo
==========================

Reasoning graph
---------------
- late_delivery -> supplier_risk
- invoice_risk -> supplier_risk
- missing_certificate -> supplier_risk
- supplier_risk -> escalate
- old_positive_history -> context_note
- context_note -> ∅
- marketing_tag -> unrelated_note
- unrelated_note -> ∅

Decision backbone
-----------------
- escalate
- invoice_risk
- late_delivery
- missing_certificate
- supplier_risk

Dangling branches
-----------------
- context_note
- marketing_tag
- old_positive_history
- unrelated_note
```

This is the quickest way to see structural explainability: not every connected fact carries the decision.

---

## 3. Controlled evolution demo

Run:

```bash
sce run-controlled-evolution-demo-pretty
```

The output shows local prediction error and trajectory reliability:

```text
SCE Controlled Evolution Demo
=============================

Step errors
-----------
step                         predicted   actual   error
-------------------------------------------------------
score_supplier_risk              0.90     0.72    0.18
select_escalation_plan           0.78     0.70    0.08
execute_followup                 0.74     0.73    0.01

Trajectory report
-----------------
cumulative_error: 0.27
mean_error:       0.09
reliability:      0.79
trend:            improving
is_reliable:      True
```

This is the quickest way to see the control idea: local errors are tracked and summarized as trajectory-level reliability.

---

## 4. Reliability-aware planning demo

Run:

```bash
sce run-reliability-aware-planning-demo-pretty
```

The output shows reliability changing the selected plan:

```text
SCE Reliability-Aware Planning Demo
===================================

1) Without trajectory reliability
---------------------------------
plan                         base    memory   total
------------------------------------------------------
supplier_risk_plan           0.60     0.00    0.60
escalation_plan              0.40     0.00    0.40
monitor_plan                 0.10     0.00    0.10

Selected plan: supplier_risk_plan

2) With trajectory reliability
------------------------------
plan                         base    memory   rel   total
----------------------------------------------------------
escalation_plan              0.40     0.00   0.95    1.35
supplier_risk_plan           0.60     0.00   0.10    0.70
monitor_plan                 0.10     0.00   0.20    0.30

Selected plan: escalation_plan
Changed choice: YES
```

This closes the loop: reliability is no longer only observed after the fact; it can affect the next decision.

---

## 5. ASCII graph

Run:

```bash
sce visualize-graph
```

Write it to a file:

```bash
sce visualize-graph --out graph.txt
```

The ASCII renderer shows:

- states
- stability scores
- attractor markers
- constraint status
- graph edges and relation types

---

## 6. JSON graph export

Run:

```bash
sce export-graph
```

Write it to a file:

```bash
sce export-graph --out graph.json
```

The JSON export is useful for building a browser UI later.

---

## 7. Exploration demo

Run:

```bash
sce run-exploration-demo-pretty
```

This demo shows the difference between exploiting the current top-scoring plan and exploring a non-top alternative.

---

## 8. Memory-aware planning demo

Run:

```bash
sce run-memory-aware-planning-demo
```

This lower-level demo demonstrates how previous episodes bias future plan selection.

---

## 9. API docs

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

- adaptive terminal demo
- decision backbone terminal demo
- controlled evolution terminal demo
- reliability-aware planning terminal demo
- exploration terminal demo
- ASCII graph visualization
- JSON graph export
- FastAPI Swagger docs

A richer browser UI can be built on top of `sce export-graph`, decision backbone extraction, and controlled evolution reports.
