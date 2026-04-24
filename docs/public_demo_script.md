# Public Demo Script (5–7 minutes)

Audience: scientists, technical collaborators, and early users.
Tone: clear, humble, scientific, non-hyped.

## 0) One-sentence framing (15–20 sec)

SCE Core is an early computational framework for testing **Constraint-Driven Stability (CDS)** ideas in inspectable decision workflows, not a finished predictive product.

---

## 1) CDS formula + plain-language explanation (40–60 sec)

Use this formula:

\[
\mathrm{CDS} = \max_{\pi \in \Pi} \; S(\pi) \quad \text{subject to constraints } C
\]

Talk track:
- We consider candidate trajectories or regimes \(\pi\).
- We score each by a stability functional \(S(\pi)\).
- We only accept candidates that satisfy explicit constraints \(C\) (capacity, risk limits, intervention bounds, etc.).
- SCE operationalizes this by ranking constrained options and exposing *why* one carries versus others.

Plain-language line:
> “Pick the most stable option you can, but only inside the real constraints of the system.”

---

## 2) Resource-stability demo (60–75 sec)

Command:

```bash
sce demo resource-stability
```

What to narrate:
- This is a compact toy environment with resource pressure and population dynamics.
- SCE generates deterministic candidate regimes, checks constraints, and ranks by stability.
- Highlight: selected regime, non-selected alternatives, and concrete follow-up actions.
- Emphasize this is a **research scaffold**, not an ecological forecasting claim.

---

## 3) Resource-stability sensitivity grid (45–60 sec)

Reference doc: `docs/resource_stability_sensitivity.md`

What to narrate:
- We perturb key assumptions/parameters and observe whether selection is robust.
- Stable choices that persist across the grid are more credible.
- Regime flips under small perturbations indicate fragility and where more data is needed.

Key line:
> “Sensitivity behavior is often more informative than a single best-run output.”

---

## 4) Epidemic-regime demo (60–75 sec)

Command:

```bash
sce demo epidemic-regime
```

What to narrate:
- Same CDS workflow in a different domain: spread dynamics under capacity/intervention constraints.
- Show ranked regimes and rationale under constraints.
- Explicit non-claim: this is *not* a clinical or public-health forecasting system; it is a constrained stability modeling exercise.

---

## 5) Hypothesis research demo (45–60 sec)

Command:

```bash
sce demo hypothesis
```

What to narrate:
- SCE ranks competing hypotheses and separates decision-carrying evidence from background context.
- It produces structured next actions for data collection or experiment design.
- Position this as support for disciplined research iteration, not automated scientific truth.

---

## 6) AI vs SCE comparison via `/compare` (45–60 sec)

Command example:

```bash
curl -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "goal":"assess supplier risk",
    "context":{"supplier_id":"supplier A","claim":"supplier may be unreliable"},
    "constraints":["prefer external verification"],
    "execute":false
  }'
```

What to narrate:
- `/compare` shows side-by-side outputs for the same input:
  - a generic one-shot baseline answer,
  - SCE’s constrained, ranked, inspectable result.
- The point is not “AI bad, SCE good”; the point is **inspectability, constraint handling, and reproducibility**.

---

## 7) Memory / reliability / graph inspection (50–70 sec)

Endpoints:
- `GET /memory`
- `GET /reliability`
- `GET /graph`

What to narrate:
- Memory: what prior episodes are retained and can influence reselection pressure.
- Reliability: empirical quality signals accumulated over outcomes.
- Graph: inspectable structure of decision logic and links between options/evidence.
- Message: SCE is designed so collaborators can audit internal structure, not only consume final answers.

---

## 8) What SCE does **not** claim (25–35 sec)

State explicitly:
- Not a universal predictor.
- Not validated for high-stakes deployment by default.
- Not a replacement for domain expertise, experiments, or governance.
- Not evidence of causal truth from ranking alone.

---

## 9) Feedback and collaboration needed (25–35 sec)

Ask for:
- Domain-specific constraint sets worth encoding.
- Benchmark scenarios with known outcomes for stress-testing stability selection.
- Failure cases where rankings look plausible but are wrong.
- Collaborations on calibration, sensitivity protocols, and reproducibility criteria.

Close line:
> “If you bring rigorous problems and failure cases, SCE can be a useful shared lab for constrained decision science.”
