# Controlled Evolution

SCE Core models agent behavior as repeated decision/evolution steps:

```text
state → plan → score → execute → observe → learn → next state
```

The controlled evolution layer tracks how accurate those local steps are.

---

## Core idea

A decision trajectory is not judged only by the final outcome. Each step can be compared against what the system expected:

```text
predicted value → actual observed value → step error
```

Accumulated step error gives a simple reliability estimate for the trajectory.

---

## Step error

Each step records:

- name
- predicted value
- actual value
- optional weight
- absolute weighted error

```text
error = abs(predicted_value - actual_value) * weight
```

---

## Trajectory reliability

The current implementation derives reliability from accumulated error:

```text
reliability = 1 / (1 + cumulative_error)
```

This is intentionally simple. It gives a bounded score where:

- lower error means higher reliability
- higher error means lower reliability
- reliability is always between 0 and 1

---

## Why this matters

SCE already tracks:

- state stability
- memory bias
- exploration
- decision backbone

Controlled evolution adds another question:

```text
how reliable was the stepwise evolution that produced this decision?
```

This is useful for:

- comparing plan trajectories
- adjusting future memory bias
- detecting unreliable planners
- triggering exploration when predictions degrade
- escalating to a human when reliability is low

---

## Demo

Run:

```bash
sce run-controlled-evolution-demo-pretty
```

The demo prints:

- predicted values
- actual values
- per-step errors
- cumulative error
- mean error
- reliability
- trend

---

## Future work

Planned extensions:

- integrate reliability into plan scoring
- record controlled evolution reports as memory episodes
- use worsening error trends to trigger exploration
- attach reliability to decision backbone paths
- expose trajectory reliability through the API
