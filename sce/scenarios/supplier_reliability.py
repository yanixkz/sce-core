from __future__ import annotations

from typing import Any, Dict, List, Tuple

from sce.core.evolution import SCEEvolver
from sce.core.explain import SCEExplainer
from sce.core.scoring import SCEScoringEngine
from sce.core.types import Constraint, Link, RelationType, Rule, State
from sce.storage.memory import MemoryRepository


def make_supplier_reliability_scenario() -> Tuple[MemoryRepository, State]:
    repo = MemoryRepository()

    reliable_state = State(
        state_type="supplier_reliability_hypothesis",
        data={
            "supplier_id": "A",
            "category": "X",
            "claim": "supplier A is reliable for category X",
            "late_delivery_rate": 0.08,
            "complaints_90d": 3,
            "price_delta_vs_market": -0.04,
        },
    )
    repo.add_state(reliable_state)

    evidence_states = [
        State(state_type="supplier_metric", data={"supplier_id": "A", "metric": "on_time_rate", "value": 0.92}),
        State(state_type="supplier_metric", data={"supplier_id": "A", "metric": "late_delivery_rate", "value": 0.08}),
        State(state_type="supplier_metric", data={"supplier_id": "A", "metric": "price_delta_vs_market", "value": -0.04}),
        State(state_type="supplier_metric", data={"supplier_id": "A", "metric": "complaints_90d", "value": 3}),
    ]
    for state in evidence_states:
        repo.add_state(state)

    repo.add_link(Link(evidence_states[0].state_id, reliable_state.state_id, RelationType.SUPPORTS, 0.8))
    repo.add_link(Link(evidence_states[1].state_id, reliable_state.state_id, RelationType.SUPPORTS, 0.6))
    repo.add_link(Link(evidence_states[2].state_id, reliable_state.state_id, RelationType.SUPPORTS, 0.4))
    repo.add_link(Link(evidence_states[3].state_id, reliable_state.state_id, RelationType.CONTRADICTS, 0.3))

    repo.add_constraint(
        Constraint(
            name="late_delivery_rate_must_be_below_20_percent",
            constraint_type="reliability_rule",
            scope_type="state_type",
            scope_ref="supplier_reliability_hypothesis",
            hard=True,
            weight=1.0,
            priority=10,
            predicate=lambda s: float(s.data.get("late_delivery_rate", 1.0)) <= 0.20,
        )
    )

    def rule_conditional_reliability(source: State) -> List[State]:
        if source.state_type != "supplier_reliability_hypothesis":
            return []
        return [
            State(
                state_type="supplier_reliability_hypothesis",
                data={
                    **source.data,
                    "claim": "supplier A is reliable only with extended deadline",
                    "late_delivery_rate": 0.19,
                    "condition": "extended_deadline_required",
                },
            )
        ]

    repo.add_rule(
        Rule(
            name="create_conditional_reliability_state",
            rule_type="risk_adjustment",
            transform=rule_conditional_reliability,
            cost_model=lambda source, target: 0.12,
            priority=10,
        )
    )

    def rule_manual_review(source: State) -> List[State]:
        if source.state_type != "supplier_reliability_hypothesis":
            return []
        return [
            State(
                state_type="supplier_review_required",
                data={
                    "supplier_id": source.data.get("supplier_id"),
                    "category": source.data.get("category"),
                    "claim": "supplier requires manual review",
                    "reason": "risk or contradiction detected",
                    "late_delivery_rate": source.data.get("late_delivery_rate"),
                },
            )
        ]

    repo.add_rule(
        Rule(
            name="create_manual_review_state",
            rule_type="risk_control",
            transform=rule_manual_review,
            cost_model=lambda source, target: 0.25,
            priority=5,
        )
    )

    def rule_exclude_from_pool(source: State) -> List[State]:
        if source.state_type != "supplier_reliability_hypothesis":
            return []
        return [
            State(
                state_type="supplier_reliability_hypothesis",
                data={**source.data, "claim": "supplier A is excluded from reliable pool", "status": "excluded_from_reliable_pool"},
            )
        ]

    repo.add_rule(
        Rule(
            name="exclude_from_reliable_pool",
            rule_type="risk_control",
            transform=rule_exclude_from_pool,
            cost_model=lambda source, target: 0.45,
            priority=3,
        )
    )
    return repo, reliable_state


def run_demo() -> Dict[str, Any]:
    repo, start_state = make_supplier_reliability_scenario()
    scorer = SCEScoringEngine(repo)
    evolver = SCEEvolver(repo, scorer)
    explainer = SCEExplainer(repo)

    result = evolver.evolve(start_state, max_steps=5, epsilon=0.001)
    explanation = explainer.explain_state(result.final_state.state_id)

    return {
        "reason": result.reason,
        "final_state_id": str(result.final_state.state_id),
        "final_state_type": result.final_state.state_type,
        "final_state_data": result.final_state.data,
        "trace": [
            {
                "state_id": str(s.state_id),
                "state_type": s.state_type,
                "status": s.status,
                "claim": s.data.get("claim"),
                "stability": s.stability,
                "conflict": s.conflict,
                "entropy": s.entropy,
                "coherence": s.coherence,
                "support": s.support,
            }
            for s in result.trace
        ],
        "selected_transitions": [
            {
                "transition_id": str(t.transition_id),
                "from": str(t.from_state_id),
                "to": str(t.to_state_id),
                "cost": t.cost,
                "selected": t.selected,
                "admissible": t.admissible,
            }
            for t in result.selected_transitions
        ],
        "candidate_count": len(repo.transitions),
        "state_count": len(repo.states),
        "event_count": len(repo.events),
        "attractor": None if result.attractor is None else {
            "id": str(result.attractor.attractor_id),
            "type": result.attractor.attractor_type,
            "signature": result.attractor.signature_hash,
            "stability_score": result.attractor.stability_score,
        },
        "explanation": explanation,
    }
