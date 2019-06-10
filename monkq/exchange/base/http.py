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
from functools import partial
from typing import Callable, Optional

from aiohttp import (  # type:ignore
    ClientResponse, ClientSession, ClientTimeout, TCPConnector,
)
from aiohttp.helpers import sentinel
from logbook import Logger
from monkq.exception import MaxRetryError
from monkq.exchange.base.auth import AuthProtocol
from monkq.utils.i18n import _
from yarl import URL


class HTTPInterfaceBase:
    base_url: str

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
        self.logger = Logger(self.__class__.__name__)
        if loop:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()
        self.exchange_setting = exchange_setting
        self._proxy = proxy
        self._ssl = ssl

        self._connector = connector  # type:ignore
        self.session = session

    async def abnormal_status_checking(self, resp: ClientResponse, retry_callback: Callable) -> None:
        raise NotImplementedError()

    async def curl(self, path: str, query: Optional[dict] = None, postdict: Optional[dict] = None,
                   timeout: int = sentinel, method: Optional[str] = None,
                   max_retry: int = 5, auth_instance: Optional[AuthProtocol] = None) -> ClientResponse:
        url = self.base_url + path

        url_obj = URL(url)
        # if timeout is None:
        #     timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not method:
            method = 'POST' if postdict else 'GET'

        if query:
            url_obj = url_obj.with_query(query)

        headers = {}

        if postdict:
            data = json.dumps(postdict)
            headers.update({'content-type': "application/json"})
        else:
            data = ''

        if auth_instance:
            headers.update(auth_instance.gen_http_headers(method, url_obj, data))

        if timeout is not sentinel:
            cli_timeout = ClientTimeout(total=timeout)
        else:
            cli_timeout = sentinel

        async def retry(retry_time: int) -> ClientResponse:
            self.logger.info("Retry on remain times {}".format(retry_time))
            retry_time -= 1
            if retry_time < 0:
                self.logger.warning(_(
                    "Request with args {}, {}, {}, {}, {}, {} failed "
                    "with retries").format(path, query, postdict, cli_timeout, method,
                                           max_retry))
                raise MaxRetryError(url=path, method=method,
                                    body=json.dumps(postdict), headers=headers)
            else:
                return await self.curl(path, query, postdict, timeout, method, retry_time)

        try:
            resp = await self.session.request(method=method, url=str(url_obj),
                                              proxy=self._proxy, headers=headers,
                                              data=data,
                                              ssl=self._ssl, timeout=cli_timeout)
            if 200 <= resp.status < 300:
                return resp
            else:
                content = await resp.text()

                self.logger.warning(_("Request url:{}, method:{}, postdict:{}, "
                                      "headers:{} abnormal ."
                                      "Return with status code:{}, header {} ,"
                                      "content: {}").format(resp.request_info.url,
                                                            resp.request_info.method,
                                                            postdict,
                                                            resp.request_info.headers,
                                                            resp.status, resp.headers, content))

                await self.abnormal_status_checking(resp, partial(retry, max_retry))
                return resp
        except asyncio.TimeoutError:
            # Timeout, re-run this request
            self.logger.warning(_("Timed out on request: path:{}, query:{}, "
                                  "postdict:{}, verb:{}, timeout:{}, retry:{}, "
                                  "retrying...").format(path, query, postdict,
                                                        method, timeout, max_retry))
            return await retry(max_retry)
