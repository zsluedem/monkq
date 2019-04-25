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

import datetime
from typing import Dict, Optional, ValuesView

from logbook import Logger
from monkq.assets.order import ORDER_T, LimitOrder, MarketOrder
from monkq.assets.trade import Trade
from monkq.exception import ImpossibleError
from monkq.stat import Statistic
from monkq.utils.id import gen_unique_id

from .log import core_log_group

logger = Logger('trade_counter')
core_log_group.add_logger(logger)


class TradeCounter:
    def __init__(self, stat: Statistic) -> None:
        self._open_orders: Dict[str, ORDER_T] = {}
        self.stat = stat
        self._traded_orders: Dict[str, ORDER_T] = {}

    def match(self, match_time: datetime.datetime) -> None:
        close_order_ids = []
        for order in self._open_orders.values():
            if isinstance(order, MarketOrder):
                trade = Trade(order, order.account.exchange.last_price(order.instrument),
                              order.quantity, gen_unique_id(), match_time)
            elif isinstance(order, LimitOrder):
                trade = Trade(order, order.price, order.quantity, gen_unique_id(), match_time)
            else:
                raise ImpossibleError("Unsupported order type {}".format(type(order)))

            self.stat.collect_trade(trade)

            logger.debug("Trade counter match a trade {}".format(trade))
            order.deal(trade)
            if order.remain_quantity == 0:
                close_order_ids.append(order.order_id)
        for order_id in close_order_ids:
            self._open_orders.pop(order_id)

    def submit_order(self, order: ORDER_T) -> None:
        self._open_orders[order.order_id] = order
        self.stat.collect_order(order)

    def cancel_order(self, order_id: str) -> ORDER_T:
        return self._open_orders.pop(order_id)

    # TODO
    def amend_order(self, order_id: str, quantity: Optional[float], price: Optional[float]) -> None:
        raise NotImplementedError()

    def open_orders(self) -> ValuesView[ORDER_T]:
        return self._open_orders.values()
