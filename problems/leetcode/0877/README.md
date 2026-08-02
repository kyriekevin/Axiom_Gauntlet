# 0877. Stone Game

[English](README.md) | [简体中文](README_zh-CN.md)

> Source: [LeetCode](https://leetcode.com/problems/stone-game/) · UID: `leetcode:0877`

## Core insight

<!-- State the decisive observation in one or two sentences. -->

## Approach

<!-- Explain the algorithm as a short sequence of ideas. -->

## Why it works

<!-- Give the invariant, induction, exchange argument, or other fitting proof. -->

## Complexity

- Time: `O(n^2)` to compute the score difference for every interval.
- Auxiliary space: `O(n^2)` for the DP table; the same recurrence can be compressed to `O(n)` space.

## Pitfalls

<!-- Record boundary cases, failed approaches, and implementation traps. -->

## Visualization

<!-- diagram:start -->
<!-- Add Mermaid or a local asset only when it materially improves understanding. -->
<!-- diagram:end -->

## Review log

| Date | Event | Result | Reflection |
| --- | --- | --- | --- |
| 2026-08-02 | Initial solve and code review | Python Accepted | Interval score-difference DP is a reliable general approach; revisit the `O(n)` space optimization and this problem's parity strategy during the weekly review. |
