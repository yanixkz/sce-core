from __future__ import annotations

from statistics import median

from sce.core.types import ScoringWeights

DEFAULT_POPULATION_SIZE = 32
DEFAULT_WEIGHTS = ScoringWeights()


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_stability_score(
    *,
    coherence: float,
    entropy: float,
    support: float,
    conflict: float,
    cost: float,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> float:
    """Compute the CDS weighted stability score used by the core scorer."""
    stability = (
        weights.coherence * coherence
        - weights.cost * cost
        - weights.conflict * conflict
        - weights.entropy * entropy
        + weights.support * support
    )
    return round(stability, 4)


def generate_candidate_population(population_size: int = DEFAULT_POPULATION_SIZE) -> list[dict]:
    """Generate a deterministic toy population with transparent scoring dimensions."""
    candidates: list[dict] = []
    for index in range(1, population_size + 1):
        coherence = _clamp(0.22 + (((index * 37) % 71) / 100))
        entropy = _clamp(0.08 + (((index * 19 + 11) % 61) / 100))
        support = _clamp(0.18 + (((index * 29 + 7) % 73) / 100))
        conflict = _clamp(0.04 + (((index * 13 + 5) % 47) / 100))
        cost = _clamp(0.03 + (((index * 17 + 3) % 43) / 100))
        stability = compute_stability_score(
            coherence=coherence,
            entropy=entropy,
            support=support,
            conflict=conflict,
            cost=cost,
        )
        candidates.append(
            {
                "id": index,
                "label": f"Candidate {index}",
                "coherence": round(coherence, 4),
                "entropy": round(entropy, 4),
                "support": round(support, 4),
                "conflict": round(conflict, 4),
                "cost": round(cost, 4),
                "stability": stability,
            }
        )
    return candidates


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """Return candidates ranked by descending stability with deterministic tie-breaks."""
    ranked = sorted(candidates, key=lambda item: (-item["stability"], item["id"]))
    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank
    return ranked


def build_stability_distribution(candidates: list[dict], bucket_size: float = 0.10) -> list[dict]:
    """Build a simple histogram over stability scores for CLI visualization."""
    buckets: list[dict] = []
    bucket_count = int(1.0 / bucket_size) + 1
    for offset in range(bucket_count):
        upper = round(1.0 - (offset * bucket_size), 2)
        lower = round(upper - bucket_size, 2)
        if offset == bucket_count - 1:
            lower = float("-inf")
        count = sum(1 for candidate in candidates if lower < candidate["stability"] <= upper)
        buckets.append(
            {
                "bucket": f"{upper:.2f}",
                "lower_exclusive": lower,
                "upper_inclusive": upper,
                "count": count,
            }
        )
    return buckets


def render_ascii_distribution(distribution: list[dict]) -> str:
    return "\n".join(f"{bucket['bucket']} | {'*' * bucket['count']}" for bucket in distribution)


def run_selection_landscape_demo(population_size: int = DEFAULT_POPULATION_SIZE) -> dict:
    population = generate_candidate_population(population_size)
    ranked = rank_candidates(population)
    median_stability = median(candidate["stability"] for candidate in ranked)
    median_candidate = min(
        ranked, key=lambda item: (abs(item["stability"] - median_stability), item["rank"])
    )
    distribution = build_stability_distribution(ranked)
    return {
        "demo": "selection-landscape",
        "population_size": len(ranked),
        "best_candidate": ranked[0],
        "worst_candidate": ranked[-1],
        "median_candidate": median_candidate,
        "top_candidates": ranked[:5],
        "worst_candidates": list(reversed(ranked[-5:])),
        "stability_distribution": distribution,
        "ascii_visualization": render_ascii_distribution(distribution),
        "ranking": ranked,
        "pipeline": ["Possibility Space", "Scoring Dimensions", "Stability Landscape", "Selection"],
    }


def _format_candidate(candidate: dict) -> str:
    return (
        f"{candidate['label']}\n"
        f"Stability = {candidate['stability']:.4f}\n"
        f"coherence={candidate['coherence']:.2f} entropy={candidate['entropy']:.2f} "
        f"support={candidate['support']:.2f} conflict={candidate['conflict']:.2f} cost={candidate['cost']:.2f}"
    )


def format_selection_landscape_demo(result: dict) -> str:
    return "\n".join(
        [
            "Selection Landscape Explorer",
            "============================",
            "",
            "Possibility Space -> Scoring Dimensions -> Stability Landscape -> Selection",
            "A deterministic toy model; not a prediction system or intelligence claim.",
            "",
            f"Population Size: {result['population_size']}",
            "",
            "Top Candidates",
            "--------------",
            *[_format_candidate(candidate) for candidate in result["top_candidates"]],
            "",
            "Worst Candidates",
            "----------------",
            *[_format_candidate(candidate) for candidate in result["worst_candidates"]],
            "",
            "Best Candidate",
            "--------------",
            _format_candidate(result["best_candidate"]),
            "",
            "Median Candidate",
            "----------------",
            _format_candidate(result["median_candidate"]),
            "",
            "Worst Candidate",
            "---------------",
            _format_candidate(result["worst_candidate"]),
            "",
            "Stability Distribution",
            "----------------------",
            result["ascii_visualization"],
        ]
    )
