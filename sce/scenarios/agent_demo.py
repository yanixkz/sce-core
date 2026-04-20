from __future__ import annotations

import os
from typing import Any, Dict

from sce.core.agent_loop import SCEAgentLoop
from sce.core.llm_candidates import LLMClient
from sce.core.types import State
from sce.storage.memory import MemoryRepository


class FakeLLM:
    def complete_json(self, prompt: str) -> Dict[str, Any]:
        return {
            "candidates": [
                {"state_type": "agent_state", "data": {"claim": "supplier is reliable"}},
                {"state_type": "agent_state", "data": {"claim": "supplier is unreliable"}},
            ]
        }


def _build_client() -> LLMClient:
    use_openai = os.getenv("SCE_USE_OPENAI", "false").lower() in {"1", "true"}
    if not use_openai:
        return FakeLLM()
    try:
        from sce.core.llm_openai import OpenAIJSONClient

        return OpenAIJSONClient()
    except Exception:
        return FakeLLM()


def run_agent_demo() -> Dict[str, Any]:
    repo = MemoryRepository()

    initial = State(
        state_type="agent_context",
        data={
            "entity": "supplier A",
            "facts": [
                "many deliveries were late",
                "there are complaints",
                "historically some orders were on time",
            ],
        },
    )

    agent = SCEAgentLoop(
        repo=repo,
        llm_client=_build_client(),
        task="Refine belief about supplier reliability",
    )

    result = agent.run(initial_state=initial, steps=3)

    return {
        "scenario": "agent_loop",
        "final_claim": result.final_claim,
        "steps": [
            {
                "step": step.step,
                "selected_claim": step.selected_claim,
            }
            for step in result.steps
        ],
    }
