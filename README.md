# Axiom Gauntlet

[English](README.md) | [简体中文](README_zh-CN.md)

> The algorithm proving ground of the **Nightglass Protocol**.

Axiom Gauntlet is where I practice algorithms and make that growth visible. It is the first proving
ground of the Nightglass Protocol.

I solve problems here, reflect on them, and return to challenge myself again. An Accepted verdict
marks one battle; what I want to build over time is the ability to face unfamiliar problems, find a
path through them, and turn that reasoning into working code.

## Current Build

The first scaffold provides:

- structured problem entries with English and Simplified Chinese notes;
- repository validation and deterministic activity heatmaps;
- a small `axiom` CLI for creating, validating, and rendering entries;
- tests and CI checks for every pull request.

Create a draft entry:

```bash
uv sync --locked --all-groups
uv run axiom new leetcode 1 \
  --title "Two Sum" \
  --url "https://leetcode.com/problems/two-sum/" \
  --difficulty easy \
  --language cpp
```

After the online judge explicitly confirms acceptance, record the result. Complete both language
notes before advancing the entry to `documented`:

```bash
uv run axiom accept leetcode 1 --language cpp --date 2026-08-01
uv run axiom document leetcode 1 --date 2026-08-01
```

The repo-local `axiom-practice` skill provides the conversational workflow around these commands:
spoiler-controlled help, acceptance confirmation, code review, and bilingual note writing.

See the [problem schema](docs/SCHEMA.md) and [note style guide](docs/STYLE_GUIDE.md) for the current
repository contracts. Run the complete local gate with `make verify`.

## Activity

Activity maps are generated from recorded problem events rather than Git commit counts.

![LeetCode activity heatmap](assets/heatmaps/leetcode.svg)

![AcWing activity heatmap](assets/heatmaps/acwing.svg)

![Codeforces activity heatmap](assets/heatmaps/codeforces.svg)

## Continuous Integration

Pull requests run the complete verification gate. A separate workflow validates source data and
refreshes checked-in activity maps after relevant changes on `main` and on a daily schedule.
