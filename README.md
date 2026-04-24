# SCE Core

[![Tests](https://img.shields.io/github/actions/workflow/status/yanixkz/sce-core/tests.yml?branch=main&label=tests)](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml)

SCE Core is an **early alpha** computational framework for studying
**Constraint-Driven Stability (CDS)** in adaptive systems,
with an applied decision-engine surface for AI agents.

It combines:
- constrained decision selection,
- explainability via decision backbone extraction,
- reliability tracking from outcomes,
- episodic memory that influences later choices,
- inspectable API/graph/UI surfaces.

```text
Decide → Explain → Remember/Reliability → Improve
```

## Alpha release status

- **Release channel:** `v0.1-alpha`
- **Python package version (PEP 440):** `0.1.0a0`
- **Maturity:** usable for exploration, demos, and API prototyping; not a stable production contract yet.

## Fastest path to value (5 minutes)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[api]
```

Run core demos:

```bash
sce demo
sce demo hypothesis
sce demo resource-stability
sce demo epidemic-regime
```

Run the API and open UI:

```bash
uvicorn sce.api:app --reload
# then open http://127.0.0.1:8000/ui
```

## What SCE Core is (and is not)

SCE Core is not a chat wrapper and not only a demo collection.
It is a reusable computational research and decision layer with demos, API endpoints, and theory/research documentation.

- **Scientific framework layer:** CDS-oriented toy models and inspectable stability workflows.
- **Applied decision layer:** runnable demos and API/UI surfaces for agent decision tasks.
- **Theory bridge:** CDS → SCE operational mapping.
- **Research layer:** open problems grounded in implemented mechanisms.
- **Origin layer:** historical and philosophical motivation.

## Canonical CLI and graph commands

```bash
sce demo
sce demo supplier-risk
sce demo hypothesis
sce demo resource-stability
sce demo list
sce export-graph
sce visualize-graph
```

## Reusable API surface

Core reusable endpoints:

```text
POST /decide
POST /compare
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
- `/compare` is an additive comparison surface for **Generic AI vs SCE** on the same input:
  deterministic mock baseline answer + real SCE structured decision output.
- `/memory` and `/reliability` default to process-local in-memory inspection and automatically switch to durable PostgreSQL-backed episode history when `SCE_DATABASE_URL` is configured.
- Demo endpoints remain as product/story routes over the same engine.
- Baseline providers for `/compare` are optional: default is deterministic/mock; OpenAI/Anthropic are opt-in and fall back to mock if not configured.

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

Example comparison call:

```bash
curl -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "goal":"assess supplier risk",
    "context":{"supplier_id":"supplier A","claim":"supplier may be unreliable"},
    "constraints":["prefer external verification"],
    "execute":false
  }'
```

`/compare` is intended for visual comparison experiences where the same input is rendered as:
- Generic AI one-shot answer (baseline),
- SCE ranked and inspectable decision output.

## Flagship demos

Scientific entrypoint (recommended first stop for labs): [`docs/scientific_examples.md`](docs/scientific_examples.md).

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

### `resource-stability` (scientific toy model)

First compact CDS research-facing scenario:
- initial unstable population/resource regime,
- deterministic candidate regime evolution,
- stability scoring and ranking under explicit constraints,
- selected carrying regime plus non-carrying regimes,
- concrete follow-up research actions.

Details and run order are centralized in [`docs/scientific_examples.md`](docs/scientific_examples.md).

### `epidemic-regime` (scientific toy model)

Second compact CDS research-facing scenario in a different domain:
- deterministic epidemic regime candidates,
- explicit spread/capacity/intervention constraints,
- stability ranking with selected regime,
- toy-model disclaimer to avoid epidemiological overclaiming.

Details and run order are centralized in [`docs/scientific_examples.md`](docs/scientific_examples.md).

## Why this architecture matters

SCE Core keeps four mechanisms coupled in one inspectable loop:

1. **Constraints + trajectory selection** choose admissible plans.
2. **Decision backbone** shows what carried the decision.
3. **Reliability tracking** measures empirical stability quality.
4. **Episodic memory** changes future reselection pressure.

This coupling is what makes the system both practical and research-relevant.

## Documentation map

- **Product entrypoint:** `README.md` (this file)
- **Release notes:** [`CHANGELOG.md`](CHANGELOG.md)
- **Roadmap / delivery priorities:** [`ROADMAP.md`](ROADMAP.md)
- **Origin (history and motivation):** [`docs/origin.md`](docs/origin.md)
- **Theory bridge (CDS → SCE):** [`docs/constraint_driven_stability.md`](docs/constraint_driven_stability.md)
- **Scientific examples index (entrypoint):** [`docs/scientific_examples.md`](docs/scientific_examples.md)
- **Scientific positioning:** [`docs/scientific_positioning.md`](docs/scientific_positioning.md)
- **Research program (open problems):** [`docs/research_program.md`](docs/research_program.md)
- **Russian overview:** [`docs/OVERVIEW_RU.md`](docs/OVERVIEW_RU.md)
- **Extended docs index:** [`docs/README.md`](docs/README.md)
- **Governance/workflow guide:** [`docs/governance.md`](docs/governance.md)
- **Release checklist:** [`docs/release_readiness.md`](docs/release_readiness.md)

## Near-term direction (concise)

Near-term work stays split across product and research, on one engine:

- improve decision inspectability and replayability,
- make reliability/memory policies more robust over time,
- evolve `supplier-risk`, `hypothesis`, `resource-stability`, and `epidemic-regime` into a compact benchmark set,
- continue hardening API/UI surfaces without breaking compatibility.

Details: [`ROADMAP.md`](ROADMAP.md) and [`docs/research_program.md`](docs/research_program.md).

## Full install options

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

## License

Apache 2.0
