from typing import Any

from yarl import URL


class AuthProtocol():
    def gen_http_headers(self, method: str, url: URL, data: str) -> dict:
        raise NotImplementedError()

    def signature(self, method: str, request_path: str, body: str) -> str:
        raise NotImplementedError()

    def get_timestamp(self) -> Any:
        raise NotImplementedError()
