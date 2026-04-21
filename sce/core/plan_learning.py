from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from sce.core.planning import Plan


@dataclass(frozen=True)
class PlanOutcome:
    """Observed result of executing a plan."""

    success: bool
    reward: float
    reason: str = ""


@dataclass(frozen=True)
class PlanLearningStep:
    plan_name: str
    outcome: PlanOutcome
    weights_after: Dict[str, float]


class PlanLearning:
    """Simple online learning layer for plan selection.

    This is not full reinforcement learning. It is a small adaptive memory that
    shifts feature weights based on execution outcomes.
    """

    def __init__(self, learning_rate: float = 0.1) -> None:
        self.learning_rate = learning_rate
        self.weights: Dict[str, float] = {
            "evidence": 1.0,
            "escalation": 1.0,
            "monitoring": 1.0,
            "efficiency": 1.0,
        }
        self.history: List[PlanLearningStep] = []

    def evaluate_outcome(self, success: bool, reason: str = "") -> PlanOutcome:
        return PlanOutcome(success=success, reward=1.0 if success else -1.0, reason=reason)

    def update(self, plan: Plan, outcome: PlanOutcome) -> Dict[str, float]:
        reward = max(-1.0, min(1.0, outcome.reward))
        lr = self.learning_rate

        for action in plan.actions:
            if action.name == "fetch_supplier_risk":
                self.weights["evidence"] = max(0.0, self.weights["evidence"] + lr * reward)
            elif action.name == "request_review":
                self.weights["escalation"] = max(0.0, self.weights["escalation"] + lr * reward)
            elif action.name == "monitor":
                self.weights["monitoring"] = max(0.0, self.weights["monitoring"] + lr * reward)

        if not outcome.success:
            self.weights["efficiency"] = max(0.0, self.weights["efficiency"] - lr * 0.5)
        elif len(plan.actions) <= 2:
            self.weights["efficiency"] = max(0.0, self.weights["efficiency"] + lr * 0.25)

        snapshot = self.get_weights()
        self.history.append(
            PlanLearningStep(
                plan_name=plan.name,
                outcome=outcome,
                weights_after=snapshot,
            )
        )
        return snapshot

    def get_weights(self) -> Dict[str, float]:
        return dict(self.weights)
