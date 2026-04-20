from __future__ import annotations

from typing import Any, Dict

from sce.core.llm_planner import LLMPlanner
from sce.core.planning import PlanExecutor
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


class FakeLLM:
    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "steps": [
                {
                    "name": "fetch_supplier_risk",
                    "description": "Fetch supplier risk data",
                    "tool": "supplier_risk_api",
                    "arguments": {"supplier_id": "supplier A"},
                },
                {
                    "name": "request_review",
                    "description": "Escalate for review",
                    "arguments": {},
                },
            ]
        }


def run_llm_planning_demo() -> Dict[str, Any]:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)

    state = State(
        state_type="planning_context",
        data={"entity": "supplier A", "claim": "supplier may be unreliable"},
    )

    planner = LLMPlanner(FakeLLM())
    plan = planner.plan(state, goal="assess supplier risk")

    executor = PlanExecutor(bridge)
    result = executor.execute(plan, state)

    return {
        "scenario": "llm_planning",
        "plan": [a.name for a in plan.actions],
        "success": result.success,
    }
