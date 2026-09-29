from __future__ import annotations
import argparse, json
from pathlib import Path
from sce.research.bitcoin_temporal_field import parse_price_csv, build_temporal_field
from sce.research.bitcoin_regime_evaluation import TransitionLabelConfig, independent_regime_labels, persistent_transitions, evaluate_leading_signal, build_event_records, build_false_alarm_episodes
from sce.research.bitcoin_baselines import evaluate_simple_baselines
from sce.research.bitcoin_robustness import evaluate_by_era
from sce.research.bitcoin_event_windows import event_windows, summarize_event_windows, summarize_by_transition
from sce.research.bitcoin_price_response import price_response_study, summarize_price_responses
from sce.research.bitcoin_signal_value import enrich_price_responses, summarize_signal_value, matched_controls
from sce.research.bitcoin_event_table import event_table_csv
from sce.research.bitcoin_coherence_episodes import classify_coherence_episodes, summarize_coherence_episodes
from sce.research.bitcoin_causal_surfing import causal_alarm_responses, summarize_causal_alarms
from sce.research.bitcoin_alarm_features import causal_alarm_features, summarize_feature_separation
from sce.research.bitcoin_surfing_backtest import walk_forward_predictions, backtest_predictions
from sce.research.bitcoin_confirmed_surfing import confirmation_sweep
from sce.research.bitcoin_wave_rider import wave_rider
from sce.research.bitcoin_wave_rider_exact import exact_wave_rider
from sce.research.bitcoin_wave_geometry import daily_wave_states, summarize_wave_states

ERAS=(("early","2010-07-18","2016-12-31"),("middle","2017-01-01","2020-12-31"),("later","2021-01-01","2099-12-31"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="data/bitcoin/btc_priceusd_1d.csv")
    p.add_argument("--out",default="data/bitcoin/bitcoin_regime_evaluation.json")
    args=p.parse_args()
    points=parse_price_csv(Path(args.input).read_text())
    field=build_temporal_field(points)
    config=TransitionLabelConfig()
    labels=independent_regime_labels(points,config)
    events=persistent_transitions(labels,config.persistence_days)
    evaluation=evaluate_leading_signal(field,events)
    windows=event_windows(field,events,5)
    event_records=build_event_records(field,events)
    price_responses=price_response_study(points,events)
    enriched_responses=enrich_price_responses(price_responses,event_records)
    controls=matched_controls(points,[e['time'] for e in events])
    control_responses=price_response_study(points,controls)
    coherence_episodes=classify_coherence_episodes(field,events)
    causal_alarms=causal_alarm_responses(field,events)
    alarm_features=causal_alarm_features(field,causal_alarms)
    surfing_predictions=walk_forward_predictions(alarm_features)
    surfing_backtest=backtest_predictions(surfing_predictions)
    confirmed_surfing=confirmation_sweep(surfing_predictions)
    wave_rider_result=wave_rider(surfing_predictions,confirm=3)
    exact_wave_rider_result=exact_wave_rider(surfing_predictions,points,confirm=3)
    wave_states=daily_wave_states(field)
    result={
        "method":"independent forward-regime labels; CDS field remains causal",
        "scale_semantics":field.get("scale_semantics"),
        "evaluation":evaluation,
        "eras":evaluate_by_era(field,events,ERAS),
        "baselines":evaluate_simple_baselines(field,events),
        "coherence_episode_summary":summarize_coherence_episodes(coherence_episodes),
        "coherence_episodes":coherence_episodes,
        "events":event_records,
        "signal_value_summary":summarize_signal_value(enriched_responses),
        "control_price_response_summary":summarize_price_responses(control_responses),
        "event_window_5d_summary":summarize_event_windows(windows),
        "event_window_5d_by_transition":summarize_by_transition(windows),
        "event_windows_5d":windows,
        "price_response_summary":summarize_price_responses(price_responses),
        "price_responses":enriched_responses,
        "control_price_responses":control_responses,
        "false_alarm_episodes":build_false_alarm_episodes(field,events),
        "causal_alarm_summary":summarize_causal_alarms(causal_alarms),
        "causal_alarm_responses":causal_alarms,
        "causal_alarm_feature_summary":summarize_feature_separation(alarm_features),
        "causal_alarm_features":alarm_features,
        "surfing_backtest":surfing_backtest,
        "confirmed_surfing":confirmed_surfing,
        "wave_rider":wave_rider_result,
        "exact_wave_rider":exact_wave_rider_result,
        "wave_geometry_summary":summarize_wave_states(wave_states),
        "wave_states":wave_states,
        "surfing_predictions":surfing_predictions,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2))
    print(json.dumps({"evaluation":evaluation,"eras":result["eras"],"baselines":result["baselines"],"coherence_episode_summary":result["coherence_episode_summary"]},indent=2))
if __name__=="__main__": main()
