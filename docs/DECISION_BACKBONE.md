# Decision Backbone

SCE Core models decisions as graph-shaped state evolution:

```text
sources / evidence
↓
intermediate states
↓
constraints and transitions
↓
decision / action targets
```

A decision graph can contain many connected branches that are not actually relevant to the final decision. SCE uses a **decision backbone** to separate the part of the graph that carries a decision from dangling or irrelevant branches.

---

## Core idea

Given a directed graph, a set of source nodes, and a set of target nodes:

```text
forward  = nodes reachable from sources
backward = nodes that can reach targets
backbone = forward ∩ backward
dangling = forward - backbone
```

The backbone contains nodes that are both:

- supported by evidence or source state, and
- able to contribute to a target decision or action.

Dangling nodes may be connected to the graph, but they do not carry the decision from sources to targets.

---

## Why this matters

Most agent systems can explain decisions with a score or a generated text explanation.

SCE can additionally expose a structural explanation:

```text
which states, facts, constraints, and transitions actually carry the decision?
```

This is useful for:

- supplier risk decisions
- contract risk checks
- compliance workflows
- incident response
- memory audit and replay
- reasoning graph pruning

---

## Example

```text
late_delivery ─┐
invoice_risk ──┼→ supplier_risk → escalate
old_note ──────┘
marketing_tag ────────────────┐
                               └→ dangling branch
```

If `late_delivery`, `invoice_risk`, and `supplier_risk` connect evidence to the `escalate` target, they belong to the decision backbone.

If `marketing_tag` is reachable from the source but cannot reach the decision target, it is dangling.

---

## Relationship to SCE

Decision backbone extraction complements existing SCE mechanisms:

- scoring chooses the most stable or useful state/plan
- memory biases future planning
- exploration can try alternatives
- backbone extraction explains which graph structure carried the decision

It does not replace scoring or memory. It adds graph-level observability.

---

## Planned implementation

The initial implementation is intentionally general and graph-based:

- no grid-specific assumptions
- no lattice-specific code
- no dependency on external solvers
- works on directed reasoning graphs

Future work:

- weighted decision backbones
- constraint-aware backbones
- memory-aware backbones
- supplier risk backbone demo
- integration with graph export and browser UI
