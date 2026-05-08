from __future__ import annotations

EPIDEMIC_REGIME_LABELS = frozenset(
    {
        "uncontrolled_spread",
        "overload_risk",
        "managed_containment",
        "suppressed_low_activity",
        "recovery_dominant",
    }
)


def _select_expected_regime(
    *,
    transmission_multiplier: float,
    recovery_support_multiplier: float,
    healthcare_capacity_multiplier: float,
    pressure_index: float,
    capacity_gap: float,
    recovery_balance: float,
    intervention_burden: float,
) -> tuple[str, str, str]:
    """Map compact diagnostics to one existing epidemic-regime candidate label."""
    if pressure_index >= 1.25 and capacity_gap >= 0.2 and recovery_balance <= -0.1:
        return (
            "overload_risk",
            "pressured",
            "Transmission pressure materially exceeds effective capacity while recovery support lags.",
        )
    if transmission_multiplier >= 1.12 and recovery_support_multiplier <= 0.95:
        return (
            "uncontrolled_spread",
            "unstable",
            "Elevated transmission plus weak recovery support points to spread escalation risk.",
        )
    if transmission_multiplier <= 0.82:
        return (
            "suppressed_low_activity",
            "low_activity",
            "Low activity pressure makes the suppressed low-activity regime the transparent heuristic expectation.",
        )
    if transmission_multiplier <= 0.92 and recovery_support_multiplier >= 1.08:
        return (
            "recovery_dominant",
            "stable",
            "Lower transmission with stronger recovery support favors recovery-led dynamics.",
        )
    if (
        transmission_multiplier >= 1.05
        and recovery_support_multiplier >= 1.05
        and healthcare_capacity_multiplier >= 1.0
        and intervention_burden <= 1.1
    ):
        return (
            "managed_containment",
            "managed",
            "Higher transmission is partly offset by recovery support and available capacity.",
        )
    if intervention_burden >= 1.15:
        return (
            "managed_containment",
            "cost_constrained",
            "High intervention burden penalizes stricter suppression in this coarse heuristic.",
        )
    if recovery_balance >= 0.12:
        return (
            "recovery_dominant",
            "stable",
            "Recovery support exceeds transmission pressure enough to favor recovery dominance.",
        )
    return (
        "managed_containment",
        "managed",
        "Pressure and support are mixed, so containment is the conservative expected regime.",
    )


def evaluate_epidemic_regime_heuristic(
    *,
    transmission_multiplier: float,
    recovery_support_multiplier: float,
    healthcare_capacity_multiplier: float,
    intervention_cost_multiplier: float,
) -> dict:
    """Return a deterministic heuristic expectation for epidemic-regime CSV cases.

    The result is an early behavioral sanity-check baseline only; it is not
    epidemiological validation and is not a ground-truth label.
    """
    pressure_index = transmission_multiplier / max(healthcare_capacity_multiplier, 0.01)
    capacity_gap = transmission_multiplier - healthcare_capacity_multiplier
    recovery_balance = recovery_support_multiplier - transmission_multiplier
    intervention_burden = intervention_cost_multiplier
    expected_regime, expected_class, reason = _select_expected_regime(
        transmission_multiplier=transmission_multiplier,
        recovery_support_multiplier=recovery_support_multiplier,
        healthcare_capacity_multiplier=healthcare_capacity_multiplier,
        pressure_index=pressure_index,
        capacity_gap=capacity_gap,
        recovery_balance=recovery_balance,
        intervention_burden=intervention_burden,
    )

    return {
        "expected_regime": expected_regime,
        "expected_class": expected_class,
        "agreement_key": expected_regime,
        "heuristic_reason": reason,
        "pressure_index": round(pressure_index, 4),
        "capacity_gap": round(capacity_gap, 4),
        "recovery_balance": round(recovery_balance, 4),
        "intervention_burden": round(intervention_burden, 4),
    }


def build_epidemic_regime_validation_rows(rows: list[dict]) -> list[dict]:
    results: list[dict] = []
    for row in rows:
        heuristic = evaluate_epidemic_regime_heuristic(
            transmission_multiplier=row["transmission_multiplier"],
            recovery_support_multiplier=row["recovery_support_multiplier"],
            healthcare_capacity_multiplier=row["healthcare_capacity_multiplier"],
            intervention_cost_multiplier=row["intervention_cost_multiplier"],
        )
        agreement = row["selected_regime"] == heuristic["agreement_key"]
        results.append(
            {
                **row,
                "heuristic_expected_regime": heuristic["expected_regime"],
                "heuristic_expected_class": heuristic["expected_class"],
                "heuristic_reason": heuristic["heuristic_reason"],
                "pressure_index": heuristic["pressure_index"],
                "capacity_gap": heuristic["capacity_gap"],
                "recovery_balance": heuristic["recovery_balance"],
                "intervention_burden": heuristic["intervention_burden"],
                "agreement": agreement,
            }
        )
    return results
