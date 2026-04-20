from __future__ import annotations

from sce.core.planning import PlanExecutor, ToolPlanner
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def test_tool_planner_builds_supplier_risk_plan():
    planner = ToolPlanner()
    state = State(
        state_type="planning_context",
        data={"entity": "supplier A", "claim": "supplier A may be high risk"},
    )

    plan = planner.plan(state, goal="assess supplier risk")

    assert plan.name == "supplier_risk_plan"
    assert len(plan.actions) == 1
    assert plan.actions[0].name == "fetch_supplier_risk"
    assert plan.actions[0].payload["tool"] == "supplier_risk_api"


def test_tool_planner_falls_back_to_monitor_plan():
    planner = ToolPlanner()
    state = State(
        state_type="planning_context",
        data={"claim": "system is stable"},
    )

    plan = planner.plan(state, goal="observe current state")

    assert plan.name == "monitor_plan"
    assert len(plan.actions) == 1
    assert plan.actions[0].name == "monitor"


def test_plan_executor_runs_tool_plan_and_returns_tool_result_state():
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)
    executor = PlanExecutor(bridge)

    planner = ToolPlanner()
    state = State(
        state_type="planning_context",
        data={"entity": "supplier A", "claim": "supplier A may be high risk"},
    )
    plan = planner.plan(state, goal="assess supplier risk")

    result = executor.execute(plan, state)

    assert result.success is True
    assert result.final_state is not None
    assert result.final_state.data["tool"] == "supplier_risk_api"
    assert result.final_state.data["success"] is True
