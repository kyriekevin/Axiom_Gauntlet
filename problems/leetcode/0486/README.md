# 0486. Predict the Winner

[English](README.md) | [简体中文](README_zh-CN.md)

> Source: [LeetCode](https://leetcode.com/problems/predict-the-winner/) · UID: `leetcode:0486`

## Core insight

<!-- State the decisive observation in one or two sentences. -->

## Approach

<!-- Explain the algorithm as a short sequence of ideas. -->

## Why it works

<!-- Give the invariant, induction, exchange argument, or other fitting proof. -->

## Complexity

- Time: `O(n^2)` for all intervals.
- Auxiliary space: `O(n^2)` for the DP table; the same recurrence can be compressed to `O(n)`
  space.

## Pitfalls

<!-- Record boundary cases, failed approaches, and implementation traps. -->

## Visualization

<!-- diagram:start -->
<!-- Add Mermaid or a local asset only when it materially improves understanding. -->
<!-- diagram:end -->

## Review log

| Date | Event | Result | Reflection |
| --- | --- | --- | --- |
| 2026-08-01 | Initial solve and code review | Accepted in Python and C++ | The 2D score-difference DP is clear; re-derive the `O(n)` space compression during the weekend review. |
