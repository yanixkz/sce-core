from __future__ import annotations

from typing import Any, Dict

from sce.core.agent_loop import SCEAgentLoop
from sce.core.goal_agent import GoalDrivenAgent
from sce.core.goals import Goal
from sce.core.types import State
from sce.storage.memory import MemoryRepository


class FakeLLM:
    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "candidates": [
                {"state_type": "agent_state", "data": {"claim": "supplier is unreliable"}},
                {"state_type": "agent_state", "data": {"claim": "supplier is reliable"}},
            ]
        }


def test_goal_driven_agent_reaches_goal():
    repo = MemoryRepository()
    loop = SCEAgentLoop(repo=repo, llm_client=FakeLLM(), task="detect supplier risk")
    goal = Goal(
        name="detect_unreliable",
        score_fn=lambda state: 1.0 if "unreliable" in str(state.data.get("claim", "")).lower() else 0.0,
        threshold=1.0,
    )
    agent = GoalDrivenAgent(loop=loop, goal=goal)

    initial = State("context", {"facts": ["supplier has late deliveries", "supplier has complaints"]})
    result = agent.run(initial, max_steps=2)

    assert result.reached is True
    assert result.final_claim == "supplier is unreliable"
    assert result.steps[0].goal_score == 1.0
