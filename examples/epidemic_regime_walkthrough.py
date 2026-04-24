from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.epidemic_regime_demo import run_epidemic_regime_demo


def _format_candidate_table(result: dict) -> str:
    lines = [
        "regime                    transmission overload  cost    stability  rank",
        "-----------------------------------------------------------------------",
    ]
    by_name = {candidate["name"]: candidate for candidate in result["candidates"]}
    for score_row in result["scores"]:
        candidate = by_name[score_row["state"]]
        lines.append(
            f"{candidate['name']:<24} {candidate['transmission_pressure']:>8.3f} "
            f"{candidate['overload_pressure']:>8.3f} {candidate['intervention_cost']:>7.3f} "
            f"{score_row['stability']:>10.3f} {score_row['rank']:>5d}"
        )
    return "\n".join(lines)


def build_walkthrough_report() -> str:
    baseline = run_epidemic_regime_demo()
    stressed = run_epidemic_regime_demo(transmission_multiplier=1.1, healthcare_capacity_multiplier=0.95)

    return "\n".join(
        [
            "# Epidemic Regime Walkthrough (CDS)",
            "",
            "## A) Scientific question",
            baseline["research_question"],
            "",
            "## B) Toy-model disclaimer",
            baseline["disclaimer"],
            "",
            "## C) CDS mapping",
            "- I: susceptible/infected/recovered fractions + spread indicators.",
            "- E: healthcare capacity and recovery support.",
            "- C: capacity, transmission, and intervention-cost constraints.",
            "- t: deterministic transition from initial regime to candidate regimes.",
            "- Stab: weighted SCE stability score.",
            "- S: selected stable epidemic regime.",
            "",
            "## D) Baseline deterministic run",
            f"Initial state: {baseline['initial_state']}",
            "",
            _format_candidate_table(baseline),
            "",
            f"Selected regime: {baseline['selected_regime']['name']}",
            f"Why selected: {baseline['stability_explanation']}",
            "",
            "## E) Sensitivity check",
            "Change: transmission_multiplier = 1.10, healthcare_capacity_multiplier = 0.95.",
            _format_candidate_table(stressed),
            "",
            (
                f"Baseline winner: {baseline['selected_regime']['name']} "
                f"(stability {baseline['selected_regime']['stability']:.3f})"
            ),
            (
                f"Stressed winner: {stressed['selected_regime']['name']} "
                f"(stability {stressed['selected_regime']['stability']:.3f})"
            ),
            "Interpretation: ranking remains deterministic; tighter capacity increases overload penalties.",
        ]
    )


if __name__ == "__main__":
    print(build_walkthrough_report())
