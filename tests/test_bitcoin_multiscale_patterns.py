from sce.research.bitcoin_multiscale_patterns import analyze_event_propagation

def test_analyze_all_available_scales():
    times=[f"2026-01-01T00:0{i}:00Z" for i in range(6)]
    rows=[]
    for scale,onset in [("1m",1),("5m",2),("15m",3),("1h",4)]:
        for i,t in enumerate(times):
            rows.append({"time":t,"scale":scale,"stability":0.3 if i>=onset else 0.8,"transition_pressure":0.7 if i>=onset else 0.2})
    events=[{"time":times[5],"from_regime":0,"to_regime":1}]
    out=analyze_event_propagation(rows,events)
    assert out["events"] == 1
    assert out["events_with_multiscale_pattern"] == 1
    assert out["first_scale_counts"]["1m"] == 1
    assert out["direction_counts"]["lower_to_higher"] == 1
    assert out["signatures"][0]["coverage"] == 4
