from __future__ import annotations

from sce.core.actions import Action, ActionExecutor, ActionPolicy, monitor_handler, request_review_handler
from sce.core.types import State


def test_action_policy_requests_review_for_unreliable_state():
    state = State("decision", {"claim": "supplier is unreliable"})
    policy = ActionPolicy()

    actions = policy.propose(state)

    assert len(actions) == 1
    assert actions[0].name == "request_review"


def test_action_policy_monitors_non_risky_state():
    state = State("decision", {"claim": "supplier is stable"})
    policy = ActionPolicy()

    actions = policy.propose(state)

    assert len(actions) == 1
    assert actions[0].name == "monitor"


def test_action_executor_runs_registered_handler():
    state = State("decision", {"claim": "supplier is unreliable"})
    action = Action(name="request_review", description="Request review")
    executor = ActionExecutor()
    executor.register("request_review", request_review_handler)

    result = executor.execute(action, state)

    assert result.success is True
    assert result.resulting_state.data["status"] == "review_requested"


def test_action_executor_returns_failure_for_missing_handler():
    state = State("decision", {"claim": "supplier is unreliable"})
    action = Action(name="unknown", description="Unknown action")
    executor = ActionExecutor()

    result = executor.execute(action, state)

    assert result.success is False
    assert result.resulting_state is state
    assert result.meta["missing_handler"] == "unknown"


def test_monitor_handler_returns_monitoring_state():
    state = State("decision", {"claim": "supplier is stable"})
    action = Action(name="monitor", description="Monitor")

    result = monitor_handler(action, state)

    assert result.success is True
    assert result.resulting_state.data["status"] == "monitoring"
