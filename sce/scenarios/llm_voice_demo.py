from __future__ import annotations

from typing import Dict, Any

from sce.core.cognitive_agent import CognitiveAgent
from sce.core.llm_intent import LLMIntentParser
from sce.core.planning import PlanExecutor
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.voice_os import VoiceOSBridge


class FakeLLMIntent:
    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "intent": "assess_supplier_risk",
            "goal": "assess supplier risk",
            "entities": {
                "entity": "supplier A",
                "claim": "supplier might be unreliable",
            },
        }


def run_llm_voice_demo() -> Dict:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())

    bridge = ToolActionBridge(registry)
    executor = PlanExecutor(bridge)

    agent = CognitiveAgent(executor)
    parser = LLMIntentParser(FakeLLMIntent())
    voice = VoiceOSBridge(agent, parser=parser)

    result = voice.handle_text("Check supplier reliability urgently")

    return {
        "intent": result.intent.intent,
        "goal": result.intent.goal,
        "plan": result.agent_result.selected_plan,
        "response": result.response_text,
    }
