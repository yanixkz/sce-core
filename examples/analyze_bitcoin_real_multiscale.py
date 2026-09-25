from __future__ import annotations
import csv, json, math, random
from bisect import bisect_right
from pathlib import Path

SCALES=("15m","1h","4h","1d")
LOOKBACK=20

def load(path):
    rows=[]
    with open(path,newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r["time"],float(r["close"])))
    return rows

def states(rows):
    out=[]
    for i,(t,p) in enumerate(rows):
        if i<LOOKBACK: continue
        q=rows[i-LOOKBACK][1]
        ret=math.log(p/q)
        out.append((t,1 if ret>0 else -1 if ret<0 else 0,p))
    return out

def align(series):
    # Causal alignment on 1h checkpoints: only observations timestamped <= checkpoint.
    base=series["1h"]; idx={k:0 for k in SCALES}; out=[]
    times={k:[x[0] for x in series[k]] for k in SCALES}
    for t,_,price in base:
        vals=[]
        ok=True
        for k in SCALES:
            j=bisect_right(times[k],t)-1
            if j<0: ok=False; break
            vals.append(series[k][j][1])
        if ok: out.append((t,price,vals))
    return out

def geometry(aligned):
    rows=[];prev_b=0;prev_d=0;persist=0
    for t,p,s in aligned:
        sm=sum(s);d=1 if sm>0 else -1 if sm<0 else 0
        aligned_flags=[x==d and d!=0 for x in s]
        b=sum(aligned_flags)/len(s)
        # contiguous front from smallest scale; prevents skipping an intermediate scale.
        front=0
        for flag in aligned_flags:
            if not flag: break
            front+=1
        v=b-prev_b if d==prev_d else b
        persist=persist+1 if d==prev_d and d else (1 if d else 0)
        phase="neutral"
        if d:
            if v>0: phase="propagation"
            elif b>=.75 and persist>=3: phase="synchronized"
            else: phase="decay"
        rows.append({"time":t,"price":p,"direction":d,"breadth":b,"front":front,"velocity":v,"persistence":persist,"phase":phase,"states":s})
        prev_b,prev_d=b,d
    return rows

def forward_return(rows,i,h):
    j=min(len(rows)-1,i+h);return rows[j]["price"]/rows[i]["price"]-1

def summarize(rows):
    phases={}
    transitions={}
    for i,r in enumerate(rows):
        phases[r["phase"]]=phases.get(r["phase"],0)+1
        if i:
            k=rows[i-1]["phase"]+"->"+r["phase"];transitions[k]=transitions.get(k,0)+1
    # Event study at propagation onset; 24/72/168 hours.
    events=[]
    for i,r in enumerate(rows):
        if r["phase"]=="propagation" and (i==0 or rows[i-1]["phase"]!="propagation"):
            events.append({"i":i,"direction":r["direction"],"front":r["front"]})
    response={}
    for d in (-1,1):
        es=[e for e in events if e["direction"]==d]
        response[str(d)]={"n":len(es)}
        for h in (24,72,168):
            xs=[forward_return(rows,e["i"],h)*d for e in es if e["i"]+h<len(rows)]
            xs.sort()
            response[str(d)][f"directional_median_{h}h"]=xs[len(xs)//2] if xs else None
            response[str(d)][f"directional_hit_{h}h"]=sum(x>0 for x in xs)/len(xs) if xs else None
    return {"rows":len(rows),"phase_days_or_hours":phases,"phase_transitions":transitions,"propagation_response":response}

def null_test(rows,iterations=500,seed=7):
    # Tests whether observed 72h directional response at propagation onsets exceeds
    # randomized onset timing while preserving direction counts and price path.
    rng=random.Random(seed);valid=list(range(1,len(rows)-73))
    obs=[]
    onsets=[]
    for i,r in enumerate(rows[:-73]):
        if i and r["phase"]=="propagation" and rows[i-1]["phase"]!="propagation":
            x=forward_return(rows,i,72)*r["direction"];obs.append(x);onsets.append(r["direction"])
    observed=sum(obs)/len(obs) if obs else 0
    sims=[]
    for _ in range(iterations):
        sample=rng.sample(valid,min(len(onsets),len(valid)))
        xs=[forward_return(rows,i,72)*d for i,d in zip(sample,onsets)]
        sims.append(sum(xs)/len(xs))
    p=(1+sum(x>=observed for x in sims))/(len(sims)+1)
    return {"metric":"mean 72h direction-adjusted return","observed":observed,"null_mean":sum(sims)/len(sims),"permutation_p_one_sided":p,"iterations":iterations,"n_events":len(obs)}

def main():
    root=Path("data/bitcoin/coinbase")
    series={k:states(load(root/f"btc_usd_{k}.csv")) for k in SCALES}
    rows=geometry(align(series))
    out={"method":{"scales":SCALES,"lookback_bars":LOOKBACK,"alignment":"causal <= checkpoint","front":"contiguous from 15m","warning":"exploratory; scale-relative 20-bar direction"},"summary":summarize(rows),"null_72h":null_test(rows)}
    (root/"wave_geometry_real.json").write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
