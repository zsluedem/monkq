from typing import Any


class AuthProtocol():
    def gen_http_headers(self, method: str, request_path: str, data: str) -> dict:
        raise NotImplementedError()

    def signature(self, method: str, request_path: str, body: str) -> str:
        raise NotImplementedError()

    def get_timestamp(self) -> float:
        raise NotImplementedError()