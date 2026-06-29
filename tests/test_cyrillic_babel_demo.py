from sce.scenarios.cyrillic_babel_demo import (
    DEFAULT_TARGET_PHRASE,
    generate_candidate_sample,
    normalize_phrase,
    run_cyrillic_babel_demo,
)


def test_cyrillic_babel_normalization_keeps_supported_cyrillic_only():
    assert normalize_phrase("  ЧТО?!\nВыбирает\tReality  ") == "что выбирает"


def test_cyrillic_babel_address_is_deterministic():
    first = run_cyrillic_babel_demo()
    second = run_cyrillic_babel_demo()

    assert first["address"] == second["address"]
    assert first["address"].startswith("sce-cyrillic-babel:")


def test_cyrillic_babel_candidate_generation_is_deterministic():
    normalized = normalize_phrase(DEFAULT_TARGET_PHRASE)
    first = generate_candidate_sample(normalized)
    second = generate_candidate_sample(normalized)

    assert first == second
    assert first[0] == normalized
    assert all(len(candidate) == len(normalized) for candidate in first)


def test_cyrillic_babel_selected_candidate_remains_stable():
    result = run_cyrillic_babel_demo()

    assert result["selected_candidate"] == result["normalized_phrase"]
    assert result["top_candidates"][0]["candidate"] == result["selected_candidate"]


def test_cyrillic_babel_result_contains_scoring_breakdown():
    result = run_cyrillic_babel_demo()

    assert result["candidate_count"] == len(result["candidate_sample"])
    assert result["scoring_breakdown"] == result["top_candidates"]
    assert result["scoring_breakdown"]
    for scored_candidate in result["scoring_breakdown"]:
        assert {
            "candidate",
            "score",
            "dictionary_hits",
            "whitespace_score",
            "repeated_character_penalty",
            "character_diversity",
            "bigram_hits",
        } <= scored_candidate.keys()
