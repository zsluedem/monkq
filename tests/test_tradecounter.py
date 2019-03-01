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

from unittest.mock import MagicMock, call

import pytest
from MonkTrader.assets.order import LimitOrder, MarketOrder
from MonkTrader.tradecounter import TradeCounter
from MonkTrader.utils.id import gen_unique_id


async def test_trader_counter() -> None:
    exchange = MagicMock()
    account = MagicMock()

    trade_counter = TradeCounter(exchange)

    async def last_price() -> float:
        return 20.

    exchange.get_last_price.return_value = last_price()

    order1 = LimitOrder(account=account, order_id=gen_unique_id(), instrument=MagicMock(), quantity=100, price=10)
    order2 = LimitOrder(account=account, order_id=gen_unique_id(), instrument=MagicMock(), quantity=200, price=20)
    order3 = MarketOrder(account=account, order_id=gen_unique_id(), instrument=MagicMock(), quantity=100)
    trade_counter.submit_order(order1)
    trade_counter.submit_order(order2)
    trade_counter.submit_order(order3)
    assert len(trade_counter.open_orders()) == 3
    trade_counter.cancel_order(order1.order_id)

    with pytest.raises(NotImplementedError):
        trade_counter.amend_order(order2.order_id, 100, 20)

    assert len(trade_counter.open_orders()) == 2
    await trade_counter.match()

    assert len(order2.trades) == 1
    assert len(order3.trades) == 1
    assert len(trade_counter.open_orders()) == 0
    trades = []
    trades.extend(order2.trades)
    trades.extend(order3.trades)
    trade_calls = [call(t) for t in trades]
    account.deal.assert_has_calls(trade_calls)
