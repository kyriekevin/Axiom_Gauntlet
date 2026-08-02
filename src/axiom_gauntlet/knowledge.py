"""Knowledge-topic scaffolding, lifecycle transitions, validation, and indexes."""

from __future__ import annotations

import json
import os
import re
import stat
import tempfile
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from string import Template
from typing import Any

import tomlkit
from tomlkit import TOMLDocument

TOPIC_SCHEMA_VERSION = 1
TOPIC_STATES = frozenset({"draft", "documented"})
_PATH_PART_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_TAG_RE = _PATH_PART_RE
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_PLACEHOLDER_RE = re.compile(r"\bTODO\b|TBD|待补充|填写|在这里", re.IGNORECASE)
REQUIRED_SECTIONS = {
    "README.md": (
        "Overview",
        "Recognition",
        "Model",
        "Derivation",
        "Variants",
        "Examples",
        "Review log",
    ),
    "README_zh-CN.md": (
        "概览",
        "识别信号",
        "建模",
        "推导",
        "变体",
        "例题",
        "复习记录",
    ),
}


class TopicMetadataError(ValueError):
    """Raised when a topic manifest cannot be decoded."""

    def __init__(self, messages: Sequence[str]):
        self.messages = tuple(messages)
        super().__init__("; ".join(self.messages))


@dataclass(frozen=True)
class TopicExample:
    uid: str
    role: str


@dataclass(frozen=True)
class TopicActivity:
    event_type: str
    date: date
    result: str | None = None


