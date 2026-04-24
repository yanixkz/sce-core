from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.resource_stability_demo import run_resource_stability_demo


def _format_candidate_table(result: dict) -> str:
    lines = [
        "name                  pressure  overshoot  stability  rank",
        "------------------------------------------------------------",
    ]
    by_name = {candidate["name"]: candidate for candidate in result["candidates"]}
    for score_row in result["scores"]:
        candidate = by_name[score_row["state"]]
        lines.append(
            f"{candidate['name']:<21} {candidate['pressure']:>8.3f}   "
            f"{candidate['overshoot']:>8.3f}   {score_row['stability']:>8.3f}   {score_row['rank']:>4d}"
        )
    return "\n".join(lines)


def build_walkthrough_report() -> str:
    baseline = run_resource_stability_demo()
    sensitivity = run_resource_stability_demo(consumption_rate_multiplier=1.12)

    return "\n".join(
        [
            "# Resource Stability Walkthrough (CDS)",
            "",
            "## A) Scientific question",
            baseline["research_question"],
            "",
            "## B) CDS mapping",
            "- I (state information): population, available_resources, consumption_rate, regeneration_rate.",
            "- E (capacity): available_resources and regeneration ability.",
            "- C (constraints): hard pressure <= 1.0, soft regeneration >= 0.9 * consumption.",
            "- t (evolution steps): initial regime -> candidate regime transitions.",
            "- Stab (scoring): SCE weighted stability score over coherence/support/conflict/entropy under constraints.",
            "- S (selected regime): highest-ranked viable candidate.",
            "",
            "## C) Run the real scenario",
            "- Source function: `sce.scenarios.resource_stability_demo.run_resource_stability_demo()`.",
            "- Baseline parameters: population x1.0, consumption x1.0, regeneration x1.0.",
            "",
            "## D) Inspect candidate states",
            f"Initial state: {baseline['initial_state']}",
            "",
            _format_candidate_table(baseline),
            "",
            f"Selected state: {baseline['selected_state']['name']}",
            f"Why selected: {baseline['stability_explanation']}",
            "",
            "## E) Interpret the result",
            "- Stability improves when pressure stays below the hard bound and overshoot is removed.",
            "- Regeneration floor influences ranking by penalizing depletion dynamics.",
            f"- Remaining instability: {', '.join(baseline['non_carrying_regimes']) or 'none'}.",
            "- Next research actions:",
            *[f"  - {action}" for action in baseline["next_research_actions"]],
            "",
            "## F) One-parameter sensitivity: higher consumption pressure",
            "Scenario change: consumption_rate_multiplier = 1.12 (12% higher demand).",
            _format_candidate_table(sensitivity),
            "",
            (
                f"Baseline winner: {baseline['selected_state']['name']} "
                f"(stability {baseline['selected_state']['stability']:.3f})"
            ),
            (
                f"Sensitivity winner: {sensitivity['selected_state']['name']} "
                f"(stability {sensitivity['selected_state']['stability']:.3f})"
            ),
            "Interpretation: the ranking remains but margins tighten as pressure and overshoot penalties increase.",
        ]
    )


if __name__ == "__main__":
    print(build_walkthrough_report())
