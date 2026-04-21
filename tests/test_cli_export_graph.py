from __future__ import annotations

import json
import sys

from sce import cli


def test_cli_export_graph_prints_json(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["sce", "export-graph"])
    cli.main()
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert "nodes" in payload
    assert "edges" in payload
    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)
    assert payload["nodes"]
