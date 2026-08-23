# Axiom Coach Workflow

[English](COACH_WORKFLOW.md) | [简体中文](COACH_WORKFLOW_zh-CN.md)

Axiom Coach is the selection layer in front of the existing practice and review workflows. Its job
is to remove the blank-page question—“what should I do today?”—without turning practice into a
streak, quota, or fixed curriculum replay.

## Three commands to remember

The default interaction is a sentence to Codex, not a terminal command. Daily practice starts with:

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

Weekly and monthly use equally small prompts:

```text
Review this week.
Check this month's learning direction.
```

| Scale | What happens | What does not happen |
|---|---|---|
| Daily | One brief diagnostic, then the smallest useful learn, attempt, or solve action | A mandatory pipeline that must reach AC |
| Weekly | When evidence is sufficient, a delayed hidden-topic check becomes that day's practice; useful knowledge synthesis is optional | Extra homework, a weekly quota, or catch-up work after a sparse week |
| Monthly | A 5–10 minute decision about what to continue, lighten, pause, or explore next | A coverage report, course-progress audit, or backlog |

Daily, weekly, and monthly are three observation scales, not three stacked assignments. Each is
triggered when useful; skipping one creates no debt.

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

The user accepts, overrides, or declines the recommendation, then independently solves, submits, and
confirms Accepted. The agent handles repository inspection, scaffolding, Git, generated artifacts,
validation, skill routing, and pull-request bookkeeping.

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

For a calibrated OJ problem, the useful process is broader than “write code and get AC”:

```text
understand and model → invariant and complexity → independent implementation
→ counterexamples or stress testing → debugging → confirmed AC → code review
```

This is a possible loop, not a form that must be completed every day. A session may stop after
learning something useful, making a serious attempt, or locating the actual blocker. Testing,
debugging, and review count as trained only when they really happened.

## What the evidence means

| Layer | Example | What it supports |
|---|---|---|
| Result evidence | Platform Accepted plus recorded time and space complexity | The outcome of one concrete submission |
| Process evidence | Modeling, assistance, a counterexample, bug, test strategy, or code review | What was actually exercised during the session |
| Ability evidence | A delayed, hidden-topic, unfamiliar, mostly independent solve or reconstruction | A stronger observation of retrieval and transfer |

An AC is valuable, but it is not a mastery label. Missing process evidence stays unknown, and one
delayed success is still one dated observation. Weekly and monthly language stays at `observed`,
`not yet observed`, or `needs another observation` rather than percentages or scores.

## Capability focus

| Capability | How the workflow exercises it | Limit |
|---|---|---|
| Retrieval and recognition | Closed-book diagnosis and delayed hidden-topic checks | Immediate template replay is not delayed evidence |
| Decomposition and modeling | Converting a statement into states, graphs, or subproblems | AC alone does not reveal the model |
| Correctness and complexity | Invariants, boundaries, counterexamples, and cost analysis | Judge tests are not a correctness proof |
| Implementation, testing, and debugging | Independent code, hand cases, stress tests, and failure localization | These improve only when actually practiced |
| Review of AI-generated algorithm code | Checking models, invariants, boundaries, complexity, and counterexamples | This does not replace full architecture, security, maintainability, or systems review |
| AI fundamentals | Separate concept, implementation, and experiment evidence | A Deep-ML function AC usually supports implementation only |

## Pilot boundary

This version defines the human-in-the-loop workflow and skill handoffs. It does not claim that Axiom
already has a complete curriculum or stable deterministic recommender. The first sessions keep
diagnostic and assistance details in the conversation; existing `problem.toml` and `topic.toml`
contracts remain unchanged. Repeated sessions—not an imagined mastery model—will decide whether a
later curriculum, CLI, or schema should persist recommendation roles, disclosure, assistance, or
checkpoint outcomes.
