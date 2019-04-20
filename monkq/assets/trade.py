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
import dataclasses
import datetime
from typing import TYPE_CHECKING, Optional

from monkq.assets.const import SIDE
from monkq.assets.order import BaseOrder

if TYPE_CHECKING:
    from monkq.assets.instrument import Instrument  # pragma: no cover


@dataclasses.dataclass()
class Trade():
    order: "BaseOrder"
    exec_price: float
    exec_quantity: float
    trade_id: str

    trade_datetime: Optional[datetime.datetime] = None

    @property
    def side(self) -> "SIDE":
        return self.order.side

    @property
    def instrument(self) -> "Instrument":
        return self.order.instrument

    @property
    def order_id(self) -> str:
        return self.order.order_id

    @property
    def value(self) -> float:
        return self.exec_quantity * self.exec_price

    @property
    def commission(self) -> float:
        return abs(self.value) * self.instrument.taker_fee

    def to_dict(self) -> dict:
        return {
            'exec_price': self.exec_price,
            'exec_quantity': self.exec_quantity,
            'trade_id': self.trade_id,
            'trade_datetime': self.trade_datetime,
            'side': self.side.name,
            'symbol': self.instrument.symbol,
            'order_id': self.order_id,
            'value': self.value,
            'commission': self.commission
        }

    # stupid mistake
    # @property
    # def avg_price(self) -> float:
    #     # not (abs(self.value) + self.commission) / (self.exec_quantity)
    #     # because this one is faster. It is the same result
    #     return (self.value + self.commission) / self.exec_quantity if self.side == SIDE.BUY \
    #         else (self.value - self.commission) / self.exec_quantity
