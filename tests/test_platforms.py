from __future__ import annotations

import pytest

from axiom_gauntlet.platforms import (
    PLATFORM_SPECS,
    PlatformRegistryError,
    canonical_platform_problem_id,
    normalize_platform_problem_id,
    parse_platform_registry,
)


def test_bundled_registry_drives_existing_platform_behavior() -> None:
    assert PLATFORM_SPECS["leetcode"].canonical_width == 4
    assert PLATFORM_SPECS["codeforces"].default_difficulty_scheme == "rating"
    assert PLATFORM_SPECS["deep-ml"].label == "Deep-ML"
    assert PLATFORM_SPECS["deep-ml"].coverage_categories == (
        "linear-algebra",
        "machine-learning",
        "deep-learning",
        "nlp",
        "computer-vision",
    )


def test_data_only_platform_entry_uses_generic_slug_strategy() -> None:
    registry = parse_platform_registry(
        {
            "version": 1,
            "platforms": {
                "example-oj": {
                    "label": "Example OJ",
                    "id_strategy": "slug",
                    "default_difficulty_scheme": "level",
                }
            },
        }
    )
    spec = registry["example-oj"]

    assert normalize_platform_problem_id(spec, "ABC-12") == "ABC-12"
    assert canonical_platform_problem_id(spec, "ABC-12") == "ABC-12"


@pytest.mark.parametrize(
    "raw",
    (
        {"version": 2, "platforms": {"oj": {}}},
        {
            "version": 1,
            "platforms": {
                "Bad Slug": {
                    "label": "Bad",
                    "id_strategy": "slug",
                    "default_difficulty_scheme": "level",
                }
            },
        },
        {
            "version": 1,
            "platforms": {
                "oj": {
                    "label": "OJ",
                    "id_strategy": "contest-index",
                    "canonical_width": 4,
                    "default_difficulty_scheme": "rating",
                }
            },
        },
    ),
)
def test_registry_rejects_invalid_contracts(raw: dict[str, object]) -> None:
    with pytest.raises(PlatformRegistryError):
        parse_platform_registry(raw)
