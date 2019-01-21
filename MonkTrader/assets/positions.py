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
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Type, TypeVar

from dataclasses import dataclass
from MonkTrader.assets.instrument import FutureInstrument, Instrument
from MonkTrader.assets.variable import DIRECTION, POSITION_EFFECT
from MonkTrader.exception import MarginException, MarginNotEnoughException

if TYPE_CHECKING:
    from MonkTrader.assets.trade import Trade
    from MonkTrader.assets.account import BaseAccount, FutureAccount

T_ACCOUNT = TypeVar("T_ACCOUNT", bound="BaseAccount")
T_POSITION = TypeVar("T_POSITION", bound="BasePosition")
T_INSTRUMENT = TypeVar("T_INSTRUMENT", bound="Instrument")


@dataclass()
class BasePosition():
    instrument: Instrument
    account: "BaseAccount"
    quantity: float = 0
    open_price: float = 0

    def position_effect(self, trade: "Trade") -> POSITION_EFFECT:
        if self.quantity == 0:
            # open a position
            return POSITION_EFFECT.OPEN
        elif self.quantity * trade.exec_quantity > 0:
            # get more on position
            return POSITION_EFFECT.GET_MORE
        else:
            # 3,4,5 condition
            if abs(self.quantity) - abs(trade.exec_quantity) > 0:
                # sell part of the position
                return POSITION_EFFECT.CLOSE_PART
            elif abs(self.quantity) - abs(trade.exec_quantity) < 0:
                # close a position and open a opposite position
                return POSITION_EFFECT.CLOSE_AND_OPEN
            else:
                # close position
                return POSITION_EFFECT.CLOSE

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
        position_effect = self.position_effect(trade)
        if position_effect == POSITION_EFFECT.OPEN:
            # open a position
            self.open_price += trade.exec_price
            self.quantity += trade.exec_quantity
        elif position_effect == POSITION_EFFECT.GET_MORE:
            # get more on position
            self.open_price = (trade.exec_price * trade.exec_quantity + self.quantity * self.open_price) / \
                              (trade.exec_quantity + self.quantity)
            self.quantity += trade.exec_quantity
        else:
            # 3,4,5 condition
            if position_effect == POSITION_EFFECT.CLOSE_PART:
                # sell part of the position
                self.quantity += trade.exec_quantity
            elif position_effect == POSITION_EFFECT.CLOSE_AND_OPEN:
                # close a position and open a opposite position
                self.quantity += trade.exec_quantity
                self.open_price = trade.exec_price
            else:
                # close position
                self.quantity = 0
                self.open_price = 0


@dataclass()
class FutureBasePosition(BasePosition):
    instrument: FutureInstrument
    account: "FutureAccount"

    @property
    def direction(self) -> DIRECTION:
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
    def maint_margin(self) -> float:
        raise NotImplementedError()

    @property
    def liq_price(self) -> float:
        """
        liquidated price, if the position reach to this price ,
        the position would be liquidated.
        The liq price need the maint_margin to be implemented.

        The equation would be like :

        open_value - liq_value = maintain_margin - minimum_maintain_margin -
        commission_taker_fee- funding_fee

        :return:
        """
        if self.direction == DIRECTION.LONG:
            # if have funding rate
            # (self.open_value - self.maint_margin) /
            # (1-self.instrument.maint_margin-self.instrument.taker_fee -
            # funding_rate) / self.quantity
            # don't consider the funding situation yet
            return (self.open_value - self.maint_margin) / \
                   (1 - self.instrument.maint_margin_rate - self.instrument.taker_fee) / abs(self.quantity)
        else:
            # if have funding rate
            # (self.open_value + self.maint_margin) /
            # (1+self.instrument.maint_margin+self.instrument.taker_fee +
            # funding_rate) / self.quantity
            # don't consider the funding situation yet
            return (self.open_value + self.maint_margin) / \
                   (1 + self.instrument.maint_margin_rate + self.instrument.taker_fee) / abs(self.quantity)

    @property
    def bankruptcy_price(self) -> float:
        """
        bankcruptcy price, if the position reach to this price ,
        no margin would be left The equation would be like :

        open_value - liq_value = maintain_margin - commission_taker_fee-
        funding_fee

        :return:
        """
        # same as liq_price without considering the funding rate
        if self.direction == DIRECTION.LONG:
            return (self.open_value - self.maint_margin) / (1 - self.instrument.taker_fee) / abs(self.quantity)
        else:
            return (self.open_value + self.maint_margin) / (1 + self.instrument.taker_fee) / abs(self.quantity)


