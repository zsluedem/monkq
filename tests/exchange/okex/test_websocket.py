from typing import Generator, Callable, Coroutine
from asyncio import AbstractEventLoop, Lock, sleep
import pytest
from functools import partial
from aiohttp.test_utils import TestServer

from aiohttp import ClientSession, web
from unittest.mock import MagicMock
from monkq.exchange.okex.websocket import OKexWebsocket
from monkq.exchange.okex.auth import OKexAuth
from tests.tools import get_resource_path
import zlib
import logging

ws_data_path = get_resource_path("okex/okex_websocket_data.txt")

passphrase = '123456789'
api_key = 'ab58ebe8-3557-4521-9c2f-asf9341239f9'
api_secret = '5B07K919C77118F8E234K28344F82Q9D5'

def ret_data() -> Generator[str, None, None]:
    with open(ws_data_path) as f:
        ret_data = f.readlines()
    for data in ret_data:
        yield data


async def realtime_handler(request: web.Request, close_lock: Lock) -> web.WebSocketResponse:
    ws_data = ret_data()

    await close_lock.acquire()
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    # send welcome data

    while not ws.closed:
        try:
            data = next(ws_data)
            obj = zlib.compressobj(wbits=-zlib.MAX_WBITS)
            d = obj.compress(data.encode('utf8'))
            d += obj.flush()
            await ws.send_bytes(d)
            # in the test , this step never jump to another task,
            # which caused the websocket doesn't get any message
            await sleep(0.001)  # in order to jump out of this loop
        except StopIteration:
            break
    close_lock.release()
    return ws


@pytest.fixture()  # type:ignore
async def close_lock(loop: AbstractEventLoop) -> Lock:
    yield Lock(loop=loop)


@pytest.fixture()  # type:ignore
async def okex_websocket_server(aiohttp_server: Callable[[web.Application], Coroutine[TestServer, None, None]],
                                close_lock: Lock) -> None:
    app = web.Application()
    app.router.add_get('/tess_websocket', partial(realtime_handler, close_lock=close_lock))
    server = await aiohttp_server(app)
    yield server


async def test_okex_websocket(loop: AbstractEventLoop, okex_websocket_server: TestServer, close_lock: Lock):
    session = ClientSession()
    auth_ins = OKexAuth(api_key, api_secret, passphrase)
    ws = OKexWebsocket(MagicMock(), loop, session, "ws://localhost:{}/tess_websocket".format(okex_websocket_server.port),
                       api_key=api_key, api_secret=api_secret,
                       pass_phrase=passphrase, auth_instance=auth_ins)
    await ws.setup()
    await ws.subscribe('swap/depth:BTC-USD-SWAP')

    await close_lock.acquire()
    await ws.stop()
    await session.close()


async def test_okex_websocket_checksum(loop: AbstractEventLoop):
    depth_partial_data = {
        "table": "spot/depth",
        "action": "partial",
        "data": [{
            "instrument_id": "ETH-USDT",
            "asks": [
                ["8.8", "96.99999966", 1],
                ["9", "39", 3],
                ["9.5", "100", 1],
                ["12", "12", 1],
                ["95", "0.42973686", 3],
                ["11111", "1003.99999795", 1]
            ],
            "bids": [
                ["5", "7", 4],
                ["3", "5", 3],
                ["2.5", "100", 2],
                ["1.5", "100", 1],
                ["1.1", "100", 1],
                ["1", "1004.9998", 1]
            ],
            "timestamp": "2018-12-18T07:27:13.655Z",
            "checksum": 468410539
        }]
    }

    session = ClientSession()
    auth_ins = OKexAuth(api_key, api_secret, passphrase)
    ws = OKexWebsocket(MagicMock(), loop, session, "test", api_key=api_key, api_secret=api_secret,
                       pass_phrase=passphrase, auth_instance=auth_ins)
    ws.on_message(depth_partial_data)

    assert ws.is_checksum_correct('ETH-USDT', 468410539)
