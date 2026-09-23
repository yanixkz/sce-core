# Bitcoin Temporal Field

Bitcoin Temporal Field is an empirical CDS research track for studying Bitcoin as one
dynamic system observed across multiple temporal scales.

The project begins with a deliberately narrow question:

> Do losses of cross-scale stability and coherence precede observable Bitcoin regime transitions?

This is a research hypothesis, not an established result and not a trading signal.

## Core model

We represent the observable market state as a temporal field:

```text
F(t, tau)
```

where:

- `t` is historical market time,
- `tau` is the observation scale (for example 1h, 4h, 1d, 1w, 1m),
- each field cell contains measurements computed using information available at or
  before `t`.

A timeframe is therefore treated as a scale of observation, not as an independent
market.

The CDS mapping is:

```text
Bitcoin history
↓
Temporal scales
↓
Observable constraints
↓
Cross-scale dynamics
↓
Stability / coherence / persistence
↓
Regime transitions
```

## Research principles

1. **Whole-history perspective.** Study the longest defensible Bitcoin market history.
2. **No look-ahead.** A state at time `t` may use only information available by `t`.
3. **Data provenance.** Every dataset records source, market/venue, coverage, timezone,
   frequency, and missing-data policy.
4. **Unequal historical coverage.** Price, derivatives, order-book, and on-chain data
   are separate layers; later datasets must not be projected backward.
5. **Log-price aware.** Long-cycle visualizations and return calculations should avoid
   misleading comparisons caused by Bitcoin's orders-of-magnitude price change.
6. **Hypothesis before optimization.** Define transition labels and evaluation metrics
   before tuning CDS parameters.
7. **Research before trading.** No strategy or execution claims until an out-of-sample
   effect survives walk-forward testing.

## Field layers

### Layer 0 — price field

Initial measurements:

- OHLCV
- log return
- rolling realized volatility
- drawdown from rolling/all-time peak
- normalized trend/momentum
- distance from rolling range

This layer can be built wherever defensible historical OHLCV exists.

### Layer 1 — market-structure field

Later additions:

- spot volume by venue
- liquidity proxies
- spread/order-book measures where available

### Layer 2 — derivatives field

Only for periods with real coverage:

- open interest
- funding
- futures basis
- liquidations

### Layer 3 — on-chain field

Candidate additions:

- realized-cap based measures
- holder/UTXO age structure
- exchange flows
- network activity

Each layer keeps its own availability mask.

## Temporal scales

The first implementation should support configurable scales rather than hard-code a
single list. A practical initial set is:

```text
1h
4h
1d
1w
1m
```

For early Bitcoin history, only scales justified by the source data are populated.

## Per-scale state

For each `(t, tau)`, compute a transparent feature vector. The first version should
prefer robust, interpretable features over many indicators.

Candidate normalized dimensions:

```text
trend
momentum
volatility
drawdown_pressure
range_position
volume_pressure
```

These are observations, not predictions.

## CDS quantities

The first empirical definitions are intentionally provisional and must remain
inspectable.

### Stability

A bounded score describing how internally persistent the current per-scale regime is.
It should combine persistence, directional consistency, and disturbance pressure
without using future observations.

### Cross-scale coherence

Agreement of regime state across available temporal scales at the same historical
time. Coherence is not required to mean equal raw returns; it measures structural
agreement after scale normalization.

### Persistence

How long the inferred state has remained within its current regime using only elapsed
history.

### Transition pressure

A descriptive quantity that increases when stability deteriorates, disturbances rise,
or neighboring scales lose coherence. It is a hypothesis variable until validated.

### Stability basin

A later experiment: perturb current normalized observations and measure how much
perturbation is required to change the selected regime.

## Regime labels

Do not optimize labels to match famous Bitcoin tops and bottoms. Define a reproducible
forward-looking evaluation label independently of the CDS score.

A first benchmark can label future windows from forward log return and realized
volatility into broad states such as:

- expansion up
- expansion down
- range / low-directionality

The label generator may inspect the future only for evaluation. The CDS feature and
score pipeline may not.

## Evaluation

Primary experiment:

