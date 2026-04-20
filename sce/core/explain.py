from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from sce.core.types import RelationType
from sce.storage.memory import MemoryRepository


class SCEExplainer:
    def __init__(self, repo: MemoryRepository) -> None:
        self.repo = repo

    def explain_state(self, state_id: UUID) -> Dict[str, Any]:
        state = self.repo.get_state(state_id)
        incoming = self.repo.incoming_links(state_id)
        supporting_links = [
            link
            for link in incoming
            if link.relation_type
            in {RelationType.SUPPORTS, RelationType.RESONATES_WITH, RelationType.DERIVED_FROM, RelationType.SIMILAR_TO}
        ]
        contradicting_links = [link for link in incoming if link.relation_type == RelationType.CONTRADICTS]

        active_constraints = []
        violated_constraints = []
        for constraint in self.repo.constraints.values():
            if constraint.applies_to(state):
                active_constraints.append(constraint.name)
                if not constraint.is_satisfied(state):
                    violated_constraints.append(constraint.name)

        return {
            "state_id": str(state.state_id),
            "state_type": state.state_type,
            "status": state.status,
            "data": state.data,
            "metrics": {
                "coherence": state.coherence,
                "conflict": state.conflict,
                "entropy": state.entropy,
                "support": state.support,
                "stability": state.stability,
            },
            "active_constraints": active_constraints,
            "violated_constraints": violated_constraints,
            "supporting_links": [
                {"from": str(link.source_state_id), "relation": link.relation_type.value, "strength": link.strength}
                for link in supporting_links
            ],
            "contradicting_links": [
                {"from": str(link.source_state_id), "relation": link.relation_type.value, "strength": link.strength}
                for link in contradicting_links
            ],
        }
