# SCE forecast phase 2: volume, microstructure, and readiness gate

## Continuous prospective collection

The operational workflow on `main` is deliberately small: it checks out a
**pinned, tested research commit** and the independent
`experiment/bitcoin-forecast-ledger` branch, runs one cycle, and appends only
new forecast, snapshot, and outcome files. Forecasts never change after issue.
One recorded forecast is allowed per completed 15m candle, even if the cron
fires more often. A scheduled run can be delayed or dropped; coverage must be
measured from expected bar times rather than inferred from green CI checks.

The forecast is labeled +15m/+30m **from the observed bar close**. The actual
lead from its issue timestamp is recorded; a forecast is skipped if the bar is
already ten minutes old. If the public Coinbase endpoint is stale, missing or
has gaps in the 97-bar history, the cycle fails or skips without fabrication.
After both target candles close, a later cycle writes a separate outcome.
An outage beyond the recent 30-hour fetch window requires manual recovery.

This scheduler is research infrastructure. It does not place orders or call
the trading bot. It runs from `main` because GitHub Actions scheduled workflows
cannot run from a nondefault branch. PR #81 remains unmerged.

## New market layer

At issue time a separate snapshot records the last closed candle's volume
relative to the median of the prior 96 candles; Coinbase Exchange public REST
L2 top-ten bid/ask size, spread, and its recent-trade sample are collected
before the price-only forecast is issued. Trade `side` is the **maker** side,
so `sell` indicates an aggressive buy. The snapshot is not a synchronized
15-minute order-flow history. If REST fails, it is labeled `UNAVAILABLE` and
the price-only forecast still records normally. Availability has to be proved
by the CI probe before interpreting these fields.

The prespecified retrospective candidate used four-bar momentum only when
the latest complete candle's volume exceeded 1.5 times the previous 96-bar
median. Hourly origins and no tuning on these results:

| Era | Horizon | Flat MAE | Volume-gated MAE | Flat Brier | Volume-gated Brier |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017–20 | 15m | 0.2621% | 0.2848% | 0.2500 | 0.2517 |
| 2017–20 | 30m | 0.3713% | 0.4293% | 0.2500 | 0.2520 |
| 2021–23 | 15m | 0.2337% | 0.2502% | 0.2500 | 0.2516 |
| 2021–23 | 30m | 0.3156% | 0.3595% | 0.2500 | 0.2516 |
| 2024+ | 15m | 0.1609% | 0.1728% | 0.2500 | 0.2512 |
| 2024+ | 30m | 0.2277% | 0.2610% | 0.2500 | 0.2513 |

Volume gating reduced the error of raw momentum but did not beat the flat
baseline in any era/horizon. The candidate is rejected as a forecasting edge.

## Trading evaluation

The shadow trade proxy enters in the momentum direction only during elevated
volume, exits at the +15m/+30m candle close, and subtracts an illustrative
0.10% round-trip cost. Mean net return per trade ranged from -0.092% to
-0.097% across the six era/horizon cells. It omits historical spread, borrow,
funding, execution timing, and liquidation, so it is **not executable**.

`bitcoin_trade_readiness.assess` returns `BLOCKED` for the current candidate.
The necessary gates include improvement over flat price error and Brier score
in each historical era, positive net shadow return, at least 500 independent
hourly prospective forecasts across 30 days, and scored prospective evidence
for a frozen candidate. Even if gates pass, the function does not enable paper
or live orders; it only permits a further execution-aware study.
