"""Explicit research gates before even considering a paper strategy."""
from __future__ import annotations

from datetime import datetime


def assess(volume_report, prospective_records):
    reasons=[]
    eras=volume_report["eras"]
    for era,period in eras.items():
        for horizon in ("15","30"):
            x=period[horizon]
            if x["volume_gated_abs_pct"]>=x["flat_abs_pct"] or x["volume_gated_brier"]>=x["flat_brier"]:
                reasons.append(f"{era} +{horizon}m: no improvement over flat in both scores")
            if x["paper_mean_net_return_pct"] is None or x["paper_mean_net_return_pct"]<=0:
                reasons.append(f"{era} +{horizon}m: nonpositive paper net per trade")
    complete=sorted((r for r in prospective_records if r.get("status")=="RESOLVED" and "issued_at" in r),
                    key=lambda r:r["issued_at"])
    independent=[]
    for r in complete:
        t=datetime.fromisoformat(r["issued_at"])
        if not independent or (t-datetime.fromisoformat(independent[-1]["issued_at"])).total_seconds()>=3600:
            independent.append(r)
    times=[datetime.fromisoformat(r["issued_at"]) for r in independent]
    if len(times)<500:reasons.append(f"prospective N={len(times)} < 500")
    if len(times)<2 or (times[-1]-times[0]).days<30:
        reasons.append("prospective span < 30 days")
    if not independent or any("candidate_model" not in r for r in independent):
        reasons.append("no frozen candidate with prospective scored outcomes")
    else:
        for horizon in ("15","30"):
            scored=[r for r in independent if horizon in r.get("outcomes",{})]
            if len(scored)<500:
                reasons.append(f"+{horizon}m prospective scored N={len(scored)} < 500")
                continue
            flat=sum(r["outcomes"][horizon]["flat_abs_pct"] for r in scored)/len(scored)
            candidate=sum(r["outcomes"][horizon]["candidate_abs_pct"] for r in scored)/len(scored)
            if candidate>=flat:reasons.append(f"+{horizon}m prospective price error does not beat flat")
            if sum(r["outcomes"][horizon]["candidate_brier"] for r in scored)/len(scored)>=.25:
                reasons.append(f"+{horizon}m prospective Brier does not beat 0.25")
    return {"status":"BLOCKED" if reasons else "RESEARCH_GATE_PASSED",
            "live_trading_enabled":False,"paper_trading_enabled":False,
            "prospective_n":len(times),"reasons":reasons,
            "note":"Passing these necessary gates would permit a further execution-aware study, not real orders."}
