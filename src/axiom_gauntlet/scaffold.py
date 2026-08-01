"""Create a new problem directory from repository templates."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from string import Template

from .model import (
    LANGUAGE_FILES,
    PLATFORMS,
    canonical_problem_id,
    expected_uid,
    normalize_language,
    normalize_problem_id,
)

_SOLUTION_PLACEHOLDERS = {
    "cpp": "// TODO: paste the accepted solution.\n",
    "python": "# TODO: paste the accepted solution.\n",
    "go": "// TODO: paste the accepted solution.\n",
}
_TAG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PLATFORM_LABELS = {
    "leetcode": "LeetCode",
    "acwing": "AcWing",
    "codeforces": "Codeforces",
}


def create_problem(
    repo_root: str | Path,
    *,
    platform: str,
    problem_id: str,
    title: str,
    url: str,
    canonical_id: str | None = None,
    difficulty_scheme: str = "unknown",
    difficulty_value: str | int = "unknown",
    difficulty_normalized: str | None = None,
    tags: Iterable[str] = (),
    languages: Iterable[str] = (),
    force: bool = False,
) -> Path:
    """Create a draft problem and return its directory.

    ``languages`` accepts ``cpp``, ``python``/``py``, and ``go``.  The generated
    files are placeholders: the state remains ``draft`` and no AC event is
    invented.  Callers should advance the state only after a real acceptance.
    """

    root = Path(repo_root)
    platform = platform.strip().lower()
    if platform not in PLATFORMS:
        raise ValueError(
            f"unsupported platform {platform!r}; choose one of {', '.join(sorted(PLATFORMS))}"
        )
    normalized_id = normalize_problem_id(platform, str(problem_id))
    derived_canonical_id = canonical_problem_id(platform, normalized_id)
    if canonical_id is not None and canonical_id != derived_canonical_id:
        raise ValueError(
            f"canonical_id must be {derived_canonical_id!r} for {platform}:{problem_id}"
        )
    canonical_id = derived_canonical_id

    title = title.strip()
    url = url.strip()
    if not title:
        raise ValueError("title must not be empty")
    if not url:
        raise ValueError("url must not be empty")

    tag_list = _normalize_tags(tags)
    language_list = _normalize_languages(languages)
    difficulty_scheme = difficulty_scheme.strip().lower()
    difficulty_scheme, difficulty_value = _normalize_difficulty_fields(
        difficulty_scheme, difficulty_value
    )
    normalized_difficulty = _normalize_difficulty(difficulty_value, difficulty_normalized)

    template_dir = root / "templates" / "problem"
    metadata_template = _load_template(template_dir / "problem.toml")
    readme_template = _load_template(template_dir / "README.md")
    chinese_readme_template = _load_template(template_dir / "README_zh-CN.md")

    solution_tables = "\n\n".join(
        "\n".join(
            (
                "[[solutions]]",
                f"file = {_toml_literal(LANGUAGE_FILES[language])}",
                f"language = {_toml_literal(language)}",
            )
        )
        for language in language_list
    )
    metadata = metadata_template.substitute(
        uid=_toml_literal(expected_uid(platform, normalized_id)),
        platform=_toml_literal(platform),
        problem_id=_toml_literal(normalized_id),
        title=_toml_literal(title),
        url=_toml_literal(url),
        tags=_toml_array(tag_list),
        difficulty_scheme=_toml_literal(difficulty_scheme),
        difficulty_value=_toml_literal(difficulty_value),
        difficulty_normalized=_toml_literal(normalized_difficulty),
        solutions=solution_tables,
    )
    readme_values = dict(
        canonical_id=canonical_id,
        platform_label=_PLATFORM_LABELS[platform],
        title=title,
        url=url,
        uid=expected_uid(platform, normalized_id),
    )
    readme = readme_template.substitute(readme_values)
    chinese_readme = chinese_readme_template.substitute(readme_values)

    target = root / "problems" / platform / canonical_id
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"problem directory already exists: {target}")
    target.mkdir(parents=True, exist_ok=True)
    (target / "problem.toml").write_text(metadata, encoding="utf-8", newline="\n")
    (target / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    (target / "README_zh-CN.md").write_text(chinese_readme, encoding="utf-8", newline="\n")
    for language in language_list:
        (target / LANGUAGE_FILES[language]).write_text(
            _SOLUTION_PLACEHOLDERS[language], encoding="utf-8", newline="\n"
        )
    return target


def _normalize_languages(languages: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    for language in languages:
        normalized = normalize_language(language)
        if normalized in result:
            raise ValueError(f"duplicate language: {normalized}")
        result.append(normalized)
    return tuple(result)


def _normalize_tags(tags: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    for raw_tag in tags:
        tag = raw_tag.strip()
        if not _TAG_RE.fullmatch(tag):
            raise ValueError(f"tag {tag!r} must use lowercase kebab-case")
        if tag in result:
            raise ValueError(f"duplicate tag: {tag}")
        result.append(tag)
    return tuple(result)


def _normalize_difficulty(value: str | int, normalized: str | None) -> str:
    if normalized is None:
        if isinstance(value, str) and value.strip().lower() in {
            "easy",
            "medium",
            "hard",
        }:
            return value.strip().lower()
        return "unknown"
    result = normalized.strip().lower()
    if result not in {"easy", "medium", "hard", "unknown"}:
        raise ValueError("difficulty_normalized must be easy, medium, hard, or unknown")
    return result


def _normalize_difficulty_fields(scheme: str, value: str | int) -> tuple[str, str | int]:
    if scheme not in {"level", "rating", "unknown"}:
        raise ValueError("difficulty_scheme must be level, rating, or unknown")
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("difficulty_value must be a string or integer")
    if scheme != "rating":
        return scheme, value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lower() == "unknown":
            return "unknown", "unknown"
        if stripped.isdigit():
            value = int(stripped)
    if not isinstance(value, int) or value <= 0:
        raise ValueError("rating difficulty requires a positive integer value")
    return scheme, value


def _load_template(path: Path) -> Template:
    try:
        return Template(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise FileNotFoundError(f"cannot read scaffold template: {path}") from error


def _toml_array(values: Iterable[str]) -> str:
    return "[" + ", ".join(_toml_literal(value) for value in values) + "]"


def _toml_literal(value: str | int) -> str:
    if isinstance(value, bool):
        raise TypeError("boolean is not a supported TOML literal here")
    if isinstance(value, int):
        return str(value)
    return json.dumps(value, ensure_ascii=False)
