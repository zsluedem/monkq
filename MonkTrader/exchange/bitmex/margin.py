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

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from MonkTrader.exchange.bitmex.positionreal import SimulatePosition
    from MonkTrader.exchange.bitmex.instrument import Instrument

xbt_factor = 100000000


class AccountMargin():
    def __init__(self,walletBalance, marginBalance, availableMargin):
        self.walletBalance = walletBalance  # 钱包余额
        self.unrealisedPnl = 0  # 未实现盈亏
        self.marginBalance = marginBalance  # 保证金余额
        self.maintMargin = 0  # 仓位保证金
        self.initMargin = 0  # 委托保证金
        self.availableMargin = availableMargin  # 可用保证金
        self.marginLeverage = 0  # 杠杆
        self.marginUsedPcnt = 0  # 保证金使用百分比



class SimulateTrade():
    def __init__(self, price, contract_amount, symbol):
        self.price = price
        self.contract_amount = contract_amount
        self.symbol = symbol

    @property
    def value(self):
        return self.contract_amount/ self.price * xbt_factor

    @property
    def commision(self):
        return self.value * 0.00075

    @property
    def used_margin(self):
        return self.value * 0.01

    @property
    def cost_margin(self):
        """
        This is incorrect right now.
        The second taker fee needs to be taken based on the position value at the bankruptcy price ($3130.65.)

        Here is the 1% and entry taker fee on the entry price value:
        0.94878000 * 0.01 = 0.0094878
        0.94878000 * 0.00075 = 0.00071159

        Now to calculate the exit taker fee on the bankruptcy price value:
        1/3130.65 = 0.00031942
        0.00031942 * 3000 = 0.95826
        0.95826 * 0.00075 = 0.0007187

        Now to add them up:
        0.0094878 + 0.00071159 + 0.0007187
        0.01091809
        :return:
        """
        return self.value * (0.01 + 0.00075*2)


class SimulateAccount():

    def __init__(self, init_margin, exchange):
        self.init_margin = init_margin
        self.wallet_balance = init_margin
        self.exchange= exchange


        self.current_long = list()
        self.current_short = list()

        self.positions:Dict[str, "SimulatePosition"] = {}

    @classmethod
    def create_account(cls, init_margin):
        return cls(init_margin)


    def get_position(self, instrument: "Instrument") -> "SimulatePosition":
        return self.positions.get(instrument.symbol)

    @property
    def margin_balance(self):
        return self.wallet_balance + self.unrealised_pnl

    @property
    def available_balance(self):
        return self.margin_balance - self.order_margin - self.position_margin

    @property
    def unrealised_pnl(self):
        return sum([position.unrealised_pnl for _, position in self.positions])

    @property
    def position_margin(self):
        return sum([[position.position_margin for _, position in self.positions]])

    @property
    def order_margin(self):
        return

    #
    # def long(self, usd, price):
    #     # 开多
    #     order = SimulateTrade(price, usd, "XBTUSD")
    #     if self.current_margin < order.contract_amount:
    #         raise Exception("not enough margin")
    #     self.current_margin -= (order.used_margin + order.commision)
    #     self.current_long.append(order)
    #
    # def short(self, usd, price):
    #     # 开空
    #     order = SimulateTrade(price, usd, "XBTUSD")
    #     if self.current_margin < order.contract_amount:
    #         raise Exception("not enough margin")
    #     self.current_margin -= (order.used_margin + order.commision)
    #     self.current_short.append(order)
    #
    # def long_close(self, usd, price):
    #     # 多平
    #     order = SimulateTrade(price, usd, "XBTUSD")
    #
    #
    # def short_close(self, usd, price):
    #     # 空平
    #     pass
    #
    # def order(self, usd, price):
    #     if usd > 0:
    #         side = 'buy'
    #     elif usd < 0:
    #         side = 'sell'
    #     else:
    #         return
    #     abs_usd = abs(usd)
    #     if side == "buy":
    #         if self.position >= 0:
    #             amount = abs_usd / price * xbt_factor
    #             start_margin = amount * (self.initMar + self.taker_commission * 2)
    #             if self.current_margin < start_margin:
    #                 raise Exception("not enough margin")
    #             self.current_margin -= amount * (self.initMar + self.taker_commission)
    #             self.position += abs_usd
    #         elif self.position < 0:
    #             if abs_usd > abs(self.position):
    #                 # 先平仓再加仓
    #                 pass
    #             else:
    #                 # 只平仓
    #                 pass
    #     elif side == "sell":
    #         pass
