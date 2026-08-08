"""Deterministic activity heatmaps for the repository README.

The renderer intentionally uses only static SVG primitives.  GitHub does not
run scripts or animation embedded in SVG files, and keeping the output static
also makes generated assets easy to review in pull requests.
"""

from __future__ import annotations

import tomllib
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

from .platforms import PLATFORMS

COUNTED_ACTIVITY_TYPES = frozenset({"ac", "note", "review"})
_LEVEL_CLASSES = tuple(f"heatmap-level-{level}" for level in range(5))

_CELL_SIZE = 11
_CELL_GAP = 4
_CELL_STEP = _CELL_SIZE + _CELL_GAP
_GRID_LEFT = 58
_GRID_TOP = 88


class HeatmapDataError(ValueError):
    """Raised when a problem file cannot be decoded as TOML."""


def discover(root: Path) -> tuple[Path, ...]:
    """Return problem manifests below *root* in a stable order.

    A manifest lives at ``problems/<platform>/<problem>/problem.toml``.  The
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


def aggregate_activity(root: Path, year: int) -> dict[date, int]:
    """Count AC, note, and review events across all supported platforms.

    Dates in ``problem.toml`` are already Asia/Shanghai calendar dates; this
    module deliberately performs no timezone conversion.
    """

    _validate_year(year)
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
            if event_date is not None and event_date.year == year:
                counts[event_date] += 1

    return dict(sorted(counts.items()))


def _validate_year(year: int) -> None:
    if isinstance(year, bool) or not isinstance(year, int) or not 1 <= year <= 9999:
        raise ValueError("year must be an integer between 1 and 9999")


def _calendar_bounds(year: int) -> tuple[date, date, int]:
    first = date(year, 1, 1)
    last = date(year, 12, 31)
    grid_start = first - timedelta(days=first.weekday())
    grid_end = last + timedelta(days=6 - last.weekday())
    weeks = ((grid_end - grid_start).days + 1) // 7
    return grid_start, grid_end, weeks


def _intensity(count: int) -> int:
    if count <= 0:
        return 0
    return min(count, 4)


def render_heatmap(year: int, counts: Mapping[date, int]) -> str:
    """Render total repository activity as a deterministic, script-free SVG string."""

    _validate_year(year)
    grid_start, grid_end, weeks = _calendar_bounds(year)
    width = _GRID_LEFT + weeks * _CELL_STEP + 30
    grid_bottom = _GRID_TOP + 7 * _CELL_STEP - _CELL_GAP
    height = grid_bottom + 58
    label = "Axiom Gauntlet"

    normalized_counts = {
        day: max(0, int(count))
        for day, count in counts.items()
        if isinstance(day, date) and day.year == year
    }
    total_events = sum(normalized_counts.values())
    active_days = sum(1 for count in normalized_counts.values() if count > 0)
    title_id = f"total-{year}-title"
    desc_id = f"total-{year}-desc"

    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="{title_id} {desc_id}">'
        ),
        f'  <title id="{title_id}">{escape(label)} activity in {year}</title>',
        (
            f'  <desc id="{desc_id}">{total_events} counted activities across '
            f"{active_days} active days. AC, note, and review events are included.</desc>"
        ),
        "  <style>",
        "    .heatmap-background { fill: #f6f8fa; }",
        "    .heatmap-primary { fill: #1f2328; }",
        "    .heatmap-secondary { fill: #57606a; }",
        "    .heatmap-muted { fill: #6e7781; }",
        "    .heatmap-level-0 { fill: #e8ecf1; }",
        "    .heatmap-level-1 { fill: #67e8f9; }",
        "    .heatmap-level-2 { fill: #06b6d4; }",
        "    .heatmap-level-3 { fill: #0e7490; }",
        "    .heatmap-level-4 { fill: #164e63; }",
        "    @media (prefers-color-scheme: dark) {",
        "      .heatmap-background { fill: #1d1e2c; }",
        "      .heatmap-primary { fill: #e6e9f2; }",
        "      .heatmap-secondary { fill: #b8c1d8; }",
        "      .heatmap-muted { fill: #8d99b2; }",
        "      .heatmap-level-0 { fill: #34384a; }",
        "      .heatmap-level-1 { fill: #0e7490; }",
        "      .heatmap-level-2 { fill: #0891b2; }",
        "      .heatmap-level-3 { fill: #22d3ee; }",
        "      .heatmap-level-4 { fill: #a5f3fc; }",
        "    }",
        "  </style>",
        f'  <rect class="heatmap-background" width="{width}" height="{height}" rx="16"/>',
        '  <circle cx="25" cy="25" r="4" fill="#ff5f57"/>',
        '  <circle cx="39" cy="25" r="4" fill="#febc2e"/>',
        '  <circle cx="53" cy="25" r="4" fill="#28c840"/>',
        (
            f'  <text class="heatmap-primary" x="70" y="31" font-family="ui-monospace, '
            f'SFMono-Regular, Menlo, Consolas, monospace" font-size="16" '
            f'font-weight="700">{escape(label)} Activity</text>'
        ),
        (
            f'  <text class="heatmap-secondary" x="{width - 26}" y="31" text-anchor="end" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="14">{year}</text>'
        ),
        (
            '  <text class="heatmap-secondary" x="25" y="56" font-family="ui-monospace, '
            'SFMono-Regular, Menlo, Consolas, monospace" font-size="11">'
            "ALL PLATFORMS · AC · NOTE · REVIEW</text>"
        ),
        (
            f'  <text class="heatmap-secondary" x="{width - 26}" y="56" text-anchor="end" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="11">{total_events} EVENTS · {active_days} ACTIVE DAYS</text>'
        ),
    ]

    month_names = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )
    for month, month_name in enumerate(month_names, start=1):
        month_day = date(year, month, 1)
        week = (month_day - grid_start).days // 7
        x = _GRID_LEFT + week * _CELL_STEP
        lines.append(
            f'  <text class="heatmap-secondary" x="{x}" y="78" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="10">{month_name}</text>'
        )

    weekday_labels = {0: "Mon", 2: "Wed", 4: "Fri"}
    for weekday, weekday_label in weekday_labels.items():
        y = _GRID_TOP + weekday * _CELL_STEP + 9
        lines.append(
            f'  <text class="heatmap-muted" x="25" y="{y}" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="9">{weekday_label}</text>'
        )

    current = grid_start
    while current <= grid_end:
        if current.year == year:
            week = (current - grid_start).days // 7
            weekday = current.weekday()
            x = _GRID_LEFT + week * _CELL_STEP
            y = _GRID_TOP + weekday * _CELL_STEP
            count = normalized_counts.get(current, 0)
            level = _intensity(count)
            noun = "event" if count == 1 else "events"
            lines.extend(
                (
                    (
                        f'  <rect class="heatmap-cell {_LEVEL_CLASSES[level]}" '
                        f'x="{x}" y="{y}" width="{_CELL_SIZE}" '
                        f'height="{_CELL_SIZE}" rx="2" '
                        f'data-date="{current.isoformat()}" data-count="{count}" '
                        f'data-level="{level}">'
                    ),
                    f"    <title>{current.isoformat()}: {count} {noun}</title>",
                    "  </rect>",
                )
            )
        current += timedelta(days=1)

    footer_y = grid_bottom + 31
    lines.append(
        f'  <text class="heatmap-muted" x="25" y="{footer_y}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="9">LESS</text>'
    )
    legend_x = 57
    for level, level_class in enumerate(_LEVEL_CLASSES):
        x = legend_x + level * _CELL_STEP
        lines.append(
            f'  <rect class="{level_class}" x="{x}" y="{footer_y - 9}" '
            f'width="{_CELL_SIZE}" height="{_CELL_SIZE}" rx="2"/>'
        )
    lines.append(
        f'  <text class="heatmap-muted" x="{legend_x + 5 * _CELL_STEP + 2}" '
        f'y="{footer_y}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="9">MORE</text>'
    )
    lines.append(
        f'  <text class="heatmap-muted" x="{width - 26}" y="{footer_y}" '
        f'text-anchor="end" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="9">ASIA/SHANGHAI CALENDAR DATE</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def heatmap_path(root: Path) -> Path:
    """Return the checked-in path for the cross-platform activity heatmap."""

    return Path(root) / "assets" / "heatmaps" / "total.svg"


def generate_heatmaps(
    root: Path,
    year: int,
    *,
    check: bool = False,
) -> tuple[Path, ...]:
    """Generate the total heatmap and return its path when changed or stale.

    In check mode no files are written; the returned tuple contains missing or
    stale assets.  This makes the function directly usable by a CLI command:
    an empty result means the repository is up to date.
    """

    _validate_year(year)
    root = Path(root)
    output = heatmap_path(root)
    expected = render_heatmap(year, aggregate_activity(root, year))
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


def check_heatmaps(
    root: Path,
    year: int,
) -> bool:
    """Return ``True`` when the generated total heatmap is current."""

    return not generate_heatmaps(root, year, check=True)


# A descriptive alias for callers that treat generation as a rendering step.
render_all = generate_heatmaps
