# Selection Landscape Explorer

Selection Landscape Explorer is a deterministic scientific toy model for illustrating a CDS idea:

> A possibility space contains many candidates with different stability scores. Selection emerges from the landscape itself.

It is not a prediction system, an intelligence benchmark, a meaning-discovery process, or a claim about consciousness. It is a reproducible selection experiment with transparent arithmetic.

## Conceptual pipeline

```text
Possibility Space
↓
Scoring Dimensions
↓
Stability Landscape
↓
Selection
```

## Possibility space

The example creates a fixed-size population of numbered candidates. The candidates do not model a real domain; they are points in a toy possibility space.

## Candidate population

Each candidate receives five deterministic dimensions:

- `coherence`: how internally aligned the toy candidate is.
- `entropy`: how uncertain or underspecified it is.
- `support`: how much toy evidence or reinforcement it has.
- `conflict`: how much toy contradiction or constraint pressure it has.
- `cost`: how expensive it is to select or transition to it.

## Stability score

The demo uses the same weighted CDS stability formulation used by the core scorer:

```text
stability = coherence - 0.5 * cost - 0.8 * conflict - 0.4 * entropy + 0.6 * support
```

Higher stability ranks earlier. Lower stability ranks later.

## Stability distribution

The full ranked population is summarized as a histogram so the CLI can show the landscape, not only the winner:

```text
1.00 | *
0.90 | ***
0.80 | *****
0.70 | ********
```

The exact bars depend on the deterministic population size and scores.

## Emergence of ranking

The ranking is not manually assigned. It emerges from applying one scoring rule to every candidate in the possibility space sample. The demo reports the best, median, and worst candidates to show that selection is a property of the whole stability landscape.

## CLI usage

```bash
sce demo selection-landscape
sce demo selection-landscape --json
python examples/selection_landscape_demo.py
```

This example is intended as a bridge between the Cyrillic Babel possibility-space demo and future Constraint Sweep experiments.
