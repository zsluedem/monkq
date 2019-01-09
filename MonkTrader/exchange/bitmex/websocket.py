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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
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
import traceback
import decimal
from decimal import Decimal
import asyncio
import time
import ssl
from functools import wraps
from collections import defaultdict, namedtuple

from aiohttp import ClientSession
from MonkTrader.exchange.bitmex.auth import gen_header_dict
from MonkTrader.logger import trade_log
from MonkTrader.config import CONF
from MonkTrader.interface import AbcStrategy

from typing import Dict, Union

OrderBook = namedtuple('OrderBook', ['Buy', 'Sell'])
CURRENCY = 'XBt'
INTERVAL_FACTOR = 20


def findItemByKeys(keys: list, table: list, matchData: dict):
    for item in table:
        matched = True
        for key in keys:
            if item[key] != matchData[key]:
                matched = False
        if matched:
            return item


def toNearest(num: float, tickSize: float):
    """Given a number, round it to the nearest tick. Very useful for sussing float error
       out of numbers: e.g. toNearest(401.46, 0.01) -> 401.46, whereas processing is
       normally with floats would give you 401.46000000000004.
       Use this after adding/subtracting/multiplying numbers."""
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))


def timestamp_update(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        self._last_comm_time = time.time()
        ret = func(self, *args, **kwargs)
        return ret

    return wrapped


class BitmexWebsocket():
    MAX_TABLE_LEN = 200

    def __init__(self, caller: AbcStrategy, loop: asyncio.AbstractEventLoop, session: ClientSession,
                 ssl: ssl.SSLContext = None):
        self._loop = loop
        self._data = dict()
        self._keys = dict()
        self._ws = None
        self._ssl = ssl
        self.caller = caller
        self.session: ClientSession = session
        self.inited = False
        self._last_comm_time = 0

        self.quote_data = defaultdict(dict)
        self.order_book: Dict[str, OrderBook[Dict, Dict]] = defaultdict(lambda: OrderBook(Buy=dict(), Sell=dict()))
        self.positions: Dict[str, Dict] = defaultdict(dict)
        self.margin: Dict = dict()

    async def setup(self):
        headers = gen_header_dict('GET', "/realtime", '')
        if CONF.HTTP_PROXY:
            proxy = CONF.HTTP_PROXY
        else:
            proxy = None

        self._ws = await self.session.ws_connect(CONF.Bitmex_ws_url, headers=headers, proxy=proxy, ssl=self._ssl)
        self._last_comm_time = time.time()
        self._loop.create_task(self.run())
        self._loop.create_task(self._ping())

    def open_orders(self):
        orders = self._data['order']
        # Filter to only open orders (leavesQty > 0) and those that we actually placed
        return orders
        # return [o for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and o['leavesQty'] > 0]

    async def _ping(self):
        while 1:
            if time.time() - self._last_comm_time > INTERVAL_FACTOR:
                trade_log.debug(
                    'No communication during {} seconds. Send ping signal to keep connection open'.format(
                        INTERVAL_FACTOR))
                await self._ws.ping()
                self._last_comm_time = time.time()
            await asyncio.sleep(INTERVAL_FACTOR)

    async def run(self):
        async for message in self._ws:
            trade_log.debug("Receive message from bitmex:{}".format(message.data))
            decode_message = json.loads(message.data)
            self._on_message(decode_message)

            # call strategy method
            # websocket first package is not a normal package , so we use 'limit' to skip it
            if decode_message.get('action'):
                if decode_message.get('table') == 'execution':
                    start = time.time()
                    await self.caller.on_trade(message=decode_message)
                    trade_log.debug('User on_trade process time: {}'.format(round(time.time() - start, 7)))
                else:
                    start = time.time()
                    await self.caller.tick(message=decode_message)
                    trade_log.debug('User tick process time: {}'.format(round(time.time() - start, 7)))

    @timestamp_update
    async def subscribe(self, topic, symbol=''):
        await self._ws.send_json({'op': 'subscribe', "args": [':'.join((topic, symbol))]})

    @timestamp_update
    async def subscribe_multiple(self, topics: list):
        await self._ws.send_json({'op': 'subscribe', "args": topics})

    @timestamp_update
    async def unsubscribe(self, topic, symbol=''):
        args = ":".join((topic, symbol))
        await self._ws.send_json({'op': 'unsubscribe', "args": [args]})

    def recent_trades(self):
        return self._data['trade']

    def funds(self):
        return self._data['margin']

    def get_position(self, symbol: str = None):
        if symbol is None:
            return self.positions
        return self.positions[symbol]

    def error(self, error):
        pass

    def get_instrument(self, symbol: str = None):
        if symbol is None:
            return self._data['instrument']
        instruments = self._data['instrument']
        matchingInstruments = [i for i in instruments if i['symbol'] == symbol]
        if len(matchingInstruments) == 0:
            raise Exception("Unable to find instrument or index with symbol: " + symbol)
        instrument = matchingInstruments[0]
        # Turn the 'tickSize' into 'tickLog' for use in rounding
        # http://stackoverflow.com/a/6190291/832202
        instrument['tickLog'] = decimal.Decimal(str(instrument['tickSize'])).as_tuple().exponent * -1
        return instrument

    def get_ticker(self, symbol: str):
        '''Return a ticker object. Generated from instrument.'''

        instrument = self.get_instrument(symbol)

        # If this is an index, we have to get the data from the last trade.
        if instrument['symbol'][0] == '.':
            ticker = {}
            ticker['mid'] = ticker['buy'] = ticker['sell'] = ticker['last'] = instrument['markPrice']
        # Normal instrument
        else:
            bid = instrument['bidPrice'] or instrument['lastPrice']
            ask = instrument['askPrice'] or instrument['lastPrice']
            ticker = {
                "last": instrument['lastPrice'],
                "buy": bid,
                "sell": ask,
                "mid": (bid + ask) / 2
            }

        # The instrument has a tickSize. Use it to round values.
        return {k: toNearest(float(v or 0), instrument['tickSize']) for k, v in ticker.items()}

    def get_quote(self, symbol: str):
        return self.quote_data[symbol]

    def get_order_book(self, symbol: str):
        return self.order_book[symbol]

    @timestamp_update
    def _on_message(self, message: Union[dict, list]):
        '''Handler for parsing WS messages.'''
        start = time.time()

        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        try:
            if 'subscribe' in message:
                if message['success']:
                    trade_log.debug("Subscribed to %s." % message['subscribe'])
                else:
                    self.error("Unable to subscribe to %s. Error: \"%s\" Please check and restart." %
                               (message['request']['args'][0], message['error']))
            elif 'unsubscribe' in message:
                if message['success']:
                    trade_log.debug("Unsubscribed to %s." % message['unsubscribe'])
                else:
                    self.error("Unable to unsubscribe to %s. Error: \"%s\" Please check and restart." %
                               (message['request']['args'][0], message['error']))
            elif 'status' in message:
                if message['status'] == 400:
                    self.error(message['error'])
                if message['status'] == 401:
                    self.error("API Key incorrect, please check and restart.")
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
                    trade_log.debug("%s: partial" % table)
                    if message['table'] == "quote":
                        for data in message['data']:
                            self.quote_data[data['symbol']] = data
                    elif message['table'] == 'orderBookL2':
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
                        self._keys[table] = message['keys']
                elif action == 'insert':
                    trade_log.debug('%s: inserting %s' % (table, message['data']))
                    if message['table'] == 'quote':
                        for data in message['data']:
                            self.quote_data[data['symbol']] = data
                    elif message['table'] == 'orderBookL2':
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
                    trade_log.debug('%s: updating %s' % (table, message['data']))
                    # Locate the item in the collection and update it.
                    if message['table'] == "orderBookL2":
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
                                        instrument = self.get_instrument(item['symbol'])
                                        trade_log.info("Execution: %s %d Contracts of %s at %.*f" %
                                                       (item['side'], contExecuted, item['symbol'],
                                                        instrument['tickLog'], item['price']))

                            # Update this item.
                            item.update(updateData)

                            # Remove canceled / filled orders
                            if table == 'order' and item['leavesQty'] <= 0:
                                self._data[table].remove(item)

                elif action == 'delete':
                    trade_log.debug('%s: deleting %s' % (table, message['data']))
                    # Locate the item in the collection and remove it.

                    if message['table'] == "orderBookL2":
                        for data in message['data']:
                            side_book = getattr(self.order_book[data['symbol']], data['side'])
                            side_book.pop(data['id'])
                    else:
                        for deleteData in message['data']:
                            item = findItemByKeys(self._keys[table], self._data[table], deleteData)
                            self._data[table].remove(item)
                else:
                    raise Exception("Unknown action: %s" % action)
            trade_log.debug("Tick data process time: {}".format(round(time.time() - start, 7)))
        except:
            trade_log.error(traceback.format_exc())
