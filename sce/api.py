from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from sce.cli import DEMO_CHOICES, DEMO_REGISTRY, format_demo, run_demo
from sce.core.cognitive_agent import CognitiveAgent
from sce.core.baseline_ai import BASELINE_LIMITATIONS, build_baseline_client
from sce.core.evolution import SCEEvolver
from sce.core.llm_intent import LLMIntentParser
from sce.core.planning import MemoryAwarePlanner, PlanExecutor, ReliabilityAwarePlanner, ToolPlanner
from sce.core.queries import GraphQueryLayer
from sce.core.scoring import SCEScoringEngine
from sce.core.episode_memory import EpisodeMemory
from sce.core.types import State
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.voice_os import SimpleIntentParser, VoiceOSBridge
from sce.scenarios.supplier_reliability import make_supplier_reliability_scenario
from sce.storage.postgres import PostgresEpisodeRepository

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


class DecideRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="Decision goal, task, or question")
    context: Dict[str, Any] = Field(default_factory=dict, description="Current known facts")
    constraints: list[str] = Field(default_factory=list, description="Optional natural-language constraints")
    execute: bool = Field(False, description="Execute selected plan after ranking")
    reliability_weight: float = Field(1.0, ge=0.0, le=5.0, description="Weight of reliability in ranking")


class DecisionCandidateScore(BaseModel):
    plan: str
    reason: str
    base_score: float
    memory_bias: float
    reliability: float
    reliability_bonus: float
    total_score: float


class DecisionExecutionStep(BaseModel):
    action: str
    success: bool
    message: str


class DecideResponse(BaseModel):
    version: str
    goal: str
    selected_plan: str
    selected_reason: str
    action_names: list[str]
    executed: bool
    execution_success: bool | None = None
    execution_trace: list[DecisionExecutionStep] = Field(default_factory=list)
    scores: list[DecisionCandidateScore]
    meta: Dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="Decision goal, task, or question")
    context: Dict[str, Any] = Field(default_factory=dict, description="Current known facts")
    constraints: list[str] = Field(default_factory=list, description="Optional natural-language constraints")
    execute: bool = Field(False, description="Execute selected SCE plan after ranking")
    reliability_weight: float = Field(1.0, ge=0.0, le=5.0, description="Weight of reliability in ranking")
    baseline_provider: Optional[str] = Field(None, description="mock (default), openai, or anthropic")


class CompareBaselineResponse(BaseModel):
    answer: str
    rationale: str
    limitations: list[str] = Field(default_factory=list)
    provider: str
    source: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class CompareSCEResponse(BaseModel):
    selected_plan: str
    selected_reason: str
    action_names: list[str]
    executed: bool
    execution_success: bool | None = None
    execution_trace: list[DecisionExecutionStep] = Field(default_factory=list)
    scores: list[DecisionCandidateScore]
    meta: Dict[str, Any] = Field(default_factory=dict)


class CompareResponse(BaseModel):
    version: str
    input_summary: Dict[str, Any]
    baseline: CompareBaselineResponse
    sce: CompareSCEResponse
    comparison: Dict[str, Any]
    meta: Dict[str, Any] = Field(default_factory=dict)


class MemoryEpisodeView(BaseModel):
    episode_id: str
    created_at: str
    goal: str
    selected_plan: str
    action_names: list[str]
    success: bool
    reward: float
    reliability: float | None = None
    reason: str = ""


class MemoryResponse(BaseModel):
    version: str
    episodes: list[MemoryEpisodeView]
    meta: Dict[str, Any] = Field(default_factory=dict)


