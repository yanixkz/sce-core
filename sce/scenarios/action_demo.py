from __future__ import annotations

from typing import Any, Dict

from sce.core.actions import ActionExecutor, ActionPolicy, monitor_handler, request_review_handler
from sce.core.goal_agent import GoalDrivenAgent
from sce.core.goals import Goal
from sce.core.agent_loop import SCEAgentLoop
from sce.core.types import State
from sce.scenarios.agent_demo import _build_client
from sce.storage.memory import MemoryRepository


def run_action_demo() -> Dict[str, Any]:
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

    loop = SCEAgentLoop(repo=repo, llm_client=_build_client(), task="Assess supplier risk")

    goal = Goal(
        name="detect_risk",
        score_fn=lambda s: 1.0 if "unreliable" in str(s.data.get("claim", "")).lower() else 0.0,
        threshold=1.0,
    )

    agent = GoalDrivenAgent(loop, goal)
    result = agent.run(initial, max_steps=3)

    executor = ActionExecutor()
    executor.register("request_review", request_review_handler)
    executor.register("monitor", monitor_handler)

    policy = ActionPolicy()

    final_state = State("final", {"claim": result.final_claim})
    actions = policy.propose(final_state)

    executed = [executor.execute(action, final_state) for action in actions]

    return {
        "scenario": "action_layer",
        "final_claim": result.final_claim,
        "actions": [
            {
                "name": a.name,
                "description": a.description,
            }
            for a in actions
        ],
        "results": [
            {
                "success": r.success,
                "message": r.message,
                "state": r.resulting_state.data,
            }
            for r in executed
        ],
    }
