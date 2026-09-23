from __future__ import annotations
import argparse, json
from pathlib import Path
from sce.research.bitcoin_temporal_field import parse_price_csv, build_temporal_field
from sce.research.bitcoin_regime_evaluation import TransitionLabelConfig, independent_regime_labels, persistent_transitions, evaluate_leading_signal

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="data/bitcoin/btc_priceusd_1d.csv")
    p.add_argument("--out",default="data/bitcoin/bitcoin_regime_evaluation.json")
    args=p.parse_args()
    points=parse_price_csv(Path(args.input).read_text())
    field=build_temporal_field(points)
    labels=independent_regime_labels(points)
    events=persistent_transitions(labels)
    result={"method":"independent forward-regime labels; CDS field remains causal","evaluation":evaluate_leading_signal(field,events),"events":events}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result["evaluation"],indent=2))
if __name__=="__main__": main()
