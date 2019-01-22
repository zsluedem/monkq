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
from typing import TYPE_CHECKING

import dataclasses
from MonkTrader.assets.const import SIDE
from MonkTrader.assets.order import BaseOrder

if TYPE_CHECKING:
    from MonkTrader.assets.instrument import Instrument


@dataclasses.dataclass()
class Trade():
    order: "BaseOrder"
    exec_price: float
    exec_quantity: float
    trade_id: str

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

    # stupid mistake
    # @property
    # def avg_price(self) -> float:
    #     # not (abs(self.value) + self.commission) / (self.exec_quantity)
    #     # because this one is faster. It is the same result
    #     return (self.value + self.commission) / self.exec_quantity if self.side == SIDE.BUY \
    #         else (self.value - self.commission) / self.exec_quantity
