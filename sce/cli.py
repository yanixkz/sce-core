from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class DemoSpec:
    name: str
    title: str
    runner: Callable[[], dict]
    formatter: Callable[[dict], str]


def _pretty_json_formatter(result: dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False)


def _demo_spec_from_module(
    *, name: str, title: str, module: str, run_fn: str, format_fn: str | None = None
) -> Callable[[], DemoSpec]:
    def _factory() -> DemoSpec:
        demo_module = import_module(module)
        runner = getattr(demo_module, run_fn)
        formatter = getattr(demo_module, format_fn) if format_fn else _pretty_json_formatter
        return DemoSpec(name=name, title=title, runner=runner, formatter=formatter)

    return _factory


DEMO_REGISTRY: dict[str, Callable[[], DemoSpec]] = {
    "supplier-risk": _demo_spec_from_module(
        name="supplier-risk",
        title="Supplier Risk Agent",
        module="sce.scenarios.supplier_risk_demo",
        run_fn="run_supplier_risk_demo",
        format_fn="format_supplier_risk_demo",
    ),
    "hypothesis": _demo_spec_from_module(
        name="hypothesis",
        title="Hypothesis Research (Flagship)",
        module="sce.scenarios.hypothesis_research_demo",
        run_fn="run_hypothesis_research_demo",
        format_fn="format_hypothesis_research_demo",
    ),
    "resource-stability": _demo_spec_from_module(
        name="resource-stability",
        title="Resource Stability (Scientific)",
        module="sce.scenarios.resource_stability_demo",
        run_fn="run_resource_stability_demo",
        format_fn="format_resource_stability_demo",
    ),
    "adaptive-agent": _demo_spec_from_module(
        name="adaptive-agent",
        title="Adaptive Agent",
        module="sce.scenarios.adaptive_agent_demo",
        run_fn="run_adaptive_agent_demo",
        format_fn="format_adaptive_agent_demo",
    ),
    "exploration": _demo_spec_from_module(
        name="exploration",
        title="Exploration Policy",
        module="sce.scenarios.exploration_demo",
        run_fn="run_exploration_demo",
        format_fn="format_exploration_demo",
    ),
    "controlled-evolution": _demo_spec_from_module(
        name="controlled-evolution",
        title="Controlled Evolution",
        module="sce.scenarios.controlled_evolution_demo",
        run_fn="run_controlled_evolution_demo",
        format_fn="format_controlled_evolution_demo",
    ),
    "reliability-planning": _demo_spec_from_module(
        name="reliability-planning",
        title="Reliability-Aware Planning",
        module="sce.scenarios.reliability_aware_planning_demo",
        run_fn="run_reliability_aware_planning_demo",
        format_fn="format_reliability_aware_planning_demo",
    ),
    "decision-backbone": _demo_spec_from_module(
        name="decision-backbone",
        title="Decision Backbone",
        module="sce.scenarios.decision_backbone_demo",
        run_fn="run_decision_backbone_demo",
        format_fn="format_decision_backbone_demo",
    ),
    "planning": _demo_spec_from_module(
        name="planning",
        title="Planning",
        module="sce.scenarios.planning_demo",
        run_fn="run_planning_demo",
    ),
}
DEMO_CHOICES = tuple(DEMO_REGISTRY)
DEFAULT_DEMO = "supplier-risk"
LEGACY_RUN_ALIASES = (
    "run-demo",
    "run-supplier-risk-demo",
    "run-supplier-risk-demo-pretty",
    "run-conflict-demo",
    "run-llm-demo",
    "run-llm-planning-demo",
    "run-contract-demo",
    "run-agent-demo",
    "run-goal-agent-demo",
    "run-action-demo",
    "run-learning-demo",
    "run-learning-planning-demo",
    "run-memory-aware-planning-demo",
    "run-adaptive-agent-demo",
    "run-adaptive-agent-demo-pretty",
    "run-exploration-demo",
    "run-exploration-demo-pretty",
    "run-decision-backbone-demo",
    "run-decision-backbone-demo-pretty",
    "run-controlled-evolution-demo",
    "run-controlled-evolution-demo-pretty",
    "run-reliability-aware-planning-demo",
    "run-reliability-aware-planning-demo-pretty",
    "run-hypothesis-research-demo",
    "run-hypothesis-research-demo-pretty",
    "run-multi-agent-demo",
    "run-tools-demo",
    "run-planning-demo",
    "run-plan-scoring-demo",
    "run-cognitive-agent-demo",
    "run-llm-voice-demo",
)


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def run_demo(name: str) -> dict:
    return DEMO_REGISTRY[name]().runner()


def format_demo(name: str, result: dict) -> str:
    return DEMO_REGISTRY[name]().formatter(result)


def render_ascii_graph(graph: dict) -> str:
    """Compatibility wrapper kept for tests and monkeypatching."""
    from sce.visualization.graph_ascii import render_ascii_graph as _render_ascii_graph

    return _render_ascii_graph(graph)


