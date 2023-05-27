from typing import Any, Dict, List

from pydantic.main import BaseModel

from flower import ActionProtocol


class ActionCall(BaseModel):
    action: str
    params: Dict[str, Any]


class Workflow(BaseModel):
    steps: List[ActionCall]


class Schema(BaseModel):
    actions: Dict[str, ActionProtocol]
    workflows: Dict[str, Workflow]

    class Config:
        arbitrary_types_allowed = True
