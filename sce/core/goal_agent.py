from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from sce.core.agent_loop import SCEAgentLoop
from sce.core.goals import Goal
from sce.core.types import State


@dataclass(frozen=True)
class GoalStep:
    step: int
    claim: Any
    goal_score: float


@dataclass(frozen=True)
class GoalResult:
    reached: bool
    final_claim: Any
    steps: List[GoalStep]


class GoalDrivenAgent:
    """Wraps SCEAgentLoop with a goal and stopping condition."""

    def __init__(self, loop: SCEAgentLoop, goal: Goal) -> None:
        self.loop = loop
        self.goal = goal

    def run(self, initial_state: State, max_steps: int = 5) -> GoalResult:
        result = self.loop.run(initial_state, steps=max_steps)

        steps: List[GoalStep] = []
        reached = False

        for idx, step in enumerate(result.steps, start=1):
            # reconstruct state-like structure
            claim = step.selected_claim
            fake_state = State("goal_eval", {"claim": claim})
            score = self.goal.score(fake_state)

            steps.append(GoalStep(step=idx, claim=claim, goal_score=score))

            if score >= self.goal.threshold:
                reached = True
                return GoalResult(reached=True, final_claim=claim, steps=steps)

        return GoalResult(
            reached=reached,
            final_claim=result.final_claim,
            steps=steps,
        )