> Does deterioration in stability/coherence at time t contain information about a
> regime transition after t?

Use walk-forward evaluation. Report at minimum:

- transition-event precision/recall at predeclared horizons,
- lead-time distribution,
- false-alarm rate,
- results by historical era,
- results by temporal scale,
- ablation of each field component,
- comparison against simple baselines such as volatility and moving-average regime
  changes.

Do not report only hand-picked historical examples.

## Visualization

The canonical visualization is a **Bitcoin Temporal Stability Field**:

```text
                       historical time →
1m  ─────────────────────────────────────────
1w  ─────────────────────────────────────────
1d  ─────────────────────────────────────────
4h  ─────────────────────────────────────────
1h  ─────────────────────────────────────────
     stability / regime / coherence by cell
```

The first interactive view should contain:

1. logarithmic BTC price over the full available history,
2. aligned heatmap with time on x and temporal scale on y,
3. selectable field metric: stability, regime, coherence, transition pressure,
4. transition markers generated by the independent evaluation labels,
5. hover inspection showing only information available at that historical point.

A later 3D view may render `time × temporal scale × stability` as a landscape, but
the 2D heatmap remains the scientific reference because it is easier to inspect and
compare.

## Historical events as overlays, not inputs

Halvings, known cycle theories, Elliott-wave interpretations, macro events, and other
external narratives should initially be overlays used after the field has been
computed. They must not be baked into the first stability model.

This lets us ask whether an independently derived CDS structure aligns with, conflicts
with, or adds information to those theories.

## Implementation phases

### v0.1 — specification and deterministic field prototype

- temporal-field data structures,
- OHLCV ingestion contract,
- resampling rules,
- causal feature computation,
- availability masks,
- synthetic deterministic fixture,
- stability/coherence prototype,
- heatmap-ready JSON export,
- unit tests for causality and deterministic behavior.

### v0.2 — historical Bitcoin dataset

- choose and document defensible source(s),
- ingest the longest reliable price history,
- record venue/source transitions explicitly,
- build 1d/1w/1m whole-history field,
- add finer scales only where source coverage permits.

### v0.3 — transition experiment

- freeze regime-label definition,
- freeze baseline metrics,
- walk-forward evaluation,
- lead-time and false-alarm analysis,
- historical-era robustness checks.

### v0.4 — richer constraint fields

Add derivatives, liquidity, and on-chain layers without rewriting missing historical
periods.

## Non-claims

Bitcoin Temporal Field does not currently claim:

- that timeframes are physical fields,
- that CDS predicts Bitcoin,
- that Bitcoin follows a fixed cycle,
- that cross-scale coherence is a profitable signal,
- that a stability score is a probability,
- or that the framework is ready for live trading.

The field language is an operational mathematical representation to be tested against
data. Physical or philosophical field analogies remain hypotheses unless independently
supported.


## Historical data provider — first empirical source

The first connected provider is the **Coin Metrics Community API v4** asset-metrics
endpoint. The initial fetch intentionally requests only daily `PriceUSD` for BTC.
This gives the whole-history layer a simple, inspectable starting series before we add
venue-specific OHLCV and higher-frequency fields.

Run:

```bash
python examples/fetch_bitcoin_history.py
```

Optional bounded request:

```bash
python examples/fetch_bitcoin_history.py --start 2010-07-17 --end 2020-12-31
```

Outputs:

```text
data/bitcoin/btc_priceusd_1d.csv
data/bitcoin/btc_priceusd_1d.provenance.json
```

The provenance sidecar records provider, endpoint, requested coverage, actual first and
last observations, timezone, retrieval date, and a license/redistribution reminder.

Important distinction: Coin Metrics `PriceUSD` is an asset-level price metric, not a
single-exchange OHLCV candle series. It is suitable for the first long-history price
field, while venue-specific OHLCV will be connected separately. Kraken's downloadable
OHLCVT archive is a candidate for the later market microstructure/high-frequency layer
because it provides multiple candle intervals from the beginning of each Kraken market.

The repository does not commit downloaded market data by default. This avoids silently
freezing a third-party dataset or redistributing it without an explicit data policy.
