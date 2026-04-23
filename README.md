# SCE Core

[![Tests](https://img.shields.io/github/actions/workflow/status/yanixkz/sce-core/tests.yml?branch=main&label=tests)](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml)

SCE Core is a decision engine for AI agents.

It combines:
- constrained decision selection,
- explainability via decision backbone extraction,
- reliability tracking from outcomes,
- episodic memory that influences later choices,
- inspectable API/graph/UI surfaces.

```text
Decide → Explain → Remember/Reliability → Improve
```

## What SCE Core is (and is not)

SCE Core is not a chat wrapper and not only a demo collection.
It is a reusable decision layer that currently ships with demos, API endpoints, and a theory/research documentation stack.

- **Product layer:** runnable demos and API/UI surfaces.
- **Theory bridge:** CDS → SCE operational mapping.
- **Research layer:** open problems grounded in the implemented loop.
- **Origin layer:** historical and philosophical motivation.

## Start in one command

```bash
sce demo
```

Canonical demo commands:

```bash
sce demo supplier-risk
sce demo hypothesis
sce demo list
```

Graph inspection:

```bash
sce export-graph
sce visualize-graph
```

## Flagship demos

### `supplier-risk` (product-facing)

Practical window into the core loop:

```text
supplier context → plan choice → backbone explanation → reliability signal → memory influence → improved next choice
```

### `hypothesis` (research-facing)

Research window into the same engine:
- competing hypothesis ranking,
- decision-carrying evidence vs dangling context,
- concrete next research actions.

## Reusable API surface

Core reusable endpoints:

```text
POST /decide
GET  /memory
GET  /reliability
GET  /graph
GET  /ui
```

Showcase/supporting endpoints:

```text
POST /ask
GET  /demo
POST /demo
POST /demo/explain
```

Notes:
- `/decide` is the generalized decision endpoint (`goal + context → ranked decision response`).
- `/memory` and `/reliability` are process-local inspection surfaces based on executed decisions in the current API process.
- Demo endpoints remain as product/story routes over the same engine.

## Run API locally

```bash
uvicorn sce.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/ui
```

Example decision call:

```bash
curl -X POST http://127.0.0.1:8000/decide \
  -H "Content-Type: application/json" \
  -d '{
    "goal":"assess supplier risk",
    "context":{"supplier_id":"supplier A","claim":"supplier may be unreliable"},
    "execute":true
  }'
```

## Why this architecture matters

SCE Core keeps four mechanisms coupled in one inspectable loop:

1. **Constraints + trajectory selection** choose admissible plans.
2. **Decision backbone** shows what carried the decision.
3. **Reliability tracking** measures empirical stability quality.
4. **Episodic memory** changes future reselection pressure.

This coupling is what makes the system both practical and research-relevant.

## Documentation map

- **Product entrypoint:** `README.md` (this file)
- **Roadmap / delivery priorities:** [`ROADMAP.md`](ROADMAP.md)
- **Origin (history and motivation):** [`docs/origin.md`](docs/origin.md)
- **Theory bridge (CDS → SCE):** [`docs/constraint_driven_stability.md`](docs/constraint_driven_stability.md)
- **Research program (open problems):** [`docs/research_program.md`](docs/research_program.md)
- **Russian overview:** [`docs/OVERVIEW_RU.md`](docs/OVERVIEW_RU.md)
- **Extended docs index:** [`docs/README.md`](docs/README.md)
- **Governance/workflow guide:** [`docs/governance.md`](docs/governance.md)

## Near-term direction (concise)

Near-term work stays split across product and research, on one engine:

- improve decision inspectability and replayability,
- make reliability/memory policies more robust over time,
- evolve `supplier-risk` and `hypothesis` into a stronger benchmark pair,
- continue hardening API/UI surfaces without breaking compatibility.

Details: [`ROADMAP.md`](ROADMAP.md) and [`docs/research_program.md`](docs/research_program.md).

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

## Tests

```bash
pytest
```

## Status

Early product/research system for explainable adaptive decision workflows.

## License

Apache 2.0
