# Visual Demo

SCE Core can be inspected from the terminal without a separate UI.

The two quickest demos are:

```bash
sce run-adaptive-agent-demo-pretty
sce run-decision-backbone-demo-pretty
```

The adaptive demo shows an agent generating candidate plans, scoring them, executing a plan, writing the outcome to memory, re-scoring, and changing its future decision.

The decision backbone demo shows which reasoning nodes carry the decision from evidence to target action, and which branches are dangling.

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

Sources / evidence
------------------
- invoice_risk
- late_delivery
- marketing_tag
- missing_certificate
- old_positive_history

Targets / decisions
-------------------
- escalate

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

## 3. ASCII graph

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

Example shape:

```text
State Graph
===========

⭐ supplier_reliable (stab=0.82)
  ✓ constraints satisfied
  └─[supports]→ supplier_contract_safe

supplier_risky (stab=-0.21)
  ✗ constraints unsatisfied
  └─[conflicts]→ supplier_contract_safe
```

---

## 4. JSON graph export

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

## 5. Exploration demo

Run:

```bash
sce run-exploration-demo-pretty
```

This demo shows the difference between exploiting the current top-scoring plan and exploring a non-top alternative.

---

## 6. Memory-aware planning demo

Run:

```bash
sce run-memory-aware-planning-demo
```

This lower-level demo demonstrates how previous episodes bias future plan selection.

Expected shape:

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

## 7. API docs

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
- exploration terminal demo
- ASCII graph visualization
- JSON graph export
- FastAPI Swagger docs

A richer browser UI can be built on top of `sce export-graph` and decision backbone extraction.
