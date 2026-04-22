from __future__ import annotations

from sce.core.backbone import DecisionBackboneExtractor


def test_decision_backbone_extracts_source_to_target_nodes():
    graph = {
        "late_delivery": ["supplier_risk"],
        "invoice_risk": ["supplier_risk"],
        "supplier_risk": ["escalate"],
        "marketing_tag": ["unrelated_note"],
        "unrelated_note": [],
    }

    result = DecisionBackboneExtractor().extract(
        graph,
        sources={"late_delivery", "invoice_risk", "marketing_tag"},
        targets={"escalate"},
    )

    assert result.has_backbone is True
    assert result.backbone_nodes == {
        "late_delivery",
        "invoice_risk",
        "supplier_risk",
        "escalate",
    }
    assert result.dangling_nodes == {"marketing_tag", "unrelated_note"}
    assert result.unreachable_targets == set()


def test_decision_backbone_reports_unreachable_targets():
    graph = {
        "evidence": ["intermediate"],
        "intermediate": [],
        "decision": [],
    }

    result = DecisionBackboneExtractor().extract(
        graph,
        sources={"evidence"},
        targets={"decision"},
    )

    assert result.has_backbone is False
    assert result.backbone_nodes == set()
    assert result.dangling_nodes == {"evidence", "intermediate"}
    assert result.unreachable_targets == {"decision"}


def test_decision_backbone_handles_missing_source_and_target_nodes():
    result = DecisionBackboneExtractor().extract(
        graph={},
        sources={"source"},
        targets={"target"},
    )

    assert result.backbone_nodes == set()
    assert result.dangling_nodes == {"source"}
    assert result.unreachable_targets == {"target"}
