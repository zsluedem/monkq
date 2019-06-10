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
import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from aiohttp import ClientWebSocketResponse, WSMsgType  # type: ignore
from logbook import Logger
from monkq.utils.i18n import _

T = TypeVar("T")


@dataclass()
class BackgroundTask:
    ping: asyncio.Task = field(init=False)
    handler: asyncio.Task = field(init=False)


class ExchangeWebsocketBase(Generic[T]):
    ws_conn: ClientWebSocketResponse
    ping_interval: int
    last_comm_time: float
    logger: Logger
    ws_url: str
    loop: asyncio.AbstractEventLoop
    background_task: BackgroundTask
    exchange_name: str

    async def setup(self) -> None:
        self.background_task = BackgroundTask()
        self.ws_conn = await self.connect()
        self.last_comm_time = time.time()
        self.background_task.handler = self.loop.create_task(self.run())
        self.background_task.ping = self.loop.create_task(self.ping_loop())

    async def run(self) -> None:
        try:
            while not self.ws_conn.closed:
                message = await self.ws_conn.receive()
                self.logger.debug(_("Receive message from {}:{}").format(self.exchange_name, message.data))
                if message.type in (WSMsgType.CLOSE, WSMsgType.CLOSING):
                    self.logger.debug(
                        _("{} receiving close message type:{}, message data:{}").format(self.exchange_name,
                                                                                        message.type, message.data))
                    continue
                elif message.type == WSMsgType.CLOSED:
                    self.logger.debug(
                        _("Closing {} websocket connection with data {}").format(self.exchange_name, message.data))
                    break

                decode_message = self.decode_raw_data(message.data)

                on_m = self.on_message(decode_message)
                if asyncio.iscoroutine(on_m):
                    await on_m
                # call strategy method
                # websocket first package is not a normal package , so we use 'limit' to skip it
                # TODO trigger on trade and tick
                # if decode_message.get('action'):
                #     if decode_message.get('table') == 'execution':
                #         start = time.time()
                #         ret = self.strategy.on_trade(message=decode_message)
                #         if asyncio.iscoroutine(ret):
                #             await ret
                #         logger.debug(_('User on_trade process time: {}').format(round(time.time() - start, 7)))
                #     else:
                #         start = time.time()
                #         ret = self.strategy.tick(message=decode_message)
                #         if asyncio.iscoroutine(ret):
                #             await ret
                #         logger.debug(_('User tick process time: {}').format(round(time.time() - start, 7)))
        except asyncio.CancelledError:
            self.logger.warning(_('Your {} handler has been stopped').format(self.exchange_name))

    async def ping_loop(self) -> None:
        try:
            while not self.ws_conn.closed:
                if time.time() - self.last_comm_time > self.ping_interval:
                    self.logger.debug(
                        _('No communication during {} seconds in {}. Send ping signal to keep connection open').format(
                            self.ping_interval, self.exchange_name))
                    await self.ws_conn.ping()
                    self._last_comm_time = time.time()
                await asyncio.sleep(self.ping_interval)
        except asyncio.CancelledError:
            self.logger.warning(_('Your {} ping task has been stopped').format(self.exchange_name))

    async def stop(self) -> None:
        if not self.ws_conn.closed:
            await self.ws_conn.close()
        await self.background_task.handler
        await self.background_task.ping

    async def connect(self) -> ClientWebSocketResponse:
        raise NotImplementedError

    async def subscribe(self, topic: str) -> None:
        raise NotImplementedError()

    async def unsubscribe(self, topic: str) -> None:
        raise NotImplementedError()

    def decode_raw_data(self, data: Any) -> T:
        raise NotImplementedError()

    def on_message(self, message: T) -> Any:
        raise NotImplementedError()
