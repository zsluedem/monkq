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
from dataclasses import dataclass, field
from MonkTrader.assets import AbcExchange
from MonkTrader.assets.trade import Trade
from MonkTrader.assets.positions import PositionManager, BasePosition, FuturePosition, POSITION_EFFECT, DIRECTION
from typing import Optional, Type


@dataclass()
class BaseAccount():
    exchange: AbcExchange
    position_cls: Type[BasePosition]
    positions: PositionManager = field(init=False)
    wallet_balance: float = 0

    def __post_init__(self):
        self.positions = PositionManager(self.position_cls, self)

    def deal(self, trade: Trade) -> None:
        raise NotImplementedError()


@dataclass()
class FutureAccount(BaseAccount):
    position_cls: Type[FuturePosition]

    @property
    def position_margin(self) -> float:
        return sum([position.position_margin for instrument, position in self.positions.items()])

    # TODO
    @property
    def order_margin(self) -> float:
        """
        Not that simple
        :return:
        """
        return sum([order.order_margin for order in self.exchange.open_orders()])

    @property
    def unrealised_pnl(self) -> float:
        return sum([position.unrealised_pnl for instrument, position in self.positions.items()])

    @property
    def margin_balance(self):
        return self.wallet_balance + self.unrealised_pnl

    @property
    def available_balance(self):
        return self.margin_balance - self.order_margin - self.position_margin

    def deal(self, trade: Trade) -> None:
        position = self.positions[trade.instrument]
        position_effect = position.position_effect(trade)

        if position_effect == POSITION_EFFECT.OPEN or position_effect == POSITION_EFFECT.GET_MORE:
            pass
        else:
            if position_effect == POSITION_EFFECT.CLOSE or position_effect == POSITION_EFFECT.CLOSE_PART:
                profit_quantity = abs(trade.exec_quantity)
            elif abs(position.quantity)>= abs(trade.exec_quantity):
                profit_quantity = abs(trade.exec_quantity)
            else:
                profit_quantity = abs(position.quantity)

            if position.direction == DIRECTION.LONG:
                profit = trade.exec_price * profit_quantity - position.open_price * profit_quantity
            else:
                profit = position.open_price * profit_quantity - trade.exec_price * profit_quantity
            self.wallet_balance += profit

        self.wallet_balance -= trade.commission
        position.deal(trade)
