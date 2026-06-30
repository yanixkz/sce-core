# Persistence Over Time

This demo asks a narrow toy-model question: after a structure has been selected,
how long does it survive under deterministic environmental pressure?

It demonstrates persistence rather than one-step selection.

```text
Selection
↓
Persistence
↓
Survival Duration
```

## Model

The simulation generates four deterministic candidates and evaluates them from
`t0` through `t100`. At each time step, deterministic environmental pressure is
applied and the demo tracks:

- stability
- survival
- elimination

This is a toy model only. It does not claim real-world prediction.

## Metric

```text
Persistence Score = survival_steps / total_steps
```

The default run uses `total_steps = 100`.

## Example output

```text
Candidate A = 1.00
Candidate B = 0.84
Candidate C = 0.35
Candidate D = 0.07
```

```text
A ██████████
B ████████
C ███
D █
```

## CLI

```bash
sce demo persistence
```
