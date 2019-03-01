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

from typing import Dict, Optional, ValuesView

from MonkTrader.assets.order import BaseOrder, LimitOrder, MarketOrder
from MonkTrader.assets.trade import Trade
from MonkTrader.exception import ImpossibleError
from MonkTrader.exchange.base import BaseExchange
from MonkTrader.utils.id import gen_unique_id


class TradeCounter():
    def __init__(self, exchange: BaseExchange) -> None:
        self._open_orders: Dict[str, BaseOrder] = {}
        self.exchange: BaseExchange = exchange

        self._traded_orders: Dict[str, BaseOrder] = {}

    async def match(self) -> None:
        close_order_ids = []
        for order in self._open_orders.values():
            if isinstance(order, MarketOrder):
                trade = Trade(order, await self.exchange.get_last_price(order.instrument), order.quantity,
                              gen_unique_id())
            elif isinstance(order, LimitOrder):
                trade = Trade(order, order.price, order.quantity, gen_unique_id())
            else:
                raise ImpossibleError("Unsupported order type {}".format(type(order)))

            order.deal(trade)
            if order.remain_quantity == 0:
                close_order_ids.append(order.order_id)
        for order_id in close_order_ids:
            self._open_orders.pop(order_id)

    def submit_order(self, order: BaseOrder) -> None:
        self._open_orders[order.order_id] = order

    def cancel_order(self, order_id: str) -> None:
        self._open_orders.pop(order_id)

    def amend_order(self, order_id: str, quantity: Optional[float], price: Optional[float]) -> None:
        raise NotImplementedError()

    def open_orders(self) -> ValuesView[BaseOrder]:
        return self._open_orders.values()
