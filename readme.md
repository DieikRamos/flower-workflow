# Flower

Flower is a lightweight Python workflow engine for defining data-fetching and transformation flows in YAML, then running them with Python actions.

It is useful when you want workflow definitions to stay declarative while keeping custom behavior in normal Python classes.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Workflow Schema](#workflow-schema)
- [Built-in Actions](#built-in-actions)
- [Custom Actions](#custom-actions)
- [FastAPI Example](#fastapi-example)
- [Development](#development)
- [Project Review](#project-review)
- [Core Components](#core-components)

## Features

- Define workflows with YAML files.
- Merge multiple schema files into one runtime schema.
- Execute steps with dependency ordering.
- Run independent steps concurrently.
- Reuse workflows as sub-workflows.
- Use built-in HTTP request and mapping actions.
- Add custom Python actions with a small callable protocol.
- Expose workflows through FastAPI or any other Python interface.

## Installation

This project uses Poetry for packaging.

```bash
poetry install
```

If Poetry is not available, install the package in a virtual environment with your preferred Python packaging tool.

## Quick Start

Create a workflow file:

```yaml
context:
  base_url: "https://openlibrary.org"

workflows:
  get_author:
    params:
      author_key: str
    steps:
      request_author:
        action: http_request
        params:
          method: "GET"
          path: /authors/{author_key}.json
          path_params:
            author_key: params["author_key"]
      output:
        action: basic_mapping
        depends: [request_author]
        params:
          key: context["request_author"].get("key")
          name: context["request_author"].get("name")
```

Run it from Python:

```python
from flower import Flower

flower = Flower(["workflows.yml"])

result = flower.run("get_author", {"author_key": "OL23919A"})
print(result)
```

## Workflow Schema

Schemas are YAML documents with two important top-level sections:

- `context`: shared values available to all steps.
- `workflows`: named workflows that define params and steps.

Each step defines an `action`, optional `depends`, and `params`.

```yaml
steps:
  step_name:
    action: basic_mapping
    depends: [another_step]
    params:
      message: params["message"]
```

Parameter expressions are evaluated with `params` and `context` in scope. Because expressions are evaluated as Python, workflow files should be treated as trusted input.

## Built-in Actions

- `http_request`: calls an HTTP endpoint using `requests`.
- `basic_mapping`: returns parsed params as a dictionary.
- `list_mapping`: maps a list into a new list, with optional filtering.

## Custom Actions

Custom actions implement `ActionProtocol`.

```python
from flower import ActionProtocol


class PrintMessage(ActionProtocol):
    should_parse_params = True

    def __call__(self, context, workflow_context, params):
        print(params["message"])
        return params["message"]
```

Register custom actions when creating `Flower`:

```python
from flower import Flower

flower = Flower(
    ["workflows.yml"],
    actions={"print_message": PrintMessage()},
)
```

## FastAPI Example

The `basic_usage` folder contains a FastAPI app that exposes a workflow as an endpoint.

```bash
cd basic_usage
python basic_usage.py
```

Then call:

```bash
curl -H "Authorization: demo" http://localhost:8080/author_summary/OL23919A
```

## Development

Recommended local checks:

```bash
poetry install
poetry run python -c "from flower import Flower; print(Flower)"
poetry run black .
poetry run pre-commit run --all-files
```

AI contributor guidance is available in `AGENTS.md` and `.github/copilot-instructions.md`.

## Project Review

Initial review notes:

- Runtime dependency alignment was updated so `requests` is installed with the package, because `flower.actions.http_request` imports it directly.
- Package metadata now points to the existing `readme.md` file.
- Black's target version now matches the package's Python 3.10+ requirement.
- There is no automated test suite yet. Runner behavior, parameter parsing, schema merging, and built-in actions are the highest-value areas to test next.
- `eval` powers parameter expressions. That keeps workflows flexible, but schemas should be considered trusted code.

## Core Components

- `Flower`: public entry point that loads schemas and registers actions.
- `FlowerRunner`: executes workflow steps and resolves dependencies.
- `Schema`, `Workflow`, and `ActionCall`: dataclasses that model the workflow definition.
- `ActionProtocol`: callable interface for built-in and custom actions.
