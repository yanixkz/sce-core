from __future__ import annotations

import hashlib

CYRILLIC_BABEL_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,"
DEFAULT_TARGET_PHRASE = "что выбирает реальность из пространства возможностей"


def normalize_phrase(phrase: str, alphabet: str = CYRILLIC_BABEL_ALPHABET) -> str:
    """Normalize text to the finite alphabet used by the toy possibility space."""
    lowered = phrase.lower().replace("\n", " ").replace("\t", " ")
    normalized = "".join(char for char in lowered if char in alphabet)
    return " ".join(normalized.split())


def _deterministic_address(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sce-cyrillic-babel:{digest[:16]}:{digest[16:32]}:{digest[32:48]}:{digest[48:64]}"


def run_cyrillic_babel_demo(target_phrase: str = DEFAULT_TARGET_PHRASE) -> dict:
    normalized = normalize_phrase(target_phrase)
    alphabet_size = len(CYRILLIC_BABEL_ALPHABET)
    target_length = len(normalized)
    total_possibilities = alphabet_size**target_length

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
        "cds_connection": {
            "possibility_space": "All strings of the same length over the finite Cyrillic alphabet.",
            "constraints": "The alphabet and fixed length bound the space; normalization removes unsupported symbols.",
            "search_selection": "The target phrase is treated as one selected point identified by a deterministic hash address.",
            "meaningful_persistent_pattern": "Meaning is assigned by a reader or task; the demo only shows selection of a stable, reproducible pattern from a vast combinatorial space.",
        },
        "non_claims": [
            "This is a deterministic educational toy, not a simulator of language, consciousness, physics, or Borges's fiction.",
            "The hash address is an index-like label, not evidence that the phrase was discovered by exhaustive search.",
            "Possibility count alone does not create meaning; interpretation and selection criteria matter.",
        ],
    }


def format_cyrillic_babel_demo(result: dict) -> str:
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
            f"Total possible strings of this length: {result['total_possibility_count_scientific']}",
            f"Deterministic address: {result['address']}",
            "",
            "Interpretation",
            "--------------",
            "The phrase is one reproducibly addressable point inside the finite but enormous set",
            "of same-length strings over the chosen Cyrillic alphabet.",
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
