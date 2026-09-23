from datetime import datetime, timedelta, timezone
from sce.research.bitcoin_temporal_field import PricePoint, build_temporal_field
from sce.research.bitcoin_regime_evaluation import independent_regime_labels, persistent_transitions, evaluate_leading_signal

def history(n=220):
    start=datetime(2020,1,1,tzinfo=timezone.utc)
    out=[]
    price=100.0
    for i in range(n):
        price *= 1.006 if i < 100 else (0.994 if i < 170 else 1.003)
        out.append(PricePoint(start+timedelta(days=i),price))
    return out

def test_labels_use_future_only_for_evaluation_and_are_deterministic():
    pts=history()
    a=independent_regime_labels(pts)
    assert a == independent_regime_labels(pts)
    assert len(a) == len(pts)-30
    assert {x["regime"] for x in a} <= {-1,0,1}

def test_transition_and_signal_evaluation_is_bounded():
    pts=history()
    labels=independent_regime_labels(pts)
    events=persistent_transitions(labels)
    result=evaluate_leading_signal(build_temporal_field(pts),events)
    assert 0 <= result["recall"] <= 1
    assert 0 <= result["false_alarm_fraction"] <= 1
