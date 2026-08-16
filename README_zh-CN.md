<h1 align="center">Axiom Gauntlet</h1>

<p align="center">
  <strong>Nightglass Protocol</strong> 的算法试炼场 ——
  经在线评测确认的练习，沉淀为可复用的双语知识 wiki。
</p>

<p align="center">
  <a href="README.md">English</a> · 简体中文
</p>

<p align="center">
  <a href="https://github.com/kyriekevin/Axiom_Gauntlet/actions/workflows/verify.yml"><img alt="Verify" src="https://github.com/kyriekevin/Axiom_Gauntlet/actions/workflows/verify.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/kyriekevin/Axiom_Gauntlet?style=flat-square"></a>
  <img alt="Managed by uv" src="https://img.shields.io/badge/managed%20by-uv-261230?style=flat-square">
</p>

> [!IMPORTANT]
> `problems/` 只记录在线评测平台确认的判定，绝不由本地测试推断。多道题共享的推理
> 沉淀到 `knowledge/`，形成双语知识 wiki。

## 最近完成

<!-- recent-problems:start -->

| 日期 | 题目 | 平台 | 语言 |
| --- | --- | --- | --- |
| 2026-08-16 | [最佳牛围栏](problems/acwing/102/) | AcWing | C++ |
| 2026-08-16 | [Number of Ways](problems/codeforces/466C/) | Codeforces | C++ |
| 2026-08-16 | [Calculate the Mean by Row or Column](problems/deep-ml/4/) | Deep-ML | Python |
| 2026-08-16 | [Scalar Multiplication of a Matrix](problems/deep-ml/5/) | Deep-ML | Python |
| 2026-08-15 | [数的范围](problems/acwing/789/) | AcWing | C++ |

<!-- recent-problems:end -->

## 覆盖情况

![按平台、原生难度和语言统计的练习覆盖](assets/dashboards/practice-coverage.svg)

## 活动

活动热力图统计所有已支持平台记录的题目事件，而不是 Git commit。

![总计题目活动热力图](assets/heatmaps/total.svg)

## 工作原理

```text
在在线评测平台解题
├── axiom new / accept ──────→ problems/<平台>/<题号>/        problem.toml = 证据
├── axiom knowledge ─────────→ knowledge/<类别>/<主题>/       topic.toml = 可复用推理
├── axiom render ────────────→ README 表格、面板、热力图
└── axiom knowledge render ──→ 知识索引
```

所有生命周期状态变更都经由 `axiom` CLI 完成；生成的表格、面板与索引一律不手工编辑。

## 每日练习

```bash
uv sync --locked --all-groups                 # 克隆后执行一次

git switch main
git pull --ff-only

# 当天首次新建，之后每次自动复用
git switch practice/YYYY-MM-DD 2>/dev/null \
  || git switch -c practice/YYYY-MM-DD

uv run axiom new codeforces 118A \
  --title "String Task" --url <题目链接> --language cpp
#   ↑ 只生成条目和代码骨架；解题与提交由你自己完成

# 只有平台返回 Accepted 之后：
uv run axiom accept codeforces 118A \
  --language cpp --time-complexity "O(n)" --space-complexity "O(n)"

make verify                                   # 提 PR 前的完整校验
```

练习通过每日 PR 合入；延迟的知识沉淀走临时的 `notes/YYYY-MM-DD` 分支。完整约定见
[AGENTS.md](AGENTS.md)。

## 文档导航

| 指南 | 内容 |
|---|---|
| [Schema](docs/SCHEMA_zh-CN.md) | `problem.toml` 与 `topic.toml` 契约及生成产物 |
| [写作规范](docs/STYLE_GUIDE_zh-CN.md) | 知识笔记的撰写与复习 |
| [知识架构](docs/KNOWLEDGE_ARCHITECTURE_zh-CN.md) | 题目证据与可复用知识为何分离 |
| [知识索引](knowledge/INDEX_zh-CN.md) | 已沉淀的主题本身 |

## License

MIT —— 见 [LICENSE](LICENSE)。
