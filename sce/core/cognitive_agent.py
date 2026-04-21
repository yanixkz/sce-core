from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from sce.core.abstractions import AbstractionEngine, RuleMemory
from sce.core.episode_memory import EpisodeMemory
from sce.core.plan_learning import PlanLearning
from sce.core.plan_scoring import PlanScorer, PlanSelector
from sce.core.plan_validation import PlanValidator
from sce.core.planning import Plan, PlanExecutor, PlanExecutionResult
from sce.core.types import State


@dataclass(frozen=True)
class CognitiveAgentResult:
    selected_plan: str
    valid: bool
    score: float
    execution_success: bool
    weights: Dict[str, float]
    memory_size: int
    rule_count: int
    validation_errors: List[str]
    execution: PlanExecutionResult | None = None


class CognitiveAgent:
    """Closed-loop agent over SCE planning primitives.

    Full cycle:
    plan candidates -> validate -> score/select -> execute -> learn -> remember -> abstract
    """

    def __init__(
        self,
        executor: PlanExecutor,
        validator: PlanValidator | None = None,
        learning: PlanLearning | None = None,
        memory: EpisodeMemory | None = None,
        rule_memory: RuleMemory | None = None,
        abstraction_engine: AbstractionEngine | None = None,
    ) -> None:
        self.executor = executor
        self.validator = validator or PlanValidator()
        self.learning = learning or PlanLearning()
        self.memory = memory or EpisodeMemory()
        self.rule_memory = rule_memory or RuleMemory()
        self.abstraction_engine = abstraction_engine or AbstractionEngine()

    def run(self, state: State, goal: str, candidate_plans: List[Plan]) -> CognitiveAgentResult:
        valid_plans: List[Plan] = []
        validation_errors: List[str] = []

        for plan in candidate_plans:
            validation = self.validator.validate(plan, state)
            if validation.valid:
                valid_plans.append(plan)
            else:
                validation_errors.extend(validation.errors)

        if not valid_plans:
            return CognitiveAgentResult(
                selected_plan="",
                valid=False,
                score=0.0,
                execution_success=False,
                weights=self.learning.get_weights(),
                memory_size=len(self.memory.episodes),
                rule_count=len(self.rule_memory.rules),
                validation_errors=validation_errors,
            )

        scorer = PlanScorer(learning=self.learning, memory=self._combined_memory())
        selector = PlanSelector(scorer)
        selected = selector.select(valid_plans, state, goal)

        execution = self.executor.execute(selected.plan, state)
        outcome = self.learning.evaluate_outcome(execution.success)
        weights = self.learning.update(selected.plan, outcome)

        self.memory.remember(
            state=state,
            goal=goal,
            plan=selected.plan,
            success=execution.success,
            reward=outcome.reward,
            reason=outcome.reason,
        )

        rules = self.abstraction_engine.extract_rules(self.memory, min_support=2)
        self.rule_memory.update(rules)

        return CognitiveAgentResult(
            selected_plan=selected.plan.name,
            valid=True,
            score=selected.score,
            execution_success=execution.success,
            weights=weights,
            memory_size=len(self.memory.episodes),
            rule_count=len(self.rule_memory.rules),
            validation_errors=[],
            execution=execution,
        )

    def _combined_memory(self) -> Any:
        agent = self

        class CombinedMemory:
            def plan_bias(self, plan: Plan, state: State, goal: str) -> float:
                return agent.memory.plan_bias(plan, state, goal) + agent.rule_memory.plan_bias(plan, state, goal)

        return CombinedMemory()
