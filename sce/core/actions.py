from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol
from uuid import UUID, uuid4

from sce.core.types import State


@dataclass(frozen=True)
class Action:
    """An external or internal operation that can change system state."""

    name: str
    description: str
    action_type: str = "internal"
    payload: Dict[str, Any] = field(default_factory=dict)
    action_id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class ActionResult:
    """Result of executing an action."""

    action_id: UUID
    success: bool
    message: str
    resulting_state: State
    meta: Dict[str, Any] = field(default_factory=dict)


class ActionHandler(Protocol):
    def __call__(self, action: Action, current_state: State) -> ActionResult:
        ...


class ActionExecutor:
    """Registry-based action executor.

    The executor does not call real external services by default. Handlers can
    be registered explicitly, which makes the layer safe for tests and demos.
    """

    def __init__(self) -> None:
        self.handlers: Dict[str, ActionHandler] = {}

    def register(self, action_name: str, handler: ActionHandler) -> None:
        self.handlers[action_name] = handler

    def execute(self, action: Action, current_state: State) -> ActionResult:
        if action.name not in self.handlers:
            return ActionResult(
                action_id=action.action_id,
                success=False,
                message=f"No handler registered for action: {action.name}",
                resulting_state=current_state,
                meta={"missing_handler": action.name},
            )
        return self.handlers[action.name](action, current_state)


class ActionPolicy:
    """Select actions from a state using simple deterministic rules."""

    def propose(self, state: State) -> List[Action]:
        claim = str(state.data.get("claim", "")).lower()
        if "unreliable" in claim or "high risk" in claim or "risky" in claim:
            return [
                Action(
                    name="request_review",
                    description="Request human or operational review for a risky state.",
                    action_type="workflow",
                    payload={"reason": claim},
                )
            ]
        return [
            Action(
                name="monitor",
                description="Continue monitoring the current state.",
                action_type="workflow",
                payload={"reason": claim or "no explicit risk"},
            )
        ]


def request_review_handler(action: Action, current_state: State) -> ActionResult:
    next_state = State(
        state_type="action_result",
        data={
            "action": action.name,
            "status": "review_requested",
            "source_claim": current_state.data.get("claim"),
            "reason": action.payload.get("reason"),
        },
    )
    return ActionResult(
        action_id=action.action_id,
        success=True,
        message="Review requested.",
        resulting_state=next_state,
    )


def monitor_handler(action: Action, current_state: State) -> ActionResult:
    next_state = State(
        state_type="action_result",
        data={
            "action": action.name,
            "status": "monitoring",
            "source_claim": current_state.data.get("claim"),
            "reason": action.payload.get("reason"),
        },
    )
    return ActionResult(
        action_id=action.action_id,
        success=True,
        message="Monitoring continued.",
        resulting_state=next_state,
    )
