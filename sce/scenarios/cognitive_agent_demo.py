from __future__ import annotations

from typing import Dict

from sce.core.actions import Action
from sce.core.cognitive_agent import CognitiveAgent
from sce.core.planning import Plan, PlanExecutor
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def run_cognitive_agent_demo() -> Dict:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)
    executor = PlanExecutor(bridge)

    agent = CognitiveAgent(executor)

    state = State("context", {"claim": "supplier is unreliable"})
    goal = "assess supplier risk"

    plans = [
        Plan(
            name="good",
            actions=[
                Action(name="fetch_supplier_risk", description="", action_type="tool", payload={"tool": "supplier_risk_api", "arguments": {}}),
                Action(name="request_review", description="", action_type="workflow", payload={}),
            ],
            reason="",
        ),
        Plan(
            name="weak",
            actions=[Action(name="monitor", description="", action_type="workflow", payload={})],
            reason="",
        ),
    ]

    result1 = agent.run(state, goal, plans)
    result2 = agent.run(state, goal, plans)

    return {
        "first_run": {
            "plan": result1.selected_plan,
            "success": result1.execution_success,
            "rules": result1.rule_count,
        },
        "second_run": {
            "plan": result2.selected_plan,
            "success": result2.execution_success,
            "rules": result2.rule_count,
        },
    }
