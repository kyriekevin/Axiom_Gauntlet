---
name: axiom-practice
description: Guide a weekday Axiom Gauntlet problem from scaffolding through independent solving, platform-confirmed acceptance, complexity recording, and code review. Use when the user starts or continues an OJ problem, asks for spoiler-controlled hints or debugging, provides an Accepted screenshot or confirmation, or requests review of accepted code. Do not use for problem recommendation, spaced-review scheduling, or cross-problem knowledge-wiki maintenance.
---

# Axiom Practice

Keep daily practice focused on solving. Use the repository CLI for deterministic bookkeeping and
leave reusable knowledge synthesis to `axiom-review`.

## Establish context

1. Read the root `AGENTS.md` and the target `problem.toml` when it exists.
2. Read `docs/SCHEMA.md` only when the machine contract is needed.
3. Use Asia/Shanghai dates and pass explicit `--date YYYY-MM-DD` values.
4. Keep recommendations, review scheduling, and knowledge-wiki editing out of scope.

## Start a problem

Gather the platform, ID, title, official URL, difficulty, useful tags, and language. Never copy the
full statement into the repository. Reuse an existing entry instead of overwriting it.

```bash
uv run axiom new <platform> <id> \
  --title "<title>" \
  --url "<url>" \
  --difficulty "<difficulty>" \
  --language <language>
```

Report the created path and leave the state as `draft`.

## Protect independent solving

- Do not reveal a complete solution unless the user explicitly asks for one.
- Escalate help gradually: clarify constraints, give a directional hint, identify the key
  observation, explain an invariant, then offer pseudocode.
- Inspect and debug the user's code when asked, but do not replace it silently.
- Treat compilation and local tests as debugging evidence only. Never record AC from them.

## Record acceptance

Require explicit confirmation that the online judge returned Accepted. Preserve the exact accepted
implementation unless the user asks to change it. Review the accepted code for correctness,
counterexamples, boundary cases, clarity, complexity, and useful alternative approaches. Before the
transition, record both time and auxiliary-space complexity, including non-obvious variables. When
the review yields a concise problem-specific lesson, preserve it as the optional activity reflection.

```bash
uv run axiom accept <platform> <id> \
  --language <language> \
  --date <YYYY-MM-DD> \
  --time-complexity "O(...)" \
  --space-complexity "O(...)" \
  --reflection "<problem-specific observation>"
```

Distinguish a general technique from a constraint-specific shortcut. Report suggestions before
editing; do not present an unsubmitted rewrite as confirmed AC.

Keep each problem README as a lightweight source card. Capture only problem-specific evidence in
`problem.toml` and solution files. Do not duplicate a reusable explanation beside every similar
problem.

## Finish the session

Run the relevant checks, then the complete gate before handoff:

```bash
uv run axiom validate
uv run axiom render
make verify
```

Summarize the state, accepted language, recorded complexities, code-review conclusions, and checks.
If broader synthesis is valuable, defer it to a later `notes/YYYY-MM-DD` branch with
`axiom-review`; do not start that work implicitly.
