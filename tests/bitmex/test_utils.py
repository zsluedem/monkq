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
from MonkTrader.assets.const import SIDE
from MonkTrader.const import TICK_DIRECTION
from MonkTrader.exchange.bitmex.data.utils import read_trade_tar
from tests.tools import get_resource_path


def test_read_trade_tar() -> None:
    path = get_resource_path('bitmex/20170430.csv.gz')
    df = read_trade_tar(path, True)
    assert df['side'][0] == SIDE.BUY.value
    assert df['side'][1] == SIDE.SELL.value

    assert df['tickDirection'][0] == TICK_DIRECTION.MINUS_TICK.value
    assert df['tickDirection'][1] == TICK_DIRECTION.ZERO_MINUS_TICK.value
    assert df['tickDirection'][2] == TICK_DIRECTION.PLUS_TICK.value
    assert df['tickDirection'][3] == TICK_DIRECTION.ZERO_PLUS_TICK.value
