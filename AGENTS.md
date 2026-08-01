# Repository guidance

- Use `uv` for Python versions, dependencies, commands, and lockfile updates.
- Run `uv sync --locked --all-groups` after cloning. After changing `pyproject.toml`, run
  `uv lock` and then sync the locked environment.
- Treat each `problem.toml` as the machine-readable source of truth.
- Keep human reasoning in the adjacent problem `README.md`; do not copy full problem statements.
- Never infer an online-judge Accepted verdict from compilation or local tests. Record `ac` only
  after the platform confirms it.
- Do not edit files under `assets/heatmaps/` by hand. Regenerate them with
  `uv run axiom render`.
- Before handing off changes, run `make verify`.
