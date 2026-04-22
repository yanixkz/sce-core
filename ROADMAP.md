# SCE Core Roadmap

## North Star

```text
Decide. Explain. Improve.
```

SCE Core is a decision engine for AI agents.

It helps an agent:

1. choose a plan,
2. explain which facts carried the decision,
3. remember outcomes and reliability,
4. improve the next choice.

The roadmap is now focused on making that loop simple, visible, and useful in one concrete domain first: **supplier risk**.

---

## Current State (v0.6-alpha)

SCE Core currently has:

- main supplier-risk terminal demo
- memory-aware planning
- reliability-aware planning
- reliability stored in episodic memory
- decision backbone extraction
- controlled evolution / prediction error tracking
- exploration-aware plan selection
- constraint DSL
- graph export and ASCII visualization
- persistent episodic memory with PostgreSQL support
- FastAPI API
- LLM provider clients
- PostgreSQL-backed CI tests

The main command is:

```bash
sce run-supplier-risk-demo-pretty
```

This demo shows the whole SCE loop:

```text
supplier risk → plan choice → decision backbone → reliability → memory → improved next choice
```

---

## Completed Milestones

### v0.1 — Cognitive Core
- Core state model
- Scoring and evolution
- Explainability
- Agent loop
- Tool layer
- Learning layer
- Episodic memory
- Abstraction rules
- Voice OS bridge
- FastAPI API

### v0.2 — Constraint DSL
- Human-readable constraint language
- DSL → predicate compiler
- Safe evaluator without eval/exec
- Constraint compatibility tests

### v0.3 — Graph + Persistence Foundation
- Graph export (JSON)
- ASCII visualization in CLI
- Episode serialization (to_dict / from_dict)
- EpisodeRepository abstraction
- InMemoryEpisodeRepository
- PostgresEpisodeRepository
- PostgreSQL migration
- JSONB storage
- PostgreSQL service container in CI

### v0.4 — Adaptive Decision Observability
- Adaptive agent demo
- Exploration-aware planner
- Decision backbone extractor
- Controlled evolution error tracker
- Pretty terminal demos

### v0.5 — Reliability-Aware Planning
- Reliability-aware planner
- Reliability-aware planning demo
- Controlled evolution reports stored as episode reliability
- Episode serialization includes optional reliability
- Remembered reliability can rerank candidate plans
- Reliability-aware learning executor

### v0.6 — Simple Main Demo
- Main supplier-risk demo
- One-command story: `sce run-supplier-risk-demo-pretty`
- README simplified around Decide / Explain / Improve
- Visual guide simplified around the main demo
- Advanced demos moved below the main story

---

## Next Priorities

### v0.7 — Supplier Risk Product Demo
Goal: make the current demo feel like a real product scenario.

- Add richer supplier inputs:
  - delivery delays
  - invoice risk
  - missing certificates
  - contract exceptions
  - dependency risk
- Add domain constraints for supplier risk
- Add clearer business decision actions:
  - monitor
  - request documents
  - escalate
  - block / pause supplier
- Add before/after explanation:
  - what a plain LLM would say
  - what SCE explains structurally
- Keep the demo one command and one story

### v0.8 — Minimal Web UI
Goal: make the idea visible without reading terminal output.

- Simple browser page
- Left: supplier facts
- Middle: decision backbone
- Right: selected plan and reliability
- Bottom: remembered episodes
- Use existing graph export and demo outputs where possible

### v0.9 — Product API
Goal: expose the useful loop through API endpoints.

- Endpoint for supplier risk decision
- Endpoint for decision backbone
- Endpoint for reliability report
- Endpoint for memory episodes
- Basic API stabilization
- Clear JSON response shape for product demos

### v1.0 — Hardening
Goal: make the project robust enough for external testers.

- Better docs for first-time users
- More integration tests
- API hardening
- Optional auth
- Deployment config
- Better error messages

---

## Research Backlog

These are valuable, but should not distract from the simple product path.

- Critical decision nodes and edges
- Constraint-aware decision backbone extraction
- Memory-aware decision backbone extraction
- Reliability decay over time
- Reliability-aware exploration triggers
- Reliability-aware memory pruning
- Trajectory replay and audit output
- Advanced abstraction / causal rules
- Topological reasoning over decision graphs
- Multi-agent coordination
- Voice-native interfaces

---

## Status

SCE Core has moved from a broad research prototype to a focused early product/research system.

Current focus:

```text
Supplier Risk Agent
↓
Decide. Explain. Improve.
↓
Web UI
↓
Product API
```
