from sce.scenarios.stability_basin import format_stability_basin_demo, run_stability_basin_demo


def test_stability_basin_default_boundary():
    result = run_stability_basin_demo()

    assert result["selected_candidate"]["label"] == "Candidate A"
    assert [item["stable_label"] for item in result["perturbations"]] == ["Yes", "Yes", "Yes", "No", "No"]
    assert result["stability_basin_size_percent"] == 10


def test_stability_basin_pretty_output_contains_table_and_ascii():
    rendered = format_stability_basin_demo(run_stability_basin_demo())

    assert "Stability Basin" in rendered
    assert "Perturbation  Stable?" in rendered
    assert " 10%          Yes" in rendered
    assert " 20%          No" in rendered
    assert "Stable\n███████████████" in rendered
    assert "Unstable\n██" in rendered
