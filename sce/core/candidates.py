from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol, Tuple

from sce.core.types import Rule, State


@dataclass(frozen=True)
class CandidateResult:
    """A generated candidate state plus optional provenance."""

    state: State
    rule: Optional[Rule] = None
    source: str = "unknown"


class CandidateGenerator(Protocol):
    """Interface for generating possible next states."""

    def generate(self, current_state: State) -> List[CandidateResult]:
        ...


class RuleCandidateGenerator:
    """Generate candidates by applying active transformation rules."""

    def __init__(self, rules: List[Rule]) -> None:
        self.rules = rules

    def generate(self, current_state: State) -> List[CandidateResult]:
        candidates: List[CandidateResult] = []

        for rule in sorted(self.rules, key=lambda item: item.priority, reverse=True):
            if not rule.active:
                continue

            for state in rule.transform(current_state):
                state.status = "candidate"
                candidates.append(CandidateResult(state=state, rule=rule, source="rule"))

        return candidates


class CompositeCandidateGenerator:
    """Combine multiple candidate generators into one source."""

    def __init__(self, generators: List[CandidateGenerator]) -> None:
        self.generators = generators

    def generate(self, current_state: State) -> List[CandidateResult]:
        candidates: List[CandidateResult] = []
        for generator in self.generators:
            candidates.extend(generator.generate(current_state))
        return candidates


def candidate_results_to_legacy_pairs(
    candidates: List[CandidateResult],
) -> List[Tuple[State, Optional[Rule]]]:
    """Compatibility helper for existing evolution code."""

    return [(candidate.state, candidate.rule) for candidate in candidates]
