from sce.core.abstractions import AbstractionEngine, RuleMemory
from sce.core.actions import Action
from sce.core.episode_memory import EpisodeMemory
from sce.core.planning import Plan
from sce.core.types import State


def test_rule_extraction_and_usage():
    memory = EpisodeMemory()

    state = State("context", {"entity": "supplier A"})

    plan = Plan(
        name="p1",
        actions=[
            Action(name="fetch_supplier_risk", description="", action_type="tool", payload={}),
            Action(name="request_review", description="", action_type="workflow", payload={}),
        ],
        reason="",
    )

    # store successful episodes
    for _ in range(3):
        memory.remember(state, "assess supplier risk", plan, True, 1.0)

    engine = AbstractionEngine()
    rules = engine.extract_rules(memory, min_support=2)

    assert len(rules) >= 1

    rule_memory = RuleMemory()
    rule_memory.update(rules)

    bias = rule_memory.plan_bias(plan, state, "assess supplier risk")
    assert bias > 0
