from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from axiom_gauntlet.coverage import (
    aggregate_coverage,
    generate_coverage,
    render_coverage_svg,
)


def _write_problem(
    root: Path,
    *,
    platform: str,
    directory_id: str,
    problem_id: str,
    difficulty_scheme: str,
    difficulty_value: str | int,
    normalized: str,
    tags: tuple[str, ...] = (),
    languages: tuple[str, ...] = (),
) -> None:
    tag_values = ", ".join(f'"{tag}"' for tag in tags)
    value = f'"{difficulty_value}"' if isinstance(difficulty_value, str) else difficulty_value
    activities = "\n".join(
        f'[[activity]]\ntype = "ac"\ndate = 2026-08-08\nlanguage = "{language}"'
        for language in languages
    )
    manifest = root / "problems" / platform / directory_id / "problem.toml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        f"""version = 1
uid = "{platform}:{directory_id}"
platform = "{platform}"
problem_id = "{problem_id}"
title = "Example"
url = "https://example.com/{problem_id}"
state = "accepted"
tags = [{tag_values}]

[difficulty]
scheme = "{difficulty_scheme}"
value = {value}
normalized = "{normalized}"

{activities}
""",
        encoding="utf-8",
    )


def _sample_repository(root: Path) -> None:
    _write_problem(
        root,
        platform="leetcode",
        directory_id="0001",
        problem_id="1",
        difficulty_scheme="level",
        difficulty_value="Easy",
        normalized="easy",
        languages=("python",),
    )
    _write_problem(
        root,
        platform="leetcode",
        directory_id="0002",
        problem_id="2",
        difficulty_scheme="level",
        difficulty_value="Hard",
        normalized="hard",
        languages=("cpp", "python"),
    )
    _write_problem(
        root,
        platform="codeforces",
        directory_id="4A",
        problem_id="4A",
        difficulty_scheme="rating",
        difficulty_value=1200,
        normalized="easy",
        languages=("cpp",),
    )
    _write_problem(
        root,
        platform="deep-ml",
        directory_id="1",
        problem_id="1",
        difficulty_scheme="level",
        difficulty_value="Medium",
        normalized="medium",
        tags=("linear-algebra",),
        languages=("python",),
    )


def _populated_repository(root: Path) -> None:
    _sample_repository(root)
    for problem_id, level, normalized, language in (
        ("1", "Easy", "easy", "python"),
        ("2", "Medium", "medium", "cpp"),
    ):
        _write_problem(
            root,
            platform="acwing",
            directory_id=problem_id,
            problem_id=problem_id,
            difficulty_scheme="level",
            difficulty_value=level,
            normalized=normalized,
            languages=(language,),
        )

    for index, rating in enumerate((800, 1000, 1400, 1600), start=1):
        problem_id = f"{100 + index}A"
        _write_problem(
            root,
            platform="codeforces",
            directory_id=problem_id,
            problem_id=problem_id,
            difficulty_scheme="rating",
            difficulty_value=rating,
            normalized="medium",
            languages=(("cpp", "go") if rating == 1600 else ("cpp",)),
        )

    deep_ml_examples = (
        (2, "Easy", "easy", "linear-algebra"),
        (3, "Medium", "medium", "machine-learning"),
        (4, "Hard", "hard", "machine-learning"),
        (5, "Hard", "hard", "deep-learning"),
        (6, "Easy", "easy", "nlp"),
        (7, "Medium", "medium", "computer-vision"),
    )
    for problem_id, level, normalized, category in deep_ml_examples:
        _write_problem(
            root,
            platform="deep-ml",
            directory_id=str(problem_id),
            problem_id=str(problem_id),
            difficulty_scheme="level",
            difficulty_value=level,
            normalized=normalized,
            tags=(category,),
            languages=(("python", "go") if problem_id == 7 else ("python",)),
        )


def test_aggregate_uses_native_profiles_and_unique_problem_languages(tmp_path: Path) -> None:
    _sample_repository(tmp_path)

    snapshot = aggregate_coverage(tmp_path)
    platforms = {coverage.spec.slug: coverage for coverage in snapshot.platforms}

    assert snapshot.accepted_problems == 4
    assert snapshot.active_platforms == 3
    assert snapshot.languages == {"Python": 3, "C++": 2}
    assert platforms["leetcode"].difficulty == {"easy": 1, "hard": 1}
    assert platforms["codeforces"].ratings == {"1200–1399": 1}
    assert platforms["deep-ml"].categories == {"linear-algebra": 1}
    assert platforms["acwing"].accepted == 0


def test_render_is_static_accessible_and_keeps_empty_platforms_compact(tmp_path: Path) -> None:
    _sample_repository(tmp_path)

    svg = render_coverage_svg(aggregate_coverage(tmp_path))

    assert "Practice Coverage" in svg
    assert "4 accepted problems across 3 active platforms" in svg
    assert 'data-ring="platform"' in svg
    assert 'data-ring="language"' in svg
    assert "OUTER PLATFORM · INNER LANGUAGE" in svg
    assert "Native profiles" in svg
    assert "@media (prefers-color-scheme: dark)" in svg
    assert 'class="coverage-background"' in svg
    for color in ("#f6f8fa", "#e8ecf1", "#1d1e2c", "#34384a"):
        assert color in svg
    assert "1200–1399 1" in svg
    assert "Linear Algebra 1" in svg
    assert "No accepted problems yet" in svg
    assert "<script" not in svg.lower()
    assert "animate" not in svg.lower()
    ET.fromstring(svg)


def test_render_handles_populated_native_profiles(tmp_path: Path) -> None:
    _populated_repository(tmp_path)

    snapshot = aggregate_coverage(tmp_path)
    svg = render_coverage_svg(snapshot)

    platforms = {coverage.spec.slug: coverage for coverage in snapshot.platforms}
    assert platforms["codeforces"].ratings == {
        "≤999": 1,
        "1000–1199": 1,
        "1200–1399": 1,
        "1400–1599": 1,
        "1600+": 1,
    }
    assert platforms["deep-ml"].difficulty == {"easy": 2, "medium": 3, "hard": 2}
    assert platforms["deep-ml"].categories == {
        "linear-algebra": 2,
        "machine-learning": 2,
        "deep-learning": 1,
        "nlp": 1,
        "computer-vision": 1,
    }
    assert snapshot.active_platforms == 4
    assert snapshot.languages == {"Python": 10, "C++": 7, "Go": 2}
    assert 'data-segment="1600+" data-count="1"' in svg
    assert "≤999 → 1600+ · 5 problems" in svg
    assert "Linear Algebra 2 · ML 2 · CV 1" in svg
    ET.fromstring(svg)


def test_generate_and_check_detect_stale_dashboard_without_writing(tmp_path: Path) -> None:
    _sample_repository(tmp_path)

    changed = generate_coverage(tmp_path)
    assert tuple(path.name for path in changed) == ("practice-coverage.svg",)
    assert generate_coverage(tmp_path, check=True) == ()

    output = tmp_path / "assets" / "dashboards" / "practice-coverage.svg"
    output.write_text("stale\n", encoding="utf-8")
    assert generate_coverage(tmp_path, check=True) == (output,)
    assert output.read_text(encoding="utf-8") == "stale\n"
