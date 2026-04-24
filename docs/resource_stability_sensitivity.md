# Resource Stability Sensitivity Grid (Scientific CDS Toy Experiment)

This document describes a lightweight, reproducible sensitivity experiment for the `resource-stability` scenario.

## Scientific question

> How do controlled changes in population pressure, consumption demand, and regeneration capacity shift the selected stable regime and stability margins?

The experiment is intentionally small and deterministic. It is a scientific-style inspection artifact, not a calibrated domain model.

## What is varied

The script runs `run_resource_stability_demo(...)` over a compact grid:

- `population_multiplier`: `(0.95, 1.00, 1.05)`
- `consumption_rate_multiplier`: `(0.95, 1.00, 1.10)`
- `regeneration_rate_multiplier`: `(0.95, 1.00)`

Total runs: `3 * 3 * 2 = 18`

## How to run

```bash
python examples/resource_stability_sensitivity.py
```

Optional CSV output:

```bash
python examples/resource_stability_sensitivity.py \
  --out examples/output/resource_stability_sensitivity.csv
```

## What to look for in output

Each row reports:

- parameter triplet (`population_multiplier`, `consumption_rate_multiplier`, `regeneration_rate_multiplier`),
- selected regime (`selected_state` / `selected_regime`),
- top stability score,
- runner-up stability score,
- stability margin (`top - runner_up`).

Interpretation focus:

- where winner identity changes,
- where the winner stays the same but stability margin shrinks,
- whether higher demand pressure narrows viable ranking separation.

## CDS mapping

This uses the same CDS mapping as the base scenario:

- **I**: state variables (`population`, `available_resources`, `consumption_rate`, `regeneration_rate`),
- **E**: available capacity (`available_resources`, regeneration capability),
- **C**: hard/soft resource constraints,
- **t**: transition from unstable initial regime to candidate regimes,
- **Stab**: SCE weighted scoring under constraints,
- **S**: selected regime returned as `selected_state`.

Formula reference remains:

- `S = Stab(D(I, E, C, t))`

## Why this is still a toy experiment

This experiment is useful for reproducibility and qualitative trend checks, but it is:

- not fitted to empirical data,
- not a validated ecological or socio-economic simulator,
- not a claim of domain forecasting.

It is a transparent CDS research scaffold.

## How a scientist could extend it

Natural next steps:

1. sweep a wider or finer multiplier range around identified transition boundaries,
2. add stochastic perturbations with fixed seeds and compare confidence intervals,
3. compare CDS ranking trends with a baseline model (e.g., logistic-resource dynamics),
4. introduce interacting populations or explicit policy control levers.
