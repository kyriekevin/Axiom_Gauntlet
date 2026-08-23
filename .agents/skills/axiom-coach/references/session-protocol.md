# Coach session protocol

Read this reference when selecting a multi-step topic block, preparing a delayed blind check, or
interpreting the outcome of a coached session.

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

## Evidence language

Describe dated events rather than permanent mastery:

- `anchor completed`: standard form solved with the topic disclosed;
- `guided transfer completed`: a disclosed variation was solved;
- `blind transfer pass`: a delayed problem was recognized and solved without topic help;
- `blind transfer assisted`: the problem was completed after a topic or directional reveal;
- `review pass` or `review fail`: the outcome of one later reconstruction.

Never translate one event into “verified forever”, a mastery percentage, contest readiness, or
coverage of all variants.

## Mock acceptance criteria

The workflow is working when:

- the user can begin from “今天练什么？” without additional configuration;
- the first useful action appears quickly;
- obvious stages are skipped rather than repeated;
- a difficulty mismatch leads to a smoother route, not a learner label;
- same-session transfer and delayed blind evidence remain distinct;
- the user does not need to manage Git, rendering, or PR bookkeeping;
- the session can end after an AC or short debrief without mandatory documentation.
