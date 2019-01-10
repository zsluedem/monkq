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

from MonkTrader.assets.order import BaseOrder, SIDE, ORDERSTATUS, FutureLimitOrder
from MonkTrader.assets.trade import Trade
from ..utils import random_string
import pytest


def test_buy_order_trade(base_account, instrument):
    order_id = random_string(6)
    order = BaseOrder(account=base_account, order_id=order_id, instrument=instrument, quantity=100)

    assert order.order_id == order_id
    assert order.side == SIDE.BUY
    assert order.quantity == 100
    assert order.order_status == ORDERSTATUS.NOT_TRADED

    trade1 = Trade(order=order, exec_price=10, exec_quantity=50, trade_id=random_string(6))
    order.deal(trade1)
    assert order.traded_quantity == 50
    assert order.order_status == ORDERSTATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.deal(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=50, trade_id=random_string(6))

    order.deal(trade2)

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


def test_sell_order_trade(base_account, instrument):
    order_id = random_string(6)
    order = BaseOrder(account=base_account, order_id=order_id, instrument=instrument, quantity=-100)

    assert order.order_id == order_id
    assert order.side == SIDE.SELL
    assert order.quantity == -100
    assert order.order_status == ORDERSTATUS.NOT_TRADED

    trade1 = Trade(order=order, exec_price=10, exec_quantity=-50, trade_id=random_string(6))
    order.deal(trade1)
    assert order.traded_quantity == -50
    assert order.order_status == ORDERSTATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.deal(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=-50, trade_id=random_string(6))

    order.deal(trade2)

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


def test_future_limit_order(future_instrument, future_account):
    future_account.positions[future_instrument].quantity = 0
    future_account.positions[future_instrument].leverage = 10
    order1 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=100, price=11)
    assert order1.margin_value == 115.775  # open a position, 100 * 11 /10 * (1+ 0.05 + 0.0025)

    future_account.positions[future_instrument].quantity = 100
    future_account.positions[future_instrument].leverage = 5
    order2 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=100, price=11)
    assert order2.margin_value == 231.55  # get more on a position 100 * 11 /5 * (1+ 0.05 + 0.0025)

    future_account.positions[future_instrument].quantity = 200
    future_account.positions[future_instrument].leverage = 5
    order3 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-200, price=11)
    assert order3.margin_value == 0  # reduce position does't require the margin

    future_account.positions[future_instrument].quantity = 100
    future_account.positions[future_instrument].leverage = 5
    order4 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-100, price=11)
    assert order4.margin_value == 0  # close position does't require the margin

    future_account.positions[future_instrument].quantity = 200
    future_account.positions[future_instrument].leverage = 5
    order5 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-300, price=12)
    assert order5.margin_value == 252.6  # close position and open a opposite position 100 * 12 /5 * (1+ 0.05+ 0.0025)

    future_account.positions[future_instrument].quantity = 0
    future_account.positions[future_instrument].leverage = 3
    order6 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-300, price=12)
    assert order6.margin_value == 1263.0  # open a position, 300 * 12 /3 * (1+ 0.05 + 0.0025)

    future_account.positions[future_instrument].quantity = -300
    future_account.positions[future_instrument].leverage = 3
    order7 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-100, price=12)
    assert order7.margin_value == 421.0  # open a position, 300 * 12 /3 * (1+ 0.05 + 0.0025)

    future_account.positions[future_instrument].quantity = -400
    future_account.positions[future_instrument].leverage = 3
    order8 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=200, price=12)
    assert order8.margin_value == 0  # reduce position does't require the margin

    future_account.positions[future_instrument].quantity = -200
    future_account.positions[future_instrument].leverage = 2
    order9 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=200, price=12)
    assert order9.margin_value == 0  # close position does't require the margin

    future_account.positions[future_instrument].quantity = -200
    future_account.positions[future_instrument].leverage = 2
    order10 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                               quantity=300, price=12)
    assert order10.margin_value == 631.5  # close position and open a opposite position 100 * 12 /2 * (1+ 0.05+ 0.0025)
