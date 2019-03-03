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
from unittest.mock import MagicMock

from MonkTrader.assets.order import BaseOrder, LimitOrder, MarketOrder
from MonkTrader.utils.as_dict import (
    base_order_to_dict, limit_order_to_dict, market_order_to_dict,
)
from MonkTrader.utils.id import gen_unique_id


def test_base_order_to_dict() -> None:
    instrument = MagicMock()
    instrument.symbol = "XBTUSD"
    order = BaseOrder(MagicMock(), gen_unique_id(), instrument, 100)

    d_order = base_order_to_dict(order)

    assert d_order == {'order_id': order.order_id,
                       'quantity': 100,
                       'traded_quantity': 0,
                       'trades': [],
                       'symbol': "XBTUSD"}


def tests_limit_order_to_dict() -> None:
    instrument = MagicMock()
    instrument.symbol = "XBTUSD"
    order = LimitOrder(MagicMock(), gen_unique_id(), instrument, 100, price=10)

    d_order = limit_order_to_dict(order)

    assert d_order == {'order_id': order.order_id,
                       'quantity': 100,
                       'traded_quantity': 0,
                       'trades': [],
                       'symbol': "XBTUSD", 'price': 10, 'order_type': 'limit'}


def test_market_order_to_dict() -> None:
    instrument = MagicMock()
    instrument.symbol = "XBTUSD"
    order = MarketOrder(MagicMock(), gen_unique_id(), instrument, 100)

    d_order = market_order_to_dict(order)

    assert d_order == {'order_id': order.order_id,
                       'quantity': 100,
                       'traded_quantity': 0,
                       'trades': [],
                       'symbol': "XBTUSD", 'order_type': 'market'}
