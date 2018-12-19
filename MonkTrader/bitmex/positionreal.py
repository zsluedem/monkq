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
from MonkTrader.bitmex.const import PositionDirection
from MonkTrader.bitmex.instrument import Instrument
from MonkTrader.bitmex.margin import SimulateAccount
from MonkTrader.const import XBtUnit

@dataclass
class Position():
    symbol: str
    currentQty: int

class PositionReal():
    def __init__(self, symbol, currency, underlying, quoteCurrency, initMarginReq, maintMarginReq, crossMargin, deleveragePercentile, prevRealisedPnl, rebalancedPnl, currentQty, realisedPnl, unrealisedPnl, liquidationPrice, bankruptPrice, markPrice, markValue, homeNotional, foreignNotional):
        self.symbol = symbol
        self.currency = currency
        self.underlying = underlying
        self.quoteCurrency = quoteCurrency
        self.initMarginReq = initMarginReq
        self.maintMarginReq = maintMarginReq

        self.crossMargin = crossMargin
        self.deleveragePercentile = deleveragePercentile
        self.prevRealisedPnl = prevRealisedPnl  # 上次清仓的盈亏
        self.rebalancedPnl = rebalancedPnl # 一天已经实现的盈亏
        self.currentQty = currentQty
        self.realisedPnl = realisedPnl # 根据book上价格的盈亏
        self.unrealisedPnl = unrealisedPnl # 根据mark price的盈亏
        self.liquidationPrice = liquidationPrice # 强平价格
        self.bankruptPrice = bankruptPrice # 破产价格
        self.markValue = markValue # 标记市值
        self.markPrice = markPrice # 标记价格
        self.foreignNotional =foreignNotional
        self.homeNotional = homeNotional

class SimulatePosition():
    def __init__(self, symbol: Instrument, account: SimulateAccount):
        self.symbol = symbol
        self.account = account
        self.amount = 0
        self.entry_price = 0
        self.isolated = False # isolated or cross
        self.leverage = 0

    @property
    def direction(self):
        return PositionDirection.LONG if self.amount > 0 else PositionDirection.SHORT

    @property
    def value(self):
        return abs(self.amount) / self.mark_price * XBtUnit

    @property
    def funding_rate(self):
        return -0.00375

    @property
    def liq_price(self):
        if self.isolated:
            if self.direction == PositionDirection.LONG:
                funding_rate = self.funding_rate if self.funding_rate > 0 else 0
                return self.entry_price / (1 + 1 / self.leverage - self.symbol.maintMargin - funding_rate)
            else:
                funding_rate = self.funding_rate if self.funding_rate < 0 else 0
                return self.entry_price / (1 - 1 / self.leverage + self.symbol.maintMargin - funding_rate)
        else:
            if self.direction == PositionDirection.LONG:
                return 1/ (1/ self.entry_price * (1- self.symbol.maintMargin) + self.account.wallet_balance/XBtUnit / abs(self.amount))
            else:
                return 1/ (1/ self.entry_price * (1 + self.symbol.maintMargin) - self.account.wallet_balance/XBtUnit / abs(self.amount))

    @property
    def mark_price(self) -> float:
        return

    @property
    def index_price(self):
        return

    @property
    def last_price(self):
        return

    @property
    def position_margin(self):
        return

    @property
    def unrealised_pnl(self):
        return

if __name__ == '__main__':
    from MonkTrader.bitmex.instrument import XBT_SYMBOL
    print(XBT_SYMBOL.takerFee, XBT_SYMBOL.maintMargin)
    account = SimulateAccount(500000)
    p = SimulatePosition(XBT_SYMBOL, account)
    p.isolated = True
    p.amount = -100
    p.entry_price = 3000
    p.leverage = 10
    print(p.liq_price)