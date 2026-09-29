"""Prespecified volume-conditioned momentum comparison; retrospective only."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import median

from sce.research.bitcoin_forecast_lab import BAR_SECONDS, LOOKBACK, predict
from sce.research.bitcoin_trade_readiness import assess


def evaluate(rows):
    metrics = {era: {str(h): {"n":0,"active":0,"flat_abs_pct":0.,"momentum_abs_pct":0.,
                              "volume_gated_abs_pct":0.,"flat_brier":0.,
                              "momentum_brier":0.,"volume_gated_brier":0.,
                              "paper_trades":0,"paper_net_return_pct_sum":0.,"paper_wins":0}
                     for h in (15,30)} for era in ("2017-2020","2021-2023","2024+")}
    streak=1
    for i in range(1,len(rows)-2):
        streak=streak+1 if (rows[i][0]-rows[i-1][0]).total_seconds()==BAR_SECONDS else 1
        if streak<LOOKBACK+1 or i%4:continue
        f=predict([r[1] for r in rows[i-LOOKBACK:i+1]])
        v=rows[i][2]
        typical=median(r[2] for r in rows[i-LOOKBACK:i])
        active=v>1.5*typical if typical>0 else False
        year=rows[i][0].year
        era="2017-2020" if year<=2020 else ("2021-2023" if year<=2023 else "2024+")
        for h in (1,2):
            if (rows[i+h][0]-rows[i][0]).total_seconds()!=h*BAR_SECONDS:continue
            actual=rows[i+h][1];p=rows[i][1];y=float(actual>p)
            forecast=f[str(15*h)];m=metrics[era][str(15*h)]
            m["n"]+=1;m["active"]+=int(active)
            for model,price,prob in (("flat",p,.5),
                      ("momentum",forecast["momentum_price"],forecast["momentum_p_up"]),
                      ("volume_gated",forecast["momentum_price"] if active else p,
                       forecast["momentum_p_up"] if active else .5)):
                m[model+"_abs_pct"]+=abs(price-actual)/p*100
                m[model+"_brier"]+=(prob-y)**2
            direction=1 if forecast["momentum_p_up"]>.5 else -1
            if active:
                # Deliberately optimistic spot-like proxy. A short here has
                # no borrow/funding model and is NOT an executable backtest.
                net=direction*(actual/p-1)*100-0.10
                m["paper_trades"]+=1
                m["paper_net_return_pct_sum"]+=net
                m["paper_wins"]+=int(net>0)
    for data in metrics.values():
        for m in data.values():
            n=m["n"]
            for key in m:
                if key not in ("n","active","paper_trades","paper_net_return_pct_sum","paper_wins"):
                    m[key]=m[key]/n if n else None
            m["active_fraction"]=m["active"]/n if n else None
            m["paper_mean_net_return_pct"]=(m["paper_net_return_pct_sum"]/m["paper_trades"]
                                             if m["paper_trades"] else None)
            m["paper_win_fraction"]=(m["paper_wins"]/m["paper_trades"] if m["paper_trades"] else None)
    return {"status":"RETROSPECTIVE", "hypothesis":"4-bar momentum only when last closed bar volume >1.5x median prior 96 bars",
            "sampling":"hourly, nonoverlapping target windows", "no_tuning":True,
            "paper_assumption":"0.10% round-trip fee/slippage proxy; excludes spread, borrow and funding; no orders",
            "warning":"single prespecified rule; paper proxy is not an executable backtest", "eras":metrics}


def main():
    root=Path("data/bitcoin/coinbase")
    with (root/"btc_usd_15m.csv").open(newline="") as f:
        rows=[(datetime.fromisoformat(r["time"]),float(r["close"]),float(r["volume"])) for r in csv.DictReader(f)]
    result=evaluate(rows)
    (root/"forecast_lab").mkdir(exist_ok=True)
    (root/"forecast_lab"/"volume_backtest.json").write_text(json.dumps(result,indent=2)+"\n")
    readiness=assess(result,[])
    (root/"forecast_lab"/"trade_readiness.json").write_text(json.dumps(readiness,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print(json.dumps(readiness,indent=2))


if __name__=="__main__":main()
