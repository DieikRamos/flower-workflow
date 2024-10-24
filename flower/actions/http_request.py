from dataclasses import dataclass
from typing import Optional

from flower import ActionProtocol
from requests import request


@dataclass
class RequestParams:
    base_url: str
    path: str
    method: str
    headers: Optional[dict]
    query_params: Optional[dict]
    path_params: Optional[dict]
    payload: Optional[dict]

    def __init__(
        self,
        base_url: str,
        path: str,
        method: str,
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        path_params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ):
        self.base_url = base_url
        self.path = path
        self.method = method
        self.headers = headers or {}
        self.query_params = query_params or {}
        self.path_params = path_params or {}
        self.payload = payload or None


class HttpRequest(ActionProtocol):
    should_parse_params = True

    def __call__(self, context, workflow_context, params):
        params["base_url"] = context["base_url"]
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
