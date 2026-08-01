"""Typed model and TOML loader for Axiom Gauntlet problems."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
PLATFORMS = frozenset({"leetcode", "acwing", "codeforces"})
STATES = frozenset({"draft", "accepted", "documented"})
NORMALIZED_DIFFICULTIES = frozenset({"easy", "medium", "hard", "unknown"})
LANGUAGE_FILES = {
    "cpp": "solution.cpp",
    "python": "solution.py",
    "go": "solution.go",
}
LANGUAGE_ALIASES = {
    "cpp": "cpp",
    "c++": "cpp",
    "python": "python",
    "py": "python",
    "go": "go",
    "golang": "go",
}


class MetadataError(ValueError):
    """Raised when ``problem.toml`` cannot be converted into a Problem."""

    def __init__(self, messages: Sequence[str]):
        self.messages = tuple(messages)
        super().__init__("; ".join(self.messages))


@dataclass(frozen=True)
class Difficulty:
    scheme: str
    value: str | int
    normalized: str


@dataclass(frozen=True)
class Solution:
    file: str
    language: str


@dataclass(frozen=True)
class Activity:
    event_type: str
    date: date
    language: str | None = None
    result: str | None = None


@dataclass(frozen=True)
class Problem:
    version: int
    uid: str
    platform: str
    problem_id: str
    title: str
    url: str
    state: str
    tags: tuple[str, ...]
    difficulty: Difficulty
    solutions: tuple[Solution, ...]
    activity: tuple[Activity, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> Problem:
        errors: list[str] = []
        allowed_top_level = {
            "version",
            "uid",
            "platform",
            "problem_id",
            "title",
            "url",
            "state",
            "tags",
            "difficulty",
            "solutions",
            "activity",
        }
        _report_unknown_keys(raw, allowed_top_level, "top level", errors)

        version = _integer(raw, "version", errors)
        uid = _string(raw, "uid", errors)
        platform = _string(raw, "platform", errors)
        problem_id = _string(raw, "problem_id", errors)
        title = _string(raw, "title", errors)
        url = _string(raw, "url", errors)
        state = _string(raw, "state", errors)
        tags = _string_list(raw, "tags", errors)

        difficulty_raw = raw.get("difficulty")
        if not isinstance(difficulty_raw, Mapping):
            errors.append("difficulty must be a table")
            difficulty = Difficulty("", "", "")
        else:
            _report_unknown_keys(
                difficulty_raw,
                {"scheme", "value", "normalized"},
                "difficulty",
                errors,
            )
            scheme = _string(difficulty_raw, "scheme", errors, "difficulty.")
            value = difficulty_raw.get("value")
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                errors.append("difficulty.value must be a string or integer")
                value = ""
            normalized = _string(difficulty_raw, "normalized", errors, "difficulty.")
            difficulty = Difficulty(scheme, value, normalized)

        solutions_raw = raw.get("solutions", [])
        solutions: list[Solution] = []
        if not isinstance(solutions_raw, list):
            errors.append("solutions must be an array of tables")
        else:
            for index, item in enumerate(solutions_raw):
                label = f"solutions[{index}]"
                if not isinstance(item, Mapping):
                    errors.append(f"{label} must be a table")
                    continue
                _report_unknown_keys(item, {"file", "language"}, label, errors)
                solutions.append(
                    Solution(
                        file=_string(item, "file", errors, f"{label}."),
                        language=_string(item, "language", errors, f"{label}."),
                    )
                )

        activity_raw = raw.get("activity", [])
        activity: list[Activity] = []
        if not isinstance(activity_raw, list):
            errors.append("activity must be an array of tables")
        else:
            for index, item in enumerate(activity_raw):
                label = f"activity[{index}]"
                if not isinstance(item, Mapping):
                    errors.append(f"{label} must be a table")
                    continue
                _report_unknown_keys(item, {"type", "date", "language", "result"}, label, errors)
                event_date = _date(item.get("date"), f"{label}.date", errors)
                activity.append(
                    Activity(
                        event_type=_string(item, "type", errors, f"{label}."),
                        date=event_date,
                        language=_optional_string(item, "language", errors, f"{label}."),
                        result=_optional_string(item, "result", errors, f"{label}."),
                    )
                )

        if errors:
            raise MetadataError(errors)

        return cls(
            version=version,
            uid=uid,
            platform=platform,
            problem_id=problem_id,
            title=title,
            url=url,
            state=state,
            tags=tuple(tags),
            difficulty=difficulty,
            solutions=tuple(solutions),
            activity=tuple(activity),
        )


def load_problem(path: str | Path) -> Problem:
    """Load and type-check a ``problem.toml`` file."""

    metadata_path = Path(path)
    try:
        with metadata_path.open("rb") as stream:
            raw = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise MetadataError((f"cannot read TOML: {error}",)) from error
    return Problem.from_mapping(raw)


def normalize_problem_id(platform: str, problem_id: str) -> str:
    """Return the normalized source ID stored in ``problem.toml``."""

    if platform not in PLATFORMS:
        raise ValueError(f"unsupported platform: {platform!r}")
    raw = str(problem_id).strip()

    if platform in {"leetcode", "acwing"}:
        if not re.fullmatch(r"\d+", raw):
            raise ValueError(f"{platform} problem_id must contain only digits")
        number = int(raw)
        if number <= 0:
            raise ValueError(f"{platform} problem_id must be greater than zero")
        return str(number)

    match = re.fullmatch(r"0*(\d+)([A-Za-z][A-Za-z0-9]*)", raw)
    if match is None:
        raise ValueError("codeforces problem_id must be a contest number followed by an index")
    contest = int(match.group(1))
    if contest <= 0:
        raise ValueError("codeforces contest number must be greater than zero")
    return f"{contest}{match.group(2).upper()}"


def canonical_problem_id(platform: str, problem_id: str) -> str:
    """Return the stable directory ID for a platform problem."""

    normalized = normalize_problem_id(platform, problem_id)
    if platform == "leetcode":
        return normalized.zfill(4)
    return normalized


def expected_uid(platform: str, problem_id: str) -> str:
    return f"{platform}:{canonical_problem_id(platform, problem_id)}"


def normalize_language(language: str) -> str:
    normalized = LANGUAGE_ALIASES.get(language.strip().lower())
    if normalized is None:
        supported = ", ".join(sorted(LANGUAGE_FILES))
        raise ValueError(f"unsupported language {language!r}; choose one of {supported}")
    return normalized


def _report_unknown_keys(
    mapping: Mapping[str, Any],
    allowed: set[str],
    label: str,
    errors: list[str],
) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        errors.append(f"{label} contains unknown keys: {', '.join(unknown)}")


def _string(
    mapping: Mapping[str, Any],
    key: str,
    errors: list[str],
    prefix: str = "",
) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}{key} must be a non-empty string")
        return ""
    return value.strip()


def _optional_string(
    mapping: Mapping[str, Any],
    key: str,
    errors: list[str],
    prefix: str = "",
) -> str | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}{key} must be a non-empty string when present")
        return None
    return value.strip()


def _integer(mapping: Mapping[str, Any], key: str, errors: list[str]) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{key} must be an integer")
        return 0
    return value


def _string_list(mapping: Mapping[str, Any], key: str, errors: list[str]) -> list[str]:
    value = mapping.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be an array of strings")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{key}[{index}] must be a non-empty string")
        else:
            result.append(item.strip())
    return result


def _date(value: Any, label: str, errors: list[str]) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    errors.append(f"{label} must be an ISO date (YYYY-MM-DD)")
    return date.min
