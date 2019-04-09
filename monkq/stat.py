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
import pickle
from typing import TYPE_CHECKING, Dict, List, Union

from monkq.assets.order import ORDER_T, BaseOrder
from monkq.assets.trade import Trade

if TYPE_CHECKING:
    from monkq.context import Context

DAILY_STAT_TYPE = Dict[str, Union[float, datetime.datetime]]


class Statistic():
    def __init__(self, context: "Context"):
        self.context = context
        self.report_file: str = getattr(self.context.settings, 'REPORT_FILE', 'result.pkl')
        self.daily_capital: List[DAILY_STAT_TYPE] = []
        self.order_collections: List[BaseOrder] = []
        self.trade_collections: List[Trade] = []

    def collect_daily(self) -> None:
        accounts_capital: DAILY_STAT_TYPE = {k: v.total_capital for k, v in self.context.accounts.items()}
        accounts_capital.update({'timestamp': self.context.now})
        self.daily_capital.append(accounts_capital)

    def collect_order(self, order: ORDER_T) -> None:
        self.order_collections.append(order)

    def collect_trade(self, trade: Trade) -> None:
        self.trade_collections.append(trade)

    def _pickle_obj(self) -> dict:
        return {
            "daily_capital": self.daily_capital,
            "orders": self.order_collections,
            "trades": self.trade_collections,
            "start_datetime": self.context.settings.START_TIME,  # type: ignore
            "end_datetime": self.context.settings.END_TIME,  # type:ignore
        }

    def report(self) -> None:
        with open(self.report_file, 'wb') as f:
            pickle.dump(self._pickle_obj(), f)
