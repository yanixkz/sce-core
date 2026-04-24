from __future__ import annotations

from dataclasses import dataclass

from sce.core.scoring import SCEScoringEngine
from sce.core.types import Constraint, Link, RelationType, ScoringWeights, State
from sce.storage.memory import MemoryRepository


@dataclass(frozen=True)
class ResourceCandidate:
    name: str
    population: float
    available_resources: float
    consumption_rate: float
    regeneration_rate: float
    support: float
    conflict: float
    entropy: float
    coherence_hint: float
    monitoring_signal: str


def _build_candidate_state(candidate: ResourceCandidate) -> State:
    pressure = (candidate.population * candidate.consumption_rate) / max(candidate.available_resources, 1.0)
    overshoot = max(0.0, pressure - 1.0)
    return State(
        state_type="resource_regime",
        data={
            "name": candidate.name,
            "population": candidate.population,
            "available_resources": candidate.available_resources,
            "consumption_rate": candidate.consumption_rate,
            "regeneration_rate": candidate.regeneration_rate,
            "pressure": round(pressure, 4),
            "overshoot": round(overshoot, 4),
            "monitoring_signal": candidate.monitoring_signal,
        },
        entropy=candidate.entropy,
        conflict=candidate.conflict,
        support=candidate.support,
        coherence=candidate.coherence_hint,
    )


def _regime_row(state: State, stability: float) -> dict:
    return {
        "name": state.data["name"],
        "population": state.data["population"],
        "available_resources": state.data["available_resources"],
        "consumption_rate": state.data["consumption_rate"],
        "regeneration_rate": state.data["regeneration_rate"],
        "pressure": state.data["pressure"],
        "overshoot": state.data["overshoot"],
        "support": round(state.support, 4),
        "conflict": round(state.conflict, 4),
        "entropy": round(state.entropy, 4),
        "coherence": round(state.coherence, 4),
        "stability": round(stability, 4),
    }


def _apply_candidate_multipliers(
    candidate: ResourceCandidate,
    *,
    population_multiplier: float,
    consumption_rate_multiplier: float,
    regeneration_rate_multiplier: float,
) -> ResourceCandidate:
    return ResourceCandidate(
        name=candidate.name,
        population=round(candidate.population * population_multiplier, 4),
        available_resources=candidate.available_resources,
        consumption_rate=round(candidate.consumption_rate * consumption_rate_multiplier, 4),
        regeneration_rate=round(candidate.regeneration_rate * regeneration_rate_multiplier, 4),
        support=candidate.support,
        conflict=candidate.conflict,
        entropy=candidate.entropy,
        coherence_hint=candidate.coherence_hint,
        monitoring_signal=candidate.monitoring_signal,
    )


