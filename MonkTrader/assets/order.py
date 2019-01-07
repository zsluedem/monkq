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
from dataclasses import field, dataclass
import enum
from MonkTrader.assets.instrument import Instrument
from MonkTrader.exception import ImpossibleException
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from MonkTrader.assets.trade import Trade


class SIDE(enum.Enum):
    BUY = 1
    SELL = 2


class ORDERSTATUS(enum.Enum):
    NOT_TRADED = 1
    FULL_TRADED = 2
    PARTLY_TRADED = 3


@dataclass()
class BaseOrder():
    order_id: str
    instrument: Instrument
    quantity: float = 0
    traded_quantity: float = 0
    trades: List["Trade"] = field(default_factory=list)

    @property
    def order_status(self) -> ORDERSTATUS:
        if self.traded_quantity == 0:
            return ORDERSTATUS.NOT_TRADED
        elif self.traded_quantity == self.quantity:
            return ORDERSTATUS.FULL_TRADED
        elif abs(self.traded_quantity) < abs(self.quantity):
            return ORDERSTATUS.PARTLY_TRADED
        else:
            raise ImpossibleException(
                "order quantity: {}, traded quantity: {}".format(self.quantity, self.traded_quantity))

    @property
    def side(self) -> SIDE:
        return SIDE.BUY if self.quantity > 0 else SIDE.SELL

    def traded(self, trade: "Trade") -> None:
        assert trade not in self.trades
        self.traded_quantity += trade.exec_quantity
        self.trades.append(trade)

class LimitOrder(BaseOrder):
    price: float

    @property
    def order_value(self):
        return self.price * self.quantity

class MarketOrder(BaseOrder):
    pass


class StopMarketOrder(BaseOrder):
    stop_price: float


class StopLimitOrder(BaseOrder):
    stop_price: float


class FutureLimitOrder(LimitOrder):
    leverage: float =1
    @property
    def margin_value(self):
        return self.order_value / self.leverage

