from __future__ import annotations
import argparse, json
from pathlib import Path
from sce.research.bitcoin_multiscale_field import parse_multiscale_csv, build_scale_states
from sce.research.bitcoin_propagation_geometry import propagation_features, compare_propagation_groups

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="data/bitcoin/btc_binance_multiscale.csv")
    p.add_argument("--events",default="data/bitcoin/bitcoin_regime_evaluation.json")
    p.add_argument("--out",default="data/bitcoin/bitcoin_propagation_evaluation.json")
    args=p.parse_args()
    states=build_scale_states(parse_multiscale_csv(Path(args.input).read_text()))
    ev=json.loads(Path(args.events).read_text())
    signatures=[]
    for e in ev.get("events",[]):
        if e.get("classification")!="hit": continue
        signatures.append({"classification":"hit","event_time":e["time"],**propagation_features(states,e["time"])})
    for e in ev.get("false_alarm_episodes",[]):
        t=e["end_time"]
        signatures.append({"classification":"false_alarm","event_time":t,**propagation_features(states,t)})
    result={"summary":compare_propagation_groups(signatures),"signatures":signatures,
            "note":"descriptive geometry; not evidence of predictive superiority until matched-null testing"}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result["summary"],indent=2))
if __name__=="__main__":main()
