from flower import ActionProtocol


class PrintMessage(ActionProtocol):
    def __call__(self, context, params):
        context["count"] = context.get("count", 0) + 1
        print(f'{params["message"]} - {context["count"]}')
