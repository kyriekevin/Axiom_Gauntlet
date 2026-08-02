from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pytest

from axiom_gauntlet.knowledge import (
    create_topic,
    document_topic,
    load_topic,
    render_indexes,
    review_topic,
)
from axiom_gauntlet.validate import validate_repository

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _empty_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "knowledge").mkdir(parents=True)
    for platform in ("leetcode", "acwing", "codeforces"):
        (root / "problems" / platform).mkdir(parents=True)
    shutil.copytree(
        REPOSITORY_ROOT / "templates" / "knowledge",
        root / "templates" / "knowledge",
    )
    return root


def _complete_notes(directory: Path) -> None:
    english = {
        "Overview": "Solve problems whose state is a contiguous interval.",
        "Recognition": "Each move removes or splits an interval.",
        "Model": "Let f[i][j] describe the remaining interval [i, j].",
        "Derivation": "Enumerate the boundary choice and reduce to a shorter interval.",
        "Variants": "Memoization and bottom-up evaluation share the same recurrence.",
        "Examples": "leetcode:0486 exposes the score-difference model.",
        "Review log": "| 2026-08-02 | Initial note | pass | Re-derived the state. |",
    }
    chinese = {
        "概览": "处理状态是连续区间的一类问题。",
        "识别信号": "每次选择都会移除或切分区间。",
        "建模": "用 f[i][j] 表示当前剩余区间 [i, j]。",
        "推导": "枚举边界选择，并转移到更短的区间。",
        "变体": "记忆化搜索与递推只是同一状态依赖的不同求值方式。",
        "例题": "leetcode:0486 展示净胜分模型。",
        "复习记录": "| 2026-08-02 | 首次整理 | 通过 | 重新推导了状态。 |",
    }
    (directory / "README.md").write_text(
        "# Interval DP\n\n"
        + "\n\n".join(f"## {heading}\n\n{content}" for heading, content in english.items())
        + "\n",
        encoding="utf-8",
    )
    (directory / "README_zh-CN.md").write_text(
        "# 区间动态规划\n\n"
        + "\n\n".join(f"## {heading}\n\n{content}" for heading, content in chinese.items())
        + "\n",
        encoding="utf-8",
    )


def test_topic_lifecycle_rolls_back_incomplete_notes(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    directory = create_topic(
        root,
        topic_path="dynamic-programming/interval-dp",
        title="Interval DP",
        title_zh_cn="区间动态规划",
        tags=("dynamic-programming",),
    )
    manifest = directory / "topic.toml"
    original = manifest.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="missing or incomplete"):
        document_topic(root, "dynamic-programming/interval-dp", date(2026, 8, 2))

    assert manifest.read_text(encoding="utf-8") == original
    _complete_notes(directory)
    document_topic(root, "dynamic-programming/interval-dp", date(2026, 8, 2))
    review_topic(root, "dynamic-programming/interval-dp", date(2026, 8, 9), "pass")

    topic = load_topic(manifest)
    assert topic.state == "documented"
    assert [(event.event_type, event.result) for event in topic.activity] == [
        ("note", None),
        ("review", "pass"),
    ]


def test_indexes_detect_stale_generated_files(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    create_topic(
        root,
        topic_path="dynamic-programming/interval-dp",
        title="Interval DP",
        title_zh_cn="区间动态规划",
    )

    assert render_indexes(root, check=True)
    render_indexes(root)
    assert render_indexes(root, check=True) == ()
    assert "dynamic-programming/interval-dp/README.md" in (
        root / "knowledge" / "INDEX.md"
    ).read_text(encoding="utf-8")


def test_repository_rejects_dangling_knowledge_references(tmp_path: Path) -> None:
    root = _empty_repo(tmp_path)
    create_topic(
        root,
        topic_path="dynamic-programming/interval-dp",
        title="Interval DP",
        title_zh_cn="区间动态规划",
        links=("dynamic-programming/state-machine-dp",),
        examples=(("leetcode:0486", "baseline"),),
    )

    issues = validate_repository(root)

    assert any(issue.code == "knowledge.link-missing" for issue in issues)
    assert any(issue.code == "knowledge.example-missing" for issue in issues)
