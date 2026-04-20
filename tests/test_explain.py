from sce.core.explain import SCEExplainer
from sce.core.scoring import SCEScoringEngine
from sce.scenarios.supplier_reliability import make_supplier_reliability_scenario


def test_explain_state_contains_metrics():
    repo, start_state = make_supplier_reliability_scenario()
    scorer = SCEScoringEngine(repo)
    scorer.compute_stability(start_state)
    explainer = SCEExplainer(repo)
    explanation = explainer.explain_state(start_state.state_id)
    assert "metrics" in explanation
    assert "active_constraints" in explanation
