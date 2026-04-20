from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol

from sce.core.actions import Action, ActionResult
from sce.core.types import State


@dataclass(frozen=True)
class ToolCall:
    """A request to an external tool or system."""

    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    """Result returned by a tool adapter."""

    tool_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class ToolAdapter(Protocol):
    def call(self, call: ToolCall) -> ToolResult:
        ...


class ToolRegistry:
    """Registry for external tool adapters.

    The registry is intentionally explicit: no external service is called unless
    a tool adapter is registered by the application.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolAdapter] = {}

    def register(self, name: str, adapter: ToolAdapter) -> None:
        self._tools[name] = adapter

    def call(self, call: ToolCall) -> ToolResult:
        adapter = self._tools.get(call.tool_name)
        if adapter is None:
            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error=f"No tool registered: {call.tool_name}",
            )
        return adapter.call(call)


class MockSupplierRiskAPI:
    """Deterministic demo adapter representing an external supplier-risk API."""

    def call(self, call: ToolCall) -> ToolResult:
        supplier_id = call.arguments.get("supplier_id", "supplier A")
        return ToolResult(
            tool_name=call.tool_name,
            success=True,
            data={
                "supplier_id": supplier_id,
                "late_delivery_rate": 0.31,
                "complaints_90d": 8,
                "breach_reported": True,
            },
        )


class ToolActionBridge:
    """Execute SCE actions through registered tools and convert results to states."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, action: Action, current_state: State) -> ActionResult:
        tool_name = action.payload.get("tool")
        if not isinstance(tool_name, str):
            return ActionResult(
                action_id=action.action_id,
                success=False,
                message="Action payload must include a string 'tool' field.",
                resulting_state=current_state,
            )

        call = ToolCall(tool_name=tool_name, arguments=action.payload.get("arguments", {}))
        result = self.registry.call(call)
        resulting_state = State(
            state_type="tool_result",
            data={
                "action": action.name,
                "tool": tool_name,
                "success": result.success,
                "data": result.data,
                "error": result.error,
            },
        )
        return ActionResult(
            action_id=action.action_id,
            success=result.success,
            message="Tool call completed." if result.success else (result.error or "Tool call failed."),
            resulting_state=resulting_state,
        )
