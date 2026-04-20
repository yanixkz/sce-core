# SCE Core in one page

SCE Core began with a simple question:

> Why does chaos become structure?

Across many domains — water vortices, cells, markets, neural networks, galaxies — stable forms appear from moving systems. SCE Core is an attempt to turn that intuition into a computational model for AI.

## Core principle

SCE Core is based on **Constraint-Driven Stability (CDS)**:

```text
Stable structures emerge when information and energy pass through constraints over time and settle into self-reinforcing regimes.
```

For AI systems, this becomes:

```text
state + constraints + scoring → stable admissible state
```

## Why AI needs this

Most AI systems generate answers.

But they usually do not track:

- which answer is stable
- which answer is contradicted
- which constraints are active
- why a belief changed
- what would destabilise it

SCE Core adds a reasoning layer:

```text
LLM → proposes hypotheses
SCE → filters, scores, selects, explains
```

In short:

```text
LLMs propose. SCE decides.
```

## Stability function

```text
Stab(x) = a·Coh(x) − b·Cost(x) − c·Conf(x) − d·Ent(x) + e·Support(x)
```

Where:

- `Coh` = coherence
- `Cost` = transition or maintenance cost
- `Conf` = conflict
- `Ent` = uncertainty
- `Support` = evidence / links / history

## What the prototype does

SCE Core models data as evolving states instead of static facts.

It currently includes:

- state / transition / constraint / link model
- candidate generation
- stability scoring
- attractor detection
- graph query layer
- explainability layer
- PostgreSQL persistence phase 1
- demos for supplier reliability, conflicting memory, LLM memory, and contract risk

## The point

SCE Core is not trying to replace LLMs.

It tries to answer a different question:

```text
Given several possible states, which one is most stable under constraints — and why?
```

That makes it useful for:

- AI agent memory
- decision systems
- knowledge graphs
- contract and supplier risk
- explainable reasoning layers

## Longer origin

See:

```text
docs/origin.md
```

SCE Core is a research prototype. Not production-ready. All claims are exploratory.
