---
name: axiom-coach
description: Select and calibrate the next Algorithms or AI learning session from Axiom evidence. Use when the user asks what to practice today, targets a topic or lane, wants a lighter alternative, or continues a coach-led learning block. Do not use after a concrete problem has been chosen or for delayed knowledge synthesis.
---

# Axiom Coach

Remove the cost of choosing what to study while preserving independent solving. Treat course
history as prior exposure, not current mastery, and make recommendations from observable repository
evidence plus the user's stated energy, time, or interests.

## Start from one user message

Support three entry modes without making the user configure a session:

- **Coach-led:** “今天练什么？” Select one primary session. This is the default.
- **Targeted:** “今天想练差分” or “今天练 AI，30 分钟。” Honor the lane, topic, or time box.
- **Continue or adjust:** “继续上次的内容”, “轻一点”, or “换到 AI。” Preserve useful context and
  recalibrate without penalty.

The user must initiate the conversation. A repository skill cannot send a scheduled prompt by
itself; treat reminders or scheduled tasks as a separate, explicitly requested automation.

## Establish evidence before recommending

1. Read `AGENTS.md` and inspect the current branch and worktree without changing them.
2. Inspect recent `problem.toml` records, relevant `topic.toml` records, and unfinished drafts.
3. Use historical course completion only to identify likely prior exposure. Do not infer current
   ability from an old completion mark, missing repository entry, rating, or problem count.
4. Do not mutate the repository while merely selecting. Scaffold only after the user accepts a
   concrete problem.

For a planned topic block or checkpoint evaluation, read
[the session protocol](references/session-protocol.md).

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

Ask one compact closed-book question before revealing instruction. Route from the observed gap:

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

## Hand off instead of absorbing other workflows

Once the user accepts and scaffolds a concrete OJ problem, hand the session to `axiom-practice` for
independent solving, platform-confirmed acceptance, complexity, Git bookkeeping, and the daily PR.

At the end of an ordinary session, ask only for a short debrief when useful:

1. recognition signal;
2. core invariant or model;
3. actual sticking point or useful delta.

Do not require a knowledge page after every topic. When several examples support a reusable model
and a delayed reconstruction is worthwhile, hand it to `axiom-review` on a later notes branch.

During the pilot, keep disclosure level, assistance, and diagnostic outcome in the conversation;
record only evidence already supported by the repository schema. Propose schema or CLI additions
only after repeated mock sessions show that the same information is durable and useful.
