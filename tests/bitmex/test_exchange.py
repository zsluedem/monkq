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

import json
from asyncio import AbstractEventLoop
from typing import Generator
from unittest.mock import MagicMock

import pandas
import pytest
from asynctest import CoroutineMock
from monkq.assets.instrument import FutureInstrument
from monkq.exchange.bitmex.exchange import (
    BitmexExchange, BitmexSimulateExchange, bitmex_info,
)
from monkq.tradecounter import TradeCounter
from monkq.utils.id import gen_unique_id
from monkq.utils.timefunc import utc_datetime

from ..tools import get_resource_path


@pytest.fixture()
def mock_httpinterface() -> Generator[MagicMock, None, None]:
    m = MagicMock()
    m.get_instrument_info = CoroutineMock(return_value=[{'lastPrice': 100}])
    m.place_limit_order = CoroutineMock(return_value=gen_unique_id())
    m.place_market_order = CoroutineMock(return_value=gen_unique_id())
    resp = MagicMock()
    resp.status = 200
    m.amend_order = CoroutineMock(return_value=resp)
    m.cancel_order = CoroutineMock(return_value=resp)
    m.open_orders_http = CoroutineMock(return_value=[])
    with open(get_resource_path('bitmex/active_instrument.json')) as f:
        instruments = json.load(f)
    m.active_instruments = CoroutineMock(return_value=instruments)
    with open(get_resource_path('bitmex/kline_data.json')) as f:
        klines = json.load(f)
    m.get_kline = CoroutineMock(return_value=klines)
    trades = json.loads("""[
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
    m.get_recent_trades = CoroutineMock(return_value=trades)
    yield m


async def test_exchange(mock_httpinterface: MagicMock, loop: AbstractEventLoop) -> None:
    WS = MagicMock()
    ws = WS()
    ws.setup = CoroutineMock(return_value=None)
    context = MagicMock()
    context.settings.SSL_PATH = None
    exchange = BitmexExchange(context, 'bitmex', {"IS_TEST": True}, loop)
    exchange.http_interface = mock_httpinterface
    exchange.ws = ws
    await exchange.setup()

    instrument = MagicMock()
    instrument.symbol = "XBTUSD"
    account = MagicMock()
    assert await exchange.get_last_price(instrument) == 100

    #
    assert exchange.exchange_info() == bitmex_info

    order = await exchange.place_limit_order(account, instrument, 10, 100)

    await exchange.place_market_order(account, instrument, 100)

    await exchange.amend_order(account, order, 200, 10)

    await exchange.cancel_order(account, order)
    # TODO
    await exchange.open_orders(account)

    await exchange.available_instruments()
    # use cache below
    await exchange.available_instruments()

    instru = await exchange.get_instrument('XRPH19')
    assert instru.symbol == 'XRPH19'

    df = await exchange.get_kline(instrument)
    assert isinstance(df, pandas.DataFrame)

    await exchange.get_recent_trades(instrument)

    await exchange.close()


async def test_bitmex_exchange_simulate(tem_data_dir: str, instrument: FutureInstrument) -> None:
    context = MagicMock()
    account = MagicMock()
    trade_counter = TradeCounter(MagicMock())
    context.trade_counter = trade_counter
    context.settings.DATA_DIR = tem_data_dir
    sim_exchange = BitmexSimulateExchange(context, 'bitmex', {"START_WALLET_BALANCE": 1000000})

    await sim_exchange.setup()
    instrument = instrument
    context.now = utc_datetime(2016, 10, 3, 12, 30)
    assert await sim_exchange.get_last_price(instrument) == 63744.0

    assert sim_exchange.exchange_info() == bitmex_info

    order_id = await sim_exchange.place_limit_order(account, instrument, 10, 100)

    market_order_id = await sim_exchange.place_market_order(account, instrument, 100)

    await sim_exchange.cancel_order(account, order_id)

    open_orders = await sim_exchange.open_orders(account)

    assert len(open_orders) == 1

    order = open_orders[0]
    assert order['order_id'] == market_order_id

    assert await sim_exchange.available_instruments()

    ins = await sim_exchange.get_instrument('XBUZ15')
    assert ins.symbol == 'XBUZ15'

    kline = await sim_exchange.get_kline(instrument)

    assert kline.index[-1] == utc_datetime(2016, 10, 3, 12, 30)

    sim_exchange.match_open_orders()

    sim_exchange.all_data(instrument)
