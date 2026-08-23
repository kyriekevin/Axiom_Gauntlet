# Coach session protocol

Read this reference when selecting a multi-step topic block, preparing a delayed blind check, or
interpreting the outcome of a coached session.

## Cadence

| Scale | Trigger | Useful action | Stop condition |
|---|---|---|---|
| Daily | “今天练什么？” or a targeted request | Diagnose briefly, then learn, attempt, or solve one calibrated item | Stop after a useful learning result, attempt, blocker diagnosis, or AC |
| Weekly | “复盘这周” and enough related evidence or delay | Use a delayed hidden-topic check as that day's practice; optionally identify one synthesis candidate | If evidence is sparse, summarize and skip; create no extra assignment |
| Monthly | “做本月路线检查” | In 5–10 minutes decide what to continue, lighten, pause, or explore | Adjust only future direction; do not create catch-up work |

These are three observation scales, not stacked obligations. Route weekly knowledge synthesis to
`axiom-review`; keep the weekly learning overview and monthly route decision in Coach.

## Recommendation card

Present a compact card with this shape:

```text
Today
  Lane: Algorithms | AI
  Role: Recall | Learn | Anchor | Guided transfer | Blind check | Capstone
  Why now: one evidence-based sentence
  Effort: a rough range
  Start: one concrete action

Options: Lighter | Switch lane | Not today
```

Do not ask the user to choose a platform, mode, difficulty, and duration before making the default
recommendation. Ask a follow-up only when a material constraint cannot be inferred safely.

## Algorithm session

Use a recall prompt to locate the gap, then choose only the needed stages:

```text
Recall / diagnostic
├── concept blank ───────────────→ Learn → Anchor
├── implementation fuzzy ───────→ Anchor
├── recognition weak ───────────→ Guided transfer
└── recent transfer evidence ───→ Delayed blind check
```

A standard implementation can be an Anchor even if it is easy. Guided transfer should change a
constraint, representation, boundary, or modeling step without making several difficulty jumps at
once. An advanced-course problem is an optional checkpoint only when its prerequisites are present;
it is not the universal endpoint of a topic.

When a concrete problem is chosen, preserve this possible training loop:

```text
understand and model
→ state invariant and complexity
→ implement independently
→ construct counterexamples or stress tests when useful
→ debug model or code
→ platform-confirmed AC
→ review correctness, complexity, boundaries, and alternatives
```

The arrows are not mandatory form fields. Record only what actually happened, and allow a session
to end with a useful attempt or diagnosed blocker. Hard problems are valuable only while the user
can productively engage; learning a solution and returning later for a hidden check is valid.

For a first recovery, prefer a focused blind check whose candidate pool mostly exercises the recent
topic. Later use mixed blind checks across several recovered topics. A blind-check recommendation
must not disclose tags, the topic, or a method-bearing reason before the attempt. Avoid a candidate
whose title itself reveals the technique.

## AI session

Evaluate AI topics on separate dimensions:

- `Concept`: explain assumptions, model, objective, and important gradients;
- `Implementation`: implement the core primitive while handling shape, dtype, boundaries, and
  numerical stability;
- `Experiment`: split data correctly, choose a baseline and metric, evaluate, and inspect failures
  or limitations.

The dimensions may be completed in different sessions. A small function Accepted verdict is useful
implementation evidence but does not establish model or experiment understanding. Not every topic
needs its own Lab or Project; combine related topics into occasional capstones.

An experiment should at least expose a hypothesis, baseline or metric, and interpretation of the
result. One experiment is still one observation, not proof of general transfer.

## Value and limits

| Capability | Where the workflow exercises it | Evidence boundary |
|---|---|---|
| Retrieval and recognition | Closed-book recall and delayed hidden-topic problems | Immediate template replay is not delayed evidence |
| Decomposition and modeling | Turning a statement into states, graph structure, or subproblems | AC alone does not expose the model used |
| Correctness reasoning | Invariants, boundary analysis, and counterexamples | Judge tests are result evidence, not a proof |
| Complexity intuition | Predicting and reviewing time and auxiliary space | Record the actual implementation, not an idealized rewrite |
| Implementation fluency | Independent coding under exact constraints | Assisted completion should remain visibly assisted |
| Testing and debugging | Hand cases, stress tests, differential checks, and failure localization | These count only when actually performed |
| AI algorithm-code review | Checking generated models, invariants, boundaries, complexity, and counterexamples | This is not full architecture, security, maintainability, or systems review |
| AI understanding | Concept, implementation, and experiment evidence | A Deep-ML function AC usually covers implementation only |

## Evidence language

Keep three layers distinct:

| Layer | Minimal evidence | Do not infer |
|---|---|---|
| Result | Accepted plus recorded time and space complexity | Topic mastery |
| Process | Assistance level plus one useful model, counterexample, bug, or test strategy | Abilities that were not observed |
| Ability | Delayed, hidden-topic, unfamiliar, mostly independent performance | Permanent mastery or a precise score |

Describe dated events rather than permanent mastery:

- `anchor completed`: standard form solved with the topic disclosed;
- `guided transfer completed`: a disclosed variation was solved;
- `blind transfer pass`: a delayed problem was recognized and solved without topic help;
- `blind transfer assisted`: the problem was completed after a topic or directional reveal;
- `review pass` or `review fail`: the outcome of one later reconstruction.

Never translate one event into “verified forever”, a mastery percentage, contest readiness, or
coverage of all variants. At weekly and monthly scales, use “observed”, “not yet observed”, and
“needs another observation”.

## Mock acceptance criteria

The workflow is working when:

- the user can begin from “今天练什么？” without additional configuration;
- the first useful action appears quickly;
- obvious stages are skipped rather than repeated;
- a difficulty mismatch leads to a smoother route, not a learner label;
- same-session transfer and delayed blind evidence remain distinct;
- the user does not need to manage Git, rendering, or PR bookkeeping;
- the session can end after an AC or short debrief without mandatory documentation.
- weekly review can replace that day's practice and sparse weeks are skipped without debt;
- monthly review changes future direction without producing a progress audit.
