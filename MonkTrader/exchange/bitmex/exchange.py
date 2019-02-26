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
import datetime
import json
import ssl
import time
from typing import (
    Any, Callable, Dict, List, Optional, TypeVar, Union, ValuesView, cast,
)

from aiohttp import (  # type:ignore
    ClientResponse, ClientSession, ClientTimeout, TCPConnector, TraceConfig,
)
from aiohttp.helpers import sentinel
from logbook import Logger
from MonkTrader.assets.instrument import FutureInstrument, Instrument
from MonkTrader.config import settings
from MonkTrader.context import Context
from MonkTrader.exception import (
    AuthError, HttpAuthError, HttpError, MarginNotEnoughError, MaxRetryError,
    NotFoundError, RateLimitError,
)
from MonkTrader.exchange.base import BaseExchange
from MonkTrader.exchange.base.info import ExchangeInfo
from MonkTrader.exchange.bitmex.auth import gen_header_dict
from MonkTrader.exchange.bitmex.const import (
    BITMEX_API_URL, BITMEX_TESTNET_API_URL, BITMEX_TESTNET_WEBSOCKET_URL,
    BITMEX_WEBSOCKET_URL,
)
from MonkTrader.exchange.bitmex.websocket import BitmexWebsocket
from MonkTrader.utils.i18n import _
from yarl import URL

from .log import logger_group

logger = Logger('exchange.bitmex.exchange')
logger_group.add_logger(logger)
T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)

bitmex_info = ExchangeInfo(name="bitmex",
                           location="unknown",
                           info="famous exchange")


def authentication_required(fn: F) -> F:
    """Annotation for methods that require auth."""

    def wrapped(self: "BitmexExchange", *args: Any, **kwargs: Any) -> F:
        if not (self.api_key):
            raise AuthError(_("You must be authenticated to use this method"))
        else:
            return fn(self, *args, **kwargs)

    return cast(F, wrapped)


class BitmexSimulateExchange(BaseExchange):
    def __init__(self, context: Context, name: str, exchange_setting: dict) -> None:
        super(BitmexSimulateExchange, self).__init__(context, name, exchange_setting)
        # self.trade_counter = TradeCounter(self)

    async def setup(self) -> None:
        raise NotImplementedError()

    async def get_last_price(self, instrument: "Instrument") -> float:
        raise NotImplementedError()

    def exchange_info(self) -> ExchangeInfo:
        return bitmex_info

    async def place_limit_order(self, target: Union[str, T_INSTRUMENT],
                                price: float, quantity: float) -> str:
        raise NotImplementedError()

    async def place_market_order(self, target: Union[str, T_INSTRUMENT],
                                 quantity: float) -> str:
        raise NotImplementedError()

    async def amend_order(self, order_id: str, quantity: Optional[float], price: Optional[float]) -> bool:
        raise NotImplementedError()

    async def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError()

    async def open_orders(self) -> str:
        raise NotImplementedError()

    # def get_order(self, order_id: str):
    #     raise NotImplementedError()
    #
    # def get_account(self):
    #     raise NotImplementedError()

    async def available_instruments(self) -> ValuesView["Instrument"]:
        raise NotImplementedError()

    async def get_kline(self, target: "Instrument", freq: str,
                        count: int = 100, including_now: bool = False) -> List:
        raise NotImplementedError()

    async def get_recent_trades(self, instrument: "Instrument") -> List[dict]:
        raise NotImplementedError()


