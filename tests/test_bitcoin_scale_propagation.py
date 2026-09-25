from sce.research.bitcoin_scale_propagation import propagation_signature, summarize_propagations

def test_lower_to_higher_signature():
    sig = propagation_signature({"1m":"2026-01-01T00:00:00Z","5m":"2026-01-01T00:01:00Z","15m":"2026-01-01T00:02:00Z","1h":"2026-01-01T00:03:00Z"})
    assert sig["first_scale"] == "1m"
    assert sig["direction"] == "lower_to_higher"
    assert sig["coverage"] == 4

def test_higher_to_lower_signature():
    sig = propagation_signature({"1m":"2026-01-01T00:03:00Z","5m":"2026-01-01T00:02:00Z","15m":"2026-01-01T00:01:00Z","1h":"2026-01-01T00:00:00Z"})
    assert sig["first_scale"] == "1h"
    assert sig["direction"] == "higher_to_lower"

def test_summary_counts_patterns():
    summary = summarize_propagations([
        {"coverage":3,"first_scale":"1m","direction":"lower_to_higher"},
        {"coverage":4,"first_scale":"1m","direction":"lower_to_higher"},
        {"coverage":2,"first_scale":"4h","direction":"higher_to_lower"},
        {"coverage":1,"first_scale":"1d","direction":"mixed"},
    ])
    assert summary["events_with_multiscale_propagation"] == 3
    assert summary["first_scale_counts"]["1m"] == 2
    assert summary["direction_counts"]["lower_to_higher"] == 2
