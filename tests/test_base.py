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

from asyncio import AbstractEventLoop, Lock, sleep
from functools import partial
from typing import Callable, Coroutine
from unittest.mock import MagicMock

import pytest
from aiohttp import (  # type:ignore
    ClientSession, ClientWebSocketResponse, WSMsgType, web,
)
from aiohttp.test_utils import TestServer
from logbook import Logger
from monkq.config.global_settings import PING_INTERVAL_FACTOR
from monkq.exchange.base.websocket import AbsExchangeWebsocket, BackgroundTask

pytestmark = pytest.mark.asyncio

INFO = "Message"


class ExchangeWebsocketBase(AbsExchangeWebsocket):
    ping_interval = PING_INTERVAL_FACTOR
    logger = Logger('TestWebsocketBase')

    def __init__(self, ws_url: str, exchange_name: str, session: ClientSession, loop: AbstractEventLoop):
        self.ws_url = ws_url
        self.exchange_name = exchange_name
        self.session = session
        self.loop = loop
        self.background_task = BackgroundTask()

    async def connect(self) -> ClientWebSocketResponse:
        return await self.session.ws_connect(self.ws_url)

    def decode_raw_data(self, data: str) -> str:
        return data

    def on_message(self, message: str) -> None:
        pass


@pytest.fixture()  # type:ignore
async def close_lock(loop: AbstractEventLoop) -> Lock:
    yield Lock(loop=loop)


async def base_handler(request: web.Request, close_lock: Lock) -> None:
    ws = web.WebSocketResponse(autoping=False)
    await close_lock.acquire()
    await ws.prepare(request)
    await ws.send_str(INFO)

    await sleep(PING_INTERVAL_FACTOR + 3)

    mes = await ws.receive()
    assert mes.type == WSMsgType.PING
    await ws.pong()
    close_lock.release()

    while not ws.closed:
        await sleep(0.2)


@pytest.fixture()  # type:ignore
async def ping_bitmex_server(aiohttp_server: Callable[[web.Application], Coroutine[TestServer, None, None]],
                             close_lock: Lock) -> None:
    app = web.Application()
    app.router.add_get('/realtime', partial(base_handler, close_lock=close_lock))  # type:ignore
    server = await aiohttp_server(app)
    yield server


async def test_base_websocket(ping_bitmex_server: TestServer, loop: AbstractEventLoop, close_lock: Lock) -> None:
    session = ClientSession()

    ws = ExchangeWebsocketBase("ws://127.0.0.1:{}/realtime".format(ping_bitmex_server.port), "test_exchange", session,
                               loop)
    decode_mock = MagicMock()
    on_message_mock = MagicMock()
    ws.decode_raw_data = decode_mock  # type:ignore
    ws.on_message = on_message_mock  # type:ignore

    await ws.setup()
    await close_lock.acquire()
    await ws.stop()
    decode_mock.assert_called_once_with(INFO)
    on_message_mock.assert_called_once()
    await session.close()