class BitmexExchange(BaseExchange):
    INSTRUMENT_KEY_MAP = {
        'symbol': 'symbol',
        'listing': 'listing_date',
        'expiry': 'expiry_date',
        'underlying': 'underlying',
        "quoteCurrency": 'quote_currency',
        'lotSize': 'lot_size',
        'tickSize': 'tick_size',
        'makerFee': 'maker_fee',
        'takerFee': 'taker_fee',

        'initMargin': 'init_margin_rate',
        'maintMargin': 'maint_margin_rate',

        'settlementFee': 'settlement_fee',
        'settlCurrency': 'settle_currency',

        'settle': 'settle_date',
        'front': 'front_date',
        'referenceSymbol': 'reference_symbol',
        'deleverage': 'deleverage',

        'rootSymbol': 'root_symbol'
    }

    def __init__(self, context: Context, name: str, exchange_setting: dict,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        :param exchange_setting:
        example:
        {
            'engine': 'MonkTrader.exchange.bitmex',
            "IS_TEST": True,
            "API_KEY": '',
            "API_SECRET": ''
        }
        """
        super(BitmexExchange, self).__init__(context=context, name=name,
                                             exchange_setting=exchange_setting)
        if loop:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()
        if self.exchange_setting['IS_TEST']:
            base_url = BITMEX_TESTNET_API_URL
            ws_url = BITMEX_TESTNET_WEBSOCKET_URL
        else:
            base_url = BITMEX_API_URL
            ws_url = BITMEX_WEBSOCKET_URL
        self.base_url = base_url

        self._trace_config = TraceConfig()
        # self._trace_config.on_request_end.append(self._end_request)

        # used only for testing
        self._ssl = ssl.create_default_context()
        if settings.SSL_PATH:
            self._ssl.load_verify_locations(settings.SSL_PATH)

        self.api_key = exchange_setting.get("API_KEY", '')
        self.api_secret = exchange_setting.get("API_SECRET", '')

        self._available_instrument_cache: Dict[str, Instrument] = {}

        self._connector = TCPConnector(keepalive_timeout=90)  # type:ignore
        self.session = ClientSession(trace_configs=[self._trace_config],
                                     loop=self._loop,
                                     connector=self._connector)
        self.ws = BitmexWebsocket(strategy=context.strategy, loop=self._loop,
                                  session=self.session, ws_url=ws_url,
                                  api_key=self.api_key, api_secret=self.api_secret,
                                  ssl=self._ssl, http_proxy=None)

    # async def get_quote(self, target: Union[str, T_INSTRUMENT],
    #                     timeout: int = sentinel, max_retry: int = 0):
    #     if isinstance(target, Instrument):
    #         target = Instrument.symbol
    #     query = {
    #         "symbol": target,
    #         "depth": "1"
    #     }
    #     resp = await self._curl_bitmex(path='orderBook/L2', query=query,
    #                                    timeout=timeout, max_retry=max_retry)
    #     return await resp.json()

    async def get_last_price(self, instrument: Instrument,
                             timeout: int = sentinel, max_retry: int = 0) -> float:
        query = {
            "symbol": instrument.symbol,
        }
        resp = await self._curl_bitmex(path='instrument', query=query,
                                       timeout=timeout, max_retry=max_retry)
        content = await resp.json()
        try:
            one = content[0]
            last_price = one['lastPrice']
            return last_price
        except IndexError:
            return 0

    def exchange_info(self) -> ExchangeInfo:
        return bitmex_info

    async def place_limit_order(self, target: Union[str, Instrument],
                                price: float, quantity: float, timeout: int = sentinel,
                                max_retry: int = 0) -> str:
        if isinstance(target, Instrument):
            target = Instrument.symbol
        postdict = {
            "symbol": target,
            "price": price,
            "orderQty": quantity
        }
        resp = await self._curl_bitmex(path="order", postdict=postdict, method="POST",
                                       timeout=timeout, max_retry=max_retry)
        order_info = await resp.json()
        return order_info['orderID']

    async def place_market_order(self, target: Union[str, Instrument],
                                 quantity: float, timeout: int = sentinel,
                                 max_retry: int = 0) -> str:
        if isinstance(target, Instrument):
            target = Instrument.symbol
        postdict = {
            "symbol": target,
            "orderQty": quantity,
            "ordType": "Market"
        }
        resp = await self._curl_bitmex(path="order", postdict=postdict,
                                       method="POST", timeout=timeout,
                                       max_retry=max_retry)
        order_info = await resp.json()
        return order_info['orderID']

    async def amend_order(self, order_id: str, quantity: Optional[float] = None,
                          price: Optional[float] = None, timeout: int = sentinel,
                          max_retry: int = 0) -> bool:
        postdict: Dict[str, Union[str, float]] = {
            "orderID": order_id,
        }
        if quantity:
            postdict.update({"orderQty": quantity})
        if price:
            postdict.update({'price': price})
        resp = await self._curl_bitmex(path="order", postdict=postdict,
                                       method="PUT", timeout=timeout,
                                       max_retry=max_retry)
        if 300 > resp.status >= 200:
            return True
        else:
            return False

    @authentication_required
    async def cancel_order(self, order_id: str, timeout: int = sentinel,
                           max_retry: int = 0) -> bool:
        path = "order"
        postdict = {
            'orderID': order_id,
        }
        resp = await self._curl_bitmex(path=path, postdict=postdict,
                                       method="DELETE", timeout=timeout,
                                       max_retry=max_retry)
        if 300 > resp.status >= 200:
            return True
        else:
            return False

    @authentication_required
    async def open_orders_http(self, timeout: int = sentinel, max_retry: int = 0) -> str:
        query = {"filter": '{"open": true}', "count": 500}
        resp = await self._curl_bitmex(path='order', query=query,
                                       method="GET", timeout=timeout,
                                       max_retry=max_retry)
        return await resp.json()

    open_orders = open_orders_http

    async def available_instruments(self, timeout: int = sentinel) -> ValuesView[Instrument]:
        if self._available_instrument_cache:
            return self._available_instrument_cache.values()
        resp = await self._curl_bitmex(path='instrument/active', method='GET',
                                       max_retry=0, timeout=timeout)
        contents = await resp.json()
        for one in contents:
            instrument = FutureInstrument.create(self.INSTRUMENT_KEY_MAP, one, self)
            self._available_instrument_cache[instrument.symbol] = instrument
        return self._available_instrument_cache.values()

    async def setup(self) -> None:
        await self.ws.setup()

    async def get_kline(self, instrument: Instrument, freq: str,
                        count: int = 100, including_now: bool = False,
                        timeout: int = sentinel, max_retry: int = 5) -> List:
        query = {
            "symbol": instrument.symbol,
            "partial": "true" if including_now else "false",
            "binSize": freq,
            "reverse": "true",
            "count": count
        }
        resp = await self._curl_bitmex(path='trade/bucketed', query=query,
                                       timeout=timeout, max_retry=max_retry)
        return await resp.json()

    async def get_recent_trades(self, instrument: Instrument,
                                count: int = 100, timeout: int = sentinel,
                                max_retry: int = 5) -> List[dict]:
        query = {
            "symbol": instrument.symbol,
            "count": count,
            "reverse": "true"
        }
        resp = await self._curl_bitmex(path="trade", query=query,
                                       method="GET", timeout=timeout,
                                       max_retry=max_retry)
        return await resp.json()

    # @authentication_required
    # async def cancel(self, orderID):
    #     """Cancel an existing order."""
    #     path = "order"
    #     postdict = {
    #         'orderID': orderID,
    #     }
    #     resp = await self._curl_bitmex(path=path,
    #                                    postdict=postdict, verb="DELETE")
    #     return await resp.json()
    #
    # def funds(self):
    #     return self.ws.funds()
    #
    # @property
    # def order_book(self):
    #     return
    #
    # @authentication_required
    # async def withdraw(self, amount, fee, address):
    #     path = "user/requestWithdrawal"
    #     postdict = {
    #         'amount': amount,
    #         'fee': fee,
    #         'currency': 'XBt',
    #         'address': address
    #     }
    #     resp = await self._curl_bitmex(path=path, postdict=postdict, verb="POST")
    #     return await resp.json()
    #
    # def deposit(self):
    #     pass
    #
    # async def subscribe(self, topic: str, symbol: str = ''):
    #     await self.ws.subscribe(topic, symbol)
    #
    # async def subscribe_multiple(self, topics: list):
    #     await self.ws.subscribe_multiple(topics)
    #
    # async def unsubscribe(self, topic: str, symbol: str = ''):
    #     await self.ws.unsubscribe(topic, symbol)
    #
    # def ticker_data(self, symbol=None):
    #     """Get ticker data."""
    #     return self.ws.get_ticker(symbol)
    #
    # def instrument(self, symbol):
    #     """Get an instrument's details."""
    #     return self.ws.get_instrument(symbol)
    #
    # def recent_trades(self):
    #     """Get recent trades."""
    #     return self.ws.recent_trades()
    #
    # async def recent_klines(self, symbol: str, frequency: str, count: int):
    #     path = 'trade/bucketed'
    #     query = {
    #         "symbol": symbol,
    #         "binSize": frequency,
    #         "count": count,
    #         "reverse": "true"
    #     }
    #     return await self._curl_bitmex(path=path, query=query)
    #
    # async def instruments(self, filter=None):
    #     query = {}
    #     if filter is not None:
    #         query['filter'] = json.dumps(filter)
    #     resp = await self._curl_bitmex(path='instrument', query=query, verb='GET')
    #     return await resp.json()
    #
    # @authentication_required
    # async def leverage_position(self, symbol, leverage):
    #     """Set the leverage on an isolated margin position"""
    #     path = "position/leverage"
    #     postdict = {
    #         'symbol': symbol,
    #         'leverage': leverage
    #     }
    #     resp = await self._curl_bitmex(path=path, postdict=postdict, verb="POST")
    #     return await resp.json()
    #
    # @authentication_required
    # async def isolate_position(self, symbol: str, is_not: bool):
    #     path = "position/isolate"
    #     postdict = {
    #         'symbol': symbol,
    #         'enabled': 'true' if is_not else 'false'
    #     }
    #     resp = self._curl_bitmex(path=path, postdict=postdict, verb="POST")
    #     return await resp.json()
    #
    # @authentication_required
    # async def place_quick_order(self, order: dict, max_retry=5):
    #     return await self._curl_bitmex(path="order", postdict=order, verb="POST", max_retry=max_retry)
    #
    # @authentication_required
    # async def amend_bulk_orders(self, orders):
    #     """Amend multiple orders."""
    #     # Note rethrow; if this fails, we want to catch it and re-tick
    #     return await self._curl_bitmex(path='order/bulk',
    #                                    postdict={'orders': [order.to_postdict() for order in orders]}, verb='PUT')
    #
    # @authentication_required
    # async def create_bulk_orders(self, orders):
    #     """Create multiple orders."""
    #     return await self._curl_bitmex(path='order/bulk',
    #                                    postdict={'orders': [order.to_postdict() for order in orders]}, verb='POST')
    #
    # @authentication_required
    # async def http_open_orders(self, symbol):
    #     """Get open orders via HTTP. Used on close to ensure we catch them all."""
    #     path = "order"
    #     resp = await self._curl_bitmex(
    #         path=path,
    #         query={
    #             'filter': json.dumps({'ordStatus.isTerminated': False, 'symbol': symbol}),
    #             'count': 500
    #         },
    #         verb="GET"
    #     )
    #     orders = await resp.json()
    #     # Only return orders that start with our clOrdID prefix.
    #     return [o for o in orders if str(o['clOrdID']).startswith(self.orderIDPrefix)]
    #
    # @authentication_required
    # async def user(self):
    #     path = 'user'
    #     resp = await self._curl_bitmex(path, verb="GET")
    #     return await resp.json()
    #
    # @authentication_required
    # async def cancel_all_after_http(self, timeout, max_retry=5):
    #     return await self._curl_bitmex(path='order/cancelAllAfter',
    #                                    postdict={'timeout': timeout * 1000},
    #                                    verb="POST",
    #                                    max_retry=max_retry)
    #
    # @authentication_required
    # async def close_position(self, symbol, max_retry=5):
    #     return await self._curl_bitmex(path='order',
    #                                    postdict={'execInst': "Close", "symbol": symbol},
    #                                    verb="POST",
    #                                    max_retry=max_retry)

    async def _curl_bitmex(self, path: str, query: Optional[dict] = None, postdict: Optional[dict] = None,
                           timeout: int = sentinel, method: str = None,
                           max_retry: int = 5) -> ClientResponse:  # type:ignore
        url = self.base_url + path

        url_obj = URL(url)
        # if timeout is None:
        #     timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not method:
            method = 'POST' if postdict else 'GET'

        # By default don't retry POST or PUT. Retrying GET/DELETE is
        # okay because they are idempotent.
        # In the future we could allow retrying PUT,
        # so long as 'leavesQty' is not used (not idempotent),
        # or you could change the clOrdID
        # (set {"clOrdID": "new", "origClOrdID": "old"}) so that an amend
        # can't erroneously be applied twice.

        if query:
            url_obj = url_obj.with_query(query)

        if settings.HTTP_PROXY:
            proxy = settings.HTTP_PROXY
        else:
            proxy = None

        headers = {}

        if postdict:
            data = json.dumps(postdict)
            headers.update({'content-type': "application/json"})
        else:
            data = ''

        headers.update(gen_header_dict(self.api_secret, self.api_key, method, str(url_obj), data))

        if timeout is not sentinel:
            timeout = ClientTimeout(total=timeout)

        async def retry(retry_time: int) -> ClientResponse:
            logger.info("Retry on remain times {}".format(retry_time))
            retry_time -= 1
            if retry_time < 0:
                logger.warning(_(
                    "Request with args {}, {}, {}, {}, {}, {} failed "
                    "with retries").format(path, query, postdict, timeout, method, max_retry))
                raise MaxRetryError(url=path, method=method,
                                    body=json.dumps(postdict), headers=headers)
            else:
                return await self._curl_bitmex(path, query, postdict, timeout, method, retry_time)

        try:
            resp = await self.session.request(method=method, url=str(url_obj),
                                              proxy=proxy, headers=headers,
                                              data=data,
                                              ssl=self._ssl, timeout=timeout)
            if 200 <= resp.status < 300:
                return resp
            elif 404 >= resp.status >= 400:
                content = await resp.json()
                error = content['error']
                message = error['message'].lower() if error else ''
                name = error['name'].lower() if error else ''
                logger.warning(_("Bitmex request url:{}, method:{}, postdict:{}, "
                                 "headers:{} error ."
                                 "Return with status code:{}, error {} ,"
                                 "message: {}").format(resp.request_info.url,
                                                       resp.request_info.method,
                                                       postdict,
                                                       resp.request_info.headers,
                                                       resp.status, name,
                                                       message))
                if resp.status == 400:
                    if 'insufficient available balance' in message:
                        logger.warning(_('Account out of funds. The message: {}').format(error["message"]))
                        raise MarginNotEnoughError(message)
                elif resp.status == 401:
                    raise HttpAuthError(self.api_key, self.api_secret)
                elif resp.status == 403:
                    raise HttpError(url=resp.request_info.url, method=resp.request_info.method,
                                    body=json.dumps(postdict), headers=resp.request_info.headers,
                                    message=message)
                elif resp.status == 404:
                    if method == 'DELETE':
                        if postdict:
                            logger.warning(_("Order not found: {}").format(postdict.get('orderID')))
                    raise NotFoundError(url=resp.request_info.url, method=resp.request_info.method,
                                        body=json.dumps(postdict), headers=resp.request_info.headers,
                                        message=message)
                return resp
                # exit_or_throw()
            elif resp.status == 429:
                logger.warning(_("Ratelimited on current request. Sleeping, "
                                 "then trying again. Try fewer order pairs or"
                                 " contact support@bitmex.com to raise your limits. "
                                 "Request: {}  postdict: {}").format(url_obj, postdict))

                # Figure out how long we need to wait.
                ratelimit_reset = resp.headers['X-RateLimit-Reset']
                to_sleep = int(ratelimit_reset) - int(time.time())
                reset_str = datetime.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

                logger.warning(_("Your ratelimit will reset at {}. "
                                 "Sleeping for {} seconds.").format(reset_str, to_sleep))
                raise RateLimitError(url=resp.request_info.url,
                                     method=resp.request_info.method,
                                     body=json.dumps(postdict), headers=resp.request_info.headers,
                                     ratelimit_reset=ratelimit_reset)

            # 503 - BitMEX temporary downtime, likely due to a deploy. Try again
            elif resp.status == 503:
                logger.warning(_("Unable to contact the BitMEX API (503), retrying. "
                                 "Bitmex is mostly overloaded now,"
                                 "Request: {} {} "
                                 "Response header :{}").format(url_obj, postdict, resp.headers))
                return await retry(max_retry)

            else:
                content = await resp.text()
                raise HttpError(url=resp.request_info.url, method=resp.request_info.method,
                                body=json.dumps(postdict), headers=resp.request_info.headers, message=content)

        except asyncio.TimeoutError:
            # Timeout, re-run this request
            logger.warning(_("Timed out on request: path:{}, query:{}, "
                             "postdict:{}, verb:{}, timeout:{}, retry:{}, "
                             "retrying...").format(path, query, postdict,
                                                   method, timeout, max_retry))
            return await retry(max_retry)
