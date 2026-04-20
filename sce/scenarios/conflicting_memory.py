from __future__ import annotations

from typing import Any, Dict

from sce.core.explain import SCEExplainer
from sce.core.scoring import SCEScoringEngine
from sce.core.types import Constraint, Link, RelationType, State
from sce.storage.memory import MemoryRepository


def run_conflicting_memory_demo() -> Dict[str, Any]:
    """Demonstrate how SCE Core scores and explains competing memory states.

    Scenario:
        An AI agent has conflicting evidence about whether a supplier is reliable.
        The system evaluates two competing states, selects the more stable one,
        and explains the decision.
    """

    repo = MemoryRepository()

    reliable = State(
        state_type="memory_hypothesis",
        data={
            "entity": "supplier A",
            "claim": "supplier A is reliable",
            "late_delivery_rate": 0.08,
        },
    )
    unreliable = State(
        state_type="memory_hypothesis",
        data={
            "entity": "supplier A",
            "claim": "supplier A is unreliable",
            "late_delivery_rate": 0.31,
        },
    )

    repo.add_state(reliable)
    repo.add_state(unreliable)

    evidence_on_time = State(
        state_type="evidence",
        data={"source": "order_history", "fact": "92% of orders were on time"},
    )
    evidence_late_recent = State(
        state_type="evidence",
        data={"source": "recent_orders", "fact": "31% of recent orders were late"},
    )
    evidence_complaints = State(
        state_type="evidence",
        data={"source": "support", "fact": "multiple recent complaints"},
    )

    for state in [evidence_on_time, evidence_late_recent, evidence_complaints]:
        repo.add_state(state)

    repo.add_link(Link(evidence_on_time.state_id, reliable.state_id, RelationType.SUPPORTS, 0.8))
    repo.add_link(Link(evidence_late_recent.state_id, reliable.state_id, RelationType.CONTRADICTS, 0.9))
    repo.add_link(Link(evidence_complaints.state_id, reliable.state_id, RelationType.CONTRADICTS, 0.6))

    repo.add_link(Link(evidence_late_recent.state_id, unreliable.state_id, RelationType.SUPPORTS, 0.9))
    repo.add_link(Link(evidence_complaints.state_id, unreliable.state_id, RelationType.SUPPORTS, 0.6))
    repo.add_link(Link(evidence_on_time.state_id, unreliable.state_id, RelationType.CONTRADICTS, 0.4))

    repo.add_constraint(
        Constraint(
            name="reliable_memory_requires_late_rate_below_20_percent",
            constraint_type="memory_consistency",
            scope_type="state_type",
            scope_ref="memory_hypothesis",
            hard=False,
            weight=1.0,
            predicate=lambda state: not (
                state.data.get("claim") == "supplier A is reliable"
                and float(state.data.get("late_delivery_rate", 1.0)) > 0.20
            ),
        )
    )

    scorer = SCEScoringEngine(repo)
    scorer.compute_stability(reliable)
    scorer.compute_stability(unreliable)

    candidates = [reliable, unreliable]
    selected = max(candidates, key=lambda state: state.stability)
    explanation = SCEExplainer(repo).explain_comparison([state.state_id for state in candidates])

    return {
        "scenario": "conflicting_memory",
        "question": "Which memory state is more stable under current evidence?",
        "candidates": [
            {
                "claim": state.data["claim"],
                "late_delivery_rate": state.data["late_delivery_rate"],
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
