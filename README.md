# Axiom Gauntlet

[English](README.md) | [简体中文](README_zh-CN.md)

> The algorithm proving ground of the **Nightglass Protocol**.

Axiom Gauntlet separates daily solving evidence from reusable algorithm knowledge. Accepted code
and judge-confirmed results live under `problems/`; delayed review turns shared reasoning into a
bilingual wiki under `knowledge/`.

## Workflow

Create a draft without copying the full problem statement:

```bash
uv sync --locked --all-groups
uv run axiom new leetcode 1 \
  --title "Two Sum" \
  --url "https://leetcode.com/problems/two-sum/" \
  --difficulty easy \
  --language cpp
```

Only after the online judge explicitly confirms Accepted, record the exact accepted language and
its complexity:

```bash
uv run axiom accept leetcode 1 \
  --language cpp \
  --date 2026-08-01 \
  --time-complexity "O(n)" \
  --space-complexity "O(n)"
```

During delayed review, group related problems into a canonical knowledge topic rather than writing
the same tutorial beside each problem:

```bash
uv run axiom knowledge new dynamic-programming/interval-dp \
  --title "Interval DP" \
  --title-zh-cn "区间动态规划" \
  --tag dynamic-programming
```

Complete the generated English and Simplified Chinese topic notes, then record and render them:

```bash
uv run axiom knowledge document dynamic-programming/interval-dp --date 2026-08-02
uv run axiom knowledge render
```

`axiom-practice` guides daily solving, AC recording, complexity, and code review.
`axiom-review` guides weekly synthesis, knowledge-page maintenance, and purposeful visuals.

See the [problem and knowledge schema](docs/SCHEMA.md),
[knowledge architecture](docs/KNOWLEDGE_ARCHITECTURE.md), and
[knowledge-note style guide](docs/STYLE_GUIDE.md). Run the complete local gate with `make verify`.

## Activity

Problem activity maps are generated from recorded problem events rather than Git commit counts.
Knowledge maintenance has its own generated [`LOG.md`](knowledge/LOG.md).

![LeetCode activity heatmap](assets/heatmaps/leetcode.svg)

![AcWing activity heatmap](assets/heatmaps/acwing.svg)

![Codeforces activity heatmap](assets/heatmaps/codeforces.svg)

## Continuous Integration

Pull requests run the complete verification gate. Generated heatmaps and knowledge indexes are
checked for freshness.
