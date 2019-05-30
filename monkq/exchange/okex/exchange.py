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


@dataclass()
class BackgroundTask:
    ping: asyncio.Task = field(init=False)
    handler: asyncio.Task = field(init=False)


class OKexWebsocket():
    def __init__(self, strategy: BaseStrategy, loop: asyncio.AbstractEventLoop, session: ClientSession, ws_url: str,
                 api_key: str, api_secret: str, ssl: Optional[ssl.SSLContext] = None,
                 http_proxy: Optional[str] = None):

        self._ws: ClientWebSocketResponse
        self._ssl = ssl
        self._ws_url = ws_url
        self._api_key = api_key
        self._api_secret = api_secret
        self._http_proxy = http_proxy
        self.background_task = BackgroundTask()
        self.strategy = strategy
        self.session: ClientSession = session
        self._last_comm_time = 0.  # this is used for a mark point for ping


