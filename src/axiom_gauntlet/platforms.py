"""Data-driven online-judge platform registry."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import files
from types import MappingProxyType
from typing import Any

REGISTRY_VERSION = 1
ID_STRATEGIES = frozenset({"positive-integer", "contest-index", "slug"})
DIFFICULTY_SCHEMES = frozenset({"level", "rating", "unknown"})
MAX_COVERAGE_LABEL_LENGTH = 14
_PLATFORM_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PlatformRegistryError(ValueError):
    """Raised when the bundled platform registry is invalid."""


@dataclass(frozen=True)
class PlatformSpec:
    slug: str
    label: str
    coverage_label: str
    id_strategy: str
    default_difficulty_scheme: str
    canonical_width: int = 0
    coverage_categories: tuple[str, ...] = ()


def _require_string(raw: Mapping[str, Any], key: str, slug: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PlatformRegistryError(f"platform {slug!r} requires a non-empty {key}")
    return value.strip()


def parse_platform_registry(raw: Mapping[str, Any]) -> Mapping[str, PlatformSpec]:
    """Validate and decode a platform-registry mapping."""

    unknown_top_level = sorted(set(raw) - {"version", "platforms"})
    if unknown_top_level:
        raise PlatformRegistryError(
            f"platform registry contains unknown keys: {', '.join(unknown_top_level)}"
        )
    version = raw.get("version")
    if isinstance(version, bool) or version != REGISTRY_VERSION:
        raise PlatformRegistryError(f"platform registry version must be {REGISTRY_VERSION}")
    raw_platforms = raw.get("platforms")
    if not isinstance(raw_platforms, Mapping) or not raw_platforms:
        raise PlatformRegistryError("platform registry requires a non-empty platforms table")

    specs: dict[str, PlatformSpec] = {}
    for slug, raw_spec in raw_platforms.items():
        if not isinstance(slug, str) or _PLATFORM_SLUG_RE.fullmatch(slug) is None:
            raise PlatformRegistryError(f"invalid platform slug: {slug!r}")
        if not isinstance(raw_spec, Mapping):
            raise PlatformRegistryError(f"platform {slug!r} must be a table")
        unknown = sorted(
            set(raw_spec)
            - {
                "label",
                "coverage_label",
                "id_strategy",
                "canonical_width",
                "default_difficulty_scheme",
                "coverage_categories",
            }
        )
        if unknown:
            raise PlatformRegistryError(
                f"platform {slug!r} contains unknown keys: {', '.join(unknown)}"
            )

        strategy = _require_string(raw_spec, "id_strategy", slug)
        if strategy not in ID_STRATEGIES:
            choices = ", ".join(sorted(ID_STRATEGIES))
            raise PlatformRegistryError(f"platform {slug!r} id_strategy must be one of: {choices}")
        width = raw_spec.get("canonical_width", 0)
        if isinstance(width, bool) or not isinstance(width, int) or width < 0:
            raise PlatformRegistryError(
                f"platform {slug!r} canonical_width must be a non-negative integer"
            )
        if width and strategy != "positive-integer":
            raise PlatformRegistryError(
                f"platform {slug!r} canonical_width requires positive-integer IDs"
            )

        label = _require_string(raw_spec, "label", slug)
        raw_coverage_label = raw_spec.get("coverage_label", label)
        if not isinstance(raw_coverage_label, str) or not raw_coverage_label.strip():
            raise PlatformRegistryError(
                f"platform {slug!r} coverage_label must be a non-empty string"
            )
        coverage_label = raw_coverage_label.strip()
        if len(coverage_label) > MAX_COVERAGE_LABEL_LENGTH:
            raise PlatformRegistryError(
                f"platform {slug!r} coverage_label must be at most "
                f"{MAX_COVERAGE_LABEL_LENGTH} characters"
            )

        difficulty_scheme = _require_string(raw_spec, "default_difficulty_scheme", slug).lower()
        if difficulty_scheme not in DIFFICULTY_SCHEMES:
            choices = ", ".join(sorted(DIFFICULTY_SCHEMES))
            raise PlatformRegistryError(
                f"platform {slug!r} default_difficulty_scheme must be one of: {choices}"
            )

        raw_categories = raw_spec.get("coverage_categories", [])
        if not isinstance(raw_categories, list):
            raise PlatformRegistryError(
                f"platform {slug!r} coverage_categories must be an array of kebab-case strings"
            )
        categories: list[str] = []
        for category in raw_categories:
            if not isinstance(category, str) or _PLATFORM_SLUG_RE.fullmatch(category) is None:
                raise PlatformRegistryError(
                    f"platform {slug!r} coverage_categories must contain kebab-case strings"
                )
            if category in categories:
                raise PlatformRegistryError(
                    f"platform {slug!r} contains duplicate coverage category {category!r}"
                )
            categories.append(category)

        specs[slug] = PlatformSpec(
            slug=slug,
            label=label,
            coverage_label=coverage_label,
            id_strategy=strategy,
            default_difficulty_scheme=difficulty_scheme,
            canonical_width=width,
            coverage_categories=tuple(categories),
        )
    return MappingProxyType(specs)


def _load_registry() -> Mapping[str, PlatformSpec]:
    resource = files("axiom_gauntlet").joinpath("platforms.toml")
    try:
        with resource.open("rb") as stream:
            raw = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise PlatformRegistryError(f"cannot read platform registry: {error}") from error
    return parse_platform_registry(raw)


PLATFORM_SPECS = _load_registry()
PLATFORMS = frozenset(PLATFORM_SPECS)


def platform_spec(platform: str) -> PlatformSpec:
    """Return the registered specification for *platform*."""

    try:
        return PLATFORM_SPECS[platform]
    except KeyError as error:
        choices = ", ".join(sorted(PLATFORMS))
        raise ValueError(f"unsupported platform {platform!r}; choose one of {choices}") from error


def normalize_platform_problem_id(spec: PlatformSpec, problem_id: str) -> str:
    """Normalize a source problem ID according to a registered strategy."""

    raw = str(problem_id).strip()
    if spec.id_strategy == "positive-integer":
        if re.fullmatch(r"\d+", raw) is None:
            raise ValueError(f"{spec.slug} problem_id must contain only digits")
        number = int(raw)
        if number <= 0:
            raise ValueError(f"{spec.slug} problem_id must be greater than zero")
        return str(number)

    if spec.id_strategy == "contest-index":
        match = re.fullmatch(r"0*(\d+)([A-Za-z][A-Za-z0-9]*)", raw)
        if match is None:
            raise ValueError(
                f"{spec.slug} problem_id must be a contest number followed by an index"
            )
        contest = int(match.group(1))
        if contest <= 0:
            raise ValueError(f"{spec.slug} contest number must be greater than zero")
        return f"{contest}{match.group(2).upper()}"

    if re.fullmatch(r"[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*", raw) is None:
        raise ValueError(
            f"{spec.slug} problem_id must be a filesystem-safe slug containing letters and digits"
        )
    return raw


def canonical_platform_problem_id(spec: PlatformSpec, problem_id: str) -> str:
    """Return the stable directory ID for *problem_id*."""

    normalized = normalize_platform_problem_id(spec, problem_id)
    return normalized.zfill(spec.canonical_width)
