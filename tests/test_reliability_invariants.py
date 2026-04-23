from __future__ import annotations

import pytest

from sce.core.actions import Action
from sce.core.episode_memory import EpisodeMemory
from sce.core.evolution_control import EvolutionErrorTracker
from sce.core.planning import (
    MemoryAwarePlanner,
    Plan,
    PlanExecutor,
    ReliabilityAwareLearningPlanExecutor,
    ToolPlanner,
)
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def test_reliability_decreases_when_cumulative_error_increases_and_stays_bounded():
    low_error = EvolutionErrorTracker()
    low_error.record_step("predict", predicted_value=0.8, actual_value=0.78)
    low_error.record_step("execute", predicted_value=0.7, actual_value=0.69)

    high_error = EvolutionErrorTracker()
    high_error.record_step("predict", predicted_value=0.8, actual_value=0.3)
    high_error.record_step("execute", predicted_value=0.7, actual_value=0.1)

    low_report = low_error.report()
    high_report = high_error.report()

    assert low_report.reliability > high_report.reliability
    assert 0.0 <= low_report.reliability <= 1.0
    assert 0.0 <= high_report.reliability <= 1.0


def test_reliability_report_is_persisted_in_episodic_memory_by_learning_executor():
    state = State("supplier_context", {"supplier_id": "supplier A"})
    goal = "assess supplier risk"
    plan = Plan(
        name="supplier_risk_plan",
        actions=[
            Action(
                name="fetch_supplier_risk",
                description="",
                action_type="tool",
                payload={"tool": "supplier_risk_api", "arguments": {"supplier_id": "supplier A"}},
            )
        ],
    )

    tracker = EvolutionErrorTracker()
    tracker.record_step("score", predicted_value=0.9, actual_value=0.85)
    report = tracker.report()

    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    executor = PlanExecutor(ToolActionBridge(registry))

    memory = EpisodeMemory()
    learning_executor = ReliabilityAwareLearningPlanExecutor(executor, memory)
    execution_result = learning_executor.execute(plan, state, goal, report=report)

    assert execution_result.success is True
    assert len(memory.episodes) == 1
    assert memory.episodes[0].reliability == pytest.approx(report.reliability)


def test_episodic_memory_changes_next_plan_ranking_and_selected_choice():
    state = State("supplier_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"
    base_planner = ToolPlanner()
    candidates = base_planner.candidates(state, goal)

    memory = EpisodeMemory()
    planner = MemoryAwarePlanner(base_planner, memory)

    before = planner.score(candidates, state, goal)
    assert before[0].plan.name == "supplier_risk_plan"

    escalation = next(plan for plan in candidates if plan.name == "escalation_plan")
    memory.remember(state, goal, escalation, success=True, reward=1.0)

    after = planner.score(candidates, state, goal)

    assert after[0].plan.name == "escalation_plan"
    assert after[0].memory_bias > before[0].memory_bias
