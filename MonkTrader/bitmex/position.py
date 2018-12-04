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

class Position():
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