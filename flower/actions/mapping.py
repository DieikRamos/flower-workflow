from flower import ActionProtocol


class BasicMapping(ActionProtocol):
    def __call__(self, context, workflow_context, params):
        return params
