# Cyrillic Babel Demo

The Cyrillic/Bukvitsa-style Babel demo is a small deterministic educational toy for SCE Core. It illustrates a simple chain:

```text
Possibility Space → Constraints → Search/Selection → Meaningful/Persistent Pattern
```

It does **not** copy or reproduce libraryofbabel.info. It uses a related combinatorial idea: a finite alphabet and fixed text length imply a very large but finite set of possible strings.

## How to run

From an editable install of SCE Core:

```bash
sce demo cyrillic-babel
```

As a standalone example script:

```bash
python examples/cyrillic_babel_demo.py
```

## What the demo shows

The demo defines a finite Cyrillic alphabet:

```text
абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,
```

It then normalizes a target phrase, by default:

```text
что выбирает реальность из пространства возможностей
```

Unsupported characters are removed, whitespace is normalized, and the resulting string length is measured. The total number of possible same-length strings is then:

```text
alphabet_size ** target_length
```

Finally, the normalized phrase receives a deterministic SHA-256 based address. This address makes the selected phrase reproducibly identifiable without claiming that the system performed exhaustive search. The CLI also prints the possibility-space size, candidate sample size, selection criteria, top candidates, and selected candidate.

## Selection-pressure extension

The demo now adds a small v2 selection layer on top of the original fixed-alphabet and deterministic-address illustration. It samples a small, deterministic set of same-length Cyrillic candidate strings from the enormous possibility space and intentionally includes the normalized target phrase as one candidate. Including the target is an interpretable anchor, not a claim that the system found meaning by itself.

Each sampled candidate is scored with transparent toy rules:

- hits against a tiny in-code Russian word list,
- rough whitespace plausibility for the target length,
- a penalty for long repeated-character runs,
- character-diversity measurement, and
- hits against a tiny in-code Cyrillic bigram list.

The highest-scoring sampled candidate is reported as the selected candidate, together with a scoring breakdown for the top candidates. This demonstrates reproducible candidate filtering under explicit criteria: a toy form of selection pressure over sampled strings. It is not semantic understanding, real Russian NLP, consciousness modeling, or a reproduction of the Library of Babel.

## Why Cyrillic

SCE Core has multilingual documentation and conceptual material, including Russian-language material. A Cyrillic alphabet makes the example visually distinct from common Latin-alphabet toy examples and keeps the phrase close to the repository's existing conceptual vocabulary around possibility, selection, and stability.

The term “Bukvitsa-style” is used only as a loose stylistic cue toward Cyrillic letter forms. The implementation is a plain Unicode string alphabet, not a historical or philological model of any writing tradition.

## Relation to Library of Babel

The demo is inspired by the general educational idea associated with finite-alphabet combinatorial libraries: if an alphabet and length are fixed, the complete possibility space is finite but enormous.

The demo does not reproduce the Library of Babel website, its indexing scheme, its interface, its text corpus presentation, or Borges's literary work. It is a compact SCE Core example focused on combinatorics and selection.

## Relation to CDS

The demo maps the toy problem to Constraint-Driven Stability (CDS) conservatively:

| CDS-facing idea | Demo element |
|---|---|
| Possibility space | All strings of the target length over the finite Cyrillic alphabet. |
| Constraints | Allowed alphabet, fixed length, and normalization rules. |
| Search/selection | A deterministic sample is scored with transparent toy rules; the target phrase is included as an anchor and also assigned a deterministic hash address. |
| Meaningful/persistent pattern | The normalized phrase is a reproducible pattern that can be interpreted by a reader or downstream task. |

This is not a full SCE decision workflow. It is a minimal illustration of how constraints define a bounded space, how a deterministic sample can be filtered by explicit toy criteria, and how selection identifies a tiny subset of interest.

## Why possibility alone is not meaning

The possibility space contains every allowed string of the same length, including strings that look random or uninterpretable to a reader. Merely being possible does not make a string meaningful.

Meaning enters through external criteria: language, reader interpretation, task relevance, empirical grounding, or some other selection rule. In the demo, the target phrase is supplied in advance, so its meaningfulness is not discovered by the algorithm.

## Why selection matters

Selection turns a vast undifferentiated possibility space into a concrete object of attention. The deterministic address makes the selected phrase persistent and reproducible: running the same normalization and hashing steps gives the same result.

For CDS-oriented explanation, this highlights the difference between:

- a huge set of possible states, and
- a selected state or pattern that remains identifiable under explicit constraints.

## Limitations and non-claims

- This is a deterministic toy example, not a scientific simulator.
- It does not model consciousness, reality, physics, language emergence, or semantic understanding.
- It does not claim that combinatorial possibility creates meaning by itself.
- It does not claim to explain Borges or reproduce the Library of Babel project.
- The hash address is only a reproducible label, not proof of exhaustive search.
- The phrase is selected by the demo author/user, not discovered from data.
