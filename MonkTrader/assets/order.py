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
from MonkTrader.assets.instrument import Instrument, FutureInstrument
from MonkTrader.exception import ImpossibleException
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from MonkTrader.assets.account import BaseAccount, FutureAccount
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
    account: "BaseAccount"
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

    def deal(self, trade: "Trade") -> None:
        assert trade not in self.trades
        assert abs(self.quantity) >= abs(self.traded_quantity + trade.exec_quantity)
        self.traded_quantity += trade.exec_quantity
        self.trades.append(trade)


@dataclass()
class LimitOrder(BaseOrder):
    price: float = 0

    @property
    def order_value(self):
        return self.price * self.quantity

    @property
    def remain_quantity(self):
        return self.quantity - self.traded_quantity



@dataclass()
class MarketOrder(BaseOrder):
    pass


@dataclass()
class StopMarketOrder(BaseOrder):
    stop_price: float = 0


@dataclass()
class StopLimitOrder(BaseOrder):
    stop_price: float = 0


@dataclass()
class FutureLimitOrder(LimitOrder):
    account: "FutureAccount"
    instrument: FutureInstrument

    # @property
    # def order_margin(self):
    #     """
    #     It is related with the position
    #     1. open a position
    #     2. get more on a position
    #     3. close a position and reduce position
    #     4. close a position and open a opposite position
    #     """
    #     position = self.account.positions[self.instrument]
    #     if position.isolated:
    #         leverage = position.leverage
    #     else:
    #         leverage = 1
    #     if self.account.positions[self.instrument].quantity * self.quantity >= 0:
    #         # open a position  or get more on a position
    #         ret = self.remain_quantity* self.price / leverage * (1 + self.instrument.init_margin_rate + self.instrument.taker_fee)
    #     elif abs(self.account.positions[self.instrument].quantity) >= abs(self.quantity):
    #         # close a position and reduce position
    #         ret = 0
    #     else:
    #         # close a position and open a opposite position
    #         ret = self.order_value / self.quantity * \
    #               abs(self.account.positions[self.instrument].quantity + self.remain_quantity) / \
    #               leverage * (1 + self.instrument.init_margin_rate + self.instrument.taker_fee)
    #     return abs(ret)
