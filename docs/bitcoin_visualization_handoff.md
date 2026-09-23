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
