import os
import tempfile

import pytest
import yaml

from flower import Flower, ActionProtocol


MINIMAL_SCHEMA = {
    "context": {},
    "workflows": {
        "hello": {
            "params": {},
            "steps": {
                "output": {
                    "action": "basic_mapping",
                    "params": {"msg": "hello"},
                }
            },
        }
    },
}


def _write_schema(tmp_path, data):
    p = tmp_path / "schema.yml"
    p.write_text(yaml.dump(data))
    return str(p)


class CustomAction(ActionProtocol):
    should_parse_params = False

    def __call__(self, context, workflow_context, params):
        return "custom"


def test_custom_actions_do_not_leak_between_instances(tmp_path):
    """
    Creating two Flower instances with different custom actions must not
    contaminate each other's registries. Previously, schema_dict["actions"]
    pointed at the module-level default_actions dict, so .update() would
    mutate it in place and affect all subsequent instances.
    """
    schema_file = _write_schema(tmp_path, MINIMAL_SCHEMA)

    custom = CustomAction()
    flower_a = Flower([schema_file], actions={"my_action": custom})
    flower_b = Flower([schema_file])

    assert "my_action" in flower_a.schema.actions
    assert "my_action" not in flower_b.schema.actions


def test_default_actions_present_in_every_instance(tmp_path):
    schema_file = _write_schema(tmp_path, MINIMAL_SCHEMA)

    flower = Flower([schema_file])

    assert "http_request" in flower.schema.actions
    assert "basic_mapping" in flower.schema.actions
    assert "list_mapping" in flower.schema.actions
