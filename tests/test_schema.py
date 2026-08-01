from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from axiom_gauntlet.model import canonical_problem_id, expected_uid, load_problem
from axiom_gauntlet.scaffold import create_problem
from axiom_gauntlet.validate import validate_problem_dir, validate_repository

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _empty_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for platform in ("leetcode", "acwing", "codeforces"):
        (root / "problems" / platform).mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        REPOSITORY_ROOT / "templates" / "problem",
        root / "templates" / "problem",
    )
    return root


def _record_ac(problem_dir: Path, language: str = "cpp") -> None:
    metadata_path = problem_dir / "problem.toml"
    metadata = metadata_path.read_text(encoding="utf-8")
    metadata = metadata.replace('state = "draft"', 'state = "accepted"')
    metadata += f'\n[[activity]]\ntype = "ac"\ndate = 2026-08-01\nlanguage = "{language}"\n'
    metadata_path.write_text(metadata, encoding="utf-8")
    extension = {"cpp": "cpp", "python": "py", "go": "go"}[language]
    (problem_dir / f"solution.{extension}").write_text(
        "int main() { return 0; }\n" if language == "cpp" else "pass\n",
        encoding="utf-8",
    )


def _complete_readmes(problem_dir: Path) -> None:
    (problem_dir / "README.md").write_text(
        """# Example

## Core insight

Store each visited number and its index in a hash table.

## Approach

Scan the array, look up the complement, and then record the current number.

## Why it works

When the right endpoint is reached, the left endpoint is already stored, so the pair is found.

## Complexity

- Time: O(n)
- Space: O(n)

## Pitfalls

Look up before inserting so the same element cannot be used twice.

## Review log

| Date | Event | Result | Reflection |
| --- | --- | --- | --- |
| 2026-08-01 | Initial solve | Accepted | Recheck the lookup-before-insert invariant. |
""",
        encoding="utf-8",
    )
    (problem_dir / "README_zh-CN.md").write_text(
        """# 示例

## 核心洞察

使用哈希表保存已经访问过的数字及其下标。

## 解题思路

依次扫描数组，先查找目标差值，再记录当前数字。

## 正确性说明

扫描到答案右端点时，左端点已在表中，因此一定返回合法下标。

## 复杂度

- 时间：O(n)
- 空间：O(n)

## 易错点

必须先查询再插入，避免同一元素被使用两次。

## 复习记录

| 日期 | 事件 | 结果 | 反思 |
| --- | --- | --- | --- |
| 2026-08-01 | 首次解题 | 通过 | 复查先查询后插入的不变量。 |
""",
        encoding="utf-8",
    )


def test_platform_canonical_ids() -> None:
    assert canonical_problem_id("leetcode", "1") == "0001"
    assert canonical_problem_id("leetcode", "3536") == "3536"
    assert canonical_problem_id("acwing", "0785") == "785"
    assert canonical_problem_id("codeforces", "004a") == "4A"
    assert expected_uid("leetcode", "1") == "leetcode:0001"


