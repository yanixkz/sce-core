from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from sce.core.types import State


@dataclass(frozen=True)
class Goal:
    """A target condition for an SCE agent loop."""

    name: str
    score_fn: Callable[[State], float]
    threshold: float = 0.8
    description: Optional[str] = None

    def score(self, state: State) -> float:
        value = float(self.score_fn(state))
        return max(0.0, min(1.0, value))

    def is_satisfied(self, state: State) -> bool:
        return self.score(state) >= self.threshold
