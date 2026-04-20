from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from sce.core.types import ScoringWeights, State


@dataclass(frozen=True)
class FeedbackSignal:
    """Feedback for one selected state.

    reward is expected in [-1, 1]. Positive reward reinforces the factors that
    contributed to selection. Negative reward weakens them.
    """

    state_id: str
    reward: float
    reason: str = ""


@dataclass(frozen=True)
class LearningStep:
    old_weights: ScoringWeights
    new_weights: ScoringWeights
    reward: float
    reason: str = ""


class StabilityWeightLearner:
    """Small online learner for SCE stability weights.

    This is intentionally simple: it updates scoring weights based on whether a
    selected state received positive or negative feedback.
    """

    def __init__(self, weights: ScoringWeights | None = None, learning_rate: float = 0.05) -> None:
        self.weights = weights or ScoringWeights()
        self.learning_rate = learning_rate
        self.history: List[LearningStep] = []

    def update(self, selected_state: State, feedback: FeedbackSignal) -> ScoringWeights:
        reward = max(-1.0, min(1.0, feedback.reward))
        old = self.weights
        lr = self.learning_rate

        new = ScoringWeights(
            coherence=max(0.0, old.coherence + lr * reward * selected_state.coherence),
            cost=max(0.0, old.cost - lr * reward * selected_state.energy),
            conflict=max(0.0, old.conflict - lr * reward * selected_state.conflict),
            entropy=max(0.0, old.entropy - lr * reward * selected_state.entropy),
            support=max(0.0, old.support + lr * reward * selected_state.support),
        )

        self.weights = new
        self.history.append(
            LearningStep(
                old_weights=old,
                new_weights=new,
                reward=reward,
                reason=feedback.reason,
            )
        )
        return new

    def snapshot(self) -> Dict[str, float]:
        return {
            "coherence": self.weights.coherence,
            "cost": self.weights.cost,
            "conflict": self.weights.conflict,
            "entropy": self.weights.entropy,
            "support": self.weights.support,
        }
