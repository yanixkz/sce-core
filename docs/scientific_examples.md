# Scientific Examples Index

SCE Core scientific examples are lightweight, deterministic toy models for studying Constraint-Driven Stability (CDS).
They are transparent and reproducible, but they are **not** validated domain simulators.

## Quick start

Want to validate backend endpoints with real requests (outside CLI demos)? See [`live_api_quickstart.md`](live_api_quickstart.md).

| Example | Command | Artifact type | What it demonstrates | CDS concepts used |
|---|---|---|---|---|
| `resource-stability` | `sce demo resource-stability` | CLI scientific demo | Resource-constrained regime selection and carrying-state preference under explicit hard/soft constraints. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `resource-stability` walkthrough | `python examples/resource_stability_walkthrough.py` | Walkthrough script + notes (`docs/resource_stability_walkthrough.md`) | Stepwise interpretation of candidate regimes, ranking, selected state, and one-parameter stress rerun. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `resource-stability` sensitivity grid | `python examples/resource_stability_sensitivity.py` | Parameter grid script + notes (`docs/resource_stability_sensitivity.md`) | Deterministic sweep over pressure/demand/regeneration multipliers and stability-margin shifts. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `resource-stability` CSV runner | `python examples/run_resource_stability_csv.py examples/data/resource_stability_cases.csv` | User-case batch script + notes (`docs/resource_stability_csv.md`) | User-provided case list with deterministic stability-selection outputs. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `resource-stability` heuristic validation | `python examples/validate_resource_stability_csv.py examples/data/resource_stability_cases.csv` | Baseline comparison script + notes (`docs/resource_stability_validation.md`) | Early behavioral sanity check: SCE selected regime vs transparent heuristic expectation. | `C`, `Stab`, `S` |
| `epidemic-regime` | `sce demo epidemic-regime` | CLI scientific demo | Regime selection under transmission, capacity, and intervention-cost constraints with explicit toy-model disclaimer. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `epidemic-regime` walkthrough | `python examples/epidemic_regime_walkthrough.py` | Walkthrough script + notes (`docs/epidemic_regime_demo.md`) | Candidate comparison and deterministic sensitivity checks in a second constrained domain. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `epidemic-regime` CSV runner | `python examples/run_epidemic_regime_csv.py examples/data/epidemic_regime_cases.csv` | User-case batch script + notes (`docs/epidemic_regime_csv.md`) | User-provided epidemic toy cases with deterministic regime-selection outputs. | `I`, `E`, `C`, `t`, `Stab`, `S` |
| `cyrillic-babel` | `sce demo cyrillic-babel` or `python examples/cyrillic_babel_demo.py` | CLI scientific toy + standalone example (`docs/cyrillic_babel_demo.md`) | Finite Cyrillic alphabet possibility space, normalization constraints, deterministic selection address, toy selection pressure over sampled Cyrillic candidates, and persistence of one reproducible pattern. | possibility space, `C`, selection, persistent pattern |
| `epidemic-regime` heuristic validation | `python examples/validate_epidemic_regime_csv.py examples/data/epidemic_regime_cases.csv` | Baseline comparison script + notes (`docs/epidemic_regime_validation.md`) | Early behavioral sanity check: SCE selected epidemic regime vs transparent heuristic expectation. | `C`, `Stab`, `S` |

## Recommended path for a new scientific reader

1. Read scientific framing and non-claims in [`scientific_positioning.md`](scientific_positioning.md).
2. Read the scientist-facing outreach/readiness note in [`scientist_pitch.md`](scientist_pitch.md).
3. Run `sce demo resource-stability`.
4. Run the resource sensitivity grid (`python examples/resource_stability_sensitivity.py`).
5. Run the CSV case runner (`python examples/run_resource_stability_csv.py examples/data/resource_stability_cases.csv`).
6. Run `sce demo epidemic-regime`.
7. Run `sce demo cyrillic-babel` for a compact possibility-space and selection toy.
8. Read the broader open-problems roadmap in [`research_program.md`](research_program.md).

## CDS mapping summary across examples

| CDS element | `resource-stability` family | `epidemic-regime` family | `cyrillic-babel` toy |
|---|---|---|---|
| `I` (state information) | Population, available resources, consumption and regeneration rates. | Susceptible/infected/recovered state, transmission and overload pressures. | Normalized phrase and string length. |
| `E` (capacity/support) | Resource stock and regeneration capacity. | Healthcare capacity and recovery support. | Finite alphabet capacity that bounds constructible strings. |
| `C` (constraints) | Hard pressure guardrail + soft regeneration-vs-consumption viability pressure. | Hard overload guardrail + soft transmission and intervention-cost pressures. | Allowed characters, fixed length, and normalization. |
| `t` (candidate transition step) | Deterministic transition from initial unstable regime to candidate carrying/non-carrying regimes. | Deterministic transition from escalating regime to candidate intervention regimes. | Deterministic normalization, candidate sampling, scoring, and hash-address generation. |
| `Stab` (scoring + selection) | Weighted CDS-style stability ranking under explicit constraints. | Same ranking principle in a different constrained domain. | Toy scorer; illustrates transparent selection pressure over sampled Cyrillic candidates from a constrained space. |
| `S` (selected stable regime) | Top-ranked selected state (`selected_state`) with transparent score table. | Top-ranked selected regime (`selected_regime`) with transparent score table. | The normalized phrase as selected point and persistent pattern. |

## Extension ideas

- Add empirical data calibration layers while preserving reproducible baseline artifacts.
- Compare CDS ranking trends against known toy dynamics baselines.
- Expand parameter sweeps around regime-boundary regions.
- Add trajectory replay artifacts across repeated runs.
- Add attractor/regime recurrence detection for longer-run analysis.

## Limitations

- All scientific examples here are deterministic toy models.
- They are not validated scientific simulators.
- They do not yet support empirical performance or forecasting claims.
