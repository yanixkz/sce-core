from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sce.core.episode_memory import Episode, EpisodeMemory
from sce.core.planning import Plan
from sce.core.types import State


@dataclass(frozen=True)
class AbstractRule:
    """A generalized rule extracted from successful episodes."""

    condition: str
    recommended_actions: List[str]
    confidence: float
    support_count: int
    rule_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)


class AbstractionEngine:
    """Extract simple reusable rules from episodic memory.

    Phase 1 groups successful episodes by goal and action sequence.
    """

    def extract_rules(self, memory: EpisodeMemory, min_support: int = 2) -> List[AbstractRule]:
        groups: dict[tuple[str, tuple[str, ...]], List[Episode]] = {}

        for episode in memory.episodes:
            if not episode.success:
                continue
            key = (episode.goal.lower(), tuple(episode.action_names))
            groups.setdefault(key, []).append(episode)

        rules: List[AbstractRule] = []
        for (goal, actions), episodes in groups.items():
            if len(episodes) < min_support:
                continue
            total_reward = sum(episode.reward for episode in episodes)
            confidence = max(0.0, min(1.0, total_reward / len(episodes)))
            rules.append(
                AbstractRule(
                    condition=f"goal == '{goal}'",
                    recommended_actions=list(actions),
                    confidence=confidence,
                    support_count=len(episodes),
                )
            )

        return rules


class RuleMemory:
    """Stores extracted abstract rules and produces plan bias."""

    def __init__(self) -> None:
        self.rules: List[AbstractRule] = []

    def update(self, rules: List[AbstractRule]) -> None:
        existing = {(rule.condition, tuple(rule.recommended_actions)) for rule in self.rules}
        for rule in rules:
            key = (rule.condition, tuple(rule.recommended_actions))
            if key not in existing:
                self.rules.append(rule)

    def plan_bias(self, plan: Plan, state: State, goal: str) -> float:
        plan_actions = [action.name for action in plan.actions]
        goal_condition = f"goal == '{goal.lower()}'"
        bias = 0.0

        for rule in self.rules:
            if rule.condition != goal_condition:
                continue
            if self._actions_match(rule.recommended_actions, plan_actions):
                bias += rule.confidence

        return bias

    @staticmethod
    def _actions_match(expected: List[str], actual: List[str]) -> bool:
        return all(action in actual for action in expected)
