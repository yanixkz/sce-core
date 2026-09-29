from __future__ import annotations

from sce.scenarios.bitcoin_temporal_field import (
    TemporalObservation,
    cross_scale_coherence,
    directional_state,
    observation_stability,
    run_bitcoin_temporal_field_demo,
    transition_pressure,
)


def _observation(scale: str, trend: float, momentum: float) -> TemporalObservation:
    return TemporalObservation(
        timestamp="T",
        scale=scale,
        trend=trend,
        momentum=momentum,
        volatility=0.2,
        drawdown_pressure=0.1,
        range_position=0.6,
        volume_pressure=0.1,
    )


def test_temporal_field_demo_is_deterministic():
    assert run_bitcoin_temporal_field_demo() == run_bitcoin_temporal_field_demo()


def test_directional_state_is_transparent():
    assert directional_state(_observation("1d", 0.8, 0.5)) == 1
    assert directional_state(_observation("1d", -0.8, -0.5)) == -1
    assert directional_state(_observation("1d", 0.01, -0.01)) == 0


def test_coherence_is_high_when_scales_agree():
    aligned = [_observation(scale, 0.6, 0.4) for scale in ("1h", "4h", "1d", "1w")]
    mixed = [
        _observation("1h", 0.6, 0.4),
        _observation("4h", -0.6, -0.4),
        _observation("1d", 0.6, 0.4),
        _observation("1w", -0.6, -0.4),
    ]
    assert cross_scale_coherence(aligned) > cross_scale_coherence(mixed)


def test_scores_are_bounded():
    rows = [_observation("1h", 0.6, 0.4), _observation("1d", -0.4, -0.2)]
    assert all(0.0 <= observation_stability(row) <= 1.0 for row in rows)
    assert 0.0 <= cross_scale_coherence(rows) <= 1.0
    assert 0.0 <= transition_pressure(rows) <= 1.0


def test_demo_marks_fixture_as_non_empirical():
    result = run_bitcoin_temporal_field_demo()
    assert result["empirical"] is False
    assert result["field"] == "F(t, tau)"
    assert len(result["cells"]) == 5
