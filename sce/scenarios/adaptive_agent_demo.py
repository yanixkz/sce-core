from __future__ import annotations

from sce.core.actions import Action
from sce.core.episode_memory import EpisodeMemory
from sce.core.planning import LearningPlanExecutor, MemoryAwarePlanner, Plan, PlanExecutor, ToolPlanner
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def _score_summary(planner: MemoryAwarePlanner, plans: list[Plan], state: State, goal: str) -> list[dict]:
    return [
        {
            "plan_name": score.plan.name,
            "base_score": score.base_score,
            "memory_bias": score.memory_bias,
            "total_score": score.total_score,
        }
        for score in planner.score(plans, state, goal)
    ]


def run_adaptive_agent_demo() -> dict:
    """Show an agent changing plan choice after learning from execution outcomes."""

    memory = EpisodeMemory()
    base_planner = ToolPlanner()
    planner = MemoryAwarePlanner(base_planner, memory)

    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    executor = LearningPlanExecutor(PlanExecutor(ToolActionBridge(registry)), memory)

    state = State("supplier_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"
    candidates = base_planner.candidates(state, goal)

    first_scores = _score_summary(planner, candidates, state, goal)
    first_plan = planner.plan(state, goal, candidates)
    first_result = executor.execute(first_plan, state, goal)

    escalation_plan = next(plan for plan in candidates if plan.name == "escalation_plan")
    memory.remember(
        state,
        goal,
        escalation_plan,
        success=True,
        reward=1.5,
        reason="manual_review_confirmed_escalation_was_best",
    )

    second_scores = _score_summary(planner, candidates, state, goal)
    second_plan = planner.plan(state, goal, candidates)

    return {
        "goal": goal,
        "state": state.data,
        "first_choice": first_plan.name,
        "first_execution_success": first_result.success,
        "episodes_after_learning": len(memory.episodes),
        "second_choice": second_plan.name,
        "changed_choice": first_plan.name != second_plan.name,
        "before_learning_scores": first_scores,
        "after_learning_scores": second_scores,
        "explanation": (
            "The first choice follows base planning scores. After a successful escalation episode is remembered, "
            "memory bias changes the next plan selection."
        ),
    }
