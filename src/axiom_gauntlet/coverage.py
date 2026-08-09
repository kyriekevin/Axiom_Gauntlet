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
_DIFFICULTY_ACCENTS = {
    "easy": "coverage-teal",
    "medium": "coverage-peach",
    "hard": "coverage-red",
    "unknown": "coverage-overlay",
}
_RATING_BANDS = (
    ("≤999", 0, 999),
    ("1000–1199", 1000, 1199),
    ("1200–1399", 1200, 1399),
    ("1400–1599", 1400, 1599),
    ("1600+", 1600, None),
)
_RATING_ACCENTS = (
    "coverage-green",
    "coverage-teal",
    "coverage-sapphire",
    "coverage-mauve",
    "coverage-red",
)
_PLATFORM_ACCENTS = (
    "coverage-peach",
    "coverage-sapphire",
    "coverage-mauve",
    "coverage-teal",
    "coverage-green",
)
_LANGUAGE_LABELS = {"cpp": "C++", "python": "Python", "go": "Go"}
_LANGUAGE_ACCENTS = {
    "C++": "coverage-mauve",
    "Python": "coverage-blue",
    "Go": "coverage-teal",
}

_WIDTH = 900
_PROFILE_ROW_HEIGHT = 58


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


def _profile_label(coverage: PlatformCoverage) -> str:
    if coverage.spec.default_difficulty_scheme == "rating":
        return "RATING PROFILE"
    return "LEVEL PROFILE"


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
    clip_id = f"{data_prefix}-profile-clip"
    lines.append(
        f'  <rect class="coverage-track" x="{x}" y="{y}" width="{width}" height="{height}" rx="6"/>'
    )
    if total <= 0:
        return
    lines.append(
        f'  <clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{width}" '
        f'height="{height}" rx="6"/></clipPath>'
    )
    cursor = float(x)
    nonzero = [(label, value, color) for label, value, color in values if value > 0]
    for index, (label, value, color) in enumerate(nonzero):
        segment_width = width * value / total
        if index == len(nonzero) - 1:
            segment_width = x + width - cursor
        lines.extend(
            (
                f'  <rect x="{cursor:.2f}" y="{y}" width="{segment_width:.2f}" '
                f'height="{height}" class="coverage-accent {color}" '
                f'clip-path="url(#{clip_id})" '
                f'data-profile="{data_prefix}" '
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
            for (label, _, _), color in zip(_RATING_BANDS, _RATING_ACCENTS, strict=True)
        )
    return tuple(
        (_DIFFICULTY_LABELS[level], coverage.difficulty.get(level, 0), _DIFFICULTY_ACCENTS[level])
        for level in _DIFFICULTY_ORDER
    )


def _render_profile_legend(
    lines: list[str],
    *,
    coverage: PlatformCoverage,
    values: tuple[tuple[str, int, str], ...],
    y: int,
) -> None:
    populated = [(label, count, color) for label, count, color in values if count > 0]
    rating_profile = coverage.spec.default_difficulty_scheme == "rating"
    columns = 2 if rating_profile else 3
    column_width = 118 if rating_profile else 78
    first_baseline = y + 16 if rating_profile else y + 25
    row_gap = 15
    for index, (label, count, color) in enumerate(populated):
        row, column = divmod(index, columns)
        x = 640 + column * column_width
        baseline = first_baseline + row * row_gap
        lines.extend(
            (
                f'  <circle class="coverage-accent {color}" cx="{x + 3}" '
                f'cy="{baseline - 3}" r="3"/>',
                f'  <text class="coverage-secondary" x="{x + 11}" y="{baseline}" '
                'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
                f'font-size="9" data-profile-summary="{coverage.spec.slug}" '
                f'data-segment="{escape(label)}" data-count="{count}">'
                f"{escape(label)} {count}</text>",
            )
        )


def _render_ring(
    lines: list[str],
    *,
    cx: int,
    cy: int,
    radius: int,
    stroke_width: int,
    values: tuple[tuple[str, int, str], ...],
    data_prefix: str,
) -> None:
    circumference = 2 * math.pi * radius
    lines.append(
        f'  <circle class="coverage-track-stroke" cx="{cx}" cy="{cy}" r="{radius}" '
        f'fill="none" stroke-width="{stroke_width}"/>'
    )
    total = sum(value for _, value, _ in values)
    if total <= 0:
        return

    cursor = 0.0
    for label, value, color in values:
        if value <= 0:
            continue
        segment = circumference * value / total
        gap = min(3.0, segment * 0.15)
        visible = max(0.8, segment - gap)
        lines.extend(
            (
                f'  <circle class="coverage-accent {color}" cx="{cx}" cy="{cy}" r="{radius}" '
                f'style="fill:none" stroke-width="{stroke_width}" '
                f'stroke-dasharray="{visible:.2f} {circumference - visible:.2f}" '
                f'stroke-dashoffset="{-cursor:.2f}" transform="rotate(-90 {cx} {cy})" '
                f'data-ring="{data_prefix}" data-segment="{escape(label)}" '
                f'data-count="{value}">',
                f"    <title>{escape(label)}: {value}</title>",
                "  </circle>",
            )
        )
        cursor += segment


def _render_profile_row(lines: list[str], coverage: PlatformCoverage, index: int, y: int) -> None:
    accent = _PLATFORM_ACCENTS[index % len(_PLATFORM_ACCENTS)]
    marker_class = (
        f"coverage-accent {accent} coverage-empty"
        if coverage.accepted <= 0
        else f"coverage-accent {accent}"
    )
    lines.extend(
        (
            f'  <circle class="{marker_class}" cx="31" cy="{y + 20}" r="5"/>',
            f'  <text class="coverage-primary" x="44" y="{y + 26}" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            f'font-size="16" font-weight="650">{escape(coverage.spec.coverage_label)}</text>',
            f'  <text class="coverage-muted" x="44" y="{y + 45}" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="9">{_profile_label(coverage)} · {coverage.accepted} AC</text>',
        )
    )

    if coverage.accepted <= 0:
        _render_segments(
            lines,
            x=220,
            y=y + 13,
            width=400,
            height=16,
            values=(),
            data_prefix=coverage.spec.slug,
        )
        lines.append(
            f'  <text class="coverage-muted" x="640" y="{y + 26}" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            'font-size="12">No accepted problems yet</text>'
        )
    else:
        values = _profile_values(coverage)
        _render_segments(
            lines,
            x=220,
            y=y + 13,
            width=400,
            height=16,
            values=values,
            data_prefix=coverage.spec.slug,
        )
        _render_profile_legend(lines, coverage=coverage, values=values, y=y)

    lines.append(
        f'  <line class="coverage-divider" x1="24" '
        f'y1="{y + _PROFILE_ROW_HEIGHT - 1}" x2="876" '
        f'y2="{y + _PROFILE_ROW_HEIGHT - 1}"/>'
    )


def _render_share_item(
    lines: list[str],
    *,
    x: int,
    y: int,
    width: int,
    label: str,
    count: int,
    share: float,
    accent: str,
    marker: str,
) -> None:
    """Render one compact composition item with a precise count and visual share."""

    marker_class = (
        f"coverage-accent {accent} coverage-empty" if count <= 0 else f"coverage-accent {accent}"
    )
    marker_svg = (
        f'  <circle class="{marker_class}" cx="{x + 5}" cy="{y - 5}" r="5"/>'
        if marker == "circle"
        else f'  <rect class="{marker_class}" x="{x}" y="{y - 10}" width="10" height="10" rx="3"/>'
    )
    track_x = x + 18
    track_y = y + 9
    percentage_x = x + width
    track_width = width - 58
    filled_width = track_width * share / 100
    count_class = "coverage-secondary" if count else "coverage-muted"
    lines.extend(
        (
            marker_svg,
            f'  <text class="coverage-primary" x="{x + 18}" y="{y}" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            f'font-size="14" font-weight="600">{escape(label)}</text>',
            f'  <text class="{count_class}" x="{percentage_x}" y="{y}" text-anchor="end" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="11">{count}</text>',
            f'  <rect class="coverage-track" x="{track_x}" y="{track_y}" '
            f'width="{track_width}" height="5" rx="2.5"/>',
        )
    )
    if filled_width > 0:
        lines.extend(
            (
                f'  <rect class="coverage-accent {accent}" x="{track_x}" y="{track_y}" '
                f'width="{filled_width:.2f}" height="5" rx="2.5" '
                f'data-share="{share:.1f}" data-count="{count}">',
                f"    <title>{escape(label)}: {count} ({share:.0f}%)</title>",
                "  </rect>",
            )
        )
    lines.append(
        f'  <text class="coverage-muted" x="{percentage_x}" y="{y + 17}" text-anchor="end" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'font-size="9">{share:.0f}%</text>'
    )


def render_coverage_svg(snapshot: CoverageSnapshot) -> str:
    """Render a focused overview with nested composition rings and native profiles."""

    platform_rows = max(1, math.ceil(len(snapshot.platforms) / 2))
    language_rows = max(1, len(snapshot.languages))
    overview_top = 82
    overview_height = max(198, 54 + platform_rows * 40, 54 + language_rows * 30)
    profile_heading_y = overview_top + overview_height + 33
    profile_top = profile_heading_y + 16
    height = profile_top + len(snapshot.platforms) * _PROFILE_ROW_HEIGHT + 22
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
        "  <style>",
        "    .coverage-background { fill: #eff1f5; }",
        "    .coverage-primary { fill: #4c4f69; }",
        "    .coverage-secondary { fill: #5c5f77; }",
        "    .coverage-muted { fill: #6c6f85; }",
        "    .coverage-track { fill: #ccd0da; }",
        "    .coverage-track-stroke { stroke: #ccd0da; }",
        "    .coverage-divider { stroke: #bcc0cc; }",
        "    .coverage-yellow { fill: #df8e1d; stroke: #df8e1d; }",
        "    .coverage-blue { fill: #1e66f5; stroke: #1e66f5; }",
        "    .coverage-sapphire { fill: #209fb5; stroke: #209fb5; }",
        "    .coverage-mauve { fill: #8839ef; stroke: #8839ef; }",
        "    .coverage-green { fill: #40a02b; stroke: #40a02b; }",
        "    .coverage-peach { fill: #fe640b; stroke: #fe640b; }",
        "    .coverage-red { fill: #d20f39; stroke: #d20f39; }",
        "    .coverage-teal { fill: #179299; stroke: #179299; }",
        "    .coverage-overlay { fill: #7c7f93; stroke: #7c7f93; }",
        "    .coverage-accent { opacity: 0.72; }",
        "    .coverage-empty { opacity: 0.32; }",
        "    @media (prefers-color-scheme: dark) {",
        "      .coverage-background { fill: #1e1e2e; }",
        "      .coverage-primary { fill: #cdd6f4; }",
        "      .coverage-secondary { fill: #bac2de; }",
        "      .coverage-muted { fill: #a6adc8; }",
        "      .coverage-track { fill: #313244; }",
        "      .coverage-track-stroke { stroke: #313244; }",
        "      .coverage-divider { stroke: #45475a; }",
        "      .coverage-yellow { fill: #f9e2af; stroke: #f9e2af; }",
        "      .coverage-blue { fill: #89b4fa; stroke: #89b4fa; }",
        "      .coverage-sapphire { fill: #74c7ec; stroke: #74c7ec; }",
        "      .coverage-mauve { fill: #cba6f7; stroke: #cba6f7; }",
        "      .coverage-green { fill: #a6e3a1; stroke: #a6e3a1; }",
        "      .coverage-peach { fill: #fab387; stroke: #fab387; }",
        "      .coverage-red { fill: #f38ba8; stroke: #f38ba8; }",
        "      .coverage-teal { fill: #94e2d5; stroke: #94e2d5; }",
        "      .coverage-overlay { fill: #9399b2; stroke: #9399b2; }",
        "      .coverage-accent { opacity: 1; }",
        "      .coverage-empty { opacity: 0.45; }",
        "    }",
        "  </style>",
        f'  <rect class="coverage-background" width="{_WIDTH}" height="{height}" rx="16"/>',
        '  <text class="coverage-primary" x="24" y="37" '
        'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
        'font-size="22" font-weight="700">Practice Coverage</text>',
        f'  <text class="coverage-muted" x="24" y="59" '
        'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="12">'
        f"{snapshot.accepted_problems} accepted problems across "
        f"{snapshot.active_platforms} active {active_text}</text>",
    ]

    ring_cx = 126
    ring_cy = overview_top + 84
    platform_values = tuple(
        (
            coverage.spec.label,
            coverage.accepted,
            _PLATFORM_ACCENTS[index % len(_PLATFORM_ACCENTS)],
        )
        for index, coverage in enumerate(snapshot.platforms)
    )
    language_values = tuple(
        (
            language,
            count,
            _LANGUAGE_ACCENTS.get(language, _PLATFORM_ACCENTS[index % len(_PLATFORM_ACCENTS)]),
        )
        for index, (language, count) in enumerate(snapshot.languages.items())
    )
    _render_ring(
        lines,
        cx=ring_cx,
        cy=ring_cy,
        radius=67,
        stroke_width=16,
        values=platform_values,
        data_prefix="platform",
    )
    _render_ring(
        lines,
        cx=ring_cx,
        cy=ring_cy,
        radius=46,
        stroke_width=10,
        values=language_values,
        data_prefix="language",
    )
    lines.extend(
        (
            f'  <text class="coverage-primary" x="{ring_cx}" y="{ring_cy + 3}" '
            'text-anchor="middle" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            f'font-size="26" font-weight="700">{snapshot.accepted_problems}</text>',
            f'  <text class="coverage-secondary" x="{ring_cx}" y="{ring_cy + 22}" '
            'text-anchor="middle" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            'font-size="9">PROBLEMS</text>',
            f'  <text class="coverage-muted" x="{ring_cx}" y="{overview_top + 184}" '
            'text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            'font-size="9">OUTER PLATFORM · INNER LANGUAGE</text>',
            f'  <text class="coverage-muted" x="260" y="{overview_top + 18}" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            'font-size="10">ACCEPTED BY PLATFORM</text>',
            f'  <text class="coverage-muted" x="690" y="{overview_top + 18}" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            'font-size="10">SOLUTION LANGUAGES</text>',
        )
    )

    legend_rows = math.ceil(len(snapshot.platforms) / 2)
    for index, coverage in enumerate(snapshot.platforms):
        column = index // legend_rows
        row = index % legend_rows
        x = 260 + column * 205
        y = overview_top + 48 + row * 40
        share = (
            coverage.accepted / snapshot.accepted_problems * 100
            if snapshot.accepted_problems
            else 0.0
        )
        accent = _PLATFORM_ACCENTS[index % len(_PLATFORM_ACCENTS)]
        _render_share_item(
            lines,
            x=x,
            y=y,
            width=185,
            label=coverage.spec.coverage_label,
            count=coverage.accepted,
            share=share,
            accent=accent,
            marker="circle",
        )

    language_total = sum(snapshot.languages.values())
    if language_values:
        for index, (language, count, color) in enumerate(language_values):
            y = overview_top + 48 + index * 30
            share = count / language_total * 100 if language_total else 0.0
            _render_share_item(
                lines,
                x=690,
                y=y - 3,
                width=170,
                label=language,
                count=count,
                share=share,
                accent=color,
                marker="square",
            )
    else:
        lines.append(
            f'  <text class="coverage-muted" x="690" y="{overview_top + 49}" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            'font-size="13">No accepted solutions yet</text>'
        )

    lines.extend(
        (
            f'  <line class="coverage-divider" x1="24" '
            f'y1="{overview_top + overview_height}" x2="876" '
            f'y2="{overview_top + overview_height}"/>',
            f'  <text class="coverage-primary" x="24" y="{profile_heading_y}" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            'font-size="16" font-weight="700">Native profiles</text>',
        )
    )
    for index, coverage in enumerate(snapshot.platforms):
        _render_profile_row(lines, coverage, index, profile_top + index * _PROFILE_ROW_HEIGHT)

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
