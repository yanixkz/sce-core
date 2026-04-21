from __future__ import annotations

from typing import Dict, List


def _node_label(node: dict) -> str:
    star = "⭐" if node.get("is_attractor") else ""
    status = "✓" if node.get("constraints_satisfied") else "✗"
    return f"[{node['state_type']}] (stab={node['stability']:.2f}) {status} {star}".strip()


def render_ascii_graph(graph: Dict[str, List[dict]]) -> str:
    nodes = {n["state_id"]: n for n in graph.get("nodes", [])}
    edges = graph.get("edges", [])

    outgoing = {}
    for e in edges:
        outgoing.setdefault(e["source_state_id"], []).append(e)

    lines: List[str] = []

    for node_id, node in nodes.items():
        lines.append(_node_label(node))

        for edge in outgoing.get(node_id, []):
            target = nodes.get(edge["target_state_id"])
            if not target:
                continue
            rel = edge.get("relation_type")
            strength = edge.get("strength", 0.0)
            lines.append(
                f"  └── {rel} ({strength:.2f}) → {_node_label(target)}"
            )

        lines.append("")

    return "\n".join(lines)
