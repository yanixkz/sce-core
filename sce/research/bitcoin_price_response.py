from __future__ import annotations
from statistics import median

HORIZONS=(1,2,3,5,10,20,30)
LEVELS=(.01,.02,.03,.05,.10)

def price_response_study(points, events):
    times=[p["time"] for p in points]; prices=[p["price_usd"] for p in points]; by={t:i for i,t in enumerate(times)}
    out=[]
    for e in events:
        i=by.get(e["time"])
        if i is None or i+1>=len(points): continue
        p0=prices[i]
        forward=prices[i+1:min(len(prices),i+31)]
        backward=prices[max(0,i-5):i+1]
        rec={"time":e["time"],"from_regime":e.get("from_regime"),"to_regime":e.get("to_regime"),
             "price_usd":p0,
             "pre_5d_return_pct":round((p0/backward[0]-1)*100,3) if len(backward)>1 else None}
        for h in HORIZONS:
            if i+h<len(prices): rec[f"return_{h}d_pct"]=round((prices[i+h]/p0-1)*100,3)
        if forward:
            rets=[p/p0-1 for p in forward]
            rec["mfe_30d_pct"]=round(max(rets)*100,3); rec["mae_30d_pct"]=round(min(rets)*100,3)
            for level in LEVELS:
                up=next((k+1 for k,r in enumerate(rets) if r>=level),None)
                dn=next((k+1 for k,r in enumerate(rets) if r<=-level),None)
                key=str(int(level*100))
                rec[f"up_{key}pct_day"]=up; rec[f"down_{key}pct_day"]=dn
                rec[f"up_{key}pct_first"]=up is not None and (dn is None or up<dn)
                rec[f"down_{key}pct_first"]=dn is not None and (up is None or dn<up)
        out.append(rec)
    return out

def summarize_price_responses(rows):
    groups={}
    for r in rows: groups.setdefault(f'{r.get("from_regime")}->{r.get("to_regime")}',[]).append(r)
    result={}
    for key,g in groups.items():
        d={"events":len(g)}
        for h in HORIZONS:
            vals=[r[f"return_{h}d_pct"] for r in g if f"return_{h}d_pct" in r]
            d[f"median_return_{h}d_pct"]=round(median(vals),3) if vals else None
            d[f"positive_{h}d_pct"]=round(100*sum(v>0 for v in vals)/len(vals),2) if vals else None
        d["median_mfe_30d_pct"]=round(median(r["mfe_30d_pct"] for r in g if "mfe_30d_pct" in r),3)
        d["median_mae_30d_pct"]=round(median(r["mae_30d_pct"] for r in g if "mae_30d_pct" in r),3)
        for level in LEVELS:
            k=str(int(level*100))
            d[f"up_{k}pct_first_rate"]=round(100*sum(bool(r.get(f"up_{k}pct_first")) for r in g)/len(g),2)
            d[f"down_{k}pct_first_rate"]=round(100*sum(bool(r.get(f"down_{k}pct_first")) for r in g)/len(g),2)
        result[key]=d
    return result