class ReliabilityResponse(BaseModel):
    version: str
    reliability: Dict[str, Any]
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

    if name == "resource-stability":
        return {
            "view": "resource-stability",
            "panel_order": [
                "research_question",
                "initial_state",
                "candidate_ranking",
                "selected_state",
                "constraints",
                "next_research_actions",
            ],
            "panels": {
                "research_question": {
                    "label": "Research question",
                    "text": raw_result.get("research_question"),
                },
                "initial_state": {
                    "label": "Initial state",
                    "state": raw_result.get("initial_state"),
                },
                "candidate_ranking": {
                    "label": "Candidate ranking",
                    "scores": raw_result.get("scores", []),
                },
                "selected_state": {
                    "label": "Selected state",
                    "state": raw_result.get("selected_state"),
                },
                "constraints": {
                    "label": "Constraints",
                    "items": raw_result.get("constraints", []),
                },
                "next_research_actions": {
                    "label": "Next research actions",
                    "actions": raw_result.get("next_research_actions", []),
                },
            },
        }

    if name == "epidemic-regime":
        return {
            "view": "epidemic-regime",
            "panel_order": [
                "research_question",
                "initial_state",
                "candidate_ranking",
                "selected_regime",
                "constraints",
                "next_research_actions",
            ],
            "panels": {
                "research_question": {
                    "label": "Research question",
                    "text": raw_result.get("research_question"),
                },
                "initial_state": {
                    "label": "Initial state",
                    "state": raw_result.get("initial_state"),
                },
                "candidate_ranking": {
                    "label": "Candidate ranking",
                    "scores": raw_result.get("scores", []),
                },
                "selected_regime": {
                    "label": "Selected regime",
                    "state": raw_result.get("selected_regime"),
                },
                "constraints": {
                    "label": "Constraints",
                    "items": raw_result.get("constraints", []),
                },
                "next_research_actions": {
                    "label": "Next research actions",
                    "actions": raw_result.get("next_research_actions", []),
                },
            },
        }

    return {"view": "generic", "panel_order": ["summary"], "panels": {"summary": {"label": "Summary"}}}


def _build_durable_episode_repository() -> PostgresEpisodeRepository | None:
    dsn = os.getenv("SCE_DATABASE_URL")
    if not dsn:
        return None
    repo = PostgresEpisodeRepository(dsn)
    repo.init_schema()
    return repo


def _run_sce_decision(
    request: DecideRequest,
    shared_episode_memory: EpisodeMemory,
    durable_episode_repository: PostgresEpisodeRepository | None,
    durable_status: str,
) -> DecideResponse:
    state = State("decision_request", request.context)
    base_planner = ToolPlanner()
    memory_planner = MemoryAwarePlanner(base_planner=base_planner, memory=shared_episode_memory)
    planner = ReliabilityAwarePlanner(memory_planner=memory_planner, reliability_weight=request.reliability_weight)

    candidates = base_planner.candidates(state, request.goal)
    ranked_scores = planner.score(candidates, state, request.goal)
    selected = ranked_scores[0]

    execution_success: bool | None = None
    execution_trace: list[DecisionExecutionStep] = []
    if request.execute:
        executor = _build_plan_executor()
        execution = executor.execute(selected.plan, state)
        execution_success = execution.success
        shared_episode_memory.remember(
            state=state,
            goal=request.goal,
            plan=selected.plan,
            success=execution.success,
            reward=1.0 if execution.success else -1.0,
            reason="decide_execute",
            reliability=1.0 if execution.success else 0.0,
            source="/decide",
            scope="api_execute",
        )
        execution_trace = [
            DecisionExecutionStep(
                action=result.resulting_state.data.get("action", "unknown"),
                success=result.success,
                message=result.message,
            )
            for result in execution.results
        ]

    return DecideResponse(
        version=API_VERSION,
        goal=request.goal,
        selected_plan=selected.plan.name,
        selected_reason=selected.plan.reason,
        action_names=[action.name for action in selected.plan.actions],
        executed=request.execute,
        execution_success=execution_success,
        execution_trace=execution_trace,
        scores=[
            DecisionCandidateScore(
                plan=score.plan.name,
                reason=score.plan.reason,
                base_score=score.base_score,
                memory_bias=score.memory_bias,
                reliability=score.reliability,
                reliability_bonus=score.reliability_bonus,
                total_score=score.total_score,
            )
            for score in ranked_scores
        ],
        meta={
            "constraints": request.constraints,
            "constraints_supported": False,
            "context_keys": sorted(request.context.keys()),
            "candidate_count": len(ranked_scores),
            "memory_matches": len(shared_episode_memory.similar(state, request.goal, limit=5)),
            "memory_scope": "process-local in-memory episodes collected by /decide with execute=true",
            "memory_persistence": "postgres+memory" if durable_episode_repository is not None else "memory-only",
            "memory_durable_status": durable_status,
        },
    )


