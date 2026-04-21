from __future__ import annotations

from sce.core.actions import Action
from sce.core.episode_memory import EpisodeMemory
from sce.core.memory_repository import InMemoryEpisodeRepository
from sce.core.planning import Plan
from sce.core.types import State


def run_memory_aware_planning_demo() -> dict:
    """Demonstrate how remembered outcomes bias future plan selection."""

    repository = InMemoryEpisodeRepository()
    memory = EpisodeMemory(repository=repository)

    state = State("supplier_context", {"entity": "supplier A", "risk": "high"})
    goal = "reduce supplier risk"

    slow_plan = Plan(
        name="slow_monitoring_plan",
        actions=[Action(name="monitor", description="Passive monitoring", action_type="internal", payload={})],
        reason="Low-effort monitoring path.",
    )
    escalation_plan = Plan(
        name="escalation_plan",
        actions=[Action(name="escalate", description="Escalate supplier risk", action_type="workflow", payload={})],
        reason="Escalate based on prior high-risk outcomes.",
    )

    memory.remember(state, goal, slow_plan, success=False, reward=-0.8, reason="monitoring did not reduce risk")
    memory.remember(state, goal, escalation_plan, success=True, reward=1.0, reason="escalation reduced risk")
    memory.remember(state, goal, escalation_plan, success=True, reward=0.8, reason="escalation produced faster response")

    candidates = [slow_plan, escalation_plan]
    scored = [
        {
            "plan_name": plan.name,
            "memory_bias": memory.plan_bias(plan, state, goal),
            "reason": plan.reason,
        }
        for plan in candidates
    ]
    selected = max(scored, key=lambda item: item["memory_bias"])

    return {
        "goal": goal,
        "state": state.data,
        "remembered_episode_count": len(repository.list_episodes()),
        "candidate_scores": scored,
        "selected_plan": selected["plan_name"],
        "explanation": "The selected plan has the strongest positive bias from similar remembered episodes.",
    }
