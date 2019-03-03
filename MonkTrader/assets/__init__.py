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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from MonkTrader.assets.instrument import Instrument  # noqa: F401  pragma: no cover
    from MonkTrader.assets.order import BaseOrder  # noqa: F401  pragma: no cover

T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")
T_ORDER = TypeVar("T_ORDER", bound="BaseOrder")


class AbcInstrument(ABC):
    pass


class AbcAccount(ABC):
    pass


class AbcPosition(ABC):
    pass


class AbcPositions(ABC):
    @abstractmethod
    def get(self, instrument: AbcInstrument) -> AbcPosition:
        raise NotImplementedError()


class AbcOrder(ABC):
    pass


class AbcTrade(ABC):
    pass
