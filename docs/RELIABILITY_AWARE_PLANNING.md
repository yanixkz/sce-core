# Reliability-Aware Planning

SCE Core can use trajectory reliability as part of plan selection.

Traditional plan scoring in SCE starts with:

```text
base_score + memory_bias
```

Reliability-aware planning extends this to:

```text
base_score + memory_bias + reliability_bonus
```

---

## Why this matters

A plan can have a strong base score but poor historical reliability.

Another plan can have a lower base score but a more reliable trajectory.

Reliability-aware planning lets SCE prefer the plan that is not only promising, but also more dependable based on controlled evolution signals.

---

## Planner

`ReliabilityAwarePlanner` wraps `MemoryAwarePlanner` and adds reliability to ranking.

```python
from sce.core.planning import MemoryAwarePlanner, ReliabilityAwarePlanner, ToolPlanner
from sce.core.episode_memory import EpisodeMemory

memory_planner = MemoryAwarePlanner(ToolPlanner(), EpisodeMemory())
planner = ReliabilityAwarePlanner(
    memory_planner,
    reliability_by_plan={
        "supplier_risk_plan": 0.1,
        "escalation_plan": 0.95,
    },
    reliability_weight=1.0,
)
```

---

## Demo

Run:

```bash
sce run-reliability-aware-planning-demo-pretty
```

The demo shows the planner selecting one plan without reliability and a different plan when trajectory reliability is included.

---

## Relationship to controlled evolution

Controlled evolution measures trajectory reliability:

```text
predicted value → actual value → step error → reliability
```

Reliability-aware planning uses that reliability during future plan scoring.

This closes the loop:

```text
execute → observe error → compute reliability → affect next plan
```

---

## Future work

Planned extensions:

- automatic reliability updates from executed plans
- reliability stored inside episodic memory
- reliability decay over time
- reliability by state/goal/context, not only by plan name
- reliability-aware exploration triggers
