import pytest

from sce.core.constraint_dsl import ConstraintDSLError, compile_constraint_dsl
from sce.core.types import Constraint, State


def test_comparison_operators():
    state = State("supplier", {"rate": 0.2, "tier": 2})
    assert compile_constraint_dsl("rate == 0.2")(state) is True
    assert compile_constraint_dsl("rate != 0.1")(state) is True
    assert compile_constraint_dsl("tier < 3")(state) is True
    assert compile_constraint_dsl("tier <= 2")(state) is True
    assert compile_constraint_dsl("tier > 1")(state) is True
    assert compile_constraint_dsl("tier >= 2")(state) is True


def test_boolean_operators_and_parentheses():
    expr = '(tier >= 2 AND status == "active") OR NOT blocked'
    predicate = compile_constraint_dsl(expr)

    assert predicate(State("supplier", {"tier": 2, "status": "active", "blocked": True})) is True
    assert predicate(State("supplier", {"tier": 1, "status": "active", "blocked": False})) is True
    assert predicate(State("supplier", {"tier": 1, "status": "inactive", "blocked": True})) is False


def test_boolean_literals():
    predicate = compile_constraint_dsl("approved == true AND flagged == false")
    assert predicate(State("supplier", {"approved": True, "flagged": False})) is True
    assert predicate(State("supplier", {"approved": True, "flagged": True})) is False


def test_missing_value_from_state_data():
    predicate = compile_constraint_dsl("unknown == 10")
    assert predicate(State("supplier", {"known": 10})) is False


def test_compiled_predicate_is_compatible_with_constraint():
    constraint = Constraint(
        name="max_late_rate",
        predicate=compile_constraint_dsl("late_delivery_rate <= 0.3"),
    )

    valid = State("supplier", {"late_delivery_rate": 0.2})
    invalid = State("supplier", {"late_delivery_rate": 0.5})

    assert constraint.is_satisfied(valid) is True
    assert constraint.is_satisfied(invalid) is False


def test_invalid_syntax_raises():
    with pytest.raises(ConstraintDSLError):
        compile_constraint_dsl("tier >=")


def test_invalid_type_comparison_raises():
    predicate = compile_constraint_dsl('tier < "gold"')
    with pytest.raises(ConstraintDSLError):
        predicate(State("supplier", {"tier": 2}))
