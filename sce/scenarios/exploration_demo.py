from __future__ import annotations

import random

from sce.core.episode_memory import EpisodeMemory
from sce.core.planning import MemoryAwarePlanner, ToolPlanner
from sce.core.types import State


def run_exploration_demo() -> dict:
    """Demonstrate exploit vs explore behavior in memory-aware planning."""

    state = State("supplier_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"
    base_planner = ToolPlanner()
    candidates = base_planner.candidates(state, goal)

    exploit_planner = MemoryAwarePlanner(
        base_planner,
        EpisodeMemory(),
        exploration_rate=0.0,
        rng=random.Random(42),
    )
    explore_planner = MemoryAwarePlanner(
        base_planner,
        EpisodeMemory(),
        exploration_rate=1.0,
        rng=random.Random(42),
    )

    ranked_scores = [
        {
            "plan_name": score.plan.name,
            "base_score": score.base_score,
            "memory_bias": score.memory_bias,
            "total_score": score.total_score,
        }
        for score in exploit_planner.score(candidates, state, goal)
    ]

    exploit_choice = exploit_planner.plan(state, goal, candidates)
    explore_choice = explore_planner.plan(state, goal, candidates)

    return {
        "goal": goal,
        "state": state.data,
        "candidate_scores": ranked_scores,
        "exploit_choice": exploit_choice.name,
        "explore_choice": explore_choice.name,
        "exploration_rate_for_exploit": 0.0,
        "exploration_rate_for_explore": 1.0,
        "explored_non_top_plan": explore_choice.name != exploit_choice.name,
        "explanation": (
            "With exploration_rate=0.0, the planner exploits the current top-scoring plan. "
            "With exploration_rate=1.0, it deliberately tries a non-top candidate to gather experience."
        ),
    }


def format_exploration_demo(result: dict) -> str:
    lines = [
        "SCE Exploration Demo",
        "====================",
        "",
        f"Goal:  {result['goal']}",
        f"State: {result['state']}",
        "",
        "Candidate ranking",
        "-----------------",
        "plan                         base    memory   total",
        "------------------------------------------------------",
    ]
    for item in result["candidate_scores"]:
        lines.append(
            f"{item['plan_name']:<28} "
            f"{item['base_score']:>5.2f}   "
            f"{item['memory_bias']:>6.2f}   "
            f"{item['total_score']:>5.2f}"
        )

    lines.extend(
        [
            "",
            "Exploit mode",
            "------------",
            f"exploration_rate={result['exploration_rate_for_exploit']:.1f}",
            f"selected: {result['exploit_choice']}",
            "",
            "Explore mode",
            "------------",
            f"exploration_rate={result['exploration_rate_for_explore']:.1f}",
            f"selected: {result['explore_choice']}",
            f"explored non-top plan: {result['explored_non_top_plan']}",
            "",
            "Interpretation",
            "--------------",
            result["explanation"],
        ]
    )
    return "\n".join(lines)
