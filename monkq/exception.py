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

from typing import Mapping, Optional


class MonkError(BaseException):
    pass


class CommandError(MonkError):
    pass


class SettingError(MonkError):
    pass


class DataError(MonkError):
    pass


class AuthError(MonkError):
    pass


class RequestError(MonkError):
    pass


class HttpError(RequestError):
    def __init__(self, url: str, method: Optional[str], body: Optional[str], headers: Optional[Mapping],
                 message: str = ''):
        self.url = url
        self.method = method
        self.body = body
        self.headers = headers
        self.message = message


class MaxRetryError(HttpError):
    pass


class NotFoundError(HttpError):
    pass


class RateLimitError(HttpError):
    def __init__(self, url: str, method: str, body: str, headers: Mapping, message: str = '',
                 ratelimit_reset: int = 0) -> None:
        super(RateLimitError, self).__init__(url, method, body, headers, message)
        self.ratelimit_reset = ratelimit_reset


class HttpAuthError(AuthError, HttpError):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret


class BacktestError(MonkError):
    pass


class DataDownloadError(MonkError):
    pass


class LoadDataError(MonkError):
    pass


class ImpossibleError(MonkError):
    pass


class UnKnownError(MonkError):
    pass


class AssetsError(MonkError):
    pass


class MarginError(AssetsError):
    pass


class MarginNotEnoughError(MarginError):
    pass
