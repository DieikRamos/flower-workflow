from typing import Protocol, runtime_checkable


@runtime_checkable
class ActionProtocol(Protocol):
    should_parse_params: bool = True

    @staticmethod
    def __call__(self, context, workflow_context, params):
        ...