@dataclass(frozen=True)
class KnowledgeTopic:
    version: int
    path: str
    title: str
    title_zh_cn: str
    state: str
    tags: tuple[str, ...]
    links: tuple[str, ...]
    examples: tuple[TopicExample, ...]
    activity: tuple[TopicActivity, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> KnowledgeTopic:
        errors: list[str] = []
        allowed = {
            "version",
            "path",
            "title",
            "title_zh_cn",
            "state",
            "tags",
            "links",
            "examples",
            "activity",
        }
        unknown = sorted(set(raw) - allowed)
        if unknown:
            errors.append(f"top level contains unknown keys: {', '.join(unknown)}")

        version = _integer(raw, "version", errors)
        topic_path = _string(raw, "path", errors)
        title = _string(raw, "title", errors)
        title_zh_cn = _string(raw, "title_zh_cn", errors)
        state = _string(raw, "state", errors)
        tags = _string_list(raw, "tags", errors)
        links = _string_list(raw, "links", errors)

        examples: list[TopicExample] = []
        raw_examples = raw.get("examples", [])
        if not isinstance(raw_examples, list):
            errors.append("examples must be an array of tables")
        else:
            for index, item in enumerate(raw_examples):
                label = f"examples[{index}]"
                if not isinstance(item, Mapping):
                    errors.append(f"{label} must be a table")
                    continue
                unknown = sorted(set(item) - {"uid", "role"})
                if unknown:
                    errors.append(f"{label} contains unknown keys: {', '.join(unknown)}")
                examples.append(
                    TopicExample(
                        uid=_string(item, "uid", errors, f"{label}."),
                        role=_string(item, "role", errors, f"{label}."),
                    )
                )

        activity: list[TopicActivity] = []
        raw_activity = raw.get("activity", [])
        if not isinstance(raw_activity, list):
            errors.append("activity must be an array of tables")
        else:
            for index, item in enumerate(raw_activity):
                label = f"activity[{index}]"
                if not isinstance(item, Mapping):
                    errors.append(f"{label} must be a table")
                    continue
                unknown = sorted(set(item) - {"type", "date", "result"})
                if unknown:
                    errors.append(f"{label} contains unknown keys: {', '.join(unknown)}")
                activity.append(
                    TopicActivity(
                        event_type=_string(item, "type", errors, f"{label}."),
                        date=_date(item.get("date"), f"{label}.date", errors),
                        result=_optional_string(item, "result", errors, f"{label}."),
                    )
                )

        if errors:
            raise TopicMetadataError(errors)
        return cls(
            version=version,
            path=topic_path,
            title=title,
            title_zh_cn=title_zh_cn,
            state=state,
            tags=tuple(tags),
            links=tuple(links),
            examples=tuple(examples),
            activity=tuple(activity),
        )


def normalize_topic_path(value: str) -> str:
    raw = value.strip().strip("/")
    pure = PurePosixPath(raw)
    if not raw or pure.is_absolute() or len(pure.parts) < 2:
        raise ValueError("knowledge path must contain at least two lowercase kebab-case parts")
    if any(part in {".", ".."} or not _PATH_PART_RE.fullmatch(part) for part in pure.parts):
        raise ValueError("knowledge path must use lowercase kebab-case parts")
    return pure.as_posix()


def load_topic(path: str | Path) -> KnowledgeTopic:
    manifest = Path(path)
    try:
        with manifest.open("rb") as stream:
            raw = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise TopicMetadataError((f"cannot read TOML: {error}",)) from error
    return KnowledgeTopic.from_mapping(raw)


def create_topic(
    repo_root: str | Path,
    *,
    topic_path: str,
    title: str,
    title_zh_cn: str,
    tags: Iterable[str] = (),
    links: Iterable[str] = (),
    examples: Iterable[tuple[str, str]] = (),
) -> Path:
    root = Path(repo_root)
    normalized_path = normalize_topic_path(topic_path)
    title = title.strip()
    title_zh_cn = title_zh_cn.strip()
    if not title or not title_zh_cn:
        raise ValueError("both English and Simplified Chinese titles are required")
    tag_list = _normalize_values(tags, "tag")
    link_list = tuple(normalize_topic_path(link) for link in links)
    if len(set(link_list)) != len(link_list):
        raise ValueError("duplicate knowledge link")
    example_list = tuple((uid.strip(), role.strip()) for uid, role in examples)
    if any(not uid or not role for uid, role in example_list):
        raise ValueError("knowledge examples require non-empty uid and role")
    if len({uid for uid, _ in example_list}) != len(example_list):
        raise ValueError("duplicate example uid")

    template_dir = root / "templates" / "knowledge"
    target = root / "knowledge" / normalized_path
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"knowledge topic already exists: {target}")
    target.mkdir(parents=True, exist_ok=True)

    example_tables = "\n\n".join(
        "\n".join(
            (
                "[[examples]]",
                f"uid = {json.dumps(uid)}",
                f"role = {json.dumps(role)}",
            )
        )
        for uid, role in example_list
    )
    metadata = Template((template_dir / "topic.toml").read_text(encoding="utf-8")).substitute(
        path=json.dumps(normalized_path),
        title=json.dumps(title, ensure_ascii=False),
        title_zh_cn=json.dumps(title_zh_cn, ensure_ascii=False),
        tags=_toml_array(tag_list),
        links=_toml_array(link_list),
        examples=example_tables,
    )
    values = {"title": title, "title_zh_cn": title_zh_cn}
    readme = Template((template_dir / "README.md").read_text(encoding="utf-8")).substitute(values)
    readme_zh = Template((template_dir / "README_zh-CN.md").read_text(encoding="utf-8")).substitute(
        values
    )
    (target / "topic.toml").write_text(metadata, encoding="utf-8", newline="\n")
    (target / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    (target / "README_zh-CN.md").write_text(readme_zh, encoding="utf-8", newline="\n")
    return target


def document_topic(repo_root: str | Path, topic_path: str, event_date: date) -> Path:
    root = Path(repo_root)
    directory = root / "knowledge" / normalize_topic_path(topic_path)
    manifest = directory / "topic.toml"
    topic = load_topic(manifest)
    if any(event.event_type == "note" and event.date == event_date for event in topic.activity):
        raise ValueError(f"note event already exists on {event_date.isoformat()}")

    def mutate(document: TOMLDocument) -> None:
        document["state"] = "documented"
        _append_activity(document, "note", event_date)

    _mutate_topic(root, manifest, directory, mutate)
    return directory


def review_topic(repo_root: str | Path, topic_path: str, event_date: date, result: str) -> Path:
    root = Path(repo_root)
    directory = root / "knowledge" / normalize_topic_path(topic_path)
    manifest = directory / "topic.toml"
    topic = load_topic(manifest)
    if topic.state != "documented":
        raise ValueError("knowledge review requires a documented topic")
    result = result.strip().lower()
    if result not in {"pass", "fail"}:
        raise ValueError("review result must be pass or fail")
    if any(event.event_type == "review" and event.date == event_date for event in topic.activity):
        raise ValueError(f"review event already exists on {event_date.isoformat()}")

    def mutate(document: TOMLDocument) -> None:
        _append_activity(document, "review", event_date, result)

    _mutate_topic(root, manifest, directory, mutate)
    return directory


def validate_topic_dir(directory: Path) -> list[str]:
    issues: list[str] = []
    manifest = directory / "topic.toml"
    try:
        topic = load_topic(manifest)
    except TopicMetadataError as error:
        return [f"{manifest}: {message}" for message in error.messages]
    try:
        normalized = normalize_topic_path(topic.path)
    except ValueError as error:
        issues.append(f"{manifest}: {error}")
        normalized = ""
    expected = Path(*normalized.split("/")) if normalized else None
    if expected is not None and tuple(directory.parts[-len(expected.parts) :]) != expected.parts:
        issues.append(f"{manifest}: path must match knowledge/{normalized}")
    if topic.version != TOPIC_SCHEMA_VERSION:
        issues.append(f"{manifest}: version must be {TOPIC_SCHEMA_VERSION}")
    if topic.state not in TOPIC_STATES:
        issues.append(f"{manifest}: state must be draft or documented")
    if len(set(topic.tags)) != len(topic.tags) or any(
        not _TAG_RE.fullmatch(tag) for tag in topic.tags
    ):
        issues.append(f"{manifest}: tags must be unique lowercase kebab-case values")
    if len(set(topic.links)) != len(topic.links):
        issues.append(f"{manifest}: links must be unique")
    for link in topic.links:
        try:
            normalize_topic_path(link)
        except ValueError as error:
            issues.append(f"{manifest}: invalid link {link!r}: {error}")
    if len({example.uid for example in topic.examples}) != len(topic.examples):
        issues.append(f"{manifest}: example uids must be unique")
    activity_types: set[str] = set()
    for event in topic.activity:
        activity_types.add(event.event_type)
        if event.event_type not in {"note", "review"}:
            issues.append(f"{manifest}: activity type must be note or review")
        if event.event_type == "review" and event.result not in {"pass", "fail"}:
            issues.append(f"{manifest}: review activity requires result pass or fail")
    for filename in REQUIRED_SECTIONS:
        readme = directory / filename
        if not readme.is_file():
            issues.append(f"{readme}: file is required")
        elif topic.state == "documented":
            issues.extend(_validate_sections(readme, REQUIRED_SECTIONS[filename]))
    if topic.state == "documented" and "note" not in activity_types:
        issues.append(f"{manifest}: documented topic requires a note activity")
    if topic.state == "draft" and activity_types:
        issues.append(f"{manifest}: draft topic cannot have activity")
    return sorted(issues)


def discover_topics(root: Path) -> tuple[Path, ...]:
    return tuple(sorted((root / "knowledge").glob("**/topic.toml")))


def render_indexes(root: Path, *, check: bool = False) -> tuple[Path, ...]:
    knowledge_root = root / "knowledge"
    topics = [load_topic(path) for path in discover_topics(root)]
    english = ["# Knowledge Index", ""]
    chinese = ["# 知识索引", ""]
    if topics:
        for topic in sorted(topics, key=lambda item: item.path):
            english.append(f"- [{topic.title}]({topic.path}/README.md) — `{topic.state}`")
            chinese.append(
                f"- [{topic.title_zh_cn}]({topic.path}/README_zh-CN.md) — `{topic.state}`"
            )
    else:
        english.append("No knowledge topics yet.")
        chinese.append("暂时还没有知识主题。")

    events = sorted(
        (
            event.date,
            topic.path,
            event.event_type,
            event.result,
        )
        for topic in topics
        for event in topic.activity
    )
    log = ["# Knowledge Activity Log", ""]
    if events:
        for event_date, path, event_type, result in events:
            suffix = f" ({result})" if result else ""
            log.append(
                f"- {event_date.isoformat()} — `{event_type}` — [{path}]({path}/README.md){suffix}"
            )
    else:
        log.append("No knowledge activity yet.")

    outputs = {
        knowledge_root / "INDEX.md": "\n".join(english) + "\n",
        knowledge_root / "INDEX_zh-CN.md": "\n".join(chinese) + "\n",
        knowledge_root / "LOG.md": "\n".join(log) + "\n",
    }
    changed = tuple(path for path, content in outputs.items() if _different(path, content))
    if not check:
        knowledge_root.mkdir(parents=True, exist_ok=True)
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    return changed


def _validate_sections(path: Path, required: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    matches = list(_HEADING_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[match.end() : end].strip()
    issues: list[str] = []
    for heading in required:
        content = _COMMENT_RE.sub("", sections.get(heading, "")).strip()
        if not content or _PLACEHOLDER_RE.search(content):
            issues.append(f"{path}: section '## {heading}' is missing or incomplete")
    return issues


def _mutate_topic(root: Path, manifest: Path, directory: Path, mutate: Any) -> None:
    original = manifest.read_text(encoding="utf-8")
    document = tomlkit.parse(original)
    mutate(document)
    _atomic_write(manifest, tomlkit.dumps(document))
    issues = validate_topic_dir(directory)
    if not issues:
        from .validate import validate_repository

        reference_codes = {
            "knowledge.duplicate-path",
            "knowledge.example-missing",
            "knowledge.link-missing",
        }
        issues.extend(
            str(issue)
            for issue in validate_repository(root)
            if issue.path == manifest and issue.code in reference_codes
        )
    if issues:
        _atomic_write(manifest, original)
        raise ValueError("knowledge transition failed validation: " + "; ".join(issues))


def _append_activity(
    document: TOMLDocument, event_type: str, event_date: date, result: str | None = None
) -> None:
    activity = document.get("activity")
    if activity is None:
        activity = tomlkit.aot()
        document["activity"] = activity
    event = tomlkit.table()
    event.add("type", event_type)
    event.add("date", event_date)
    if result is not None:
        event.add("result", result)
    activity.append(event)


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


def _normalize_values(values: Iterable[str], label: str) -> tuple[str, ...]:
    result = tuple(value.strip() for value in values)
    if any(not _TAG_RE.fullmatch(value) for value in result):
        raise ValueError(f"{label} must use lowercase kebab-case")
    if len(set(result)) != len(result):
        raise ValueError(f"duplicate {label}")
    return result


def _different(path: Path, content: str) -> bool:
    try:
        return path.read_text(encoding="utf-8") != content
    except OSError:
        return True


def _toml_array(values: Iterable[str]) -> str:
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def _string(mapping: Mapping[str, Any], key: str, errors: list[str], prefix: str = "") -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}{key} must be a non-empty string")
        return ""
    return value.strip()


def _optional_string(
    mapping: Mapping[str, Any], key: str, errors: list[str], prefix: str = ""
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
