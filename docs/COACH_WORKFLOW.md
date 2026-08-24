# Axiom Coach Workflow

[English](COACH_WORKFLOW.md) | [简体中文](COACH_WORKFLOW_zh-CN.md)

Axiom Coach chooses the next useful Algorithms or AI session without turning practice into a
streak, quota, or fixed curriculum replay.

## Three prompts and direct overrides

```text
Today, what should I practice?
Review this week.
Check this month's learning direction.
```

You can also invoke `$axiom-coach` explicitly or override the default in one sentence:

```text
Today I want to recover difference arrays.
Give me an AI session of about 30 minutes.
Continue the previous topic.
Make today's session lighter.
```

The coach returns one primary recommendation with `Lighter`, `Switch lane`, and `Not today`
options. It asks a follow-up only when a missing constraint would materially change the session.

| Scale | What happens | What does not happen |
|---|---|---|
| Daily | Briefly diagnose, then learn, attempt, or solve one calibrated item | A mandatory pipeline that must reach AC |
| Weekly | When evidence is sufficient, use a delayed hidden-topic check as that day's practice | Extra homework or catch-up work after a sparse week |
| Monthly | In 5–10 minutes decide what to continue, lighten, pause, or explore | A coverage report, course-progress audit, or backlog |

Skipping a scale creates no debt.

## Responsibility flow

```text
Axiom Coach
  select topic → diagnose recall → calibrate one next step
        │
        ├── concrete OJ problem chosen → Axiom Practice
        │      scaffold → independent solve → confirmed AC → daily PR
        │
        └── reusable delayed reconstruction → Axiom Review
               synthesize topic → record review evidence → notes PR
```

The user accepts, overrides, or declines the recommendation, then independently solves, submits,
and confirms Accepted. The agent handles repository inspection, scaffolding, validation, skill
routing, Git, generated artifacts, and pull-request bookkeeping.

## Rules and pilot boundary

This pilot defines a human-in-the-loop workflow, not a complete curriculum or deterministic
recommender. The repository skill cannot initiate scheduled prompts; automation requires a separate,
explicit request. Agent behavior is defined in [the Coach skill](../.agents/skills/axiom-coach/SKILL.md),
with detailed routes, tables, evidence vocabulary, and judgment criteria in
[the session protocol](../.agents/skills/axiom-coach/references/session-protocol.md).
