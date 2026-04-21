from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


class AnthropicJSONClient:
    """Anthropic-backed JSON client for SCE LLM integration.

    Requires the optional dependency `anthropic` and ANTHROPIC_API_KEY.
    """

    def __init__(self, model: str = "claude-3-5-haiku-latest", api_key: Optional[str] = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for AnthropicJSONClient")

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "AnthropicJSONClient requires the optional dependency `anthropic`. "
                "Install it with: pip install anthropic"
            ) from exc

        self.client = Anthropic(api_key=self.api_key)

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system="Return JSON only. No markdown. No prose.",
            messages=[{"role": "user", "content": prompt}],
        )

        text_parts = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)

        content = "".join(text_parts).strip()
        if not content:
            raise ValueError("Anthropic response did not contain text content")

        payload = json.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("Anthropic response JSON must be an object")
        return payload
