from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pytest

from axiom_gauntlet.lifecycle import record_acceptance, record_documentation
from axiom_gauntlet.model import PLATFORMS, load_problem
from axiom_gauntlet.scaffold import create_problem

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _empty_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "knowledge").mkdir(parents=True)
    for platform in PLATFORMS:
        (root / "problems" / platform).mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        REPOSITORY_ROOT / "templates" / "problem",
        root / "templates" / "problem",
    )
    return root


def _draft(tmp_path: Path, *, languages: tuple[str, ...] = ("cpp",)) -> tuple[Path, Path]:
    root = _empty_repo(tmp_path)
    directory = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
        languages=languages,
    )
    return root, directory


def _complete_notes(directory: Path) -> None:
    (directory / "README.md").write_text(
        """# Two Sum

## Core insight

Store visited values in a hash table.

## Approach

Look up each complement before inserting the current value.

## Why it works

When the second endpoint is visited, the first endpoint is already stored.

## Complexity

- Time: O(n)
- Space: O(n)

## Pitfalls

Lookup must happen before insertion.

## Review log

| Date | Event | Result | Reflection |
| --- | --- | --- | --- |
| 2026-08-01 | Initial solve | Accepted | Recheck lookup order. |
""",
        encoding="utf-8",
    )
    (directory / "README_zh-CN.md").write_text(
        """# 两数之和

## 核心洞察

使用哈希表保存已经访问过的值。

## 解题思路

查询目标差值后，再插入当前值。

## 正确性说明

访问答案右端点时，左端点已经保存在哈希表中。

## 复杂度

- 时间：O(n)
- 空间：O(n)

## 易错点

必须先查询再插入。

## 复习记录

| 日期 | 事件 | 结果 | 反思 |
| --- | --- | --- | --- |
| 2026-08-01 | 首次解题 | Accepted | 复查查询顺序。 |
""",
        encoding="utf-8",
    )


def test_record_acceptance_advances_draft_and_preserves_comments(tmp_path: Path) -> None:
    root, directory = _draft(tmp_path)
    (directory / "solution.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")

    record_acceptance(
        root,
        platform="leetcode",
        problem_id="1",
        language="cpp",
        event_date=date(2026, 8, 1),
        time_complexity="O(n)",
        space_complexity="O(n)",
    )

    problem = load_problem(directory / "problem.toml")
    assert problem.state == "accepted"
    assert [(event.event_type, event.language) for event in problem.activity] == [("ac", "cpp")]
    metadata = (directory / "problem.toml").read_text(encoding="utf-8")
    assert "Add an activity only after the platform confirms the result." in metadata


def test_record_acceptance_rejects_placeholder_without_mutating_metadata(tmp_path: Path) -> None:
    root, directory = _draft(tmp_path)
    metadata_path = directory / "problem.toml"
    original = metadata_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="placeholder"):
        record_acceptance(
            root,
            platform="leetcode",
            problem_id="1",
            language="cpp",
            event_date=date(2026, 8, 1),
            time_complexity="O(n)",
            space_complexity="O(n)",
        )

    assert metadata_path.read_text(encoding="utf-8") == original


def test_record_acceptance_requires_the_selected_language_code(tmp_path: Path) -> None:
    root, directory = _draft(tmp_path, languages=("cpp", "python"))
    (directory / "solution.py").write_text("print(0)\n", encoding="utf-8")

    with pytest.raises(ValueError, match="solution.cpp"):
        record_acceptance(
            root,
            platform="leetcode",
            problem_id="1",
            language="cpp",
            event_date=date(2026, 8, 1),
            time_complexity="O(n)",
            space_complexity="O(n)",
        )


def test_record_documentation_rolls_back_until_both_notes_are_complete(tmp_path: Path) -> None:
    root, directory = _draft(tmp_path)
    (directory / "solution.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    record_acceptance(
        root,
        platform="leetcode",
        problem_id="1",
        language="cpp",
        event_date=date(2026, 8, 1),
        time_complexity="O(n)",
        space_complexity="O(n)",
    )
    metadata_path = directory / "problem.toml"
    accepted_metadata = metadata_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="readme.section-missing"):
        record_documentation(
            root,
            platform="leetcode",
            problem_id="1",
            event_date=date(2026, 8, 2),
        )

    assert metadata_path.read_text(encoding="utf-8") == accepted_metadata

    _complete_notes(directory)
    record_documentation(
        root,
        platform="leetcode",
        problem_id="1",
        event_date=date(2026, 8, 2),
    )
    problem = load_problem(metadata_path)
    assert problem.state == "documented"
    assert [event.event_type for event in problem.activity] == ["ac", "note"]
