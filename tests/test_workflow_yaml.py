"""
Sanity-checks on the bundled YAML workflow files:
- all sub-workflow param names match the declared params in their target workflow
- no raw string expressions leak through (i.e. params are resolvable)
"""

import os
import yaml
import pytest

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "basic_usage", "resources")
BASE_FILE = os.path.join(BASE_DIR, "base-workflows.yml")
MAIN_FILE = os.path.join(BASE_DIR, "main-workflows.yml")


def load(path):
    with open(path) as f:
        return yaml.safe_load(f)


def test_base_schema_loads():
    schema = load(BASE_FILE)
    assert "workflows" in schema
    assert "get_author_by_key" in schema["workflows"]
    assert "get_books_by_author" in schema["workflows"]


def test_main_schema_loads():
    schema = load(MAIN_FILE)
    assert "workflows" in schema
    assert "author_summary" in schema["workflows"]


def test_author_books_step_passes_correct_param_name():
    """
    The author_books step calls get_books_by_author which declares author_key.
    Before the fix it passed field_id, causing a silent KeyError at runtime.
    """
    main = load(MAIN_FILE)
    base = load(BASE_FILE)

    step_params = main["workflows"]["author_summary"]["steps"]["author_books"]["params"]
    target_declared = base["workflows"]["get_books_by_author"]["params"]

    passed_keys = set(step_params.keys())
    declared_keys = set(target_declared.keys())

    missing = declared_keys - passed_keys
    assert not missing, f"Step is missing required params for get_books_by_author: {missing}"


def test_no_undeclared_params_passed_to_sub_workflows():
    """All params passed to sub-workflows must be declared by those workflows."""
    main = load(MAIN_FILE)
    base = load(BASE_FILE)

    steps = main["workflows"]["author_summary"]["steps"]

    for step_name, step in steps.items():
        action = step["action"]
        if action in base.get("workflows", {}):
            declared = set(base["workflows"][action]["params"].keys())
            passed = set(step.get("params", {}).keys())
            undeclared = passed - declared
            assert not undeclared, (
                f"Step '{step_name}' passes undeclared params to '{action}': {undeclared}"
            )
