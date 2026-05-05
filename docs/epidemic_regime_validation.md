# Epidemic-Regime Heuristic Validation Baseline

This workflow adds a lightweight, transparent baseline comparison for the epidemic-regime scenario.

## What this validates (and what it does not)

This validates a narrow behavioral sanity check:

- given the same case multipliers,
- compare SCE's selected epidemic regime against a deterministic heuristic expectation,
- inspect where behavior agrees or diverges.

This does **not** validate epidemiological correctness, predictive performance, or real-world calibration.
The heuristic is **not** ground truth.

## Run

```bash
python examples/validate_epidemic_regime_csv.py examples/data/epidemic_regime_cases.csv
```

Optional CSV output:

```bash
python examples/validate_epidemic_regime_csv.py \
  examples/data/epidemic_regime_cases.csv \
  --out examples/output/epidemic_regime_validation.csv
```

## Output columns

- case id and multipliers,
- SCE selected regime and top score,
- heuristic expected regime/class,
- agreement flag,
- concise heuristic reason,
- compact heuristic diagnostics (`pressure_index`, `capacity_gap`, `recovery_balance`, `intervention_burden`),
- concise SCE explanation.

## How to interpret agreement/disagreement

- **Agreement** means SCE and heuristic point to the same regime under this toy setup.
- **Disagreement** is an inspection signal, not proof of model failure:
  - SCE constraint weighting may emphasize different tradeoffs,
  - heuristic thresholds are intentionally coarse,
  - cases near boundaries may flip with small multiplier shifts.

## Why this helps scientific credibility

- makes assumptions explicit and inspectable,
- adds a reproducible baseline comparator,
- supports falsifiable follow-up tests rather than narrative-only interpretation.

## Next validation steps

- compare against deterministic SIR/SEIR toy outcomes,
- compare against domain expert expectations,
- calibrate heuristic parameters on known toy examples,
- expand benchmark CSV cases around boundary regions.
