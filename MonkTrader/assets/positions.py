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
from dataclasses import dataclass
from typing import Dict
from MonkTrader.assets.instrument import Instrument, FutureInstrument
from MonkTrader.exception import MarginNotEnough
from collections import defaultdict
from typing import TYPE_CHECKING, Type
from enum import Enum

if TYPE_CHECKING:
    from MonkTrader.assets.trade import Trade
    from MonkTrader.assets.account import BaseAccount, FutureAccount


class DIRECTION(Enum):
    LONG = 1
    SHORT = 2


@dataclass()
class BasePosition():
    instrument: Instrument
    account: "BaseAccount"
    quantity: float = 0
    open_price: float = 0

    def deal(self, trade: "Trade") -> None:
        """
        When a position make a trade, the position would be changed by the trade.
        There are 5 conditions
        1. open a position
        2. get more on position
        3. sell part of the position
        4. close position
        5. close a position and open a opposite position
        :param trade:
        :return:
        """
        if self.quantity == 0:
            # open a position
            self.open_price += trade.avg_price
            self.quantity += trade.exec_quantity
        elif self.quantity * trade.exec_quantity > 0:
            # get more on position
            self.open_price = (trade.avg_price * trade.exec_quantity + self.quantity * self.open_price) / (
                    trade.exec_quantity + self.quantity)
            self.quantity += trade.exec_quantity
        else:
            # 3,4,5 condition
            if abs(self.quantity) - abs(trade.exec_quantity) > 0:
                # sell part of the position
                self.quantity += trade.exec_quantity
            elif abs(self.quantity) - abs(trade.exec_quantity) < 0:
                # close a position and open a opposite position
                self.quantity += trade.exec_quantity
                self.open_price = trade.avg_price
            else:
                # close position
                self.quantity = 0
                self.open_price = 0


@dataclass()
class FutureBasePosition(BasePosition):
    instrument: FutureInstrument
    account: "FutureAccount"

    @property
    def direction(self):
        """
        position direction.
        :return:
        """
        return DIRECTION.LONG if self.quantity >= 0 else DIRECTION.SHORT

    @property
    def market_value(self) -> float:
        return self.instrument.last_price * abs(self.quantity)

    @property
    def open_value(self) -> float:
        return self.open_price * abs(self.quantity)

    @property
    def unrealised_pnl(self) -> float:
        """
        unrealised_pnl including the exit commission fee.
        :return:
        """
        if self.direction == DIRECTION.LONG:
            return self.market_value - self.open_value - self.market_value * self.instrument.taker_fee
        else:
            return self.open_value - self.market_value - self.market_value * self.instrument.taker_fee

    @property
    def min_open_maint_margin(self) -> float:
        """
        The minimum margin for this position.
        If the margin for this position is lower than the maint_margin, the position would be liquidated.
        :return:
        """
        return self.open_value * self.instrument.maint_margin_rate

    @property
    def open_init_margin(self) -> float:
        return self.open_value * self.instrument.init_margin_rate

    @property
    def min_last_maint_margin(self) -> float:
        return self.market_value * self.instrument.maint_margin_rate

    @property
    def last_init_margin(self) -> float:
        return self.market_value * self.instrument.init_margin_rate

    @property
    def maint_margin(self):
        raise NotImplementedError()

    @property
    def liq_price(self) -> float:
        """
        liquidated price, if the position reach to this price , the position would be liquidated.
        The liq price need the maint_margin to be implemented.

        The equation would be like :

        open_value - liq_value = maintain_margin - minimum_maintain_margin - commission_taker_fee- funding_fee

        :return:
        """
        if self.direction == DIRECTION.LONG:
            # if have funding rate
            # (self.open_value - self.maint_margin) / (1-self.instrument.maint_margin-self.instrument.taker_fee - funding_rate) / self.quantity
            # don't consider the funding situation yet
            return (self.open_value - self.maint_margin) / (
                    1 - self.instrument.maint_margin_rate - self.instrument.taker_fee) / self.quantity
        else:
            # if have funding rate
            # (self.open_value + self.maint_margin) / (1+self.instrument.maint_margin+self.instrument.taker_fee + funding_rate) / self.quantity
            # don't consider the funding situation yet
            return (self.open_value + self.maint_margin) / (
                    1 + self.instrument.maint_margin_rate + self.instrument.taker_fee) / self.quantity

    @property
    def bankruptcy_price(self) -> float:
        """
        bankcruptcy price, if the position reach to this price , no margin would be left
        The equation would be like :

        open_value - liq_value = maintain_margin - commission_taker_fee- funding_fee

        :return:
        """
        # same as liq_price without considering the funding rate
        if self.direction == DIRECTION.LONG:
            return (self.open_value - self.maint_margin) / (1 - self.instrument.taker_fee) / self.quantity
        else:
            return (self.open_value + self.maint_margin) / (1 + self.instrument.taker_fee) / self.quantity


@dataclass()
class CrossPosition(FutureBasePosition):
    @property
    def maint_margin(self):
        return self.account.available_balance + self.position_margin + self.account.unrealised_pnl

    @property
    def position_margin(self):
        return self.market_value * (self.instrument.init_margin_rate + self.instrument.taker_fee)


@dataclass()
class IsolatedPosition(FutureBasePosition):
    _maint_margin: float = 0

    @property
    def maint_margin(self):
        return self._maint_margin

    @maint_margin.setter
    def maint_margin(self, value: float):
        if value >= self.account.available_balance or value < self.open_init_margin:
            raise MarginNotEnough()
        else:
            self._maint_margin = value

    @property
    def position_margin(self):
        return self.maint_margin

    @property
    def leverage(self):
        return self.market_value / self.maint_margin

    def set_leverage(self, leverage:float):
        """
        This method set the leverage base on the last value
        :return:
        """
        maint_margin = self.market_value / leverage
        self.set_maint_margin(maint_margin)

    def set_maint_margin(self, value: float):
        self.maint_margin = value

@dataclass()
class FuturePosition(BasePosition):
    """
    There are two kinds of future position in Bitmex, Cross position and isolated position.

    This position support to change from one to another.

    1. Cross position would use all the available margin in the account to support the position.
        cross position doesn't support setting the attr `leverage`.
    2.
    """
    leverage = 1

    isolated: bool = False  # isolate or cross position



class PositionManager(defaultdict, Dict[Instrument, BasePosition]):
    def __init__(self, position_cls: Type[BasePosition], account: "BaseAccount"):
        super(PositionManager, self).__init__()
        self.position_cls = position_cls
        self.account = account

    def __missing__(self, key):
        ret = self.position_cls(instrument=key, account=self.account)
        self[key] = ret
        return ret
