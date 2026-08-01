# Problem schema

[English](SCHEMA.md) | [简体中文](SCHEMA_zh-CN.md)

`problem.toml` is the machine-readable source of truth. `README.md`, solution
files, translated notes, and heatmaps must agree with it; generators should
never infer identity from a title.

## Directory identity

Every problem lives at:

```text
problems/<platform>/<canonical-id>/
├── problem.toml
├── README.md
└── README_zh-CN.md
```

Supported platforms and canonical IDs are:

| Platform | `problem_id` in TOML | Canonical directory ID | Example UID |
| --- | --- | --- | --- |
| LeetCode | Positive integer without leading zeroes | At least four digits, zero-padded | `leetcode:0001` |
| AcWing | Positive integer without leading zeroes | Same integer | `acwing:785` |
| Codeforces | Contest number plus uppercase index | No leading contest zeroes | `codeforces:4A` |

Thus input `leetcode/1`, `acwing/0785`, and `codeforces/004a` become paths
`leetcode/0001`, `acwing/785`, and `codeforces/4A`. Titles and difficulty do not
belong in paths because both can change.

## TOML fields

```toml
version = 1
uid = "codeforces:4A"
platform = "codeforces"
problem_id = "4A"
title = "Watermelon"
url = "https://codeforces.com/problemset/problem/4/A"
state = "documented"
tags = ["math"]

[difficulty]
scheme = "rating"
value = 800
normalized = "easy"

[[solutions]]
file = "solution.cpp"
language = "cpp"

[[activity]]
type = "ac"
date = 2026-08-01
language = "cpp"

[[activity]]
type = "note"
date = 2026-08-01

[[activity]]
type = "review"
date = 2026-08-08
language = "cpp"
result = "pass"
```

Required top-level fields are `version`, `uid`, `platform`, `problem_id`,
`title`, `url`, `state`, `tags`, and `[difficulty]`. `[[solutions]]` and
`[[activity]]` may be absent while a problem is a draft.

- `version` is currently `1`.
- `platform` is `leetcode`, `acwing`, or `codeforces`.
- `uid` is `<platform>:<canonical-id>`.
- `tags` are unique lowercase kebab-case values.
- `difficulty.scheme` is `level`, `rating`, or `unknown`.
- `difficulty.value` preserves the platform value, such as `"Easy"` or `800`.
- `difficulty.normalized` is `easy`, `medium`, `hard`, or `unknown`; it is only
  a display/filtering aid, not a claim that platform scales are equivalent.

## Solutions and activity

One problem may contain any combination of:

| Language | Metadata value | File |
| --- | --- | --- |
| C++ | `cpp` | `solution.cpp` |
| Python | `python` | `solution.py` |
| Go | `go` | `solution.go` |

The `py` spelling is accepted by the scaffold CLI as an input alias, but TOML
always stores `python`. Every listed file must exist in the problem directory.

An activity `type` is `ac`, `note`, or `review`. AC events require a canonical
`language` matching a listed solution. A `note` records a day on which the
explanation materially changed. Review events require `result = "pass"` or
`result = "fail"`. Dates use the unquoted TOML local-date form
`YYYY-MM-DD`; quoted ISO dates are also accepted by the loader.

## State machine

```text
draft -> accepted -> documented
```

- `draft`: work may be incomplete. Scaffolded solution files are placeholders,
  and there must not yet be an AC event.
- `accepted`: requires at least one AC event and at least one existing,
  non-placeholder file listed in `[[solutions]]`.
- `documented`: has the same AC/code requirements as `accepted`, requires a
  `note` activity event, and both language versions of its note must complete
  their required reasoning, correctness, complexity, pitfalls, and review sections.

`Visualization` is deliberately optional. The template includes stable diagram
markers so a future skill can insert Mermaid or a checked-in asset without making
every small problem generate decorative artwork.

Review events do not create a fourth terminal state. A failed later review is
valuable learning history and does not erase the fact that the problem was
previously accepted and documented.
