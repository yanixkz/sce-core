from __future__ import annotations
import csv,json,math
from bisect import bisect_left
from pathlib import Path

# Scale-space experiment: one 15m price path, observed under progressively
# wider causal smoothing scales. No trading labels, no future returns.
TAUS=(1,2,4,8,16,32,64,128,256,512,1024)

def load(path):
    out=[]
    with open(path,newline="") as f:
        for r in csv.DictReader(f): out.append((r["time"],float(r["close"])))
    return out

def ema(xs,n):
    a=2/(n+1); out=[];v=xs[0]
    for x in xs:
        v=a*x+(1-a)*v;out.append(v)
    return out

def extrema(xs):
    # causal confirmation: an extremum at i is known at i+1.
    out=[]
    for i in range(1,len(xs)-1):
        if xs[i]>xs[i-1] and xs[i]>=xs[i+1]: out.append((i,"H",xs[i]))
        elif xs[i]<xs[i-1] and xs[i]<=xs[i+1]: out.append((i,"L",xs[i]))
    return out

def build_index(events):
    return {kind: ([e[0] for e in events if e[1]==kind],
                   [e for e in events if e[1]==kind]) for kind in ("H","L")}

def nearest(index,i,kind,maxdist):
    positions, events = index[kind]
    j=bisect_left(positions,i)
    candidates=[]
    if j < len(events): candidates.append(events[j])
    if j: candidates.append(events[j-1])
    if not candidates: return None
    best=min(candidates,key=lambda e:abs(e[0]-i))
    return best if abs(best[0]-i)<=maxdist else None

def main():
    root=Path("data/bitcoin/coinbase")
    rows=load(root/"btc_usd_15m.csv"); prices=[p for _,p in rows]
    levels={}
    for tau in TAUS:
        sm=ema(prices,tau); ex=extrema(sm)
        levels[tau]={"extrema":ex,"index":build_index(ex)}
    # Track extrema from fine to coarse. A feature persists if a same-kind extremum
    # survives near its previous location; tolerance grows with scale.
    tracks=[]
    for e in levels[TAUS[0]]["extrema"]:
        tr=[(TAUS[0],e[0],e[1],e[2])]
        cur=e
        for tau in TAUS[1:]:
            m=nearest(levels[tau]["index"],cur[0],cur[1],max(2,tau))
            if not m: break
            tr.append((tau,m[0],m[1],m[2]));cur=m
        tracks.append(tr)
    hist={}
    for tr in tracks:
        death=tr[-1][0];hist[str(death)]=hist.get(str(death),0)+1
    durable=[tr for tr in tracks if len(tr)>=6]
    sample=[]
    for tr in durable[:200]:
        a=tr[0];z=tr[-1]
        sample.append({"kind":a[2],"birth_tau":a[0],"death_tau":z[0],"levels":len(tr),
                       "birth_time":rows[a[1]][0],"last_time":rows[z[1]][0],
                       "price_at_birth":a[3],"price_at_last":z[3]})
    summary={
      "method":"causal EMA scale-space extrema persistence",
      "base_resolution":"15m","taus_bars":TAUS,
      "tau_hours":[round(x*.25,2) for x in TAUS],
      "base_extrema":len(tracks),"durable_6plus_levels":len(durable),
      "durable_fraction":len(durable)/len(tracks) if tracks else 0,
      "death_scale_histogram":hist,
      "warning":"exploratory topology proxy; matching tolerance and EMA family require robustness tests",
      "durable_sample":sample}
    (root/"scale_space_persistence.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!="durable_sample"},indent=2))
if __name__=="__main__":main()
