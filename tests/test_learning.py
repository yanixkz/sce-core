from __future__ import annotations

from sce.core.learning import FeedbackSignal, StabilityWeightLearner
from sce.core.types import State


def test_stability_weight_learner_positive_feedback_updates_weights():
    state = State("decision", {"claim": "supplier is unreliable"})
    state.coherence = 0.4
    state.conflict = 0.2
    state.entropy = 0.1
    state.support = 0.8
    state.energy = 0.3

    learner = StabilityWeightLearner(learning_rate=0.1)
    before = learner.snapshot()

    learner.update(state, FeedbackSignal(state_id=str(state.state_id), reward=1.0, reason="good decision"))
    after = learner.snapshot()

    assert after["coherence"] > before["coherence"]
    assert after["support"] > before["support"]
    assert after["conflict"] < before["conflict"]
    assert after["entropy"] < before["entropy"]
    assert len(learner.history) == 1


def test_stability_weight_learner_clamps_reward():
    state = State("decision", {"claim": "supplier is unreliable"})
    state.support = 1.0

    learner = StabilityWeightLearner(learning_rate=0.1)
    learner.update(state, FeedbackSignal(state_id=str(state.state_id), reward=10.0))

    assert learner.history[0].reward == 1.0
