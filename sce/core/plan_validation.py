from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from sce.core.planning import Plan
from sce.core.types import Constraint, State


@dataclass(frozen=True)
class PlanValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)


class PlanValidator:
    """Validate generated plans before execution.

    Phase 1 checks:
    - allowed action names
    - allowed tool names
    - optional state constraints on the current state
    """

    def __init__(
        self,
        allowed_actions: Set[str] | None = None,
        allowed_tools: Set[str] | None = None,
        constraints: List[Constraint] | None = None,
    ) -> None:
        self.allowed_actions = allowed_actions or {
            "fetch_supplier_risk",
            "request_review",
            "monitor",
        }
        self.allowed_tools = allowed_tools or {"supplier_risk_api"}
        self.constraints = constraints or []

    def validate(self, plan: Plan, current_state: State) -> PlanValidationResult:
        errors: List[str] = []

        for index, action in enumerate(plan.actions):
            if action.name not in self.allowed_actions:
                errors.append(f"Action at index {index} is not allowed: {action.name}")

            tool = action.payload.get("tool")
            if tool is not None and tool not in self.allowed_tools:
                errors.append(f"Tool at index {index} is not allowed: {tool}")

        for constraint in self.constraints:
            if not constraint.is_satisfied(current_state):
                errors.append(f"Current state violates constraint: {constraint.name}")

        return PlanValidationResult(valid=len(errors) == 0, errors=errors)
