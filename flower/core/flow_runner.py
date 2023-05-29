from typing import Dict, Any

from flower.core.functions import parse_params, execute
from flower.models.core import Schema


class FlowerRunner:
    def __init__(self, schema: Schema, workflow: str, params: Dict[str, Any]):
        self.schema = schema
        self.workflow = workflow
        self.params = params

    def run(self):
        context = self.schema.context.copy()
        workflow_params = self.params
        workflow_definition = self.schema.workflows.get(self.workflow)

        result = {}
        executed_steps = []
        pending_steps = [item for item in workflow_definition.steps.items()]

        while len(pending_steps) > 0:
            steps_to_call = []
            for key, step in pending_steps:
                if step.depends is None or all([item in executed_steps for item in step.depends]):
                    steps_to_call.append((key, step))

            pending_steps = [item for item in pending_steps if item not in steps_to_call]
            args = [(step, context, workflow_params, key, result) for key, step in steps_to_call]

            execute(lambda x: self.run_step(*x), args)
            executed_steps.extend([key for key, step in steps_to_call])

        return result["output"]

    def run_step(self, step, context, workflow_params, key, result):
        action = self.schema.actions.get(step.action)

        if action:
            parsed_params = parse_params(action_params=step.params,context=context, params=workflow_params)

            result["output"] = context[key] = action.__call__(context=context,
                                                              workflow_context=workflow_params,
                                                              params=parsed_params)
        else:
            if self.schema.workflows.get(step.action):
                sub_flow_runner = FlowerRunner(self.schema, step.action, workflow_params)
                result["output"] = context[key] = sub_flow_runner.run()

        return result
