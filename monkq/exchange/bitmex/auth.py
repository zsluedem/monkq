#
# MIT License
#
# Copyright (c) 2018 WillQ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import hashlib
import hmac
import time
from typing import Optional
from urllib.parse import urlparse

from monkq.exchange.base.auth import AuthProtocol
from monkq.utils.timefunc import local_offset_seconds
from yarl import URL

_safe_nonce = 300

expire_ts = int(local_offset_seconds + _safe_nonce)


def generate_expires(timestamp: Optional[float] = None, expire: int = expire_ts) -> int:
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp + expire)


def generate_signature(secret: str, verb: str, url: str, nonce: float, data: str) -> str:
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsedURL = urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query

    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')

    # print "Computing HMAC: %s" % verb + path + str(nonce) + data
    message = verb + path + str(nonce) + data

    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature


def gen_header_dict(api_key: str, api_secret: str, verb: str, url: str, data: str, now: Optional[float] = None,
                    nonce: int = expire_ts) -> dict:
    if now is None:
        now = time.time()
    expire = generate_expires(now, nonce)

    sign = generate_signature(api_secret, verb, url, expire, data)

    return {
        "api-expires": str(expire),
        "api-signature": sign,
        "api-key": api_key
    }


class BitmexAuth(AuthProtocol):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_timestamp(self) -> float:
        stamp = time.time()
        return generate_expires(stamp, expire_ts)

    def gen_http_headers(self, method: str, url: URL, data: str) -> dict:
        return gen_header_dict(self.api_key, self.api_secret, method, str(url), data)

    def signature(self, method: str, request_path: str, body: str) -> str:
        return generate_signature(self.api_secret, method, request_path, self.get_timestamp(), body)
