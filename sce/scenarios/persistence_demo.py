from __future__ import annotations

TOTAL_STEPS = 100

# Survival lengths are intentionally fixed to make the toy model transparent and
# deterministic. Candidate A survives all t0..t100 evaluations; other candidates
# are eliminated at their configured survival horizon.
_CANDIDATE_SPECS = (
    {"id": "A", "label": "Candidate A", "base_stability": 0.99, "decay": 0.0000, "survival_steps": 100},
    {"id": "B", "label": "Candidate B", "base_stability": 0.92, "decay": 0.0025, "survival_steps": 84},
    {"id": "C", "label": "Candidate C", "base_stability": 0.74, "decay": 0.0060, "survival_steps": 35},
    {"id": "D", "label": "Candidate D", "base_stability": 0.55, "decay": 0.0180, "survival_steps": 7},
)


def _stability_at_step(candidate: dict, step: int) -> float:
    pressure = step / TOTAL_STEPS
    return round(max(0.0, candidate["base_stability"] - (candidate["decay"] * step) - (0.02 * pressure)), 4)


def _candidate_trace(candidate: dict, total_steps: int = TOTAL_STEPS) -> dict:
    survival_steps = min(candidate["survival_steps"], total_steps)
    trace = []
    for step in range(total_steps + 1):
        survived = step <= survival_steps
        trace.append(
            {
                "time": f"t{step}",
                "step": step,
                "stability": _stability_at_step(candidate, step) if survived else 0.0,
                "survived": survived,
                "eliminated": not survived,
            }
        )
    elimination_step = None if survival_steps == total_steps else survival_steps + 1
    return {
        "id": candidate["id"],
        "label": candidate["label"],
        "survival_steps": survival_steps,
        "total_steps": total_steps,
        "persistence_score": round(survival_steps / total_steps, 2),
        "elimination_step": elimination_step,
        "status": "survived" if elimination_step is None else "eliminated",
        "trace": trace,
    }


def render_persistence_bar(score: float, width: int = 10) -> str:
    filled = int(score * width)
    if score > 0 and filled == 0:
        filled = 1
    return "█" * filled


def run_persistence_demo(total_steps: int = TOTAL_STEPS) -> dict:
    candidates = [_candidate_trace(candidate, total_steps) for candidate in _CANDIDATE_SPECS]
    return {
        "demo": "persistence",
        "model": "deterministic toy model only; not a real-world prediction system",
        "total_steps": total_steps,
        "environmental_pressure": "linear deterministic pressure applied from t0 through t100",
        "metric": "Persistence Score = survival_steps / total_steps",
        "pipeline": ["Selection", "Persistence", "Survival Duration"],
        "candidates": candidates,
        "scores": {candidate["label"]: candidate["persistence_score"] for candidate in candidates},
        "ascii_visualization": render_persistence_ascii(candidates),
    }


def render_persistence_ascii(candidates: list[dict]) -> str:
    return "\n".join(
        f"{candidate['id']} {render_persistence_bar(candidate['persistence_score'])}"
        for candidate in candidates
    )


def format_persistence_demo(result: dict) -> str:
    score_lines = [
        f"{candidate['label']} = {candidate['persistence_score']:.2f}"
        for candidate in result["candidates"]
    ]
    return "\n".join(
        [
            "Persistence Over Time",
            "=====================",
            "",
            "Selection -> Persistence -> Survival Duration",
            "Deterministic toy model only; not a real-world prediction system.",
            "",
            f"Time Steps: t0..t{result['total_steps']}",
            "Environmental Pressure: deterministic linear pressure each step",
            "Metric: Persistence Score = survival_steps / total_steps",
            "",
            "Persistence Scores",
            "------------------",
            *score_lines,
            "",
            "ASCII",
            "-----",
            result["ascii_visualization"],
            "",
            "Survival / Elimination",
            "----------------------",
            *[
                f"{candidate['label']}: {candidate['status']}"
                + (" through final step" if candidate["elimination_step"] is None else f" at t{candidate['elimination_step']}")
                for candidate in result["candidates"]
            ],
        ]
    )
