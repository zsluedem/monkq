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
from MonkTrader.bitmex.positionreal import SimulatePosition
from MonkTrader.bitmex.const import PositionDirection
from MonkTrader.const import XBtUnit
import pytest

class MockAccount():
    def __init__(self, wallet_balance):
        self.wallet_balance = wallet_balance


class MockInstrument():
    def __init__(self):
        self.maintMargin = 0.005
        self.initMargin = 0.01
        self.takerFee = 0.00075


account = MockAccount(1000000)
instrument = MockInstrument()


def test_isolated_perpetual_position():
    position = SimulatePosition(instrument, account)
    position.isolated = True
    position.amount = 1000
    position.entry_price = 3600
    position.leverage = 3

    assert position.direction == PositionDirection.LONG
    assert position.value == 1000 / 3600 * XBtUnit
    assert position.liq_price == pytest.approx(2710.5, 0.1)


def test_cross_perpetual_position():
    position = SimulatePosition(instrument, account)
    position.isolated = False
    position.amount = 1000
    position.entry_price = 3600
