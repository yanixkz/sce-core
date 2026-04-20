from __future__ import annotations

from typing import Any, Dict

from sce.core.goals import Goal
from sce.core.types import State
from sce.core.world import AgentSpec, MultiAgentWorld
from sce.scenarios.agent_demo import _build_client
from sce.storage.memory import MemoryRepository


def run_multi_agent_demo() -> Dict[str, Any]:
    repo = MemoryRepository()

    initial = State(
        state_type="world_init",
        data={
            "facts": [
                "supplier A has late deliveries",
                "supplier A has complaints",
                "supplier A had some good history",
            ]
        },
    )

    def risk_goal(state: State) -> float:
        claim = str(state.data.get("claim", "")).lower()
        return 1.0 if "risk" in claim or "unreliable" in claim else 0.0

    def stability_goal(state: State) -> float:
        claim = str(state.data.get("claim", "")).lower()
        return 1.0 if "reliable" in claim else 0.0

    agents = [
        AgentSpec(
            name="RiskAgent",
            role="risk_detector",
            goal=Goal(name="detect_risk", score_fn=risk_goal, threshold=1.0),
            task="Assess risk of supplier",
        ),
        AgentSpec(
            name="StabilityAgent",
            role="stability_checker",
            goal=Goal(name="detect_stability", score_fn=stability_goal, threshold=1.0),
            task="Assess stability of supplier",
        ),
    ]

    world = MultiAgentWorld(
        repo=repo,
        llm_client=_build_client(),
        agents=agents,
    )

    result = world.run(initial, ticks=2)

    return {
        "scenario": "multi_agent",
        "ticks": result.ticks,
        "steps": [
            {
                "tick": s.tick,
                "agent": s.agent_name,
                "claim": s.selected_claim,
                "action": s.action,
            }
            for s in result.steps
        ],
        "final_world": result.final_world_state,
    }
