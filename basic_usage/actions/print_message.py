from flower import ActionProtocol


class PrintMessage(ActionProtocol):
    def __call__(self, context, workflow_context, params):
        context["count"] = workflow_context.get("count", 0) + 1
        print(f'{params["message"]} - {context["count"]}')
