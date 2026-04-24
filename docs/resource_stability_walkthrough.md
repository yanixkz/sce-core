# Resource Stability Walkthrough (Scientific CDS Example)

This walkthrough is a reproducible, lightweight notebook-style artifact for the first scientific scenario in SCE Core.

## Run it

```bash
python examples/resource_stability_walkthrough.py
```

The walkthrough uses the real scenario implementation:

- `sce.scenarios.resource_stability_demo.run_resource_stability_demo()`

## A) Scientific question

> How does a simple population/resource system settle into a more stable regime under resource constraints?

In code, the scenario asks:

- `Which population-resource regime remains viable under explicit resource constraints?`

## B) CDS mapping used in the scenario

- **I (state information):** `population`, `available_resources`, `consumption_rate`, `regeneration_rate`.
- **E (available capacity/resources):** resource stock and regeneration capacity.
- **C (constraints):**
  - hard: `pressure <= 1.0`
  - soft: `regeneration_rate >= 0.9 * consumption_rate`
- **t (evolution steps):** transition from an unstable initial state to candidate regimes.
- **Stab (stability scoring/selection):** SCE weighted stability score under constraints.
- **S (selected stable regime):** top-ranked candidate from `scores` and `selected_state`.

Reference formula from the scenario output:

- `S = Stab(D(I, E, C, t))`

## C) Run the scenario directly

```python
from sce.scenarios.resource_stability_demo import run_resource_stability_demo

result = run_resource_stability_demo()
print(result["selected_state"])
```

## D) Inspect candidate states

The walkthrough script prints:

1. initial state
2. candidate regimes
3. stability score ranking
4. selected state + explanation

## E) Interpret baseline result

Typical interpretation:

- selected regime avoids persistent overshoot (`pressure <= 1.0`)
- regeneration stays close to consumption (soft renewal pressure)
- stability improves through lower conflict and higher support
- non-carrying regimes remain for follow-up experiments

## F) Parameter sensitivity (one change)

The walkthrough reruns the same scenario with one controlled change:

- `consumption_rate_multiplier=1.12`

This demonstrates how increased demand pressure changes stability margins and can alter candidate viability, while reusing the same scientific logic.

## Why this artifact exists

This file + script make the `resource-stability` scenario easier for scientists/labs to:

- understand CDS mapping concretely,
- reproduce results quickly,
- modify one parameter without refactoring core logic,
- extend toward richer resource-dynamics studies.
