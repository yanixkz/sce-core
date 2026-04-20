from __future__ import annotations

import math
from typing import List, Optional

from sce.core.types import Event, EventType, RelationType, Rule, ScoringWeights, State
from sce.storage.memory import MemoryRepository


class SCEScoringEngine:
    def __init__(self, repo: MemoryRepository, weights: Optional[ScoringWeights] = None) -> None:
        self.repo = repo
        self.weights = weights or ScoringWeights()

    def compute_coherence(self, state: State) -> float:
        incoming = self.repo.incoming_links(state.state_id)
        support_strength = sum(
            link.strength
            for link in incoming
            if link.relation_type
            in {RelationType.SUPPORTS, RelationType.RESONATES_WITH, RelationType.DERIVED_FROM, RelationType.SIMILAR_TO}
        )
        contradiction_strength = sum(link.strength for link in incoming if link.relation_type == RelationType.CONTRADICTS)
        return self._squash(support_strength - contradiction_strength * 0.5)

    def compute_conflict(self, state: State) -> float:
        conflict = 0.0
        for constraint in self.repo.constraints.values():
            if not constraint.applies_to(state):
                continue
            if not constraint.is_satisfied(state):
                penalty = constraint.weight * (2.0 if constraint.hard else 1.0)
                conflict += penalty
        incoming = self.repo.incoming_links(state.state_id)
        conflict += sum(link.strength for link in incoming if link.relation_type == RelationType.CONTRADICTS)
        return self._squash(conflict)

    def compute_entropy(self, state: State) -> float:
        data = state.data or {}
        if not data:
            return 1.0
        uncertain = 0
        total = 0
        for value in data.values():
            total += 1
            if value is None or (isinstance(value, str) and value.strip() == ""):
                uncertain += 1
            elif isinstance(value, float) and math.isnan(value):
                uncertain += 1
        return uncertain / total if total else 1.0

    def compute_support(self, state: State, trace: Optional[List[State]] = None) -> float:
        incoming = self.repo.incoming_links(state.state_id)
        support = sum(
            link.strength
            for link in incoming
            if link.relation_type in {RelationType.SUPPORTS, RelationType.RESONATES_WITH, RelationType.DERIVED_FROM}
        )
        if trace:
            repeated_type_count = sum(1 for s in trace if s.state_type == state.state_type)
            support += min(repeated_type_count * 0.1, 0.5)
        return self._squash(support)

    def compute_transition_cost(self, source: State, target: State, rule: Optional[Rule] = None) -> float:
        if rule and rule.cost_model:
            return float(rule.cost_model(source, target))
        changed_keys = 0
        all_keys = set(source.data.keys()) | set(target.data.keys())
        for key in all_keys:
            if source.data.get(key) != target.data.get(key):
                changed_keys += 1
        return changed_keys / len(all_keys) if all_keys else 0.0

    def compute_stability(self, state: State, transition_cost: float = 0.0, trace: Optional[List[State]] = None) -> float:
        state.coherence = self.compute_coherence(state)
        state.conflict = self.compute_conflict(state)
        state.entropy = self.compute_entropy(state)
        state.support = self.compute_support(state, trace)
        w = self.weights
        state.stability = (
            w.coherence * state.coherence
            - w.cost * transition_cost
            - w.conflict * state.conflict
            - w.entropy * state.entropy
            + w.support * state.support
        )
        self.repo.add_event(
            Event(
                EventType.STATE_EVALUATED,
                state_id=state.state_id,
                payload={
                    "coherence": state.coherence,
                    "conflict": state.conflict,
                    "entropy": state.entropy,
                    "support": state.support,
                    "transition_cost": transition_cost,
                    "stability": state.stability,
                },
            )
        )
        return state.stability

    @staticmethod
    def _squash(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))
