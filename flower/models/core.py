from typing import Any, Dict, List, Optional

from pydantic.main import BaseModel

from flower import ActionProtocol


class ActionCall(BaseModel):
    action: str
    params: Dict[str, Any]
    depends: Optional[List[str]]


class Workflow(BaseModel):
    steps: dict[str, ActionCall]


class Schema(BaseModel):
    context: Optional[Dict[str, Any]]
    actions: Dict[str, ActionProtocol]
    workflows: Dict[str, Workflow]

    class Config:
        arbitrary_types_allowed = True
