from __future__ import annotations

from typing import List, Optional, Tuple

from sce.core.attractors import AttractorDetector, FixedPointAttractorDetector
from sce.core.candidates import CandidateGenerator, RuleCandidateGenerator, candidate_results_to_legacy_pairs
from sce.core.scoring import SCEScoringEngine
from sce.core.types import Attractor, Event, EventType, EvolutionResult, Rule, State, Transition, TransitionType
from sce.storage.memory import MemoryRepository


class SCEEvolver:
    def __init__(
        self,
        repo: MemoryRepository,
        scorer: SCEScoringEngine,
        candidate_generator: Optional[CandidateGenerator] = None,
        attractor_detector: Optional[AttractorDetector] = None,
    ) -> None:
        self.repo = repo
        self.scorer = scorer
        self.candidate_generator = candidate_generator
        self.attractor_detector = attractor_detector or FixedPointAttractorDetector()

    def admissible_state(self, state: State) -> bool:
        for constraint in self.repo.constraints.values():
            if constraint.hard and not constraint.is_satisfied(state):
                return False
        return True

    def admissible_transition(self, source: State, target: State) -> bool:
        return self.admissible_state(target)

    def generate_candidates(self, current_state: State) -> List[Tuple[State, Optional[Rule]]]:
        generator = self.candidate_generator
        if generator is None:
            generator = RuleCandidateGenerator(list(self.repo.rules.values()))
        return candidate_results_to_legacy_pairs(generator.generate(current_state))

    def detect_attractor(self, trace: List[State]) -> Optional[Attractor]:
        return self.attractor_detector.detect(trace)

    def evolve(self, current_state: State, max_steps: int = 10, epsilon: float = 0.01) -> EvolutionResult:
        trace: List[State] = [current_state]
        selected_transitions: List[Transition] = []

        self.repo.add_state(current_state)
        self.scorer.compute_stability(current_state, transition_cost=0.0, trace=trace)

        for _step in range(1, max_steps + 1):
            candidates_with_rules = self.generate_candidates(current_state)
            if not candidates_with_rules:
                self.repo.add_event(Event(EventType.HALT, state_id=current_state.state_id, payload={"reason": "no candidates"}))
                return EvolutionResult("no candidates", current_state, trace, selected_transitions)

            scored: List[Tuple[State, Optional[Rule], Transition, float]] = []
            for candidate, rule in candidates_with_rules:
                self.repo.add_state(candidate)
                transition_cost = self.scorer.compute_transition_cost(current_state, candidate, rule)
                admissible = self.admissible_transition(current_state, candidate)
                transition = Transition(
                    from_state_id=current_state.state_id,
                    to_state_id=candidate.state_id,
                    rule_id=rule.rule_id if rule else None,
                    transition_type=TransitionType.RULE_BASED,
                    cost=transition_cost,
                    admissible=admissible,
                    selected=False,
                )
                self.repo.add_transition(transition)
                if not admissible:
                    candidate.status = "rejected"
                    continue
                score = self.scorer.compute_stability(candidate, transition_cost=transition_cost, trace=trace)
                scored.append((candidate, rule, transition, score))

            if not scored:
                self.repo.add_event(Event(EventType.HALT, state_id=current_state.state_id, payload={"reason": "no admissible transitions"}))
                return EvolutionResult("no admissible transitions", current_state, trace, selected_transitions)

            next_state, selected_rule, selected_transition, _ = max(scored, key=lambda item: item[3])
            next_state.status = "active"
            self.repo.mark_transition_selected(selected_transition.transition_id)
            selected_transitions.append(selected_transition)
            self.repo.add_event(
                Event(
                    EventType.TRANSITION_SELECTED,
                    state_id=next_state.state_id,
                    transition_id=selected_transition.transition_id,
                    payload={
                        "from": str(current_state.state_id),
                        "to": str(next_state.state_id),
                        "rule": selected_rule.name if selected_rule else None,
                        "stability": next_state.stability,
                    },
                )
            )
            trace.append(next_state)

            if abs(next_state.stability - current_state.stability) < epsilon:
                attractor = self.detect_attractor(trace)
                if attractor:
                    self.repo.add_attractor(attractor)
                    return EvolutionResult("converged", next_state, trace, selected_transitions, attractor)
            current_state = next_state

        attractor = self.detect_attractor(trace)
        if attractor:
            self.repo.add_attractor(attractor)
        return EvolutionResult("max steps reached", current_state, trace, selected_transitions, attractor)
