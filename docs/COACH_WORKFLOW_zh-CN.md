# Axiom Coach 工作流

[English](COACH_WORKFLOW.md) | [简体中文](COACH_WORKFLOW_zh-CN.md)

Axiom Coach 负责选择下一次有价值的算法或 AI 练习，但不会把练习变成连续打卡、配额或固定
课程重播。

## 三句入口与直接覆盖

```text
今天练什么？
复盘这周。
做本月路线检查。
```

你也可以显式调用 `$axiom-coach`，或用一句话覆盖默认推荐：

```text
今天想恢复差分。
今天练 AI，控制在 30 分钟左右。
继续上次的知识点。
今天轻一点。
```

Coach 每次只给一个主推荐，同时保留 `轻一点`、`换路线` 和 `今天不练` 三个出口。只有缺失
条件确实会改变本次安排时，它才会追问。

| 尺度 | 会发生什么 | 不会发生什么 |
|---|---|---|
| 每日 | 简短诊断，然后学习、尝试或完成一项难度合适的练习 | 必须一路走到 AC 的固定流水线 |
| 每周 | 证据足够时，用一次延迟、隐藏知识点的检查替代当天练习 | 额外作业，或练得少时补欠账 |
| 每月 | 用 5–10 分钟决定接下来继续、降难、暂停或探索什么 | 覆盖率报表、课程进度审计或 backlog |

跳过任何一个尺度都不会产生学习债务。

## 职责流转

```text
Axiom Coach
  选知识点 → 闭卷诊断 → 校准下一步
        │
        ├── 已选定具体 OJ 题 → Axiom Practice
        │      建骨架 → 独立解题 → 平台确认 AC → 当日 PR
        │
        └── 值得延迟重建的通用知识 → Axiom Review
               整理主题 → 记录复习证据 → notes PR
```

你负责接受、覆盖或拒绝推荐，再独立解题、提交并确认 Accepted。仓库检查、建骨架、验证、
Skill 路由、Git、生成产物和 PR 记录由 agent 处理。

## 规则与 pilot 边界

当前 pilot 定义的是人机协作流程，不代表 Axiom 已经拥有完整课程或确定性推荐器。仓库 Skill
不能主动发送定时提醒；automation 需要另行明确提出。Agent 的行为规范见
[Coach Skill](../.agents/skills/axiom-coach/SKILL.md)，详细路由、表格、证据词汇和判定标准见
[session protocol](../.agents/skills/axiom-coach/references/session-protocol.md)。
