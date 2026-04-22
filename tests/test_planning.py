from __future__ import annotations

import random

import pytest

from sce.core.actions import Action
from sce.core.episode_memory import EpisodeMemory
from sce.core.planning import MemoryAwarePlanner, Plan, PlanExecutor, ReliabilityAwarePlanner, ToolPlanner
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


def test_tool_planner_returns_multiple_supplier_candidates():
    planner = ToolPlanner()
    state = State(
        state_type="planning_context",
        data={"entity": "supplier A", "claim": "supplier A may be high risk"},
    )

    candidates = planner.candidates(state, goal="assess supplier risk")

    assert [plan.name for plan in candidates] == [
        "supplier_risk_plan",
        "escalation_plan",
        "monitor_plan",
    ]


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


def test_memory_aware_planner_scores_base_plus_memory_bias():
    memory = EpisodeMemory()
    planner = MemoryAwarePlanner(ToolPlanner(), memory)
    state = State("planning_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"

    low_base_plan = Plan(
        name="escalation_plan",
        actions=[Action(name="escalate", description="", action_type="workflow", payload={})],
        meta={"base_score": 0.1},
    )
    high_base_plan = Plan(
        name="supplier_risk_plan",
        actions=[Action(name="fetch_supplier_risk", description="", action_type="tool", payload={})],
        meta={"base_score": 0.6},
    )

    memory.remember(state, goal, low_base_plan, success=True, reward=1.0)

    scores = planner.score([high_base_plan, low_base_plan], state, goal)

    assert scores[0].plan.name == "escalation_plan"
    assert scores[0].base_score == 0.1
    assert scores[0].memory_bias > 0
    assert scores[0].total_score > scores[1].total_score


def test_memory_aware_planner_selects_best_memory_weighted_plan():
    memory = EpisodeMemory()
    planner = MemoryAwarePlanner(ToolPlanner(), memory)
    state = State("planning_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"

    escalation_plan = Plan(
        name="escalation_plan",
        actions=[Action(name="escalate", description="", action_type="workflow", payload={})],
        meta={"base_score": 0.2},
    )
    supplier_plan = Plan(
        name="supplier_risk_plan",
        actions=[Action(name="fetch_supplier_risk", description="", action_type="tool", payload={})],
        meta={"base_score": 0.6},
    )

    memory.remember(state, goal, escalation_plan, success=True, reward=1.0)
    selected = planner.plan(state, goal, candidates=[supplier_plan, escalation_plan])

    assert selected.name == "escalation_plan"


def test_memory_aware_planner_can_explore_non_top_plan():
    memory = EpisodeMemory()
    planner = MemoryAwarePlanner(
        ToolPlanner(),
        memory,
        exploration_rate=1.0,
        rng=random.Random(0),
    )
    state = State("planning_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"
    candidates = ToolPlanner().candidates(state, goal)

    selected = planner.plan(state, goal, candidates=candidates)

    assert selected.name != "supplier_risk_plan"


def test_memory_aware_planner_rejects_invalid_exploration_rate():
    with pytest.raises(ValueError, match="exploration_rate"):
        MemoryAwarePlanner(ToolPlanner(), EpisodeMemory(), exploration_rate=1.5)


def test_reliability_aware_planner_can_rerank_by_reliability():
    state = State("planning_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"
    memory_planner = MemoryAwarePlanner(ToolPlanner(), EpisodeMemory())
    planner = ReliabilityAwarePlanner(
        memory_planner,
        reliability_by_plan={
            "supplier_risk_plan": 0.1,
            "escalation_plan": 0.95,
        },
        reliability_weight=1.0,
    )
    candidates = ToolPlanner().candidates(state, goal)

    selected = planner.plan(state, goal, candidates)
    scores = planner.score(candidates, state, goal)

    assert selected.name == "escalation_plan"
    assert scores[0].plan.name == "escalation_plan"
    assert scores[0].reliability_bonus == pytest.approx(0.95)


def test_reliability_aware_planner_rejects_negative_weight():
    with pytest.raises(ValueError, match="reliability_weight"):
        ReliabilityAwarePlanner(MemoryAwarePlanner(ToolPlanner(), EpisodeMemory()), reliability_weight=-1.0)


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
