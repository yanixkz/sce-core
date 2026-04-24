from __future__ import annotations

from dataclasses import dataclass

from sce.core.scoring import SCEScoringEngine
from sce.core.types import Constraint, Link, RelationType, ScoringWeights, State
from sce.storage.memory import MemoryRepository


@dataclass(frozen=True)
class EpidemicCandidate:
    name: str
    susceptible_fraction: float
    infected_fraction: float
    recovered_fraction: float
    transmission_pressure: float
    recovery_support: float
    healthcare_capacity: float
    intervention_cost: float
    support: float
    conflict: float
    entropy: float
    coherence_hint: float


def _build_candidate_state(candidate: EpidemicCandidate) -> State:
    overload_pressure = candidate.infected_fraction / max(candidate.healthcare_capacity, 0.01)
    instability = (
        0.45 * candidate.transmission_pressure
        + 0.35 * overload_pressure
        + 0.20 * candidate.intervention_cost
    )
    return State(
        state_type="epidemic_regime",
        data={
            "name": candidate.name,
            "susceptible_fraction": candidate.susceptible_fraction,
            "infected_fraction": candidate.infected_fraction,
            "recovered_fraction": candidate.recovered_fraction,
            "transmission_pressure": round(candidate.transmission_pressure, 4),
            "recovery_support": round(candidate.recovery_support, 4),
            "healthcare_capacity": round(candidate.healthcare_capacity, 4),
            "intervention_cost": round(candidate.intervention_cost, 4),
            "overload_pressure": round(overload_pressure, 4),
            "instability": round(instability, 4),
        },
        entropy=candidate.entropy,
        conflict=candidate.conflict,
        support=candidate.support,
        coherence=candidate.coherence_hint,
    )


def _candidate_row(state: State, stability: float) -> dict:
    return {
        "name": state.data["name"],
        "susceptible_fraction": state.data["susceptible_fraction"],
        "infected_fraction": state.data["infected_fraction"],
        "recovered_fraction": state.data["recovered_fraction"],
        "transmission_pressure": state.data["transmission_pressure"],
        "recovery_support": state.data["recovery_support"],
        "healthcare_capacity": state.data["healthcare_capacity"],
        "intervention_cost": state.data["intervention_cost"],
        "overload_pressure": state.data["overload_pressure"],
        "instability": state.data["instability"],
        "support": round(state.support, 4),
        "conflict": round(state.conflict, 4),
        "entropy": round(state.entropy, 4),
        "coherence": round(state.coherence, 4),
        "stability": round(stability, 4),
    }


def _apply_candidate_multipliers(
    candidate: EpidemicCandidate,
    *,
    transmission_multiplier: float,
    recovery_support_multiplier: float,
    healthcare_capacity_multiplier: float,
    intervention_cost_multiplier: float,
) -> EpidemicCandidate:
    return EpidemicCandidate(
        name=candidate.name,
        susceptible_fraction=candidate.susceptible_fraction,
        infected_fraction=candidate.infected_fraction,
        recovered_fraction=candidate.recovered_fraction,
        transmission_pressure=round(candidate.transmission_pressure * transmission_multiplier, 4),
        recovery_support=round(candidate.recovery_support * recovery_support_multiplier, 4),
        healthcare_capacity=round(candidate.healthcare_capacity * healthcare_capacity_multiplier, 4),
        intervention_cost=round(candidate.intervention_cost * intervention_cost_multiplier, 4),
        support=candidate.support,
        conflict=candidate.conflict,
        entropy=candidate.entropy,
        coherence_hint=candidate.coherence_hint,
    )


