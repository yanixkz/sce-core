from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from sce.core.actions import Action, ActionExecutor, ActionResult, monitor_handler, request_review_handler
from sce.core.agent_loop import SCEAgentLoop
from sce.core.goal_agent import GoalDrivenAgent
from sce.core.goals import Goal
from sce.core.types import State
from sce.storage.memory import MemoryRepository


@dataclass
class AgentSpec:
    """Configuration for one agent in a shared SCE world."""

    name: str
    role: str
    goal: Goal
    task: str


@dataclass
class AgentWorldStep:
    tick: int
    agent_name: str
    selected_claim: Any
    goal_reached: bool
    action: str
    action_success: bool


@dataclass
class AgentWorldResult:
    ticks: int
    steps: List[AgentWorldStep] = field(default_factory=list)
    final_world_state: Dict[str, Any] = field(default_factory=dict)


class MultiAgentWorld:
    """Minimal multi-agent environment for SCE agents.

    Agents share a repository and a world state. Each agent evaluates the world,
    selects a state through SCE, checks its goal, proposes an action, and the
    action updates the world state.
    """

    def __init__(self, repo: MemoryRepository, llm_client: Any, agents: List[AgentSpec]) -> None:
        self.repo = repo
        self.llm_client = llm_client
        self.agents = agents
        self.world_state: Dict[str, Any] = {"events": []}
        self.executor = ActionExecutor()
        self.executor.register("request_review", request_review_handler)
        self.executor.register("monitor", monitor_handler)

    def run(self, initial_state: State, ticks: int = 2) -> AgentWorldResult:
        result = AgentWorldResult(ticks=ticks)
        current_world_state = initial_state

        for tick in range(1, ticks + 1):
            for agent in self.agents:
                loop = SCEAgentLoop(
                    repo=self.repo,
                    llm_client=self.llm_client,
                    task=agent.task,
                )
                goal_agent = GoalDrivenAgent(loop=loop, goal=agent.goal)
                goal_result = goal_agent.run(current_world_state, max_steps=1)

                selected_state = State(
                    state_type="agent_decision",
                    data={
                        "agent": agent.name,
                        "role": agent.role,
                        "claim": goal_result.final_claim,
                    },
                )
                self.repo.add_state(selected_state)

                action = self._action_for(agent, selected_state, goal_result.reached)
                action_result = self.executor.execute(action, selected_state)
                self.repo.add_state(action_result.resulting_state)

                self.world_state["events"].append(
                    {
                        "tick": tick,
                        "agent": agent.name,
                        "claim": goal_result.final_claim,
                        "action": action.name,
                        "success": action_result.success,
                    }
                )

                result.steps.append(
                    AgentWorldStep(
                        tick=tick,
                        agent_name=agent.name,
                        selected_claim=goal_result.final_claim,
                        goal_reached=goal_result.reached,
                        action=action.name,
                        action_success=action_result.success,
                    )
                )

                current_world_state = State(
                    state_type="world_state",
                    data={
                        "facts": [
                            f"{event['agent']} selected {event['claim']} and executed {event['action']}"
                            for event in self.world_state["events"]
                        ]
                    },
                )

        result.final_world_state = self.world_state
        return result

    def _action_for(self, agent: AgentSpec, state: State, goal_reached: bool) -> Action:
        claim = str(state.data.get("claim", "")).lower()
        if goal_reached or "risk" in claim or "unreliable" in claim:
            return Action(
                name="request_review",
                description=f"{agent.name} requests review based on its selected state.",
                action_type="workflow",
                payload={"agent": agent.name, "claim": claim},
            )
        return Action(
            name="monitor",
            description=f"{agent.name} continues monitoring.",
            action_type="workflow",
            payload={"agent": agent.name, "claim": claim},
        )
