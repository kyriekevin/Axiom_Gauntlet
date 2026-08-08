from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import pytest

from axiom_gauntlet.heatmap import (
    HeatmapDataError,
    aggregate_activity,
    check_heatmaps,
    discover,
    generate_heatmaps,
    render_heatmap,
)


def _write_problem(root: Path, platform: str, slug: str, body: str) -> Path:
    manifest = root / "problems" / platform / slug / "problem.toml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(body, encoding="utf-8")
    return manifest


def test_discover_uses_exact_problem_layout_and_stable_order(tmp_path: Path) -> None:
    second = _write_problem(tmp_path, "leetcode", "0002", 'title = "Two"\n')
    first = _write_problem(tmp_path, "acwing", "0001", 'title = "One"\n')
    nested = tmp_path / "problems" / "leetcode" / "drafts" / "0003" / "problem.toml"
    nested.parent.mkdir(parents=True)
    nested.write_text('title = "Draft"\n', encoding="utf-8")

    assert discover(tmp_path) == (first, second)


def test_aggregate_counts_activity_across_platforms_and_filters_year(tmp_path: Path) -> None:
    _write_problem(
        tmp_path,
        "leetcode",
        "0001-two-sum",
        """
title = "Two Sum"

[[activity]]
type = "ac"
date = 2026-08-01

[[activity]]
type = "NOTE"
date = "2026-08-01"

[[activity]]
type = "review"
date = 2026-08-02

[[activity]]
type = "attempt"
date = 2026-08-02

[[activity]]
type = "ac"
date = 2025-12-31
""".lstrip(),
    )
    _write_problem(
        tmp_path,
        "deep-ml",
        "0001",
        """
[[activity]]
type = "ac"
date = 2026-08-01
""".lstrip(),
    )

    _write_problem(
        tmp_path,
        "unsupported",
        "0001",
        '[[activity]]\ntype = "ac"\ndate = 2026-08-01\n',
    )

    assert aggregate_activity(tmp_path, 2026) == {
        date(2026, 8, 1): 3,
        date(2026, 8, 2): 1,
    }


def test_aggregate_ignores_malformed_events_but_reports_invalid_toml(tmp_path: Path) -> None:
    _write_problem(
        tmp_path,
        "leetcode",
        "invalid-events",
        """
[[activity]]
type = 7
date = 2026-01-01

[[activity]]
type = "ac"
date = "not-a-date"
""".lstrip(),
    )
    assert aggregate_activity(tmp_path, 2026) == {}

    _write_problem(tmp_path, "leetcode", "broken", "this = [is not valid")
    with pytest.raises(HeatmapDataError, match="cannot read"):
        aggregate_activity(tmp_path, 2026)


def test_render_is_deterministic_static_and_records_intensity() -> None:
    counts = {
        date(2026, 1, 1): 1,
        date(2026, 1, 2): 2,
        date(2026, 1, 3): 4,
        date(2025, 12, 31): 99,
    }

    first = render_heatmap(2026, counts)
    second = render_heatmap(2026, dict(reversed(tuple(counts.items()))))

    assert first == second
    assert "<script" not in first.lower()
    assert "animate" not in first.lower()
    assert "3 EVENTS · 3 ACTIVE DAYS" not in first
    assert "7 EVENTS · 3 ACTIVE DAYS" in first
    assert 'data-date="2026-01-01" data-count="1" data-level="1"' in first
    assert 'data-date="2026-01-02" data-count="2" data-level="2"' in first
    assert 'data-date="2026-01-03" data-count="4" data-level="4"' in first
    assert "@media (prefers-color-scheme: dark)" in first
    assert 'class="heatmap-cell heatmap-level-1"' in first
    for color in ("#f6f8fa", "#e8ecf1", "#1d1e2c", "#34384a", "#a5f3fc"):
        assert color in first
    ET.fromstring(first)


@pytest.mark.parametrize(
    ("year", "expected_days"),
    ((2025, 365), (2024, 366)),
)
def test_empty_heatmap_contains_every_day(year: int, expected_days: int) -> None:
    svg = render_heatmap(year, {})
    document = ET.fromstring(svg)
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    day_cells = [
        cell for cell in document.findall("svg:rect", namespace) if "data-date" in cell.attrib
    ]

    assert len(day_cells) == expected_days
    assert "0 counted activities across 0 active days" in svg
    assert "0 EVENTS · 0 ACTIVE DAYS" in svg


def test_generate_and_check_mode_detect_stale_assets_without_writing(tmp_path: Path) -> None:
    _write_problem(
        tmp_path,
        "leetcode",
        "0001-two-sum",
        """
[[activity]]
type = "ac"
date = 2026-08-01
""".lstrip(),
    )

    changed = generate_heatmaps(tmp_path, 2026)
    assert tuple(path.name for path in changed) == ("total.svg",)
    assert check_heatmaps(tmp_path, 2026)
    assert generate_heatmaps(tmp_path, 2026, check=True) == ()

    total = tmp_path / "assets" / "heatmaps" / "total.svg"
    total.write_text("stale\n", encoding="utf-8")
    stale = generate_heatmaps(tmp_path, 2026, check=True)
    assert stale == (total,)
    assert total.read_text(encoding="utf-8") == "stale\n"

    assert generate_heatmaps(tmp_path, 2026) == (total,)
    assert check_heatmaps(tmp_path, 2026)


def test_rejects_invalid_year(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="year"):
        render_heatmap(0, {})
