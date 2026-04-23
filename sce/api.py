from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from sce.cli import DEMO_CHOICES, DEMO_REGISTRY, format_demo, run_demo
from sce.core.cognitive_agent import CognitiveAgent
from sce.core.evolution import SCEEvolver
from sce.core.llm_intent import LLMIntentParser
from sce.core.planning import PlanExecutor
from sce.core.queries import GraphQueryLayer
from sce.core.scoring import SCEScoringEngine
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.voice_os import SimpleIntentParser, VoiceOSBridge
from sce.scenarios.supplier_reliability import make_supplier_reliability_scenario

API_VERSION = "v1"


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
    format: Literal["pretty", "json"] = Field("pretty")


class DemoResponse(BaseModel):
    version: str
    name: str
    format: str
    result: Any
    explanation: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class DemoExplanationResponse(BaseModel):
    version: str
    name: str
    explanation: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class DemoListItem(BaseModel):
    name: str
    title: str


class GraphResponse(BaseModel):
    version: str
    graph: Dict[str, Any]
    meta: Dict[str, Any] = Field(default_factory=dict)


def _export_supplier_graph() -> dict:
    repo, start_state = make_supplier_reliability_scenario()
    scorer = SCEScoringEngine(repo)
    evolver = SCEEvolver(repo, scorer)
    evolver.evolve(start_state, max_steps=5, epsilon=0.001)
    return GraphQueryLayer(repo).export_graph_json()


def _load_ui_html() -> str:
    return (Path(__file__).with_name("ui.html")).read_text(encoding="utf-8")


def _build_demo_ui_meta(name: str, raw_result: dict) -> Dict[str, Any]:
    if name == "supplier-risk":
        return {
            "view": "supplier-risk",
            "panel_order": [
                "selected_plan",
                "explanation_backbone",
                "reliability",
                "memory_influence",
                "summary",
            ],
            "panels": {
                "selected_plan": {
                    "label": "Selected plan",
                    "first_choice": raw_result.get("first_choice"),
                    "final_choice": raw_result.get("final_choice"),
                    "changed_choice": raw_result.get("changed_choice"),
                },
                "explanation_backbone": {
                    "label": "Explanation backbone",
                    "backbone_nodes": raw_result.get("backbone_nodes", []),
                    "dangling_nodes": raw_result.get("dangling_nodes", []),
                },
                "reliability": {
                    "label": "Reliability",
                    "reliability": raw_result.get("reliability"),
                    "cumulative_error": raw_result.get("cumulative_error"),
                    "trend": raw_result.get("reliability_trend"),
                },
                "memory_influence": {
                    "label": "Memory influence",
                    "remembered_episodes": raw_result.get("remembered_episodes"),
                },
                "summary": {
                    "label": "Summary",
                    "text": raw_result.get("summary"),
                },
            },
        }

    if name == "hypothesis":
        return {
            "view": "hypothesis",
            "panel_order": [
                "research_question",
                "ranked_hypotheses",
                "winning_hypothesis",
                "decision_evidence",
                "dangling_context",
                "next_actions",
            ],
            "panels": {
                "research_question": {
                    "label": "Research question",
                    "text": raw_result.get("research_question"),
                },
                "ranked_hypotheses": {
                    "label": "Ranked hypotheses",
                    "scores": raw_result.get("scores", []),
                },
                "winning_hypothesis": {
                    "label": "Winning hypothesis",
                    "selected_hypothesis": raw_result.get("selected_hypothesis"),
                },
                "decision_evidence": {
                    "label": "Decision-carrying evidence",
                    "backbone_nodes": raw_result.get("backbone_nodes", []),
                },
                "dangling_context": {
                    "label": "Dangling context",
                    "dangling_nodes": raw_result.get("dangling_nodes", []),
                },
                "next_actions": {
                    "label": "Next actions",
                    "actions": raw_result.get("next_actions", []),
                },
            },
        }

    return {"view": "generic", "panel_order": ["summary"], "panels": {"summary": {"label": "Summary"}}}


def build_app() -> FastAPI:
    app = FastAPI(title="SCE Core API", version="0.1.0-alpha")

    @app.get("/ui", response_class=HTMLResponse)
    def ui() -> HTMLResponse:
        return HTMLResponse(content=_load_ui_html())

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/demo", response_model=list[DemoListItem])
    def list_demos() -> list[DemoListItem]:
        return [DemoListItem(name=name, title=DEMO_REGISTRY[name]().title) for name in DEMO_CHOICES]

    @app.get("/graph", response_model=GraphResponse)
    def graph() -> GraphResponse:
        exported = _export_supplier_graph()
        nodes = exported.get("nodes", [])
        edges = exported.get("edges", [])
        return GraphResponse(
            version=API_VERSION,
            graph=exported,
            meta={
                "source": "supplier-reliability",
                "node_count": len(nodes),
                "edge_count": len(edges),
                "schema": {
                    "node_fields": [
                        "state_id",
                        "state_type",
                        "stability",
                        "is_attractor",
                        "constraints",
                        "constraints_satisfied",
                        "data",
                    ],
                    "edge_fields": [
                        "edge_id",
                        "source_state_id",
                        "target_state_id",
                        "relation_type",
                        "strength",
                        "directed",
                    ],
                },
                "ui": {"default_layout": "force-directed", "primary_node_label": "state_type"},
            },
        )

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

        raw_result = run_demo(request.name)
        ui_meta = _build_demo_ui_meta(request.name, raw_result)

        if request.format == "json":
            return DemoResponse(
                version=API_VERSION,
                name=request.name,
                format="json",
                result=raw_result,
                meta={"type": "raw", "ui": ui_meta},
            )

        pretty = format_demo(request.name, raw_result)
        return DemoResponse(
            version=API_VERSION,
            name=request.name,
            format="pretty",
            result=raw_result,
            explanation=pretty,
            meta={"type": "formatted", "ui": ui_meta},
        )

    @app.post("/demo/explain", response_model=DemoExplanationResponse)
    def explain_demo(request: DemoRequest) -> DemoExplanationResponse:
        if request.name not in DEMO_CHOICES:
            raise HTTPException(status_code=400, detail=f"Unknown demo: {request.name}")

        raw_result = run_demo(request.name)
        return DemoExplanationResponse(
            version=API_VERSION,
            name=request.name,
            explanation=format_demo(request.name, raw_result),
            meta={
                "type": "explanation",
                "ui": _build_demo_ui_meta(request.name, raw_result),
                "sections": ["question_or_goal", "analysis", "decision", "summary"],
            },
        )

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
