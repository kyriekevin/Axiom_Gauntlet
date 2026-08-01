"""Repository and per-problem validation."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from .model import (
    LANGUAGE_FILES,
    NORMALIZED_DIFFICULTIES,
    PLATFORMS,
    SCHEMA_VERSION,
    STATES,
    MetadataError,
    Problem,
    canonical_problem_id,
    expected_uid,
    load_problem,
    normalize_language,
    normalize_problem_id,
)

REQUIRED_DOCUMENTED_SECTIONS = {
    "README.md": (
        "Core insight",
        "Approach",
        "Why it works",
        "Complexity",
        "Pitfalls",
        "Review log",
    ),
    "README_zh-CN.md": (
        "核心洞察",
        "解题思路",
        "正确性说明",
        "复杂度",
        "易错点",
        "复习记录",
    ),
}
_TAG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_PLACEHOLDER_RE = re.compile(
    r"\bTODO\b|TBD|待补充|填写|在这里|paste the accepted solution",
    re.IGNORECASE,
)


@dataclass(frozen=True, order=True)
class ValidationIssue:
    path: Path
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


class RepositoryValidationError(ValueError):
    def __init__(self, issues: Iterable[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__("\n".join(str(issue) for issue in self.issues))


def validate_problem_dir(problem_dir: str | Path) -> list[ValidationIssue]:
    """Validate one ``problems/<platform>/<canonical-id>`` directory."""

    directory = Path(problem_dir)
    issues: list[ValidationIssue] = []
    metadata_path = directory / "problem.toml"
    readme_paths = tuple(directory / name for name in REQUIRED_DOCUMENTED_SECTIONS)

    if not metadata_path.is_file():
        issues.append(
            ValidationIssue(metadata_path, "metadata.missing", "problem.toml is required")
        )
        return issues

    try:
        problem = load_problem(metadata_path)
    except MetadataError as error:
        issues.extend(
            ValidationIssue(metadata_path, "metadata.invalid", message)
            for message in error.messages
        )
        return sorted(issues)

    _validate_identity(directory, problem, issues)
    _validate_metadata(metadata_path, problem, issues)
    existing_solutions = _validate_solutions(directory, problem, issues)
    activity_types, ac_languages = _validate_activity(metadata_path, problem, issues)

    for readme_path in readme_paths:
        if not readme_path.is_file():
            issues.append(
                ValidationIssue(
                    readme_path,
                    "readme.missing",
                    f"{readme_path.name} is required",
                )
            )
        elif problem.state == "documented":
            _validate_documented_readme(
                readme_path,
                REQUIRED_DOCUMENTED_SECTIONS[readme_path.name],
                issues,
            )

    if problem.state in {"accepted", "documented"}:
        if "ac" not in activity_types:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.ac-required",
                    f"state {problem.state!r} requires at least one AC activity event",
                )
            )
        if not problem.solutions:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.solution-required",
                    f"state {problem.state!r} requires at least one listed solution",
                )
            )
        elif not existing_solutions:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.solution-required",
                    f"state {problem.state!r} requires an existing solution file",
                )
            )
        elif not any(_has_solution_content(path) for path in existing_solutions):
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.solution-placeholder",
                    f"state {problem.state!r} requires non-placeholder solution code",
                )
            )
        elif ac_languages and not any(
            _has_solution_content(directory / LANGUAGE_FILES[language]) for language in ac_languages
        ):
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.solution-placeholder",
                    f"state {problem.state!r} requires non-placeholder code for an AC language",
                )
            )
        if problem.state == "documented" and "note" not in activity_types:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.note-required",
                    "state 'documented' requires at least one note activity event",
                )
            )
    elif problem.state == "draft":
        if "ac" in activity_types:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.ac-in-draft",
                    "a problem with an AC event must advance to accepted or documented",
                )
            )
        if "review" in activity_types:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "state.review-in-draft",
                    "a review requires a previously accepted problem",
                )
            )

    return sorted(issues)


def validate_repository(repo_root: str | Path) -> list[ValidationIssue]:
    """Validate every supported platform directory in a repository."""

    root = Path(repo_root)
    problems_root = root / "problems"
    issues: list[ValidationIssue] = []
    seen_uids: dict[str, Path] = {}

    if not problems_root.is_dir():
        return [
            ValidationIssue(
                problems_root, "repository.problems-missing", "problems directory is required"
            )
        ]

    for child in sorted(problems_root.iterdir(), key=lambda item: item.name):
        if child.name.startswith("."):
            continue
        if not child.is_dir() or child.name not in PLATFORMS:
            issues.append(
                ValidationIssue(
                    child,
                    "repository.unknown-platform",
                    f"only these platform directories are allowed: {', '.join(sorted(PLATFORMS))}",
                )
            )

    for platform in sorted(PLATFORMS):
        platform_dir = problems_root / platform
        if not platform_dir.is_dir():
            issues.append(
                ValidationIssue(
                    platform_dir,
                    "repository.platform-missing",
                    f"platform directory {platform!r} is required",
                )
            )
            continue

        for problem_dir in sorted(platform_dir.iterdir(), key=lambda item: item.name):
            if problem_dir.name.startswith("."):
                continue
            if not problem_dir.is_dir():
                issues.append(
                    ValidationIssue(
                        problem_dir,
                        "repository.unexpected-file",
                        "platform directories may contain only problem directories and .gitkeep",
                    )
                )
                continue

            problem_issues = validate_problem_dir(problem_dir)
            issues.extend(problem_issues)
            try:
                problem = load_problem(problem_dir / "problem.toml")
            except MetadataError:
                continue
            previous = seen_uids.get(problem.uid)
            if previous is not None and previous != problem_dir:
                issues.append(
                    ValidationIssue(
                        problem_dir / "problem.toml",
                        "metadata.duplicate-uid",
                        f"uid {problem.uid!r} is already used by {previous}",
                    )
                )
            else:
                seen_uids[problem.uid] = problem_dir

    return sorted(issues)


def raise_for_issues(issues: Iterable[ValidationIssue]) -> None:
    collected = tuple(issues)
    if collected:
        raise RepositoryValidationError(collected)


def _validate_identity(directory: Path, problem: Problem, issues: list[ValidationIssue]) -> None:
    metadata_path = directory / "problem.toml"
    if directory.parent.parent.name != "problems":
        issues.append(
            ValidationIssue(
                directory,
                "path.layout",
                "problem must live at problems/<platform>/<canonical-id>",
            )
        )
    if problem.platform not in PLATFORMS:
        issues.append(
            ValidationIssue(
                metadata_path,
                "platform.unsupported",
                f"platform must be one of {', '.join(sorted(PLATFORMS))}",
            )
        )
        return

    try:
        normalized_id = normalize_problem_id(problem.platform, problem.problem_id)
        canonical_id = canonical_problem_id(problem.platform, problem.problem_id)
    except ValueError as error:
        issues.append(ValidationIssue(metadata_path, "problem-id.invalid", str(error)))
        return

    if problem.problem_id != normalized_id:
        issues.append(
            ValidationIssue(
                metadata_path,
                "problem-id.not-normalized",
                f"problem_id must be {normalized_id!r}",
            )
        )
    if directory.parent.name != problem.platform:
        issues.append(
            ValidationIssue(
                directory,
                "path.platform-mismatch",
                f"parent directory must be {problem.platform!r}",
            )
        )
    if directory.name != canonical_id:
        issues.append(
            ValidationIssue(
                directory,
                "path.id-mismatch",
                f"directory name must be canonical ID {canonical_id!r}",
            )
        )
    wanted_uid = expected_uid(problem.platform, problem.problem_id)
    if problem.uid != wanted_uid:
        issues.append(
            ValidationIssue(
                metadata_path,
                "uid.mismatch",
                f"uid must be {wanted_uid!r}",
            )
        )


def _validate_metadata(
    metadata_path: Path, problem: Problem, issues: list[ValidationIssue]
) -> None:
    if problem.version != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                metadata_path,
                "version.unsupported",
                f"version must be {SCHEMA_VERSION}",
            )
        )
    if problem.state not in STATES:
        issues.append(
            ValidationIssue(
                metadata_path,
                "state.invalid",
                f"state must be one of {', '.join(sorted(STATES))}",
            )
        )

    parsed_url = urlsplit(problem.url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        issues.append(
            ValidationIssue(
                metadata_path,
                "url.invalid",
                "url must be an absolute HTTP or HTTPS URL",
            )
        )

    seen_tags: set[str] = set()
    for tag in problem.tags:
        if not _TAG_RE.fullmatch(tag):
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "tag.invalid",
                    f"tag {tag!r} must use lowercase kebab-case",
                )
            )
        if tag in seen_tags:
            issues.append(ValidationIssue(metadata_path, "tag.duplicate", f"duplicate tag {tag!r}"))
        seen_tags.add(tag)

    difficulty = problem.difficulty
    if difficulty.scheme not in {"level", "rating", "unknown"}:
        issues.append(
            ValidationIssue(
                metadata_path,
                "difficulty.scheme",
                "difficulty.scheme must be level, rating, or unknown",
            )
        )
    if difficulty.scheme == "rating" and (
        isinstance(difficulty.value, bool)
        or not isinstance(difficulty.value, int)
        or difficulty.value <= 0
    ):
        issues.append(
            ValidationIssue(
                metadata_path,
                "difficulty.rating",
                "a rating difficulty requires a positive integer value",
            )
        )
    if difficulty.normalized not in NORMALIZED_DIFFICULTIES:
        issues.append(
            ValidationIssue(
                metadata_path,
                "difficulty.normalized",
                "difficulty.normalized must be easy, medium, hard, or unknown",
            )
        )


def _validate_solutions(
    directory: Path, problem: Problem, issues: list[ValidationIssue]
) -> list[Path]:
    metadata_path = directory / "problem.toml"
    existing: list[Path] = []
    seen_files: set[str] = set()
    for solution in problem.solutions:
        pure_path = PurePosixPath(solution.file)
        if (
            pure_path.is_absolute()
            or len(pure_path.parts) != 1
            or "\\" in solution.file
            or solution.file in {".", ".."}
        ):
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "solution.path",
                    f"solution file must be a basename, got {solution.file!r}",
                )
            )
            continue
        if solution.file in seen_files:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "solution.duplicate",
                    f"duplicate solution file {solution.file!r}",
                )
            )
        seen_files.add(solution.file)

        try:
            language = normalize_language(solution.language)
        except ValueError as error:
            issues.append(ValidationIssue(metadata_path, "solution.language", str(error)))
            continue
        if language != solution.language:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "solution.language-alias",
                    f"metadata must use canonical language {language!r}",
                )
            )
        expected_file = LANGUAGE_FILES[language]
        if solution.file != expected_file:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "solution.filename",
                    f"language {language!r} must use {expected_file!r}",
                )
            )

        solution_path = directory / solution.file
        if not solution_path.is_file():
            issues.append(
                ValidationIssue(
                    solution_path,
                    "solution.missing",
                    "listed solution file does not exist",
                )
            )
        else:
            existing.append(solution_path)
    return existing


def _validate_activity(
    metadata_path: Path, problem: Problem, issues: list[ValidationIssue]
) -> tuple[set[str], set[str]]:
    activity_types: set[str] = set()
    ac_languages: set[str] = set()
    solution_languages = {solution.language for solution in problem.solutions}
    for index, event in enumerate(problem.activity):
        label = f"activity[{index}]"
        if event.event_type not in {"ac", "note", "review"}:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "activity.type",
                    f"{label}.type must be ac, note, or review",
                )
            )
            continue
        activity_types.add(event.event_type)
        if event.language is not None:
            try:
                language = normalize_language(event.language)
            except ValueError as error:
                issues.append(ValidationIssue(metadata_path, "activity.language", str(error)))
                language = None
            if language is not None and language != event.language:
                issues.append(
                    ValidationIssue(
                        metadata_path,
                        "activity.language-alias",
                        f"{label}.language must use canonical value {language!r}",
                    )
                )
        else:
            language = None

        if event.event_type == "ac":
            if language is None:
                issues.append(
                    ValidationIssue(
                        metadata_path,
                        "activity.ac-language",
                        f"{label} AC event requires language",
                    )
                )
            elif language not in solution_languages:
                issues.append(
                    ValidationIssue(
                        metadata_path,
                        "activity.ac-solution",
                        f"{label} language must match a listed solution",
                    )
                )
            else:
                ac_languages.add(language)
        elif event.event_type == "review" and event.result not in {"pass", "fail"}:
            issues.append(
                ValidationIssue(
                    metadata_path,
                    "activity.review-result",
                    f"{label} review event requires result = pass or fail",
                )
            )
    return activity_types, ac_languages


def _validate_documented_readme(
    readme_path: Path,
    required_sections: tuple[str, ...],
    issues: list[ValidationIssue],
) -> None:
    try:
        text = readme_path.read_text(encoding="utf-8")
    except OSError as error:
        issues.append(ValidationIssue(readme_path, "readme.unreadable", str(error)))
        return

    sections = _markdown_sections(text)
    for heading in required_sections:
        content = sections.get(heading)
        if content is None:
            issues.append(
                ValidationIssue(
                    readme_path,
                    "readme.section-missing",
                    f"documented README requires section '## {heading}'",
                )
            )
            continue
        if not _section_is_complete(heading, content):
            issues.append(
                ValidationIssue(
                    readme_path,
                    "readme.section-incomplete",
                    f"section '## {heading}' still contains only placeholder content",
                )
            )


def _markdown_sections(text: str) -> dict[str, str]:
    matches = list(_HEADING_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[match.end() : end].strip()
    return sections


def _section_is_complete(heading: str, content: str) -> bool:
    without_comments = _COMMENT_RE.sub("", content).strip()
    if not without_comments or _PLACEHOLDER_RE.search(without_comments):
        return False
    if heading in {"Complexity", "复杂度"}:
        time_match = re.search(r"(?:时间|time)\s*[:：]\s*(\S.+)", without_comments, re.I)
        space_match = re.search(r"(?:空间|space)\s*[:：]\s*(\S.+)", without_comments, re.I)
        return time_match is not None and space_match is not None
    if heading in {"Review log", "复习记录"}:
        table_rows = [
            line
            for line in without_comments.splitlines()
            if line.strip().startswith("|")
            and "---" not in line
            and "Date" not in line
            and "日期" not in line
        ]
        return bool(table_rows)
    meaningful = re.findall(r"[A-Za-z0-9_\u3400-\u9fff]", without_comments)
    return len(meaningful) >= 6


def _has_solution_content(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    return bool(text.strip()) and not _PLACEHOLDER_RE.search(text)
