from __future__ import annotations

from typing import Any, Dict

from sce.core.voice_os import VoiceIntent


class LLMIntentParser:
    """LLM-backed intent parser for Voice OS.

    The client must expose `complete_json(prompt) -> dict`.
    """

    def __init__(self, llm_client: Any) -> None:
        self.llm = llm_client

    def parse(self, text: str) -> VoiceIntent:
        payload = self.llm.complete_json(self._prompt(text))

        intent = str(payload.get("intent", "observe"))
        entities = payload.get("entities", {})
        if not isinstance(entities, dict):
            entities = {}
        goal = str(payload.get("goal", "observe current state"))

        return VoiceIntent(
            raw_text=text,
            intent=intent,
            entities=entities,
            goal=goal,
        )

    def _prompt(self, text: str) -> str:
        return f"""
Extract a structured intent for SCE Core Voice OS.

User text:
{text}

Return JSON only:
{{
  "intent": "assess_supplier_risk | observe | other",
  "goal": "short goal string",
  "entities": {{
    "entity": "...",
    "claim": "..."
  }}
}}
""".strip()
