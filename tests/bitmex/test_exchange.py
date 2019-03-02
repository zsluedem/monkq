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

from typing import List, Any, Generator, Type
from MonkTrader.exchange.bitmex.exchange import BitmexExchange, bitmex_info
from unittest.mock import MagicMock, patch
from asyncio import AbstractEventLoop
import pytest
from uuid import uuid4
import json
import pandas
from ..tools import get_resource_path

kline_data = """[
  {
    "timestamp": "2019-03-02T02:14:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822.5,
    "low": 3821.5,
    "close": 3822.5,
    "trades": 19,
    "volume": 10702,
    "vwap": 3821.8995,
    "lastSize": 2,
    "turnover": 280019022,
    "homeNotional": 2.8001902199999993,
    "foreignNotional": 10702
  },
  {
    "timestamp": "2019-03-02T02:13:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822.5,
    "low": 3822,
    "close": 3822,
    "trades": 11,
    "volume": 764,
    "vwap": 3822.1916,
    "lastSize": 100,
    "turnover": 19988954,
    "homeNotional": 0.19988953999999998,
    "foreignNotional": 764
  },
  {
    "timestamp": "2019-03-02T02:12:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822.5,
    "low": 3822,
    "close": 3822,
    "trades": 3,
    "volume": 113,
    "vwap": 3822.4839,
    "lastSize": 10,
    "turnover": 2956232,
    "homeNotional": 0.029562320000000003,
    "foreignNotional": 113
  },
  {
    "timestamp": "2019-03-02T02:11:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822,
    "low": 3822,
    "close": 3822,
    "trades": 1,
    "volume": 7,
    "vwap": 3822,
    "lastSize": 7,
    "turnover": 183148,
    "homeNotional": 0.00183148,
    "foreignNotional": 7
  },
  {
    "timestamp": "2019-03-02T02:10:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822,
    "low": 3822,
    "close": 3822,
    "trades": 0,
    "volume": 0,
    "vwap": null,
    "lastSize": null,
    "turnover": 0,
    "homeNotional": 0,
    "foreignNotional": 0
  },
  {
    "timestamp": "2019-03-02T02:09:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822,
    "low": 3822,
    "close": 3822,
    "trades": 0,
    "volume": 0,
    "vwap": null,
    "lastSize": null,
    "turnover": 0,
    "homeNotional": 0,
    "foreignNotional": 0
  },
  {
    "timestamp": "2019-03-02T02:08:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822.5,
    "low": 3822,
    "close": 3822,
    "trades": 15,
    "volume": 1827,
    "vwap": 3822.3377,
    "lastSize": 100,
    "turnover": 47798889,
    "homeNotional": 0.4779888900000001,
    "foreignNotional": 1827
  },
  {
    "timestamp": "2019-03-02T02:07:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822,
    "low": 3822,
    "close": 3822,
    "trades": 0,
    "volume": 0,
    "vwap": null,
    "lastSize": null,
    "turnover": 0,
    "homeNotional": 0,
    "foreignNotional": 0
  },
  {
    "timestamp": "2019-03-02T02:06:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822,
    "low": 3822,
    "close": 3822,
    "trades": 0,
    "volume": 0,
    "vwap": null,
    "lastSize": null,
    "turnover": 0,
    "homeNotional": 0,
    "foreignNotional": 0
  },
  {
    "timestamp": "2019-03-02T02:05:00.000Z",
    "symbol": "XBTUSD",
    "open": 3822,
    "high": 3822,
    "low": 3822,
    "close": 3822,
    "trades": 0,
    "volume": 0,
    "vwap": null,
    "lastSize": null,
    "turnover": 0,
    "homeNotional": 0,
    "foreignNotional": 0
  }
]"""


class MockInterface():
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def get_instrument_info(self, *args: Any, **kwargs: Any) -> List[dict]:
        return [{'lastPrice': 100}]

    async def place_limit_order(self, *args: Any, **kwargs: Any) -> str:
        return str(uuid4())

    async def place_market_order(self, *args: Any, **kwargs: Any) -> str:
        return str(uuid4())

    async def amend_order(self, *args: Any, **kwargs: Any) -> MagicMock:
        resp = MagicMock()
        resp.status = 200
        return resp

    async def cancel_order(self, *args: Any, **kwargs: Any) -> MagicMock:
        resp = MagicMock()
        resp.status = 200
        return resp

    async def open_orders(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def active_instruments(self, *args: Any, **kwargs: Any) -> List[dict]:
        with open(get_resource_path('bitmex/active_instrument.json')) as f:
            return json.load(f)

    async def get_kline(self, *args: Any, **kwargs: Any) -> List[dict]:
        with open(get_resource_path('bitmex/kline_data.json')) as f:
            return json.load(f)

    async def get_recent_trades(self, *args: Any, **kwargs: Any) -> List[dict]:
        return json.loads("""[
{
  "timestamp": "2019-03-02T02:38:58.304Z",
  "symbol": "XBTUSD",
  "side": "Sell",
  "size": 1297,
  "price": 3828.5,
  "tickDirection": "ZeroMinusTick",
  "trdMatchID": "8260edc2-26d6-e8b7-616a-1d5c21ffa37f",
  "grossValue": 33877640,
  "homeNotional": 0.3387764,
  "foreignNotional": 1297
}]""")


@pytest.fixture()
def mock_httpinterface() -> Generator[Type[MockInterface], None, None]:
    yield MockInterface


async def test_exchange(mock_httpinterface: MagicMock, loop: AbstractEventLoop) -> None:
    with patch("MonkTrader.exchange.bitmex.exchange.BitMexHTTPInterface", mock_httpinterface):
        exchange = BitmexExchange(MagicMock(), 'bitmex', {"IS_TEST": True}, loop)
        exchange.http_interface = mock_httpinterface
        # await exchange.setup()

        instrument = MagicMock()
        instrument.symbol = "XBTUSD"
        assert await exchange.get_last_price(instrument) == 100

        assert exchange.exchange_info() == bitmex_info

        order = await exchange.place_limit_order(instrument, 10, 100)

        await exchange.place_market_order(instrument, 100)

        await exchange.amend_order(order, 200, 10)

        await exchange.cancel_order(order)
        # TODO
        await exchange.open_orders()

        await exchange.available_instruments()
        # use cache below
        await exchange.available_instruments()

        df = await exchange.get_kline(instrument, '1m')
        assert isinstance(df, pandas.DataFrame)

        await exchange.get_recent_trades(instrument)

        await exchange.close()
