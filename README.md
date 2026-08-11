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
| 2026-08-09 | [String Task](problems/codeforces/118A/) | Codeforces | Python |
| 2026-08-09 | [Transpose of a Matrix](problems/deep-ml/2/) | Deep-ML | Python |
| 2026-08-08 | [归并排序](problems/acwing/787/) | AcWing | C++ |
| 2026-08-08 | [Way Too Long Words](problems/codeforces/71A/) | Codeforces | C++ |
| 2026-08-08 | [Matrix times Vector](problems/deep-ml/1/) | Deep-ML | Python |

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
├── axiom new / accept ──→ problems/<platform>/<id>/        problem.toml = evidence
├── axiom knowledge ─────→ knowledge/<category>/<topic>/    topic.toml = reusable reasoning
└── axiom render ────────→ README table, dashboards, heatmap, and indexes
```

Every lifecycle transition goes through the `axiom` CLI. Generated tables, dashboards, and
indexes are never edited by hand.

## Daily practice

```bash
uv sync --locked --all-groups        # once after cloning
git pull --ff-only                   # start the day on a clean main
git switch -c practice/YYYY-MM-DD    # create or reuse the Asia/Shanghai daily branch
uv run axiom new ...                 # scaffold, solve, submit
uv run axiom accept ...              # record the judge-confirmed verdict
make verify                          # full gate before the pull request
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
