from __future__ import annotations

from sce.core.backbone import DecisionBackboneExtractor


def run_decision_backbone_demo() -> dict:
    """Demonstrate decision-carrying vs dangling reasoning graph branches."""

    graph = {
        "late_delivery": ["supplier_risk"],
        "invoice_risk": ["supplier_risk"],
        "missing_certificate": ["supplier_risk"],
        "supplier_risk": ["escalate"],
        "old_positive_history": ["context_note"],
        "context_note": [],
        "marketing_tag": ["unrelated_note"],
        "unrelated_note": [],
    }
    sources = {
        "late_delivery",
        "invoice_risk",
        "missing_certificate",
        "old_positive_history",
        "marketing_tag",
    }
    targets = {"escalate"}

    result = DecisionBackboneExtractor().extract(graph, sources=sources, targets=targets)

    return {
        "graph": graph,
        "sources": sorted(result.sources),
        "targets": sorted(result.targets),
        "backbone_nodes": sorted(result.backbone_nodes),
        "dangling_nodes": sorted(result.dangling_nodes),
        "unreachable_targets": sorted(result.unreachable_targets),
        "has_backbone": result.has_backbone,
        "explanation": (
            "Backbone nodes are reachable from evidence and can reach the decision target. "
            "Dangling nodes are connected to the reasoning graph but do not carry the decision."
        ),
    }


def format_decision_backbone_demo(result: dict) -> str:
    def bullet(items: list[str]) -> list[str]:
        return [f"- {item}" for item in items] or ["- none"]

    graph_lines = []
    for node, neighbors in result["graph"].items():
        if neighbors:
            graph_lines.append(f"- {node} -> {', '.join(neighbors)}")
        else:
            graph_lines.append(f"- {node} -> ∅")

    return "\n".join(
        [
            "SCE Decision Backbone Demo",
            "==========================",
            "",
            "Reasoning graph",
            "---------------",
            *graph_lines,
            "",
            "Sources / evidence",
            "------------------",
            *bullet(result["sources"]),
            "",
            "Targets / decisions",
            "-------------------",
            *bullet(result["targets"]),
            "",
            "Decision backbone",
            "-----------------",
            *bullet(result["backbone_nodes"]),
            "",
            "Dangling branches",
            "-----------------",
            *bullet(result["dangling_nodes"]),
            "",
            "Unreachable targets",
            "-------------------",
            *bullet(result["unreachable_targets"]),
            "",
            f"Has decision backbone: {result['has_backbone']}",
            "",
            "Interpretation",
            "--------------",
            result["explanation"],
        ]
    )
