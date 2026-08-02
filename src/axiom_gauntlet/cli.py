"""Command-line interface for repository maintenance."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date, datetime
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

    accept = subparsers.add_parser("accept", help="Record a platform-confirmed AC event.")
    accept.add_argument("platform", choices=("leetcode", "acwing", "codeforces"))
    accept.add_argument("problem_id")
    accept.add_argument(
        "--language",
        required=True,
        choices=("cpp", "python", "py", "go"),
    )
    accept.add_argument("--date", type=_iso_date, default=None)
    accept.add_argument("--time-complexity", required=True)
    accept.add_argument("--space-complexity", required=True)

    document = subparsers.add_parser(
        "document", help="Record completed bilingual notes for an accepted problem."
    )
    document.add_argument("platform", choices=("leetcode", "acwing", "codeforces"))
    document.add_argument("problem_id")
    document.add_argument("--date", type=_iso_date, default=None)

    knowledge = subparsers.add_parser("knowledge", help="Maintain reusable knowledge topics.")
    knowledge_commands = knowledge.add_subparsers(dest="knowledge_command", required=True)

    knowledge_new = knowledge_commands.add_parser("new", help="Create a knowledge-topic draft.")
    knowledge_new.add_argument("path")
    knowledge_new.add_argument("--title", required=True)
    knowledge_new.add_argument("--title-zh-cn", required=True)
    knowledge_new.add_argument("--tag", action="append", default=[])
    knowledge_new.add_argument("--link", action="append", default=[])
    knowledge_new.add_argument(
        "--example",
        action="append",
        default=[],
        metavar="UID=ROLE",
        help="Link a problem UID with its role; repeat for multiple examples.",
    )

    knowledge_document = knowledge_commands.add_parser(
        "document", help="Record a completed knowledge note."
    )
    knowledge_document.add_argument("path")
    knowledge_document.add_argument("--date", type=_iso_date, default=None)

    knowledge_review = knowledge_commands.add_parser(
        "review", help="Record a later knowledge review."
    )
    knowledge_review.add_argument("path")
    knowledge_review.add_argument("--date", type=_iso_date, default=None)
    knowledge_review.add_argument("--result", choices=("pass", "fail"), required=True)

    knowledge_render = knowledge_commands.add_parser(
        "render", help="Generate knowledge indexes and activity log."
    )
    knowledge_render.add_argument("--check", action="store_true")

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


def _iso_date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from error
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    return parsed


def _event_date(value: date | None) -> date:
    return value or datetime.now(SHANGHAI).date()


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


def _run_accept(args: argparse.Namespace) -> int:
    from .lifecycle import record_acceptance

    directory = record_acceptance(
        args.root,
        platform=args.platform,
        problem_id=args.problem_id,
        language=args.language,
        event_date=_event_date(args.date),
        time_complexity=args.time_complexity,
        space_complexity=args.space_complexity,
    )
    print(f"Accepted: {directory.relative_to(args.root)}")
    return 0


def _run_document(args: argparse.Namespace) -> int:
    from .lifecycle import record_documentation

    directory = record_documentation(
        args.root,
        platform=args.platform,
        problem_id=args.problem_id,
        event_date=_event_date(args.date),
    )
    print(f"Documented: {directory.relative_to(args.root)}")
    return 0


def _parse_example(value: str) -> tuple[str, str]:
    uid, separator, role = value.partition("=")
    if not separator or not uid.strip() or not role.strip():
        raise ValueError("knowledge examples must use UID=ROLE")
    return uid.strip(), role.strip()


def _run_knowledge(args: argparse.Namespace) -> int:
    from .knowledge import create_topic, document_topic, render_indexes, review_topic

    if args.knowledge_command == "new":
        created = create_topic(
            args.root,
            topic_path=args.path,
            title=args.title,
            title_zh_cn=args.title_zh_cn,
            tags=args.tag,
            links=args.link,
            examples=tuple(_parse_example(value) for value in args.example),
        )
        print(created.relative_to(args.root))
        return 0
    if args.knowledge_command == "document":
        directory = document_topic(args.root, args.path, _event_date(args.date))
        print(f"Documented knowledge: {directory.relative_to(args.root)}")
        return 0
    if args.knowledge_command == "review":
        directory = review_topic(args.root, args.path, _event_date(args.date), args.result)
        print(f"Reviewed knowledge: {directory.relative_to(args.root)}")
        return 0
    if args.knowledge_command == "render":
        changed = render_indexes(args.root, check=args.check)
        if args.check and changed:
            print("error: generated knowledge indexes are out of date")
            return 1
        if args.check:
            print("Knowledge indexes are up to date.")
        else:
            print("Rendered knowledge indexes.")
        return 0
    raise AssertionError(f"unhandled knowledge command: {args.knowledge_command}")


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
        if args.command == "accept":
            return _run_accept(args)
        if args.command == "document":
            return _run_document(args)
        if args.command == "knowledge":
            return _run_knowledge(args)
        if args.command == "render":
            return _run_render(args)
    except (FileExistsError, ValueError) as error:
        parser.error(str(error))
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
