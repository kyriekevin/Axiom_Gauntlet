"""Compact, platform-aware practice coverage dashboard."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path

from .heatmap import discover
from .model import Problem, load_problem
from .platforms import PLATFORM_SPECS, PlatformSpec

_DIFFICULTY_ORDER = ("easy", "medium", "hard", "unknown")
_DIFFICULTY_LABELS = {
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
    "unknown": "Unknown",
}
_DIFFICULTY_COLORS = {
    "easy": "#34d399",
    "medium": "#fbbf24",
    "hard": "#fb7185",
    "unknown": "#64748b",
}
_RATING_BANDS = (
    ("≤999", 0, 999),
    ("1000–1199", 1000, 1199),
    ("1200–1399", 1200, 1399),
    ("1400–1599", 1400, 1599),
    ("1600+", 1600, None),
)
_RATING_COLORS = ("#94a3b8", "#34d399", "#22d3ee", "#a78bfa", "#fb7185")
_PLATFORM_COLORS = ("#fbbf24", "#22d3ee", "#a78bfa", "#34d399", "#fb7185")
_LANGUAGE_LABELS = {"cpp": "C++", "python": "Python", "go": "Go"}
_LANGUAGE_COLORS = {"C++": "#a78bfa", "Python": "#22d3ee", "Go": "#34d399"}

_WIDTH = 900
_CARD_GAP = 14
_CARD_WIDTH = 419
_CARD_HEIGHT = 146
_CARD_LEFT = 24
_CARD_TOP = 76


@dataclass(frozen=True)
class PlatformCoverage:
    spec: PlatformSpec
    accepted: int
    difficulty: dict[str, int]
    ratings: dict[str, int]
    categories: dict[str, int]


@dataclass(frozen=True)
class CoverageSnapshot:
    platforms: tuple[PlatformCoverage, ...]
    accepted_problems: int
    active_platforms: int
    languages: dict[str, int]


def _rating_value(problem: Problem) -> int | None:
    value = problem.difficulty.value
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
        return parsed if parsed > 0 else None
    return None


def _rating_band(value: int) -> str:
    for label, lower, upper in _RATING_BANDS:
        if value >= lower and (upper is None or value <= upper):
            return label
    raise AssertionError(f"rating {value} did not match a band")


def aggregate_coverage(root: str | Path) -> CoverageSnapshot:
    """Aggregate accepted problems by native platform facets and solution language."""

    root = Path(root)
    accepted_by_platform: Counter[str] = Counter()
    difficulty_by_platform: dict[str, Counter[str]] = {slug: Counter() for slug in PLATFORM_SPECS}
    ratings_by_platform: dict[str, Counter[str]] = {slug: Counter() for slug in PLATFORM_SPECS}
    categories_by_platform: dict[str, Counter[str]] = {slug: Counter() for slug in PLATFORM_SPECS}
    accepted_languages: set[tuple[str, str]] = set()

    for manifest in discover(root):
        problem = load_problem(manifest)
        accepted = [event for event in problem.activity if event.event_type.lower() == "ac"]
        if not accepted:
            continue
        spec = PLATFORM_SPECS.get(problem.platform)
        if spec is None:
            continue

        accepted_by_platform[problem.platform] += 1
        normalized = problem.difficulty.normalized.lower()
        difficulty_by_platform[problem.platform][
            normalized if normalized in _DIFFICULTY_ORDER else "unknown"
        ] += 1

        rating = _rating_value(problem)
        if rating is not None and problem.difficulty.scheme.lower() == "rating":
            ratings_by_platform[problem.platform][_rating_band(rating)] += 1

        for category in spec.coverage_categories:
            if category in problem.tags:
                categories_by_platform[problem.platform][category] += 1

        for event in accepted:
            if event.language is not None:
                accepted_languages.add((problem.uid, event.language))

    platforms = tuple(
        PlatformCoverage(
            spec=spec,
            accepted=accepted_by_platform[slug],
            difficulty=dict(difficulty_by_platform[slug]),
            ratings=dict(ratings_by_platform[slug]),
            categories=dict(categories_by_platform[slug]),
        )
        for slug, spec in PLATFORM_SPECS.items()
    )
    language_counts = Counter(
        _LANGUAGE_LABELS.get(language, language) for _, language in accepted_languages
    )
    return CoverageSnapshot(
        platforms=platforms,
        accepted_problems=sum(accepted_by_platform.values()),
        active_platforms=sum(1 for count in accepted_by_platform.values() if count > 0),
        languages=dict(sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))),
    )


def _category_label(category: str) -> str:
    if category == "nlp":
        return "NLP"
    return category.replace("-", " ").title()


def _profile_label(coverage: PlatformCoverage) -> str:
    if coverage.spec.default_difficulty_scheme == "rating":
        return "RATING PROFILE"
    if coverage.spec.coverage_categories:
        return "CATEGORY × LEVEL"
    return "DIFFICULTY PROFILE"


def _render_segments(
    lines: list[str],
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    values: tuple[tuple[str, int, str], ...],
    data_prefix: str,
) -> None:
    total = sum(value for _, value, _ in values)
    lines.append(
        f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="6" fill="#252d3d"/>'
    )
    if total <= 0:
        return
    cursor = float(x)
    nonzero = [(label, value, color) for label, value, color in values if value > 0]
    for index, (label, value, color) in enumerate(nonzero):
        segment_width = width * value / total
        if index == len(nonzero) - 1:
            segment_width = x + width - cursor
        lines.extend(
            (
                f'  <rect x="{cursor:.2f}" y="{y}" width="{segment_width:.2f}" '
                f'height="{height}" fill="{color}" data-profile="{data_prefix}" '
                f'data-segment="{escape(label)}" data-count="{value}">',
                f"    <title>{escape(label)}: {value}</title>",
                "  </rect>",
            )
        )
        cursor += segment_width


def _profile_values(coverage: PlatformCoverage) -> tuple[tuple[str, int, str], ...]:
    if coverage.spec.default_difficulty_scheme == "rating":
        return tuple(
            (label, coverage.ratings.get(label, 0), color)
            for (label, _, _), color in zip(_RATING_BANDS, _RATING_COLORS, strict=True)
        )
    return tuple(
        (_DIFFICULTY_LABELS[level], coverage.difficulty.get(level, 0), _DIFFICULTY_COLORS[level])
        for level in _DIFFICULTY_ORDER
    )


def _profile_summary(values: tuple[tuple[str, int, str], ...]) -> str:
    populated = [f"{label} {count}" for label, count, _ in values if count > 0]
    return " · ".join(populated)


def _render_platform_card(
    lines: list[str], coverage: PlatformCoverage, index: int, x: int, y: int
) -> None:
    accent = _PLATFORM_COLORS[index % len(_PLATFORM_COLORS)]
    lines.extend(
        (
            f'  <rect x="{x}" y="{y}" width="{_CARD_WIDTH}" height="{_CARD_HEIGHT}" '
            'rx="14" fill="#151b29" stroke="#293246"/>',
            f'  <circle cx="{x + 18}" cy="{y + 25}" r="5" fill="{accent}"/>',
            f'  <text x="{x + 31}" y="{y + 31}" fill="#f0f3f8" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            f'font-size="18" font-weight="700">{escape(coverage.spec.label)}</text>',
            f'  <text x="{x + _CARD_WIDTH - 18}" y="{y + 30}" text-anchor="end" '
            'fill="#a8b3cf" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="12">{coverage.accepted} ACCEPTED</text>',
            f'  <text x="{x + 18}" y="{y + 57}" fill="#64748b" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="10">{_profile_label(coverage)}</text>',
        )
    )

    if coverage.accepted <= 0:
        lines.append(
            f'  <text x="{x + 18}" y="{y + 94}" fill="#64748b" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            'font-size="14">No accepted problems yet</text>'
        )
        return

    values = _profile_values(coverage)
    _render_segments(
        lines,
        x=x + 18,
        y=y + 68,
        width=_CARD_WIDTH - 36,
        height=18,
        values=values,
        data_prefix=coverage.spec.slug,
    )
    summary = _profile_summary(values) or "Difficulty not recorded"
    lines.append(
        f'  <text x="{x + 18}" y="{y + 108}" fill="#b8c1d8" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'font-size="11">{escape(summary)}</text>'
    )

    categories = sorted(
        ((category, count) for category, count in coverage.categories.items() if count > 0),
        key=lambda item: (-item[1], item[0]),
    )[:3]
    if categories:
        category_summary = " · ".join(
            f"{_category_label(category)} {count}" for category, count in categories
        )
        lines.append(
            f'  <text x="{x + 18}" y="{y + 132}" fill="#64748b" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            f'font-size="11">{escape(category_summary)}</text>'
        )


def render_coverage_svg(snapshot: CoverageSnapshot) -> str:
    """Render a compact static SVG with platform-native coverage profiles."""

    columns = 2
    rows = max(1, math.ceil(len(snapshot.platforms) / columns))
    language_top = _CARD_TOP + rows * (_CARD_HEIGHT + _CARD_GAP) + 4
    height = language_top + 118
    active_text = "platform" if snapshot.active_platforms == 1 else "platforms"
    title = "Practice coverage"
    description = (
        f"{snapshot.accepted_problems} accepted problems across "
        f"{snapshot.active_platforms} active {active_text}, with native difficulty profiles and "
        "accepted solution languages."
    )
    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{height}" '
            f'viewBox="0 0 {_WIDTH} {height}" role="img" '
            'aria-labelledby="coverage-title coverage-desc">'
        ),
        f'  <title id="coverage-title">{title}</title>',
        f'  <desc id="coverage-desc">{escape(description)}</desc>',
        f'  <rect width="{_WIDTH}" height="{height}" rx="16" fill="#0d111b"/>',
        '  <text x="24" y="37" fill="#f0f3f8" '
        'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
        'font-size="22" font-weight="700">Practice Coverage</text>',
        f'  <text x="{_WIDTH - 24}" y="36" text-anchor="end" fill="#8d99b2" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12">'
        f"{snapshot.accepted_problems} ACCEPTED · {snapshot.active_platforms} ACTIVE</text>",
    ]

    for index, coverage in enumerate(snapshot.platforms):
        column = index % columns
        row = index // columns
        x = _CARD_LEFT + column * (_CARD_WIDTH + _CARD_GAP)
        y = _CARD_TOP + row * (_CARD_HEIGHT + _CARD_GAP)
        _render_platform_card(lines, coverage, index, x, y)

    lines.extend(
        (
            f'  <text x="24" y="{language_top + 25}" fill="#f0f3f8" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            'font-size="16" font-weight="700">Accepted solution languages</text>',
            f'  <text x="{_WIDTH - 24}" y="{language_top + 25}" text-anchor="end" '
            'fill="#64748b" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="11">{sum(snapshot.languages.values())} SOLUTIONS</text>',
        )
    )
    language_values = tuple(
        (
            language,
            count,
            _LANGUAGE_COLORS.get(language, _PLATFORM_COLORS[index % len(_PLATFORM_COLORS)]),
        )
        for index, (language, count) in enumerate(snapshot.languages.items())
    )
    _render_segments(
        lines,
        x=24,
        y=language_top + 39,
        width=_WIDTH - 48,
        height=20,
        values=language_values,
        data_prefix="language",
    )
    language_summary = _profile_summary(language_values) or "No accepted solution languages yet"
    lines.append(
        f'  <text x="24" y="{language_top + 82}" fill="#b8c1d8" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'font-size="11">{escape(language_summary)}</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def coverage_path(root: str | Path) -> Path:
    return Path(root) / "assets" / "dashboards" / "practice-coverage.svg"


def generate_coverage(root: str | Path, *, check: bool = False) -> tuple[Path, ...]:
    """Generate the checked-in practice coverage dashboard."""

    root = Path(root)
    output = coverage_path(root)
    expected = render_coverage_svg(aggregate_coverage(root))
    try:
        actual = output.read_text(encoding="utf-8")
    except FileNotFoundError:
        actual = None
    if actual == expected:
        return ()
    if not check:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(expected, encoding="utf-8", newline="\n")
    return (output,)