def run_epidemic_regime_demo(
    *,
    transmission_multiplier: float = 1.0,
    recovery_support_multiplier: float = 1.0,
    healthcare_capacity_multiplier: float = 1.0,
    intervention_cost_multiplier: float = 1.0,
) -> dict:
    """
    Deterministic toy scenario: select an epidemic regime that is stable under explicit constraints.
    This is not a validated epidemiology simulator.
    """
    repo = MemoryRepository()
    scorer = SCEScoringEngine(
        repo,
        weights=ScoringWeights(coherence=0.95, cost=0.2, conflict=0.9, entropy=0.45, support=0.7),
    )

    repo.add_constraint(
        Constraint(
            name="capacity_guardrail",
            predicate=lambda state: state.data["overload_pressure"] <= 1.0,
            constraint_type="healthcare_limit",
            hard=True,
            weight=1.35,
        )
    )
    repo.add_constraint(
        Constraint(
            name="transmission_control",
            predicate=lambda state: state.data["transmission_pressure"] <= 0.7,
            constraint_type="spread_control",
            hard=False,
            weight=0.8,
        )
    )
    repo.add_constraint(
        Constraint(
            name="intervention_affordability",
            predicate=lambda state: state.data["intervention_cost"] <= 0.55,
            constraint_type="cost_bound",
            hard=False,
            weight=0.65,
        )
    )

    initial_candidate = EpidemicCandidate(
        name="escalating_wave_start",
        susceptible_fraction=0.72,
        infected_fraction=0.18,
        recovered_fraction=0.10,
        transmission_pressure=0.92,
        recovery_support=0.38,
        healthcare_capacity=0.16,
        intervention_cost=0.22,
        support=0.24,
        conflict=0.86,
        entropy=0.36,
        coherence_hint=0.22,
    )

    candidate_inputs = [
        EpidemicCandidate(
            name="uncontrolled_spread",
            susceptible_fraction=0.67,
            infected_fraction=0.24,
            recovered_fraction=0.09,
            transmission_pressure=0.96,
            recovery_support=0.32,
            healthcare_capacity=0.17,
            intervention_cost=0.18,
            support=0.22,
            conflict=0.88,
            entropy=0.39,
            coherence_hint=0.20,
        ),
        EpidemicCandidate(
            name="managed_containment",
            susceptible_fraction=0.69,
            infected_fraction=0.11,
            recovered_fraction=0.20,
            transmission_pressure=0.58,
            recovery_support=0.72,
            healthcare_capacity=0.19,
            intervention_cost=0.44,
            support=0.73,
            conflict=0.19,
            entropy=0.12,
            coherence_hint=0.78,
        ),
        EpidemicCandidate(
            name="overload_risk",
            susceptible_fraction=0.64,
            infected_fraction=0.20,
            recovered_fraction=0.16,
            transmission_pressure=0.78,
            recovery_support=0.49,
            healthcare_capacity=0.15,
            intervention_cost=0.35,
            support=0.40,
            conflict=0.62,
            entropy=0.30,
            coherence_hint=0.42,
        ),
        EpidemicCandidate(
            name="recovery_dominant",
            susceptible_fraction=0.50,
            infected_fraction=0.07,
            recovered_fraction=0.43,
            transmission_pressure=0.47,
            recovery_support=0.84,
            healthcare_capacity=0.20,
            intervention_cost=0.52,
            support=0.79,
            conflict=0.14,
            entropy=0.10,
            coherence_hint=0.83,
        ),
        EpidemicCandidate(
            name="suppressed_low_activity",
            susceptible_fraction=0.78,
            infected_fraction=0.04,
            recovered_fraction=0.18,
            transmission_pressure=0.29,
            recovery_support=0.63,
            healthcare_capacity=0.18,
            intervention_cost=0.61,
            support=0.64,
            conflict=0.18,
            entropy=0.11,
            coherence_hint=0.76,
        ),
    ]

    initial_candidate = _apply_candidate_multipliers(
        initial_candidate,
        transmission_multiplier=transmission_multiplier,
        recovery_support_multiplier=recovery_support_multiplier,
        healthcare_capacity_multiplier=healthcare_capacity_multiplier,
        intervention_cost_multiplier=intervention_cost_multiplier,
    )
    candidate_inputs = [
        _apply_candidate_multipliers(
            candidate,
            transmission_multiplier=transmission_multiplier,
            recovery_support_multiplier=recovery_support_multiplier,
            healthcare_capacity_multiplier=healthcare_capacity_multiplier,
            intervention_cost_multiplier=intervention_cost_multiplier,
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

        if state.data["overload_pressure"] > 1.0:
            relation = RelationType.CONTRADICTS
            strength = min(1.0, state.data["overload_pressure"] - 0.6)
        elif state.data["transmission_pressure"] <= 0.7:
            relation = RelationType.SUPPORTS
            strength = max(0.2, 0.9 - state.data["transmission_pressure"])
        else:
            relation = RelationType.RELATED
            strength = 0.35

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
    capacity_stressed = [state.data["name"] for state in candidate_states if state.data["overload_pressure"] > 1.0]

    return {
        "research_question": "Which epidemic regime remains most stable under spread, capacity, and intervention constraints?",
        "initial_state": _candidate_row(initial_state, scorer.compute_stability(initial_state)),
        "candidates": [_candidate_row(item["state"], item["stability"]) for item in scored],
        "selected_regime": _candidate_row(selected, scored[0]["stability"]),
        "scores": [
            {"state": item["state"].data["name"], "stability": round(item["stability"], 4), "rank": idx + 1}
            for idx, item in enumerate(scored)
        ],
        "stability_explanation": (
            "The selected regime stays below healthcare overload and spread-control thresholds while preserving "
            "higher support and lower conflict, which yields a better CDS stability score."
        ),
        "constraints": [
            {
                "name": "capacity_guardrail",
                "type": "hard",
                "rule": "overload_pressure <= 1.0",
                "effect": "rejects regimes that push infected load beyond healthcare capacity",
            },
            {
                "name": "transmission_control",
                "type": "soft",
                "rule": "transmission_pressure <= 0.7",
                "effect": "penalizes regimes with persistent high spread pressure",
            },
            {
                "name": "intervention_affordability",
                "type": "soft",
                "rule": "intervention_cost <= 0.55",
                "effect": "penalizes regimes that stabilize only via unsustainably high intervention cost",
            },
        ],
        "next_research_actions": [
            "Sweep transmission and capacity multipliers to map overload boundaries.",
            "Add age-structure or contact heterogeneity as an additional constrained state dimension.",
            "Compare deterministic regime ranking against a simple compartment baseline for sanity checks.",
        ],
        "capacity_stressed_regimes": capacity_stressed,
        "formula_reference": "S = Stab(D(I, E, C, t))",
        "parameters": {
            "transmission_multiplier": transmission_multiplier,
            "recovery_support_multiplier": recovery_support_multiplier,
            "healthcare_capacity_multiplier": healthcare_capacity_multiplier,
            "intervention_cost_multiplier": intervention_cost_multiplier,
        },
        "disclaimer": "Toy scientific scenario only; not a validated epidemiology simulator.",
    }


def format_epidemic_regime_demo(result: dict) -> str:
    winner = result["selected_regime"]
    rows = [
        "regime                    transmission overload  cost    stability",
        "---------------------------------------------------------------",
    ]
    for item in result["scores"]:
        candidate = next(c for c in result["candidates"] if c["name"] == item["state"])
        rows.append(
            f"{item['state']:<24} {candidate['transmission_pressure']:>8.3f} "
            f"{candidate['overload_pressure']:>8.3f} {candidate['intervention_cost']:>7.3f} {item['stability']:>10.3f}"
        )

    return "\n".join(
        [
            "SCE Epidemic Regime Stability Demo",
            "===================================",
            "",
            "Toy scientific scenario only (deterministic and inspectable; not a validated epidemiology simulator).",
            "",
            "Research question",
            "-----------------",
            result["research_question"],
            "",
            "1) Initial epidemic regime",
            "---------------------------",
            (
                f"{result['initial_state']['name']}: infected {result['initial_state']['infected_fraction']:.3f}, "
                f"transmission {result['initial_state']['transmission_pressure']:.3f}, "
                f"overload {result['initial_state']['overload_pressure']:.3f}, "
                f"stability {result['initial_state']['stability']:.3f}"
            ),
            "",
            "2) Candidate regimes and ranking",
            "---------------------------------",
            *rows,
            "",
            "Selected stable epidemic regime",
            "--------------------------------",
            (
                f"{winner['name']} (infected {winner['infected_fraction']:.3f}, "
                f"transmission {winner['transmission_pressure']:.3f}, "
                f"overload {winner['overload_pressure']:.3f}, stability {winner['stability']:.3f})"
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
            "Capacity-stressed regimes",
            "-------------------------",
            *([f"- {name}" for name in result["capacity_stressed_regimes"]] or ["- none"]),
            "",
            "Next research actions",
            "---------------------",
            *[f"- {action}" for action in result["next_research_actions"]],
        ]
    )
