from datetime import datetime,timedelta,timezone
from sce.research.bitcoin_temporal_field import PricePoint,build_temporal_field
def _history(n=120):
    start=datetime(2020,1,1,tzinfo=timezone.utc)
    return [PricePoint(start+timedelta(days=i),100*(1.01**i)) for i in range(n)]
def test_field_deterministic_bounded():
    a=build_temporal_field(_history());assert a==build_temporal_field(_history());assert a["cells"];assert all(0<=x["stability"]<=1 for x in a["cells"]);assert all(0<=x["coherence"]<=1 for x in a["timeline"])
def test_future_extension_does_not_rewrite_past():
    a=build_temporal_field(_history(90));b=build_temporal_field(_history(120));bc={(x["time"],x["scale"]):x for x in b["cells"]};assert a["cells"];assert all(bc[(x["time"],x["scale"])]==x for x in a["cells"])
