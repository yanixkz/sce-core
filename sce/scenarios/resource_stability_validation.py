from __future__ import annotations


def _select_expected_regime(*, pressure: float, regeneration_gap: float) -> tuple[str, str, str]:
    if pressure >= 1.12 and regeneration_gap >= 0.08:
        return (
            "strict_austerity",
            "unstable",
            "High pressure and weak regeneration imply a constrained regime is expected.",
        )
    if pressure <= 0.78 and regeneration_gap <= 0.0:
        return (
            "balanced_regeneration",
            "stable",
            "Low pressure with regeneration keeping pace supports a balanced carrying regime.",
        )
    if regeneration_gap >= 0.12:
        return (
            "strict_austerity",
            "constrained",
            "Regeneration falls well below consumption, so a conservation-heavy regime is expected.",
        )
    if pressure >= 1.0:
        return (
            "strict_austerity",
            "pressured",
            "Pressure at or above the limit suggests selecting the lower-demand regime.",
        )
    if pressure >= 0.9:
        return (
            "balanced_regeneration",
            "balanced",
            "Moderate pressure with manageable regeneration gap favors the balanced regime.",
        )
    return (
        "balanced_regeneration",
        "stable",
        "Pressure remains below hard limits, so the balanced regime is expected.",
    )


def evaluate_resource_stability_heuristic(
    *,
    population_multiplier: float,
    consumption_rate_multiplier: float,
    regeneration_rate_multiplier: float,
) -> dict:
    """Return a deterministic, transparent heuristic expectation for resource-stability cases."""
    pressure = population_multiplier * consumption_rate_multiplier
    regeneration_gap = consumption_rate_multiplier - regeneration_rate_multiplier
    expected_regime, expected_class, reason = _select_expected_regime(
        pressure=pressure,
        regeneration_gap=regeneration_gap,
    )
    return {
        "expected_regime": expected_regime,
        "expected_class": expected_class,
        "agreement_key": expected_regime,
        "heuristic_reason": reason,
        "heuristic_pressure": round(pressure, 4),
        "heuristic_regeneration_gap": round(regeneration_gap, 4),
    }


def build_resource_stability_validation_rows(rows: list[dict]) -> list[dict]:
    results: list[dict] = []
    for row in rows:
        heuristic = evaluate_resource_stability_heuristic(
            population_multiplier=row["population_multiplier"],
            consumption_rate_multiplier=row["consumption_rate_multiplier"],
            regeneration_rate_multiplier=row["regeneration_rate_multiplier"],
        )
        agreement = row["selected_regime"] == heuristic["agreement_key"]
        results.append(
            {
                **row,
                "heuristic_expected_regime": heuristic["expected_regime"],
                "heuristic_expected_class": heuristic["expected_class"],
                "heuristic_reason": heuristic["heuristic_reason"],
                "heuristic_pressure": heuristic["heuristic_pressure"],
                "heuristic_regeneration_gap": heuristic["heuristic_regeneration_gap"],
                "agreement": agreement,
            }
        )
    return results
