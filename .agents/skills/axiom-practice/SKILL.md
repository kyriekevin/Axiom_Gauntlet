---
name: axiom-practice
description: Guide the Axiom Gauntlet algorithm-practice workflow from creating a problem through independent solving, platform-confirmed acceptance, code review, and bilingual documentation. Use when the user wants to start or continue an OJ problem, asks for spoiler-controlled hints or debugging, provides an Accepted screenshot or confirmation, requests review of accepted code, or wants the discussion turned into English and Simplified Chinese problem notes. Do not use for problem recommendation, spaced-review scheduling, or knowledge-wiki maintenance.
---

# Axiom Practice

Keep the conversation as the human interface and use the repository CLI for deterministic state
changes. Preserve independent problem solving while turning confirmed work into durable notes.

## Establish context

1. Read the root `AGENTS.md` and the target `problem.toml` when it exists.
2. Read `docs/SCHEMA.md` and `docs/STYLE_GUIDE.md` only when their contract is needed.
3. Use Asia/Shanghai calendar dates and pass explicit `--date YYYY-MM-DD` values to lifecycle
   commands.
4. Keep selection recommendations, spaced-review queues, and cross-problem wiki work out of scope.

## Start a problem

Gather or derive the platform, canonical problem ID, title, source URL, difficulty, useful tags, and
implementation language. Prefer the official problem page when web lookup is needed. Never copy the
full statement into the repository.

Create the draft with `uv run axiom new`. Reuse an existing entry instead of overwriting it.

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

Require an explicit statement that the online judge returned Accepted. A legible screenshot or
submission link can support the confirmation but is optional. Do not store screenshots unless the
user asks.

Before changing state:

1. Save the exact accepted implementation in the listed `solution.<ext>` file.
2. Confirm the selected language matches `problem.toml`.
3. Run relevant local checks without treating them as the verdict.
4. Call the lifecycle command with the confirmed language and date.

```bash
uv run axiom accept <platform> <id> --language <language> --date <YYYY-MM-DD>
```

After recording AC, review the code for correctness, counterexamples, complexity, boundary cases,
clarity, and better approaches. Report suggestions first. Do not rewrite accepted code unless the
user explicitly requests changes; distinguish tested improvements from platform-confirmed code.

## Build bilingual notes

Discuss the user's reasoning in Chinese first when that is their natural language. Write
`README_zh-CN.md` as natural Chinese, introducing important English terms where useful. Then write
`README.md` as a semantically aligned English explanation rather than a literal translation.

Complete the required insight, approach, correctness, complexity, pitfalls, and review-log
sections. Keep machine facts in `problem.toml`, complete code in solution files, and full problem
statements at the official source.

Once both notes are complete, record the transition:

```bash
uv run axiom document <platform> <id> --date <YYYY-MM-DD>
```

If validation rejects the transition, fix the notes or metadata rather than bypassing the CLI.

## Finish the session

Run:

```bash
uv run axiom validate
uv run axiom render
make verify
```

Summarize the problem state, accepted language, code-review conclusions, note files changed, and
verification results. Never claim an online-judge verdict that the user did not confirm.
