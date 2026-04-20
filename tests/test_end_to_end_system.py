from __future__ import annotations

from typing import Any, Dict

from sce.core.actions import ActionExecutor, ActionPolicy, monitor_handler, request_review_handler
from sce.core.agent_loop import SCEAgentLoop
from sce.core.goal_agent import GoalDrivenAgent
from sce.core.goals import Goal
from sce.core.learning import FeedbackSignal, StabilityWeightLearner
from sce.core.types import State
from sce.core.world import AgentSpec, MultiAgentWorld
from sce.storage.memory import MemoryRepository


class FakeLLM:
    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "candidates": [
                {"state_type": "agent_state", "data": {"claim": "supplier is unreliable"}},
                {"state_type": "agent_state", "data": {"claim": "supplier is reliable"}},
            ]
        }


def test_end_to_end_reasoning_action_learning_world_flow():
    repo = MemoryRepository()
    llm = FakeLLM()

    initial = State(
        "context",
        {"facts": ["supplier has late deliveries", "supplier has complaints"]},
    )

    loop = SCEAgentLoop(repo=repo, llm_client=llm, task="assess supplier risk")
    goal = Goal(
        name="detect_unreliable",
        score_fn=lambda state: 1.0 if "unreliable" in str(state.data.get("claim", "")).lower() else 0.0,
        threshold=1.0,
    )
    agent = GoalDrivenAgent(loop=loop, goal=goal)
    result = agent.run(initial, max_steps=2)

    assert result.reached is True
    assert result.final_claim == "supplier is unreliable"

    final_state = State("decision", {"claim": result.final_claim})
    policy = ActionPolicy()
    actions = policy.propose(final_state)

    executor = ActionExecutor()
    executor.register("request_review", request_review_handler)
    executor.register("monitor", monitor_handler)
    action_result = executor.execute(actions[0], final_state)

    assert action_result.success is True
    assert action_result.resulting_state.data["status"] == "review_requested"

    learner = StabilityWeightLearner(learning_rate=0.1)
    final_state.coherence = 0.4
    final_state.support = 0.7
    final_state.conflict = 0.2
    final_state.entropy = 0.1
    before = learner.snapshot()
    learner.update(final_state, FeedbackSignal(state_id=str(final_state.state_id), reward=1.0))
    after = learner.snapshot()

    assert after["support"] > before["support"]

    world = MultiAgentWorld(
        repo=MemoryRepository(),
        llm_client=llm,
        agents=[
            AgentSpec(
                name="RiskAgent",
                role="risk_detector",
                goal=goal,
                task="assess supplier risk",
            )
        ],
    )
    world_result = world.run(initial, ticks=1)

    assert world_result.ticks == 1
    assert len(world_result.steps) == 1
    assert len(world_result.final_world_state["events"]) == 1