def build_app() -> FastAPI:
    app = FastAPI(title="SCE Core API", version="0.1.0a0")
    durable_episode_repository: PostgresEpisodeRepository | None = None
    durable_status = "disabled"
    try:
        durable_episode_repository = _build_durable_episode_repository()
        if durable_episode_repository is not None:
            durable_status = "enabled"
    except Exception:
        durable_status = "error-fallback-in-memory"
    shared_episode_memory = EpisodeMemory(repository=durable_episode_repository)

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

    @app.post("/decide", response_model=DecideResponse)
    def decide(request: DecideRequest) -> DecideResponse:
        return _run_sce_decision(
            request=request,
            shared_episode_memory=shared_episode_memory,
            durable_episode_repository=durable_episode_repository,
            durable_status=durable_status,
        )

    @app.post("/compare", response_model=CompareResponse)
    def compare(request: CompareRequest) -> CompareResponse:
        decision = _run_sce_decision(
            request=DecideRequest(
                goal=request.goal,
                context=request.context,
                constraints=request.constraints,
                execute=request.execute,
                reliability_weight=request.reliability_weight,
            ),
            shared_episode_memory=shared_episode_memory,
            durable_episode_repository=durable_episode_repository,
            durable_status=durable_status,
        )

        baseline_meta: Dict[str, Any] = {}
        try:
            baseline_client, baseline_meta = build_baseline_client(request.baseline_provider)
            baseline = baseline_client.generate(request.goal, request.context, request.constraints)
        except Exception as exc:
            fallback_client, fallback_meta = build_baseline_client("mock")
            baseline = fallback_client.generate(request.goal, request.context, request.constraints)
            baseline_meta = {
                "requested_provider": request.baseline_provider or "mock",
                "effective_provider": "mock",
                "fallback_used": True,
                "fallback_reason": f"provider initialization failed: {exc.__class__.__name__}",
                **fallback_meta,
            }

        return CompareResponse(
            version=API_VERSION,
            input_summary={
                "goal": request.goal,
                "context_keys": sorted(request.context.keys()),
                "constraints": request.constraints,
                "execute": request.execute,
                "reliability_weight": request.reliability_weight,
            },
            baseline=CompareBaselineResponse(
                answer=baseline.answer,
                rationale=baseline.rationale,
                limitations=baseline.limitations,
                provider=baseline.provider,
                source=baseline.source,
                meta={**baseline.meta, **baseline_meta},
            ),
            sce=CompareSCEResponse(
                selected_plan=decision.selected_plan,
                selected_reason=decision.selected_reason,
                action_names=decision.action_names,
                executed=decision.executed,
                execution_success=decision.execution_success,
                execution_trace=decision.execution_trace,
                scores=decision.scores,
                meta=decision.meta,
            ),
            comparison={
                "differences": [
                    "Baseline returns one answer; SCE returns ranked candidate decisions.",
                    "Baseline rationale is generic; SCE ties explanation to selected plan and score structure.",
                    "Baseline has no adaptive memory; SCE can reuse remembered episodes.",
                    "Baseline has no reliability signal; SCE tracks reliability-aware selection.",
                ],
                "baseline_has_ranking": False,
                "baseline_has_memory": False,
                "baseline_has_reliability": False,
            },
            meta={
                "purpose": "Generic AI vs SCE structured decision contrast on the same input.",
                "baseline_limitations_reference": BASELINE_LIMITATIONS,
            },
        )

    @app.get("/memory", response_model=MemoryResponse)
    def memory(limit: int = Query(default=10, ge=1, le=100)) -> MemoryResponse:
        if durable_episode_repository is not None:
            recent = durable_episode_repository.list_episodes(limit=limit)
            scope = "durable postgres + process-local in-memory runtime"
            persistence = "postgres"
        else:
            recent = list(reversed(shared_episode_memory.episodes[-limit:]))
            scope = "process-local in-memory"
            persistence = "none"
        episodes = [
            MemoryEpisodeView(
                episode_id=str(episode.episode_id),
                created_at=episode.created_at.isoformat(),
                goal=episode.goal,
                selected_plan=episode.plan_name,
                action_names=episode.action_names,
                success=episode.success,
                reward=episode.reward,
                reliability=episode.reliability,
                reason=episode.reason,
            )
            for episode in recent
        ]
        return MemoryResponse(
            version=API_VERSION,
            episodes=episodes,
            meta={
                "scope": scope,
                "source": "/decide with execute=true",
                "persistence": persistence,
                "durable_status": durable_status,
                "total_episodes": len(recent) if durable_episode_repository is not None else len(shared_episode_memory.episodes),
                "returned_episodes": len(episodes),
            },
        )

    @app.get("/reliability", response_model=ReliabilityResponse)
    def reliability(limit: int = Query(default=25, ge=1, le=100)) -> ReliabilityResponse:
        if durable_episode_repository is not None:
            recent = durable_episode_repository.list_episodes(limit=limit)
            scope = "durable postgres + process-local in-memory runtime"
            persistence = "postgres"
        else:
            recent = list(reversed(shared_episode_memory.episodes[-limit:]))
            scope = "process-local in-memory"
            persistence = "none"
        reliability_values = [episode.reliability for episode in recent if episode.reliability is not None]
        successful = [episode for episode in recent if episode.success]
        return ReliabilityResponse(
            version=API_VERSION,
            reliability={
                "recent_window_size": len(recent),
                "reliability_episode_count": len(reliability_values),
                "average_reliability": (sum(reliability_values) / len(reliability_values)) if reliability_values else None,
                "success_rate": (len(successful) / len(recent)) if recent else None,
                "latest": [
                    {
                        "episode_id": str(episode.episode_id),
                        "created_at": episode.created_at.isoformat(),
                        "goal": episode.goal,
                        "selected_plan": episode.plan_name,
                        "success": episode.success,
                        "reliability": episode.reliability,
                        "reward": episode.reward,
                    }
                    for episode in recent[:5]
                ],
            },
            meta={
                "scope": scope,
                "source": "/decide with execute=true",
                "persistence": persistence,
                "durable_status": durable_status,
                "note": "Reliability values are derived from remembered execution outcomes.",
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
    executor = _build_plan_executor()
    agent = CognitiveAgent(executor)

    parser = SimpleIntentParser()
    if request.use_llm_intent:
        parser = _build_llm_parser(request.provider)

    return VoiceOSBridge(agent, parser=parser)


def _build_plan_executor() -> PlanExecutor:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())
    bridge = ToolActionBridge(registry)
    return PlanExecutor(bridge)


def _build_llm_parser(provider: Optional[str]) -> LLMIntentParser:
    selected = (provider or "openai").lower()
    if selected == "anthropic":
        from sce.core.llm_anthropic import AnthropicJSONClient

        return LLMIntentParser(AnthropicJSONClient())

    from sce.core.llm_openai import OpenAIJSONClient

    return LLMIntentParser(OpenAIJSONClient())


app = build_app()
