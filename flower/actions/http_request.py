from dataclasses import dataclass, field
from typing import Optional

from flower import ActionProtocol
from requests import request


@dataclass
class RequestParams:
    base_url: str
    path: str
    method: str
    headers: dict = field(default_factory=dict)
    query_params: dict = field(default_factory=dict)
    path_params: dict = field(default_factory=dict)
    payload: Optional[dict] = None


class HttpRequest(ActionProtocol):
    should_parse_params = True

    def __call__(self, context, workflow_context, params):
        if "base_url" not in params:
            params["base_url"] = context.get("base_url", "")
        request_params = RequestParams(**params)

        final_url = request_params.base_url + request_params.path.format(**request_params.path_params)
        print("[BEGIN] Requesting URL: ", final_url)

        response = request(
            url=final_url,
            method=request_params.method,
            headers=request_params.headers,
            params=request_params.query_params,
            json=request_params.payload,
        )

        print("[END] Requesting URL: ", final_url)

        response.raise_for_status()

        if response.content:
            return response.json()
        else:
            return None
