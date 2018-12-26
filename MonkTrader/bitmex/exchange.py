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
import asyncio
import json
import aiohttp
import time
import datetime

from aiohttp.helpers import sentinel

from yarl import URL
from MonkTrader.config import CONF
import ssl
from MonkTrader.bitmex.websocket import BitmexWebsocket
from MonkTrader.bitmex.auth import gen_header_dict
from MonkTrader.bitmex.order import Order
from MonkTrader.logger import trade_log
from MonkTrader.bitmex.exception import MaxRetryException, RateLimitException
from typing import List

def authentication_required(fn):
    """Annotation for methods that require auth."""

    def wrapped(self, *args, **kwargs):
        if not (CONF.API_KEY):
            msg = "You must be authenticated to use this method"
            raise Exception(msg)
        else:
            return fn(self, *args, **kwargs)

    return wrapped


class BitmexExchange():
    def __init__(self, base_url: str, loop: asyncio.AbstractEventLoop, orderIDPrefix: str, caller):
        self._loop = loop
        self.base_url = base_url
        self.orderIDPrefix = orderIDPrefix

        self._trace_config = aiohttp.TraceConfig()
        # self._trace_config.on_request_end.append(self._end_request)

        # used only for testing
        if CONF.SSL_PATH:
            self._ssl = ssl.create_default_context()
            self._ssl.load_verify_locations(CONF.SSL_PATH)
        else:
            self._ssl = None
        self._connector = aiohttp.TCPConnector(keepalive_timeout=90)
        self.session = aiohttp.ClientSession(trace_configs=[self._trace_config], loop=self._loop, connector=self._connector)
        self.caller = caller
        self.ws = BitmexWebsocket(loop=loop, session=self.session, ssl=self._ssl, caller=self.caller)


    async def setup(self):
        await self.ws.setup()

    async def subscribe(self, topic:str, symbol:str=''):
        await self.ws.subscribe(topic, symbol)

    async def subscribe_multiple(self, topics:list):
        await self.ws.subscribe_multiple(topics)

    async def unsubscribe(self, topic:str, symbol:str=''):
        await self.ws.unsubscribe(topic, symbol)

    def funds(self):
        return self.ws.funds()

    def ticker_data(self, symbol=None):
        """Get ticker data."""
        return self.ws.get_ticker(symbol)

    def instrument(self, symbol):
        """Get an instrument's details."""
        return self.ws.get_instrument(symbol)

    def recent_trades(self):
        """Get recent trades."""
        return self.ws.recent_trades()

    @authentication_required
    def position(self, symbol):
        """Get your open position."""
        return self.ws.positions.get(symbol)

    @authentication_required
    def open_orders(self):
        """Get open orders."""
        return self.ws.open_orders()

    async def recent_klines(self, symbol:str, frequency:str, count:int):
        path = 'trade/bucketed'
        query = {
            "symbol": symbol,
            "binSize": frequency,
            "count": count,
            "reverse": "true"
        }
        return  await self._curl_bitmex(path=path, query=query)

    async def instruments(self, filter=None):
        query = {}
        if filter is not None:
            query['filter'] = json.dumps(filter)
        resp = self._curl_bitmex(path='instrument', query=query, verb='GET')
        return await resp.json()

    @authentication_required
    async def leverage_position(self, symbol, leverage):
        """Set the leverage on an isolated margin position"""
        path = "position/leverage"
        postdict = {
            'symbol': symbol,
            'leverage': leverage
        }
        resp = await self._curl_bitmex(path=path, postdict=postdict, verb="POST")
        return await resp.json()

    @authentication_required
    async def isolate_position(self, symbol:str, is_not:bool):
        path = "position/isolate"
        postdict = {
            'symbol': symbol,
            'enabled': 'true' if is_not else  'false'
        }
        resp = self._curl_bitmex(path=path, postdict=postdict, verb="POST")
        return await resp.json()

    @authentication_required
    async def place_order(self,order:Order):
        """Place an order."""
        return await self._curl_bitmex(path="order", postdict=order.to_postdict(), verb="POST")

    @authentication_required
    async def place_quick_order(self, order:dict, max_retry=5):
        return await self._curl_bitmex(path="order", postdict=order, verb="POST", max_retry=max_retry)

    @authentication_required
    async def amend_bulk_orders(self, orders:List[Order]):
        """Amend multiple orders."""
        # Note rethrow; if this fails, we want to catch it and re-tick
        return await self._curl_bitmex(path='order/bulk', postdict={'orders': [order.to_postdict() for order in orders]}, verb='PUT')

    @authentication_required
    async def create_bulk_orders(self, orders:List[Order]):
        """Create multiple orders."""
        return await self._curl_bitmex(path='order/bulk', postdict={'orders': [order.to_postdict() for order in orders]}, verb='POST')

    @authentication_required
    async def http_open_orders(self, symbol):
        """Get open orders via HTTP. Used on close to ensure we catch them all."""
        path = "order"
        resp = await self._curl_bitmex(
            path=path,
            query={
                'filter': json.dumps({'ordStatus.isTerminated': False, 'symbol': symbol}),
                'count': 500
            },
            verb="GET"
        )
        orders = await resp.json()
        # Only return orders that start with our clOrdID prefix.
        return [o for o in orders if str(o['clOrdID']).startswith(self.orderIDPrefix)]

    @authentication_required
    async def cancel(self, orderID):
        """Cancel an existing order."""
        path = "order"
        postdict = {
            'orderID': orderID,
        }
        resp = await self._curl_bitmex(path=path, postdict=postdict, verb="DELETE")
        return await resp.json()

    @authentication_required
    async def withdraw(self, amount, fee, address):
        path = "user/requestWithdrawal"
        postdict = {
            'amount': amount,
            'fee': fee,
            'currency': 'XBt',
            'address': address
        }
        resp = await self._curl_bitmex(path=path, postdict=postdict, verb="POST")
        return await resp.json()

    @authentication_required
    async def user(self):
        path = 'user'
        resp = await self._curl_bitmex(path, verb="GET")
        return await resp.json()

    @authentication_required
    async def cancel_all_after_http(self, timeout, max_retry=5):
        return await self._curl_bitmex(path='order/cancelAllAfter', postdict={'timeout': timeout*1000}, verb="POST", max_retry=max_retry)

    @authentication_required
    async def close_position(self, symbol, max_retry=5):
        return await self._curl_bitmex(path='order', postdict={'execInst':"Close", "symbol":symbol}, verb="POST", max_retry=max_retry)

    async def _curl_bitmex(self, path, query=None, postdict=None, timeout=sentinel, verb=None, max_retry=5) -> aiohttp.ClientResponse:
        url = self.base_url + path

        url = URL(url)
        # if timeout is None:
        #     timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not verb:
            verb = 'POST' if postdict else 'GET'

        # By default don't retry POST or PUT. Retrying GET/DELETE is okay because they are idempotent.
        # In the future we could allow retrying PUT, so long as 'leavesQty' is not used (not idempotent),
        # or you could change the clOrdID (set {"clOrdID": "new", "origClOrdID": "old"}) so that an amend
        # can't erroneously be applied twice.

        if query:
            url = url.with_query(query)

        if CONF.HTTP_PROXY:
            proxy = CONF.HTTP_PROXY
        else:
            proxy = None

        headers = {}

        async def retry(retry_time):
            trade_log.info(f"Retry on remain times {retry_time}")
            retry_time -= 1
            if retry_time < 0:
                trade_log.error(f"Request with args {path}, {query}, {postdict}, {timeout}, {verb}, {max_retry} failed with retries")
                raise MaxRetryException()
            else:
                return await self._curl_bitmex(path, query, postdict, timeout, verb, retry_time)

        if postdict:
            data = json.dumps(postdict)
            headers.update({'content-type':"application/json"})
        else:
            data = ''

        headers.update(gen_header_dict(verb, str(url), data, 5))

        if timeout is not sentinel:
            timeout = aiohttp.ClientTimeout(total=timeout)

        try:
            resp = await self.session.request(method=verb, url=str(url), proxy=proxy, headers=headers, data=data, ssl=self._ssl, timeout=timeout)

            if resp.status == 401:
                trade_log.error("API Key or Secret incorrect, please check and restart.")
                trade_log.error("Error: " + await resp.text())
                if postdict:
                    trade_log.error(postdict)
                exit(1)
            elif resp.status == 404:
                if verb == 'DELETE':
                    trade_log.error(f"Order not found: {postdict['orderID']}")
                    return resp
                trade_log.error("Unable to contact the BitMEX API (404). " +
                                  f"Request: {url} \n {postdict}" )
                # exit_or_throw()
            elif resp.status == 429:
                trade_log.error("Ratelimited on current request. Sleeping, then trying again. Try fewer " +
                                  "order pairs or contact support@bitmex.com to raise your limits. " +
                                  f"Request: {url} \n {postdict}")

                # Figure out how long we need to wait.
                ratelimit_reset = resp.headers['X-RateLimit-Reset']
                to_sleep = int(ratelimit_reset) - int(time.time())
                reset_str = datetime.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

                trade_log.error(f"Your ratelimit will reset at {reset_str}. Sleeping for {to_sleep} seconds.")
                raise RateLimitException(ratelimit_reset)

            # 503 - BitMEX temporary downtime, likely due to a deploy. Try again
            elif resp.status == 503:
                trade_log.warning("Unable to contact the BitMEX API (503), retrying. " +
                                    f"Request: {url} \n {postdict}")
                trade_log.warning(f"Response header :{resp.headers}")
                return await retry(max_retry)
            elif resp.status == 400:
                content = await resp.json()
                error = content['error']
                message = error['message'].lower() if error else ''

                trade_log.error(f"An error occured, and return {content} \n Request: {url}, {postdict}")
                if 'insufficient available balance' in message:
                    trade_log.error(f'Account out of funds. The message: {error["message"]}' )
        except asyncio.TimeoutError:
            # Timeout, re-run this request
            trade_log.warning(f"Timed out on request: {path} ({postdict}), retrying..." )
            return await retry(max_retry)

        return resp