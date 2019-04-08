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
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

from monkq.assets.const import DIRECTION, ORDER_STATUS, SIDE
from monkq.assets.instrument import FutureInstrument, Instrument
from monkq.exception import ImpossibleError
from monkq.utils.i18n import _

if TYPE_CHECKING:
    from monkq.assets.account import BaseAccount, FutureAccount  # pragma: no cover
    from monkq.assets.trade import Trade  # pragma: no cover


@dataclass()
class BaseOrder():
    account: "BaseAccount"
    order_id: str
    instrument: Instrument
    quantity: float = 0
    traded_quantity: float = 0
    trades: List["Trade"] = field(default_factory=list)

    @property
    def order_status(self) -> ORDER_STATUS:
        if self.traded_quantity == 0:
            return ORDER_STATUS.NOT_TRADED
        elif self.traded_quantity == self.quantity:
            return ORDER_STATUS.FULL_TRADED
        elif abs(self.traded_quantity) < abs(self.quantity):
            return ORDER_STATUS.PARTLY_TRADED
        else:
            raise ImpossibleError(_(
                "order quantity: {}, traded quantity: {}").format(self.quantity, self.traded_quantity))

    @property
    def side(self) -> SIDE:
        return SIDE.BUY if self.quantity > 0 else SIDE.SELL

    def deal(self, trade: "Trade") -> None:
        assert trade not in self.trades
        assert abs(self.quantity) >= abs(self.traded_quantity + trade.exec_quantity)
        self.account.deal(trade)
        self.traded_quantity += trade.exec_quantity
        self.trades.append(trade)

    @property
    def remain_quantity(self) -> float:
        return self.quantity - self.traded_quantity

    def __getstate__(self) -> dict:
        return {
            "exchange": self.account.exchange.name,
            "order_id": self.order_id,
            "symbol": self.instrument.symbol,
            "quantity": self.quantity,
            "traded_quantity": self.traded_quantity,
            "trades": self.trades,
            "side": self.side,
            "remain_quantity": self.remain_quantity,
            "order_class": self.__class__.__name__
        }


@dataclass()
class LimitOrder(BaseOrder):
    price: float = 0

    @property
    def order_value(self) -> float:
        return self.price * abs(self.quantity)

    @property
    def remain_value(self) -> float:
        return self.price * abs(self.remain_quantity)

    def __getstate__(self) -> dict:
        state = super(LimitOrder, self).__getstate__()
        state.update({
            'price': self.price,
            'order_value': self.order_value,
            'remain_value': self.remain_value
        })
        return state


@dataclass()
class MarketOrder(BaseOrder):
    pass


@dataclass()
class StopMarketOrder(BaseOrder):
    stop_price: float = 0

    def __getstate__(self) -> dict:
        state = super(StopMarketOrder, self).__getstate__()
        state.update({
            'stop_price': self.stop_price,
        })
        return state


@dataclass()
class StopLimitOrder(BaseOrder):
    stop_price: float = 0

    def __getstate__(self) -> dict:
        state = super(StopLimitOrder, self).__getstate__()
        state.update({
            'stop_price': self.stop_price,
        })
        return state


@dataclass()
class FutureLimitOrder(LimitOrder):
    account: "FutureAccount"
    instrument: FutureInstrument

    @property
    def direction(self) -> DIRECTION:
        return DIRECTION.LONG if self.quantity > 0 else DIRECTION.SHORT

    def __getstate__(self) -> dict:
        state = super(FutureLimitOrder, self).__getstate__()
        state.update({
            'direction': self.direction
        })
        return state


@dataclass()
class FutureMarketOrder(MarketOrder):
    account: "FutureAccount"
    instrument: FutureInstrument

    @property
    def direction(self) -> DIRECTION:
        return DIRECTION.LONG if self.quantity > 0 else DIRECTION.SHORT

    def __getstate__(self) -> dict:
        state = super(FutureMarketOrder, self).__getstate__()
        state.update({
            'direction': self.direction
        })
        return state


ORDER_T = Union[FutureLimitOrder, FutureLimitOrder, MarketOrder, LimitOrder, StopLimitOrder, StopMarketOrder]
