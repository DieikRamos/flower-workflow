"""Tests for BasicMapping and ListMapping actions."""

import pytest
from flower.actions.mapping import BasicMapping, ListMapping
from flower.models.protocols import ActionProtocol


CTX = {}
WF = {}


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

def test_basic_mapping_satisfies_protocol():
    assert isinstance(BasicMapping(), ActionProtocol)


def test_list_mapping_satisfies_protocol():
    assert isinstance(ListMapping(), ActionProtocol)


def test_basic_mapping_parses_params():
    assert BasicMapping.should_parse_params is True


def test_list_mapping_does_not_parse_params():
    assert ListMapping.should_parse_params is False


# ---------------------------------------------------------------------------
# BasicMapping
# ---------------------------------------------------------------------------

def test_basic_mapping_returns_params_as_is():
    action = BasicMapping()
    result = action(context=CTX, workflow_context=WF, params={"a": 1, "b": "two"})
    assert result == {"a": 1, "b": "two"}


def test_basic_mapping_with_empty_params():
    action = BasicMapping()
    assert action(context=CTX, workflow_context=WF, params={}) == {}


# ---------------------------------------------------------------------------
# ListMapping
# ---------------------------------------------------------------------------

def test_list_mapping_maps_list():
    action = ListMapping()
    items = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    context = {"data": items}
    result = action(
        context=context,
        workflow_context=WF,
        params={
            "input": 'context["data"]',
            "output": {"label": 'params["name"]'},
        },
    )
    assert result == [{"label": "Alice"}, {"label": "Bob"}]


def test_list_mapping_filters_items():
    action = ListMapping()
    items = [{"val": 1}, {"val": None}, {"val": 3}]
    context = {"data": items}
    result = action(
        context=context,
        workflow_context=WF,
        params={
            "input": 'context["data"]',
            "filter": 'params["val"] is not None',
            "output": {"v": 'params["val"]'},
        },
    )
    assert result == [{"v": 1}, {"v": 3}]


def test_list_mapping_empty_input():
    action = ListMapping()
    context = {"data": []}
    result = action(
        context=context,
        workflow_context=WF,
        params={"input": 'context["data"]', "output": {"x": 'params["x"]'}},
    )
    assert result == []
