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
from MonkTrader.assets import AbcExchange
from MonkTrader.assets.positions import PositionManager
from typing import Optional

@dataclasses.dataclass()
class BaseAccount():
    exchange: AbcExchange


class FutureAccount(BaseAccount):
    positions: PositionManager
    wallet_balance: float = 0
    @property
    def position_balance(self) -> float:
        return sum([position.margin_value for intrument, position in self.positions.items()])

    @property
    def order_margin(self) -> float:
        return

    @property
    def unrealised_pnl(self) -> float:
        return

    @property
    def margin_balance(self):
        return self.wallet_balance + self.unrealised_pnl

    @property
    def available_balance(self):
        return self.margin_balance - self.order_margin - self.position_balance
