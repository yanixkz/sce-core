# SCE Core Roadmap (Updated)

## Current State (v0.3-alpha)

SCE Core has evolved into a cognitive AI system with:

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

---

## Next Priorities

### v0.4 — Persistent Memory Hardening
- PostgreSQL integration tests in CI
- Connection lifecycle improvements
- Batch inserts / performance tuning
- Error handling and retries

### v0.5 — Advanced Abstraction
- Causal pattern extraction
- Condition-based rules
- Rule scoring

### v0.6 — Production API Hardening
- API stabilization
- Auth
- Rate limiting
- Deployment configs

### v0.7 — Richer Visual UI (Later)
- Rich graph UI beyond ASCII
- Interactive exploration

---

## Long-Term

- Autonomous agents
- Real-time systems
- Voice-native interfaces
- Multi-agent coordination

---

## Status

Transitioned from research prototype → cognitive architecture → early product system with persistent memory.
