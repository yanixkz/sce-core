from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from sce.core.actions import Action
from sce.core.cognitive_agent import CognitiveAgent, CognitiveAgentResult
from sce.core.planning import Plan
from sce.core.types import State


@dataclass(frozen=True)
class VoiceIntent:
    """Structured intent extracted from a voice command."""

    raw_text: str
    intent: str
    entities: Dict[str, Any] = field(default_factory=dict)
    goal: str = ""


@dataclass(frozen=True)
class VoiceOSResult:
    intent: VoiceIntent
    agent_result: CognitiveAgentResult
    response_text: str


class SimpleIntentParser:
    """Deterministic voice-intent parser for early integration."""

    def parse(self, text: str) -> VoiceIntent:
        lowered = text.lower()
        if "supplier" in lowered or "поставщик" in lowered:
            supplier_id = "supplier A"
            return VoiceIntent(
                raw_text=text,
                intent="assess_supplier_risk",
                entities={"entity": supplier_id, "claim": "supplier is unreliable"},
                goal="assess supplier risk",
            )

        return VoiceIntent(
            raw_text=text,
            intent="observe",
            entities={"claim": text},
            goal="observe current state",
        )


class VoiceOSBridge:
    """Bridge between a voice interface and the SCE cognitive agent."""

    def __init__(self, agent: CognitiveAgent, parser: SimpleIntentParser | None = None) -> None:
        self.agent = agent
        self.parser = parser or SimpleIntentParser()

    def handle_text(self, text: str) -> VoiceOSResult:
        intent = self.parser.parse(text)
        state = State("voice_intent", dict(intent.entities))
        plans = self._plans_for_intent(intent)
        agent_result = self.agent.run(state, intent.goal, plans)
        response = self._response(intent, agent_result)
        return VoiceOSResult(intent=intent, agent_result=agent_result, response_text=response)

    def _plans_for_intent(self, intent: VoiceIntent) -> List[Plan]:
        if intent.intent == "assess_supplier_risk":
            return [
                Plan(
                    name="assess_and_escalate",
                    actions=[
                        Action(
                            name="fetch_supplier_risk",
                            description="Fetch supplier risk data",
                            action_type="tool",
                            payload={"tool": "supplier_risk_api", "arguments": {"supplier_id": intent.entities.get("entity", "supplier A")}},
                        ),
                        Action(
                            name="request_review",
                            description="Request review if supplier appears risky",
                            action_type="workflow",
                            payload={"reason": intent.entities.get("claim", "")},
                        ),
                    ],
                    reason="Voice command asks for supplier risk assessment.",
                ),
                Plan(
                    name="monitor_only",
                    actions=[Action(name="monitor", description="Monitor", action_type="workflow", payload={})],
                    reason="Low-risk fallback plan.",
                ),
            ]

        return [
            Plan(
                name="observe",
                actions=[Action(name="monitor", description="Observe current state", action_type="workflow", payload={})],
                reason="Default observation plan.",
            )
        ]

    def _response(self, intent: VoiceIntent, result: CognitiveAgentResult) -> str:
        if not result.valid:
            return f"I could not build a valid plan for: {intent.raw_text}"
        if result.execution_success:
            return f"Done. I selected plan '{result.selected_plan}' for intent '{intent.intent}'."
        return f"I selected plan '{result.selected_plan}', but execution failed."
