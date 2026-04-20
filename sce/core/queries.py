from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from sce.core.types import Attractor, Constraint, Link, State
from sce.storage.memory import MemoryRepository


@dataclass(frozen=True)
class PathResult:
    """A path through the state graph plus a simple stability score."""

    state_ids: List[UUID]
    stability_score: float


class GraphQueryLayer:
    """Structural queries over the SCE state graph.

    Phase 1 implementation targets MemoryRepository and keeps the algorithms
    deterministic and dependency-free.
    """

    def __init__(self, repo: MemoryRepository) -> None:
        self.repo = repo

    def top_stable(self, k: int = 5) -> List[State]:
        """Return the k most stable states."""

        if k <= 0:
            return []
        return sorted(self.repo.states.values(), key=lambda state: state.stability, reverse=True)[:k]

    def fragile(self, new_constraint: Constraint) -> List[State]:
        """Return states that would become invalid under a new constraint."""

        return [
            state
            for state in self.repo.states.values()
            if new_constraint.applies_to(state) and not new_constraint.is_satisfied(state)
        ]

    def nearest_attractor(self, state_id: UUID) -> Optional[Attractor]:
        """Return the closest attractor by unweighted graph distance.

        Distance is computed through state links. If multiple attractors are at
        the same distance, the one with higher stability score is preferred.
        """

        if state_id not in self.repo.states:
            raise KeyError(state_id)
        if not self.repo.attractors:
            return None

        distances = self._bfs_distances(state_id)
        candidates: List[tuple[int, float, Attractor]] = []
        for attractor in self.repo.attractors.values():
            member_distances = [distances[mid] for mid in attractor.member_state_ids if mid in distances]
            if member_distances:
                candidates.append((min(member_distances), -attractor.stability_score, attractor))

        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2]

    def path_to(self, source_id: UUID, target_id: UUID) -> Optional[PathResult]:
        """Find a path from source to target with the best average stability.

        Phase 1 enumerates simple paths with BFS and keeps the best-scoring path.
        This is intentionally simple and suitable for small graphs/demos.
        """

        if source_id not in self.repo.states:
            raise KeyError(source_id)
        if target_id not in self.repo.states:
            raise KeyError(target_id)
        if source_id == target_id:
            state = self.repo.get_state(source_id)
            return PathResult([source_id], state.stability)

        queue = deque([[source_id]])
        best: Optional[PathResult] = None
        max_paths = max(1, len(self.repo.states) * len(self.repo.states))
        explored_paths = 0

        while queue and explored_paths < max_paths:
            path = queue.popleft()
            explored_paths += 1
            current = path[-1]

            for neighbor in self._neighbor_ids(current):
                if neighbor in path:
                    continue
                next_path = [*path, neighbor]
                if neighbor == target_id:
                    result = self._score_path(next_path)
                    if best is None or result.stability_score > best.stability_score:
                        best = result
                else:
                    queue.append(next_path)

        return best

    def _score_path(self, state_ids: List[UUID]) -> PathResult:
        states = [self.repo.get_state(state_id) for state_id in state_ids]
        avg_stability = sum(state.stability for state in states) / len(states)
        return PathResult(state_ids=state_ids, stability_score=avg_stability)

    def _neighbor_ids(self, state_id: UUID) -> List[UUID]:
        ids = set()
        for link in self.repo.links.values():
            if link.source_state_id == state_id:
                ids.add(link.target_state_id)
            if link.target_state_id == state_id:
                ids.add(link.source_state_id)
        return list(ids)

    def _bfs_distances(self, source_id: UUID) -> dict[UUID, int]:
        distances = {source_id: 0}
        queue = deque([source_id])

        while queue:
            current = queue.popleft()
            for neighbor in self._neighbor_ids(current):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)

        return distances