def _format_state_graph(graph: dict) -> str:
    return "\n".join(["State Graph", "===========", "", render_ascii_graph(graph)])


def _run_named_demo(name: str, as_json: bool = False) -> None:
    result = run_demo(name)
    if as_json:
        _print_json(result)
    else:
        print(format_demo(name, result))


def _list_demos() -> None:
    for name in DEMO_CHOICES:
        spec = DEMO_REGISTRY[name]()
        print(f"{spec.name}\t{spec.title}")


def _export_supplier_graph() -> dict:
    from sce.core.evolution import SCEEvolver
    from sce.core.queries import GraphQueryLayer
    from sce.core.scoring import SCEScoringEngine
    from sce.scenarios.supplier_reliability import make_supplier_reliability_scenario

    repo, start_state = make_supplier_reliability_scenario()
    scorer = SCEScoringEngine(repo)
    evolver = SCEEvolver(repo, scorer)
    evolver.evolve(start_state, max_steps=5, epsilon=0.001)
    return GraphQueryLayer(repo).export_graph_json()


def _register_legacy_aliases(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register deprecated run-* aliases retained for backward compatibility."""
    for alias in LEGACY_RUN_ALIASES:
        sub.add_parser(alias, help="Legacy alias (backward compatibility).")


def _register_graph_commands(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    export_graph_parser = sub.add_parser(
        "export-graph",
        help="Export supplier-risk graph as JSON for inspection.",
        description="Export the internal supplier-risk state graph as JSON.",
    )
    export_graph_parser.add_argument("--out", type=Path, default=None)
    visualize_graph_parser = sub.add_parser(
        "visualize-graph",
        help="Render supplier-risk graph as terminal ASCII.",
        description="Render the internal supplier-risk state graph as ASCII for terminal inspection.",
    )
    visualize_graph_parser.add_argument("--out", type=Path, default=None)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sce",
        description=(
            "SCE Core CLI — CDS demos for practical decision systems and scientific toy models."
        ),
        epilog=(
            "Primary surface:\n"
            "  sce demo\n"
            "  sce demo supplier-risk\n"
            "  sce demo hypothesis\n"
            "  sce demo resource-stability\n"
            "  sce demo list\n"
            "Graph inspection:\n"
            "  sce export-graph\n"
            "  sce visualize-graph\n"
            "Compatibility:\n"
            "  run-* commands are retained as legacy aliases."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        description=(
            "Canonical entrypoints: `sce demo`, `sce demo supplier-risk`, "
            "`sce demo hypothesis`, `sce demo resource-stability`, `sce demo list`."
        ),
    )
    demo_parser = sub.add_parser(
        "demo",
        help="Run flagship demos (`supplier-risk`, `hypothesis`, `resource-stability`) or list demos.",
        description=(
            "Run canonical SCE demos. Use `supplier-risk` for a practical product story "
            "`hypothesis` for competing hypotheses, and `resource-stability` for CDS toy modeling."
        ),
    )
    demo_parser.add_argument(
        "name",
        nargs="?",
        choices=("list", *DEMO_CHOICES),
        default=DEFAULT_DEMO,
        help="Demo name (default: supplier-risk). Use `list` to print all demo ids.",
    )
    demo_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw demo result as JSON instead of pretty narrative output.",
    )
    _register_graph_commands(sub)
    # Legacy run-* commands are intentionally kept for backward compatibility.
    _register_legacy_aliases(sub)
    sub.add_parser("explain-demo")
    sub.add_parser("print-migration")
    args = parser.parse_args()

    if args.command == "demo":
        if args.name == "list":
            _list_demos()
        else:
            _run_named_demo(args.name, as_json=args.json)
    elif args.command == "run-demo":
        from sce.scenarios.supplier_reliability import run_demo as run_supplier_reliability_demo

        _print_json(run_supplier_reliability_demo())
    elif args.command == "run-supplier-risk-demo":
        _print_json(run_demo("supplier-risk"))
    elif args.command == "run-supplier-risk-demo-pretty":
        _run_named_demo("supplier-risk")
    elif args.command == "run-conflict-demo":
        from sce.scenarios.conflicting_memory import run_conflicting_memory_demo

        _print_json(run_conflicting_memory_demo())
    elif args.command == "run-llm-demo":
        from sce.scenarios.llm_memory import run_llm_memory_demo

        _print_json(run_llm_memory_demo())
    elif args.command == "run-llm-planning-demo":
        from sce.scenarios.llm_planning_demo import run_llm_planning_demo

        _print_json(run_llm_planning_demo())
    elif args.command == "run-contract-demo":
        from sce.scenarios.contract_risk import run_contract_risk_demo

        _print_json(run_contract_risk_demo())
    elif args.command == "run-agent-demo":
        from sce.scenarios.agent_demo import run_agent_demo

        _print_json(run_agent_demo())
    elif args.command == "run-goal-agent-demo":
        from sce.scenarios.goal_agent_demo import run_goal_agent_demo

        _print_json(run_goal_agent_demo())
    elif args.command == "run-action-demo":
        from sce.scenarios.action_demo import run_action_demo

        _print_json(run_action_demo())
    elif args.command == "run-learning-demo":
        from sce.scenarios.learning_demo import run_learning_demo

        _print_json(run_learning_demo())
    elif args.command == "run-learning-planning-demo":
        from sce.scenarios.learning_planning_demo import run_learning_planning_demo

        _print_json(run_learning_planning_demo())
    elif args.command == "run-memory-aware-planning-demo":
        from sce.scenarios.memory_aware_planning_demo import run_memory_aware_planning_demo

        _print_json(run_memory_aware_planning_demo())
    elif args.command == "run-adaptive-agent-demo":
        from sce.scenarios.adaptive_agent_demo import run_adaptive_agent_demo

        _print_json(run_adaptive_agent_demo())
    elif args.command == "run-adaptive-agent-demo-pretty":
        from sce.scenarios.adaptive_agent_demo import format_adaptive_agent_demo, run_adaptive_agent_demo

        print(format_adaptive_agent_demo(run_adaptive_agent_demo()))
    elif args.command == "run-exploration-demo":
        from sce.scenarios.exploration_demo import run_exploration_demo

        _print_json(run_exploration_demo())
    elif args.command == "run-exploration-demo-pretty":
        from sce.scenarios.exploration_demo import format_exploration_demo, run_exploration_demo

        print(format_exploration_demo(run_exploration_demo()))
    elif args.command == "run-decision-backbone-demo":
        from sce.scenarios.decision_backbone_demo import run_decision_backbone_demo

        _print_json(run_decision_backbone_demo())
    elif args.command == "run-decision-backbone-demo-pretty":
        from sce.scenarios.decision_backbone_demo import format_decision_backbone_demo, run_decision_backbone_demo

        print(format_decision_backbone_demo(run_decision_backbone_demo()))
    elif args.command == "run-controlled-evolution-demo":
        from sce.scenarios.controlled_evolution_demo import run_controlled_evolution_demo

        _print_json(run_controlled_evolution_demo())
    elif args.command == "run-controlled-evolution-demo-pretty":
        from sce.scenarios.controlled_evolution_demo import format_controlled_evolution_demo, run_controlled_evolution_demo

        print(format_controlled_evolution_demo(run_controlled_evolution_demo()))
    elif args.command == "run-reliability-aware-planning-demo":
        from sce.scenarios.reliability_aware_planning_demo import run_reliability_aware_planning_demo

        _print_json(run_reliability_aware_planning_demo())
    elif args.command == "run-reliability-aware-planning-demo-pretty":
        from sce.scenarios.reliability_aware_planning_demo import (
            format_reliability_aware_planning_demo,
            run_reliability_aware_planning_demo,
        )

        print(format_reliability_aware_planning_demo(run_reliability_aware_planning_demo()))
    elif args.command == "run-hypothesis-research-demo":
        _print_json(run_demo("hypothesis"))
    elif args.command == "run-hypothesis-research-demo-pretty":
        _run_named_demo("hypothesis")
    elif args.command == "run-multi-agent-demo":
        from sce.scenarios.multi_agent_demo import run_multi_agent_demo

        _print_json(run_multi_agent_demo())
    elif args.command == "run-tools-demo":
        from sce.scenarios.tools_demo import run_tools_demo

        _print_json(run_tools_demo())
    elif args.command == "run-planning-demo":
        from sce.scenarios.planning_demo import run_planning_demo

        _print_json(run_planning_demo())
    elif args.command == "run-plan-scoring-demo":
        from sce.scenarios.plan_scoring_demo import run_plan_scoring_demo

        _print_json(run_plan_scoring_demo())
    elif args.command == "run-cognitive-agent-demo":
        from sce.scenarios.cognitive_agent_demo import run_cognitive_agent_demo

        _print_json(run_cognitive_agent_demo())
    elif args.command == "run-llm-voice-demo":
        from sce.scenarios.llm_voice_demo import run_llm_voice_demo

        _print_json(run_llm_voice_demo())
    elif args.command == "export-graph":
        graph_json = json.dumps(_export_supplier_graph(), indent=2, ensure_ascii=False)
        if args.out is None:
            print(graph_json)
        else:
            args.out.write_text(graph_json, encoding="utf-8")
    elif args.command == "visualize-graph":
        graph = _export_supplier_graph()
        ascii_graph = render_ascii_graph(graph)
        if args.out is None:
            print("\n".join(["State Graph", "===========", "", ascii_graph]))
        else:
            args.out.write_text(ascii_graph, encoding="utf-8")
    elif args.command == "explain-demo":
        from sce.scenarios.supplier_reliability import run_demo as run_supplier_reliability_demo

        _print_json(run_supplier_reliability_demo()["explanation"])
    elif args.command == "print-migration":
        from sce.storage.postgres import POSTGRES_MIGRATION_SQL

        print(POSTGRES_MIGRATION_SQL)


if __name__ == "__main__":
    main()
