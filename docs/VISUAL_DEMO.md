# Visual Demo

SCE Core can be inspected from the terminal without a separate UI.

## 1. ASCII graph

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

## 2. JSON graph export

Run:

```bash
sce export-graph
```

Write it to a file:

```bash
sce export-graph --out graph.json
```

The JSON export is useful for building a web UI later.

## 3. Memory-aware planning demo

Run:

```bash
sce run-memory-aware-planning-demo
```

This demonstrates how previous episodes bias future plan selection.

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

## 4. API docs

Run:

```bash
uvicorn sce.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Current visual surface

SCE Core currently supports:

- terminal demos
- ASCII graph visualization
- JSON graph export
- FastAPI Swagger docs

A richer browser UI can be built on top of `sce export-graph`.
