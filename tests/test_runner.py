"""Tests for FlowerRunner execution, dependency ordering, and parallel safety."""

import threading
import time

import pytest

from flower import ActionProtocol, Flower
from flower.core.runner import FlowerRunner
from flower.models.core import Schema, Workflow, ActionCall
from flower.actions.mapping import BasicMapping


def make_schema(steps: dict, context: dict = None) -> Schema:
    workflow = Workflow(params={}, steps=steps)
    return Schema(
        context=context or {},
        actions={"basic_mapping": BasicMapping()},
        workflows={"test_flow": workflow},
    )


# ---------------------------------------------------------------------------
# Dependency ordering
# ---------------------------------------------------------------------------

def test_output_step_result_is_returned():
    schema = make_schema(
        steps={
            "output": ActionCall(action="basic_mapping", params={"value": "42"}),
        }
    )
    runner = FlowerRunner(schema, "test_flow", {})
    assert runner.run() == {"value": 42}


def test_step_result_available_in_context_for_dependent_step():
    class EchoAction(ActionProtocol):
        should_parse_params = False

        def __call__(self, context, workflow_context, params):
            return params.get("msg", "")

    schema = make_schema(
        steps={
            "first": ActionCall(action="basic_mapping", params={"msg": "hello"}),
            "output": ActionCall(
                action="basic_mapping",
                params={"forwarded": 'context["first"]["msg"]'},
                depends=["first"],
            ),
        }
    )
    schema.actions["basic_mapping"] = BasicMapping()

    from flower import Flower
    import tempfile, yaml, os

    schema_data = {
        "context": {},
        "workflows": {
            "test_flow": {
                "params": {},
                "steps": {
                    "first": {"action": "basic_mapping", "params": {"msg": "hello"}},
                    "output": {
                        "action": "basic_mapping",
                        "depends": ["first"],
                        "params": {"forwarded": 'context["first"]["msg"]'},
                    },
                },
            }
        },
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "schema.yml")
        with open(path, "w") as f:
            yaml.dump(schema_data, f)
        flower = Flower([path])
        result = flower.run("test_flow", {})

    assert result == {"forwarded": "hello"}


# ---------------------------------------------------------------------------
# Race condition: output["output"] shared key
# ---------------------------------------------------------------------------

def test_parallel_steps_do_not_corrupt_final_output():
    """
    Run many parallel steps; only the 'output' step result must be returned.
    Previously every step wrote to a shared output["output"] dict key —
    whichever thread finished last would win non-deterministically.
    """
    write_order = []
    lock = threading.Lock()

    class SlowAction(ActionProtocol):
        should_parse_params = False

        def __init__(self, name, delay):
            self.name = name
            self.delay = delay

        def __call__(self, context, workflow_context, params):
            time.sleep(self.delay)
            with lock:
                write_order.append(self.name)
            return {"from": self.name}

    steps = {
        f"step_{i}": ActionCall(action=f"action_{i}", params={})
        for i in range(5)
    }
    steps["output"] = ActionCall(
        action="output_action",
        params={},
        depends=[f"step_{i}" for i in range(5)],
    )

    actions = {f"action_{i}": SlowAction(f"step_{i}", 0.01 * (5 - i)) for i in range(5)}
    actions["output_action"] = SlowAction("output", 0.0)

    schema = Schema(
        context={},
        actions=actions,
        workflows={"test_flow": Workflow(params={}, steps=steps)},
    )
    runner = FlowerRunner(schema, "test_flow", {})
    result = runner.run()

    assert result == {"from": "output"}, (
        f"Expected output step result but got {result!r}. Write order: {write_order}"
    )


def test_step_depends_none_treated_same_as_empty_list():
    """Steps with no depends must execute in the first batch."""
    schema = make_schema(
        steps={
            "output": ActionCall(action="basic_mapping", params={"ok": True}),
        }
    )
    runner = FlowerRunner(schema, "test_flow", {})
    assert runner.run() == {"ok": True}
