from __future__ import annotations

import copy
from typing import List, Protocol

from sce.core.episode_memory import Episode


class EpisodeRepository(Protocol):
    """Persistence interface for episodic memory records."""

    def save_episode(self, episode: Episode) -> None:
        ...

    def list_episodes(self, limit: int | None = None) -> List[Episode]:
        ...

    def clear(self) -> None:
        ...


class InMemoryEpisodeRepository:
    """Simple in-process episode repository for tests and local runs."""

    def __init__(self) -> None:
        self._episodes: List[Episode] = []

    def save_episode(self, episode: Episode) -> None:
        self._episodes.append(copy.deepcopy(episode))

    def list_episodes(self, limit: int | None = None) -> List[Episode]:
        episodes = self._episodes if limit is None else self._episodes[:limit]
        return [copy.deepcopy(episode) for episode in episodes]

    def clear(self) -> None:
        self._episodes.clear()
