from __future__ import annotations

from sce.core.actions import Action
from sce.core.plan_validation import PlanValidator
from sce.core.planning import Plan
from sce.core.types import State


def test_valid_plan_passes_validation():
    validator = PlanValidator()

    plan = Plan(
        name="valid_plan",
        actions=[
            Action(
                name="fetch_supplier_risk",
                description="",
                action_type="tool",
                payload={"tool": "supplier_risk_api", "arguments": {}},
            )
        ],
        reason="test",
    )

    state = State("context", {})

    result = validator.validate(plan, state)

    assert result.valid is True
    assert result.errors == []


def test_invalid_action_fails_validation():
    validator = PlanValidator()

    plan = Plan(
        name="invalid_plan",
        actions=[
            Action(
                name="hack_system",
                description="",
                action_type="workflow",
                payload={},
            )
        ],
        reason="test",
    )

    state = State("context", {})

    result = validator.validate(plan, state)

    assert result.valid is False
    assert "not allowed" in result.errors[0]


def test_invalid_tool_fails_validation():
    validator = PlanValidator()

    plan = Plan(
        name="invalid_tool_plan",
        actions=[
            Action(
                name="fetch_supplier_risk",
                description="",
                action_type="tool",
                payload={"tool": "unknown_api", "arguments": {}},
            )
        ],
        reason="test",
    )

    state = State("context", {})

    result = validator.validate(plan, state)

    assert result.valid is False
    assert "not allowed" in result.errors[0]
