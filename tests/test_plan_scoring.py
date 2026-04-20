from __future__ import annotations

from sce.core.actions import Action
from sce.core.plan_scoring import PlanSelector
from sce.core.planning import Plan
from sce.core.types import State


def test_selector_prefers_plan_with_evidence_and_escalation():
    state = State("context", {"claim": "supplier is unreliable"})
    goal = "assess supplier risk"

    good_plan = Plan(
        name="good",
        actions=[
            Action(
                name="fetch_supplier_risk",
                description="",
                action_type="tool",
                payload={"tool": "supplier_risk_api", "arguments": {}},
            ),
            Action(
                name="request_review",
                description="",
                action_type="workflow",
                payload={},
            ),
        ],
        reason="",
    )

    weak_plan = Plan(
        name="weak",
        actions=[
            Action(
                name="monitor",
                description="",
                action_type="workflow",
                payload={},
            )
        ],
        reason="",
    )

    selector = PlanSelector()
    best = selector.select([weak_plan, good_plan], state, goal)

    assert best.plan.name == "good"
    assert best.score > 0


def test_selector_returns_single_plan_when_only_one_provided():
    state = State("context", {})
    goal = "observe"

    plan = Plan(
        name="only",
        actions=[
            Action(name="monitor", description="", action_type="workflow", payload={})
        ],
        reason="",
    )

    selector = PlanSelector()
    best = selector.select([plan], state, goal)

    assert best.plan.name == "only"
