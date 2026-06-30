# SCE Core

[![Tests](https://img.shields.io/github/actions/workflow/status/yanixkz/sce-core/tests.yml?branch=main&label=tests)](https://github.com/yanixkz/sce-core/actions/workflows/tests.yml)

SCE Core is an **early alpha** computational framework for studying
**Constraint-Driven Stability (CDS)** in adaptive systems: how constraints and
dynamics select persistent structures from larger possibility spaces,
with an applied decision-engine surface for AI agents.

It combines:
- explicit possibility spaces for plans, hypotheses, regimes, and toy candidates,
- constraints and dynamics that reduce and reshape those spaces,
- stability selection and transparent ranking,
- reliability tracking from outcomes and persistence signals,
- episodic memory and inspectable API/graph/UI surfaces as applied layers.

```text
Possibility Space
↓
Constraints
↓
Dynamics
↓
Selection
↓
Persistence
```

The decision engine, API, memory, and reliability features remain practical surfaces
built on the same CDS framework.

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
sce demo cyrillic-babel
sce demo selection-landscape
sce demo constraint-sweep
```

Run the API and open UI:

```bash
uvicorn sce.api:app --reload
# then open http://127.0.0.1:8000/ui
```

Verify the live API in 5 minutes: [`docs/live_api_quickstart.md`](docs/live_api_quickstart.md).

Run user-provided resource-stability cases from CSV:
```bash
python examples/run_resource_stability_csv.py examples/data/resource_stability_cases.csv
python examples/run_epidemic_regime_csv.py examples/data/epidemic_regime_cases.csv
```

## What SCE Core is (and is not)

SCE Core is not a chat wrapper and not only a demo collection.
It is a computational framework for studying selection and persistence in constrained experiments over possibility spaces, with reusable decision, API, memory, and reliability surfaces for applied workflows.

- **Scientific framework layer:** CDS-oriented toy models and inspectable stability-selection workflows.
- **Applied decision layer:** runnable demos and API/UI surfaces for agent decision tasks built on the same framework.
- **Theory bridge:** CDS → SCE operational mapping.
- **Research layer:** open problems grounded in implemented mechanisms for constraints, dynamics, selection, and persistence.
- **Origin layer:** historical and philosophical motivation.

## Canonical CLI and graph commands

```bash
sce demo
sce demo supplier-risk
sce demo hypothesis
sce demo resource-stability
sce demo epidemic-regime
sce demo cyrillic-babel
sce demo selection-landscape
sce demo constraint-sweep
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
- Need a practical live proof flow (including sample payloads and a verification script)? See [`docs/live_api_quickstart.md`](docs/live_api_quickstart.md).

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

## Scientific Evolution

The scientific examples are evolving from single constrained-regime demos toward broader possibility-space and persistence experiments:

```text
Resource Stability
↓
Epidemic Regime
↓
Cyrillic Babel
↓
Selection Landscape
↓
Constraint Sweep
```

- **Resource Stability** demonstrates stable regime emergence under explicit resource constraints.
- **Epidemic Regime** demonstrates selection among competing intervention regimes in a deterministic toy domain.
- **Cyrillic Babel** demonstrates a finite possibility space, normalization constraints, deterministic selection, and a reproducible persistent pattern.
- **Selection Landscape** demonstrates how stability is distributed across a sampled candidate population rather than only reporting the selected candidate.
- **Constraint Sweep** demonstrates how selection changes as constraint strength changes in a deterministic toy population.

SCE is not a theory of generation. It is a working research direction for studying selection and persistence through reproducible toy models, transparent scoring, and possibility-space exploration.

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

### `cyrillic-babel` (scientific toy model)

Possibility-space and deterministic-selection toy:
- finite Cyrillic alphabet candidate space,
- normalization constraints and deterministic address generation,
- toy selection pressure over sampled candidates,
- reproducible persistent pattern without language-understanding claims.

Details and run order are centralized in [`docs/scientific_examples.md`](docs/scientific_examples.md).

### `selection-landscape` (scientific toy model)

Deterministic possibility-space sample for a reproducible selection experiment:
- toy candidate population with explicit scoring dimensions,
- weighted stability distribution over the full sampled landscape,
- best, median, and worst candidates reported for distribution context,
- bridge to the Constraint Sweep Explorer experiment.

This demo is a toy model only; it makes no prediction or intelligence claims. Details and run order are centralized in [`docs/scientific_examples.md`](docs/scientific_examples.md).

## Why this architecture matters

SCE Core treats candidate plans, hypotheses, or toy regimes as a bounded
possibility space. Constraints and dynamics reduce that space, selection ranks
viable candidates, and reliability/memory provide early persistence signals.

SCE Core keeps four mechanisms coupled in one inspectable loop:

1. **Constraints + trajectory selection** choose admissible plans from a possibility space.
2. **Decision backbone** shows what carried the decision.
3. **Reliability tracking** measures empirical stability quality.
4. **Episodic memory** changes future reselection pressure and persistence tracking.

This coupling is what makes the system both practical and research-relevant.

## Documentation map

- **Product entrypoint:** `README.md` (this file)
- **Release notes:** [`CHANGELOG.md`](CHANGELOG.md)
- **Roadmap / delivery priorities:** [`ROADMAP.md`](ROADMAP.md)
- **Origin (history and motivation):** [`docs/origin.md`](docs/origin.md)
- **Theory bridge (CDS → SCE):** [`docs/constraint_driven_stability.md`](docs/constraint_driven_stability.md)
- **Possibility spaces and stability selection:** [`docs/possibility_and_selection.md`](docs/possibility_and_selection.md)
- **Scientific examples index (entrypoint):** [`docs/scientific_examples.md`](docs/scientific_examples.md)
- **Resource-stability CSV batch runner:** [`docs/resource_stability_csv.md`](docs/resource_stability_csv.md)
- **Epidemic-regime CSV batch runner:** [`docs/epidemic_regime_csv.md`](docs/epidemic_regime_csv.md)
- **Resource-stability heuristic validation baseline:** [`docs/resource_stability_validation.md`](docs/resource_stability_validation.md)
- **Epidemic-regime heuristic validation baseline:** [`docs/epidemic_regime_validation.md`](docs/epidemic_regime_validation.md)
- **Cyrillic Babel scientific toy:** [`docs/cyrillic_babel_demo.md`](docs/cyrillic_babel_demo.md)
- **Selection Landscape Explorer:** [`docs/selection_landscape.md`](docs/selection_landscape.md)
- **Constraint Sweep Explorer:** [`docs/constraint_sweep.md`](docs/constraint_sweep.md)
- **Scientist outreach/readiness pitch:** [`docs/scientist_pitch.md`](docs/scientist_pitch.md)
- **Public demo script (5–7 min):** [`docs/public_demo_script.md`](docs/public_demo_script.md)
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
- evolve `supplier-risk`, `hypothesis`, `resource-stability`, `epidemic-regime`, `cyrillic-babel`, and `selection-landscape` into a compact benchmark set,
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
