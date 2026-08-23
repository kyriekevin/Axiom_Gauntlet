---
name: axiom-coach
description: Select and calibrate Algorithms or AI learning from Axiom evidence across daily practice, weekly evidence review, and monthly route checks. Use when the user asks what to practice today, reviews the week, checks the monthly direction, targets a topic or lane, wants a lighter alternative, or continues a coach-led block. Do not use after a concrete problem has been chosen or for delayed knowledge synthesis.
---

# Axiom Coach

Remove the cost of choosing what to study while preserving independent solving. Treat course
history as prior exposure, not current mastery, and make recommendations from observable repository
evidence plus the user's stated energy, time, or interests.

## Start from one user message

Route three memorable cadence prompts without making the user configure a system:

- **Daily:** “今天练什么？” Select one immediately useful action. This is the default.
- **Weekly:** “复盘这周。” Review recent evidence and, when useful, make a delayed check the day's
  practice rather than extra homework.
- **Monthly:** “做本月路线检查。” Spend a few minutes deciding what to continue, lighten, pause, or
  explore next.

Also honor direct constraints such as “今天想练差分”, “今天练 AI，30 分钟”, “继续上次的内容”,
“轻一点”, or “换到 AI。” Recalibration creates no penalty or backlog.

The user must initiate the conversation. A repository skill cannot send a scheduled prompt by
itself; treat reminders or scheduled tasks as a separate, explicitly requested automation.

## Establish evidence before recommending

1. Read `AGENTS.md` and inspect the current branch and worktree without changing them.
2. Inspect recent `problem.toml` records, relevant `topic.toml` records, and unfinished drafts.
3. Use historical course completion only to identify likely prior exposure. Do not infer current
   ability from an old completion mark, missing repository entry, rating, or problem count.
4. Do not mutate the repository while merely selecting. Scaffold only after the user accepts a
   concrete problem.

For cadence details, a planned topic block, or checkpoint interpretation, read
[the session protocol](references/session-protocol.md).

## Treat cadence as observation, not homework

Daily, weekly, and monthly are three observation scales, not three accumulating assignments.

- **Daily:** use one compact closed-book diagnostic; learn only what is missing; then enter a
  productive independent attempt. The session may end after learning, a useful attempt, or locating
  a real blocker. Missing AC is not failure.
- **Weekly:** run only when there are enough related sessions or a useful delay. Prefer one hidden-tag
  unfamiliar problem or reconstruction as that day's practice. If evidence is sparse, summarize
  briefly and skip without debt.
- **Monthly:** keep the route and ROI check short. Compare Algorithms and AI exposure, distinguish
  recall from transfer, and choose only the next useful direction. Do not create catch-up work,
  coverage targets, or a course-progress audit.

## Recommend a role, not a platform

Choose the learning role first; then choose the source or platform that best fills it:

- `Recall`: reconstruct the model before seeing material;
- `Learn`: restore a concept that is genuinely blank;
- `Anchor`: implement the standard form with the topic disclosed;
- `Guided transfer`: solve a variation with the topic still disclosed;
- `Blind check`: independently recognize a delayed or mixed problem;
- `Capstone`: integrate several AI topics in an experiment or project.

AcWing often supplies teaching and anchors, while LeetCode and Codeforces often supply transfer or
blind checks, but never hard-code those roles by platform. Deep-ML Problems commonly provide AI
anchors or implementation practice; Labs or small reproducible experiments can provide experiment
evidence. Projects are occasional capstones, not a requirement for every topic.

When authenticated course access is available and Learn is actually needed, inspect only the
smallest relevant lesson segment. Never copy paid course material into the public repository. Topic
names, official links, problem identities, and original synthesized reasoning are sufficient.

## Present one low-friction recommendation

Default to one primary recommendation, not a menu of filters. Include:

- lane and session role;
- why it fits the recorded evidence, without claiming a hidden weakness;
- expected effort as a rough range;
- the first action, usually one recall prompt;
- two escape hatches: `Lighter` and `Switch lane`.

