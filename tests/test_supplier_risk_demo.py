from __future__ import annotations

from sce.scenarios.supplier_risk_demo import format_supplier_risk_demo, run_supplier_risk_demo


def test_supplier_risk_demo_tells_complete_story():
    result = run_supplier_risk_demo()

    assert result["first_choice"] == "supplier_risk_plan"
    assert result["final_choice"] == "escalation_plan"
    assert result["changed_choice"] is True
    assert "supplier_risk" in result["backbone_nodes"]
    assert "marketing_tag" in result["dangling_nodes"]
    assert result["reliability"] > 0.5
    assert result["remembered_episodes"] == 3


def test_supplier_risk_demo_pretty_output_is_simple():
    rendered = format_supplier_risk_demo(run_supplier_risk_demo())

    assert "SCE Supplier Risk Demo" in rendered
    assert "Decide. Explain. Improve." in rendered
    assert "1) Decide" in rendered
    assert "2) Explain" in rendered
    assert "3) Measure reliability" in rendered
    assert "4) Improve" in rendered
    assert "Changed choice: YES" in rendered
