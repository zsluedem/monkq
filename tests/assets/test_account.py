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
from MonkTrader.assets.account import FutureAccount
from MonkTrader.assets.positions import FuturePosition
from MonkTrader.assets.trade import Trade
from ..utils import random_string
from MonkTrader.assets.order import FutureLimitOrder
import pytest
from typing import List

@pytest.mark.xfail
def test_future_account(exchange, future_instrument, future_instrument2):
    open_orders: List[FutureLimitOrder] = []
    exchange.open_orders.return_value = open_orders
    exchange.get_last_price.return_value = 10

    account = FutureAccount(exchange=exchange, position_cls=FuturePosition, wallet_balance=10000)
    assert account.position_margin == 0
    assert account.order_margin == 0
    assert account.unrealised_pnl == 0
    assert account.wallet_balance == 10000
    assert account.margin_balance == 10000
    assert account.available_balance == 10000


    # open a position
    order1 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=100, price=11)
    open_orders.append(order1)
    # assert account.order_margin == order1.order_margin
    trade1 = Trade(order=order1, exec_price=11, exec_quantity=100, trade_id=random_string(6))
    account.deal(trade1)
    open_orders.remove(order1)

    assert account.wallet_balance == 9997.25
    assert account.position_margin == pytest.approx(52.50, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == -102.5
    assert account.margin_balance == 9894.75
    assert account.available_balance == 9842.25

    # more on a position
    order2 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=200, price=10.5)
    open_orders.append(order2)
    # assert account.order_margin == order2.order_margin
    trade2 = Trade(order=order2, exec_price=10.5, exec_quantity=200, trade_id=random_string(6))
    account.deal(trade2)
    open_orders.remove(order2)

    assert account.wallet_balance == 9992.0
    assert account.position_margin == pytest.approx(157.50, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == -207.5
    assert account.margin_balance == 9784.5
    assert account.available_balance == 9627.0

    # close part
    order3 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=-100, price=10)
    open_orders.append(order3)
    assert account.order_margin == 0
    trade3 = Trade(order=order3, exec_price=10, exec_quantity=-100, trade_id=random_string(6))
    account.deal(trade3)
    open_orders.remove(order3)

    assert account.wallet_balance == pytest.approx(9922.8333, 0.0001)
    assert account.position_margin == pytest.approx(105, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == pytest.approx( -138.3333, 0.0001)
    assert account.margin_balance == pytest.approx(9784.5000, 0.0001)
    assert account.available_balance == pytest.approx( 9679.5000, 0.0001)

    # close and open
    order4 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=-300, price=11)
    open_orders.append(order4)
    # assert account.order_margin == order4.order_margin
    trade4 = Trade(order=order4, exec_price=11, exec_quantity=-300, trade_id=random_string(6))
    account.deal(trade4)
    open_orders.remove(order4)

    assert account.wallet_balance == pytest.approx(9981.2513, 0.0001)
    assert account.position_margin == pytest.approx(52.5, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == pytest.approx(97.5, 0.0001)
    assert account.margin_balance == pytest.approx(10078.7513, 0.0001)
    assert account.available_balance == pytest.approx(10026.2513, 0.0001)

    # get more
    order5 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=-100, price=10.5)
    open_orders.append(order5)
    # assert account.order_margin == 0
    trade5 = Trade(order=order5, exec_price=10.5, exec_quantity=-100, trade_id=random_string(6))
    account.deal(trade5)
    open_orders.remove(order5)

    assert account.wallet_balance == pytest.approx(9978.6263, 0.0001)
    assert account.position_margin == pytest.approx(105, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == pytest.approx(145.0, 0.0001)
    assert account.margin_balance == pytest.approx(10123.6263, 0.0001)
    assert account.available_balance == pytest.approx(10018.6263, 0.0001)

    # close and open
    order6 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=300, price=10.5)
    open_orders.append(order6)
    # assert account.order_margin == 0
    trade6 = Trade(order=order6, exec_price=10.5, exec_quantity=300, trade_id=random_string(6))
    account.deal(trade6)
    open_orders.remove(order6)

    assert account.wallet_balance == pytest.approx(10020.7513, 0.0001)
    assert account.position_margin == pytest.approx(52.5, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == pytest.approx(-52.5, 0.0001)
    assert account.margin_balance == pytest.approx(9968.2513, 0.0001)
    assert account.available_balance == pytest.approx(9915.7513, 0.0001)

    # close
    order7 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=-100, price=9)
    open_orders.append(order7)
    # assert account.order_margin == 0
    trade7 = Trade(order=order7, exec_price=9, exec_quantity=-100, trade_id=random_string(6))
    account.deal(trade7)
    open_orders.remove(order7)

    assert account.wallet_balance == pytest.approx(9868.5013, 0.0001)
    assert account.position_margin == 0
    assert account.order_margin == 0
    assert account.unrealised_pnl == 0
    assert account.margin_balance == pytest.approx(9868.5013, 0.0001)
    assert account.available_balance == pytest.approx(9868.5013, 0.0001)

    # close
    order8 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=-150, price=11)
    open_orders.append(order8)
    # assert account.order_margin == 0
    trade8 = Trade(order=order8, exec_price=11, exec_quantity=-150, trade_id=random_string(6))
    account.deal(trade8)
    open_orders.remove(order8)

    assert account.wallet_balance == pytest.approx(9864.3763, 0.0001)
    assert account.position_margin == pytest.approx(78.7500, 0.0001)
    assert account.order_margin == 0
    assert account.unrealised_pnl == pytest.approx(146.25, 0.0001)
    assert account.margin_balance == pytest.approx(10010.6263, 0.0001)
    assert account.available_balance == pytest.approx(9931.8763, 0.0001)

    order9 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=150, price=11)
    open_orders.append(order9)
    # assert account.order_margin == 0
    trade9 = Trade(order=order9, exec_price=11, exec_quantity=150, trade_id=random_string(6))
    account.deal(trade9)
    open_orders.remove(order9)

    assert account.wallet_balance == pytest.approx(9860.2513, 0.0001)
    assert account.position_margin == 0
    assert account.order_margin == 0
    assert account.unrealised_pnl == 0
    assert account.margin_balance == pytest.approx(9860.2513, 0.0001)
    assert account.available_balance == pytest.approx(9860.2513, 0.0001)

    # test the order margin of the account when the account have two different direction orders
    # TODO
    untraded_order1 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                              quantity=100, price=5)
    untraded_order2 = FutureLimitOrder(order_id=random_string(6), account=account, instrument=future_instrument,
                                       quantity=-100, price=20)

    # test the position margin of the account when the account have two different positions
    # TODO
    assert False