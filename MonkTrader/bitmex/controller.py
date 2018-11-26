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
import base64
import uuid
import json
import aiohttp

from yarl import URL
from MonkTrader.config import CONF
import ssl
from MonkTrader.bitmex.websocket import BitmexWebsocket
from MonkTrader.bitmex.auth import gen_header_dict
from MonkTrader.interface import Strategy, NoActionStrtegy

def authentication_required(fn):
    """Annotation for methods that require auth."""

    def wrapped(self, *args, **kwargs):
        if not (CONF.API_KEY):
            msg = "You must be authenticated to use this method"
            raise Exception(msg)
        else:
            return fn(self, *args, **kwargs)

    return wrapped


class BitmexController():
    def __init__(self, base_url: str, loop: asyncio.AbstractEventLoop, orderIDPrefix: str, caller:Strategy=NoActionStrtegy()):
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
        self.session = aiohttp.ClientSession(trace_configs=[self._trace_config], loop=self._loop)
        self.caller = caller
        self.ws = BitmexWebsocket(loop, self.session, ssl=self._ssl, caller=caller)


    async def setup(self):
        await self.ws.setup()

    async def subscribe(self, topic:str, symbol:str=''):
        await self.ws.subscribe(topic, symbol)

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

    def instruments(self, filter=None):
        query = {}
        if filter is not None:
            query['filter'] = json.dumps(filter)
        return self._curl_bitmex(path='instrument', query=query, verb='GET')

    def recent_trades(self):
        """Get recent trades."""
        return self.ws.recent_trades()

    def recent_klines(self, symbol:str, frequency:str, count:int):
        path = 'trade/bucketed'
        query = {
            "symbol": symbol,
            "binSize": frequency,
            "count": count,
            "reverse": "true"
        }
        return  self._curl_bitmex(path=path, query=query)

    # TODO test
    @authentication_required
    def funds(self):
        """Get your current balance."""
        return self.ws.funds()

    @authentication_required
    def position(self, symbol):
        """Get your open position."""
        return self.ws.position(symbol)

    @authentication_required
    def leverage_position(self, symbol, leverage, rethrow_errors=False):
        """Set the leverage on an isolated margin position"""
        path = "position/leverage"
        postdict = {
            'symbol': symbol,
            'leverage': leverage
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="POST", rethrow_errors=rethrow_errors)

    @authentication_required
    def isolate_position(self, symbol:str, is_not:bool):
        path = "position/isolate"
        postdict = {
            'symbol': symbol,
            'enabled': 'true' if is_not else  'false'
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="POST")


    @authentication_required
    async def buy(self, symbol, quantity, price):
        """Place a buy order.

        Returns order object. ID: orderID
        """
        return await self.place_order(symbol, quantity, price)

    @authentication_required
    async def sell(self, symbol, quantity, price):
        """Place a sell order.

        Returns order object. ID: orderID
        """
        return await self.place_order(symbol, -quantity, price)

    @authentication_required
    async def place_order(self,symbol,  quantity, price):
        """Place an order."""
        if price < 0:
            raise Exception("Price must be positive.")

        endpoint = "order"
        # Generate a unique clOrdID with our prefix so we can identify it.
        clOrdID = self.orderIDPrefix + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
        postdict = {
            'symbol': symbol,
            'orderQty': quantity,
            'price': price,
            'clOrdID': clOrdID
        }
        return await self._curl_bitmex(path=endpoint, postdict=postdict, verb="POST")

    @authentication_required
    def amend_bulk_orders(self, orders):
        """Amend multiple orders."""
        # Note rethrow; if this fails, we want to catch it and re-tick
        return self._curl_bitmex(path='order/bulk', postdict={'orders': orders}, verb='PUT', rethrow_errors=True)

    @authentication_required
    def create_bulk_orders(self, orders, post_only=False):
        """Create multiple orders."""
        for order in orders:
            order['clOrdID'] = self.orderIDPrefix + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
            if post_only:
                order['execInst'] = 'ParticipateDoNotInitiate'
        return self._curl_bitmex(path='order/bulk', postdict={'orders': orders}, verb='POST')

    @authentication_required
    def open_orders(self):
        """Get open orders."""
        return self.ws.open_orders(self.orderIDPrefix)

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
    def cancel(self, orderID):
        """Cancel an existing order."""
        path = "order"
        postdict = {
            'orderID': orderID,
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="DELETE")

    # TODO 403 in testnet
    @authentication_required
    def withdraw(self, amount, fee, address):
        path = "user/requestWithdrawal"
        postdict = {
            'amount': amount,
            'fee': fee,
            'currency': 'XBt',
            'address': address
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="POST", max_retries=0)

    @authentication_required
    async def user(self):
        path = 'user'
        resp = await self._curl_bitmex(path, verb="GET")
        return json.loads(await resp.text())

    async def _curl_bitmex(self, path, query=None, postdict=None, timeout=None, verb=None, rethrow_errors=False,
                     max_retries=None):
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
        if max_retries is None:
            max_retries = 0 if verb in ['POST', 'PUT'] else 3

        if query:
            url = url.with_query(query)

        if CONF.HTTP_PROXY:
            proxy = CONF.HTTP_PROXY
        else:
            proxy = None

        headers = {}

        if postdict:
            data = json.dumps(postdict)
            headers.update({'content-type':"application/json"})
        else:
            data = ''

        headers.update(gen_header_dict(verb, str(url), data, 5))

        resp = await self.session.request(method=verb, url=str(url), proxy=proxy, headers=headers, data=data, ssl=self._ssl)

        return resp