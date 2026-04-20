from __future__ import annotations

from typing import Any, Dict

from sce.core.actions import Action
from sce.core.plan_scoring import PlanSelector
from sce.core.planning import Plan, PlanExecutor
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def run_plan_scoring_demo() -> Dict[str, Any]:
    state = State("context", {"claim": "supplier is unreliable"})
    goal = "assess supplier risk"

    good_plan = Plan(
        name="good_plan",
        actions=[
            Action(
                name="fetch_supplier_risk",
                description="",
                action_type="tool",
                payload={"tool": "supplier_risk_api", "arguments": {}},
            ),
            Action(
                name="request_review",
                description="",
                action_type="workflow",
                payload={},
            ),
        ],
        reason="",
    )

    weak_plan = Plan(
        name="weak_plan",
        actions=[
            Action(name="monitor", description="", action_type="workflow", payload={})
        ],
        reason="",
    )

    selector = PlanSelector()
    best = selector.select([weak_plan, good_plan], state, goal)

    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)
    executor = PlanExecutor(bridge)

    result = executor.execute(best.plan, state)

    return {
        "scenario": "plan_scoring",
        "selected_plan": best.plan.name,
        "score": best.score,
        "reason": best.reason,
        "execution_success": result.success,
    }
