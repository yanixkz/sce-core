from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sce.core.planning import Plan
from sce.core.types import State


@dataclass(frozen=True)
class ScoredPlan:
    plan: Plan
    score: float
    reason: str


class PlanScorer:
    """Heuristic scorer for comparing alternative plans.

    Phase 1 favors plans that:
    - gather external evidence when risk/supplier assessment is relevant
    - escalate when the current claim already indicates elevated risk
    - avoid unnecessary length
    """

    def score(self, plan: Plan, state: State, goal: str) -> ScoredPlan:
        goal_lower = goal.lower()
        claim = str(state.data.get("claim", "")).lower()

        value = 0.0
        reasons: List[str] = []

        if any(action.name == "fetch_supplier_risk" for action in plan.actions):
            value += 1.0
            reasons.append("includes external evidence collection")

        if ("risk" in goal_lower or "supplier" in goal_lower) and any(
            action.name == "fetch_supplier_risk" for action in plan.actions
        ):
            value += 1.0
            reasons.append("matches supplier/risk assessment goal")

        if ("unreliable" in claim or "risk" in claim) and any(
            action.name == "request_review" for action in plan.actions
        ):
            value += 1.0
            reasons.append("escalates an already risky state")

        if any(action.name == "monitor" for action in plan.actions) and ("unreliable" in claim or "risk" in claim):
            value -= 0.5
            reasons.append("monitoring may be too weak for a risky state")

        value -= max(0, len(plan.actions) - 2) * 0.1
        if len(plan.actions) <= 2:
            reasons.append("plan is compact")

        return ScoredPlan(plan=plan, score=value, reason=", ".join(reasons))


class PlanSelector:
    """Choose the highest-scoring plan from a set of alternatives."""

    def __init__(self, scorer: PlanScorer | None = None) -> None:
        self.scorer = scorer or PlanScorer()

    def select(self, plans: List[Plan], state: State, goal: str) -> ScoredPlan:
        if not plans:
            raise ValueError("plans must not be empty")
        scored = [self.scorer.score(plan, state, goal) for plan in plans]
        return max(scored, key=lambda item: item.score)
