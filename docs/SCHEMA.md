# Repository Schema

[English](SCHEMA.md) | [简体中文](SCHEMA_zh-CN.md)

The repository has two machine-readable sources of truth: `problem.toml` records solving evidence;
`topic.toml` records reusable knowledge. Generated README activity, the heatmap, and knowledge
indexes must agree with them.

## Problem records

Each problem lives at `problems/<platform>/<canonical-id>/`. The platform registry in
[`platforms.toml`](../src/axiom_gauntlet/platforms.toml) defines the display label, ID strategy,
optional canonical padding, and default difficulty scheme. Platform directories are created lazily
by `axiom new`; an unused registered platform needs no empty directory.

The registry supports positive-integer IDs, contest-number-plus-index IDs, and filesystem-safe slug
IDs. Adding a platform that fits one of these strategies is a data-only registry change. A new ID
strategy requires tooling and test changes. The stable UID is `<platform>:<canonical-id>` (for
example, `deep-ml:1`).

```toml
version = 1
uid = "leetcode:0001"
platform = "leetcode"
problem_id = "1"
title = "Two Sum"
url = "https://leetcode.com/problems/two-sum/"
state = "accepted"
tags = ["array", "hash-table"]

[difficulty]
scheme = "level"
value = "Easy"
normalized = "easy"

[[solutions]]
file = "solution.py"
language = "python"
time_complexity = "O(n)"
space_complexity = "O(n)"

[[activity]]
type = "ac"
date = 2026-08-01
language = "python"
reflection = "Recheck the lookup-before-insert invariant."
```

Supported solution metadata values are `cpp`, `python`, and `go`, mapped to `solution.cpp`,
`solution.py`, and `solution.go`. Every accepted language requires an existing non-placeholder file
and both complexity fields. An AC event is recorded only after platform confirmation.
An optional `reflection` preserves a concise problem-specific observation without expanding the
lightweight problem card into a full tutorial.

The active lifecycle is `draft -> accepted`. `documented`, problem-level `note`, and problem-level
`review` remain readable for compatibility with earlier entries, but new reusable documentation and
reviews belong to knowledge topics. Problem READMEs are lightweight source cards rather than full
tutorials.

## Knowledge topics

Every topic lives at `knowledge/<category>/<topic>/`; the path has at least two lowercase kebab-case
parts. `topic.toml` is authoritative:

```toml
version = 1
path = "dynamic-programming/interval-dp"
title = "Interval DP"
title_zh_cn = "区间动态规划"
state = "documented"
tags = ["dynamic-programming", "interval"]
links = ["dynamic-programming/memoization"]

[[examples]]
uid = "leetcode:0486"
role = "endpoint-game-general-model"

[[activity]]
type = "note"
date = 2026-08-02

[[activity]]
type = "review"
date = 2026-08-09
result = "pass"
```

`links` must resolve to existing topic paths and example UIDs must resolve to existing problems.
Tags are unique lowercase kebab-case values. Topic states are `draft` and `documented`; documenting
requires complete semantically aligned English and Simplified Chinese notes. Later reviews use
`result = "pass"` or `result = "fail"` and do not erase earlier evidence.

Use the CLI rather than editing lifecycle fields by hand:

```bash
uv run axiom knowledge new <category/topic> --title "..." --title-zh-cn "..."
uv run axiom knowledge document <category/topic> --date <YYYY-MM-DD>
uv run axiom knowledge review <category/topic> --date <YYYY-MM-DD> --result <pass|fail>
uv run axiom knowledge render
```

`knowledge/INDEX.md`, `INDEX_zh-CN.md`, and `LOG.md` are generated files.
