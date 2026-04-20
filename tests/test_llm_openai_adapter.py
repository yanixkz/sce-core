from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Requires OPENAI_API_KEY and network access")
def test_openai_client_basic():
    from sce.core.llm_openai import OpenAIJSONClient

    client = OpenAIJSONClient()
    result = client.complete_json(
        "Return JSON with candidates: [{\"state_type\": \"test\", \"data\": {\"x\": 1}}]"
    )

    assert "candidates" in result
