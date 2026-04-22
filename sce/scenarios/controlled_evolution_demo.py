from __future__ import annotations

from sce.core.evolution_control import EvolutionErrorTracker


def run_controlled_evolution_demo() -> dict:
    """Demonstrate local prediction errors becoming trajectory reliability."""

    tracker = EvolutionErrorTracker()
    tracker.record_step("score_supplier_risk", predicted_value=0.90, actual_value=0.72)
    tracker.record_step("select_escalation_plan", predicted_value=0.78, actual_value=0.70)
    tracker.record_step("execute_followup", predicted_value=0.74, actual_value=0.73)
    report = tracker.report()

    return {
        "steps": [
            {
                "name": step.name,
                "predicted_value": step.predicted_value,
                "actual_value": step.actual_value,
                "weight": step.weight,
                "error": step.error,
            }
            for step in report.steps
        ],
        "cumulative_error": report.cumulative_error,
        "mean_error": report.mean_error,
        "reliability": report.reliability,
        "trend": report.trend,
        "is_reliable": report.is_reliable,
        "explanation": (
            "Controlled evolution tracks how local prediction errors accumulate across a decision trajectory. "
            "Lower accumulated error means the agent's stepwise evolution is more reliable."
        ),
    }


def format_controlled_evolution_demo(result: dict) -> str:
    lines = [
        "SCE Controlled Evolution Demo",
        "=============================",
        "",
        "Step errors",
        "-----------",
        "step                         predicted   actual   error",
        "-------------------------------------------------------",
    ]
    for step in result["steps"]:
        lines.append(
            f"{step['name']:<28} "
            f"{step['predicted_value']:>8.2f}   "
            f"{step['actual_value']:>6.2f}   "
            f"{step['error']:>5.2f}"
        )

    lines.extend(
        [
            "",
            "Trajectory report",
            "-----------------",
            f"cumulative_error: {result['cumulative_error']:.2f}",
            f"mean_error:       {result['mean_error']:.2f}",
            f"reliability:      {result['reliability']:.2f}",
            f"trend:            {result['trend']}",
            f"is_reliable:      {result['is_reliable']}",
            "",
            "Interpretation",
            "--------------",
            result["explanation"],
        ]
    )
    return "\n".join(lines)