@dataclass()
class CrossPosition(FutureBasePosition):
    """
    Cross position use all the available margin in the account to
    ensure the position.If your account doesn't get enough
    margin for the position.You whole account may be liquidated and
    you lost all your money.It would be good to use cross
    position if you hedge your position.

    Cross position doesn't support setting up the margin. All the position
    margin cross position is going to take if based
    on the init margin ,the market value and the account available balance.
    """

    @property
    def maint_margin(self) -> float:
        return self.account.available_balance + self.open_init_margin

    @maint_margin.setter
    def maint_margin(self, value: float) -> float:
        raise MarginException("You can not set the margin in cross position")

    @property
    def leverage(self) -> float:
        raise MarginException("Cross position doesn't support to see position leverage")

    @property
    def position_margin(self) -> float:
        return self.market_value * (self.instrument.init_margin_rate + self.instrument.taker_fee)


@dataclass()
class IsolatedPosition(FutureBasePosition):
    """
    Isolated position would take a fixed margin to ensure the position.
    If the position reach to the liq price, only the
    margin you assigned would be lost. This kind of position can help you
    allocate your position more wisely to ensure
    that you don't lose all your money.

    You can set the mainain margin by yourself or set the leverage based on you market value.
    """
    _maint_margin: float = 0

    @property
    def maint_margin(self) -> float:
        return self._maint_margin

    @maint_margin.setter
    def maint_margin(self, value: float) -> None:
        """
        LONG position choose open_init_margin would be safer because it is bigger.
        SHORT position choose last_init_margin would be safer because it is bigger.
        :param value:
        :return:
        """
        if value >= self.account.available_balance or value < self.last_init_margin:
            raise MarginNotEnoughException()
        else:
            self._maint_margin = value

    @property
    def position_margin(self) -> float:
        return self.maint_margin

    @property
    def leverage(self) -> float:
        return self.market_value / self.maint_margin

    def set_leverage(self, leverage: float) -> None:
        """
        This method set the leverage base on the last value
        :return:
        """
        assert leverage >= 1
        maint_margin = self.market_value / leverage
        self.set_maint_margin(maint_margin)

    def set_maint_margin(self, value: float) -> None:
        self.maint_margin = value


@dataclass()
class FutureCrossIsolatePosition(IsolatedPosition, CrossPosition):
    """
    There are two kinds of future position in Bitmex, Cross position and isolated position.

    This position support to change from one to another.
    """

    isolated: bool = False  # isolate or cross position

    @property
    def maint_margin(self) -> float:
        if self.isolated:
            return IsolatedPosition.maint_margin.fget(self)  # type: ignore
        else:
            return CrossPosition.maint_margin.fget(self)  # type: ignore

    @maint_margin.setter
    def maint_margin(self, value: float) -> None:
        IsolatedPosition.maint_margin.fset(self, value)  # type: ignore
        self.isolated = True

    @property
    def position_margin(self) -> float:
        if self.isolated:
            return IsolatedPosition.position_margin.fget(self)  # type: ignore
        else:
            return CrossPosition.position_margin.fget(self)  # type: ignore

    @property
    def leverage(self) -> float:
        if self.isolated:
            return IsolatedPosition.leverage.fget(self)  # type: ignore
        else:
            return CrossPosition.leverage.fget(self)  # type: ignore

    def set_leverage(self, leverage: float) -> None:
        super(FutureCrossIsolatePosition, self).set_leverage(leverage)

    def set_maint_margin(self, value: float) -> None:
        super(FutureCrossIsolatePosition, self).set_maint_margin(value)

    def set_cross(self) -> None:
        self.isolated = False

    @property
    def is_isolated(self) -> bool:
        return self.isolated


FuturePosition = FutureCrossIsolatePosition


class PositionManager(defaultdict, Dict[T_INSTRUMENT, T_POSITION]):
    def __init__(self, position_cls: Type[T_POSITION], account: T_ACCOUNT):
        super(PositionManager, self).__init__()
        self.position_cls = position_cls
        self.account = account

    def __missing__(self, key: T_INSTRUMENT) -> T_POSITION:
        ret = self.position_cls(instrument=key, account=self.account)
        self[key] = ret
        return ret
