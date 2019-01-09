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
import dataclasses
from typing import Dict
from MonkTrader.assets.instrument import Instrument, FutureInstrument
from collections import defaultdict
from typing import TYPE_CHECKING, Type
from enum import Enum

if TYPE_CHECKING:
    from MonkTrader.assets.trade import Trade
    from MonkTrader.assets.account import BaseAccount


class DIRECTION(Enum):
    LONG = 1
    SHORT = 2


@dataclasses.dataclass()
class BasePosition():
    instrument: Instrument
    account: "BaseAccount"
    quantity: float = 0
    open_price: float = 0

    def deal(self, trade: "Trade") -> None:
        """
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
            self.open_price = (trade.avg_price * trade.exec_quantity + self.quantity* self.open_price) / (trade.exec_quantity + self.quantity)
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

@dataclasses.dataclass()
class FuturePosition(BasePosition):
    instrument = FutureInstrument
    leverage = 1

    isolated: bool = False # isolate or cross position

    @property
    def direction(self):
        return DIRECTION.LONG if self.quantity >= 0 else DIRECTION.SHORT

    @property
    def margin(self) -> float:
        return

    @property
    def maint_margin(self) -> float:
        return 1/ self.open_price * self.quantity * self.instrument.maint_margin +  1/ self.liq_price

    @property
    def liq_price(self) -> float:
        """if self.isolated:
            if self.direction == DIRECTION.LONG:
                funding_rate = self.funding_rate if self.funding_rate > 0 else 0
                return self.open_price / (1 + 1 / self.leverage - self.instrument.maintMargin - funding_rate)
            else:
                funding_rate = self.funding_rate if self.funding_rate < 0 else 0
                return self.open_price / (1 - 1 / self.leverage + self.instrument.maintMargin - funding_rate)
        else:
            if self.direction == DIRECTION.LONG:
                funding_rate = self.funding_rate if self.funding_rate > 0 else 0
                return 1/ (1 / self.open_price * (1 - self.instrument.maint_margin - funding_rate) + self.account.wallet_balance / XBtUnit / abs(self.quantity))
            else:
                funding_rate = self.funding_rate if self.funding_rate < 0 else 0
                return 1/ (1 / self.open_price * (1 + self.instrument.maint_margin - funding_rate) - self.account.wallet_balance / XBtUnit / abs(self.quantity))

        above is the perpetual contract liq price calculate way
        """
        return 0

    @property
    def market_value(self) -> float:
        return 1 / self.instrument.last_price * self.quantity

    @property
    def pnl(self) -> float:
        return

class PositionManager(defaultdict, Dict[Instrument, BasePosition]):
    def __init__(self, position_cls: Type[BasePosition], account: "BaseAccount"):
        super(PositionManager, self).__init__()
        self.position_cls = position_cls
        self.account = account

    def __missing__(self, key):
        return self.position_cls(instrument=key, account=self.account)
