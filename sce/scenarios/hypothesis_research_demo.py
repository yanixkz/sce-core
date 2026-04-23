from __future__ import annotations

from dataclasses import dataclass

from sce.core.backbone import DecisionBackboneExtractor


@dataclass(frozen=True)
class ResearchHypothesis:
    name: str
    prior: float
    supporting_evidence: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]


def _confidence(hypothesis: ResearchHypothesis, evidence_weights: dict[str, float]) -> float:
    support = sum(evidence_weights[item] for item in hypothesis.supporting_evidence)
    contradiction = sum(evidence_weights[item] for item in hypothesis.contradicting_evidence)
    confidence = hypothesis.prior + support - contradiction
    return max(0.0, min(1.0, confidence))


def _score_rows(hypotheses: list[ResearchHypothesis], evidence_weights: dict[str, float]) -> list[dict]:
    rows = []
    for hypothesis in hypotheses:
        support = sum(evidence_weights[item] for item in hypothesis.supporting_evidence)
        contradiction = sum(evidence_weights[item] for item in hypothesis.contradicting_evidence)
        rows.append(
            {
                "hypothesis": hypothesis.name,
                "prior": hypothesis.prior,
                "support": support,
                "contradiction": contradiction,
                "confidence": _confidence(hypothesis, evidence_weights),
            }
        )
    return sorted(rows, key=lambda item: item["confidence"], reverse=True)


def run_hypothesis_research_demo() -> dict:
    """Show SCE as a compact research loop over competing hypotheses."""

    research_question = "Why are supplier escalations increasing?"
    evidence_weights = {
        "late_delivery_spike": 0.24,
        "missing_certificates": 0.18,
        "invoice_disputes": 0.12,
        "new_supplier_region": 0.10,
        "marketing_noise": 0.05,
        "old_positive_history": 0.08,
    }
    hypotheses = [
        ResearchHypothesis(
            name="supplier_quality_degradation",
            prior=0.34,
            supporting_evidence=("late_delivery_spike", "missing_certificates", "invoice_disputes"),
            contradicting_evidence=("old_positive_history",),
        ),
        ResearchHypothesis(
            name="regional_onboarding_gap",
            prior=0.26,
            supporting_evidence=("new_supplier_region", "missing_certificates"),
            contradicting_evidence=(),
        ),
        ResearchHypothesis(
            name="reporting_artifact",
            prior=0.22,
            supporting_evidence=("marketing_noise",),
            contradicting_evidence=("late_delivery_spike", "invoice_disputes"),
        ),
    ]

    scores = _score_rows(hypotheses, evidence_weights)
    selected_hypothesis = scores[0]["hypothesis"]

    reasoning_graph = {
        "late_delivery_spike": ["supplier_quality_degradation"],
        "missing_certificates": ["supplier_quality_degradation", "regional_onboarding_gap"],
        "invoice_disputes": ["supplier_quality_degradation"],
        "new_supplier_region": ["regional_onboarding_gap"],
        "old_positive_history": ["counter_evidence_note"],
        "counter_evidence_note": [],
        "marketing_noise": ["reporting_artifact"],
        "reporting_artifact": [],
        "supplier_quality_degradation": ["research_decision"],
        "regional_onboarding_gap": ["research_decision"],
    }
    sources = set(evidence_weights)
    backbone = DecisionBackboneExtractor().extract(
        reasoning_graph,
        sources=sources,
        targets={"research_decision"},
    )

    next_actions = [
        "audit last 30 delayed deliveries",
        "sample missing certificate cases",
        "interview escalation owner for invoice disputes",
    ]

    return {
        "research_question": research_question,
        "selected_hypothesis": selected_hypothesis,
        "scores": scores,
        "backbone_nodes": sorted(backbone.backbone_nodes),
        "dangling_nodes": sorted(backbone.dangling_nodes),
        "next_actions": next_actions,
        "summary": (
            "SCE ranks competing hypotheses, separates decision-carrying evidence from dangling context, "
            "and turns the winning hypothesis into concrete research actions."
        ),
    }


def _format_scores(scores: list[dict]) -> str:
    lines = [
        "hypothesis                       prior   support   contra   confidence",
        "---------------------------------------------------------------------",
    ]
    for item in scores:
        lines.append(
            f"{item['hypothesis']:<32} "
            f"{item['prior']:>5.2f}   "
            f"{item['support']:>7.2f}   "
            f"{item['contradiction']:>6.2f}   "
            f"{item['confidence']:>10.2f}"
        )
    return "\n".join(lines)


def _bullet(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] or ["- none"]


def format_hypothesis_research_demo(result: dict) -> str:
    winner = result["scores"][0]
    runner_up = result["scores"][1] if len(result["scores"]) > 1 else None
    margin = winner["confidence"] - runner_up["confidence"] if runner_up else 0.0

    return "\n".join(
        [
            "SCE Hypothesis Research Demo",
            "============================",
            "",
            "Research showcase: decide, explain, improve.",
            "",
            "Research question",
            "-----------------",
            result["research_question"],
            "",
            "1) Competing hypotheses",
            "-----------------------",
            _format_scores(result["scores"]),
            "",
            "Selected hypothesis",
            "-------------------",
            (
                f"{result['selected_hypothesis']} "
                f"(confidence {winner['confidence']:.2f}, +{margin:.2f} vs runner-up)"
            ),
            (
                f"Why it won: support {winner['support']:.2f} outweighed "
                f"contradiction {winner['contradiction']:.2f} on prior {winner['prior']:.2f}."
            ),
            "",
            "2) Decision-carrying evidence",
            "------------------------------",
            "Decision-carrying evidence:",
            *_bullet(result["backbone_nodes"]),
            "",
            "Dangling context (non-carrying):",
            *_bullet(result["dangling_nodes"]),
            "",
            "3) Next research actions",
            "------------------------",
            *_bullet(result["next_actions"]),
            "",
            "Summary",
            "-------",
            result["summary"],
        ]
    )
