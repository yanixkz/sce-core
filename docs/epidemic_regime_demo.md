# Epidemic Regime Stability Demo (Scientific CDS Example)

This walkthrough documents a second compact scientific scenario in SCE Core.

> **Disclaimer:** this is a deterministic toy model for CDS-style regime selection, **not** a validated epidemiology simulator.

## Run it

```bash
sce demo epidemic-regime
```

Programmatic entrypoint:

- `sce.scenarios.epidemic_regime_demo.run_epidemic_regime_demo()`

## Scientific question

> Which epidemic regime remains most stable under spread, capacity, and intervention constraints?

## CDS mapping used in this scenario

- **I (state information):** susceptible/infected/recovered fractions, transmission pressure, overload pressure.
- **E (capacity/support):** healthcare capacity and recovery support.
- **C (constraints):**
  - hard: `overload_pressure <= 1.0`
  - soft: `transmission_pressure <= 0.7`
  - soft: `intervention_cost <= 0.55`
- **t (evolution step):** transition from an initially escalating regime to deterministic candidate regimes.
- **Stab (stability scoring):** SCE weighted stability under constraints.
- **S (selected stable regime):** top-ranked candidate in `scores` and `selected_regime`.

Reference formula:

- `S = Stab(D(I, E, C, t))`

## How to interpret output

The demo returns structured fields including:

- `initial_state`
- `candidates`
- `scores`
- `selected_regime`
- `constraints`
- `stability_explanation`
- `next_research_actions`
- `parameters`

Interpretation pattern:

1. inspect whether top-ranked regimes satisfy the hard capacity guardrail,
2. inspect soft-constraint penalties (spread pressure, intervention affordability),
3. compare stability margins between top candidates,
4. use `next_research_actions` to extend the toy experiment.

## Light parameterization

The demo supports deterministic multipliers for quick sensitivity checks:

- `transmission_multiplier`
- `recovery_support_multiplier`
- `healthcare_capacity_multiplier`
- `intervention_cost_multiplier`

These default to `1.0` and preserve backward-compatible behavior.

## What a scientist could extend next

- Add explicit age/contact strata while preserving deterministic selection.
- Add a small parameter grid to map regime boundary transitions.
- Compare ranking trends with a simple compartment baseline for sanity checks.
