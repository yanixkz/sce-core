import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from analyze_bitcoin_scale_hierarchy import link_levels


def test_merge_and_coarse_birth_are_counted_separately():
    fine = [(10, "H", 1.), (12, "H", 2.), (30, "L", 1.)]
    coarse = [(11, "H", 2.), (30, "L", 1.), (60, "H", 3.)]
    result = link_levels(fine, coarse, 4)
    assert result["matched_fine"] == 3
    assert result["coarse_merges"] == 1
    assert result["excess_children"] == 1
    assert result["coarse_births"] == 1


def test_parent_matching_never_crosses_extremum_kind():
    result = link_levels([(10, "H", 1.)], [(10, "L", 1.)], 2)
    assert result["matched_fine"] == 0
    assert result["coarse_births"] == 1
