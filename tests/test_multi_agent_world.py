from __future__ import annotations

from typing import Any, Dict

from sce.core.goals import Goal
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


def test_multi_agent_world_runs_ticks_and_records_events():
    repo = MemoryRepository()
    initial = State("world_init", {"facts": ["supplier has late deliveries", "supplier has complaints"]})

    agents = [
        AgentSpec(
            name="RiskAgent",
            role="risk_detector",
            goal=Goal(
                name="detect_risk",
                score_fn=lambda state: 1.0 if "unreliable" in str(state.data.get("claim", "")).lower() else 0.0,
                threshold=1.0,
            ),
            task="Assess supplier risk",
        ),
        AgentSpec(
            name="StabilityAgent",
            role="stability_checker",
            goal=Goal(
                name="detect_reliable",
                score_fn=lambda state: 1.0 if "reliable" in str(state.data.get("claim", "")).lower() else 0.0,
                threshold=1.0,
            ),
            task="Assess supplier reliability",
        ),
    ]

    world = MultiAgentWorld(repo=repo, llm_client=FakeLLM(), agents=agents)
    result = world.run(initial, ticks=2)

    assert result.ticks == 2
    assert len(result.steps) == 4
    assert len(result.final_world_state["events"]) == 4
    assert {step.agent_name for step in result.steps} == {"RiskAgent", "StabilityAgent"}
    assert all(step.action in {"request_review", "monitor"} for step in result.steps)
