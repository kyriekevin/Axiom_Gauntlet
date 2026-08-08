"""Generated reader-facing activity sections for repository homepages."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .heatmap import discover
from .model import load_problem
from .platforms import platform_spec

RECENT_PROBLEM_LIMIT = 5
RECENT_START = "<!-- recent-problems:start -->"
RECENT_END = "<!-- recent-problems:end -->"
_LANGUAGE_LABELS = {"cpp": "C++", "python": "Python", "go": "Go"}


class HomepageRenderError(ValueError):
    """Raised when a README cannot be updated safely."""


@dataclass(frozen=True)
class RecentProblem:
    uid: str
    title: str
    platform_label: str
    accepted_date: date
    languages: tuple[str, ...]
    directory: str


def recent_problems(
    root: str | Path, limit: int = RECENT_PROBLEM_LIMIT
) -> tuple[RecentProblem, ...]:
    """Return the latest uniquely accepted problems in deterministic order."""

    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise ValueError("recent problem limit must be a non-negative integer")

    root = Path(root)
    records: list[RecentProblem] = []
    for manifest in discover(root):
        problem = load_problem(manifest)
        accepted = [event for event in problem.activity if event.event_type.lower() == "ac"]
        if not accepted:
            continue
        languages = tuple(
            sorted(
                {
                    _LANGUAGE_LABELS.get(event.language, event.language)
                    for event in accepted
                    if event.language is not None
                }
            )
        )
        records.append(
            RecentProblem(
                uid=problem.uid,
                title=problem.title,
                platform_label=platform_spec(problem.platform).label,
                accepted_date=max(event.date for event in accepted),
                languages=languages,
                directory=manifest.parent.relative_to(root).as_posix(),
            )
        )

    records.sort(key=lambda record: record.uid)
    records.sort(key=lambda record: record.accepted_date, reverse=True)
    return tuple(records[:limit])


def _escape_table_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def render_recent_problems(root: str | Path, *, language: str) -> str:
    """Render the recent-problem table in English or Simplified Chinese."""

    records = recent_problems(root)
    if language == "en":
        header = ("Date", "Problem", "Platform", "Language")
        empty = "No accepted problems yet."
    elif language == "zh-CN":
        header = ("日期", "题目", "平台", "语言")
        empty = "暂无已通过题目。"
    else:
        raise ValueError(f"unsupported homepage language: {language!r}")

    if not records:
        return empty

    lines = [
        f"| {' | '.join(header)} |",
        "| --- | --- | --- | --- |",
    ]
    for record in records:
        title = _escape_table_text(record.title)
        problem_link = f"[{title}]({record.directory}/)"
        languages = " / ".join(record.languages) or "—"
        lines.append(
            f"| {record.accepted_date.isoformat()} | {problem_link} | "
            f"{_escape_table_text(record.platform_label)} | {languages} |"
        )
    return "\n".join(lines)


def _replace_recent_section(document: str, section: str, path: Path) -> str:
    if document.count(RECENT_START) != 1 or document.count(RECENT_END) != 1:
        raise HomepageRenderError(f"{path} must contain exactly one recent-problems marker pair")
    start = document.index(RECENT_START)
    end = document.index(RECENT_END)
    if end < start:
        raise HomepageRenderError(f"{path} has reversed recent-problems markers")
    content_start = start + len(RECENT_START)
    return f"{document[:content_start]}\n\n{section}\n\n{document[end:]}"


def generate_homepages(root: str | Path, *, check: bool = False) -> tuple[Path, ...]:
    """Update generated recent-problem sections in both repository READMEs."""

    root = Path(root)
    changed: list[Path] = []
    for filename, language in (("README.md", "en"), ("README_zh-CN.md", "zh-CN")):
        path = root / filename
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError as error:
            raise HomepageRenderError(f"cannot read {path}: {error}") from error
        expected = _replace_recent_section(
            actual,
            render_recent_problems(root, language=language),
            path,
        )
        if actual == expected:
            continue
        changed.append(path)
        if not check:
            path.write_text(expected, encoding="utf-8", newline="\n")
    return tuple(changed)
