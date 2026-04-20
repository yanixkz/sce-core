from __future__ import annotations

from typing import Any, Dict

from sce.core.explain import SCEExplainer
from sce.core.scoring import SCEScoringEngine
from sce.core.types import Constraint, Link, RelationType, State
from sce.storage.memory import MemoryRepository


def run_contract_risk_demo() -> Dict[str, Any]:
    """Demonstrate contract risk evaluation as state stability.

    A contract is represented as competing states:
    - healthy / acceptable risk
    - risky / unstable

    Clauses and events become evidence and constraints. SCE scores both states
    and explains why the contract moves into or stays out of risk.
    """

    repo = MemoryRepository()

    healthy = State(
        state_type="contract_risk_state",
        data={
            "contract_id": "C-001",
            "claim": "contract C-001 is within acceptable risk",
            "payment_delay_days": 3,
            "delivery_delay_days": 2,
            "change_requests_30d": 1,
            "material_breach": False,
        },
    )
    risky = State(
        state_type="contract_risk_state",
        data={
            "contract_id": "C-001",
            "claim": "contract C-001 is high risk",
            "payment_delay_days": 18,
            "delivery_delay_days": 11,
            "change_requests_30d": 5,
            "material_breach": True,
        },
    )

    repo.add_state(healthy)
    repo.add_state(risky)

    clause_payment = State(
        state_type="contract_clause",
        data={"clause": "payment must not be delayed more than 10 days"},
    )
    clause_delivery = State(
        state_type="contract_clause",
        data={"clause": "delivery delay must remain below 7 days"},
    )
    event_late_payment = State(
        state_type="contract_event",
        data={"event": "payment delayed 18 days"},
    )
    event_delivery_delay = State(
        state_type="contract_event",
        data={"event": "delivery delayed 11 days"},
    )
    event_breach = State(
        state_type="contract_event",
        data={"event": "material breach reported"},
    )

    for state in [clause_payment, clause_delivery, event_late_payment, event_delivery_delay, event_breach]:
        repo.add_state(state)

    repo.add_link(Link(clause_payment.state_id, healthy.state_id, RelationType.SUPPORTS, 0.4))
    repo.add_link(Link(clause_delivery.state_id, healthy.state_id, RelationType.SUPPORTS, 0.4))
    repo.add_link(Link(event_late_payment.state_id, healthy.state_id, RelationType.CONTRADICTS, 0.9))
    repo.add_link(Link(event_delivery_delay.state_id, healthy.state_id, RelationType.CONTRADICTS, 0.8))
    repo.add_link(Link(event_breach.state_id, healthy.state_id, RelationType.CONTRADICTS, 1.0))

    repo.add_link(Link(event_late_payment.state_id, risky.state_id, RelationType.SUPPORTS, 0.9))
    repo.add_link(Link(event_delivery_delay.state_id, risky.state_id, RelationType.SUPPORTS, 0.8))
    repo.add_link(Link(event_breach.state_id, risky.state_id, RelationType.SUPPORTS, 1.0))
    repo.add_link(Link(clause_payment.state_id, risky.state_id, RelationType.CONTRADICTS, 0.2))
    repo.add_link(Link(clause_delivery.state_id, risky.state_id, RelationType.CONTRADICTS, 0.2))

    repo.add_constraint(
        Constraint(
            name="payment_delay_must_be_below_10_days",
            constraint_type="contract_clause",
            scope_type="state_type",
            scope_ref="contract_risk_state",
            hard=False,
            weight=1.0,
            predicate=lambda state: int(state.data.get("payment_delay_days", 0)) <= 10,
        )
    )
    repo.add_constraint(
        Constraint(
            name="delivery_delay_must_be_below_7_days",
            constraint_type="contract_clause",
            scope_type="state_type",
            scope_ref="contract_risk_state",
            hard=False,
            weight=1.0,
            predicate=lambda state: int(state.data.get("delivery_delay_days", 0)) <= 7,
        )
    )
    repo.add_constraint(
        Constraint(
            name="material_breach_must_be_false",
            constraint_type="contract_clause",
            scope_type="state_type",
            scope_ref="contract_risk_state",
            hard=False,
            weight=1.0,
            predicate=lambda state: bool(state.data.get("material_breach", False)) is False,
        )
    )

    scorer = SCEScoringEngine(repo)
    candidates = [healthy, risky]
    for state in candidates:
        scorer.compute_stability(state)

    selected = max(candidates, key=lambda state: state.stability)
    explanation = SCEExplainer(repo).explain_comparison([state.state_id for state in candidates])

    return {
        "scenario": "contract_risk",
        "question": "Has the contract moved into a high-risk state?",
        "candidates": [
            {
                "claim": state.data["claim"],
                "payment_delay_days": state.data["payment_delay_days"],
                "delivery_delay_days": state.data["delivery_delay_days"],
                "material_breach": state.data["material_breach"],
                "coherence": state.coherence,
                "conflict": state.conflict,
                "entropy": state.entropy,
                "support": state.support,
                "stability": state.stability,
            }
            for state in candidates
        ],
        "selected_claim": selected.data["claim"],
        "selected_state_id": str(selected.state_id),
        "explanation": explanation,
    }
