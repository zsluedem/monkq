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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from abc import ABC, abstractmethod, abstractclassmethod, abstractstaticmethod
import datetime

from typing import Generator


class AbcInstrument(ABC):
    pass


class AbcAccount(ABC):
    pass


class AbcPosition(ABC):
    pass


class AbcPositions(ABC):
    @abstractmethod
    def get(self, instrument: AbcInstrument) -> AbcPosition:
        raise NotImplementedError


class AbcOrder(ABC):
    pass


class AbcTrade(ABC):
    pass


class AbcExchange(ABC):
    @abstractmethod
    def get_account(self) -> AbcAccount:
        raise NotImplementedError

    @abstractmethod
    def init(self):
        raise NotImplementedError


class AbcContext(ABC):
    @abstractmethod
    def get_exchange(self) -> AbcExchange:
        raise NotImplementedError

class AbcRunner(ABC):
    @abstractmethod
    def setup(self):
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError


class Ticker(ABC):
    @abstractmethod
    def timer(self) -> Generator[datetime.datetime, None, None]:
        raise NotImplementedError


class AbcStrategy():
    @abstractmethod
    async def setup(self):
        raise NotImplementedError

    @abstractmethod
    async def on_trade(self, message):
        raise NotImplementedError

    @abstractmethod
    async def tick(self, message):
        raise NotImplementedError

    @abstractmethod
    async def handle_bar(self):
        raise NotImplementedError
