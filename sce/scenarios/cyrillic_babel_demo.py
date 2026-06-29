from __future__ import annotations

import hashlib

CYRILLIC_BABEL_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,"
DEFAULT_TARGET_PHRASE = "что выбирает реальность из пространства возможностей"

# Small hand-written lists keep the scoring readable and deterministic.
# They are only toy criteria for a possibility-space demonstration, not real NLP
# and not evidence that the code understands Russian or discovers meaning.
TOY_RUSSIAN_WORDS = frozenset(
    {
        "что",
        "выбирает",
        "реальность",
        "из",
        "пространства",
        "возможностей",
        "мир",
        "слово",
        "форма",
        "смысл",
        "выбор",
        "точка",
    }
)

TOY_BIGRAMS = frozenset(
    {
        "ст",
        "то",
        "ре",
        "но",
        "ра",
        "ос",
        "во",
        "ни",
        "пр",
        "ть",
        "ет",
        "вы",
    }
)

SELECTION_CRITERIA = [
    "dictionary word hits from a tiny in-code Russian word list",
    "whitespace plausibility for the target length",
    "penalty for long repeated-character runs",
    "character-diversity measure",
    "optional hits from a tiny in-code Cyrillic bigram list",
]


def normalize_phrase(phrase: str, alphabet: str = CYRILLIC_BABEL_ALPHABET) -> str:
    """Normalize text to the finite alphabet used by the toy possibility space."""
    lowered = phrase.lower().replace("\n", " ").replace("\t", " ")
    normalized = "".join(char for char in lowered if char in alphabet)
    return " ".join(normalized.split())


