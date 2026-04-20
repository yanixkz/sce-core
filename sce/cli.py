from __future__ import annotations

import argparse
import json

from sce.scenarios.action_demo import run_action_demo
from sce.scenarios.agent_demo import run_agent_demo
from sce.scenarios.conflicting_memory import run_conflicting_memory_demo
from sce.scenarios.contract_risk import run_contract_risk_demo
from sce.scenarios.goal_agent_demo import run_goal_agent_demo
from sce.scenarios.learning_demo import run_learning_demo
from sce.scenarios.llm_memory import run_llm_memory_demo
from sce.scenarios.llm_planning_demo import run_llm_planning_demo
from sce.scenarios.multi_agent_demo import run_multi_agent_demo
from sce.scenarios.plan_scoring_demo import run_plan_scoring_demo
from sce.scenarios.planning_demo import run_planning_demo
from sce.scenarios.supplier_reliability import run_demo
from sce.scenarios.tools_demo import run_tools_demo
from sce.storage.postgres import POSTGRES_MIGRATION_SQL


def main() -> None:
    parser = argparse.ArgumentParser(prog="sce")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run-demo")
    sub.add_parser("run-conflict-demo")
    sub.add_parser("run-llm-demo")
    sub.add_parser("run-llm-planning-demo")
    sub.add_parser("run-contract-demo")
    sub.add_parser("run-agent-demo")
    sub.add_parser("run-goal-agent-demo")
    sub.add_parser("run-action-demo")
    sub.add_parser("run-learning-demo")
    sub.add_parser("run-multi-agent-demo")
    sub.add_parser("run-tools-demo")
    sub.add_parser("run-planning-demo")
    sub.add_parser("run-plan-scoring-demo")
    sub.add_parser("explain-demo")
    sub.add_parser("print-migration")
    args = parser.parse_args()

    if args.command == "run-demo":
        print(json.dumps(run_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-conflict-demo":
        print(json.dumps(run_conflicting_memory_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-llm-demo":
        print(json.dumps(run_llm_memory_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-llm-planning-demo":
        print(json.dumps(run_llm_planning_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-contract-demo":
        print(json.dumps(run_contract_risk_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-agent-demo":
        print(json.dumps(run_agent_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-goal-agent-demo":
        print(json.dumps(run_goal_agent_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-action-demo":
        print(json.dumps(run_action_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-learning-demo":
        print(json.dumps(run_learning_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-multi-agent-demo":
        print(json.dumps(run_multi_agent_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-tools-demo":
        print(json.dumps(run_tools_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-planning-demo":
        print(json.dumps(run_planning_demo(), indent=2, ensure_ascii=False))
    elif args.command == "run-plan-scoring-demo":
        print(json.dumps(run_plan_scoring_demo(), indent=2, ensure_ascii=False))
    elif args.command == "explain-demo":
        print(json.dumps(run_demo()["explanation"], indent=2, ensure_ascii=False))
    elif args.command == "print-migration":
        print(POSTGRES_MIGRATION_SQL)


if __name__ == "__main__":
    main()
