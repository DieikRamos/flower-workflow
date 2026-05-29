"""Tests for HttpRequest action."""

from unittest.mock import patch, MagicMock

import pytest

from flower.actions.http_request import HttpRequest, RequestParams


def make_response(json_data=None, status_code=200, content=b"{}"):
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content
    resp.json.return_value = json_data or {}
    resp.raise_for_status.return_value = None
    return resp


# ---------------------------------------------------------------------------
# base_url resolution
# ---------------------------------------------------------------------------

def test_base_url_taken_from_params_when_provided():
    """If base_url is in params it must not be overwritten by context."""
    action = HttpRequest()
    resp = make_response({"ok": True})

    with patch("flower.actions.http_request.request", return_value=resp) as mock_req:
        action(
            context={"base_url": "https://wrong.example.com"},
            workflow_context={},
            params={"base_url": "https://right.example.com", "path": "/test", "method": "GET"},
        )
        called_url = mock_req.call_args.kwargs["url"]
        assert called_url.startswith("https://right.example.com")


def test_base_url_falls_back_to_context():
    """When base_url is absent from params, context["base_url"] is used."""
    action = HttpRequest()
    resp = make_response({"ok": True})

    with patch("flower.actions.http_request.request", return_value=resp) as mock_req:
        action(
            context={"base_url": "https://ctx.example.com"},
            workflow_context={},
            params={"path": "/test", "method": "GET"},
        )
        called_url = mock_req.call_args.kwargs["url"]
        assert called_url.startswith("https://ctx.example.com")


def test_base_url_missing_from_both_does_not_raise_keyerror():
    """Missing base_url must not crash with KeyError (falls back to empty string)."""
    action = HttpRequest()
    resp = make_response({"ok": True})

    with patch("flower.actions.http_request.request", return_value=resp):
        try:
            action(
                context={},
                workflow_context={},
                params={"path": "/test", "method": "GET"},
            )
        except KeyError as exc:
            pytest.fail(f"Raised KeyError for missing base_url: {exc}")


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------

def test_returns_none_for_empty_response():
    action = HttpRequest()
    resp = make_response(content=b"")

    with patch("flower.actions.http_request.request", return_value=resp):
        result = action(
            context={"base_url": "https://api.example.com"},
            workflow_context={},
            params={"path": "/empty", "method": "GET"},
        )
    assert result is None


def test_returns_parsed_json():
    action = HttpRequest()
    resp = make_response(json_data={"name": "Alice"}, content=b'{"name":"Alice"}')

    with patch("flower.actions.http_request.request", return_value=resp):
        result = action(
            context={"base_url": "https://api.example.com"},
            workflow_context={},
            params={"path": "/user", "method": "GET"},
        )
    assert result == {"name": "Alice"}


# ---------------------------------------------------------------------------
# RequestParams defaults
# ---------------------------------------------------------------------------

def test_request_logs_at_debug_not_print(capsys):
    """HTTP requests must use logging (not print) so callers can control verbosity."""
    import logging

    action = HttpRequest()
    resp = make_response({"ok": True}, content=b'{"ok":true}')

    with patch("flower.actions.http_request.request", return_value=resp):
        action(
            context={"base_url": "https://api.example.com"},
            workflow_context={},
            params={"path": "/test", "method": "GET"},
        )

    captured = capsys.readouterr()
    assert captured.out == "", "HttpRequest must not write to stdout"


def test_request_params_optional_fields_default_to_empty():
    rp = RequestParams(base_url="https://x.com", path="/", method="GET")
    assert rp.headers == {}
    assert rp.query_params == {}
    assert rp.path_params == {}
    assert rp.payload is None
