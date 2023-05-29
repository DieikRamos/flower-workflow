from typing import Protocol, runtime_checkable


@runtime_checkable
class ActionProtocol(Protocol):
    @staticmethod
    def __call__(self, context, workflow_context, params):
        ...
