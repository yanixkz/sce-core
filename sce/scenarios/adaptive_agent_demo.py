from __future__ import annotations

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


def _score_by_plan(scores: list[dict]) -> dict[str, dict]:
    return {item["plan_name"]: item for item in scores}


def _format_score_table(scores: list[dict]) -> str:
    lines = ["plan                         base    memory   total", "------------------------------------------------------"]
    for item in scores:
        lines.append(
            f"{item['plan_name']:<28} "
            f"{item['base_score']:>5.2f}   "
            f"{item['memory_bias']:>6.2f}   "
            f"{item['total_score']:>5.2f}"
        )
    return "\n".join(lines)


def _format_decision_change(result: dict) -> str:
    before = _score_by_plan(result["before_learning_scores"])
    after = _score_by_plan(result["after_learning_scores"])
    selected = result["second_choice"]
    previous = result["first_choice"]

    selected_before = before[selected]
    selected_after = after[selected]
    previous_after = after[previous]

    memory_delta = selected_after["memory_bias"] - selected_before["memory_bias"]
    margin = selected_after["total_score"] - previous_after["total_score"]

    return "\n".join(
        [
            f"{selected} received a memory boost of +{memory_delta:.2f}.",
            f"After learning, {selected} beats {previous} by {margin:.2f} total score.",
            "The decision changed because remembered outcomes shifted the ranking, not because the base rules changed.",
        ]
    )


def format_adaptive_agent_demo(result: dict) -> str:
    """Render the adaptive agent demo as a readable terminal story."""

    changed = "YES" if result["changed_choice"] else "NO"
    return "\n".join(
        [
            "SCE Adaptive Agent Demo",
            "=======================",
            "",
            f"Goal:  {result['goal']}",
            f"State: {result['state']}",
            "",
            "1) Before learning",
            "------------------",
            _format_score_table(result["before_learning_scores"]),
            "",
            f"Selected plan: {result['first_choice']}",
            f"Execution success: {result['first_execution_success']}",
            "",
            "2) Execution trace",
            "------------------",
            *[f"- {step}" for step in result["execution_trace"]],
            "",
            "3) Learning event",
            "-----------------",
            "A successful escalation episode is stored in episodic memory.",
            f"Episodes in memory: {result['episodes_after_learning']}",
            "",
            "4) After learning",
            "-----------------",
            _format_score_table(result["after_learning_scores"]),
            "",
            f"Selected plan: {result['second_choice']}",
            f"Changed choice: {changed}",
            "",
            "Why the decision changed",
            "------------------------",
            _format_decision_change(result),
            "",
            "Interpretation",
            "--------------",
            result["explanation"],
        ]
    )


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

    execution_trace = [
        f"Generated {len(candidates)} candidate plans.",
        f"Selected {first_plan.name} using base scores and current memory.",
        f"Executed {first_plan.name}; success={first_result.success}.",
        "Stored the execution result as an episode.",
        "Stored an additional successful escalation episode.",
        f"Re-scored candidates and selected {second_plan.name}.",
    ]

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
        "execution_trace": execution_trace,
        "explanation": (
            "The first choice follows base planning scores. After a successful escalation episode is remembered, "
            "memory bias changes the next plan selection."
        ),
    }
