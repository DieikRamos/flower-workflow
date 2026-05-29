# AI Contributor Guide

This project is a small Python workflow engine. Keep changes focused and favor simple, readable code over new abstractions.

## Project Map

- `flower/__init__.py` exposes the public `Flower` API and registers built-in actions.
- `flower/core/functions.py` handles schema loading, recursive dict merging, parameter evaluation, and concurrent execution.
- `flower/core/runner.py` executes workflow steps and resolves dependencies.
- `flower/models/` contains dataclasses and the action protocol.
- `flower/actions/` contains built-in actions such as HTTP requests and mappings.
- `basic_usage/` is a runnable FastAPI example using YAML workflow files.

## Local Commands

Use Poetry when it is available:

```bash
poetry install
poetry run python -c "from flower import Flower; print(Flower)"
poetry run black .
poetry run pre-commit run --all-files
```

Without Poetry, create a virtual environment and install the runtime dependencies from `pyproject.toml`.

## Coding Notes

- Workflow schemas are YAML files with top-level `context` and `workflows` keys.
- Built-in actions implement `ActionProtocol` and are callable with `(context, workflow_context, params)`.
- `should_parse_params = True` means action params are evaluated before the action receives them.
- Parameter expressions are evaluated with `params` and `context` in scope. Treat workflow YAML as trusted input.
- The runner stores each step result in `context[step_name]` and returns the final `output` step value.

## Review Checklist

- Verify runtime imports are listed as runtime dependencies, not only dev dependencies.
- Keep examples in `basic_usage/resources/*.yml` aligned with the public README.
- Add or update tests when changing runner behavior, parameter parsing, dependency ordering, or built-in actions.
- Do not rename the public package import (`flower`) without updating examples and packaging metadata.
