from __future__ import annotations

from sce.core.types import ScoringWeights

DEFAULT_CONSTRAINT_VALUES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
DEFAULT_WEIGHTS = ScoringWeights()


def compute_constraint_sweep_stability(
    *,
    coherence: float,
    entropy: float,
    support: float,
    conflict: float,
    cost: float,
    constraint_strength: float,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> float:
    """Compute CDS stability while sweeping conflict and cost pressure."""
    stability = (
        weights.coherence * coherence
        - weights.entropy * entropy
        + weights.support * support
        - constraint_strength * (weights.conflict * conflict + weights.cost * cost)
    )
    return round(stability, 4)


def generate_constraint_sweep_population() -> list[dict]:
    """Return a deterministic toy population with transparent score dimensions."""
    return [
        {
            "id": 1,
            "label": "Candidate A",
            "coherence": 0.78,
            "entropy": 0.15,
            "support": 0.30,
            "conflict": 0.50,
            "cost": 0.60,
        },
        {
            "id": 2,
            "label": "Candidate B",
            "coherence": 0.70,
            "entropy": 0.10,
            "support": 0.2667,
            "conflict": 0.25,
            "cost": 0.40,
        },
        {
            "id": 3,
            "label": "Candidate C",
            "coherence": 0.64,
            "entropy": 0.10,
            "support": 0.20,
            "conflict": 0.125,
            "cost": 0.10,
        },
        {
            "id": 4,
            "label": "Candidate D",
            "coherence": 0.55,
            "entropy": 0.10,
            "support": 0.1833,
            "conflict": 0.00,
            "cost": 0.04,
        },
        {
            "id": 5,
            "label": "Candidate E",
            "coherence": 0.46,
            "entropy": 0.18,
            "support": 0.22,
            "conflict": 0.08,
            "cost": 0.12,
        },
    ]


def rank_population_for_constraint(candidates: list[dict], constraint_strength: float) -> list[dict]:
    ranked: list[dict] = []
    for candidate in candidates:
        scored = dict(candidate)
        scored["constraint_strength"] = round(constraint_strength, 1)
        scored["stability"] = compute_constraint_sweep_stability(
            coherence=candidate["coherence"],
            entropy=candidate["entropy"],
            support=candidate["support"],
            conflict=candidate["conflict"],
            cost=candidate["cost"],
            constraint_strength=constraint_strength,
        )
        ranked.append(scored)
    ranked.sort(key=lambda item: (-item["stability"], item["id"]))
    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank
    return ranked


def detect_winner_transitions(winner_history: list[dict]) -> list[dict]:
    transitions: list[dict] = []
    previous = winner_history[0]
    for current in winner_history[1:]:
        if current["winner"] != previous["winner"]:
            transitions.append(
                {
                    "constraint_strength": current["constraint_strength"],
                    "from": previous["winner"],
                    "to": current["winner"],
                }
            )
        previous = current
    return transitions


def render_constraint_sweep_ascii(winner_history: list[dict]) -> str:
    lines = ["Constraint", ""]
    lines.extend(
        f"{step['constraint_strength']:.1f} | {step['winner'].removeprefix('Candidate ')}"
        for step in winner_history
    )
    return "\n".join(lines)


def run_constraint_sweep_demo(
    constraint_values: tuple[float, ...] = DEFAULT_CONSTRAINT_VALUES,
) -> dict:
    population = generate_constraint_sweep_population()
    sweep_steps = []
    winner_history = []
    ranking_history = []

    for constraint_strength in constraint_values:
        rounded_strength = round(constraint_strength, 1)
        ranking = rank_population_for_constraint(population, rounded_strength)
        winner = ranking[0]
        sweep_steps.append(
            {
                "constraint_strength": rounded_strength,
                "winner": winner["label"],
                "winner_score": winner["stability"],
            }
        )
        winner_history.append(
            {
                "constraint_strength": rounded_strength,
                "winner": winner["label"],
            }
        )
        ranking_history.append(
            {
                "constraint_strength": rounded_strength,
                "ranking": ranking,
            }
        )

    return {
        "demo": "constraint-sweep",
        "question": "How does selection change as constraints change?",
        "population": population,
        "sweep_steps": sweep_steps,
        "winner_history": winner_history,
        "winner_transitions": detect_winner_transitions(winner_history),
        "constraint_values": [round(value, 1) for value in constraint_values],
        "ranking_history": ranking_history,
        "ascii_visualization": render_constraint_sweep_ascii(winner_history),
        "pipeline": ["Possibility Space", "Constraint Change", "Selection Change"],
    }


def format_constraint_sweep_demo(result: dict) -> str:
    transition_lines = [
        f"{transition['constraint_strength']:.1f} -> {transition['from']} -> {transition['to']}"
        for transition in result["winner_transitions"]
    ]
    return "\n".join(
        [
            "Constraint Sweep Explorer",
            "===========================",
            "",
            "Possibility Space -> Constraint Change -> Selection Change",
            "A deterministic toy model; not a prediction system, economics model, biology model, or intelligence claim.",
            "",
            "Core question: How does selection change as constraints change?",
            "",
            "Sweep Winners",
            "-------------",
            *[
                f"Constraint = {step['constraint_strength']:.1f} | Winner = {step['winner']} | Stability = {step['winner_score']:.4f}"
                for step in result["sweep_steps"]
            ],
            "",
            "Winner transitions",
            "------------------",
            *(transition_lines or ["No winner transitions detected."]),
            "",
            "ASCII visualization",
            "-------------------",
            result["ascii_visualization"],
        ]
    )
