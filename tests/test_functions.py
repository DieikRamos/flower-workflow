"""Tests for load_schema, merge_dicts, parse_params, and eval_param."""

import os
import tempfile

import pytest
import yaml

from flower.core.functions import load_schema, merge_dicts, parse_params, eval_param


# ---------------------------------------------------------------------------
# load_schema
# ---------------------------------------------------------------------------

def _write(tmp_path, name, data):
    p = os.path.join(tmp_path, name)
    with open(p, "w") as f:
        yaml.dump(data, f)
    return p


def test_load_schema_single_file(tmp_path):
    path = _write(tmp_path, "s.yml", {"context": {"k": "v"}, "workflows": {}})
    schema = load_schema([path])
    assert schema["context"]["k"] == "v"


def test_load_schema_merges_multiple_files(tmp_path):
    a = _write(tmp_path, "a.yml", {"context": {"x": 1}, "workflows": {"flow_a": {}}})
    b = _write(tmp_path, "b.yml", {"context": {"y": 2}, "workflows": {"flow_b": {}}})
    schema = load_schema([a, b])
    assert schema["context"] == {"x": 1, "y": 2}
    assert "flow_a" in schema["workflows"]
    assert "flow_b" in schema["workflows"]


def test_load_schema_rejects_python_object_tags(tmp_path):
    """yaml.safe_load must refuse !!python/object tags (security fix)."""
    path = os.path.join(tmp_path, "evil.yml")
    with open(path, "w") as f:
        f.write("key: !!python/object/apply:os.system ['echo pwned']\n")
    with pytest.raises(yaml.YAMLError):
        load_schema([path])


def test_load_schema_closes_file_handle(tmp_path):
    """open() must be used as a context manager so the handle is always closed."""
    from unittest.mock import patch, mock_open
    import yaml as _yaml

    path = _write(tmp_path, "s.yml", {"context": {}, "workflows": {}})
    yaml_text = open(path).read()

    m = mock_open(read_data=yaml_text)
    with patch("builtins.open", m):
        load_schema([path])

    handle = m()
    handle.__enter__.assert_called()
    handle.__exit__.assert_called()


# ---------------------------------------------------------------------------
# merge_dicts
# ---------------------------------------------------------------------------

def test_merge_dicts_non_overlapping_keys():
    result = dict(merge_dicts({"a": 1}, {"b": 2}))
    assert result == {"a": 1, "b": 2}


def test_merge_dicts_second_wins_on_scalar_conflict():
    result = dict(merge_dicts({"a": 1}, {"a": 2}))
    assert result == {"a": 2}


def test_merge_dicts_deep_merge():
    result = dict(merge_dicts({"ctx": {"x": 1}}, {"ctx": {"y": 2}}))
    assert result == {"ctx": {"x": 1, "y": 2}}


# ---------------------------------------------------------------------------
# eval_param and parse_params
# ---------------------------------------------------------------------------

def test_eval_param_resolves_params():
    assert eval_param('params["key"]', {"key": "hello"}, {}) == "hello"


def test_eval_param_resolves_context():
    assert eval_param('context["val"] + 1', {}, {"val": 10}) == 11


def test_parse_params_evaluates_string_expressions():
    result = parse_params({"out": 'params["x"] * 2'}, context={}, params={"x": 5})
    assert result == {"out": 10}


def test_parse_params_fallback_on_bad_expression():
    result = parse_params(
        {"out": {"expression": "params['missing']", "fallback_value": "default"}},
        context={},
        params={},
    )
    assert result["out"] == "default"


def test_parse_params_raises_on_bad_expression_without_fallback():
    """Without fallback_value, a broken expression must propagate, not be swallowed."""
    with pytest.raises(Exception):
        parse_params({"out": 'params["nonexistent_key"]'}, context={}, params={})


def test_parse_params_nested_dict():
    result = parse_params(
        {"nested": {"a": '1 + 1', "b": '"hello"'}},
        context={},
        params={},
    )
    assert result == {"nested": {"a": 2, "b": "hello"}}
