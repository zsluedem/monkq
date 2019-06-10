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
import json
import ssl
import zlib
from collections import defaultdict
from typing import Any, Dict, Optional, TypeVar

from aiohttp import ClientSession, ClientWebSocketResponse  # type: ignore
from logbook import Logger
from monkq.assets.orderbook import DictStructOrderBook
from monkq.base_strategy import BaseStrategy
from monkq.exchange.base.websocket import ExchangeWebsocketBase
from monkq.exchange.okex.auth import OKexAuth
from yarl import URL

from . import const as c

T = TypeVar('T')


class OKexWebsocket(ExchangeWebsocketBase):
    ping_interval = 3
    exchange_name = "OKEX"

    def __init__(self, strategy: BaseStrategy, loop: asyncio.AbstractEventLoop, session: ClientSession, ws_url: str,
                 api_key: str, api_secret: str, pass_phrase: str, auth_instance: Optional[OKexAuth] = None,
                 ssl: Optional[ssl.SSLContext] = None,
                 http_proxy: Optional[str] = None):
        self.strategy = strategy
        self.loop = loop
        self.ws_url = ws_url
        self.api_key = api_key
        self.api_secret = api_secret
        self._ssl = ssl
        self._http_proxy = http_proxy
        self.session = session
        self.auth_instance = auth_instance
        self.pass_phrase = pass_phrase

        self.timestamp = None
        self.logger = Logger("OkexWebsocket")
        self._order_book: Dict[str, DictStructOrderBook] = defaultdict(lambda: DictStructOrderBook())
        self._order_book_status: Dict[str, bool] = defaultdict(bool)

    async def connect(self) -> ClientWebSocketResponse:
        return await self.session.ws_connect(self.ws_url, proxy=self._http_proxy, ssl=self._ssl)

    async def setup(self) -> None:
        await super(OKexWebsocket, self).setup()
        if self.auth_instance is not None:
            await self.auth()

    async def auth(self) -> None:
        if self.auth_instance is not None:
            sign_dict = self.auth_instance.gen_http_headers("GET", URL(c.API_URL + "/users/self/verify"), '')
            await self.ws_conn.send_json(
                {"op": "login",
                 "args": [self.api_key, self.pass_phrase, sign_dict[c.OK_ACCESS_TIMESTAMP],
                          sign_dict[c.OK_ACCESS_SIGN]]})

    async def subscribe(self, topic: str) -> None:
        await self.ws_conn.send_json({"op": 'subscribe', "args": [topic]})

    async def unsubscribe(self, topic: str) -> None:
        await self.ws_conn.send_json({"op": 'unsubscribe', "args": [topic]})

    def decode_raw_data(self, data: Any) -> dict:
        decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
        )
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return json.loads(inflated)

    def checksum_value(self, instrument_id: str) -> int:
        best_bid25 = self._order_book[instrument_id].best_bid_n(25)
        best_ask25 = self._order_book[instrument_id].best_ask_n(25)
        check_string = ":".join(["{}:{}:{}:{}".format(bid.raw[0], bid.raw[1], ask.raw[0], ask.raw[1]) for bid, ask in
                                 zip(best_bid25, best_ask25)])
        return zlib.crc32(check_string.encode('utf8'))

    def is_checksum_correct(self, instrument_id: str, checksum: int) -> bool:
        return self.checksum_value(instrument_id) == checksum

    def process_depth_table(self, message: dict) -> None:
        # with open("{}.json".format(self.i), 'w') as  f:
        #     json.dump(message, f)
        action = message['action']
        data = message['data'][0]
        instrument_id = data.get('instrument_id')
        checksum = data.get('checksum')
        bid_data = data.get('bids')
        ask_data = data.get('asks')
        if action == 'partial':
            for item in bid_data:
                size = float(item[1])
                price = float(item[0])
                self._order_book[instrument_id].insert(
                    {'side': "Buy", 'id': price, 'size': size, 'price': price, 'raw': item})
            for item in ask_data:
                size = float(item[1])
                price = float(item[0])
                self._order_book[instrument_id].insert(
                    {'side': "Sell", 'id': price, 'size': size, 'price': price, 'raw': item})
        elif action == 'update':
            for item in bid_data:
                size = float(item[1])
                price = float(item[0])
                if size == 0:
                    self._order_book[instrument_id].delete({'id': price, 'side': "Buy"})
                else:
                    self._order_book[instrument_id].update(
                        {'id': price, 'size': size, 'side': "Buy", 'price': price, 'raw': item})
            for item in ask_data:
                size = float(item[1])
                price = float(item[0])
                if size == 0:
                    self._order_book[instrument_id].delete({'id': price, 'side': "Sell"})
                else:
                    self._order_book[instrument_id].update(
                        {'id': price, 'size': size, 'side': "Sell", 'price': price, 'raw': item})
        else:
            raise NotImplementedError()
        self._order_book_status[instrument_id] = True if self.is_checksum_correct(instrument_id, checksum) else False

    def on_message(self, message: dict) -> Any:
        event = message.get('event')
        if event == 'subscribe':
            self.logger.info("Successfully subscribe channel: {}".format(message.get('channel')))
        elif event == 'login':
            result = message.get('success')
            if result:
                self.logger.info("Successfully login with {}".format(self.auth_instance))
            else:
                self.logger.warning("Failed to login with {}".format(self.auth_instance))
        table = message.get('table')
        if table is None:
            return
        else:
            trade_target, subscribe_item = table.split('/')
            if subscribe_item == 'depth':
                self.process_depth_table(message)

            else:
                raise NotImplementedError()
