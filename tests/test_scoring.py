from sce.core.scoring import SCEScoringEngine
from sce.core.types import Link, RelationType, State
from sce.storage.memory import MemoryRepository


def test_supporting_links_increase_coherence():
    repo = MemoryRepository()
    target = State(state_type="hypothesis", data={"claim": "X"})
    support = State(state_type="evidence", data={"evidence": "Y"})
    repo.add_state(target)
    repo.add_state(support)
    repo.add_link(Link(support.state_id, target.state_id, RelationType.SUPPORTS, 1.0))
    scorer = SCEScoringEngine(repo)
    assert scorer.compute_coherence(target) > 0.5
