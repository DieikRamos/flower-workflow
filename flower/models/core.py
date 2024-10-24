from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from flower import ActionProtocol


@dataclass
class ActionCall:
    action: str
    params: Dict[str, Any]
    depends: Optional[List[str]]

    def __init__(self, action: str, params: Dict[str, Any], depends: Optional[List[str]] = None):
        self.action = action
        self.params = params
        self.depends = depends or []


@dataclass
class Workflow:
    params: Dict[str, Any]
    steps: dict[str, ActionCall]

    def __post_init__(self):
        self.steps = {k: ActionCall(**v) if isinstance(v, dict) else v for k, v in self.steps.items()}


@dataclass
class Schema:
    context: Optional[Dict[str, Any]]
    actions: Dict[str, ActionProtocol]
    workflows: Dict[str, Workflow]

    def __post_init__(self):
        self.context = self.context or {}
        self.workflows = {k: Workflow(**v) if isinstance(v, dict) else v for k, v in self.workflows.items()}
