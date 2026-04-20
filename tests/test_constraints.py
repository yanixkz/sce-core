from sce.core.evolution import SCEEvolver
from sce.core.scoring import SCEScoringEngine
from sce.core.types import State
from sce.scenarios.supplier_reliability import make_supplier_reliability_scenario


def test_hard_constraint_blocks_invalid_state():
    repo, _ = make_supplier_reliability_scenario()
    scorer = SCEScoringEngine(repo)
    evolver = SCEEvolver(repo, scorer)

    invalid_state = State(
        state_type="supplier_reliability_hypothesis",
        data={"supplier_id": "A", "category": "X", "late_delivery_rate": 0.35},
    )
    assert evolver.admissible_state(invalid_state) is False
