# Visual Demo

SCE Core can be inspected from the terminal without a separate UI.

The quickest demo is the adaptive agent story:

```bash
sce run-adaptive-agent-demo-pretty
```

It shows an agent generating candidate plans, scoring them, executing a plan, writing the outcome to memory, re-scoring, and changing its future decision.

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

## 2. ASCII graph

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

## 3. JSON graph export

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

## 4. Memory-aware planning demo

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

## 5. API docs

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
- ASCII graph visualization
- JSON graph export
- FastAPI Swagger docs

A richer browser UI can be built on top of `sce export-graph`.
