import json

from sce import cli


def test_export_graph_writes_to_outfile(monkeypatch, tmp_path, capsys):
    out_file = tmp_path / "graph.json"
    monkeypatch.setattr(cli, "_export_supplier_graph", lambda: {"nodes": []})
    monkeypatch.setattr("sys.argv", ["sce", "export-graph", "--out", str(out_file)])

    cli.main()

    assert json.loads(out_file.read_text(encoding="utf-8")) == {"nodes": []}
    captured = capsys.readouterr()
    assert captured.out == ""


def test_visualize_graph_writes_ascii_to_outfile(monkeypatch, tmp_path, capsys):
    out_file = tmp_path / "graph.txt"
    monkeypatch.setattr(cli, "_export_supplier_graph", lambda: {"nodes": []})
    monkeypatch.setattr(cli, "render_ascii_graph", lambda _graph: "ASCII GRAPH")
    monkeypatch.setattr("sys.argv", ["sce", "visualize-graph", "--out", str(out_file)])

    cli.main()

    assert out_file.read_text(encoding="utf-8") == "ASCII GRAPH"
    captured = capsys.readouterr()
    assert captured.out == ""
