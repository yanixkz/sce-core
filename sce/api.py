from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sce.cli import DEMO_CHOICES, DEMO_REGISTRY, format_demo, run_demo
from sce.core.cognitive_agent import CognitiveAgent
from sce.core.llm_intent import LLMIntentParser
from sce.core.planning import PlanExecutor
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.voice_os import SimpleIntentParser, VoiceOSBridge


class AskRequest(BaseModel):
    text: str = Field(..., description="User text or speech transcript")
    use_llm_intent: bool = Field(False, description="Use LLM intent parser if configured")
    provider: Optional[str] = Field(None, description="openai or anthropic")


class AskResponse(BaseModel):
    intent: str
    goal: str
    selected_plan: str
    execution_success: bool
    response_text: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class DemoRequest(BaseModel):
    name: str = Field(..., description="Demo name")
    format: Literal["pretty", "json"] = Field("pretty", description="Output format")


class DemoResponse(BaseModel):
    name: str
    output: Any


class DemoListItem(BaseModel):
    name: str
    title: str


def build_app() -> FastAPI:
    app = FastAPI(title="SCE Core API", version="0.1.0-alpha")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/demo", response_model=list[DemoListItem])
    def list_demos() -> list[DemoListItem]:
        return [DemoListItem(name=name, title=DEMO_REGISTRY[name]().title) for name in DEMO_CHOICES]

    @app.post("/ask", response_model=AskResponse)
    def ask(request: AskRequest) -> AskResponse:
        voice = _build_voice_bridge(request)
        result = voice.handle_text(request.text)
        return AskResponse(
            intent=result.intent.intent,
            goal=result.intent.goal,
            selected_plan=result.agent_result.selected_plan,
            execution_success=result.agent_result.execution_success,
            response_text=result.response_text,
            meta={
                "memory_size": result.agent_result.memory_size,
                "rule_count": result.agent_result.rule_count,
                "validation_errors": result.agent_result.validation_errors,
            },
        )

    @app.post("/demo", response_model=DemoResponse)
    def demo(request: DemoRequest) -> DemoResponse:
        if request.name not in DEMO_CHOICES:
            raise HTTPException(status_code=400, detail=f"Unknown demo: {request.name}")

        result = run_demo(request.name)
        if request.format == "json":
            return DemoResponse(name=request.name, output=result)

        return DemoResponse(name=request.name, output=format_demo(request.name, result))

    return app


def _build_voice_bridge(request: AskRequest) -> VoiceOSBridge:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)
    executor = PlanExecutor(bridge)
    agent = CognitiveAgent(executor)

    parser = SimpleIntentParser()
    if request.use_llm_intent:
        parser = _build_llm_parser(request.provider)

    return VoiceOSBridge(agent, parser=parser)


def _build_llm_parser(provider: Optional[str]) -> LLMIntentParser:
    selected = (provider or "openai").lower()
    if selected == "anthropic":
        from sce.core.llm_anthropic import AnthropicJSONClient

        return LLMIntentParser(AnthropicJSONClient())

    from sce.core.llm_openai import OpenAIJSONClient

    return LLMIntentParser(OpenAIJSONClient())


app = build_app()
