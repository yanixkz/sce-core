# Constraint Sweep Explorer

Constraint Sweep Explorer is a deterministic CDS scientific toy model for the question:

> How does selection change as constraints change?

It extends the earlier possibility-space examples from a single selection event to a sweep over changing constraint pressure:

```text
Possibility Space
↓
Constraint Change
↓
Selection Change
```

## What the demo does

The demo creates a fixed population of candidates. Each candidate has transparent score dimensions:

- coherence
- entropy
- support
- conflict
- cost

It then recomputes the CDS-style stability score at several constraint-strength values:

```text
0.0, 0.2, 0.4, 0.6, 0.8, 1.0
```

As constraint strength increases, conflict and cost penalties increase. The candidate population does not change; only the pressure applied to conflict and cost changes.

## Stability rule

The sweep uses the same weighted CDS stability terms used by the core scorer, with constraint strength applied to conflict and cost:

```text
stability = coherence - 0.4 * entropy + 0.6 * support
            - constraint_strength * (0.8 * conflict + 0.5 * cost)
```

Higher stability ranks earlier. Ties use deterministic candidate-id ordering.

## Example output

```text
Constraint

0.0 | A
0.2 | A
0.4 | B
0.6 | C
0.8 | D
1.0 | D
```

The winner changes are reported as toy phase transitions:

```text
0.4 -> Candidate A -> Candidate B
0.6 -> Candidate B -> Candidate C
0.8 -> Candidate C -> Candidate D
```

These are regime-shift illustrations inside a deterministic toy system, not empirical predictions.

## Result structure

The result includes:

```json
{
  "sweep_steps": [],
  "winner_history": [],
  "winner_transitions": [],
  "constraint_values": [],
  "ranking_history": []
}
```

Additional fields include the fixed candidate population, an ASCII visualization, the demo name, the core question, and the CDS pipeline labels.

## CLI usage

```bash
sce demo constraint-sweep
sce demo constraint-sweep --json
python examples/constraint_sweep_demo.py
```

## Scientific positioning

This example introduces three CDS ideas in a compact, inspectable form:

- **Phase transition:** a winner changes when constraint pressure crosses a threshold in the sweep.
- **Regime shift:** the selected structure changes from one candidate regime to another.
- **Constraint sensitivity:** the ranking depends on how strongly conflict and cost are penalized.

This is a deterministic toy model. It does not claim prediction, economics, biology, or intelligence modeling.
