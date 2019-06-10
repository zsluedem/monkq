# copy from okex api

import base64
import datetime
import hmac
import time
from typing import Union

from monkq.exchange.base.auth import AuthProtocol
from yarl import URL

from . import const as c


def sign(message: str, secretKey: str) -> bytes:
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp: Union[float, str], method: str, request_path: str, body: str) -> str:
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key: str, sign: str, timestamp: str, passphrase: str) -> dict:
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.OK_ACCESS_KEY] = api_key
    header[c.OK_ACCESS_SIGN] = sign
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[c.OK_ACCESS_PASSPHRASE] = passphrase

    return header


def parse_params_to_str(params: dict) -> str:
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'

    return url[0:-1]


def get_timestamp() -> str:
    now = datetime.datetime.utcnow()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def signature(timestamp: float, method: str, request_path: str, body: str, secret_key: str) -> bytes:
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + str.upper(method) + request_path + str(body)
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


class OKexAuth(AuthProtocol):
    def __init__(self, api_key: str, api_secret: str, pass_phrase: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.pass_phrase = pass_phrase

    def gen_http_headers(self, method: str, url: URL, data: str) -> dict:
        timestamp = self.get_timestamp()
        request_path = str(url.path)
        signa = sign(pre_hash(timestamp, method, request_path, data), self.api_secret)
        return get_header(self.api_key, signa.decode('utf8'), timestamp, self.pass_phrase)

    def get_timestamp(self) -> str:
        return str(round(time.time(), 3))

    def signature(self, method: str, request_path: str, body: str) -> str:
        timestamp = self.get_timestamp()
        return str(sign(pre_hash(timestamp, method, request_path, body), self.api_secret))
