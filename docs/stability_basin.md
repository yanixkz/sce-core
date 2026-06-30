# Stability Basin

This demo asks a narrow toy-model question:

> How much perturbation can a structure absorb before losing stability?

It starts with deterministic candidate structures, selects the best candidate by
an inspectable stability score, applies fixed perturbations, and recalculates
whether the selected structure remains stable.

```text
Selection
↓
Persistence
↓
Robustness
```

## Model

The default perturbation set is:

- `+1%`
- `+5%`
- `+10%`
- `+20%`
- `+30%`

For each perturbation, the demo increases the selected candidate's toy load and
recalculates stability against a capacity boundary. A candidate is marked stable
only when its perturbed load remains within capacity and its toy stability score
stays non-negative.

This is a deterministic toy model only. It does not claim a physical law,
validated engineering limit, or real-world prediction.

## Example output

```text
Perturbation  Stable?
---------------------
  1%          Yes
  5%          Yes
 10%          Yes
 20%          No
 30%          No
```

## Metric

```text
Stability Basin Size = largest tested perturbation that remains stable
```

For the default run:

```text
Stability Basin Size: 10%
```

## ASCII

```text
Stable
███████████████

Unstable
██
```

## CLI

```bash
sce demo stability-basin
sce demo stability-basin --json
```
