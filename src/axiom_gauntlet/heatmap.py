"""Deterministic rolling activity heatmaps for the repository README.

The renderer intentionally uses only static SVG primitives. GitHub does not
run scripts or animation embedded in SVG files, and keeping the output static
also makes generated assets easy to review in pull requests.
"""

from __future__ import annotations

import bisect
import tomllib
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from .platforms import PLATFORMS

COUNTED_ACTIVITY_TYPES = frozenset({"ac", "note", "review"})
SHANGHAI = ZoneInfo("Asia/Shanghai")
_LEVEL_CLASSES = tuple(f"heatmap-level-{level}" for level in range(5))

_WIDTH = 1180
_WEEKS = 53
_CELL_SIZE = 16
_CELL_GAP = 4
_CELL_STEP = _CELL_SIZE + _CELL_GAP
_GRID_LEFT = 58
_GRID_TOP = 108


class HeatmapDataError(ValueError):
    """Raised when a problem file cannot be decoded as TOML."""


def discover(root: Path) -> tuple[Path, ...]:
    """Return problem manifests below *root* in a stable order.

    A manifest lives at ``problems/<platform>/<problem>/problem.toml``. The
    exact-depth glob intentionally ignores drafts and unrelated TOML files.
    """

    problems = Path(root) / "problems"
    return tuple(sorted(problems.glob("*/*/problem.toml"), key=lambda path: path.as_posix()))


def _platform_for(path: Path, root: Path) -> str | None:
    try:
        relative = path.relative_to(Path(root) / "problems")
    except ValueError:
        return None
    return relative.parts[0].lower() if len(relative.parts) >= 3 else None


def _parse_activity_date(value: object) -> date | None:
    # datetime is a subclass of date, so check it first.
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def _read_manifest(path: Path) -> Mapping[str, object]:
    try:
        with path.open("rb") as manifest:
            parsed = tomllib.load(manifest)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise HeatmapDataError(f"cannot read {path}: {exc}") from exc
    return parsed


def aggregate_activity(root: Path) -> dict[date, int]:
    """Count AC, note, and review events across all supported platforms.

    Dates in ``problem.toml`` are already Asia/Shanghai calendar dates; this
    module deliberately performs no timezone conversion.
    """

    root = Path(root)
    counts: Counter[date] = Counter()

    for manifest_path in discover(root):
        if _platform_for(manifest_path, root) not in PLATFORMS:
            continue

        raw_activity = _read_manifest(manifest_path).get("activity", ())
        if isinstance(raw_activity, Mapping):
            activities: Iterable[object] = (raw_activity,)
        elif isinstance(raw_activity, list):
            activities = raw_activity
        else:
            continue

        for raw_event in activities:
            if not isinstance(raw_event, Mapping):
                continue
            event_type = raw_event.get("type")
            if not isinstance(event_type, str):
                continue
            if event_type.strip().lower() not in COUNTED_ACTIVITY_TYPES:
                continue
            event_date = _parse_activity_date(raw_event.get("date"))
            if event_date is not None:
                counts[event_date] += 1

    return dict(sorted(counts.items()))


def _grid_bounds(as_of: date) -> tuple[date, date]:
    grid_end = as_of + timedelta(days=6 - as_of.weekday())
    return grid_end - timedelta(days=_WEEKS * 7 - 1), grid_end


def _thresholds(values: list[int]) -> tuple[int, int, int]:
    if not values:
        return 0, 0, 0
    ordered = sorted(values)
    return tuple(
        ordered[min(len(ordered) - 1, int((len(ordered) - 1) * quantile))]
        for quantile in (0.25, 0.5, 0.75)
    )


def _intensity(count: int, thresholds: tuple[int, int, int]) -> int:
    if count <= 0:
        return 0
    return min(1 + bisect.bisect_left(thresholds, count), 4)


def _default_as_of(counts: Mapping[date, int]) -> date:
    return max(
        (day for day, count in counts.items() if count > 0), default=datetime.now(SHANGHAI).date()
    )


