from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class RelationType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CAUSES = "causes"
    DERIVED_FROM = "derived_from"
    SIMILAR_TO = "similar_to"
    CONTAINS = "contains"
    RESONATES_WITH = "resonates_with"


class TransitionType(str, Enum):
    INFERRED = "inferred"
    RULE_BASED = "rule_based"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"


class EventType(str, Enum):
    STATE_CREATED = "state_created"
    STATE_EVALUATED = "state_evaluated"
    TRANSITION_GENERATED = "transition_generated"
    TRANSITION_SELECTED = "transition_selected"
    ATTRACTOR_DETECTED = "attractor_detected"
    HALT = "halt"


@dataclass
class State:
    state_type: str
    data: Dict[str, Any]
    state_id: UUID = field(default_factory=uuid4)
    energy: float = 0.0
    entropy: float = 0.0
    coherence: float = 0.0
    conflict: float = 0.0
    stability: float = 0.0
    support: float = 0.0
    created_at: datetime = field(default_factory=utc_now)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    status: str = "active"
    signature_hash: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Link:
    source_state_id: UUID
    target_state_id: UUID
    relation_type: RelationType
    strength: float = 1.0
    directed: bool = True
    link_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Constraint:
    name: str
    predicate: Callable[[State], bool]
    constraint_type: str = "generic"
    scope_type: Optional[str] = None
    scope_ref: Optional[str] = None
    hard: bool = True
    weight: float = 1.0
    priority: int = 0
    constraint_id: UUID = field(default_factory=uuid4)
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def applies_to(self, state: State) -> bool:
        if self.scope_type is None:
            return True
        if self.scope_type == "state_type":
            return state.state_type == self.scope_ref
        if self.scope_type == "supplier_id":
            return state.data.get("supplier_id") == self.scope_ref
        return True

    def is_satisfied(self, state: State) -> bool:
        if not self.applies_to(state):
            return True
        return bool(self.predicate(state))


@dataclass
class Rule:
    name: str
    transform: Callable[[State], List[State]]
    rule_type: str = "generic"
    cost_model: Optional[Callable[[State, State], float]] = None
    active: bool = True
    priority: int = 0
    rule_id: UUID = field(default_factory=uuid4)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transition:
    from_state_id: UUID
    to_state_id: UUID
    rule_id: Optional[UUID] = None
    transition_type: TransitionType = TransitionType.RULE_BASED
    cost: float = 0.0
    probability: float = 1.0
    delta_time_ms: Optional[int] = None
    admissible: bool = True
    selected: bool = False
    transition_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    event_type: EventType
    state_id: Optional[UUID] = None
    transition_id: Optional[UUID] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    event_time: datetime = field(default_factory=utc_now)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Attractor:
    attractor_type: str
    signature_hash: str
    invariant: Dict[str, Any]
    member_state_ids: List[UUID]
    stability_score: float
    attractor_id: UUID = field(default_factory=uuid4)
    discovered_at: datetime = field(default_factory=utc_now)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoringWeights:
    coherence: float = 1.0
    cost: float = 0.5
    conflict: float = 0.8
    entropy: float = 0.4
    support: float = 0.6


@dataclass
class EvolutionResult:
    reason: str
    final_state: State
    trace: List[State]
    selected_transitions: List[Transition]
    attractor: Optional[Attractor] = None
