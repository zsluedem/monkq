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
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from aiohttp import (  # type: ignore
    ClientSession, ClientWebSocketResponse, WSMsgType,
)
from logbook import Logger
from monkq.base_strategy import BaseStrategy
from monkq.exception import ImpossibleError
from monkq.exchange.bitmex.auth import gen_header_dict
from monkq.utils.i18n import _

from .log import logger_group

OrderBook = namedtuple('OrderBook', ['Buy', 'Sell'])
CURRENCY = 'XBt'
INTERVAL_FACTOR = 3

logger = Logger("exchange.bitmex.websocket")
logger_group.add_logger(logger)

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
    def wrapped(self: "BitmexWebsocket", *args: Any, **kwargs: Any) -> F:
        self._last_comm_time = time.time()
        ret = func(self, *args, **kwargs)
        return ret

    return cast(F, wrapped)


@dataclass()
class BackgroundTask:
    ping: asyncio.Task = field(init=False)
    handler: asyncio.Task = field(init=False)


class BitmexWebsocket():
    MAX_TABLE_LEN = 200

    def __init__(self, strategy: BaseStrategy, loop: asyncio.AbstractEventLoop, session: ClientSession, ws_url: str,
                 api_key: str, api_secret: str, ssl: Optional[ssl.SSLContext] = None,
                 http_proxy: Optional[str] = None):
        self._loop = loop

        self._ws: ClientWebSocketResponse = None
        self._ssl = ssl
        self._ws_url = ws_url
        self._api_key = api_key
        self._api_secret = api_secret
        self._http_proxy = http_proxy
        self.background_task = BackgroundTask()
        self.strategy = strategy
        self.session: ClientSession = session
        self._last_comm_time = 0.  # this is used for a mark point for ping

        # below is used for data store, it depends on what kind of data it subscribe

        # normal data
        self._data: Dict = dict()
        self._keys: Dict = dict()

        self.quote_data: Dict[str, Dict] = defaultdict(dict)
        self.order_book: Dict[str, OrderBook[Dict, Dict]] = defaultdict(  # type:ignore
            lambda: OrderBook(Buy=dict(), Sell=dict()))
        self.positions: Dict[str, Dict] = defaultdict(dict)
        self.margin: Dict = dict()

    async def setup(self) -> None:
        headers = gen_header_dict(self._api_key, self._api_secret, 'GET', "/realtime", '')

        self._ws = await self.session.ws_connect(self._ws_url, headers=headers, proxy=self._http_proxy, ssl=self._ssl)
        self._last_comm_time = time.time()
        self.background_task.handler = self._loop.create_task(self._run())
        self.background_task.ping = self._loop.create_task(self._ping())

    async def stop(self) -> None:
        if not self._ws.closed:
            await self._ws.close()
        await self.background_task.handler
        await self.background_task.ping

    async def _ping(self) -> None:
        try:
            while not self._ws.closed:
                if time.time() - self._last_comm_time > INTERVAL_FACTOR:
                    logger.debug(
                        _('No communication during {} seconds. Send ping signal to keep connection open').format(
                            INTERVAL_FACTOR))
                    await self._ws.ping()
                    self._last_comm_time = time.time()
                await asyncio.sleep(INTERVAL_FACTOR)
        except asyncio.CancelledError:
            logger.warning(_('Your bitmex ping task has been stopped'))

    async def _run(self) -> None:
        try:
            while not self._ws.closed:
                message = await self._ws.receive()
                logger.debug(_("Receive message from bitmex:{}").format(message.data))
                if message.type in (WSMsgType.CLOSE, WSMsgType.CLOSING):
                    continue
                elif message.type == WSMsgType.CLOSED:
                    break
                decode_message = json.loads(message.data)
                self._on_message(decode_message)

                # call strategy method
                # websocket first package is not a normal package , so we use 'limit' to skip it
                if decode_message.get('action'):
                    if decode_message.get('table') == 'execution':
                        start = time.time()
                        ret = self.strategy.on_trade(message=decode_message)
                        if asyncio.iscoroutine(ret):
                            await ret
                        logger.debug(_('User on_trade process time: {}').format(round(time.time() - start, 7)))
                    else:
                        start = time.time()
                        ret = self.strategy.tick(message=decode_message)
                        if asyncio.iscoroutine(ret):
                            await ret
                        logger.debug(_('User tick process time: {}').format(round(time.time() - start, 7)))
        except asyncio.CancelledError:
            logger.warning(_('Your bitmex handler has been stopped'))

    @timestamp_update
    async def subscribe(self, topic: str, symbol: str = '') -> None:
        await self._ws.send_json({'op': 'subscribe', "args": [':'.join((topic, symbol))]})

    @timestamp_update
    async def subscribe_multiple(self, topics: List[str]) -> None:
        await self._ws.send_json({'op': 'subscribe', "args": topics})

    @timestamp_update
    async def unsubscribe(self, topic: str, symbol: str = '') -> None:
        args = ":".join((topic, symbol))
        await self._ws.send_json({'op': 'unsubscribe', "args": [args]})

    def orders(self) -> List[dict]:
        return self._data['order']

    def recent_trades(self) -> List[dict]:
        return self._data['trade']

    def get_position(self, symbol: str) -> dict:
        return self.positions[symbol]

    def get_quote(self, symbol: str) -> dict:
        return self.quote_data[symbol]

    def get_order_book(self, symbol: str) -> OrderBook:
        return self.order_book[symbol]

    def error(self, error: str) -> None:
        pass

    @timestamp_update
    def _on_message(self, message: dict) -> None:
        '''Handler for parsing WS messages.'''
        start = time.time()

        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        if 'subscribe' in message:
            if message['success']:
                logger.debug(_("Subscribed to {}").format(message['subscribe']))
            else:
                self.error(_("Unable to subscribe to {}. Error: \"{}\" Please check and restart.").format(
                    message['request']['args'][0], message['error']))
        elif 'unsubscribe' in message:
            if message['success']:
                logger.debug(_("Unsubscribed to {}.").format(message['unsubscribe']))
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

            # There are four possible actions from the WS:
            # 'partial' - full table image
            # 'insert'  - new row
            # 'update'  - update row
            # 'delete'  - delete row
            if action == 'partial':
                logger.debug("{}: partial".format(table))
                if message['table'] == "quote":
                    for data in message['data']:
                        self.quote_data[data['symbol']] = data
                elif message['table'] == 'orderBookL2_25':
                    for data in message['data']:
                        side_book = getattr(self.order_book[data['symbol']], data['side'])
                        side_book[data['id']] = data
                elif message['table'] == 'position':
                    for data in message['data']:
                        assert data['currency'] == CURRENCY
                        self.positions[data['symbol']] = data
                elif message['table'] == 'margin':
                    for data in message['data']:
                        assert data['currency'] == CURRENCY
                        self.margin = data
                else:
                    self._data[table] += message['data']
                    # Keys are communicated on partials to let you know how to uniquely identify
                    # an item. We use it for updates.
                    self._keys[table] = message.get('keys')
            elif action == 'insert':
                logger.debug('{}: inserting {}'.format(table, message['data']))
                if message['table'] == 'quote':
                    for data in message['data']:
                        self.quote_data[data['symbol']] = data
                elif message['table'] == 'orderBookL2_25':
                    for data in message['data']:
                        side_book = getattr(self.order_book[data['symbol']], data['side'])
                        side_book[data['id']] = data
                elif message['table'] == 'position':
                    for data in message['data']:
                        assert data['currency'] == CURRENCY
                        self.positions[data['symbol']] = data
                elif message['table'] == 'margin':
                    raise NotImplementedError
                else:
                    self._data[table] += message['data']
                    # Limit the max length of the table to avoid excessive memory usage.
                    # Don't trim orders because we'll lose valuable state if we do.
                    if table not in ['order', 'orderBookL2'] and len(
                            self._data[table]) > BitmexWebsocket.MAX_TABLE_LEN:
                        self._data[table] = self._data[table][(BitmexWebsocket.MAX_TABLE_LEN // 2):]

            elif action == 'update':
                logger.debug(_('{}: updating {}').format(table, message['data']))
                # Locate the item in the collection and update it.
                if message['table'] == "orderBookL2_25":
                    for data in message['data']:
                        side_book = getattr(self.order_book[data['symbol']], data['side'])
                        bar = side_book[data['id']]
                        bar.update(data)
                elif message['table'] == 'position':
                    for data in message['data']:
                        assert data['currency'] == CURRENCY
                        self.positions[data['symbol']].update(data)
                elif message['table'] == 'margin':
                    for data in message['data']:
                        assert data['currency'] == CURRENCY
                        self.margin.update(data)
                else:
                    for updateData in message['data']:
                        item = findItemByKeys(self._keys[table], self._data[table], updateData)
                        if not item:
                            continue  # No item found to update. Could happen before push

                        # Log executions
                        if table == 'order':
                            is_canceled = 'ordStatus' in updateData and updateData['ordStatus'] == 'Canceled'
                            if 'cumQty' in updateData and not is_canceled:
                                contExecuted = updateData['cumQty'] - item['cumQty']
                                if contExecuted > 0:
                                    logger.info("Execution: {} {} Contracts of at {}".format(
                                        item['side'], contExecuted, item['symbol'], item['price']))

                        # Update this item.
                        item.update(updateData)

                        # Remove canceled / filled orders
                        if table == 'order' and item['leavesQty'] <= 0:
                            self._data[table].remove(item)

            elif action == 'delete':
                logger.debug(_('{}: deleting {}').format(table, message['data']))
                # Locate the item in the collection and remove it.

                if message['table'] == "orderBookL2_25":
                    for data in message['data']:
                        side_book = getattr(self.order_book[data['symbol']], data['side'])
                        side_book.pop(data['id'])
                else:
                    for deleteData in message['data']:
                        item = findItemByKeys(self._keys[table], self._data[table], deleteData)
                        self._data[table].remove(item)
            else:
                raise ImpossibleError(_("Unknown action: {}").format(action))
        logger.debug(_("Tick data process time: {}").format(round(time.time() - start, 7)))
