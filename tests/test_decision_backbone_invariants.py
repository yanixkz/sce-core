from __future__ import annotations

from collections import deque

from sce.core.backbone import DecisionBackboneExtractor
from sce.scenarios.decision_backbone_demo import run_decision_backbone_demo


def _reachable(graph: dict[str, set[str]], starts: set[str]) -> set[str]:
    visited: set[str] = set()
    queue: deque[str] = deque(starts)
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(graph.get(node, set()) - visited)
    return visited


def test_backbone_equals_forward_backward_intersection_and_dangling_is_forward_minus_backbone():
    graph = {
        "fact_a": ["hypothesis"],
        "fact_b": ["hypothesis"],
        "hypothesis": ["decision"],
        "fact_noise": ["note"],
        "note": [],
    }
    sources = {"fact_a", "fact_b", "fact_noise"}
    targets = {"decision"}

    result = DecisionBackboneExtractor().extract(graph, sources=sources, targets=targets)

    normalized = {node: set(neighbors) for node, neighbors in graph.items()}
    normalized.update({"decision": set()})
    reverse = {node: set() for node in normalized}
    for node, neighbors in normalized.items():
        for neighbor in neighbors:
            reverse.setdefault(neighbor, set()).add(node)

    forward = _reachable(normalized, sources)
    backward = _reachable(reverse, targets)

    assert result.backbone_nodes == forward & backward
    assert result.dangling_nodes == forward - result.backbone_nodes
    assert result.backbone_nodes.isdisjoint(result.dangling_nodes)


def test_demo_backbone_contains_only_decision_carrying_nodes_and_excludes_dangling():
    result = run_decision_backbone_demo()

    backbone = set(result["backbone_nodes"])
    dangling = set(result["dangling_nodes"])

    assert {"supplier_risk", "escalate"}.issubset(backbone)
    assert {"marketing_tag", "unrelated_note"}.issubset(dangling)
    assert backbone.isdisjoint(dangling)
