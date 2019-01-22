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

import asyncio
from functools import partial

import pytest
from aiohttp import ClientSession, ClientTimeout, WSMsgType, web
from MonkTrader.exchange.bitmex.websocket import (
    INTERVAL_FACTOR, BitmexWebsocket,
)
from MonkTrader.interface import AbcStrategy

from ..resource import get_resource_path

pytestmark = pytest.mark.asyncio
API_KEY = "jeg9lHHlfNPu3UbCyLDCYm32"
API_SECRET = "9d9Sjm_vMhWC9BcMOsf9y2hcM37d4sAbUJTyfEumdD3t92qE"

ws_data_path = get_resource_path("mock_bitmex_ws_data.txt")

normal_data_lock = asyncio.Lock()


def ret_data():
    with open(ws_data_path) as f:
        ret_data = f.readlines()
    for data in ret_data:
        yield data


async def realtime_handler(request, async_lock, close_lock):
    ws_data = ret_data()

    await async_lock.acquire()
    await close_lock.acquire()
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    # send welcome data
    await ws.send_str(next(ws_data))

    ret = await ws.receive_json()
    assert ret.get('op') == "subscribe"
    assert ret.get('args') == ['quote:XBTUSD']

    await ws.send_str(next(ws_data))
    await ws.send_str(next(ws_data))

    ret = await ws.receive_json()
    assert ret.get('op') == 'subscribe'
    assert ret.get('args') == ['trade:XBTUSD', "orderBookL2_25:XBTUSD", "position", "margin", "order", "execution",
                               "connected"]

    while not ws.closed:
        try:
            data = next(ws_data)
            if 'unsubscribe' in data:
                async_lock.release()
                ret = await ws.receive_json()
                assert ret.get('op') == 'unsubscribe'
                assert ret.get('args') == ['orderBookL2_25:XBTUSD']
            await ws.send_str(data)
            # in the test , this step never jump to another task,
            # which caused the websocket doesn't get any message
            await asyncio.sleep(0.00001)  # in order to jump out of this loop
        except StopIteration:
            break
    await ws.close()
    close_lock.release()
    return ws


async def ping_handler(request, close_lock):
    ws_data = ret_data()
    ws = web.WebSocketResponse(autoping=False)
    await close_lock.acquire()
    await ws.prepare(request)
    await ws.send_str(next(ws_data))

    await asyncio.sleep(INTERVAL_FACTOR + 3)

    mes = await ws.receive()
    assert mes.type == WSMsgType.PING
    await ws.pong()
    await ws.send_str(next(ws_data))
    close_lock.release()

    while not ws.closed:
        await asyncio.sleep(0.2)


@pytest.fixture()
async def async_lock(loop):
    yield asyncio.Lock(loop=loop)


@pytest.fixture()
async def close_lock(loop):
    yield asyncio.Lock(loop=loop)


@pytest.fixture()
async def normal_bitmex_server(aiohttp_server, async_lock, close_lock):
    app = web.Application()
    app.router.add_get('/realtime', partial(realtime_handler, async_lock=async_lock, close_lock=close_lock))
    server = await aiohttp_server(app)
    yield server


@pytest.fixture()
async def ping_bitmex_server(aiohttp_server, close_lock):
    app = web.Application()
    app.router.add_get('/realtime', partial(ping_handler, close_lock=close_lock))
    server = await aiohttp_server(app)
    yield server


class C(AbcStrategy):
    async def setup(self) -> None:
        pass

    async def on_trade(self, message) -> None:
        pass

    async def tick(self, message) -> None:
        pass

    async def handle_bar(self) -> None:
        pass


async def test_bitmex_websocket(normal_bitmex_server, loop, async_lock, close_lock):
    session = ClientSession(timeout=ClientTimeout(total=60))
    ws = BitmexWebsocket(C(), loop, session, "ws://127.0.0.1:{}/realtime".format(normal_bitmex_server.port), API_KEY, API_SECRET)

    await ws.setup()
    await ws.subscribe('quote', 'XBTUSD')
    await asyncio.sleep(1)
    await ws.subscribe_multiple(
        ['trade:XBTUSD', "orderBookL2_25:XBTUSD", "position", "margin", "order", "execution", "connected"])

    await async_lock.acquire()
    await ws.unsubscribe("orderBookL2_25", "XBTUSD")

    await close_lock.acquire()

    xbtusd_quote = ws.get_quote('XBTUSD')
    assert xbtusd_quote['bidSize'] == 1342
    assert xbtusd_quote['bidPrice'] == 3620.5
    assert xbtusd_quote['askPrice'] == 3621
    assert xbtusd_quote['askSize'] == 62873

    trades = ws.recent_trades()

    trade1 = trades[-8]
    assert trade1['side'] == "Buy"
    assert trade1['size'] == 1595
    assert trade1['price'] == 3621
    assert trade1['tickDirection'] == 'ZeroPlusTick'
    assert trade1['trdMatchID'] == 'ed100d93-562d-9ac7-86b3-1dd153ca7d85'
    assert trade1['grossValue'] == 44049115
    assert trade1['homeNotional'] == 0.44049115
    assert trade1['foreignNotional'] == 1595

    position = ws.get_position('XBTUSD')
    assert position['currentQty'] == 1000
    assert position['markPrice'] == 3617.52
    assert position['liquidationPrice'] == 3304.5

    order_book = ws.get_order_book("XBTUSD")
    assert order_book.Buy[15599637950]['side'] == "Buy"
    assert order_book.Buy[15599637950]['size'] == 1342
    assert order_book.Buy[15599637950]['price'] == 3620.5

    orders = ws.orders()
    assert orders[-1]['orderID'] == "aeeff587-89b2-36a8-a482-d7aa49dc1261"
    assert orders[-1]['account'] == 142643
    assert orders[-1]['symbol'] == "EOSH19"
    assert orders[-1]['side'] == "Sell"
    assert orders[-1]['orderQty'] == 20
    assert orders[-1]['price'] == 0.0006991
    assert orders[-1]['leavesQty'] == 20
    assert orders[-1]['cumQty'] == 0

    await ws.stop()
    await session.close()


async def test_bitmex_websocket_ping(ping_bitmex_server, loop, close_lock):
    session = ClientSession()
    ws = BitmexWebsocket(C(), loop, session, "ws://127.0.0.1:{}/realtime".format(ping_bitmex_server.port), API_KEY, API_SECRET)

    await ws.setup()
    await close_lock.acquire()

    await ws.stop()
    await session.close()


@pytest.mark.xfail
def test_bitmex_websocket_lost_connections():
    assert False
