# Scale-space trajectory and adjacent-scale hierarchy, 2026-09-24

## Trajectory geometry: negative result for tested simple features

Coinbase BTC-USD 15m, 340,850 rows. CI run 36037934426 at commit `5738987`.
The matching uses causal EMA and nearest same-kind extrema with tolerance
`max(2, round(2 sqrt(tau)))`. Extrema at bar `i` are confirmed only at `i+1`.

| Measure | BTC | 96-bar block shuffle |
| --- | ---: | ---: |
| Tracked extrema | 168,738 | 168,528 |
| Median matched levels | 6 | 6 |
| Median normalized drift | 0.10221 | 0.10373 |
| Median maximum normalized drift | 0.5 | 0.5 |
| Median drift reversals | 0 | 0 |
| No drift reversal | 81.89% | 82.44% |

One null draw and aggregate medians cannot establish equivalence. They provide
no evidence that these specific trajectory summaries discriminate BTC from
this null. No forecasting or trading claim follows.

## Hierarchy graph: exploratory result

`examples/analyze_bitcoin_scale_hierarchy.py` maps each fine extremum to at
most one nearest same-kind extremum at the adjacent larger tau. A coarse node
can collect multiple children (`coarse_merges`), and a coarse node with no child
is a `coarse_birth`. These are graph labels under this matching rule, not
physical claims of creation or a topological persistence invariant. There are
no skipped-scale edges or parameter-free birth/death claims.

Same 15m close series; one block-shuffled return sequence each for 24, 96,
and 384 bars, distinct predetermined random seeds. Births and merges below are
fractions of coarse extrema. The complete per-level counts are emitted into
`data/bitcoin/coinbase/scale_space_hierarchy.json` in the CI artifact.

| Tau transition | BTC birth | Null birth 24 / 96 / 384 | BTC merge | Null merge 24 / 96 / 384 |
| --- | ---: | --- | ---: | --- |
| 32→64 | 20.52% | 19.54 / 20.51 / 20.61% | 25.42% | 25.23 / 24.85 / 25.31% |
| 128→256 | 38.19% | 35.26 / 35.15 / 37.99% | 24.71% | 24.31 / 24.12 / 23.60% |
| 512→1024 | 57.36% | 51.51 / 51.55 / 53.62% | 19.15% | 20.37 / 22.16 / 21.54% |

The coarsest transition shows a descriptive difference, but the sample has
fewer extrema and block-size sensitivity. The observed rates may also follow
from EMA phase lag, nonstationarity, volatility mixtures, or the permissive
nearest-parent tolerance. This is hypothesis generation only.

Next falsification: repeat null draws, report uncertainty by market era and
volatility regime, vary smoothing and matching, and compare against simpler
properties such as local extrema density. Before any forward use, expose a
graph edge only after both nodes have been confirmed; do not label a prior
timestamp with a parent discovered later.
