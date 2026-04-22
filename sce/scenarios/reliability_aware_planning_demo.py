from __future__ import annotations

from sce.core.episode_memory import EpisodeMemory
from sce.core.planning import MemoryAwarePlanner, ReliabilityAwarePlanner, ToolPlanner
from sce.core.types import State


def run_reliability_aware_planning_demo() -> dict:
    """Show remembered trajectory reliability changing plan ranking."""

    state = State("supplier_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"
    base_planner = ToolPlanner()
    memory = EpisodeMemory()
    memory_planner = MemoryAwarePlanner(base_planner, memory)
    candidates = base_planner.candidates(state, goal)

    memory_scores = [
        {
            "plan_name": score.plan.name,
            "base_score": score.base_score,
            "memory_bias": score.memory_bias,
            "total_score": score.total_score,
        }
        for score in memory_planner.score(candidates, state, goal)
    ]

    for plan in candidates:
        remembered_reliability = {
            "supplier_risk_plan": 0.1,
            "escalation_plan": 0.95,
            "monitor_plan": 0.2,
        }[plan.name]
        memory.remember(
            state,
            goal,
            plan,
            success=True,
            reward=0.0,
            reason="controlled_evolution_report",
            reliability=remembered_reliability,
        )

    reliability_planner = ReliabilityAwarePlanner(
        memory_planner,
        reliability_weight=1.0,
    )
    reliability_scores = [
        {
            "plan_name": score.plan.name,
            "base_score": score.base_score,
            "memory_bias": score.memory_bias,
            "reliability": score.reliability,
            "reliability_bonus": score.reliability_bonus,
            "total_score": score.total_score,
        }
        for score in reliability_planner.score(candidates, state, goal)
    ]

    selected_without_reliability = memory_planner.plan(state, goal, candidates).name
    selected_with_reliability = reliability_planner.plan(state, goal, candidates).name

    return {
        "goal": goal,
        "state": state.data,
        "remembered_reliability_count": len(memory.episodes),
        "selected_without_reliability": selected_without_reliability,
        "selected_with_reliability": selected_with_reliability,
        "changed_choice": selected_without_reliability != selected_with_reliability,
        "memory_scores": memory_scores,
        "reliability_scores": reliability_scores,
        "explanation": (
            "Reliability-aware planning reads trajectory reliability from episodic memory and adds it to "
            "base score and memory bias. A lower-base plan can become preferable when its remembered "
            "trajectory is more reliable."
        ),
    }


def _format_memory_scores(scores: list[dict]) -> str:
    lines = ["plan                         base    memory   total", "------------------------------------------------------"]
    for item in scores:
        lines.append(
            f"{item['plan_name']:<28} "
            f"{item['base_score']:>5.2f}   "
            f"{item['memory_bias']:>6.2f}   "
            f"{item['total_score']:>5.2f}"
        )
    return "\n".join(lines)


def _format_reliability_scores(scores: list[dict]) -> str:
    lines = [
        "plan                         base    memory   rel   total",
        "----------------------------------------------------------",
    ]
    for item in scores:
        lines.append(
            f"{item['plan_name']:<28} "
            f"{item['base_score']:>5.2f}   "
            f"{item['memory_bias']:>6.2f}   "
            f"{item['reliability']:>4.2f}   "
            f"{item['total_score']:>5.2f}"
        )
    return "\n".join(lines)


def format_reliability_aware_planning_demo(result: dict) -> str:
    changed = "YES" if result["changed_choice"] else "NO"
    return "\n".join(
        [
            "SCE Reliability-Aware Planning Demo",
            "===================================",
            "",
            f"Goal:  {result['goal']}",
            f"State: {result['state']}",
            "",
            "1) Without trajectory reliability",
            "---------------------------------",
            _format_memory_scores(result["memory_scores"]),
            "",
            f"Selected plan: {result['selected_without_reliability']}",
            "",
            "2) Remembered reliability",
            "-------------------------",
            f"Stored reliability episodes: {result['remembered_reliability_count']}",
            "",
            "3) With trajectory reliability from memory",
            "-----------------------------------------",
            _format_reliability_scores(result["reliability_scores"]),
            "",
            f"Selected plan: {result['selected_with_reliability']}",
            f"Changed choice: {changed}",
            "",
            "Interpretation",
            "--------------",
            result["explanation"],
        ]
    )
