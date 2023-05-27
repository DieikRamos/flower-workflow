from typing import Dict, Any

from flower.models.core import Schema


class FlowerRunner:
    def __init__(self, schema: Schema, workflow: str, params: Dict[str, Any]):
        self.schema = schema
        self.workflow = workflow
        self.params = params

    def run(self):
        workflow_definition = self.schema.workflows.get(self.workflow)
        context = dict()
        for step in workflow_definition.steps:
            action = self.schema.actions.get(step.action)
            action_result = action.__call__(context=context, params=step.params)
