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

class AccountMargin():
    def __init__(self, maintMargin, unrealisedPnl, walletBalance, marginBalance, marginLeverage, marginUsedPcnt, initMargin, availableMargin, grossComm, grossLastValue):
        self.walletBalance = walletBalance # 钱包余额
        self.unrealisedPnl = unrealisedPnl # 未实现盈亏
        self.marginBalance = marginBalance # 保证金余额
        self.maintMargin = maintMargin # 仓位保证金
        self.initMargin = initMargin # 委托保证金
        self.availableMargin = availableMargin # 可用保证金
        self.marginLeverage = marginLeverage # 杠杆
        self.marginUsedPcnt = marginUsedPcnt # 保证金使用百分比

        self.grossComm = grossComm # 8 小时内的合计委托费用
        self.grossLastValue =  grossLastValue # 总持仓市值
