from __future__ import annotations

from typing import Dict

from sce.core.cognitive_agent import CognitiveAgent
from sce.core.planning import PlanExecutor
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.voice_os import VoiceOSBridge


def run_voice_os_demo() -> Dict:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())

    bridge = ToolActionBridge(registry)
    executor = PlanExecutor(bridge)

    agent = CognitiveAgent(executor)
    voice = VoiceOSBridge(agent)

    result1 = voice.handle_text("Check supplier risk")
    result2 = voice.handle_text("Check supplier risk again")

    return {
        "first": {
            "intent": result1.intent.intent,
            "plan": result1.agent_result.selected_plan,
            "response": result1.response_text,
        },
        "second": {
            "intent": result2.intent.intent,
            "plan": result2.agent_result.selected_plan,
            "response": result2.response_text,
        },
    }
