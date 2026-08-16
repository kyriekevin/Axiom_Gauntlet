<h1 align="center">Axiom Gauntlet</h1>

<p align="center">
  The algorithm proving ground of the <strong>Nightglass Protocol</strong> —
  judge-confirmed practice, distilled into a reusable bilingual knowledge wiki.
</p>

<p align="center">
  English · <a href="README_zh-CN.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/kyriekevin/Axiom_Gauntlet/actions/workflows/verify.yml"><img alt="Verify" src="https://github.com/kyriekevin/Axiom_Gauntlet/actions/workflows/verify.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/kyriekevin/Axiom_Gauntlet?style=flat-square"></a>
  <img alt="Managed by uv" src="https://img.shields.io/badge/managed%20by-uv-261230?style=flat-square">
</p>

> [!IMPORTANT]
> `problems/` records only verdicts confirmed by the online judge, never inferred from local
> tests. Reasoning shared by multiple problems graduates into `knowledge/` as a bilingual wiki.

## Recently completed

<!-- recent-problems:start -->

| Date | Problem | Platform | Language |
| --- | --- | --- | --- |
| 2026-08-16 | [最佳牛围栏](problems/acwing/102/) | AcWing | C++ |
| 2026-08-15 | [数的范围](problems/acwing/789/) | AcWing | C++ |
| 2026-08-15 | [数的三次方根](problems/acwing/790/) | AcWing | C++ |
| 2026-08-15 | [Books](problems/codeforces/279B/) | Codeforces | C++ |
| 2026-08-15 | [Reshape Matrix](problems/deep-ml/3/) | Deep-ML | Python |

<!-- recent-problems:end -->

## Coverage

![Practice coverage by platform, native difficulty, and language](assets/dashboards/practice-coverage.svg)

## Activity

The activity map counts recorded problem events from every supported platform rather than Git
commits.

![Total problem activity heatmap](assets/heatmaps/total.svg)

## How it works

```text
solve on an online judge
├── axiom new / accept ──────→ problems/<platform>/<id>/      problem.toml = evidence
├── axiom knowledge ─────────→ knowledge/<category>/<topic>/  topic.toml = reusable reasoning
├── axiom render ────────────→ README table, dashboards, heatmap
└── axiom knowledge render ──→ knowledge indexes
```

Every lifecycle transition goes through the `axiom` CLI. Generated tables, dashboards, and
indexes are never edited by hand.

## Daily practice

```bash
uv sync --locked --all-groups                 # once after cloning

git switch main
git pull --ff-only

# created on the day's first session, reused by every later one
git switch practice/YYYY-MM-DD 2>/dev/null \
  || git switch -c practice/YYYY-MM-DD

uv run axiom new codeforces 118A \
  --title "String Task" --url <problem-url> --language cpp
#   ↑ scaffolds the entry and a solution stub; solving and submitting are yours

# only once the judge returns Accepted:
uv run axiom accept codeforces 118A \
  --language cpp --time-complexity "O(n)" --space-complexity "O(n)"

make verify                                   # full gate before the pull request
```

Practice lands through a daily pull request; delayed knowledge synthesis uses a short-lived
`notes/YYYY-MM-DD` branch. The full contract lives in [AGENTS.md](AGENTS.md).

## Documentation

| Guide | Covers |
|---|---|
| [Schema](docs/SCHEMA.md) | `problem.toml` and `topic.toml` contracts and generated outputs |
| [Style guide](docs/STYLE_GUIDE.md) | Writing and reviewing knowledge notes |
| [Knowledge architecture](docs/KNOWLEDGE_ARCHITECTURE.md) | Why problem evidence and reusable knowledge are separated |
| [Knowledge index](knowledge/INDEX.md) | The distilled topics themselves |

## License

MIT — see [LICENSE](LICENSE).
