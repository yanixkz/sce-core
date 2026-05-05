# Epidemic-Regime CSV Batch Runner (Toy Scientific Workflow)

This helper runs the epidemic-regime deterministic toy scenario over a small user-provided CSV of multiplier cases.

> **Important:** This is a lightweight CDS toy-model batch workflow for inspectable scenario selection. It is **not** epidemiological validation and does **not** ingest empirical epidemiology datasets.

## What this is

- A compact "bring your own cases" batch runner for epidemic-regime toy scenarios.
- Each row contains multipliers that stress or relax deterministic candidate-regime scoring.
- Output is a readable table and optional CSV with selected regime and score margin.

## Expected input CSV format

Required columns:

- `case_id`
- `transmission_multiplier`
- `recovery_support_multiplier`
- `healthcare_capacity_multiplier`
- `intervention_cost_multiplier`

Example file:

- `examples/data/epidemic_regime_cases.csv`

## Run it

```bash
python examples/run_epidemic_regime_csv.py examples/data/epidemic_regime_cases.csv
```

Optional output CSV:

```bash
python examples/run_epidemic_regime_csv.py \
  examples/data/epidemic_regime_cases.csv \
  --out examples/data/epidemic_regime_results.csv
```

## Output fields

Each result row includes:

- `case_id`
- input multipliers
- `selected_regime`
- `top_score`
- `runner_up_score`
- `margin`
- `short_explanation`

## How to interpret selected regimes and margins

- `selected_regime` is the highest-scoring deterministic candidate under the configured constraints.
- `margin = top_score - runner_up_score`.
- Larger margins indicate stronger preference for the selected regime relative to the next candidate in this toy setup.

## Limitations

- Deterministic toy batch workflow only.
- Not a validated epidemiology simulator.
- No empirical dataset ingestion, calibration, or forecasting support yet.

## How this differs from the walkthrough

- `examples/epidemic_regime_walkthrough.py` + `docs/epidemic_regime_demo.md`:
  - one guided example with narrative interpretation.
- `examples/run_epidemic_regime_csv.py` + this page:
  - user-provided batch cases in CSV with concise comparable result rows.
