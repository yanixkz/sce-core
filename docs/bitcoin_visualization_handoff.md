# Visualization handoff: BTC regime-event markers

Owner: Visualization agent
Source of truth: Research / SCE Core

## Goal
Add an event layer to the existing Bitcoin Temporal Field timeline without duplicating research logic in the UI.

## Data contract
Visualization consumes `events[]` produced by Research. Each event should support:
- `time`: confirmed regime-transition timestamp
- `from_regime`, `to_regime`
- `detected`: whether CDS alarm occurred in the causal lookback
- `signal_time`: most recent qualifying CDS alarm before transition
- `lead_days`
- `classification`: `hit | miss`
- `propagation`: optional multiscale signature with `first_scale`, `order`, `direction`, `coverage`
- `signal_snapshot`: optional `coherence`, `transition_pressure`, `mean_stability`

Research may also emit false-alarm episodes:
- `start_time`, `end_time`
- `classification: false_alarm`
- optional propagation signature

## UI requirements
On the main BTC time axis overlay:
1. CDS alarm marker at `signal_time`.
2. Confirmed transition marker at `time`.
3. Visually connect alarm -> transition and show lead time.
4. False-alarm episodes must be visually distinct and must not look like confirmed transitions.
5. Filters: All / Hits / Misses / False alarms / Bull transitions / Bear transitions.
6. Clicking a marker persists a detail panel with date, BTC price if available, from/to regime, lead time, coherence, transition pressure, mean stability, and propagation order.
7. Keep the existing Time Scanner synchronized with event selection.
8. Do not fabricate minute/high-resolution history. Render a propagation signature only when Research provides it.
9. Historical Coin Metrics 1d/1w/1m layers are causal observation horizons, not resampled candles; preserve that wording in provenance/help text.
10. Default view should remain readable over 2010-present; event markers should cluster/declutter at long zoom and expand at closer zoom.

## Suggested visual grammar
- alarm: warning tick/triangle
- confirmed transition: diamond/vertical line
- hit: connected alarm -> transition pair
- miss: transition with no preceding alarm
- false alarm: muted alarm marker/band
- bull/bear direction encoded independently from hit/miss state

Do not hard-code the old 78.09% into the UI. Read current evaluation output because Research metrics can change as methodology is corrected.


## Price Response / Trading View (required)

The visualization agent should add a dedicated **Price Response** research panel sourced only from `bitcoin_regime_evaluation.json` fields `price_response_summary`, `price_responses`, `event_window_5d_summary`, `event_window_5d_by_transition`, and `event_windows_5d`.

### Primary view
- Event-centered price trajectory with x-axis D-5 ... D0 ... D+30 and price normalized to 0% at D0.
- Regime selector: All, 0→1, 1→0, 0→-1, -1→0.
- Show median return trajectory plus individual-event traces on demand; never fabricate/interpolate missing observations.
- Visually align D0 with the coherence/stability trajectory for D-5...D+5.

### Trading-distribution view
For selected regime show:
- median returns at +1,+2,+3,+5,+10,+20,+30 days;
- positive-return frequency for each horizon;
- median MFE and MAE over 30 days;
- first-touch probabilities for ±1%, ±2%, ±3%, ±5%, ±10%.
Use paired horizontal bars for UP-first vs DOWN-first so adverse excursion is visible, not only terminal return.

### Event explorer
- sortable list of all transition events;
- selecting an event shows date, D0 BTC price, pre-5d return, returns by horizon, MFE/MAE, first-touch day for every level, from/to regime;
- synchronize selection with the existing Time Scanner and event markers.

### Interpretation / safeguards
- Label this **historical conditional distribution**, not a trading signal or forecast.
- Do not call event recall “accuracy”.
- Show sample size N prominently for every regime/filter.
- Keep future-derived regime labels visually distinct from causal CDS features.
- Add a visible warning when a subgroup is small.
- No leverage/PnL projection in this panel yet.

### Data contract
The Research agent now emits all required raw event records and summaries. Visualization must consume those fields directly; do not hard-code percentages or recompute alternative labels in the frontend.
