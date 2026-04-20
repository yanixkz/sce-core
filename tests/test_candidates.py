from __future__ import annotations

from sce.core.candidates import CompositeCandidateGenerator, RuleCandidateGenerator
from sce.core.types import Rule, State


def test_rule_candidate_generator_applies_active_rules_by_priority():
    start = State(state_type="start", data={"value": 1})

    low_priority_rule = Rule(
        name="low_priority",
        priority=1,
        transform=lambda state: [State(state_type="candidate", data={"source": "low"})],
    )
    high_priority_rule = Rule(
        name="high_priority",
        priority=10,
        transform=lambda state: [State(state_type="candidate", data={"source": "high"})],
    )
    inactive_rule = Rule(
        name="inactive",
        active=False,
        priority=100,
        transform=lambda state: [State(state_type="candidate", data={"source": "inactive"})],
    )

    generator = RuleCandidateGenerator([low_priority_rule, high_priority_rule, inactive_rule])
    candidates = generator.generate(start)

    assert [candidate.state.data["source"] for candidate in candidates] == ["high", "low"]
    assert all(candidate.state.status == "candidate" for candidate in candidates)
    assert all(candidate.source == "rule" for candidate in candidates)


def test_composite_candidate_generator_combines_sources():
    start = State(state_type="start", data={})
    first = RuleCandidateGenerator([
        Rule(name="first", transform=lambda state: [State(state_type="candidate", data={"id": 1})])
    ])
    second = RuleCandidateGenerator([
        Rule(name="second", transform=lambda state: [State(state_type="candidate", data={"id": 2})])
    ])

    generator = CompositeCandidateGenerator([first, second])
    candidates = generator.generate(start)

    assert [candidate.state.data["id"] for candidate in candidates] == [1, 2]
