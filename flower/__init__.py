from typing import List


from flower.models.protocols import ActionProtocol
from flower.core.flow_runner import FlowerRunner
from flower.core.functions import load_schema
from flower.models.core import Schema
from flower.actions.request_http import RequestHttp
from flower.actions.mapping import BasicMapping

default_actions = {
    "request_http": RequestHttp(),
    "basic_mapping": BasicMapping()
}


class Flower:
    def __init__(self, schema_files: List[str], actions: dict[str, ActionProtocol] = None):
        schema_dict = load_schema(schema_files)

        schema_dict["actions"] = default_actions

        if actions:
            schema_dict["actions"].update(actions)

        self.schema = Schema(**schema_dict)

    def run(self, flow: str, params: dict):
        flow_runner = FlowerRunner(self.schema, flow, params)
        return flow_runner.run()


__all__ = ["Flower", "ActionProtocol"]
