from __future__ import annotations

PERTURBATIONS = (0.01, 0.05, 0.10, 0.20, 0.30)
STABILITY_THRESHOLD = 0.0

_CANDIDATES = (
    {
        "id": "A",
        "label": "Candidate A",
        "load": 0.90,
        "capacity": 1.00,
        "coherence": 0.82,
        "support": 0.70,
        "entropy": 0.10,
        "conflict": 0.08,
    },
    {
        "id": "B",
        "label": "Candidate B",
        "load": 0.80,
        "capacity": 1.00,
        "coherence": 0.68,
        "support": 0.55,
        "entropy": 0.18,
        "conflict": 0.10,
    },
    {
        "id": "C",
        "label": "Candidate C",
        "load": 1.05,
        "capacity": 1.00,
        "coherence": 0.76,
        "support": 0.62,
        "entropy": 0.14,
        "conflict": 0.22,
    },
)


def _stability_score(candidate: dict, perturbation: float = 0.0) -> float:
    perturbed_load = candidate["load"] * (1.0 + perturbation)
    margin = candidate["capacity"] - perturbed_load
    score = (
        candidate["coherence"]
        + (0.5 * candidate["support"])
        + margin
        - (0.4 * candidate["entropy"])
        - (0.5 * candidate["conflict"])
    )
    if margin < 0.0:
        score -= 1.0 + abs(margin)
    return round(score, 4)


def _candidate_row(candidate: dict) -> dict:
    stability = _stability_score(candidate)
    return {
        **candidate,
        "load_ratio": round(candidate["load"] / candidate["capacity"], 4),
        "stability": stability,
        "stable": stability >= STABILITY_THRESHOLD and candidate["load"] <= candidate["capacity"],
    }


def _perturb_candidate(candidate: dict, perturbation: float) -> dict:
    perturbed_load = round(candidate["load"] * (1.0 + perturbation), 4)
    load_ratio = round(perturbed_load / candidate["capacity"], 4)
    stability = _stability_score(candidate, perturbation)
    stable = stability >= STABILITY_THRESHOLD and load_ratio <= 1.0
    return {
        "perturbation": perturbation,
        "perturbation_percent": int(round(perturbation * 100)),
        "load": perturbed_load,
        "load_ratio": load_ratio,
        "stability": stability,
        "stable": stable,
        "stable_label": "Yes" if stable else "No",
    }


def render_stability_basin_ascii(perturbation_results: list[dict]) -> str:
    stable_count = sum(1 for item in perturbation_results if item["stable"])
    unstable_count = len(perturbation_results) - stable_count
    return "\n".join(
        [
            "Stable",
            "█" * (stable_count * 5),
            "",
            "Unstable",
            "█" * unstable_count,
        ]
    )


def run_stability_basin_demo(perturbations: tuple[float, ...] = PERTURBATIONS) -> dict:
    candidates = sorted(
        (_candidate_row(candidate) for candidate in _CANDIDATES),
        key=lambda item: (-item["stability"], item["id"]),
    )
    selected = candidates[0]
    perturbation_results = [_perturb_candidate(selected, perturbation) for perturbation in perturbations]
    stable_percentages = [item["perturbation_percent"] for item in perturbation_results if item["stable"]]
    basin_size = max(stable_percentages, default=0)
    return {
        "demo": "stability-basin",
        "model": "deterministic toy model only; not a physical law or real-world prediction",
        "question": "How much perturbation can a structure absorb before losing stability?",
        "pipeline": ["Selection", "Persistence", "Robustness"],
        "candidates": candidates,
        "selected_candidate": selected,
        "perturbations": perturbation_results,
        "stability_basin_size_percent": basin_size,
        "metric": "Stability Basin Size = largest tested perturbation that remains stable",
        "ascii_visualization": render_stability_basin_ascii(perturbation_results),
    }


def format_stability_basin_demo(result: dict) -> str:
    selected = result["selected_candidate"]
    rows = ["Perturbation  Stable?", "---------------------"]
    rows.extend(
        f"{item['perturbation_percent']:>3}%          {item['stable_label']}"
        for item in result["perturbations"]
    )
    return "\n".join(
        [
            "Stability Basin",
            "================",
            "",
            "Selection -> Persistence -> Robustness",
            "Deterministic toy model only; not a physical law or real-world prediction.",
            "",
            f"Core question: {result['question']}",
            "",
            "Selected candidate",
            "------------------",
            (
                f"{selected['label']} (baseline stability {selected['stability']:.4f}, "
                f"load ratio {selected['load_ratio']:.2f})"
            ),
            "",
            "Perturbation results",
            "--------------------",
            *rows,
            "",
            f"Stability Basin Size: {result['stability_basin_size_percent']}%",
            "",
            "ASCII",
            "-----",
            result["ascii_visualization"],
        ]
    )
