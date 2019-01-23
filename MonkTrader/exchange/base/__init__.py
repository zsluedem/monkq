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
from typing import List, Union

from MonkTrader.assets import T_INSTRUMENT, T_ORDER, AbcAccount
from MonkTrader.context import Context


class BaseExchange:
    def __init__(self, context: Context, name: str, exchange_setting: dict) -> None:
        self.context = context
        self.name = name
        self.exchange_setting = exchange_setting

    def get_last_price(self, instrument: Union[str, T_INSTRUMENT]) -> float:
        """

        :param instrument:
        :return:
        """
        raise NotImplementedError()

    def exchange_info(self) -> None:
        """
        get the exchange information
        :return:
        """
        raise NotImplementedError()

    def place_limit_order(self, target: Union[str, T_INSTRUMENT], price: float, quantity: float) -> str:
        """
        create a new limit order in the exchange.

        It would return an uuid of the order, you can find the order by id.
        """
        raise NotImplementedError()

    def place_market_order(self) -> str:
        """
        create a new market order in the exchange.

        It would return an uuid of the order, you can find the order by id.
        :return:
        """
        raise NotImplementedError()

    def amend_order(self, order_id: str, **options: Union[str, float]) -> None:
        """
        amend an order price , quantitu or etc.
        """
        raise NotImplementedError()

    def cancel_order(self, order_id: str) -> None:
        """
        cancel an order from the exchange by the order id.
        """
        raise NotImplementedError()

    def open_orders(self) -> List[T_ORDER]:
        raise NotImplementedError()

    def get_order(self, order_id: str) -> T_ORDER:
        """
        get the order obj by th order_id returned when the order was created.
        :param order_id:
        :return:
        """
        raise NotImplementedError()

    def get_account(self) -> AbcAccount:
        raise NotImplementedError()

    def available_instruments(self) -> None:
        raise NotImplementedError()

    def setup(self) -> None:
        raise NotImplementedError()

    def config(self) -> None:
        raise NotImplementedError()

    # def order_book(self) -> None:
    #     raise NotImplementedError()
    # def withdraw(self) -> None:
    #     raise NotImplementedError()
    #
    # def deposit(self) -> None:
    #     raise NotImplementedError()

    # def place_stop_limit_order(self) -> None:
    #     raise NotImplementedError()
    #
    # def place_stop_market_order(self) -> None:
    #     raise NotImplementedError()
