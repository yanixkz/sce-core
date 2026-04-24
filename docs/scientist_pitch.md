# Scientist Pitch (Outreach/Readiness)

## One-sentence description

SCE Core is an early computational framework for exploring how candidate system states become stable or unstable under explicit constraints.

## Why this may be interesting to researchers

SCE Core may be useful as a compact research sandbox for Constraint-Driven Stability (CDS), especially when you want:

- reproducible toy models with deterministic behavior,
- explicit candidate/state scoring and ranking,
- clear regime selection under hard/soft constraints,
- quick sensitivity experiments to inspect stability-margin shifts,
- inspectable decision/evidence structure rather than opaque outputs,
- a lightweight platform for testing how constraint choices change selected trajectories.

## What can be run today

The following commands are available now:

```bash
sce demo resource-stability
python examples/resource_stability_walkthrough.py
python examples/resource_stability_sensitivity.py
sce demo epidemic-regime
python examples/epidemic_regime_walkthrough.py
sce demo hypothesis
```

## What SCE is not (important non-claims)

SCE Core is currently:

- not a validated scientific simulator,
- not a replacement for domain-specific models,
- not an empirical scientific result yet,
- not a “theory of everything”.

Current outputs should be treated as transparent computational artifacts for discussion, critique, and iterative refinement.

## What feedback is needed

Feedback from scientists/labs is especially helpful on:

- whether the CDS framing is scientifically useful,
- which toy systems are worth modeling next,
- what constraints/metrics are missing for credibility,
- what would make the examples more methodologically convincing,
- whether notebooks, datasets, or baseline comparisons would make evaluation easier.

## Collaboration directions

Near-term collaboration ideas:

- reproduce known toy dynamics in this framework,
- add domain-specific constraints for candidate regimes,
- compare outputs against known baseline models,
- create small benchmark datasets for repeatable checks,
- validate sensitivity behavior under controlled parameter sweeps,
- design attractor/regime recurrence experiments.

## Short outreach email template

Subject: Quick scientific feedback request on CDS toy framework

Hi Dr. [Name],

I’m building SCE Core, an early computational framework for exploring constraint-driven stability in small deterministic toy systems.

At this stage, I’m **not** claiming validated scientific results. I’m trying to make assumptions, candidate scoring, and regime selection explicit so the models are easy to inspect and critique.

If you have 15–20 minutes, I’d value your feedback on whether this framing is scientifically useful and what would make the examples more credible (metrics, constraints, baselines, or datasets).

If useful, I can send a minimal run path and outputs for:
- `resource-stability` (+ sensitivity grid)
- `epidemic-regime`
- `hypothesis`

Thanks for considering it,
[Your Name]
[GitHub/Project link]
