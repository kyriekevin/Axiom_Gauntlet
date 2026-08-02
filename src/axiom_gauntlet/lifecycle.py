"""Safe lifecycle transitions for problem records."""

from __future__ import annotations

import os
import stat
import tempfile
from collections.abc import Callable
from datetime import date
from pathlib import Path

import tomlkit
from tomlkit import TOMLDocument

from .model import (
    LANGUAGE_FILES,
    canonical_problem_id,
    load_problem,
    normalize_language,
    normalize_problem_id,
)
from .validate import has_solution_content, validate_problem_dir


def problem_directory(repo_root: str | Path, platform: str, problem_id: str) -> Path:
    """Resolve a normalized problem directory below *repo_root*."""

    normalized_platform = platform.strip().lower()
    normalized_id = normalize_problem_id(normalized_platform, problem_id)
    return (
        Path(repo_root)
        / "problems"
        / normalized_platform
        / canonical_problem_id(normalized_platform, normalized_id)
    )


def record_acceptance(
    repo_root: str | Path,
    *,
    platform: str,
    problem_id: str,
    language: str,
    event_date: date,
    time_complexity: str,
    space_complexity: str,
    reflection: str | None = None,
) -> Path:
    """Record a platform-confirmed AC event and advance a draft to accepted."""

    directory = problem_directory(repo_root, platform, problem_id)
    metadata_path = directory / "problem.toml"
    problem = load_problem(metadata_path)
    normalized_language = normalize_language(language)
    time_complexity = time_complexity.strip()
    space_complexity = space_complexity.strip()
    if not time_complexity:
        raise ValueError("time_complexity must not be empty")
    if not space_complexity:
        raise ValueError("space_complexity must not be empty")
    if reflection is not None:
        reflection = reflection.strip()
        if not reflection:
            raise ValueError("reflection must not be empty when provided")
    solution_languages = {solution.language for solution in problem.solutions}
    if normalized_language not in solution_languages:
        raise ValueError(
            f"language {normalized_language!r} must match a solution listed in problem.toml"
        )
    solution_path = directory / LANGUAGE_FILES[normalized_language]
    if not has_solution_content(solution_path):
        raise ValueError(f"accepted solution is missing or still a placeholder: {solution_path}")
    if any(
        event.event_type == "ac"
        and event.date == event_date
        and event.language == normalized_language
        for event in problem.activity
    ):
        raise ValueError(
            f"AC event already exists for {normalized_language!r} on {event_date.isoformat()}"
        )

    def mutate(document: TOMLDocument) -> None:
        if problem.state == "draft":
            document["state"] = "accepted"
        for solution in document.get("solutions", []):
            if solution.get("language") == normalized_language:
                solution["time_complexity"] = time_complexity
                solution["space_complexity"] = space_complexity
                break
        _append_activity(
            document,
            event_type="ac",
            event_date=event_date,
            language=normalized_language,
            reflection=reflection,
        )

    _mutate_and_validate(metadata_path, directory, mutate)
    return directory


def record_documentation(
    repo_root: str | Path,
    *,
    platform: str,
    problem_id: str,
    event_date: date,
) -> Path:
    """Record a completed bilingual note and advance accepted to documented."""

    directory = problem_directory(repo_root, platform, problem_id)
    metadata_path = directory / "problem.toml"
    problem = load_problem(metadata_path)
    if problem.state not in {"accepted", "documented"}:
        raise ValueError("documentation requires a previously accepted problem")
    if any(event.event_type == "note" and event.date == event_date for event in problem.activity):
        raise ValueError(f"note event already exists on {event_date.isoformat()}")

    def mutate(document: TOMLDocument) -> None:
        document["state"] = "documented"
        _append_activity(document, event_type="note", event_date=event_date)

    _mutate_and_validate(metadata_path, directory, mutate)
    return directory


def _append_activity(
    document: TOMLDocument,
    *,
    event_type: str,
    event_date: date,
    language: str | None = None,
    reflection: str | None = None,
) -> None:
    activity = document.get("activity")
    if activity is None:
        activity = tomlkit.aot()
        document["activity"] = activity
    event = tomlkit.table()
    event.add("type", event_type)
    event.add("date", event_date)
    if language is not None:
        event.add("language", language)
    if reflection is not None:
        event.add("reflection", reflection)
    activity.append(event)


def _mutate_and_validate(
    metadata_path: Path,
    directory: Path,
    mutate: Callable[[TOMLDocument], None],
) -> None:
    original = metadata_path.read_text(encoding="utf-8")
    document = tomlkit.parse(original)
    mutate(document)
    _atomic_write(metadata_path, tomlkit.dumps(document))
    issues = validate_problem_dir(directory)
    if not issues:
        return
    _atomic_write(metadata_path, original)
    details = "; ".join(f"[{issue.code}] {issue.message}" for issue in issues)
    raise ValueError(f"lifecycle transition failed validation: {details}")


def _atomic_write(path: Path, content: str) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
