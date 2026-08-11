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
| 2026-08-09 | [String Task](problems/codeforces/118A/) | Codeforces | Python |
| 2026-08-09 | [Transpose of a Matrix](problems/deep-ml/2/) | Deep-ML | Python |
| 2026-08-08 | [归并排序](problems/acwing/787/) | AcWing | C++ |
| 2026-08-08 | [Way Too Long Words](problems/codeforces/71A/) | Codeforces | C++ |
| 2026-08-08 | [Matrix times Vector](problems/deep-ml/1/) | Deep-ML | Python |

<!-- recent-problems:end -->

## 覆盖情况

![按平台、原生难度和语言统计的练习覆盖](assets/dashboards/practice-coverage.svg)

## 活动

活动热力图统计所有已支持平台记录的题目事件，而不是 Git commit。

![总计题目活动热力图](assets/heatmaps/total.svg)

## 工作原理

```text
在在线评测平台解题
├── axiom new / accept ──→ problems/<平台>/<题号>/         problem.toml = 证据
├── axiom knowledge ─────→ knowledge/<类别>/<主题>/        topic.toml = 可复用推理
└── axiom render ────────→ README 表格、面板、热力图与索引
```

所有生命周期状态变更都经由 `axiom` CLI 完成；生成的表格、面板与索引一律不手工编辑。

## 每日练习

```bash
uv sync --locked --all-groups        # 克隆后执行一次
git pull --ff-only                   # 从干净的 main 开始新的一天
git switch -c practice/YYYY-MM-DD    # 创建或复用 Asia/Shanghai 当日分支
uv run axiom new ...                 # 建题、解题、提交
uv run axiom accept ...              # 记录平台确认的判定
make verify                          # 提 PR 前的完整校验
```

练习通过每日 PR 合入；延迟的知识沉淀走短生命周期的 `notes/YYYY-MM-DD` 分支。完整约定见
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
