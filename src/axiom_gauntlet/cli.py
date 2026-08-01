"""Command-line interface for repository maintenance."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="axiom", description="Maintain Axiom Gauntlet.")
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root(),
        help=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new = subparsers.add_parser("new", help="Create a normalized problem entry.")
    new.add_argument("platform", choices=("leetcode", "acwing", "codeforces"))
    new.add_argument("problem_id")
    new.add_argument("--title", required=True)
    new.add_argument("--url", required=True)
    new.add_argument("--difficulty", default="unknown")
    new.add_argument("--difficulty-scheme", default=None)
    new.add_argument(
        "--normalized-difficulty",
        choices=("easy", "medium", "hard", "unknown"),
        default=None,
    )
    new.add_argument("--tag", action="append", default=[])
    new.add_argument(
        "--language",
        action="append",
        default=[],
        choices=("cpp", "python", "py", "go"),
        help="Create an optional solution stub; repeat for multiple languages.",
    )

    subparsers.add_parser("validate", help="Validate all problem entries.")

    render = subparsers.add_parser("render", help="Generate platform activity heatmaps.")
    render.add_argument(
        "--year",
        type=int,
        default=datetime.now(SHANGHAI).year,
        help="Calendar year to render (defaults to the current year in Asia/Shanghai).",
    )
    render.add_argument("--check", action="store_true")

    return parser


def _default_difficulty_scheme(platform: str) -> str:
    if platform == "codeforces":
        return "rating"
    return "level"


def _run_new(args: argparse.Namespace) -> int:
    from .scaffold import create_problem

    created = create_problem(
        args.root,
        platform=args.platform,
        problem_id=args.problem_id,
        title=args.title,
        url=args.url,
        difficulty_scheme=args.difficulty_scheme or _default_difficulty_scheme(args.platform),
        difficulty_value=args.difficulty,
        difficulty_normalized=args.normalized_difficulty,
        tags=args.tag,
        languages=args.language,
    )
    print(created.relative_to(args.root))
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    from .validate import validate_repository

    errors = validate_repository(args.root)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("Axiom Gauntlet is valid.")
    return 0


def _run_render(args: argparse.Namespace) -> int:
    from .heatmap import render_all

    changed = render_all(args.root, args.year, check=args.check)
    if args.check and changed:
        print("error: generated heatmaps are out of date")
        return 1
    if args.check:
        print("Heatmaps are up to date.")
    else:
        print(f"Rendered heatmaps for {args.year}.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            return _run_new(args)
        if args.command == "validate":
            return _run_validate(args)
        if args.command == "render":
            return _run_render(args)
    except (FileExistsError, ValueError) as error:
        parser.error(str(error))
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
