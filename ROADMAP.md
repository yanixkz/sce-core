# SCE Core Roadmap

## North Star

```text
Decide. Explain. Improve.
```

SCE Core is a decision engine for AI agents and a research platform for explainable adaptive decision systems.

It helps an agent:

1. choose a plan,
2. explain which facts carried the decision,
3. remember outcomes and reliability,
4. improve the next choice.

The supplier-risk scenario is the first simple demo, not the final purpose of the project.

The broader aim is to study and build decision systems that are explainable, memory-aware, reliability-aware, and structurally inspectable.

Research vision: [`docs/RESEARCH_VISION.md`](docs/RESEARCH_VISION.md)
Research program (open problems): [`docs/research_program.md`](docs/research_program.md)

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

The demo is intentionally concrete so the research idea is easy to see.

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
- Research vision added

---

## Next Priorities

### v0.7 — Better Research Demo, Not Just Supplier Risk
Goal: keep one simple story, but make it clear that SCE is a general decision research engine.

- Keep supplier risk as the concrete entry point
- Add a short “generalized mapping” section:
  - supplier facts → evidence
  - supplier risk → state
  - escalation → target decision
  - remembered reliability → adaptive memory
- Add a second tiny research-flavored scenario if needed:
  - hypothesis evaluation
  - literature evidence graph
  - scientific workflow decision
- Add before/after explanation:
  - plain LLM answer
  - SCE structured decision path
- Keep the main demo one command and one story

### v0.8 — Minimal Web UI
Goal: make the idea visible without reading terminal output.

- Simple browser page
- Left: evidence / facts
- Middle: decision backbone
- Right: selected plan and reliability
- Bottom: remembered episodes
- Use existing graph export and demo outputs where possible

### v0.9 — Research/Product API
Goal: expose the useful loop through API endpoints.

- Endpoint for a generic decision request
- Endpoint for supplier risk demo request
- Endpoint for decision backbone
- Endpoint for reliability report
- Endpoint for memory episodes
- Clear JSON response shape for product and research demos

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

This backlog is intentionally aligned with the structured research tracks in [`docs/research_program.md`](docs/research_program.md).

These are valuable and should guide the long-term direction.

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
- Scientific hypothesis evaluation demos
- Research literature graph demos
- General constrained state evolution benchmarks

---

## Status

SCE Core has moved from a broad research prototype to a focused early research/product system.

Current focus:

```text
One simple demo
↓
Decide. Explain. Improve.
↓
General research engine for explainable adaptive decisions
↓
Web UI
↓
Research/Product API
```
