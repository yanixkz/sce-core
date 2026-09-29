from datetime import datetime, timedelta, timezone
from pathlib import Path

from examples.run_bitcoin_continuous import cycle


def test_cycle_deduplicates_then_settles_without_changing_forecast(tmp_path):
    t=datetime(2026,9,25,tzinfo=timezone.utc)
    rows=[(t+timedelta(minutes=15*i),100+i/10) for i in range(102)]
    issued_at=rows[99][0]+timedelta(minutes=15,seconds=45)
    first=cycle(tmp_path,rows[:100],issued_at,lambda:{"status":"OBSERVED"})
    assert first["issued"]
    forecast=(tmp_path/"forecasts"/f"{first['issued']}.json").read_bytes()
    again=cycle(tmp_path,rows[:100],issued_at+timedelta(minutes=1),lambda:None)
    assert again["issued"] is None and again["skip_reason"]=="already_recorded"
    completed=cycle(tmp_path,rows,issued_at+timedelta(minutes=41),lambda:None)
    assert completed["settled"]==1
    assert (tmp_path/"forecasts"/f"{first['issued']}.json").read_bytes()==forecast
    assert (tmp_path/"outcomes"/f"{first['issued']}.json").exists()
