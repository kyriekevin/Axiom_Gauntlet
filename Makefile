UV ?= uv

.PHONY: sync lock-check lint format format-check test validate render render-check verify

sync:
	$(UV) sync --locked --all-groups

lock-check:
	$(UV) lock --check

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

format-check:
	$(UV) run ruff format --check .

test:
	$(UV) run pytest

validate:
	$(UV) run axiom validate

render:
	$(UV) run axiom render

render-check:
	$(UV) run axiom render --check

verify: lock-check lint format-check test validate render-check
