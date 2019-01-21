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


class MonkException(BaseException):
    pass


class MaxRetryException(MonkException):
    pass


class RateLimitException(MonkException):
    def __init__(self, ratelimit_reset: int) -> None:
        self.ratelimit_reset = ratelimit_reset


class BacktestTimeException(MonkException):
    pass


class StrategyNotFound(MonkException):
    pass


class DataDownloadException(MonkException):
    pass


class AuthException(MonkException):
    pass


class LoadDataException(MonkException):
    pass


class ImpossibleException(MonkException):
    pass


class AccountException(MonkException):
    pass


class MarginException(AccountException):
    pass


class MarginNotEnoughException(MarginException):
    pass