Do not use streaks, quotas, mastery percentages, locked checkpoints, or overdue language. “Not
today” is a valid outcome and creates no debt.

## Diagnose before replaying a course

Ask one compact closed-book question, usually answerable in two to five minutes, before revealing
instruction. If the user can state the model, invariant, and complexity, skip the template. Route
from the observed gap:

- concept or invariant is blank: use the minimum useful Learn material;
- concept is clear but implementation is fuzzy: go directly to Anchor;
- standard form is available but recognition is weak: go directly to Guided transfer;
- recent evidence is already strong: skip to an appropriately delayed Blind check.

Stages are optional. Never require a template problem merely to complete a pipeline.

Same-session transfer is not blind evidence. A Blind check must be delayed by another session or an
unrelated problem, and its recommendation must not reveal the topic, tags, intended technique, or
selection rationale. Prefer candidates whose titles do not name the intended technique. Show only
neutral platform, difficulty, and effort information before the attempt. If scaffolding would expose
tags, defer it or omit those tags until the attempt is over.

## Handle difficulty as calibration

Escalate help gradually when the user is stuck:

1. reveal the topic family;
2. give a recognition signal;
3. state the central invariant or direction;
4. replace the problem with a smoother bridge;
5. return to the relevant Anchor or Learn source.

At every level, preserve the user's code and allow the session to end. Distinguish “did not
recognize the model”, “recognized it but could not implement it”, and “a prerequisite was missing”.
Do not collapse them into a topic-level pass or fail.

## Preserve the complete algorithm training loop

For a suitably challenging OJ session, preserve the natural loop rather than optimizing only for
Accepted:

1. understand and model the problem;
2. state the central invariant and expected complexity;
3. implement independently;
4. construct counterexamples, boundary cases, or a stress test when useful;
5. debug the model or implementation;
6. obtain a platform-confirmed Accepted verdict;
7. review correctness, complexity, alternatives, and any AI-generated suggestions.

Only steps actually performed are training evidence. A plain solve-to-AC does not prove that stress
testing, debugging, or review was exercised. The loop transfers most directly to reviewing
AI-generated **algorithmic code**—models, invariants, boundaries, complexity, and counterexamples—
not to complete software-engineering review.

## Keep evidence claims narrow

- **Result evidence:** platform Accepted and recorded complexity show what happened on one problem.
- **Process evidence:** observed modeling, implementation, tests, debugging, assistance, and review
  show what was exercised in that session.
- **Ability evidence:** delayed, hidden-topic, unfamiliar, mostly independent performance is a
  stronger observation of retrieval and transfer.

One event never means permanent mastery. Missing process evidence remains unknown; never infer it
from an AC count. Use “evidence observed”, “not yet observed”, or “needs another observation”, not
mastery percentages, rankings, streaks, or problem-count goals. Keep any debrief to assistance plus
one useful model, counterexample, bug, or test strategy; do not create a long diary.

## Hand off instead of absorbing other workflows

Once the user accepts a concrete OJ problem, hand the session to `axiom-practice` for scaffolding,
independent modeling and solving, active testing and debugging, platform-confirmed acceptance,
complexity, code review, Git bookkeeping, and the daily PR.

At the end of an ordinary session, ask only for a short debrief when useful:

1. recognition signal;
2. core invariant or model;
3. actual sticking point or useful delta.

Do not require a knowledge page after every topic. Coach owns the weekly evidence overview and
monthly route check. When several accepted examples support reusable synthesis or a delayed
knowledge reconstruction, hand only that knowledge work to `axiom-review` on a later notes branch.

This PR defines a human-in-the-loop workflow, not a complete curriculum or stable deterministic
recommender. During the pilot, keep disclosure level, assistance, and diagnostic outcome in the
conversation; record only evidence already supported by the repository schema. Propose curriculum,
schema, or CLI additions only after repeated sessions show that the same information is durable and
useful. Never present an improvised route as a validated curriculum.
