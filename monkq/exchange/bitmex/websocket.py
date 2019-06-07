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
import time
from collections import defaultdict, deque
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from aiohttp import ClientSession, ClientWebSocketResponse  # type: ignore
from logbook import Logger
from monkq.assets.orderbook import DictStructOrderBook
from monkq.base_strategy import BaseStrategy
from monkq.config.global_settings import PING_INTERVAL_FACTOR
from monkq.exchange.base.websocket import ExchangeWebsocketBase
from monkq.exchange.bitmex.auth import gen_header_dict
from monkq.utils.i18n import _

CURRENCY = 'XBt'
FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)
MESSAGE = Dict[str, Union[List, str, Dict]]


def findItemByKeys(keys: list, table: list, matchData: dict) -> Optional[Dict]:
    for item in table:
        matched = True
        for key in keys:
            if item[key] != matchData[key]:
                matched = False
        if matched:
            return item
    return None


def timestamp_update(func: F) -> F:
    @wraps(func)
    def wrapped(self: "BitmexWebsocketBase", *args: Any, **kwargs: Any) -> F:
        self._last_comm_time = time.time()
        ret = func(self, *args, **kwargs)
        return ret

    return cast(F, wrapped)


class BitmexWebsocketBase(ExchangeWebsocketBase):
    MAX_TABLE_LEN = 200

    def __init__(self, strategy: BaseStrategy, loop: asyncio.AbstractEventLoop, session: ClientSession, ws_url: str,
                 api_key: str, api_secret: str, ssl: Optional[ssl.SSLContext] = None,
                 http_proxy: Optional[str] = None):
        self.loop = loop

        self._ssl = ssl
        self.ws_url = ws_url
        self._api_key = api_key
        self._api_secret = api_secret
        self._http_proxy = http_proxy
        self.strategy = strategy
        self.session: ClientSession = session
        self.ping_interval = PING_INTERVAL_FACTOR
        self.exchange_name = "Bitmex"
        self.logger = Logger("exchange.bitmex.websocket")
        self.last_comm_time = 0.  # this is used for a mark point for ping

        # normal data
        self._data: Dict = dict()
        self._keys: Dict = dict()

        self._order_book: Dict[str, DictStructOrderBook] = defaultdict(lambda: DictStructOrderBook())
        self.quote_data: Dict[str, Dict] = defaultdict(dict)
        self.positions: Dict[str, Dict] = defaultdict(dict)

        def _factory(length: int) -> Callable:
            return lambda: deque(maxlen=length)

        self.recent_trades_dict: Dict[str, deque] = defaultdict(_factory(self.MAX_TABLE_LEN))
        self.recent_orders_dict: Dict[str, deque] = defaultdict(_factory(self.MAX_TABLE_LEN))
        self.margin: Dict = dict()

    async def connect(self) -> ClientWebSocketResponse:
        headers = gen_header_dict(self._api_key, self._api_secret, 'GET', "/realtime", '')
        return await self.session.ws_connect(self.ws_url, headers=headers, proxy=self._http_proxy, ssl=self._ssl)

    @timestamp_update
    async def subscribe(self, topic: str) -> None:
        await self.ws_conn.send_json({'op': 'subscribe', "args": [topic]})

    @timestamp_update
    async def subscribe_multiple(self, topics: List[str]) -> None:
        await self.ws_conn.send_json({'op': 'subscribe', "args": topics})

    @timestamp_update
    async def unsubscribe(self, topic: str, symbol: str = '') -> None:
        args = ":".join((topic, symbol))
        await self.ws_conn.send_json({'op': 'unsubscribe', "args": [args]})

    def decode_raw_data(self, data: str) -> Dict:
        return json.loads(data)

    def orders(self) -> List[dict]:
        return self._data['order']

    def recent_trades(self, symbol: str) -> deque:
        return self.recent_trades_dict[symbol]

    def get_position(self, symbol: str) -> dict:
        return self.positions[symbol]

    def error(self, message: str) -> None:

        self.logger.warning(message)

    def get_quote(self, symbol: str) -> dict:
        return self.quote_data[symbol]

    def process_orderbook_data(self, action: str, data: List) -> None:
        if action == 'partial':
            for item in data:
                pass
        elif action == 'insert':
            pass
        elif action == 'update':
            pass
        elif action == 'delete':
            pass
        else:
            raise NotImplementedError()

    def process_margin_data(self, action: str, data: List) -> None:
        if action == 'partial':
            for item in data:
                assert item['currency'] == CURRENCY
                self.margin = item
        elif action == 'update':
            for item in data:
                assert item['currency'] == CURRENCY
                self.margin.update(item)
        else:
            raise NotImplementedError()

    def process_quote_data(self, action: str, data: List) -> None:

        if action == 'partial':
            for item in data:
                self.quote_data[item['symbol']] = item
        elif action == 'insert':
            for item in data:
                self.quote_data[item['symbol']] = item
        else:
            raise NotImplementedError()

    def process_position_data(self, action: str, data: List) -> None:
        if action == 'partial':
            for item in data:
                assert item['currency'] == CURRENCY
                self.positions[item['symbol']] = item
        elif action == 'insert':
            for item in data:
                assert item['currency'] == CURRENCY
                self.positions[item['symbol']] = item
        elif action == 'update':
            for item in data:
                assert item['currency'] == CURRENCY
                self.positions[item['symbol']].update(item)
        else:
            raise NotImplementedError()

    def process_trade_data(self, action: str, data: List) -> None:
        if action == 'partial':
            for item in data:
                self.recent_trades_dict[item['symbol']].append(item)
        elif action == 'insert':
            for item in data:
                self.recent_trades_dict[item['symbol']].append(item)
        else:
            raise NotImplementedError()

    def process_order_data(self, action: str, data: List) -> None:
        if action == 'partial':
            for item in data:
                self.recent_orders_dict[item['symbol']].append(item)
        elif action == 'insert':
            for item in data:
                self.recent_orders_dict[item['symbol']].append(item)
        elif action == "update":
            pass
        else:
            raise NotImplementedError()

    @timestamp_update
    def on_message(self, message: Dict) -> None:
        '''Handler for parsing WS messages.'''
        start = time.time()

        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        if 'subscribe' in message:
            if message['success']:
                self.logger.debug(_("Subscribed to {}").format(message['subscribe']))
            else:
                self.error(_("Unable to subscribe to {}. Error: \"{}\" Please check and restart.").format(
                    message['request']['args'][0], message['error']))
        elif 'unsubscribe' in message:
            if message['success']:
                self.logger.debug(_("Unsubscribed to {}.").format(message['unsubscribe']))
            else:
                self.error(_("Unable to subscribe to {}. Error: \"{}\" Please check and restart.").format(
                    message['request']['args'][0], message['error']))
        elif 'status' in message:
            if message['status'] == 400:
                self.error(message['error'])
            if message['status'] == 401:
                self.error(_("API Key incorrect, please check and restart."))
        elif action:
            if table not in self._data:
                self._data[table] = []

            if table not in self._keys:
                self._keys[table] = []

            if table == "orderBookL2_25":
                self.process_orderbook_data(action, message['data'])
            elif table == "quote":
                self.process_quote_data(action, message['data'])
            elif table == "margin":
                self.process_margin_data(action, message['data'])
            elif table == "position":
                self.process_position_data(action, message['data'])
            elif table == "connected":
                pass
            elif table == "trade":
                self.process_trade_data(action, message['data'])
            elif table == "order":
                # self.process_order_data(action, message['data'])
                pass
            elif table == "execution":
                pass
            else:
                raise NotImplementedError()

        self.logger.debug(_("Tick data process time: {}").format(round(time.time() - start, 7)))
