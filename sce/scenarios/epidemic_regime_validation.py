from __future__ import annotations


def evaluate_epidemic_regime_heuristic(
    *,
    transmission_multiplier: float,
    recovery_support_multiplier: float,
    healthcare_capacity_multiplier: float,
    intervention_cost_multiplier: float,
) -> dict:
    """Return a deterministic heuristic expectation for epidemic-regime CSV cases.

    This is an early behavioral sanity-check baseline only.
    """
    pressure_index = transmission_multiplier / max(healthcare_capacity_multiplier, 0.01)
    capacity_gap = transmission_multiplier - healthcare_capacity_multiplier
    recovery_balance = recovery_support_multiplier - transmission_multiplier
    intervention_burden = intervention_cost_multiplier

    if pressure_index >= 1.25 and recovery_balance <= -0.1:
        expected_regime = "overload_risk"
        expected_class = "pressured"
        reason = "Transmission pressure materially exceeds effective capacity while recovery support lags."
    elif transmission_multiplier >= 1.1 and recovery_support_multiplier <= 0.95:
        expected_regime = "uncontrolled_spread"
        expected_class = "unstable"
        reason = "Elevated transmission plus weak recovery support points to spread escalation risk."
    elif transmission_multiplier <= 0.85 and recovery_support_multiplier >= 1.05 and intervention_burden <= 1.15:
        expected_regime = "recovery_dominant"
        expected_class = "stable"
        reason = "Lower transmission with stronger recovery support favors recovery-led dynamics."
    elif transmission_multiplier <= 0.8 and intervention_burden >= 1.1:
        expected_regime = "suppressed_low_activity"
        expected_class = "low_activity"
        reason = "Activity pressure is already low and expensive intervention aligns with a suppressed regime."
    else:
        expected_regime = "managed_containment"
        expected_class = "managed"
        reason = "Pressure and support are mixed, so containment is the conservative expected regime."

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