def test_scaffold_creates_draft_with_multiple_languages(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
        difficulty_scheme="level",
        difficulty_value="Easy",
        tags=("array", "hash-table"),
        languages=("cpp", "py", "go"),
    )

    assert problem_dir == root / "problems" / "leetcode" / "0001"
    assert (problem_dir / "solution.cpp").is_file()
    assert (problem_dir / "solution.py").is_file()
    assert (problem_dir / "solution.go").is_file()
    assert (problem_dir / "README_zh-CN.md").is_file()
    problem = load_problem(problem_dir / "problem.toml")
    assert problem.uid == "leetcode:0001"
    assert problem.problem_id == "1"
    assert problem.state == "draft"
    assert [item.language for item in problem.solutions] == ["cpp", "python", "go"]
    assert not problem.activity
    readme = (problem_dir / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# 0001. Two Sum\n")
    assert "[LeetCode](https://leetcode.com/problems/two-sum/)" in readme
    assert validate_problem_dir(problem_dir) == []


def test_scaffold_refuses_to_overwrite_by_default(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    arguments = dict(
        platform="acwing",
        problem_id="0785",
        title="Quick Sort",
        url="https://www.acwing.com/problem/content/787/",
    )
    create_problem(root, **arguments)
    with pytest.raises(FileExistsError):
        create_problem(root, **arguments)


def test_validator_requires_both_language_notes(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
    )
    chinese_readme = problem_dir / "README_zh-CN.md"
    chinese_readme.unlink()

    issues = validate_problem_dir(problem_dir)

    assert any(issue.path == chinese_readme and issue.code == "readme.missing" for issue in issues)


def test_accepted_requires_ac_and_existing_solution(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="codeforces",
        problem_id="004a",
        title="Watermelon",
        url="https://codeforces.com/problemset/problem/4/A",
        difficulty_scheme="rating",
        difficulty_value=800,
        difficulty_normalized="easy",
        languages=("cpp",),
    )
    metadata_path = problem_dir / "problem.toml"
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8").replace('state = "draft"', 'state = "accepted"'),
        encoding="utf-8",
    )

    issues = validate_problem_dir(problem_dir)
    assert any(issue.code == "state.ac-required" for issue in issues)
    assert any(issue.code == "state.solution-placeholder" for issue in issues)

    _record_ac(problem_dir)
    assert validate_problem_dir(problem_dir) == []


def test_accepted_requires_code_for_the_ac_language(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
        languages=("cpp", "python"),
    )
    metadata_path = problem_dir / "problem.toml"
    metadata = metadata_path.read_text(encoding="utf-8")
    metadata = metadata.replace('state = "draft"', 'state = "accepted"')
    metadata += '\n[[activity]]\ntype = "ac"\ndate = 2026-08-01\nlanguage = "cpp"\n'
    metadata_path.write_text(metadata, encoding="utf-8")
    (problem_dir / "solution.py").write_text("print(0)\n", encoding="utf-8")

    issues = validate_problem_dir(problem_dir)

    assert any(issue.code == "state.solution-placeholder" for issue in issues)

    (problem_dir / "solution.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    assert validate_problem_dir(problem_dir) == []


def test_draft_rejects_review_activity(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
    )
    metadata_path = problem_dir / "problem.toml"
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8")
        + '\n[[activity]]\ntype = "review"\ndate = 2026-08-01\nresult = "pass"\n',
        encoding="utf-8",
    )

    issues = validate_problem_dir(problem_dir)

    assert any(issue.code == "state.review-in-draft" for issue in issues)


def test_documented_requires_complete_readme(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
        languages=("cpp",),
    )
    _record_ac(problem_dir)
    metadata_path = problem_dir / "problem.toml"
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8").replace(
            'state = "accepted"', 'state = "documented"'
        ),
        encoding="utf-8",
    )

    issues = validate_problem_dir(problem_dir)
    assert any(issue.code == "readme.section-incomplete" for issue in issues)
    assert any(issue.code == "state.note-required" for issue in issues)

    _complete_readmes(problem_dir)
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8")
        + '\n[[activity]]\ntype = "note"\ndate = 2026-08-01\n',
        encoding="utf-8",
    )
    assert validate_problem_dir(problem_dir) == []


def test_validator_rejects_path_and_uid_mismatch(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    problem_dir = create_problem(
        root,
        platform="leetcode",
        problem_id="1",
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum/",
    )
    wrong_dir = problem_dir.with_name("1")
    problem_dir.rename(wrong_dir)
    metadata_path = wrong_dir / "problem.toml"
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8").replace(
            'uid = "leetcode:0001"', 'uid = "leetcode:1"'
        ),
        encoding="utf-8",
    )

    issues = validate_problem_dir(wrong_dir)
    assert any(issue.code == "path.id-mismatch" for issue in issues)
    assert any(issue.code == "uid.mismatch" for issue in issues)


def test_repository_validation_accepts_empty_platforms(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    assert validate_repository(root) == []
