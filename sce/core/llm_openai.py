from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


class OpenAIJSONClient:
    """OpenAI-backed JSON client for SCE LLM integration.

    This adapter is optional. It requires the `openai` package and an
    `OPENAI_API_KEY` environment variable.

    It exposes the common SCE LLM interface:
    `complete_json(prompt: str) -> dict`.
    """

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIJSONClient")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAIJSONClient requires the optional dependency `openai`. "
                "Install it with: pip install openai"
            ) from exc

        self.client = OpenAI(api_key=self.api_key)

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Return JSON only. No markdown. No prose.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI response did not contain content")

        payload = json.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("OpenAI response JSON must be an object")
        return payload
