from datetime import datetime, timezone
from sce.research.bitcoin_temporal_field import PricePoint, build_temporal_field
from sce.research.bitcoin_regime_evaluation import build_event_records, build_false_alarm_episodes

def _points(n=140):
    return [PricePoint(datetime(2026,1,1,tzinfo=timezone.utc).replace(day=1),100.0)] if n==1 else [
        PricePoint(datetime.fromtimestamp(1767225600+i*86400,tz=timezone.utc),100.0+i*.5) for i in range(n)
    ]

def test_event_records_are_visualization_ready():
    field=build_temporal_field(_points())
    t=field["timeline"]
    event={"time":t[-1]["time"],"from_regime":0,"to_regime":1}
    rows=build_event_records(field,[event],lookback_days=30,pressure_threshold=0.0)
    assert rows[0]["classification"]=="hit"
    assert rows[0]["signal_time"] is not None
    assert rows[0]["transition_snapshot"]["price_usd"] is not None

def test_false_alarm_episodes_are_clustered():
    field=build_temporal_field(_points())
    eps=build_false_alarm_episodes(field,[],pressure_threshold=0.0)
    assert len(eps)==1
    assert eps[0]["classification"]=="false_alarm"
    assert eps[0]["duration_days"]==len(field["timeline"])
