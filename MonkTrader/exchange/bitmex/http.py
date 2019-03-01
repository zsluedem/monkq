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
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from aiohttp import (  # type:ignore
    ClientResponse, ClientSession, ClientTimeout, TCPConnector,
)
from aiohttp.helpers import sentinel
from logbook import Logger
from MonkTrader.config import settings
from MonkTrader.exception import (
    AuthError, HttpAuthError, HttpError, MarginNotEnoughError, MaxRetryError,
    NotFoundError, RateLimitError,
)
from MonkTrader.exchange.bitmex.auth import gen_header_dict
from MonkTrader.exchange.bitmex.const import (
    BITMEX_API_URL, BITMEX_TESTNET_API_URL,
)
from MonkTrader.utils.i18n import _
from yarl import URL

from .log import logger_group

logger = Logger('exchange.bitmex.exchange.http')
logger_group.add_logger(logger)

FuncType = Callable[..., Any]
F = TypeVar('F', bound=FuncType)


def authentication_required(fn: F) -> F:
    """Annotation for methods that require auth."""

    def wrapped(self: Any, *args: Any, **kwargs: Any) -> F:
        if not (self.api_key):
            raise AuthError(_("You must be authenticated to use this method"))
        else:
            return fn(self, *args, **kwargs)

    return cast(F, wrapped)


class BitMexHTTPInterface():

    def __init__(self, exchange_setting: dict,
                 connector: TCPConnector, session: ClientSession, ssl: ssl.SSLContext,
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

        if loop:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()
        if exchange_setting['IS_TEST']:
            base_url = BITMEX_TESTNET_API_URL
        else:
            base_url = BITMEX_API_URL
        self.base_url = base_url

        self._ssl = ssl

        self.api_key = exchange_setting.get("API_KEY", '')
        self.api_secret = exchange_setting.get("API_SECRET", '')

        self._connector = connector  # type:ignore
        self.session = session

    async def get_instrument_info(self, symbol: str,
                                  timeout: int = sentinel, max_retry: int = 0) -> List[dict]:
        query = {
            "symbol": symbol,
        }
        resp = await self._curl_bitmex(path='instrument', query=query,
                                       timeout=timeout, max_retry=max_retry)
        content = await resp.json()
        return content

    async def place_limit_order(self, symbol: str,
                                price: float, quantity: float, timeout: int = sentinel,
                                max_retry: int = 0) -> str:
        postdict = {
            "symbol": symbol,
            "price": price,
            "orderQty": quantity
        }
        resp = await self._curl_bitmex(path="order", postdict=postdict, method="POST",
                                       timeout=timeout, max_retry=max_retry)
        order_info = await resp.json()
        return order_info['orderID']

    async def place_market_order(self, symbol: str,
                                 quantity: float, timeout: int = sentinel,
                                 max_retry: int = 0) -> str:
        postdict = {
            "symbol": symbol,
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
                          max_retry: int = 0) -> ClientResponse:
        postdict: Dict[str, Union[str, float]] = {
            "orderID": order_id,
        }
        if quantity:
            postdict.update({"orderQty": quantity})
        if price:
            postdict.update({'price': price})
        return await self._curl_bitmex(path="order", postdict=postdict,
                                       method="PUT", timeout=timeout,
                                       max_retry=max_retry)

    @authentication_required
    async def cancel_order(self, order_id: str, timeout: int = sentinel,
                           max_retry: int = 0) -> ClientResponse:
        path = "order"
        postdict = {
            'orderID': order_id,
        }
        return await self._curl_bitmex(path=path, postdict=postdict,
                                       method="DELETE", timeout=timeout,
                                       max_retry=max_retry)

    @authentication_required
    async def open_orders_http(self, timeout: int = sentinel, max_retry: int = 0) -> str:
        query = {"filter": '{"open": true}', "count": 500}
        resp = await self._curl_bitmex(path='order', query=query,
                                       method="GET", timeout=timeout,
                                       max_retry=max_retry)
        return await resp.json()

    async def active_instruments(self, timeout: int = sentinel) -> ClientResponse:
        return await self._curl_bitmex(path='instrument/active', method='GET',
                                       max_retry=0, timeout=timeout)

    async def get_kline(self, symbol: str, freq: str,
                        count: int = 100, including_now: bool = False,
                        timeout: int = sentinel, max_retry: int = 5) -> ClientResponse:
        query = {
            "symbol": symbol,
            "partial": "true" if including_now else "false",
            "binSize": freq,
            "reverse": "true",
            "count": count
        }
        return await self._curl_bitmex(path='trade/bucketed', query=query,
                                       timeout=timeout, max_retry=max_retry)

    async def get_recent_trades(self, symbol: str,
                                count: int = 100, timeout: int = sentinel,
                                max_retry: int = 5) -> ClientResponse:
        query = {
            "symbol": symbol,
            "count": count,
            "reverse": "true"
        }
        return await self._curl_bitmex(path="trade", query=query,
                                       method="GET", timeout=timeout,
                                       max_retry=max_retry)

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
