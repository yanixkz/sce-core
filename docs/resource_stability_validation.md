# Resource-Stability Heuristic Validation Baseline

This workflow adds a lightweight, transparent baseline comparison for the resource-stability scenario.

## What this validates (and what it does not)

This validates a narrow behavioral sanity check:

- given the same case multipliers,
- compare SCE's selected regime against a simple deterministic heuristic expectation,
- inspect where behavior agrees or diverges.

This does **not** validate scientific correctness, predictive performance, or real-world calibration.
The heuristic is **not** ground truth.

## Run

```bash
python examples/validate_resource_stability_csv.py examples/data/resource_stability_cases.csv
```

Optional CSV output:

```bash
python examples/validate_resource_stability_csv.py \
  examples/data/resource_stability_cases.csv \
  --out examples/output/resource_stability_validation.csv
```

## Output columns

- case id and multipliers,
- SCE selected regime and top score,
- heuristic expected regime/class,
- agreement flag,
- concise heuristic reason,
- concise SCE explanation.

## How to interpret agreement/disagreement

- **Agreement** means SCE and heuristic point to the same regime under this toy setup.
- **Disagreement** is a useful inspection signal, not a failure proof:
  - constraint weighting may dominate different features,
  - heuristic thresholds may be too coarse,
  - case may sit near a regime boundary.

## Why this helps scientific credibility

- makes assumptions explicit and inspectable,
- adds a reproducible baseline comparator,
- encourages falsifiable follow-up tests instead of narrative-only interpretation.

## Next validation steps

- compare ranking trends against known toy equations,
- compare behaviors on external datasets,
- include domain expert review,
- evolve into a benchmark suite with documented failure modes.
