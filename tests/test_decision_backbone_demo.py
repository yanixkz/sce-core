from __future__ import annotations

from sce.scenarios.decision_backbone_demo import (
    format_decision_backbone_demo,
    run_decision_backbone_demo,
)


def test_decision_backbone_demo_finds_supplier_risk_backbone():
    result = run_decision_backbone_demo()

    assert result["has_backbone"] is True
    assert result["targets"] == ["escalate"]
    assert set(result["backbone_nodes"]) == {
        "late_delivery",
        "invoice_risk",
        "missing_certificate",
        "supplier_risk",
        "escalate",
    }
    assert set(result["dangling_nodes"]) == {
        "old_positive_history",
        "context_note",
        "marketing_tag",
        "unrelated_note",
    }
    assert result["unreachable_targets"] == []


def test_decision_backbone_demo_pretty_output_is_readable():
    rendered = format_decision_backbone_demo(run_decision_backbone_demo())

    assert "SCE Decision Backbone Demo" in rendered
    assert "Reasoning graph" in rendered
    assert "Decision backbone" in rendered
    assert "Dangling branches" in rendered
    assert "supplier_risk" in rendered
    assert "marketing_tag" in rendered
