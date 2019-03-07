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
from typing import TYPE_CHECKING, Any, List, Optional, ValuesView

import pandas
from MonkTrader.context import Context

from .info import ExchangeInfo

if TYPE_CHECKING:
    from MonkTrader.assets.account import BaseAccount  # pragma: no cover
    from MonkTrader.assets.instrument import Instrument  # noqa  pragma: no cover
    from MonkTrader.assets.order import BaseOrder  # noqa   pragma: no cover


class BaseExchange:
    def __init__(self, context: Context, name: str, exchange_setting: dict) -> None:
        self.context = context
        self.name = name
        self.exchange_setting = exchange_setting

    async def setup(self) -> None:
        raise NotImplementedError()

    async def get_last_price(self, instrument: Any) -> float:
        """
        get instrument last trade price
        """
        raise NotImplementedError()

    def exchange_info(self) -> ExchangeInfo:
        """
        get the exchange information
        """
        raise NotImplementedError()

    async def place_limit_order(self, instrument: Any,
                                price: float, quantity: float) -> str:
        """
        create a new limit order in the exchange.

        It would return an uuid of the order, you can find the order by id.
        """
        raise NotImplementedError()

    async def place_market_order(self, instrument: Any,
                                 quantity: float) -> str:
        """
        create a new market order in the exchange.

        It would return an uuid of the order, you can find the order by id.
        """
        raise NotImplementedError()

    async def amend_order(self, order_id: str, quantity: Optional[float], price: Optional[float]) -> bool:
        """
        amend an order price , quantitu or etc.
        """
        raise NotImplementedError()

    async def cancel_order(self, order_id: str) -> bool:
        """
        cancel an order from the exchange by the order id.
        If you cancel the order successfully, it would return True
        otherwise False.
        """
        raise NotImplementedError()

    async def open_orders(self) -> List[dict]:
        """
        get all the open orders
        """
        raise NotImplementedError()

    def get_order(self, order_id: str) -> BaseOrder:
        """
        get the order obj by th order_id returned when the order was created.
        """
        raise NotImplementedError()

    def get_account(self) -> BaseAccount:
        raise NotImplementedError()

    async def available_instruments(self) -> ValuesView["Instrument"]:
        """
        return all the available instruments at the moment
        """
        raise NotImplementedError()

    async def get_kline(self, instrument: Any, count: int = 100, including_now: bool = False) -> pandas.DataFrame:
        """
        get an instrument kline
        """
        raise NotImplementedError()

    async def get_recent_trades(self, instrument: Any) -> List[dict]:
        """
        get recent trade. Maximum recent 500 trades
        """
        raise NotImplementedError()

    # def order_book(self) -> None:
    #     raise NotImplementedError()
    # def withdraw(self) -> None:
    #     raise NotImplementedError()s
    #
    # def deposit(self) -> None:
    #     raise NotImplementedError()

    # def place_stop_limit_order(self) -> None:
    #     raise NotImplementedError()
    #
    # def place_stop_market_order(self) -> None:
    #     raise NotImplementedError()
