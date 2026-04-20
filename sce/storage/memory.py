from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from sce.core.types import Attractor, Constraint, Event, EventType, Link, Rule, State, Transition


class MemoryRepository:
    """In-memory storage for MVP execution and tests."""

    def __init__(self) -> None:
        self.states: Dict[UUID, State] = {}
        self.links: Dict[UUID, Link] = {}
        self.constraints: Dict[UUID, Constraint] = {}
        self.rules: Dict[UUID, Rule] = {}
        self.transitions: Dict[UUID, Transition] = {}
        self.events: Dict[UUID, Event] = {}
        self.attractors: Dict[UUID, Attractor] = {}

    def add_state(self, state: State) -> UUID:
        self.states[state.state_id] = state
        self.add_event(Event(EventType.STATE_CREATED, state_id=state.state_id))
        return state.state_id

    def add_link(self, link: Link) -> UUID:
        self.links[link.link_id] = link
        return link.link_id

    def add_constraint(self, constraint: Constraint) -> UUID:
        self.constraints[constraint.constraint_id] = constraint
        return constraint.constraint_id

    def add_rule(self, rule: Rule) -> UUID:
        self.rules[rule.rule_id] = rule
        return rule.rule_id

    def add_transition(self, transition: Transition) -> UUID:
        self.transitions[transition.transition_id] = transition
        self.add_event(
            Event(
                EventType.TRANSITION_GENERATED,
                transition_id=transition.transition_id,
                payload={
                    "from_state_id": str(transition.from_state_id),
                    "to_state_id": str(transition.to_state_id),
                    "cost": transition.cost,
                    "admissible": transition.admissible,
                },
            )
        )
        return transition.transition_id

    def mark_transition_selected(self, transition_id: UUID) -> None:
        self.transitions[transition_id].selected = True

    def add_event(self, event: Event) -> UUID:
        self.events[event.event_id] = event
        return event.event_id

    def add_attractor(self, attractor: Attractor) -> UUID:
        self.attractors[attractor.attractor_id] = attractor
        self.add_event(
            Event(
                EventType.ATTRACTOR_DETECTED,
                payload={
                    "attractor_id": str(attractor.attractor_id),
                    "type": attractor.attractor_type,
                    "stability_score": attractor.stability_score,
                },
            )
        )
        return attractor.attractor_id

    def get_state(self, state_id: UUID) -> State:
        return self.states[state_id]

    def incoming_links(self, state_id: UUID) -> List[Link]:
        return [link for link in self.links.values() if link.target_state_id == state_id]

    def outgoing_links(self, state_id: UUID) -> List[Link]:
        return [link for link in self.links.values() if link.source_state_id == state_id]

    def neighborhood(self, state_id: UUID) -> List[State]:
        ids = set()
        for link in self.links.values():
            if link.source_state_id == state_id:
                ids.add(link.target_state_id)
            if link.target_state_id == state_id:
                ids.add(link.source_state_id)
        return [self.states[sid] for sid in ids if sid in self.states]
