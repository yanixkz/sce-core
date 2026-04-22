from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean


@dataclass(frozen=True)
class EvolutionStep:
    """Observed quality of one predicted decision/evolution step."""

    name: str
    predicted_value: float
    actual_value: float
    weight: float = 1.0

    @property
    def error(self) -> float:
        return abs(self.predicted_value - self.actual_value) * self.weight


@dataclass(frozen=True)
class EvolutionControlReport:
    """Aggregate error and reliability report for a decision trajectory."""

    steps: list[EvolutionStep]
    cumulative_error: float
    mean_error: float
    reliability: float
    trend: str

    @property
    def is_reliable(self) -> bool:
        return self.reliability >= 0.5


class EvolutionErrorTracker:
    """Track local step error and derive trajectory-level reliability.

    SCE decisions evolve through repeated small steps: plan, score, execute,
    observe, learn. This tracker measures how well predicted step values match
    observed values and turns accumulated error into a simple reliability score.
    """

    def __init__(self) -> None:
        self._steps: list[EvolutionStep] = []

    @property
    def steps(self) -> list[EvolutionStep]:
        return list(self._steps)

    def record_step(
        self,
        name: str,
        predicted_value: float,
        actual_value: float,
        weight: float = 1.0,
    ) -> EvolutionStep:
        if weight < 0:
            raise ValueError("weight must be non-negative")
        step = EvolutionStep(
            name=name,
            predicted_value=float(predicted_value),
            actual_value=float(actual_value),
            weight=float(weight),
        )
        self._steps.append(step)
        return step

    def report(self) -> EvolutionControlReport:
        if not self._steps:
            return EvolutionControlReport(
                steps=[],
                cumulative_error=0.0,
                mean_error=0.0,
                reliability=1.0,
                trend="empty",
            )

        errors = [step.error for step in self._steps]
        cumulative_error = sum(errors)
        mean_error = mean(errors)
        reliability = 1.0 / (1.0 + cumulative_error)

        return EvolutionControlReport(
            steps=self.steps,
            cumulative_error=cumulative_error,
            mean_error=mean_error,
            reliability=reliability,
            trend=self._trend(errors),
        )

    def _trend(self, errors: list[float]) -> str:
        if len(errors) < 2:
            return "insufficient_data"
        if errors[-1] < errors[0]:
            return "improving"
        if errors[-1] > errors[0]:
            return "worsening"
        return "flat"
