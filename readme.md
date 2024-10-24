Here's a README for the Flower project based on the provided code:

# Flower

Flower is a flexible and extensible workflow execution engine that allows you to define and run complex workflows using YAML schemas and Python actions.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Core Components](#core-components)
- [Built-in Actions](#built-in-actions)
- [Extending Flower](#extending-flower)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Define workflows using YAML schemas
- Execute workflows with dependencies between steps
- Support for custom actions
- Built-in HTTP request and mapping actions
- Concurrent execution of independent steps
- Dynamic parameter parsing and evaluation
- FastAPI integration for exposing workflows as API endpoints

## Installation

To install Flower, you can use pip:

```bash
pip install flower-workflow-engine
```

(Note: This is a placeholder. Adjust based on the actual package name and installation method.)

## Usage

Here's a basic example of how to use Flower:

```python
from flower import Flower

# Initialize Flower with your schema files
flower = Flower(["path/to/your/schema.yaml"])

# Run a workflow
result = flower.run("your_workflow_name", {"param1": "value1", "param2": "value2"})
```

## Core Components

### Flower

The main class that initializes the workflow engine with schema files and custom actions.

### FlowerRunner

Responsible for executing workflows, managing step dependencies, and handling the execution context.

### Schema

Represents the structure of your workflows, including context, actions, and workflow definitions.

### ActionProtocol

A protocol that defines the interface for custom actions.

## Built-in Actions

- **HttpRequest**: Performs HTTP requests with customizable parameters.
- **BasicMapping**: A simple action for parameter mapping.
- **ListMapping**: Performs mapping operations on lists with optional filtering.

## Extending Flower

You can extend Flower by creating custom actions:

1. Create a class that implements the `ActionProtocol`.
2. Define the `__call__` method with the signature `(self, context, workflow_context, params)`.
3. Set the `should_parse_params` attribute to control parameter parsing behavior.
4. Add your custom action when initializing Flower:

```python
from flower import Flower
from your_module import YourCustomAction

flower = Flower(
    ["path/to/your/schema.yaml"],
    actions={"your_custom_action": YourCustomAction()}
)
```

## Real World Example - API Integration

Flower can be easily integrated with FastAPI to expose workflows as API endpoints:

```python
from fastapi import FastAPI, Header
from flower import Flower

app = FastAPI()
flower = Flower(["path/to/your/schema.yaml"])

@app.get("/your_endpoint/{param}")
def call_workflow(param: str, authorization: str = Header(alias="Authorization")):
    context = {"param": param, "authorization": authorization}
    result = flower.run("your_workflow", context)
    return result
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify the license here, e.g., MIT, Apache 2.0, etc.]

---

This README provides an overview of the Flower project, its main components, and basic usage instructions. It also includes information about the built-in actions, how to extend Flower with custom actions, and how to integrate it with FastAPI. You may want to expand on certain sections, add examples of schema files, or include more detailed API documentation depending on the intended audience and the complexity of your project.