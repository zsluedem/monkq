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

import pickle
from unittest.mock import MagicMock

import pytest
from monkq.assets.account import FutureAccount
from monkq.assets.const import DIRECTION, ORDER_STATUS, SIDE
from monkq.assets.instrument import FutureInstrument, Instrument
from monkq.assets.order import (
    BaseOrder, FutureLimitOrder, FutureMarketOrder, StopLimitOrder,
    StopMarketOrder,
)
from monkq.assets.trade import Trade
from monkq.utils.timefunc import utc_datetime

from ..utils import random_string


def test_buy_order_trade(instrument: Instrument) -> None:
    order_id = random_string(6)
    order = BaseOrder(account=MagicMock(), order_id=order_id, instrument=instrument,
                      quantity=100, submit_datetime=utc_datetime(2018, 1, 1))

    assert order.order_id == order_id
    assert order.side == SIDE.BUY
    assert order.quantity == 100
    assert order.order_status == ORDER_STATUS.NOT_TRADED
    assert order.submit_datetime == utc_datetime(2018, 1, 1)

    trade1 = Trade(order=order, exec_price=10, exec_quantity=50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order.deal(trade1)
    assert order.traded_quantity == 50
    assert order.order_status == ORDER_STATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.deal(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 2))

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
    order = BaseOrder(account=MagicMock(), order_id=order_id, instrument=instrument,
                      quantity=-100, submit_datetime=utc_datetime(2018, 1, 1))

    assert order.order_id == order_id
    assert order.side == SIDE.SELL
    assert order.quantity == -100
    assert order.order_status == ORDER_STATUS.NOT_TRADED
    assert order.submit_datetime == utc_datetime(2018, 1, 1)

    trade1 = Trade(order=order, exec_price=10, exec_quantity=-50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order.deal(trade1)
    assert order.traded_quantity == -50
    assert order.order_status == ORDER_STATUS.PARTLY_TRADED

    with pytest.raises(AssertionError):
        order.deal(trade1)

    trade2 = Trade(order=order, exec_price=11, exec_quantity=-50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 2))

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
                              quantity=100, price=11, submit_datetime=utc_datetime(2018, 1, 1))
    assert order1.price == 11
    assert order1.quantity == 100
    assert order1.traded_quantity == 0
    assert order1.side == SIDE.BUY
    assert order1.order_value == 1100
    assert order1.order_status == ORDER_STATUS.NOT_TRADED
    assert order1.remain_quantity == 100
    assert order1.remain_value == 1100
    assert order1.direction == DIRECTION.LONG

    trade1 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order1.deal(trade1)
    assert order1.traded_quantity == 50
    assert order1.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order1.remain_quantity == 50
    assert order1.order_value == 1100
    assert order1.remain_value == 550

    with pytest.raises(AssertionError):
        order1.deal(trade1)

    trade2 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order1.deal(trade2)
    assert order1.traded_quantity == 100
    assert order1.remain_quantity == 0
    assert order1.order_status == ORDER_STATUS.FULL_TRADED
    assert order1.remain_value == 0

    assert trade1 in order1.trades
    assert trade2 in order1.trades

    order2 = FutureLimitOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                              quantity=-100, price=13, submit_datetime=utc_datetime(2018, 1, 1))

    assert order2.price == 13
    assert order2.quantity == -100
    assert order2.traded_quantity == 0
    assert order2.side == SIDE.SELL
    assert order2.order_value == 1300
    assert order2.order_status == ORDER_STATUS.NOT_TRADED
    assert order2.remain_quantity == -100
    assert order2.remain_value == 1300
    assert order2.direction == DIRECTION.SHORT

    trade3 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order2.deal(trade3)
    assert order2.traded_quantity == -50
    assert order2.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order2.remain_quantity == -50
    assert order2.order_value == 1300
    assert order2.remain_value == 650

    with pytest.raises(AssertionError):
        order2.deal(trade3)

    trade4 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order2.deal(trade4)
    assert order2.traded_quantity == -100
    assert order2.order_status == ORDER_STATUS.FULL_TRADED
    assert order2.remain_quantity == 0
    assert order2.order_value == 1300
    assert order2.remain_value == 0


