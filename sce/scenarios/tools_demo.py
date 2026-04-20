from __future__ import annotations

from typing import Any, Dict

from sce.core.actions import Action
from sce.core.tools import MockSupplierRiskAPI, ToolActionBridge, ToolRegistry
from sce.core.types import State


def run_tools_demo() -> Dict[str, Any]:
    registry = ToolRegistry()
    registry.register("supplier_risk_api", MockSupplierRiskAPI())

    bridge = ToolActionBridge(registry)

    current = State(
        state_type="context",
        data={"supplier_id": "supplier A"},
    )

    action = Action(
        name="fetch_supplier_risk",
        description="Fetch supplier risk from external system",
        payload={
            "tool": "supplier_risk_api",
            "arguments": {"supplier_id": "supplier A"},
        },
    )

    result = bridge.execute(action, current)

    return {
        "scenario": "tools",
        "success": result.success,
        "tool_state": result.resulting_state.data,
    }
