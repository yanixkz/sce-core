from __future__ import annotations

from sce.core.backbone import DecisionBackboneExtractor
from sce.core.episode_memory import EpisodeMemory
from sce.core.evolution_control import EvolutionErrorTracker
from sce.core.planning import MemoryAwarePlanner, ReliabilityAwarePlanner, ToolPlanner
from sce.core.types import State


def _score_rows(scores) -> list[dict]:
    rows = []
    for score in scores:
        row = {
            "plan_name": score.plan.name,
            "base_score": score.base_score,
            "memory_bias": score.memory_bias,
            "total_score": score.total_score,
        }
        if hasattr(score, "reliability"):
            row["reliability"] = score.reliability
            row["reliability_bonus"] = score.reliability_bonus
        rows.append(row)
    return rows


def run_supplier_risk_demo() -> dict:
    """One compact SCE story: decide, explain, remember, improve."""

    state = State("supplier_context", {"entity": "supplier A", "risk": "high"})
    goal = "assess supplier risk"

    base_planner = ToolPlanner()
    memory = EpisodeMemory()
    memory_planner = MemoryAwarePlanner(base_planner, memory)
    candidates = base_planner.candidates(state, goal)

    first_scores = _score_rows(memory_planner.score(candidates, state, goal))
    first_choice = memory_planner.plan(state, goal, candidates)

    reasoning_graph = {
        "late_delivery": ["supplier_risk"],
        "invoice_risk": ["supplier_risk"],
        "missing_certificate": ["supplier_risk"],
        "supplier_risk": ["escalation_plan"],
        "old_positive_history": ["context_note"],
        "context_note": [],
        "marketing_tag": ["unrelated_note"],
        "unrelated_note": [],
    }
    backbone = DecisionBackboneExtractor().extract(
        reasoning_graph,
        sources={
            "late_delivery",
            "invoice_risk",
            "missing_certificate",
            "old_positive_history",
            "marketing_tag",
        },
        targets={"escalation_plan"},
    )

    tracker = EvolutionErrorTracker()
    tracker.record_step("score_supplier_risk", predicted_value=0.90, actual_value=0.72)
    tracker.record_step("select_escalation_plan", predicted_value=0.78, actual_value=0.70)
    tracker.record_step("execute_followup", predicted_value=0.74, actual_value=0.73)
    reliability_report = tracker.report()

    for plan in candidates:
        remembered_reliability = {
            "supplier_risk_plan": 0.1,
            "escalation_plan": reliability_report.reliability,
            "monitor_plan": 0.2,
        }[plan.name]
        memory.remember(
            state,
            goal,
            plan,
            success=True,
            reward=0.0,
            reason="supplier_risk_demo_memory",
            reliability=remembered_reliability,
        )

    reliability_planner = ReliabilityAwarePlanner(memory_planner, reliability_weight=1.0)
    final_scores = _score_rows(reliability_planner.score(candidates, state, goal))
    final_choice = reliability_planner.plan(state, goal, candidates)

    return {
        "goal": goal,
        "state": state.data,
        "first_choice": first_choice.name,
        "final_choice": final_choice.name,
        "changed_choice": first_choice.name != final_choice.name,
        "first_scores": first_scores,
        "final_scores": final_scores,
        "backbone_nodes": sorted(backbone.backbone_nodes),
        "dangling_nodes": sorted(backbone.dangling_nodes),
        "cumulative_error": reliability_report.cumulative_error,
        "reliability": reliability_report.reliability,
        "reliability_trend": reliability_report.trend,
        "remembered_episodes": len(memory.episodes),
        "summary": (
            "SCE chooses a plan, explains which facts carried the decision, remembers reliability, "
            "and uses that memory to improve the next choice."
        ),
    }


def _format_basic_scores(scores: list[dict]) -> str:
    lines = ["plan                         base    memory   total", "------------------------------------------------------"]
    for item in scores:
        lines.append(
            f"{item['plan_name']:<28} "
            f"{item['base_score']:>5.2f}   "
            f"{item['memory_bias']:>6.2f}   "
            f"{item['total_score']:>5.2f}"
        )
    return "\n".join(lines)


def _format_reliability_scores(scores: list[dict]) -> str:
    lines = [
        "plan                         base    memory   rel   total",
        "----------------------------------------------------------",
    ]
    for item in scores:
        lines.append(
            f"{item['plan_name']:<28} "
            f"{item['base_score']:>5.2f}   "
            f"{item['memory_bias']:>6.2f}   "
            f"{item.get('reliability', 0.0):>4.2f}   "
            f"{item['total_score']:>5.2f}"
        )
    return "\n".join(lines)


def _bullet(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] or ["- none"]


def format_supplier_risk_demo(result: dict) -> str:
    changed = "YES" if result["changed_choice"] else "NO"
    return "\n".join(
        [
            "SCE Supplier Risk Demo",
            "======================",
            "",
            "Decide. Explain. Improve.",
            "",
            f"Goal:  {result['goal']}",
            f"State: {result['state']}",
            "",
            "1) Decide",
            "---------",
            _format_basic_scores(result["first_scores"]),
            "",
            f"Initial selected plan: {result['first_choice']}",
            "",
            "2) Explain",
            "----------",
            "Decision-carrying facts:",
            *_bullet(result["backbone_nodes"]),
            "",
            "Dangling context:",
            *_bullet(result["dangling_nodes"]),
            "",
            "3) Measure reliability",
            "----------------------",
            f"cumulative_error: {result['cumulative_error']:.2f}",
            f"reliability:      {result['reliability']:.2f}",
            f"trend:            {result['reliability_trend']}",
            "",
            "4) Improve",
            "----------",
            f"Remembered episodes: {result['remembered_episodes']}",
            _format_reliability_scores(result["final_scores"]),
            "",
            f"Final selected plan: {result['final_choice']}",
            f"Changed choice: {changed}",
            "",
            "Summary",
            "-------",
            result["summary"],
        ]
    )
