from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DecisionBackbone:
    """Decision-carrying and dangling parts of a directed reasoning graph."""

    sources: set[str]
    targets: set[str]
    backbone_nodes: set[str]
    dangling_nodes: set[str]
    unreachable_targets: set[str]

    @property
    def has_backbone(self) -> bool:
        return bool(self.backbone_nodes & self.targets)


class DecisionBackboneExtractor:
    """Extract the source-to-target backbone from a directed graph.

    The graph is represented as adjacency mapping:

        {"evidence": ["state"], "state": ["decision"]}

    Nodes in the backbone are reachable from at least one source and can reach
    at least one target. Reachable nodes that cannot reach a target are treated
    as dangling decision branches.
    """

    def extract(
        self,
        graph: dict[str, Iterable[str]],
        sources: Iterable[str],
        targets: Iterable[str],
    ) -> DecisionBackbone:
        source_set = set(sources)
        target_set = set(targets)
        normalized = self._normalize_graph(graph, source_set, target_set)
        reverse = self._reverse_graph(normalized)

        forward = self._reachable(normalized, source_set)
        backward = self._reachable(reverse, target_set)

        backbone_nodes = forward & backward
        dangling_nodes = forward - backbone_nodes
        unreachable_targets = target_set - forward

        return DecisionBackbone(
            sources=source_set,
            targets=target_set,
            backbone_nodes=backbone_nodes,
            dangling_nodes=dangling_nodes,
            unreachable_targets=unreachable_targets,
        )

    def _normalize_graph(
        self,
        graph: dict[str, Iterable[str]],
        sources: set[str],
        targets: set[str],
    ) -> dict[str, set[str]]:
        normalized: dict[str, set[str]] = defaultdict(set)
        for node, neighbors in graph.items():
            normalized[node].update(neighbors)
            for neighbor in neighbors:
                normalized.setdefault(neighbor, set())
        for node in sources | targets:
            normalized.setdefault(node, set())
        return dict(normalized)

    def _reverse_graph(self, graph: dict[str, set[str]]) -> dict[str, set[str]]:
        reverse: dict[str, set[str]] = {node: set() for node in graph}
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                reverse.setdefault(neighbor, set()).add(node)
        return reverse

    def _reachable(self, graph: dict[str, set[str]], start_nodes: set[str]) -> set[str]:
        visited: set[str] = set()
        queue: deque[str] = deque(start_nodes)

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            queue.extend(graph.get(node, set()) - visited)

        return visited
