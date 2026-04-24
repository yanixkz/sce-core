from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol


BASELINE_LIMITATIONS = [
    "One-shot baseline response: no ranked alternatives.",
    "No episodic memory or adaptive history.",
    "No reliability scoring derived from outcomes.",
    "No decision backbone or structural plan graph.",
]


@dataclass(slots=True)
class BaselineAIResult:
    answer: str
    rationale: str
    limitations: list[str] = field(default_factory=lambda: list(BASELINE_LIMITATIONS))
    provider: str = "mock"
    source: str = "deterministic"
    meta: Dict[str, Any] = field(default_factory=dict)


class BaselineAIClient(Protocol):
    def generate(self, goal: str, context: Dict[str, Any], constraints: list[str]) -> BaselineAIResult: ...


class DeterministicBaselineAIClient:
    """Deterministic rule-based generic AI baseline used by default."""

    def __init__(self, provider: str = "mock", source: str = "deterministic") -> None:
        self.provider = provider
        self.source = source

    def generate(self, goal: str, context: Dict[str, Any], constraints: list[str]) -> BaselineAIResult:
        intent = f"{goal} {' '.join(str(v) for v in context.values())}".lower()

        if any(token in intent for token in ["supplier", "vendor", "procurement", "risk"]):
            answer = (
                "Perform a quick supplier-risk check by validating delivery consistency, requesting updated compliance evidence, "
                "and assigning temporary monitoring before expanding exposure."
            )
            rationale = (
                "A generic one-shot approach prioritizes immediate risk containment and common due-diligence steps, "
                "but it does not rank alternatives against historical outcomes."
            )
            baseline_type = "supplier-risk"
        elif any(token in intent for token in ["hypothesis", "research", "experiment", "test"]):
            answer = (
                "Start with the most testable hypothesis, define one measurable success metric, and run a short experiment to "
                "collect decision-relevant evidence."
            )
            rationale = (
                "A generic baseline typically chooses a plausible first hypothesis and suggests a validation loop, "
                "without structured candidate ranking or reliability weighting."
            )
            baseline_type = "hypothesis"
        else:
            answer = (
                "Choose the most feasible immediate option, state key trade-offs, and run a small reversible step before committing "
                "to broader execution."
            )
            rationale = (
                "A generic one-shot model can provide a concise recommendation, "
                "but it does not provide SCE-style ranked plans, memory influence, or reliability signals."
            )
            baseline_type = "generic"

        return BaselineAIResult(
            answer=answer,
            rationale=rationale,
            provider=self.provider,
            source=self.source,
            meta={
                "baseline_type": baseline_type,
                "constraint_count": len(constraints),
                "context_keys": sorted(context.keys()),
            },
        )


class ProviderBackedBaselineAIClient:
    """Optional provider-backed baseline with deterministic fallback handled by caller."""

    def __init__(self, provider: str, json_client: Any, model: str) -> None:
        self.provider = provider
        self.json_client = json_client
        self.model = model

    def generate(self, goal: str, context: Dict[str, Any], constraints: list[str]) -> BaselineAIResult:
        prompt = (
            "Return JSON with keys: answer (string), rationale (string), notes (array of strings), meta (object). "
            "This is a generic one-shot baseline, not a ranked decision engine. "
            f"Goal: {goal}\n"
            f"Context JSON: {json.dumps(context, ensure_ascii=False)}\n"
            f"Constraints: {json.dumps(constraints, ensure_ascii=False)}"
        )
        payload = self.json_client.complete_json(prompt)

        notes = payload.get("notes") if isinstance(payload.get("notes"), list) else []
        extra_limitations = [str(note) for note in notes]

        answer = str(payload.get("answer", "No answer produced."))
        rationale = str(payload.get("rationale", "No rationale produced."))

        return BaselineAIResult(
            answer=answer,
            rationale=rationale,
            limitations=list(BASELINE_LIMITATIONS) + extra_limitations,
            provider=self.provider,
            source="provider",
            meta={
                "model": self.model,
                "raw_meta": payload.get("meta", {}),
            },
        )


def build_baseline_client(selected_provider: Optional[str]) -> tuple[BaselineAIClient, Dict[str, Any]]:
    requested = (selected_provider or os.getenv("SCE_BASELINE_PROVIDER") or "mock").lower()

    if requested in {"mock", "generic", "deterministic"}:
        return DeterministicBaselineAIClient(provider="mock", source="deterministic"), {
            "requested_provider": requested,
            "effective_provider": "mock",
            "fallback_used": False,
        }

    if requested == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("SCE_OPENAI_MODEL", "gpt-4o-mini")
        if not api_key:
            return DeterministicBaselineAIClient(provider="mock", source="deterministic"), {
                "requested_provider": "openai",
                "effective_provider": "mock",
                "fallback_used": True,
                "fallback_reason": "OPENAI_API_KEY is not configured",
            }
        from sce.core.llm_openai import OpenAIJSONClient

        client = OpenAIJSONClient(model=model, api_key=api_key)
        return ProviderBackedBaselineAIClient(provider="openai", json_client=client, model=model), {
            "requested_provider": "openai",
            "effective_provider": "openai",
            "fallback_used": False,
        }

    if requested == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("SCE_ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
        if not api_key:
            return DeterministicBaselineAIClient(provider="mock", source="deterministic"), {
                "requested_provider": "anthropic",
                "effective_provider": "mock",
                "fallback_used": True,
                "fallback_reason": "ANTHROPIC_API_KEY is not configured",
            }
        from sce.core.llm_anthropic import AnthropicJSONClient

        client = AnthropicJSONClient(model=model, api_key=api_key)
        return ProviderBackedBaselineAIClient(provider="anthropic", json_client=client, model=model), {
            "requested_provider": "anthropic",
            "effective_provider": "anthropic",
            "fallback_used": False,
        }

    return DeterministicBaselineAIClient(provider="mock", source="deterministic"), {
        "requested_provider": requested,
        "effective_provider": "mock",
        "fallback_used": True,
        "fallback_reason": f"Unknown baseline provider: {requested}",
    }
