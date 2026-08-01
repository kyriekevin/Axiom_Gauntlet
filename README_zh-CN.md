# Axiom Gauntlet

[English](README.md) | [简体中文](README_zh-CN.md)

> **Nightglass Protocol** 的算法试炼场。

Axiom Gauntlet 是我练习算法、看见自己成长的地方，也是 Nightglass Protocol 的第一座试炼场。

我会在这里做题、复盘，也会在以后回来重新挑战自己。一次 Accepted 代表赢下了一场战斗；真正
想积累的，是面对陌生问题时找到突破口、理清思路，并把它写成正确代码的能力。

## 当前版本

第一版脚手架已经提供：

- 使用独立中英文笔记的结构化题目目录；
- 仓库校验与可重复生成的活动热力图；
- 用于创建、校验和渲染题目记录的轻量 `axiom` CLI；
- 在每个 Pull Request 上运行的测试和 CI 检查。

创建一道草稿题目：

```bash
uv sync --locked --all-groups
uv run axiom new leetcode 1 \
  --title "Two Sum" \
  --url "https://leetcode.com/problems/two-sum/" \
  --difficulty easy \
  --language cpp
```

当前仓库契约见[题目 Schema](docs/SCHEMA_zh-CN.md)与[题解写作规范](docs/STYLE_GUIDE_zh-CN.md)。
使用 `make verify` 运行完整的本地门禁。

## 活动

活动热力图根据题目中记录的事件生成，而不是统计 Git commit 数量。

![LeetCode 活动热力图](assets/heatmaps/leetcode.svg)

![AcWing 活动热力图](assets/heatmaps/acwing.svg)

![Codeforces 活动热力图](assets/heatmaps/codeforces.svg)

## 持续集成

Pull Request 会运行完整验证门禁。另一条工作流会在 `main` 的相关内容变化后以及每日定时运行，
校验源数据并刷新提交到仓库中的活动热力图。
