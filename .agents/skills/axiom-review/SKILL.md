---
name: axiom-review
description: Turn delayed or weekly review of accepted Axiom Gauntlet problems into reusable bilingual knowledge pages. Use when the user wants to review a week, group similar problems, reconstruct a technique, update the knowledge wiki, record a knowledge review result, or create a genuinely useful explanatory visual. Do not use for the initial weekday solve, problem recommendations, or recording an unconfirmed Accepted verdict.
---

# Axiom Review

Organize notes by reusable knowledge, not by one page per problem. Preserve evidence in
`problems/`; synthesize transferable reasoning in `knowledge/`.

## Establish the review boundary

1. Read `AGENTS.md`, `docs/KNOWLEDGE_ARCHITECTURE.md`, `docs/SCHEMA.md`, and
   `docs/STYLE_GUIDE.md` as needed.
2. Work on a short-lived `notes/YYYY-MM-DD` branch unless the user specifies another branch.
3. Inspect relevant `problem.toml` files and accepted solutions without rewriting accepted code.
4. Use Asia/Shanghai dates for lifecycle events.

## Reconstruct before documenting

Ask the user to reconstruct the model before polishing the note: recognition signals, state meaning,
choices, dependency order, and why the recurrence follows. Record the actual recall outcome rather
than converting the review into an answer reveal. When several problems share a model, identify
what each contributes and avoid parallel near-duplicate pages.

For dynamic programming, prefer this explanatory order when it fits:

1. abstract the game or process into a state;
2. derive the recursive relation from available choices;
3. show memoized search as direct evaluation of that relation;
4. show bottom-up order from state dependencies;
5. separate general variants and special mathematical shortcuts.

## Locate or create the canonical topic

Search `knowledge/INDEX.md` and topic manifests first. Use an OI-style hierarchy such as
`dynamic-programming/interval-dp`; do not create a topic named after a single problem.

```bash
uv run axiom knowledge new <category/topic> \
  --title "<English title>" \
  --title-zh-cn "<中文标题>" \
  --tag <tag> \
  --example '<uid>=<role>'
```

Link examples in `topic.toml` and explain their distinct roles in the Examples section. Keep the two
languages semantically aligned without forcing literal translation or copying full statements.

## Use visuals deliberately

Add a visual only when it materially helps reconstruct the abstraction, state dependency, or
transition. Prefer a small reviewable diagram when it is clear. Use ImageGen for an intuitive,
carefully composed raster walkthrough when Mermaid would be awkward; store it under the canonical
topic's `assets/`, add useful alt text, and keep the prose independently understandable. One visual
should explain the knowledge class, not be repeated for each similar problem.

## Record knowledge lifecycle

After all required sections are complete, record the documentation event through the CLI:

```bash
uv run axiom knowledge document <category/topic> --date <YYYY-MM-DD>
```

For a later independent revisit, record the real outcome:

```bash
uv run axiom knowledge review <category/topic> \
  --date <YYYY-MM-DD> \
  --result <pass|fail>
```

Do not edit `state` or `activity` manually. If validation rejects a transition, fix the note or
metadata rather than bypassing the CLI.

## Finish the review

```bash
uv run axiom knowledge render
uv run axiom validate
make verify
```

Summarize the canonical topic, contributing examples, reconstruction outcome, visual rationale,
lifecycle events, and verification. Keep commits focused and use Conventional Commits.
