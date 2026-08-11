# Repository guidance

- Use `uv` for Python versions, dependencies, commands, and lockfile updates.
- Run `uv sync --locked --all-groups` after cloning. After changing `pyproject.toml`, run
  `uv lock` and then sync the locked environment.
- Treat each `problem.toml` as the source of truth for problem evidence and each `topic.toml` as the
  source of truth for reusable knowledge.
- Keep problem READMEs as lightweight source cards. Put semantically aligned reusable reasoning in
  `knowledge/<category>/<topic>/README.md` and `README_zh-CN.md`; do not copy full statements.
- Never infer an online-judge Accepted verdict from compilation or local tests. Record `ac` only
  after the platform confirms it.
- Use `uv run axiom accept` and `uv run axiom knowledge document/review` for lifecycle transitions
  instead of editing state and activity fields by hand. Acceptance must record time and auxiliary
  space complexity for the accepted language.
- Treat the Git lifecycle as part of weekday practice bookkeeping. Before the first repository
  mutation of the day, update a clean `main` with `git pull --ff-only`, then create or reuse the
  Asia/Shanghai-dated `practice/YYYY-MM-DD` branch. Reuse that branch for all practice that day and
  never commit practice changes directly to `main`.
- Keep weekday solving in the problem workflow and delayed synthesis in a short-lived
  `notes/YYYY-MM-DD` branch.
- Regenerate knowledge indexes with `uv run axiom knowledge render`; do not edit them by hand.
- Use Conventional Commits for human-authored and automated commits.
- Do not edit files under `assets/heatmaps/` by hand. Regenerate them with
  `uv run axiom render`.
- Do not edit files under `assets/dashboards/` by hand. Regenerate them with
  `uv run axiom render`.
- Do not edit README content between the `recent-problems` markers by hand. Regenerate it with
  `uv run axiom render`.
- Before handing off changes, run `make verify`.
- After verification, commit only the session changes with a Conventional Commit, push the daily
  practice branch, and create or update its pull request against `main`. Do not merge the pull
  request unless the user explicitly asks.
