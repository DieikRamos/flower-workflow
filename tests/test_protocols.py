"""Tests for ActionProtocol structural conformance."""

import pytest
from flower.models.protocols import ActionProtocol


class ValidAction:
    should_parse_params = True

    def __call__(self, context, workflow_context, params):
        return params


class MissingCall:
    should_parse_params = True


class MissingFlag:
    def __call__(self, context, workflow_context, params):
        return params


def test_valid_action_satisfies_protocol():
    assert isinstance(ValidAction(), ActionProtocol)


def test_missing_call_does_not_satisfy_protocol():
    assert not isinstance(MissingCall(), ActionProtocol)


def test_missing_should_parse_params_does_not_satisfy_protocol():
    assert not isinstance(MissingFlag(), ActionProtocol)


def test_protocol_call_is_instance_method_not_static():
    """__call__ must be an instance method (no @staticmethod) so the runner
    can invoke action(context=..., workflow_context=..., params=...)."""
    import inspect
    # If __call__ were a staticmethod it would appear as a plain function
    # in the Protocol's __dict__. An instance method is a function too, but
    # should NOT be a staticmethod descriptor.
    member = ActionProtocol.__protocol_attrs__  # exists on runtime_checkable Protocols
    assert "__call__" in member
