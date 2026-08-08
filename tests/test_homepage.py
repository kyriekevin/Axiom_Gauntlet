from __future__ import annotations

from pathlib import Path

import pytest

from axiom_gauntlet.homepage import (
    HomepageRenderError,
    generate_homepages,
    recent_problems,
    render_recent_problems,
)


def _write_problem(
    root: Path,
    platform: str,
    problem_id: str,
    title: str,
    activities: tuple[tuple[str, str], ...],
) -> None:
    directory_id = problem_id.zfill(4) if platform == "leetcode" else problem_id
    activity = "\n".join(
        (f'[[activity]]\ntype = "ac"\ndate = {event_date}\nlanguage = "{language}"')
        for event_date, language in activities
    )
    manifest = root / "problems" / platform / directory_id / "problem.toml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        f"""version = 1
uid = "{platform}:{directory_id}"
platform = "{platform}"
problem_id = "{problem_id}"
title = "{title}"
url = "https://example.com/{problem_id}"
state = "accepted"
tags = []

[difficulty]
scheme = "level"
value = "unknown"
normalized = "unknown"

{activity}
""",
        encoding="utf-8",
    )


def _write_readmes(root: Path) -> None:
    for filename in ("README.md", "README_zh-CN.md"):
        (root / filename).write_text(
            "# Test\n\n<!-- recent-problems:start -->\nstale\n"
            "<!-- recent-problems:end -->\n\nKeep me.\n",
            encoding="utf-8",
        )


def test_recent_problems_sorts_by_latest_ac_and_deduplicates_languages(tmp_path: Path) -> None:
    _write_problem(tmp_path, "leetcode", "2", "Later", (("2026-08-07", "python"),))
    _write_problem(tmp_path, "acwing", "1", "同日", (("2026-08-07", "cpp"),))
    _write_problem(
        tmp_path,
        "leetcode",
        "1",
        "Two Languages",
        (("2026-08-01", "python"), ("2026-08-06", "cpp")),
    )

    records = recent_problems(tmp_path)

    assert [record.uid for record in records] == ["acwing:1", "leetcode:0002", "leetcode:0001"]
    assert records[2].accepted_date.isoformat() == "2026-08-06"
    assert records[2].languages == ("C++", "Python")


def test_recent_problem_table_is_bilingual_and_links_problem_cards(tmp_path: Path) -> None:
    _write_problem(tmp_path, "deep-ml", "1", "Matrix | Vector", (("2026-08-08", "python"),))

    english = render_recent_problems(tmp_path, language="en")
    chinese = render_recent_problems(tmp_path, language="zh-CN")

    assert "| Date | Problem | Platform | Language |" in english
    assert "[Matrix \\| Vector](problems/deep-ml/1/)" in english
    assert "| 日期 | 题目 | 平台 | 语言 |" in chinese
    assert "Deep-ML" in chinese


def test_recent_problems_defaults_to_five_entries(tmp_path: Path) -> None:
    for problem_id in range(1, 7):
        _write_problem(
            tmp_path,
            "deep-ml",
            str(problem_id),
            f"Problem {problem_id}",
            ((f"2026-08-{problem_id:02d}", "python"),),
        )

    records = recent_problems(tmp_path)

    assert [record.uid for record in records] == [
        "deep-ml:6",
        "deep-ml:5",
        "deep-ml:4",
        "deep-ml:3",
        "deep-ml:2",
    ]


def test_generate_homepages_supports_write_and_check_modes(tmp_path: Path) -> None:
    _write_readmes(tmp_path)
    _write_problem(tmp_path, "leetcode", "1", "Two Sum", (("2026-08-01", "python"),))

    changed = generate_homepages(tmp_path)

    assert tuple(path.name for path in changed) == ("README.md", "README_zh-CN.md")
    assert "[Two Sum](problems/leetcode/0001/)" in (tmp_path / "README.md").read_text()
    assert "Keep me." in (tmp_path / "README.md").read_text()
    assert generate_homepages(tmp_path, check=True) == ()

    _write_problem(tmp_path, "deep-ml", "1", "Matrix Times Vector", (("2026-08-08", "python"),))
    stale = generate_homepages(tmp_path, check=True)
    assert tuple(path.name for path in stale) == ("README.md", "README_zh-CN.md")
    assert "Matrix Times Vector" not in (tmp_path / "README.md").read_text()


def test_generate_homepages_requires_safe_markers(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Missing markers\n", encoding="utf-8")
    (tmp_path / "README_zh-CN.md").write_text("# 缺少标记\n", encoding="utf-8")

    with pytest.raises(HomepageRenderError, match="marker pair"):
        generate_homepages(tmp_path)
