from sce.core.evolution import SCEEvolver
from sce.core.scoring import SCEScoringEngine
from sce.scenarios.supplier_reliability import make_supplier_reliability_scenario


def test_evolution_returns_trace():
    repo, start_state = make_supplier_reliability_scenario()
    scorer = SCEScoringEngine(repo)
    evolver = SCEEvolver(repo, scorer)
    result = evolver.evolve(start_state, max_steps=3)
    assert len(result.trace) >= 1
    assert result.final_state is not None
