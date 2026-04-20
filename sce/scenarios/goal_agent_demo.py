from __future__ import annotations

from typing import Any, Dict

from sce.core.agent_loop import SCEAgentLoop
from sce.core.goal_agent import GoalDrivenAgent
from sce.core.goals import Goal
from sce.core.types import State
from sce.scenarios.agent_demo import _build_client
from sce.storage.memory import MemoryRepository


def run_goal_agent_demo() -> Dict[str, Any]:
    repo = MemoryRepository()

    initial = State(
        state_type="agent_context",
        data={
            "entity": "supplier A",
            "facts": [
                "many deliveries were late",
                "there are complaints",
                "recent breach happened",
            ],
        },
    )

    loop = SCEAgentLoop(
        repo=repo,
        llm_client=_build_client(),
        task="Refine belief about supplier risk",
    )

    def goal_score(state: State) -> float:
        claim = str(state.data.get("claim", "")).lower()
        if "high risk" in claim or "unreliable" in claim:
            return 1.0
        return 0.0

    goal = Goal(name="detect_risk", score_fn=goal_score, threshold=1.0)

    agent = GoalDrivenAgent(loop, goal)
    result = agent.run(initial, max_steps=3)

    return {
        "scenario": "goal_agent",
        "goal": goal.name,
        "reached": result.reached,
        "final_claim": result.final_claim,
        "steps": [
            {"step": s.step, "claim": s.claim, "goal_score": s.goal_score}
            for s in result.steps
        ],
    }
