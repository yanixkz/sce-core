from __future__ import annotations

import argparse
import json
from pathlib import Path


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


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


def main() -> None:
    parser = argparse.ArgumentParser(prog="sce")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    sub.add_parser("run-demo")
    sub.add_parser("run-supplier-risk-demo")
    sub.add_parser("run-supplier-risk-demo-pretty")
    sub.add_parser("run-conflict-demo")
    sub.add_parser("run-llm-demo")
    sub.add_parser("run-llm-planning-demo")
    sub.add_parser("run-contract-demo")
    sub.add_parser("run-agent-demo")
    sub.add_parser("run-goal-agent-demo")
    sub.add_parser("run-action-demo")
    sub.add_parser("run-learning-demo")
    sub.add_parser("run-learning-planning-demo")
    sub.add_parser("run-memory-aware-planning-demo")
    sub.add_parser("run-adaptive-agent-demo")
    sub.add_parser("run-adaptive-agent-demo-pretty")
    sub.add_parser("run-exploration-demo")
    sub.add_parser("run-exploration-demo-pretty")
    sub.add_parser("run-decision-backbone-demo")
    sub.add_parser("run-decision-backbone-demo-pretty")
    sub.add_parser("run-controlled-evolution-demo")
    sub.add_parser("run-controlled-evolution-demo-pretty")
    sub.add_parser("run-reliability-aware-planning-demo")
    sub.add_parser("run-reliability-aware-planning-demo-pretty")
    sub.add_parser("run-hypothesis-research-demo")
    sub.add_parser("run-hypothesis-research-demo-pretty")
    sub.add_parser("run-multi-agent-demo")
    sub.add_parser("run-tools-demo")
    sub.add_parser("run-planning-demo")
    sub.add_parser("run-plan-scoring-demo")
    sub.add_parser("run-cognitive-agent-demo")
    sub.add_parser("run-llm-voice-demo")
    export_graph_parser = sub.add_parser("export-graph")
    export_graph_parser.add_argument("--out", type=Path, default=None)
    visualize_graph_parser = sub.add_parser("visualize-graph")
    visualize_graph_parser.add_argument("--out", type=Path, default=None)
    sub.add_parser("explain-demo")
    sub.add_parser("print-migration")
    args = parser.parse_args()

    if args.command == "demo":
        from sce.scenarios.supplier_risk_demo import format_supplier_risk_demo, run_supplier_risk_demo

        print(format_supplier_risk_demo(run_supplier_risk_demo()))
    elif args.command == "run-demo":
        from sce.scenarios.supplier_reliability import run_demo

        _print_json(run_demo())
    elif args.command == "run-supplier-risk-demo":
        from sce.scenarios.supplier_risk_demo import run_supplier_risk_demo

        _print_json(run_supplier_risk_demo())
    elif args.command == "run-supplier-risk-demo-pretty":
        from sce.scenarios.supplier_risk_demo import format_supplier_risk_demo, run_supplier_risk_demo

        print(format_supplier_risk_demo(run_supplier_risk_demo()))
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
        from sce.scenarios.hypothesis_research_demo import run_hypothesis_research_demo

        _print_json(run_hypothesis_research_demo())
    elif args.command == "run-hypothesis-research-demo-pretty":
        from sce.scenarios.hypothesis_research_demo import format_hypothesis_research_demo, run_hypothesis_research_demo

        print(format_hypothesis_research_demo(run_hypothesis_research_demo()))
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
        from sce.visualization.graph_ascii import render_ascii_graph

        graph = _export_supplier_graph()
        ascii_graph = render_ascii_graph(graph)
        if args.out is None:
            print(ascii_graph)
        else:
            args.out.write_text(ascii_graph, encoding="utf-8")
    elif args.command == "explain-demo":
        from sce.scenarios.supplier_reliability import run_demo

        _print_json(run_demo()["explanation"])
    elif args.command == "print-migration":
        from sce.storage.postgres import POSTGRES_MIGRATION_SQL

        print(POSTGRES_MIGRATION_SQL)


if __name__ == "__main__":
    main()
