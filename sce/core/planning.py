from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List

from sce.core.actions import Action, ActionResult
from sce.core.tools import ToolActionBridge
from sce.core.types import State

if TYPE_CHECKING:
    from sce.core.episode_memory import EpisodeMemory


@dataclass(frozen=True)
class Plan:
    """A sequence of actions selected for a goal or state."""

    name: str
    actions: List[Action]
    reason: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanScore:
    """Inspectable score assigned to a candidate plan."""

    plan: Plan
    base_score: float
    memory_bias: float

    @property
    def total_score(self) -> float:
        return self.base_score + self.memory_bias


@dataclass(frozen=True)
class PlanExecutionResult:
    """Result of executing a plan."""

    plan_name: str
    results: List[ActionResult]

    @property
    def success(self) -> bool:
        return all(result.success for result in self.results)

    @property
    def final_state(self) -> State | None:
        if not self.results:
            return None
        return self.results[-1].resulting_state

    @property
    def reward(self) -> float:
        return 1.0 if self.success else -1.0


class ToolPlanner:
    """Simple deterministic planner for selecting tools from state context.

    Phase 1 intentionally uses explicit rules instead of opaque automation.
    This makes planning inspectable and safe for demos/tests.
    """

    def plan(self, state: State, goal: str) -> Plan:
        return self.candidates(state, goal)[0]

    def candidates(self, state: State, goal: str) -> List[Plan]:
        goal_lower = goal.lower()
        data = state.data or {}

        monitor_plan = Plan(
            name="monitor_plan",
            reason="Monitor current state without external calls.",
            actions=[
                Action(
                    name="monitor",
                    description="Monitor current state without external calls.",
                    action_type="internal",
                    payload={},
                )
            ],
            meta={"base_score": 0.1},
        )

        if "supplier" in goal_lower or "risk" in goal_lower:
            supplier_id = data.get("supplier_id") or data.get("entity") or "supplier A"
            return [
                Plan(
                    name="supplier_risk_plan",
                    reason="Goal requires supplier risk evidence from an external source.",
                    actions=[
                        Action(
                            name="fetch_supplier_risk",
                            description="Fetch supplier risk metrics from an external supplier-risk tool.",
                            action_type="tool",
                            payload={
                                "tool": "supplier_risk_api",
                                "arguments": {"supplier_id": supplier_id},
                            },
                        )
                    ],
                    meta={"supplier_id": supplier_id, "base_score": 0.6},
                ),
                Plan(
                    name="escalation_plan",
                    reason="Escalate high-risk supplier context for human or workflow follow-up.",
                    actions=[
                        Action(
                            name="escalate",
                            description="Escalate supplier risk for follow-up.",
                            action_type="workflow",
                            payload={"supplier_id": supplier_id},
                        )
                    ],
                    meta={"supplier_id": supplier_id, "base_score": 0.4},
                ),
                monitor_plan,
            ]

        return [monitor_plan]


class MemoryAwarePlanner:
    """Rank candidate plans using base scores plus episodic memory bias."""

    def __init__(self, base_planner: ToolPlanner, memory: "EpisodeMemory") -> None:
        self.base_planner = base_planner
        self.memory = memory

    def plan(self, state: State, goal: str, candidates: List[Plan] | None = None) -> Plan:
        ranked = self.score(candidates or self.base_planner.candidates(state, goal), state, goal)
        return ranked[0].plan

    def rank(self, candidates: List[Plan], state: State, goal: str) -> List[Plan]:
        return [score.plan for score in self.score(candidates, state, goal)]

    def score(self, candidates: List[Plan], state: State, goal: str) -> List[PlanScore]:
        scores = [
            PlanScore(
                plan=plan,
                base_score=float(plan.meta.get("base_score", 0.0)),
                memory_bias=self.memory.plan_bias(plan, state, goal),
            )
            for plan in candidates
        ]
        return sorted(scores, key=lambda item: item.total_score, reverse=True)


class PlanExecutor:
    """Executes tool-oriented plans through ToolActionBridge."""

    def __init__(self, bridge: ToolActionBridge) -> None:
        self.bridge = bridge

    def execute(self, plan: Plan, initial_state: State) -> PlanExecutionResult:
        current = initial_state
        results: List[ActionResult] = []

        for action in plan.actions:
            result = self.bridge.execute(action, current)
            results.append(result)
            current = result.resulting_state

        return PlanExecutionResult(plan_name=plan.name, results=results)


class LearningPlanExecutor:
    """Executes a plan and records the outcome in episodic memory."""

    def __init__(self, executor: PlanExecutor, memory: "EpisodeMemory") -> None:
        self.executor = executor
        self.memory = memory

    def execute(self, plan: Plan, initial_state: State, goal: str) -> PlanExecutionResult:
        result = self.executor.execute(plan, initial_state)
        self.memory.remember(
            initial_state,
            goal,
            plan,
            success=result.success,
            reward=result.reward,
            reason="execution_success" if result.success else "execution_failed",
        )
        return result
