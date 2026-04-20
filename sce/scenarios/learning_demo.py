from __future__ import annotations

from typing import Any, Dict

from sce.core.learning import FeedbackSignal, StabilityWeightLearner
from sce.core.scoring import SCEScoringEngine
from sce.core.types import State
from sce.storage.memory import MemoryRepository


def run_learning_demo() -> Dict[str, Any]:
    repo = MemoryRepository()

    state = State(
        state_type="learning_state",
        data={"claim": "supplier is unreliable"},
    )
    repo.add_state(state)

    scorer = SCEScoringEngine(repo)
    scorer.compute_stability(state)

    learner = StabilityWeightLearner()

    before = learner.snapshot()

    feedback = FeedbackSignal(
        state_id=str(state.state_id),
        reward=1.0,
        reason="Correctly detected risk",
    )

    learner.update(state, feedback)

    after = learner.snapshot()

    return {
        "scenario": "learning",
        "before": before,
        "after": after,
        "reward": feedback.reward,
    }
