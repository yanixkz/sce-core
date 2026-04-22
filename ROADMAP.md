# SCE Core Roadmap

## Current State (v0.4-alpha)

SCE Core has evolved into an explainable, adaptive, and controlled decision system with:

- CognitiveAgent (closed decision loop)
- Learning + Memory + Abstraction
- LLM integration (OpenAI + Anthropic)
- Voice OS bridge
- FastAPI REST API
- Multi-agent world
- Graph query layer
- Constraint DSL (safe text constraints compiled to predicates)
- Graph export (JSON) and ASCII visualization
- Persistent episodic memory (in-memory + PostgreSQL)
- Memory-aware planning
- Exploration-aware plan selection
- Adaptive agent terminal demo
- Decision backbone extraction
- Controlled evolution error tracking
- PostgreSQL-backed CI tests

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
- PostgreSQL migration (episodes table)
- JSONB storage (psycopg Jsonb)
- PostgreSQL service container in CI

### v0.4 — Adaptive Decision Observability
- Adaptive agent demo
- Pretty terminal output for adaptive planning
- Exploration-aware planner
- Exploration demo
- Decision backbone extractor
- Decision backbone demo
- Controlled evolution error tracker
- Controlled evolution demo

---

## Next Priorities

### v0.5 — Reliability-Aware Planning
- Integrate controlled evolution reports into plan scoring
- Use accumulated step error to adjust future plan bias
- Add reliability-aware memory updates
- Add trajectory replay and audit output

### v0.6 — Criticality + Backbone Hardening
- Critical backbone node detection
- Critical edge / bridge detection
- Alternative path detection
- Constraint-aware decision backbone extraction
- Memory-aware decision backbone extraction

### v0.7 — Supplier Risk Product Demo
- Domain-specific supplier risk scenario
- Evidence → constraints → risk state → decision backbone → action
- Contract/risk constraints
- Pretty output suitable for business demos

### v0.8 — Production API Hardening
- API stabilization
- Auth
- Rate limiting
- Deployment configs
- API endpoints for backbone and controlled evolution reports

### v0.9 — Richer Visual UI
- Browser graph UI beyond ASCII
- Interactive decision backbone visualization
- Reliability timeline visualization
- Memory episode browser

---

## Long-Term

- Autonomous agents
- Real-time systems
- Voice-native interfaces
- Multi-agent coordination
- Topological reasoning over decision graphs
- Reliability-aware cognitive systems

---

## Status

Transitioned from research prototype → cognitive architecture → early product system with persistent memory, decision backbone extraction, exploration-aware planning, and controlled evolution tracking.
