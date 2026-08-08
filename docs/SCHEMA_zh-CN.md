# 仓库 Schema

[English](SCHEMA.md) | [简体中文](SCHEMA_zh-CN.md)

仓库有两类机器可读事实来源：`problem.toml` 记录解题证据，`topic.toml` 记录可复用知识。
README 活动区、覆盖看板、热力图与知识索引均由它们生成并保持一致。

## 题目记录

每道题位于 `problems/<platform>/<canonical-id>/`。[`platforms.toml`](../src/axiom_gauntlet/platforms.toml)
平台注册表定义展示名称、题号策略、可选规范宽度与默认难度体系。`axiom new` 会按需创建平台
目录，尚未使用的已注册平台不需要保留空目录。

注册表支持正整数题号、比赛编号加题号，以及文件系统安全的 slug 三种策略。符合已有策略的
新平台只需增加一段注册表数据；只有全新题号规则才需要修改工具和测试。稳定 UID 为
`<platform>:<canonical-id>`（例如 `deep-ml:1`）。

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
reflection = "复查先查询后插入的不变量。"
```

解答语言元数据支持 `cpp`、`python` 和 `go`，分别对应 `solution.cpp`、`solution.py` 和
`solution.go`。每个 Accepted 语言都必须有非占位代码，以及时间和辅助空间复杂度。AC 事件只能
在平台确认后记录。
可选的 `reflection` 用于保留简短的题目特有观察，而不把轻量题目卡重新扩展成完整题解。

当前主生命周期为 `draft -> accepted`。题目级 `documented`、`note` 与 `review` 为旧记录保留
兼容；新的可复用文档和复习活动属于知识主题。题目 README 只作为轻量来源卡片，不再承担完整
教程。

## 知识主题

每个主题位于 `knowledge/<category>/<topic>/`，路径至少包含两段小写 kebab-case。
`topic.toml` 是唯一事实来源：

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

`links` 必须指向已有主题，例题 UID 必须指向已有题目；标签是不重复的小写 kebab-case。主题
状态为 `draft` 或 `documented`，只有中英文笔记都完整时才能记录 document。后续复习使用
`result = "pass"` 或 `result = "fail"`，且不会抹掉已有历史。

生命周期字段通过 CLI 更新，不手改：

```bash
uv run axiom knowledge new <category/topic> --title "..." --title-zh-cn "..."
uv run axiom knowledge document <category/topic> --date <YYYY-MM-DD>
uv run axiom knowledge review <category/topic> --date <YYYY-MM-DD> --result <pass|fail>
uv run axiom knowledge render
```

`knowledge/INDEX.md`、`INDEX_zh-CN.md` 和 `LOG.md` 都是生成文件。
