from sce.core.episode_memory import Episode
from sce.core.memory_repository import InMemoryEpisodeRepository


def test_repository_saves_and_lists_episodes():
    repository = InMemoryEpisodeRepository()
    episode = Episode(
        state_snapshot={"entity": "supplier A"},
        goal="observe",
        plan_name="p1",
        action_names=["monitor"],
        success=True,
        reward=1.0,
    )

    repository.save_episode(episode)

    episodes = repository.list_episodes()
    assert episodes == [episode]


def test_repository_list_episodes_honors_limit():
    repository = InMemoryEpisodeRepository()
    episodes = [
        Episode(
            state_snapshot={"idx": str(idx)},
            goal="observe",
            plan_name=f"p{idx}",
            action_names=["monitor"],
            success=True,
            reward=1.0,
        )
        for idx in range(3)
    ]

    for episode in episodes:
        repository.save_episode(episode)

    assert repository.list_episodes(limit=2) == episodes[:2]


def test_repository_clear_removes_all_episodes():
    repository = InMemoryEpisodeRepository()
    repository.save_episode(
        Episode(
            state_snapshot={"entity": "supplier A"},
            goal="observe",
            plan_name="p1",
            action_names=["monitor"],
            success=True,
            reward=1.0,
        )
    )

    repository.clear()

    assert repository.list_episodes() == []


def test_repository_list_episodes_returns_detached_copies():
    repository = InMemoryEpisodeRepository()
    repository.save_episode(
        Episode(
            state_snapshot={"entity": "supplier A"},
            goal="observe",
            plan_name="p1",
            action_names=["monitor"],
            success=True,
            reward=1.0,
        )
    )

    listed_episode = repository.list_episodes()[0]
    listed_episode.action_names.append("escalate")
    listed_episode.state_snapshot["entity"] = "mutated"

    stored_episode = repository.list_episodes()[0]
    assert stored_episode.action_names == ["monitor"]
    assert stored_episode.state_snapshot["entity"] == "supplier A"
