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

import pytest
from monkq.assets.account import FutureAccount
from monkq.assets.const import DIRECTION, ORDER_STATUS, SIDE
from monkq.assets.instrument import FutureInstrument, Instrument
from monkq.assets.order import (
    BaseOrder, FutureLimitOrder, FutureMarketOrder,
)
from monkq.assets.trade import Trade

from ..utils import random_string


def test_buy_order_trade(instrument: Instrument) -> None:
    order_id = random_string(6)
    order = BaseOrder(account=MagicMock(), order_id=order_id, instrument=instrument, quantity=100)

    assert order.order_id == order_id
    assert order.side == SIDE.BUY
    assert order.quantity == 100
    assert order.order_status == ORDER_STATUS.NOT_TRADED

    trade1 = Trade(order=order, exec_price=10, exec_quantity=50, trade_id=random_string(6))
    order.deal(trade1)
    assert order.traded_quantity == 50
    assert order.order_status == ORDER_STATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.deal(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=50, trade_id=random_string(6))

    order.deal(trade2)

    assert order.traded_quantity == 100
    assert order.order_status == ORDER_STATUS.FULL_TRADED

    assert trade1 in order.trades
    assert trade2 in order.trades

    assert trade1.order_id == order_id
    assert trade1.side == SIDE.BUY
    assert trade1.exec_price == 10
    assert trade1.value == 500
    assert trade1.commission == 1.25

    assert trade2.order_id == order_id
    assert trade2.side == SIDE.BUY
    assert trade2.exec_price == 11
    assert trade2.value == 550
    assert trade2.commission == 1.375


def test_sell_order_trade(instrument: Instrument) -> None:
    order_id = random_string(6)
    order = BaseOrder(account=MagicMock(), order_id=order_id, instrument=instrument, quantity=-100)

    assert order.order_id == order_id
    assert order.side == SIDE.SELL
    assert order.quantity == -100
    assert order.order_status == ORDER_STATUS.NOT_TRADED

    trade1 = Trade(order=order, exec_price=10, exec_quantity=-50, trade_id=random_string(6))
    order.deal(trade1)
    assert order.traded_quantity == -50
    assert order.order_status == ORDER_STATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.deal(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=-50, trade_id=random_string(6))

    order.deal(trade2)

    assert order.traded_quantity == -100
    assert order.order_status == ORDER_STATUS.FULL_TRADED

    assert trade1 in order.trades
    assert trade2 in order.trades

    assert trade1.order_id == order_id
    assert trade1.side == SIDE.SELL
    assert trade1.exec_price == 10
    assert trade1.value == -500
    assert trade1.commission == 1.25

    assert trade2.order_id == order_id
    assert trade2.side == SIDE.SELL
    assert trade2.exec_price == 11
    assert trade2.value == -550
    assert trade2.commission == 1.375


def test_future_limit_order(future_instrument: FutureInstrument, future_account: FutureAccount) -> None:
    order1 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=100, price=11)
    assert order1.price == 11
    assert order1.quantity == 100
    assert order1.traded_quantity == 0
    assert order1.side == SIDE.BUY
    assert order1.order_value == 1100
    assert order1.order_status == ORDER_STATUS.NOT_TRADED
    assert order1.remain_quantity == 100
    assert order1.remain_value == 1100
    assert order1.direction == DIRECTION.LONG

    trade1 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6))
    order1.deal(trade1)
    assert order1.traded_quantity == 50
    assert order1.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order1.remain_quantity == 50
    assert order1.order_value == 1100
    assert order1.remain_value == 550

    with pytest.raises(AssertionError):
        order1.deal(trade1)

    trade2 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6))
    order1.deal(trade2)
    assert order1.traded_quantity == 100
    assert order1.remain_quantity == 0
    assert order1.order_status == ORDER_STATUS.FULL_TRADED
    assert order1.remain_value == 0

    assert trade1 in order1.trades
    assert trade2 in order1.trades

    order2 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-100, price=13)

    assert order2.price == 13
    assert order2.quantity == -100
    assert order2.traded_quantity == 0
    assert order2.side == SIDE.SELL
    assert order2.order_value == 1300
    assert order2.order_status == ORDER_STATUS.NOT_TRADED
    assert order2.remain_quantity == -100
    assert order2.remain_value == 1300
    assert order2.direction == DIRECTION.SHORT

    trade3 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6))
    order2.deal(trade3)
    assert order2.traded_quantity == -50
    assert order2.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order2.remain_quantity == -50
    assert order2.order_value == 1300
    assert order2.remain_value == 650

    with pytest.raises(AssertionError):
        order2.deal(trade3)

    trade4 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6))
    order2.deal(trade4)
    assert order2.traded_quantity == -100
    assert order2.order_status == ORDER_STATUS.FULL_TRADED
    assert order2.remain_quantity == 0
    assert order2.order_value == 1300
    assert order2.remain_value == 0


def test_future_market_order(future_instrument: FutureInstrument, future_account: FutureAccount) -> None:
    order1 = FutureMarketOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                               quantity=100)
    assert order1.quantity == 100
    assert order1.traded_quantity == 0
    assert order1.side == SIDE.BUY
    assert order1.order_status == ORDER_STATUS.NOT_TRADED
    assert order1.remain_quantity == 100
    assert order1.direction == DIRECTION.LONG

    trade1 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6))
    order1.deal(trade1)
    assert order1.traded_quantity == 50
    assert order1.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order1.remain_quantity == 50

    with pytest.raises(AssertionError):
        order1.deal(trade1)

    trade2 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6))
    order1.deal(trade2)
    assert order1.traded_quantity == 100
    assert order1.remain_quantity == 0
    assert order1.order_status == ORDER_STATUS.FULL_TRADED

    assert trade1 in order1.trades
    assert trade2 in order1.trades

    order2 = FutureMarketOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                               quantity=-100)

    assert order2.quantity == -100
    assert order2.traded_quantity == 0
    assert order2.side == SIDE.SELL
    assert order2.order_status == ORDER_STATUS.NOT_TRADED
    assert order2.remain_quantity == -100
    assert order2.direction == DIRECTION.SHORT

    trade3 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6))
    order2.deal(trade3)
    assert order2.traded_quantity == -50
    assert order2.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order2.remain_quantity == -50

    with pytest.raises(AssertionError):
        order2.deal(trade3)

    trade4 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6))
    order2.deal(trade4)
    assert order2.traded_quantity == -100
    assert order2.order_status == ORDER_STATUS.FULL_TRADED
    assert order2.remain_quantity == 0
