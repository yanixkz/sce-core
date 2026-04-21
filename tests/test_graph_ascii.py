from sce.visualization.graph_ascii import render_ascii_graph


def test_render_ascii_graph_includes_required_markers_and_fields() -> None:
    graph = {
        "nodes": [
            {
                "state_id": "s1",
                "state_type": "source_state",
                "stability": 0.85,
                "is_attractor": True,
                "constraints_satisfied": False,
            },
            {
                "state_id": "s2",
                "state_type": "target_state",
                "stability": 0.42,
                "is_attractor": False,
                "constraints_satisfied": True,
            },
        ],
        "edges": [
            {
                "source_state_id": "s1",
                "target_state_id": "s2",
                "relation_type": "supports",
                "strength": 0.33,
            }
        ],
    }

    output = render_ascii_graph(graph)

    assert "source_state" in output
    assert "target_state" in output
    assert "supports" in output
    assert "(stab=0.85)" in output
    assert "(stab=0.42)" in output
    assert "⭐" in output
    assert "✗" in output
