from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from axiom_gauntlet.cli import main
from axiom_gauntlet.model import load_problem

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _empty_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "knowledge").mkdir(parents=True)
    (root / "problems").mkdir()
    shutil.copytree(
        REPOSITORY_ROOT / "templates" / "problem",
        root / "templates" / "problem",
    )
    return root


def test_new_command_creates_a_normalized_codeforces_draft(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)

    result = main(
        [
            "--root",
            str(root),
            "new",
            "codeforces",
            "004a",
            "--title",
            "Watermelon",
            "--url",
            "https://codeforces.com/problemset/problem/4/A",
            "--difficulty",
            "800",
            "--normalized-difficulty",
            "easy",
            "--language",
            "cpp",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == "problems/codeforces/4A"
    problem = load_problem(root / "problems" / "codeforces" / "4A" / "problem.toml")
    assert problem.difficulty.scheme == "rating"
    assert problem.difficulty.value == 800
    assert problem.state == "draft"


def test_new_command_creates_a_deep_ml_draft(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)

    result = main(
        [
            "--root",
            str(root),
            "new",
            "deep-ml",
            "001",
            "--title",
            "Matrix Times Vector",
            "--url",
            "https://www.deep-ml.com/problems/1",
            "--difficulty",
            "Easy",
            "--language",
            "python",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == "problems/deep-ml/1"
    problem = load_problem(root / "problems" / "deep-ml" / "1" / "problem.toml")
    assert problem.uid == "deep-ml:1"
    assert problem.problem_id == "1"
    assert problem.difficulty.scheme == "level"


def test_new_command_reports_user_errors_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)

    with pytest.raises(SystemExit, match="2"):
        main(
            [
                "--root",
                str(root),
                "new",
                "leetcode",
                "1",
                "--title",
                "Two Sum",
            ]
        )

    error = capsys.readouterr().err
    assert "--url" in error
    assert "Traceback" not in error


def test_new_command_turns_scaffold_errors_into_cli_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)
    arguments = [
        "--root",
        str(root),
        "new",
        "leetcode",
        "1",
        "--title",
        "Two Sum",
        "--url",
        "https://leetcode.com/problems/two-sum/",
    ]
    assert main(arguments) == 0
    capsys.readouterr()

    with pytest.raises(SystemExit, match="2"):
        main(arguments)

    error = capsys.readouterr().err
    assert "problem directory already exists" in error
    assert "Traceback" not in error


def test_accept_command_records_confirmed_solution(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)
    assert (
        main(
            [
                "--root",
                str(root),
                "new",
                "leetcode",
                "1",
                "--title",
                "Two Sum",
                "--url",
                "https://leetcode.com/problems/two-sum/",
                "--language",
                "cpp",
            ]
        )
        == 0
    )
    capsys.readouterr()
    problem_dir = root / "problems" / "leetcode" / "0001"
    (problem_dir / "solution.cpp").write_text(
        "int main() { return 0; }\n",
        encoding="utf-8",
    )

    result = main(
        [
            "--root",
            str(root),
            "accept",
            "leetcode",
            "1",
            "--language",
            "cpp",
            "--date",
            "2026-08-01",
            "--time-complexity",
            "O(n)",
            "--space-complexity",
            "O(n)",
            "--reflection",
            "Recheck lookup order.",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == "Accepted: problems/leetcode/0001"
    problem = load_problem(problem_dir / "problem.toml")
    assert problem.state == "accepted"
    assert problem.solutions[0].time_complexity == "O(n)"
    assert problem.solutions[0].space_complexity == "O(n)"
    assert problem.activity[0].reflection == "Recheck lookup order."


def test_lifecycle_command_rejects_noncanonical_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)

    with pytest.raises(SystemExit, match="2"):
        main(
            [
                "--root",
                str(root),
                "document",
                "leetcode",
                "1",
                "--date",
                "20260801",
            ]
        )

    assert "date must use YYYY-MM-DD" in capsys.readouterr().err


def test_knowledge_new_and_render_commands(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)
    shutil.copytree(
        REPOSITORY_ROOT / "templates" / "knowledge",
        root / "templates" / "knowledge",
    )

    result = main(
        [
            "--root",
            str(root),
            "knowledge",
            "new",
            "dynamic-programming/interval-dp",
            "--title",
            "Interval DP",
            "--title-zh-cn",
            "区间动态规划",
            "--tag",
            "dynamic-programming",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == ("knowledge/dynamic-programming/interval-dp")
    assert main(["--root", str(root), "knowledge", "render"]) == 0
    capsys.readouterr()
    assert main(["--root", str(root), "knowledge", "render", "--check"]) == 0


def test_render_command_updates_homepage_activity(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _empty_repo(tmp_path)
    for filename in ("README.md", "README_zh-CN.md"):
        (root / filename).write_text(
            "# Test\n\n<!-- recent-problems:start -->\n<!-- recent-problems:end -->\n",
            encoding="utf-8",
        )

    assert main(["--root", str(root), "render", "--year", "2026"]) == 0
    assert "Rendered homepage activity for 2026." in capsys.readouterr().out
    assert (root / "assets" / "heatmaps" / "total.svg").is_file()
    assert "No accepted problems yet." in (root / "README.md").read_text(encoding="utf-8")
    assert main(["--root", str(root), "render", "--year", "2026", "--check"]) == 0
    assert "Homepage activity is up to date." in capsys.readouterr().out
