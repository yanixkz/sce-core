from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import UUID, uuid4

from sce.core.planning import Plan
from sce.core.types import State

if TYPE_CHECKING:
    from sce.core.memory_repository import EpisodeRepository


@dataclass(frozen=True)
class Episode:
    """One remembered decision episode."""

    state_snapshot: Dict[str, Any]
    goal: str
    plan_name: str
    action_names: List[str]
    success: bool
    reward: float
    reason: str = ""
    episode_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": str(self.episode_id),
            "created_at": self.created_at.isoformat(),
            "state_snapshot": self.state_snapshot,
            "goal": self.goal,
            "plan_name": self.plan_name,
            "action_names": self.action_names,
            "success": self.success,
            "reward": self.reward,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        return cls(
            state_snapshot=data["state_snapshot"],
            goal=data["goal"],
            plan_name=data["plan_name"],
            action_names=data["action_names"],
            success=data["success"],
            reward=data["reward"],
            reason=data.get("reason", ""),
            episode_id=UUID(data["episode_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


class EpisodeMemory:
    """Simple in-memory episodic memory for plans and outcomes."""

    def __init__(self, repository: "EpisodeRepository | None" = None) -> None:
        self.episodes: List[Episode] = []
        self._repository = repository

    def remember(
        self,
        state: State,
        goal: str,
        plan: Plan,
        success: bool,
        reward: float,
        reason: str = "",
    ) -> Episode:
        episode = Episode(
            state_snapshot=dict(state.data),
            goal=goal,
            plan_name=plan.name,
            action_names=[action.name for action in plan.actions],
            success=success,
            reward=reward,
            reason=reason,
        )
        self.episodes.append(episode)
        if self._repository is not None:
            self._repository.save_episode(episode)
        return episode

    def similar(self, state: State, goal: str, limit: int = 5) -> List[Episode]:
        scored = [
            (self._similarity(episode, state, goal), episode)
            for episode in self.episodes
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [episode for score, episode in scored[:limit] if score > 0]

    def plan_bias(self, plan: Plan, state: State, goal: str) -> float:
        """Return a memory-derived bias for a candidate plan."""

        related = self.similar(state, goal, limit=10)
        if not related:
            return 0.0

        plan_actions = {action.name for action in plan.actions}
        reward = 0.0
        for episode in related:
            if episode.plan_name == plan.name or plan_actions.intersection(episode.action_names):
                reward += episode.reward
        return reward / len(related)

    def _similarity(self, episode: Episode, state: State, goal: str) -> float:
        score = 0.0
        if episode.goal.lower() == goal.lower():
            score += 1.0

        current_values = {str(value).lower() for value in (state.data or {}).values()}
        past_values = {str(value).lower() for value in episode.state_snapshot.values()}
        overlap = current_values.intersection(past_values)
        score += len(overlap) * 0.5

        return score
