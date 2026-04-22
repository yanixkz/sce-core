from datetime import datetime, timezone
from uuid import uuid4

from sce.core.actions import Action
from sce.core.episode_memory import Episode, EpisodeMemory
from sce.core.memory_repository import InMemoryEpisodeRepository
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
    assert len(memory.episodes) == 1


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


def test_memory_with_repository_persists_recorded_episodes():
    repository = InMemoryEpisodeRepository()
    memory = EpisodeMemory(repository=repository)

    state = State("context", {"entity": "supplier A"})
    plan = Plan(
        name="p1",
        actions=[Action(name="monitor", description="", action_type="workflow", payload={})],
        reason="",
    )

    remembered = memory.remember(state, "observe", plan, True, 1.0)

    stored = repository.list_episodes()
    assert len(stored) == 1
    assert stored[0] == remembered


def test_memory_records_and_returns_plan_reliability():
    memory = EpisodeMemory()
    state = State("context", {"entity": "supplier A"})
    plan = Plan(
        name="p1",
        actions=[Action(name="monitor", description="", action_type="workflow", payload={})],
        reason="",
    )

    memory.remember(state, "observe", plan, True, 0.0, reliability=0.8)
    memory.remember(state, "observe", plan, True, 0.0, reliability=0.6)

    assert memory.plan_reliability(plan, state, "observe") == 0.7


def test_memory_clamps_recorded_reliability():
    memory = EpisodeMemory()
    state = State("context", {"entity": "supplier A"})
    plan = Plan(
        name="p1",
        actions=[Action(name="monitor", description="", action_type="workflow", payload={})],
        reason="",
    )

    episode = memory.remember(state, "observe", plan, True, 0.0, reliability=2.0)

    assert episode.reliability == 1.0


def test_episode_roundtrip_serialization():
    episode = Episode(
        state_snapshot={"entity": "supplier A"},
        goal="observe",
        plan_name="p1",
        action_names=["monitor"],
        success=True,
        reward=1.0,
        reason="ok",
        reliability=0.9,
        episode_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )

    assert Episode.from_dict(episode.to_dict()) == episode


def test_episode_to_dict_serializes_episode_id_as_string():
    episode = Episode(
        state_snapshot={"entity": "supplier A"},
        goal="observe",
        plan_name="p1",
        action_names=["monitor"],
        success=True,
        reward=1.0,
    )

    assert isinstance(episode.to_dict()["episode_id"], str)


def test_episode_to_dict_serializes_created_at_as_string():
    episode = Episode(
        state_snapshot={"entity": "supplier A"},
        goal="observe",
        plan_name="p1",
        action_names=["monitor"],
        success=True,
        reward=1.0,
    )

    assert isinstance(episode.to_dict()["created_at"], str)


def test_episode_to_dict_serializes_reliability():
    episode = Episode(
        state_snapshot={"entity": "supplier A"},
        goal="observe",
        plan_name="p1",
        action_names=["monitor"],
        success=True,
        reward=1.0,
        reliability=0.75,
    )

    assert episode.to_dict()["reliability"] == 0.75
