# 知识笔记架构提案

[English](KNOWLEDGE_ARCHITECTURE.md) | [简体中文](KNOWLEDGE_ARCHITECTURE_zh-CN.md)

> 状态：基础架构已采用；具体知识内容通过独立 notes 分支补充。

## 问题

当前结构把三类内容放进了每道题的 README：

- 题目事实：来源、状态、Accepted 语言和实现；
- 可复用知识：建模、递归、记忆化搜索、DP、证明和优化；
- 学习证据：首次解题、文档整理和后续复习。

当 486 和 877 共享同一个区间博弈模型时，逐题写完整笔记会重复相同推导；一次按知识点进行的复盘，也会被误表示成多道题各自的一次文档活动。

## 目标模型

仓库应把题目档案与知识笔记分开：

```text
problems/<platform>/<id>/
├── problem.toml
├── solution.py
└── README.md / README_zh-CN.md   # 轻量题目卡片或生成入口

knowledge/
├── INDEX.md / INDEX_zh-CN.md     # 生成的知识目录
├── LOG.md                        # 追加式维护记录
└── dynamic-programming/
    ├── README.md / README_zh-CN.md
    ├── memoization/
    └── interval-dp/
        ├── topic.toml            # 身份、例题、依赖与活动
        ├── README.md
        ├── README_zh-CN.md
        └── assets/               # 真正服务于该知识点的图解
```

### 题目层

题目层负责保存不可替代的事实：

- 平台身份、难度和标签；
- 平台确认的 AC 事件；
- 原样保留的 Accepted 代码；
- 该实现的时间与空间复杂度；
- 只有这道题才有的边界条件或差异。

题目 README 不再承担完整教程。它可以保留为便于 GitHub 浏览的轻量卡片，并从知识区反向生成关联链接。

### 知识层

知识层采用“稳定目录树 + 页面交叉链接”，而不是一开始创建许多扁平 topic。目录树参考 OI Wiki 的学科分类，保证动态规划、图论、数据结构等主干可以逐步扩展；页面之间的索引、反向链接和维护日志参考 LLM Wiki，避免目录树把相关知识割裂。

486 和 877 的规范归属应是 `dynamic-programming/interval-dp`，而不是一个顶层 `interval-game-dp`。区间 DP 页面可以区分两类常见转移：

- 分割合并：枚举分割点 `k`，组合两个子区间；
- 区间收缩：从端点做选择，转移到 `[i + 1, j]` 或 `[i, j - 1]`。

这两道题属于第二类中的零和博弈例子。该章节的推导顺序是：

1. 如何把“两端取数、双方最优”抽象成零和博弈；
2. 如何定义递归状态与选择；
3. 如何写成记忆化搜索；
4. 如何根据依赖顺序转成自底向上的区间 DP；
5. 如何压缩空间；
6. 何时检查奇偶性等数学特征，使通用 DP 退化为更强结论。

题目只是章节中的例子，并明确各自角色：486 展示通用模型与平局条件，877 展示相同模型以及约束带来的数学捷径。记忆化搜索本身是可跨多类 DP 复用的知识，应有独立页面；区间 DP 只链接并展示它在当前状态图上的应用，不重复讲完整基础。

### 来源、Wiki 与 Schema

Karpathy 的 LLM Wiki 模式可以映射到本仓库：

- 来源层：`problems/` 中的平台事实、Accepted 代码和活动，以及明确引用的外部资料；
- Wiki 层：`knowledge/` 中由复盘对话持续综合、交叉链接的知识页面；
- Schema 层：仓库文档、validator 和复盘 Skill，定义页面粒度、维护流程与质量门禁。

`INDEX` 是按内容组织的入口，`LOG` 是按时间追加的维护记录。定期 lint 应检查孤立页面、失效链接、重复主题和缺少反向链接，而不仅是 Markdown 格式。

## 单一事实来源

知识主题可以使用轻量 `topic.toml`：

```toml
version = 1
path = "dynamic-programming/interval-dp"
title = "Interval DP"
title_zh_cn = "区间动态规划"
tags = ["dynamic-programming", "interval"]
links = ["dynamic-programming/memoization", "mathematics/game-theory"]

[[examples]]
uid = "leetcode:0486"
role = "endpoint-game-general-model"

[[examples]]
uid = "leetcode:0877"
role = "constraint-shortcut"

[[activity]]
type = "review"
date = 2026-08-02
result = "pass"
```

例题关系只在 `topic.toml` 中维护，避免在两边重复维护链接。当前由生成的知识索引提供统一入口，未来可以继续根据同一份数据生成题目到知识点的反向链接。新页面必须先查 `INDEX` 和相邻页面；只有当一个小节拥有独立定义、被多个页面复用，或形成了自己的复习问题与例题集合时，才拆成子页面。

## 生命周期与活动

长期方向是拆开两种生命周期：

- 题目：`draft -> accepted`；
- 知识主题：从草稿整理为可复习的知识笔记，并独立记录 `note` 与 `review`。

这样，一次区间 DP 复盘只记为一次知识复盘，不会因为包含两道例题而生成两次 note。现有题目级 `documented` 状态先保留兼容，不在第一次迁移中直接删除。

## 工作流与 Skill 边界

- `axiom-practice` 负责每日解题：建题、渐进提示、AC 确认、代码 Review、复杂度和题目特有差异。
- 新的复盘 Skill 负责周期性知识整理：从多道题抽象共同模型、检查迁移能力、维护知识主题和生成必要图解。
- `practice/YYYY-MM-DD` 只提交题目证据；`notes/YYYY-MM-DD` 更新一个或多个知识主题。

视觉资产应归属于规范知识页面，而不是复制到每道题。对于两端博弈，图解应表现“建模 → 递归 → 记忆化搜索 → 区间 DP → 数学特例”的推导路径；等区间 DP 页面结构确定后再使用 ImageGen 制作。

## 分支与交付边界

- `codex/knowledge-notes-architecture` 只整理仓库地基：本架构契约、problem 轻量化方案、knowledge schema、validator/CLI/template，以及 practice/review Skill 的职责。它不写 486/877 的正式知识内容，也不记录本次复盘活动。
- 架构分支合并后，`notes/YYYY-MM-DD` 才创建或更新知识页面、加入例题、生成图解并记录真实复盘。

这条边界让基础设施 PR 可以只讨论契约与确定性工具，让 notes PR 只讨论知识是否准确、系统且能够帮助回忆。

## 已采用的决策

- 长期内容放在 `knowledge/`；短期复盘分支命名为 `notes/YYYY-MM-DD`。
- 题目 README 保留为轻量来源卡片。
- Accepted 解答复杂度写入 `problem.toml`。
- `axiom-practice` 与 `axiom-review` 分别负责日常练习和延迟复盘。
- 知识活动使用独立生成的日志，不增加题目 AC 热力图计数。

## 参考模式

- [Karpathy 的 LLM Wiki 架构](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [OI Wiki 的动态规划目录](https://oi-wiki.org/dp/)
- [OI Wiki：记忆化搜索](https://oi-wiki.org/dp/memo/)
- [OI Wiki：区间 DP](https://oi-wiki.org/dp/interval/)
