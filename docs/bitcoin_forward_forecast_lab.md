# Bitcoin Forward Forecast Lab, baseline v0

## Fixed prospective contract

Source: Coinbase Exchange BTC-USD 15m candles. A candle stamped `t` is
eligible only after `t+15m`; the issue command requires a completed candle
less than five minutes old and 97 consecutive candles. At issue time it writes
one new, exclusive `forecasts/<sha256>.json` with observation time, wall-clock
issue time, source snapshot hash, code run ID, two target closes (+15m/+30m
from the observation), and actual effective lead from issue. It **does not**
read the future candles. Outcome is stored later in a separate exclusive file
`outcomes/<forecast_id>.json`; the original forecast is never updated.

The first CI workflow creates a research snapshot on PR updates and keeps its
artifact for 90 days. That is an auditable prototype, **not yet a permanent
or continuous ledger**. GitHub Actions scheduled workflows only run from the
default branch; this research PR is not merged. A durable independent store
and scheduler must be added before claiming a continuous forward trial.

Rules frozen before observing prospective outcomes:

- Flat baseline: unchanged last close, P(up)=0.5.
- Candidate: average log return of the last four 15m bars, extrapolated 1 or
  2 bars. P(up)=0.55 following positive drift and 0.45 otherwise; these
  probabilities are heuristic and uncalibrated.
- Indicative 80% range uses trailing 96-bar volatility with normal scaling.
  Actual coverage is reported rather than assumed.
- Price score: mean absolute error as percentage of observed price. Direction
  score: Brier score, lower is better; equal closing price counts as not up.

## Retrospective benchmark, 2017–September 2026

Computed on the Coinbase 15m dataset from CI run 36037934426, hourly forecast
origins (outcomes at +15m/+30m do not overlap), consecutive-candle guard.
These results are **retrospective**, with no execution costs; they are not
prospective evidence or a trading strategy.

| Era | Horizon | N | Flat price MAE | Momentum MAE | Flat Brier | Momentum Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2017–20 | 15m | 34,144 | 0.2621% | 0.3045% | 0.2500 | 0.2551 |
| 2017–20 | 30m | 34,139 | 0.3713% | 0.4776% | 0.2500 | 0.2555 |
| 2021–23 | 15m | 26,202 | 0.2337% | 0.2670% | 0.2500 | 0.2560 |
| 2021–23 | 30m | 26,201 | 0.3156% | 0.4023% | 0.2500 | 0.2556 |
| 2024+ | 15m | 23,810 | 0.1609% | 0.1823% | 0.2500 | 0.2536 |
| 2024+ | 30m | 23,809 | 0.2277% | 0.2865% | 0.2500 | 0.2541 |

The fixed momentum candidate loses in both metrics and all three eras. Do not
turn it into a signal. A trailing-volatility range covers ~79–81% of 15m
outcomes but only ~76–77% of 30m outcomes, suggesting that its 30m uncertainty
is too narrow. Periods have different raw volatility; compare score *within*
era, not absolute MAE across eras.

## Next test

First collect actual issue-time forecasts and evaluate their prospective
outcomes. Then compare independently sourced volume and order-flow features
against the *same* flat baseline, with a frozen evaluation procedure and no
selection on the future period. Scale-space features can be tested as regime
conditioning variables. No position management or auto trading is wired in.