def render_heatmap(as_of: date, counts: Mapping[date, int]) -> str:
    """Render trailing 53-week repository activity as a script-free SVG string."""

    if not isinstance(as_of, date):
        raise TypeError("as_of must be a date")
    grid_start, grid_end = _grid_bounds(as_of)
    grid_bottom = _GRID_TOP + 7 * _CELL_STEP - _CELL_GAP
    footer_y = grid_bottom + 36
    height = footer_y + 32
    label = "Axiom Gauntlet"

    normalized_counts = {
        day: max(0, int(count))
        for day, count in counts.items()
        if isinstance(day, date) and grid_start <= day <= as_of
    }
    positive_counts = [count for count in normalized_counts.values() if count > 0]
    thresholds = _thresholds(positive_counts)
    total_events = sum(normalized_counts.values())
    active_days = len(positive_counts)
    title_id = f"total-{as_of.isoformat()}-title"
    desc_id = f"total-{as_of.isoformat()}-desc"

    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" '
            f'height="{height}" viewBox="0 0 {_WIDTH} {height}" role="img" '
            f'aria-labelledby="{title_id} {desc_id}">'
        ),
        (
            f'  <title id="{title_id}">{escape(label)} activity for 53 weeks through '
            f"{as_of.isoformat()}</title>"
        ),
        (
            f'  <desc id="{desc_id}">{total_events} counted activities across '
            f"{active_days} active days in the trailing 53 weeks. AC, note, and review events "
            "are included.</desc>"
        ),
        "  <style>",
        "    .heatmap-background { fill: #eff1f5; }",
        "    .heatmap-primary { fill: #4c4f69; }",
        "    .heatmap-secondary { fill: #5c5f77; }",
        "    .heatmap-muted { fill: #6c6f85; }",
        "    .heatmap-level-0 { fill: #ccd0da; }",
        "    .heatmap-level-1 { fill: #179299; fill-opacity: 0.25; }",
        "    .heatmap-level-2 { fill: #179299; fill-opacity: 0.50; }",
        "    .heatmap-level-3 { fill: #179299; fill-opacity: 0.75; }",
        "    .heatmap-level-4 { fill: #179299; }",
        "    @media (prefers-color-scheme: dark) {",
        "      .heatmap-background { fill: #1e1e2e; }",
        "      .heatmap-primary { fill: #cdd6f4; }",
        "      .heatmap-secondary { fill: #bac2de; }",
        "      .heatmap-muted { fill: #a6adc8; }",
        "      .heatmap-level-0 { fill: #313244; }",
        "      .heatmap-level-1 { fill: #94e2d5; fill-opacity: 0.25; }",
        "      .heatmap-level-2 { fill: #94e2d5; fill-opacity: 0.50; }",
        "      .heatmap-level-3 { fill: #94e2d5; fill-opacity: 0.75; }",
        "      .heatmap-level-4 { fill: #94e2d5; }",
        "    }",
        "  </style>",
        f'  <rect class="heatmap-background" width="{_WIDTH}" height="{height}" rx="22"/>',
        '  <circle cx="25" cy="27" r="5" fill="#ff5f57"/>',
        '  <circle cx="41" cy="27" r="5" fill="#febc2e"/>',
        '  <circle cx="57" cy="27" r="5" fill="#28c840"/>',
        (
            f'  <text class="heatmap-primary" x="76" y="35" font-family="ui-monospace, '
            f'SFMono-Regular, Menlo, Consolas, monospace" font-size="22" '
            f'font-weight="700">{escape(label)} Activity</text>'
        ),
        (
            f'  <text class="heatmap-secondary" x="{_WIDTH - 26}" y="34" text-anchor="end" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="12">53 WEEKS · THROUGH {as_of.isoformat()}</text>'
        ),
        (
            '  <text class="heatmap-secondary" x="25" y="66" font-family="ui-monospace, '
            'SFMono-Regular, Menlo, Consolas, monospace" font-size="12">'
            "ALL PLATFORMS · AC · NOTE · REVIEW</text>"
        ),
        (
            f'  <text class="heatmap-secondary" x="{_WIDTH - 26}" y="66" text-anchor="end" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="12">{total_events} EVENTS · {active_days} ACTIVE DAYS</text>'
        ),
    ]

    seen_months: set[tuple[int, int]] = set()
    for week in range(_WEEKS):
        week_start = grid_start + timedelta(days=week * 7)
        candidates = [week_start + timedelta(days=offset) for offset in range(7)]
        month_day = next((day for day in candidates if day.day <= 7), None)
        if month_day is None or (month_day.year, month_day.month) in seen_months:
            continue
        seen_months.add((month_day.year, month_day.month))
        x = _GRID_LEFT + week * _CELL_STEP
        lines.append(
            f'  <text class="heatmap-secondary" x="{x}" y="94" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="13">{month_day.strftime("%b")}</text>'
        )

    for weekday, weekday_label in ((0, "Mon"), (2, "Wed"), (4, "Fri")):
        y = _GRID_TOP + weekday * _CELL_STEP + 13
        lines.append(
            f'  <text class="heatmap-muted" x="25" y="{y}" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="12">{weekday_label}</text>'
        )

    current = grid_start
    while current <= as_of:
        week = (current - grid_start).days // 7
        weekday = current.weekday()
        x = _GRID_LEFT + week * _CELL_STEP
        y = _GRID_TOP + weekday * _CELL_STEP
        count = normalized_counts.get(current, 0)
        level = _intensity(count, thresholds)
        noun = "event" if count == 1 else "events"
        lines.extend(
            (
                (
                    f'  <rect class="heatmap-cell {_LEVEL_CLASSES[level]}" '
                    f'x="{x}" y="{y}" width="{_CELL_SIZE}" '
                    f'height="{_CELL_SIZE}" rx="4" '
                    f'data-date="{current.isoformat()}" data-count="{count}" '
                    f'data-level="{level}">'
                ),
                f"    <title>{current.isoformat()}: {count} {noun}</title>",
                "  </rect>",
            )
        )
        current += timedelta(days=1)

    lines.append(
        f'  <text class="heatmap-muted" x="{_GRID_LEFT}" y="{footer_y}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="12">Less</text>'
    )
    legend_x = _GRID_LEFT + 34
    for level, level_class in enumerate(_LEVEL_CLASSES):
        x = legend_x + level * _CELL_STEP
        lines.append(
            f'  <rect class="{level_class}" x="{x}" y="{footer_y - 12}" '
            f'width="{_CELL_SIZE}" height="{_CELL_SIZE}" rx="4"/>'
        )
    lines.append(
        f'  <text class="heatmap-muted" x="{legend_x + 5 * _CELL_STEP + 2}" '
        f'y="{footer_y}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="12">More</text>'
    )
    lines.append(
        f'  <text class="heatmap-muted" x="{_WIDTH - 26}" y="{footer_y}" '
        f'text-anchor="end" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="12">ASIA/SHANGHAI CALENDAR DATE</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def heatmap_path(root: Path) -> Path:
    """Return the checked-in path for the cross-platform activity heatmap."""

    return Path(root) / "assets" / "heatmaps" / "total.svg"


def generate_heatmaps(
    root: Path,
    as_of: date | None = None,
    *,
    check: bool = False,
) -> tuple[Path, ...]:
    """Generate the rolling heatmap and return its path when changed or stale.

    Without an explicit cutoff, the window ends on the latest recorded activity
    date, matching the repository's deterministic evidence-first workflow.
    """

    root = Path(root)
    output = heatmap_path(root)
    counts = aggregate_activity(root)
    cutoff = as_of or _default_as_of(counts)
    expected = render_heatmap(cutoff, counts)
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


def check_heatmaps(root: Path, as_of: date | None = None) -> bool:
    """Return ``True`` when the generated rolling heatmap is current."""

    return not generate_heatmaps(root, as_of, check=True)


# A descriptive alias for callers that treat generation as a rendering step.
render_all = generate_heatmaps
