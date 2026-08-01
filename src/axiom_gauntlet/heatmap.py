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

SUPPORTED_PLATFORMS = ("leetcode", "acwing", "codeforces")
COUNTED_ACTIVITY_TYPES = frozenset({"ac", "note", "review"})

_PLATFORM_LABELS = {
    "leetcode": "LeetCode",
    "acwing": "AcWing",
    "codeforces": "Codeforces",
}

# Empty plus four intensity levels.  Each palette is deliberately legible on
# the shared dark card used by every platform.
_PALETTES = {
    "leetcode": ("#202736", "#513b11", "#8a6216", "#d99a1f", "#ffd166"),
    "acwing": ("#202736", "#083b4c", "#086f87", "#11a9c3", "#66e3f4"),
    "codeforces": ("#202736", "#34205f", "#5933a5", "#8b5cf6", "#d8b4fe"),
}

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


def aggregate_activity(root: Path, platform: str, year: int) -> dict[date, int]:
    """Count AC, note, and review events by local calendar date.

    Dates in ``problem.toml`` are already Asia/Shanghai calendar dates; this
    module deliberately performs no timezone conversion.
    """

    _validate_platform(platform)
    _validate_year(year)
    root = Path(root)
    counts: Counter[date] = Counter()

    for manifest_path in discover(root):
        if _platform_for(manifest_path, root) != platform:
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


def _validate_platform(platform: str) -> None:
    if platform not in SUPPORTED_PLATFORMS:
        choices = ", ".join(SUPPORTED_PLATFORMS)
        raise ValueError(f"unsupported platform {platform!r}; expected one of: {choices}")


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


def render_heatmap(platform: str, year: int, counts: Mapping[date, int]) -> str:
    """Render one platform/year as a deterministic, script-free SVG string."""

    _validate_platform(platform)
    _validate_year(year)
    grid_start, grid_end, weeks = _calendar_bounds(year)
    width = _GRID_LEFT + weeks * _CELL_STEP + 30
    grid_bottom = _GRID_TOP + 7 * _CELL_STEP - _CELL_GAP
    height = grid_bottom + 58
    label = _PLATFORM_LABELS[platform]
    palette = _PALETTES[platform]

    normalized_counts = {
        day: max(0, int(count))
        for day, count in counts.items()
        if isinstance(day, date) and day.year == year
    }
    total_events = sum(normalized_counts.values())
    active_days = sum(1 for count in normalized_counts.values() if count > 0)
    title_id = f"{platform}-{year}-title"
    desc_id = f"{platform}-{year}-desc"

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
        f'  <rect width="{width}" height="{height}" rx="16" fill="#0d111b"/>',
        '  <circle cx="25" cy="25" r="4" fill="#ff5f57"/>',
        '  <circle cx="39" cy="25" r="4" fill="#febc2e"/>',
        '  <circle cx="53" cy="25" r="4" fill="#28c840"/>',
        (
            f'  <text x="70" y="31" fill="#f0f3f8" font-family="ui-monospace, '
            f'SFMono-Regular, Menlo, Consolas, monospace" font-size="16" '
            f'font-weight="700">{escape(label)} Activity</text>'
        ),
        (
            f'  <text x="{width - 26}" y="31" text-anchor="end" fill="#a8b3cf" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="14">{year}</text>'
        ),
        (
            '  <text x="25" y="56" fill="#76839f" font-family="ui-monospace, '
            'SFMono-Regular, Menlo, Consolas, monospace" font-size="11">'
            "AC · NOTE · REVIEW</text>"
        ),
        (
            f'  <text x="{width - 26}" y="56" text-anchor="end" fill="#76839f" '
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
            f'  <text x="{x}" y="78" fill="#76839f" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="10">{month_name}</text>'
        )

    weekday_labels = {0: "Mon", 2: "Wed", 4: "Fri"}
    for weekday, weekday_label in weekday_labels.items():
        y = _GRID_TOP + weekday * _CELL_STEP + 9
        lines.append(
            f'  <text x="25" y="{y}" fill="#59657e" '
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
                        f'  <rect x="{x}" y="{y}" width="{_CELL_SIZE}" '
                        f'height="{_CELL_SIZE}" rx="2" fill="{palette[level]}" '
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
        f'  <text x="25" y="{footer_y}" fill="#59657e" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="9">LESS</text>'
    )
    legend_x = 57
    for level, color in enumerate(palette):
        x = legend_x + level * _CELL_STEP
        lines.append(
            f'  <rect x="{x}" y="{footer_y - 9}" width="{_CELL_SIZE}" '
            f'height="{_CELL_SIZE}" rx="2" fill="{color}"/>'
        )
    lines.append(
        f'  <text x="{legend_x + 5 * _CELL_STEP + 2}" y="{footer_y}" fill="#59657e" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="9">MORE</text>'
    )
    lines.append(
        f'  <text x="{width - 26}" y="{footer_y}" text-anchor="end" fill="#59657e" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="9">ASIA/SHANGHAI CALENDAR DATE</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def heatmap_path(root: Path, platform: str) -> Path:
    """Return the checked-in asset path for *platform*."""

    _validate_platform(platform)
    return Path(root) / "assets" / "heatmaps" / f"{platform}.svg"


def generate_heatmaps(
    root: Path,
    year: int,
    *,
    check: bool = False,
    platforms: Iterable[str] = SUPPORTED_PLATFORMS,
) -> tuple[Path, ...]:
    """Generate heatmaps and return paths that changed (or are stale).

    In check mode no files are written; the returned tuple contains missing or
    stale assets.  This makes the function directly usable by a CLI command:
    an empty result means the repository is up to date.
    """

    _validate_year(year)
    root = Path(root)
    changed: list[Path] = []

    for platform in platforms:
        _validate_platform(platform)
        output = heatmap_path(root, platform)
        expected = render_heatmap(platform, year, aggregate_activity(root, platform, year))
        try:
            actual = output.read_text(encoding="utf-8")
        except FileNotFoundError:
            actual = None
        if actual == expected:
            continue
        changed.append(output)
        if not check:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(expected, encoding="utf-8", newline="\n")

    return tuple(changed)


def check_heatmaps(
    root: Path,
    year: int,
    *,
    platforms: Iterable[str] = SUPPORTED_PLATFORMS,
) -> bool:
    """Return ``True`` when all generated heatmaps are current."""

    return not generate_heatmaps(root, year, check=True, platforms=platforms)


# A descriptive alias for callers that treat generation as a rendering step.
render_all = generate_heatmaps
