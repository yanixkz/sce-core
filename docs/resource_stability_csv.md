# Resource-Stability CSV Batch Runner

This workflow is a lightweight **bring-your-own-cases** helper for the resource-stability scientific scenario.
It lets you provide a small CSV of parameter cases, run deterministic SCE stability selection per case, and inspect an interpretable result table.

## What this is

- A small batch experiment helper for `run_resource_stability_demo(...)`.
- A way to test user-provided scenario cases instead of only built-in sweeps.
- A deterministic toy-model utility for quick research iteration.

## Expected input format

Input CSV must include these columns:

- `case_id`
- `population_multiplier`
- `consumption_rate_multiplier`
- `regeneration_rate_multiplier`

Example file: `examples/data/resource_stability_cases.csv`.

## Run it

```bash
python examples/run_resource_stability_csv.py examples/data/resource_stability_cases.csv
```

Optional output CSV:

```bash
python examples/run_resource_stability_csv.py \
  examples/data/resource_stability_cases.csv \
  --out examples/output/resource_stability_cases_results.csv
```

## Output interpretation

For each case, output includes:

- input multipliers,
- `selected_regime` / `selected_state`,
- `top_score`,
- `runner_up_score`,
- `margin` (top minus runner-up),
- short explanation.

A larger positive margin suggests clearer separation between the selected regime and the next-best alternative under current toy constraints.

## How this differs from sensitivity grid

- **Sensitivity grid** (`examples/resource_stability_sensitivity.py`): built-in deterministic parameter sweep.
- **CSV runner** (`examples/run_resource_stability_csv.py`): user-provided case list.

## Related baseline comparison

For an early behavioral sanity check against a transparent heuristic baseline, see [`resource_stability_validation.md`](resource_stability_validation.md).

## Limitations

- This is a toy parameter sweep helper, not a scientific validation pipeline.
- It does not provide real-world calibration or empirical claims.
- Arbitrary dataset ingestion and schema-flexible loaders are not implemented yet.
