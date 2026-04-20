from __future__ import annotations

from typing import Any, Dict

from sce.core.llm_planner import LLMPlanner
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


def test_llm_planner_builds_plan_from_json_steps():
    planner = LLMPlanner(FakeLLM())
    state = State("planning_context", {"entity": "supplier A", "claim": "supplier may be unreliable"})

    plan = planner.plan(state, goal="assess supplier risk")

    assert plan.name == "llm_generated_plan"
    assert len(plan.actions) == 2
    assert plan.actions[0].name == "fetch_supplier_risk"
    assert plan.actions[0].payload["tool"] == "supplier_risk_api"
    assert plan.actions[1].name == "request_review"
    assert plan.actions[1].action_type == "workflow"
