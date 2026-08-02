# Knowledge Note Style Guide

[English](STYLE_GUIDE.md) | [简体中文](STYLE_GUIDE_zh-CN.md)

Problem READMEs are lightweight source cards. Reusable reasoning belongs in bilingual pages under
`knowledge/<category>/<topic>/`, with relationships and lifecycle facts in `topic.toml`.

## Required structure

- **Overview** defines the reusable idea and its scope.
- **Recognition** records signals that suggest the model applies.
- **Model** defines states, choices, invariants, or mathematical objects before formulas.
- **Derivation** reconstructs recursion, memoization, iteration order, and correctness from the
  model rather than presenting a memorized recurrence.
- **Variants** separates general alternatives and optimizations from constraint-specific shortcuts.
- **Examples** explains what each linked problem contributes without copying its statement.
- **Review log** preserves actual recall outcomes and actionable follow-ups.

Optional sections such as `Visualization`, `Proof details`, and `Exercises` are welcome when they
improve reconstruction. A subsection becomes its own topic only when it has an independent
definition, is reused by multiple pages, or has its own review prompts and examples.

## Visual explanations

Do not add decorative diagrams. Use a visual when relationships, state dependencies, or a sequence
of transformations are materially easier to reconstruct from it. Prefer a compact, reviewable
diagram when sufficient. Use a checked-in PNG or SVG under the topic's `assets/` directory for a
carefully composed walkthrough that Mermaid cannot express clearly. Include useful alt text and
keep the prose understandable without the image.

One visual should explain the shared knowledge class, not be duplicated for every example problem.
Attribute external ideas or visuals that materially shaped the note.

## Language and review

Keep English in `README.md` and natural Simplified Chinese in `README_zh-CN.md`. They should be
semantically aligned, not literal translations. Define symbols before use, keep terminology
consistent, avoid diary narration, and keep complete accepted code in `problems/`.

Append review rows instead of rewriting history. Use ISO dates, record the actual result, and leave
one concrete observation that can change the next review.
