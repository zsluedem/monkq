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

from MonkTrader.assets.order import BaseOrder, SIDE, ORDERSTATUS
from MonkTrader.assets.trade import Trade
from ..utils import random_string
from .mock_resource import instrument
import pytest


def test_buy_order_trade():
    order_id = random_string(6)
    order = BaseOrder(order_id=order_id, instrument=instrument, quantity=100)

    assert order.order_id == order_id
    assert order.side == SIDE.BUY
    assert order.quantity == 100
    assert order.order_status == ORDERSTATUS.NOT_TRADED

    trade1 = Trade(order=order, exec_price=10, exec_quantity=50, trade_id=random_string(6))
    order.traded(trade1)
    assert order.traded_quantity == 50
    assert order.order_status == ORDERSTATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.traded(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=50, trade_id=random_string(6))

    order.traded(trade2)

    assert order.traded_quantity == 100
    assert order.order_status == ORDERSTATUS.FULL_TRADED

    assert trade1 in order.trades
    assert trade2 in order.trades

    assert trade1.order_id == order_id
    assert trade1.side == SIDE.BUY
    assert trade1.exec_price == 10
    assert trade1.value == 500
    assert trade1.commission == 1.25
    assert trade1.avg_price == 10.025

    assert trade2.order_id == order_id
    assert trade2.side == SIDE.BUY
    assert trade2.exec_price == 11
    assert trade2.value == 550
    assert trade2.commission == 1.375
    assert trade2.avg_price == 11.0275


def test_sell_order_trade():
    order_id = random_string(6)
    order = BaseOrder(order_id=order_id, instrument=instrument, quantity=-100)

    assert order.order_id == order_id
    assert order.side == SIDE.SELL
    assert order.quantity == -100
    assert order.order_status == ORDERSTATUS.NOT_TRADED

    trade1 = Trade(order=order, exec_price=10, exec_quantity=-50, trade_id=random_string(6))
    order.traded(trade1)
    assert order.traded_quantity == -50
    assert order.order_status == ORDERSTATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.traded(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=-50, trade_id=random_string(6))

    order.traded(trade2)

    assert order.traded_quantity == -100
    assert order.order_status == ORDERSTATUS.FULL_TRADED

    assert trade1 in order.trades
    assert trade2 in order.trades

    assert trade1.order_id == order_id
    assert trade1.side == SIDE.SELL
    assert trade1.exec_price == 10
    assert trade1.value == -500
    assert trade1.commission == 1.25
    assert trade1.avg_price == 10.025

    assert trade2.order_id == order_id
    assert trade2.side == SIDE.SELL
    assert trade2.exec_price == 11
    assert trade2.value == -550
    assert trade2.commission == 1.375
    assert trade2.avg_price == 11.0275
