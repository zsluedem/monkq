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
import ssl
import time
from typing import Callable, Dict, List, Optional, Union

from aiohttp import ClientResponse, ClientSession, TCPConnector  # type:ignore
from aiohttp.helpers import sentinel
from logbook import Logger
from monkq.exception import (
    HttpAuthError, HttpError, MarginNotEnoughError, NotFoundError,
    RateLimitError,
)
from monkq.exchange.base.http import HTTPInterfaceBase
from monkq.exchange.bitmex.auth import AuthProtocol
from monkq.exchange.bitmex.const import BITMEX_API_URL, BITMEX_TESTNET_API_URL
from monkq.utils.i18n import _

from .log import logger_group

logger = Logger('exchange.bitmex.exchange.http')
logger_group.add_logger(logger)


class BitMexHTTPInterface(HTTPInterfaceBase):

    def __init__(self, exchange_setting: dict,
                 connector: TCPConnector, session: ClientSession, ssl: Optional[ssl.SSLContext] = None,
                 proxy: Optional[str] = None,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        :param exchange_setting:
        example:
        {
            'engine': 'monkq.exchange.bitmex',
            "IS_TEST": True,
            "API_KEY": '',
            "API_SECRET": ''
        }
        """

        super(BitMexHTTPInterface, self).__init__(exchange_setting, connector, session, ssl, proxy, loop)
        if exchange_setting['IS_TEST']:
            base_url = BITMEX_TESTNET_API_URL
        else:
            base_url = BITMEX_API_URL
        self.base_url = base_url

    async def get_instrument_info(self, symbol: str,
                                  timeout: int = sentinel, max_retry: int = 0,
                                  auth_instance: Optional[AuthProtocol] = None) -> List[dict]:
        query = {
            "symbol": symbol,
        }
        resp = await self.curl(path='instrument', query=query,
                               timeout=timeout, max_retry=max_retry, auth_instance=auth_instance)
        content = await resp.json()
        return content

    async def place_limit_order(self, auth_instance: AuthProtocol, symbol: str,
                                price: float, quantity: float, text: str = '', timeout: int = sentinel,
                                max_retry: int = 0) -> str:
        postdict = {
            "symbol": symbol,
            "price": price,
            "orderQty": quantity,
            "text": text
        }
        resp = await self.curl(path="order", postdict=postdict, method="POST",
                               timeout=timeout, max_retry=max_retry, auth_instance=auth_instance)
        order_info = await resp.json()
        return order_info['orderID']

    async def place_market_order(self, auth_instance: AuthProtocol, symbol: str,
                                 quantity: float, text: str = '', timeout: int = sentinel,
                                 max_retry: int = 0) -> str:
        postdict = {
            "symbol": symbol,
            "orderQty": quantity,
            "ordType": "Market",
            "text": text
        }
        resp = await self.curl(path="order", postdict=postdict,
                               method="POST", timeout=timeout,
                               max_retry=max_retry, auth_instance=auth_instance)
        order_info = await resp.json()
        return order_info['orderID']

    async def amend_order(self, auth_instance: AuthProtocol, order_id: str, quantity: Optional[float] = None,
                          price: Optional[float] = None, timeout: int = sentinel,
                          max_retry: int = 0) -> ClientResponse:
        postdict: Dict[str, Union[str, float]] = {
            "orderID": order_id,
        }
        if quantity:
            postdict.update({"orderQty": quantity})
        if price:
            postdict.update({'price': price})
        return await self.curl(path="order", postdict=postdict,
                               method="PUT", timeout=timeout,
                               max_retry=max_retry, auth_instance=auth_instance)

    async def cancel_order(self, auth_instance: AuthProtocol, order_id: str, timeout: int = sentinel,
                           max_retry: int = 0) -> ClientResponse:
        path = "order"
        postdict = {
            'orderID': order_id,
        }
        return await self.curl(path=path, postdict=postdict,
                               method="DELETE", timeout=timeout,
                               max_retry=max_retry, auth_instance=auth_instance)

    async def open_orders_http(self, auth_instance: AuthProtocol,
                               timeout: int = sentinel, max_retry: int = 0) -> List[dict]:
        query = {"filter": '{"open": true}', "count": 500}
        resp = await self.curl(path='order', query=query,
                               method="GET", timeout=timeout,
                               max_retry=max_retry, auth_instance=auth_instance)
        return await resp.json()

    async def active_instruments(self, timeout: int = sentinel,
                                 auth_instance: Optional[AuthProtocol] = None) -> List[dict]:
        resp = await self.curl(path='instrument/active', method='GET',
                               max_retry=0, timeout=timeout, auth_instance=auth_instance)
        return await resp.json()

    async def get_kline(self, symbol: str, freq: str,
                        count: int = 100, including_now: bool = False,
                        timeout: int = sentinel, max_retry: int = 5,
                        auth_instance: Optional[AuthProtocol] = None) -> List[dict]:
        query = {
            "symbol": symbol,
            "partial": "true" if including_now else "false",
            "binSize": freq,
            "reverse": "true",
            "count": count
        }
        resp = await self.curl(path='trade/bucketed', query=query,
                               timeout=timeout, max_retry=max_retry, auth_instance=auth_instance)

        return await resp.json()

    async def get_recent_trades(self, symbol: str,
                                count: int = 100, timeout: int = sentinel,
                                max_retry: int = 5, auth_instance: Optional[AuthProtocol] = None) -> List[dict]:
        query = {
            "symbol": symbol,
            "count": count,
            "reverse": "true"
        }
        resp = await self.curl(path="trade", query=query,
                               method="GET", timeout=timeout,
                               max_retry=max_retry, auth_instance=auth_instance)
        return await resp.json()

    async def abnormal_status_checking(self, resp: ClientResponse, retry_callback: Callable) -> None:
        # FIXME body data unkown and use empty string ''
        if 404 >= resp.status >= 400:
            content = await resp.json()
            error = content['error']
            message = error['message'].lower() if error else ''
            # name = error['name'].lower() if error else ''
            if resp.status == 400:
                if 'insufficient available balance' in message:
                    logger.warning(_('Account out of funds. The message: {}').format(error["message"]))
                    raise MarginNotEnoughError(message)
            elif resp.status == 401:
                raise HttpAuthError('', '')
            elif resp.status == 403:
                raise HttpError(url=resp.request_info.url, method=resp.request_info.method,
                                body='', headers=resp.request_info.headers,
                                message=message)
            elif resp.status == 404:
                raise NotFoundError(url=resp.request_info.url, method=resp.request_info.method,
                                    body='', headers=resp.request_info.headers,
                                    message=message)
            else:
                content = await resp.text()
                raise HttpError(url=resp.request_info.url, method=resp.request_info.method,
                                body='', headers=resp.request_info.headers, message=content)
            # exit_or_throw()
        elif resp.status == 429:
            logger.warning(_("Ratelimited on current request. Sleeping, "
                             "then trying again. Try fewer order pairs or"
                             " contact support@bitmex.com to raise your limits. "
                             "Request: {} ").format(resp.request_info.url))

            # Figure out how long we need to wait.
            ratelimit_reset = resp.headers['X-RateLimit-Reset']
            to_sleep = int(ratelimit_reset) - int(time.time())
            reset_str = datetime.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

            logger.warning(_("Your ratelimit will reset at {}. "
                             "Sleeping for {} seconds.").format(reset_str, to_sleep))
            raise RateLimitError(url=resp.request_info.url,
                                 method=resp.request_info.method,
                                 body='', headers=resp.request_info.headers,
                                 ratelimit_reset=int(ratelimit_reset))

            # 503 - BitMEX temporary downtime, likely due to a deploy. Try again
        elif resp.status == 503:
            logger.warning(_("Unable to contact the BitMEX API (503), retrying. "
                             "Bitmex is mostly overloaded now,"
                             "Request: {}"
                             "Response header :{}").format(resp.request_info.url, resp.headers))
            return await retry_callback()

        else:
            content = await resp.text()
            raise HttpError(url=resp.request_info.url, method=resp.request_info.method,
                            body='', headers=resp.request_info.headers, message=content)
