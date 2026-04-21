from sce.core.actions import Action
from sce.core.episode_memory import EpisodeMemory
from sce.core.planning import Plan
from sce.core.types import State


def test_memory_stores_and_returns_similar():
    memory = EpisodeMemory()

    state = State("context", {"entity": "supplier A"})
    plan = Plan(
        name="p1",
        actions=[Action(name="monitor", description="", action_type="workflow", payload={})],
        reason="",
    )

    memory.remember(state, "observe", plan, True, 1.0)

    results = memory.similar(state, "observe")
    assert len(results) >= 1


def test_memory_bias_positive_for_successful_plan():
    memory = EpisodeMemory()

    state = State("context", {"entity": "supplier A"})
    plan = Plan(
        name="p1",
        actions=[Action(name="monitor", description="", action_type="workflow", payload={})],
        reason="",
    )

    memory.remember(state, "observe", plan, True, 1.0)

    bias = memory.plan_bias(plan, state, "observe")
    assert bias > 0
