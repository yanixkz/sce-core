from __future__ import annotations
from dataclasses import dataclass
from math import log

@dataclass(frozen=True)
class WaveState:
    time: str
    direction: int
    breadth: float
    velocity: float
    persistence: int
    front: float
    phase: str

def _sign(x, eps=0.0):
    return 1 if x>eps else (-1 if x<-eps else 0)

def daily_wave_states(field, scales=("1d","1w","1m")):
    """Minimal causal wave geometry over available scales.
    direction: majority sign; breadth: aligned fraction; velocity: change in breadth;
    front: highest ordered scale aligned with direction; persistence: consecutive direction days.
    """
    if isinstance(field,dict):
        # The empirical field stores one row per time in timeline and one row
        # per (time, scale) in cells. Rejoin them before extracting wave states.
        by_time={}
        for cell in field["cells"]:
            by_time.setdefault(cell["time"],{})[cell["scale"]]=cell
        rows=({"time":row["time"],"scales":by_time.get(row["time"],{})}
              for row in field["timeline"])
    else:
        rows=field
    out=[];prev_b=0.0;prev_d=0;persist=0
    for r in rows:
        states=[]
        for s in scales:
            x=r.get("scales",{}).get(s,{})
            v=.6*float(x.get("trend",0) or 0)+.4*float(x.get("momentum",0) or 0)
            states.append(_sign(v,.12))
        score=sum(states);d=_sign(score)
        b=(sum(v==d for v in states)/len(states)) if d else 0.0
        aligned=[i for i,v in enumerate(states) if d and v==d]
        front=(max(aligned)+1)/len(states) if aligned else 0.0
        vel=b-prev_b if d==prev_d else b
        persist=persist+1 if d and d==prev_d else (1 if d else 0)
        if not d: phase="neutral"
        elif vel>0: phase="propagation"
        elif b>=2/3 and persist>=3: phase="synchronized"
        else: phase="decay"
        out.append(WaveState(str(r.get("time")),d,b,vel,persist,front,phase).__dict__)
        prev_b=b;prev_d=d
    return out

def summarize_wave_states(states):
    phases={}
    for s in states: phases[s["phase"]]=phases.get(s["phase"],0)+1
    transitions={}
    for a,b in zip(states,states[1:]):
        k=f'{a["phase"]}->{b["phase"]}'
        transitions[k]=transitions.get(k,0)+1
    return {"days":len(states),"phase_days":phases,"phase_transitions":transitions,
            "note":"Descriptive causal geometry only; no trading claim."}