def run_resource_stability_demo(
    *,
    population_multiplier: float = 1.0,
    consumption_rate_multiplier: float = 1.0,
    regeneration_rate_multiplier: float = 1.0,
) -> dict:
    """
    Research-facing toy model for constraint-driven stability in population/resource dynamics.

    Optional multipliers allow lightweight parameter sensitivity experiments without changing
    the default CLI/API behavior.
    """
    repo = MemoryRepository()
    scorer = SCEScoringEngine(
        repo,
        weights=ScoringWeights(coherence=0.9, cost=0.15, conflict=0.9, entropy=0.4, support=0.75),
    )

    repo.add_constraint(
        Constraint(
            name="resource_balance",
            predicate=lambda state: state.data["pressure"] <= 1.0,
            constraint_type="resource_limit",
            hard=True,
            weight=1.3,
        )
    )
    repo.add_constraint(
        Constraint(
            name="regeneration_floor",
            predicate=lambda state: state.data["regeneration_rate"] >= 0.9 * state.data["consumption_rate"],
            constraint_type="renewal_limit",
            hard=False,
            weight=0.7,
        )
    )

    initial_candidate = ResourceCandidate(
        name="overshoot_start",
        population=180.0,
        available_resources=120.0,
        consumption_rate=0.95,
        regeneration_rate=0.55,
        support=0.2,
        conflict=0.9,
        entropy=0.35,
        coherence_hint=0.2,
        monitoring_signal="low",
    )
    candidate_inputs = [
        ResourceCandidate(
            name="strict_austerity",
            population=105.0,
            available_resources=130.0,
            consumption_rate=0.68,
            regeneration_rate=0.72,
            support=0.44,
            conflict=0.2,
            entropy=0.18,
            coherence_hint=0.52,
            monitoring_signal="",
        ),
        ResourceCandidate(
            name="balanced_regeneration",
            population=120.0,
            available_resources=150.0,
            consumption_rate=0.72,
            regeneration_rate=0.83,
            support=0.72,
            conflict=0.12,
            entropy=0.1,
            coherence_hint=0.74,
            monitoring_signal="strong",
        ),
        ResourceCandidate(
            name="fragile_growth",
            population=145.0,
            available_resources=132.0,
            consumption_rate=0.9,
            regeneration_rate=0.64,
            support=0.32,
            conflict=0.66,
            entropy=0.3,
            coherence_hint=0.38,
            monitoring_signal="",
        ),
    ]

    initial_candidate = _apply_candidate_multipliers(
        initial_candidate,
        population_multiplier=population_multiplier,
        consumption_rate_multiplier=consumption_rate_multiplier,
        regeneration_rate_multiplier=regeneration_rate_multiplier,
    )
    candidate_inputs = [
        _apply_candidate_multipliers(
            candidate,
            population_multiplier=population_multiplier,
            consumption_rate_multiplier=consumption_rate_multiplier,
            regeneration_rate_multiplier=regeneration_rate_multiplier,
        )
        for candidate in candidate_inputs
    ]

    initial_state = _build_candidate_state(initial_candidate)
    repo.add_state(initial_state)

    candidate_states: list[State] = []
    for candidate in candidate_inputs:
        state = _build_candidate_state(candidate)
        repo.add_state(state)
        candidate_states.append(state)
        if state.data["overshoot"] > 0.0:
            relation = RelationType.CONTRADICTS
            strength = min(1.0, state.data["overshoot"] + 0.25)
        else:
            relation = RelationType.SUPPORTS
            strength = max(0.2, state.data["regeneration_rate"] - state.data["consumption_rate"])
        repo.add_link(
            Link(
                source_state_id=initial_state.state_id,
                target_state_id=state.state_id,
                relation_type=relation,
                strength=round(strength, 3),
            )
        )

    scored = []
    for state in candidate_states:
        stability = scorer.compute_stability(state, transition_cost=0.0, trace=[initial_state, state])
        scored.append({"state": state, "stability": stability})
    scored.sort(key=lambda item: item["stability"], reverse=True)

    selected = scored[0]["state"]
    failing_candidates = [
        state.data["name"]
        for state in candidate_states
        if state.data["pressure"] > 1.0 or state.data["regeneration_rate"] < 0.9 * state.data["consumption_rate"]
    ]

    return {
        "research_question": "Which population-resource regime remains viable under explicit resource constraints?",
        "initial_state": _regime_row(initial_state, scorer.compute_stability(initial_state)),
        "candidates": [_regime_row(item["state"], item["stability"]) for item in scored],
        "selected_state": _regime_row(selected, scored[0]["stability"]),
        "scores": [
            {"state": item["state"].data["name"], "stability": round(item["stability"], 4), "rank": idx + 1}
            for idx, item in enumerate(scored)
        ],
        "stability_explanation": (
            "The selected regime keeps pressure below the hard resource limit and keeps regeneration close "
            "to consumption, producing low conflict and higher support under the CDS scoring profile."
        ),
        "constraints": [
            {
                "name": "resource_balance",
                "type": "hard",
                "rule": "pressure <= 1.0",
                "effect": "rejects persistent overshoot trajectories",
            },
            {
                "name": "regeneration_floor",
                "type": "soft",
                "rule": "regeneration_rate >= 0.9 * consumption_rate",
                "effect": "penalizes regimes that deplete resources faster than recovery",
            },
        ],
        "next_research_actions": [
            "Sweep regeneration and consumption ratios to map viability boundaries.",
            "Add a second interacting population to test coupled-constraint behavior.",
            "Compare this toy scoring trend against a classic logistic-resource baseline.",
        ],
        "non_carrying_regimes": failing_candidates,
        "formula_reference": "S = Stab(D(I, E, C, t))",
        "parameters": {
            "population_multiplier": population_multiplier,
            "consumption_rate_multiplier": consumption_rate_multiplier,
            "regeneration_rate_multiplier": regeneration_rate_multiplier,
        },
    }


def format_resource_stability_demo(result: dict) -> str:
    winner = result["selected_state"]
    rows = [
        "state                   pressure  overshoot  stability",
        "------------------------------------------------------",
    ]
    for item in result["scores"]:
        candidate = next(c for c in result["candidates"] if c["name"] == item["state"])
        rows.append(
            f"{item['state']:<22} {candidate['pressure']:>8.3f}   {candidate['overshoot']:>8.3f}   {item['stability']:>8.3f}"
        )

    return "\n".join(
        [
            "SCE Resource Stability Demo",
            "===========================",
            "",
            "Scientific showcase: constraint-driven stability as a computational workflow.",
            "",
            "Research question",
            "-----------------",
            result["research_question"],
            "",
            "1) Initial unstable regime",
            "--------------------------",
            (
                f"{result['initial_state']['name']}: pressure {result['initial_state']['pressure']:.3f}, "
                f"overshoot {result['initial_state']['overshoot']:.3f}, "
                f"stability {result['initial_state']['stability']:.3f}"
            ),
            "",
            "2) Candidate regimes and ranking",
            "---------------------------------",
            *rows,
            "",
            "Selected stable regime",
            "----------------------",
            (
                f"{winner['name']} (pressure {winner['pressure']:.3f}, "
                f"regeneration {winner['regeneration_rate']:.3f}, stability {winner['stability']:.3f})"
            ),
            "",
            "3) Constraint effects",
            "---------------------",
            *[
                f"- {item['name']} [{item['type']}]: {item['rule']} → {item['effect']}"
                for item in result["constraints"]
            ],
            "",
            "Stability explanation",
            "---------------------",
            result["stability_explanation"],
            "",
            "Still unstable / non-carrying regimes",
            "-------------------------------------",
            *([f"- {name}" for name in result["non_carrying_regimes"]] or ["- none"]),
            "",
            "Next research actions",
            "---------------------",
            *[f"- {action}" for action in result["next_research_actions"]],
        ]
    )
