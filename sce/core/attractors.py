from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol

from sce.core.types import Attractor, State


@dataclass(frozen=True)
class AttractorDetectionConfig:
    """Configuration for deterministic attractor detection."""

    window_size: int = 3
    stability_threshold: float = 0.5
    max_stability_delta: float = 0.05


class AttractorDetector(Protocol):
    """Interface for detecting stable regions in an evolution trace."""

    def detect(self, trace: List[State]) -> Optional[Attractor]:
        ...


class FixedPointAttractorDetector:
    """Detect simple fixed-point-like attractors in recent state history.

    This detector is intentionally conservative. It identifies an attractor when
    the most recent states share the same type and signature context, have
    sufficiently high average stability, and show low stability drift.
    """

    def __init__(self, config: Optional[AttractorDetectionConfig] = None) -> None:
        self.config = config or AttractorDetectionConfig()

    def detect(self, trace: List[State]) -> Optional[Attractor]:
        window_size = self.config.window_size
        if len(trace) < window_size:
            return None

        recent = trace[-window_size:]
        last = recent[-1]

        if not self._same_signature_context(recent):
            return None

        stability_values = [state.stability for state in recent]
        avg_stability = sum(stability_values) / len(stability_values)
        if avg_stability < self.config.stability_threshold:
            return None

        stability_delta = max(stability_values) - min(stability_values)
        if stability_delta > self.config.max_stability_delta:
            return None

        signature = self._signature(last)
        return Attractor(
            attractor_type=last.state_type,
            signature_hash=signature,
            invariant={
                "state_type": last.state_type,
                "supplier_id": last.data.get("supplier_id"),
                "category": last.data.get("category"),
                "entity": last.data.get("entity"),
                "claim": last.data.get("claim"),
            },
            member_state_ids=[state.state_id for state in recent],
            stability_score=avg_stability,
            meta={
                "detector": "FixedPointAttractorDetector",
                "window_size": window_size,
                "stability_delta": stability_delta,
            },
        )

    def _same_signature_context(self, states: List[State]) -> bool:
        signatures = {self._signature(state) for state in states}
        return len(signatures) == 1

    def _signature(self, state: State) -> str:
        return ":".join(
            [
                state.state_type,
                str(state.data.get("supplier_id") or ""),
                str(state.data.get("category") or ""),
                str(state.data.get("entity") or ""),
                str(state.data.get("claim") or ""),
            ]
        )
