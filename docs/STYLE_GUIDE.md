# Problem Note Style Guide

[English](STYLE_GUIDE.md) | [简体中文](STYLE_GUIDE_zh-CN.md)

This guide defines the human-readable contract for `README.md` and `README_zh-CN.md` in every problem directory. Machine-readable facts belong in the adjacent `problem.toml`; the notes should focus on understanding and recall.

## Required structure

Use the following sections in this order:

```markdown
# <Problem ID>. <Problem Title>

> Source: [<Platform>](<canonical problem URL>)

## Core insight

## Approach

## Why it works

## Complexity

## Pitfalls

## Review log
```

The sections have distinct jobs:

- **Core insight** states the decisive observation in one or two sentences.
- **Approach** explains the algorithm as a short sequence of ideas, not as a line-by-line translation of the code.
- **Why it works** gives a convincing correctness argument. Use an invariant, exchange argument, induction, case analysis, or another fitting proof shape.
- **Complexity** states time and auxiliary-space complexity, defines non-obvious variables, and distinguishes average from worst-case behavior when relevant.
- **Pitfalls** records failed approaches, boundary conditions, implementation traps, and platform-specific surprises worth remembering.
- **Review log** preserves dated attempts and what changed in the solver's understanding.

Optional sections such as `## Visualization`, `## Alternative approaches`, and `## Follow-ups` may be inserted when they add real explanatory value.

## Visual explanations

Visualization is optional. Do not add a diagram merely to fill the template.

When a diagram is useful, prefer Mermaid embedded directly in Markdown because it is reviewable, diffable, and maintainable. Good uses include state transitions, trees, graphs, pointer movement, and multi-step control flow.

Use a local SVG or PNG under the problem's `assets/` directory only when Mermaid cannot express the idea clearly, such as detailed geometry, dense array-state illustrations, or a carefully composed visual walkthrough. Every visual must have a short introduction and useful alt text; the prose must still communicate the essential idea if the image fails to render.

## Language and expression

- Keep the English note in `README.md` and the Simplified Chinese note in `README_zh-CN.md`; link them to each other at the top.
- Use English for metadata, code identifiers, and code comments. The Chinese note may introduce important terms bilingually, such as “invariant（不变量）”.
- Keep the two notes semantically aligned without forcing sentence-by-sentence literal translation.
- Lead with the insight, then add only the detail needed to reconstruct the solution.
- Prefer concrete claims over diary narration: write “maintain a decreasing deque” rather than “then I thought of using a deque.”
- Define symbols before using them and keep terminology consistent with the implementation.
- Keep code out of the note unless a very small fragment is essential to the explanation; complete accepted implementations belong in `solution.<ext>` files.
- Do not copy the complete problem statement, sample set, or editorial. Link to the canonical source and summarize only the constraints or setup needed for the explanation.
- Attribute any external idea, proof, or visualization that materially shaped the note.

## Review log

Append one row for each meaningful revisit; never rewrite older rows to make the learning path look cleaner.

```markdown
## Review log

| Date | Event | Result | Reflection |
| --- | --- | --- | --- |
| 2026-08-01 | Initial solve | Accepted | Missed one empty-input boundary case before submission. |
| 2026-08-15 | Independent review | Recalled with hint | Revisit the invariant before the next review. |
```

Use an ISO date (`YYYY-MM-DD`). The event should distinguish the initial solve, documentation pass, independent review, contest revisit, or another meaningful activity. Record the actual outcome and one actionable observation; a bare “reviewed” entry is not useful.