def test_future_market_order(future_instrument: FutureInstrument, future_account: FutureAccount) -> None:
    order1 = FutureMarketOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                               quantity=100, submit_datetime=utc_datetime(2018, 1, 1))
    assert order1.quantity == 100
    assert order1.traded_quantity == 0
    assert order1.side == SIDE.BUY
    assert order1.order_status == ORDER_STATUS.NOT_TRADED
    assert order1.remain_quantity == 100
    assert order1.direction == DIRECTION.LONG

    trade1 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order1.deal(trade1)
    assert order1.traded_quantity == 50
    assert order1.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order1.remain_quantity == 50

    with pytest.raises(AssertionError):
        order1.deal(trade1)

    trade2 = Trade(order=order1, exec_price=11, exec_quantity=50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order1.deal(trade2)
    assert order1.traded_quantity == 100
    assert order1.remain_quantity == 0
    assert order1.order_status == ORDER_STATUS.FULL_TRADED

    assert trade1 in order1.trades
    assert trade2 in order1.trades

    order2 = FutureMarketOrder(order_id=random_string(6), account=future_account, instrument=future_instrument,
                               quantity=-100, submit_datetime=utc_datetime(2018, 1, 1))

    assert order2.quantity == -100
    assert order2.traded_quantity == 0
    assert order2.side == SIDE.SELL
    assert order2.order_status == ORDER_STATUS.NOT_TRADED
    assert order2.remain_quantity == -100
    assert order2.direction == DIRECTION.SHORT

    trade3 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order2.deal(trade3)
    assert order2.traded_quantity == -50
    assert order2.order_status == ORDER_STATUS.PARTLY_TRADED
    assert order2.remain_quantity == -50

    with pytest.raises(AssertionError):
        order2.deal(trade3)

    trade4 = Trade(order=order2, exec_price=13, exec_quantity=-50, trade_id=random_string(6),
                   trade_datetime=utc_datetime(2018, 1, 1, 0, 1))
    order2.deal(trade4)
    assert order2.traded_quantity == -100
    assert order2.order_status == ORDER_STATUS.FULL_TRADED
    assert order2.remain_quantity == 0


def test_order_pickle(future_instrument: FutureInstrument) -> None:
    account = MagicMock()
    account.exchange.name = 'exchange_sample'
    order_id1 = random_string(6)
    order1 = FutureMarketOrder(order_id=order_id1, account=account, instrument=future_instrument,
                               quantity=100, submit_datetime=utc_datetime(2018, 1, 1))
    p_order = pickle.dumps(order1)

    unp_order = pickle.loads(p_order)

    assert unp_order.quantity == 100
    assert unp_order.traded_quantity == 0
    assert unp_order.exchange == 'exchange_sample'
    assert unp_order.order_id == order_id1
    assert unp_order.instrument.symbol == future_instrument.symbol
    assert unp_order.side == SIDE.BUY
    assert unp_order.remain_quantity == 100
    assert unp_order.order_class == "FutureMarketOrder"
    assert unp_order.direction == DIRECTION.LONG
    assert unp_order.submit_datetime == utc_datetime(2018, 1, 1)

    order_id2 = random_string(6)
    order2 = FutureLimitOrder(order_id=order_id2, account=account, instrument=future_instrument,
                              quantity=100, price=11, submit_datetime=utc_datetime(2018, 1, 1))
    p_order2 = pickle.dumps(order2)
    unp_order2 = pickle.loads(p_order2)
    assert unp_order2.quantity == 100
    assert unp_order2.traded_quantity == 0
    assert unp_order2.exchange == 'exchange_sample'
    assert unp_order2.order_id == order_id2
    assert unp_order2.instrument.symbol == future_instrument.symbol
    assert unp_order2.side == SIDE.BUY
    assert unp_order2.remain_quantity == 100
    assert unp_order2.order_class == "FutureLimitOrder"
    assert unp_order2.direction == DIRECTION.LONG
    assert unp_order2.submit_datetime == utc_datetime(2018, 1, 1)

    order_id3 = random_string(6)
    order3 = StopLimitOrder(order_id=order_id3, account=account, instrument=future_instrument,
                            quantity=100, stop_price=11, submit_datetime=utc_datetime(2018, 1, 1))
    p_order3 = pickle.dumps(order3)
    unp_order3 = pickle.loads(p_order3)
    assert unp_order3.quantity == 100
    assert unp_order3.traded_quantity == 0
    assert unp_order3.exchange == 'exchange_sample'
    assert unp_order3.order_id == order_id3
    assert unp_order3.instrument.symbol == future_instrument.symbol
    assert unp_order3.side == SIDE.BUY
    assert unp_order3.remain_quantity == 100
    assert unp_order3.order_class == "StopLimitOrder"
    assert unp_order3.stop_price == 11
    assert unp_order3.submit_datetime == utc_datetime(2018, 1, 1)

    order_id4 = random_string(6)
    order4 = StopMarketOrder(order_id=order_id4, account=account, instrument=future_instrument,
                             quantity=100, stop_price=11, submit_datetime=utc_datetime(2018, 1, 1))
    p_order4 = pickle.dumps(order4)
    unp_order4 = pickle.loads(p_order4)
    assert unp_order4.quantity == 100
    assert unp_order4.traded_quantity == 0
    assert unp_order4.exchange == 'exchange_sample'
    assert unp_order4.order_id == order_id4
    assert unp_order4.instrument.symbol == future_instrument.symbol
    assert unp_order4.side == SIDE.BUY
    assert unp_order4.remain_quantity == 100
    assert unp_order4.order_class == "StopMarketOrder"
    assert unp_order4.stop_price == 11
    assert unp_order4.submit_datetime == utc_datetime(2018, 1, 1)


def test_trade_pickle(future_instrument: FutureInstrument) -> None:
    order_id1 = random_string(6)
    account = MagicMock()
    account.exchange.name = 'exchange_sample'
    order = FutureMarketOrder(order_id=order_id1, account=account, instrument=future_instrument,
                              quantity=100, submit_datetime=utc_datetime(2018, 1, 1))
    trade_id = random_string(6)
    trade = Trade(order=order, exec_price=13, exec_quantity=50, trade_id=trade_id,
                  trade_datetime=utc_datetime(2018, 1, 1, 0, 1))

    p_trade = pickle.dumps(trade)
    unp_trade = pickle.loads(p_trade)
    assert unp_trade.order.order_id == order_id1
    assert unp_trade.exec_price == 13
    assert unp_trade.exec_quantity == 50
    assert unp_trade.trade_id == trade_id
    assert unp_trade.side == SIDE.BUY
    assert unp_trade.value == 650
    assert unp_trade.commission == 1.625
    assert unp_trade.trade_datetime == utc_datetime(2018, 1, 1, 0, 1)
