from __future__ import annotations

from typing import Any, Dict

from sce.core.planning import PlanExecutor, ToolPlanner
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def run_planning_demo() -> Dict[str, Any]:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)

    state = State(
        state_type="planning_context",
        data={
            "entity": "supplier A",
            "claim": "supplier A may be high risk",
        },
    )

    planner = ToolPlanner()
    plan = planner.plan(state, goal="assess supplier risk")
    executor = PlanExecutor(bridge)
    result = executor.execute(plan, state)

    return {
        "scenario": "planning",
        "plan": {
            "name": plan.name,
            "reason": plan.reason,
            "actions": [action.name for action in plan.actions],
        },
        "success": result.success,
        "results": [
            {
                "success": item.success,
                "message": item.message,
                "state": item.resulting_state.data,
            }
            for item in result.results
        ],
    }
