# Axiom Coach Workflow

[English](COACH_WORKFLOW.md) | [简体中文](COACH_WORKFLOW_zh-CN.md)

Axiom Coach is the selection layer in front of the existing practice and review workflows. Its job
is to remove the blank-page question—“what should I do today?”—without turning practice into a
streak, quota, or fixed curriculum replay.

## The daily command

The default interaction is a sentence to Codex, not a terminal command:

```text
Today, what should I practice?
```

When explicit skill invocation is useful:

```text
$axiom-coach Today, what should I practice?
```

The coach inspects repository evidence and returns one primary recommendation with `Lighter`,
`Switch lane`, and `Not today` escape hatches. It asks for platform, duration, or difficulty only
when that choice materially changes the session.

Other useful forms are:

```text
Today I want to recover difference arrays.
Give me an AI session of about 30 minutes.
Continue the previous topic.
Make today's session lighter.
```

These are user-directed overrides, not separate modes to configure.

## Pull, targeted, and scheduled use

| Interaction | Who chooses the topic? | What starts it? |
|---|---|---|
| Coach-led pull | Coach | “Today, what should I practice?” |
| Targeted pull | User | A lane, topic, time box, or desired adjustment |
| Scheduled prompt | Coach automation | A separately configured scheduled task |

The repository skill cannot initiate a conversation by itself. Scheduled prompts should wait until
the manual workflow has been tested and should remain optional; they must not create overdue work or
a streak.

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

The user chooses, solves, submits, and confirms Accepted. The agent handles repository inspection,
scaffolding, Git, generated artifacts, validation, and pull-request bookkeeping.

## Learning flow

The stages are optional rather than linear:

```text
Recall / diagnostic
├── concept blank ───────────────→ Learn
├── implementation fuzzy ───────→ Anchor
├── recognition weak ───────────→ Guided transfer
└── recent transfer evidence ───→ Delayed blind check
```

Same-session transfer is never called a blind check. A real blind check happens in a later session
or after an unrelated problem, and its topic, tags, and method-bearing recommendation reason stay
hidden until the attempt ends or the user asks for help. Candidates whose titles reveal the intended
technique are avoided.

Algorithm and AI lanes share this interaction but not identical evidence. AI topics may need concept,
implementation, and experiment evidence; a small function Accepted verdict covers only part of that.

## Pilot boundary

The first sessions keep diagnostic and assistance details in the conversation. Existing
`problem.toml` and `topic.toml` contracts remain unchanged. Repeated mock sessions—not an imagined
mastery model—will decide whether a later CLI or schema should persist recommendation roles,
disclosure, assistance, or checkpoint outcomes.
