# 题目 Schema

[English](SCHEMA.md) | [简体中文](SCHEMA_zh-CN.md)

`problem.toml` 是机器可读的唯一事实来源。中英文笔记、解答文件和热力图都必须与它保持一致；
生成器不能根据题目标题推断身份。

## 目录身份

每道题存放在：

```text
problems/<platform>/<canonical-id>/
├── problem.toml
├── README.md
└── README_zh-CN.md
```

当前支持的平台与规范 ID 如下：

| 平台 | TOML 中的 `problem_id` | 目录 ID | UID 示例 |
| --- | --- | --- | --- |
| LeetCode | 不带前导零的正整数 | 至少四位，不足补零 | `leetcode:0001` |
| AcWing | 不带前导零的正整数 | 与题号相同 | `acwing:785` |
| Codeforces | 比赛编号加大写题号 | 比赛编号不带前导零 | `codeforces:4A` |

例如，输入 `leetcode/1`、`acwing/0785` 和 `codeforces/004a`，会分别得到
`leetcode/0001`、`acwing/785` 和 `codeforces/4A`。标题和难度可能变化，因此不进入路径。

## TOML 字段

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

必填顶层字段为 `version`、`uid`、`platform`、`problem_id`、`title`、`url`、
`state`、`tags` 和 `[difficulty]`。草稿阶段可以没有 `[[solutions]]` 和
`[[activity]]`。

- `version` 当前为 `1`。
- `platform` 当前可以是 `leetcode`、`acwing` 或 `codeforces`。
- `uid` 格式为 `<platform>:<canonical-id>`。
- `tags` 使用不重复的小写 kebab-case。
- `difficulty.scheme` 为 `level`、`rating` 或 `unknown`。
- `difficulty.value` 保留平台原始值，例如 `"Easy"` 或 `800`。
- `difficulty.normalized` 为 `easy`、`medium`、`hard` 或 `unknown`，只用于展示和筛选，
  不表示不同平台的难度可以直接等价。

## 解答与活动

一道题可以包含下列任意语言组合：

| 语言 | 元数据值 | 文件 |
| --- | --- | --- |
| C++ | `cpp` | `solution.cpp` |
| Python | `python` | `solution.py` |
| Go | `go` | `solution.go` |

CLI 接受 `py` 作为输入别名，但 TOML 始终写入 `python`。元数据列出的文件必须真实存在。

活动 `type` 可以是 `ac`、`note` 或 `review`。AC 事件必须包含与已列出解答匹配的规范语言；
`note` 表示题解发生了实质更新；`review` 必须记录 `result = "pass"` 或
`result = "fail"`。日期使用 `YYYY-MM-DD`。

## 状态机

```text
draft -> accepted -> documented
```

- `draft`：内容可以不完整，不能存在 AC 事件。
- `accepted`：必须至少有一个 AC 事件，以及一份存在且不是占位内容的解答文件。
- `documented`：满足 accepted 的全部条件，另有 `note` 事件，并完成中英文两份题解的核心
  洞察、思路、正确性、复杂度、易错点和复习记录。

图解是可选的。复习不会产生新的终态；失败的复习是有价值的学习历史，也不会抹掉过去已经
Accepted 和完成笔记的事实。