def _deterministic_address(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sce-cyrillic-babel:{digest[:16]}:{digest[16:32]}:{digest[32:48]}:{digest[48:64]}"


def _hash_stream(seed: str, length: int) -> str:
    chars: list[str] = []
    counter = 0
    while len(chars) < length:
        digest = hashlib.sha256(f"{seed}:{counter}".encode("utf-8")).digest()
        chars.extend(CYRILLIC_BABEL_ALPHABET[byte % len(CYRILLIC_BABEL_ALPHABET)] for byte in digest)
        counter += 1
    return "".join(chars[:length])


def _candidate_from_word_pool(seed: str, target_length: int) -> str:
    words = sorted(TOY_RUSSIAN_WORDS)
    chosen: list[str] = []
    counter = 0
    # Use a few recognizable words plus deterministic filler so generated samples
    # have some structure without overpowering the intentionally included target.
    while len(" ".join(chosen)) < target_length // 2 and len(chosen) < 4:
        digest = hashlib.sha256(f"{seed}:word:{counter}".encode("utf-8")).digest()
        chosen.append(words[digest[0] % len(words)])
        counter += 1
    prefix = normalize_phrase(" ".join(chosen))
    filler_length = max(0, target_length - len(prefix))
    return (prefix + _hash_stream(f"{seed}:filler", filler_length))[:target_length]


def generate_candidate_sample(normalized_target: str, sample_size: int = 12) -> list[str]:
    """Return a deterministic candidate sample for the toy selection layer."""
    target_length = len(normalized_target)
    candidates = [normalized_target]
    seed = _deterministic_address(normalized_target)
    for index in range(sample_size * 2):
        if index % 4 == 0:
            candidate = _candidate_from_word_pool(f"{seed}:{index}", target_length)
        elif index % 4 == 1:
            candidate = _hash_stream(f"{seed}:{index}", target_length)
        elif index % 4 == 2:
            candidate = normalize_phrase(_hash_stream(f"{seed}:{index}", target_length).replace(".", " "))
            candidate = candidate[:target_length].ljust(target_length, "о")
        else:
            repeated_char = CYRILLIC_BABEL_ALPHABET[index % (len(CYRILLIC_BABEL_ALPHABET) - 3)]
            prefix = _hash_stream(f"{seed}:{index}:prefix", max(0, target_length - 8))
            candidate = (prefix + repeated_char * 8)[:target_length]
        if len(candidate) == target_length and candidate not in candidates:
            candidates.append(candidate)
        if len(candidates) >= sample_size:
            break
    return candidates


def _longest_repeated_run(candidate: str) -> int:
    longest = current = 0
    previous = None
    for char in candidate:
        current = current + 1 if char == previous else 1
        longest = max(longest, current)
        previous = char
    return longest


def score_candidate(candidate: str, target_length: int) -> dict:
    """Score a candidate with transparent toy rules, not semantic understanding."""
    words = [word for word in candidate.split(" ") if word]
    dictionary_hits = sum(1 for word in words if word in TOY_RUSSIAN_WORDS)
    space_count = candidate.count(" ")
    expected_spaces = max(1, target_length // 9)
    whitespace_score = max(0.0, 1.0 - abs(space_count - expected_spaces) / max(expected_spaces, 1))
    longest_run = _longest_repeated_run(candidate)
    repeated_character_penalty = max(0, longest_run - 2)
    diversity = len(set(candidate)) / max(target_length, 1)
    bigram_hits = sum(candidate.count(bigram) for bigram in TOY_BIGRAMS)
    total_score = (dictionary_hits * 4.0) + (whitespace_score * 2.0) + (diversity * 3.0) + (bigram_hits * 0.35) - repeated_character_penalty
    return {
        "candidate": candidate,
        "score": round(total_score, 4),
        "dictionary_hits": dictionary_hits,
        "whitespace_score": round(whitespace_score, 4),
        "repeated_character_penalty": repeated_character_penalty,
        "character_diversity": round(diversity, 4),
        "bigram_hits": bigram_hits,
    }


def select_candidates(candidates: list[str], target_length: int, top_n: int = 5) -> dict:
    scored = [score_candidate(candidate, target_length) for candidate in candidates]
    scored.sort(key=lambda item: (-item["score"], item["candidate"]))
    top_candidates = scored[:top_n]
    return {
        "candidate_count": len(candidates),
        "top_candidates": top_candidates,
        "selected_candidate": top_candidates[0]["candidate"],
        "scoring_breakdown": top_candidates,
        "selection_criteria": SELECTION_CRITERIA,
    }


def run_cyrillic_babel_demo(target_phrase: str = DEFAULT_TARGET_PHRASE) -> dict:
    normalized = normalize_phrase(target_phrase)
    alphabet_size = len(CYRILLIC_BABEL_ALPHABET)
    target_length = len(normalized)
    total_possibilities = alphabet_size**target_length
    candidate_sample = generate_candidate_sample(normalized)
    selection = select_candidates(candidate_sample, target_length)

    return {
        "demo": "cyrillic-babel",
        "alphabet": CYRILLIC_BABEL_ALPHABET,
        "alphabet_size": alphabet_size,
        "input_phrase": target_phrase,
        "normalized_phrase": normalized,
        "target_length": target_length,
        "total_possibility_count": total_possibilities,
        "total_possibility_count_scientific": f"{total_possibilities:.6e}",
        "address": _deterministic_address(normalized),
        "selected_point": normalized,
        "candidate_count": selection["candidate_count"],
        "candidate_sample": candidate_sample,
        "selection_criteria": selection["selection_criteria"],
        "top_candidates": selection["top_candidates"],
        "selected_candidate": selection["selected_candidate"],
        "scoring_breakdown": selection["scoring_breakdown"],
        "cds_connection": {
            "possibility_space": "All strings of the same length over the finite Cyrillic alphabet.",
            "constraints": "The alphabet and fixed length bound the space; normalization removes unsupported symbols.",
            "search_selection": "The target phrase anchors a deterministic candidate sample; toy scoring rules select the highest-scoring sampled candidate and the target also has a deterministic hash address.",
            "meaningful_persistent_pattern": "Meaning is assigned by a reader or task; the demo only shows selection of a stable, reproducible pattern from a vast combinatorial space.",
        },
        "non_claims": [
            "This is a deterministic educational toy, not a simulator of language, consciousness, physics, or Borges's fiction.",
            "The hash address is an index-like label, not evidence that the phrase was discovered by exhaustive search.",
            "Possibility count alone does not create meaning; these toy scores are transparent filters, not semantic understanding or real language modeling.",
        ],
    }


def _format_candidate_row(index: int, scored_candidate: dict) -> str:
    return (
        f"{index}. score={scored_candidate['score']:.4f} "
        f"words={scored_candidate['dictionary_hits']} "
        f"spaces={scored_candidate['whitespace_score']:.2f} "
        f"repeat_penalty={scored_candidate['repeated_character_penalty']} "
        f"diversity={scored_candidate['character_diversity']:.2f} "
        f"bigrams={scored_candidate['bigram_hits']} :: "
        f"{scored_candidate['candidate']}"
    )


def format_cyrillic_babel_demo(result: dict) -> str:
    candidate_rows = [
        _format_candidate_row(index, candidate)
        for index, candidate in enumerate(result["top_candidates"], start=1)
    ]
    return "\n".join(
        [
            "SCE Cyrillic/Bukvitsa-Style Babel Demo",
            "========================================",
            "",
            "A toy demonstration of possibility space -> constraints -> selection -> pattern.",
            "",
            f"Alphabet: {result['alphabet']}",
            f"Alphabet size: {result['alphabet_size']}",
            f"Normalized phrase: {result['normalized_phrase']}",
            f"Target length: {result['target_length']}",
            f"Possibility space size: {result['total_possibility_count_scientific']}",
            f"Candidate sample size: {result['candidate_count']}",
            f"Deterministic address: {result['address']}",
            "",
            "Selection criteria",
            "------------------",
            *[f"- {criterion}" for criterion in result["selection_criteria"]],
            "",
            "Top candidates",
            "--------------",
            *candidate_rows,
            "",
            f"Selected candidate: {result['selected_candidate']}",
            "",
            "Interpretation",
            "--------------",
            "The target phrase is included as an interpretable anchor in a deterministic",
            "sample of same-length strings, then simple toy filters select a candidate.",
            "",
            "CDS connection",
            "--------------",
            f"- Possibility space: {result['cds_connection']['possibility_space']}",
            f"- Constraints: {result['cds_connection']['constraints']}",
            f"- Search/selection: {result['cds_connection']['search_selection']}",
            f"- Meaningful/persistent pattern: {result['cds_connection']['meaningful_persistent_pattern']}",
            "",
            "Limitations / non-claims",
            "------------------------",
            *[f"- {claim}" for claim in result["non_claims"]],
        ]
    )


if __name__ == "__main__":
    print(format_cyrillic_babel_demo(run_cyrillic_babel_demo()))
