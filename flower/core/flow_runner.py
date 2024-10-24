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

        output = {}
        executed_steps = []
        pending_steps = list(workflow_definition.steps.items())

        while pending_steps:
            current_steps = []
            for key, step in pending_steps:
                if step.depends is None or all(item in executed_steps for item in step.depends):
                    current_steps.append((key, step))

            pending_steps = [item for item in pending_steps if item not in current_steps]
            args = [(key, step, context, workflow_params, output) for key, step in current_steps]

            execute(lambda a: self.__run_step(*a), args)
            executed_steps.extend(key for key, step in current_steps)

        return output.get("output")

    def __run_step(self, key, step, context, workflow_params, output):
        action = self.schema.actions.get(step.action)

        if action:
            parsed_params = parse_params(action_params=step.params, context=context, params=workflow_params)

            output["output"] = context[key] = action(
                context=context, workflow_context=workflow_params, params=parsed_params
            )
        else:
            sub_workflow = self.schema.workflows.get(step.action)
            if sub_workflow:
                sub_flow_runner = FlowerRunner(self.schema, step.action, workflow_params)
                output["output"] = context[key] = sub_flow_runner.run()

        return output
