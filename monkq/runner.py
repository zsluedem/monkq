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
from asyncio import get_event_loop

from logbook import Logger
from monkq.config import Setting
from monkq.context import Context
from monkq.ticker import FrequencyTicker

from .log import core_log_group

logger = Logger('runner')
core_log_group.add_logger(logger)


class Runner():
    def __init__(self, settings: Setting) -> None:
        self.setting = settings

        self.context = Context(settings)
        self.context.setup_context()

        self.start_datetime = settings.START_TIME  # type: ignore
        self.end_datetime = settings.END_TIME  # type: ignore

        self.ticker = FrequencyTicker(self.start_datetime, self.end_datetime, '1m')

        self.stat = self.context.stat

    async def _run(self) -> None:
        await self.context.strategy.setup()

        self.stat.collect_daily()

        for current_time in self.ticker.timer():
            self.context.now = current_time
            logger.debug("Handler time {}".format(current_time))

            await self.context.strategy.handle_bar()

            for key, exchange in self.context.exchanges.items():
                exchange.match_open_orders()  # type:ignore

            if current_time.hour == 0 and current_time.minute == 0 \
                    and current_time.second == 0 and current_time.microsecond == 0 \
                    and current_time != self.start_datetime and current_time != self.end_datetime:
                logger.info("Finish handle bar to {}".format(current_time))
                self.stat.collect_daily()

        self.stat.collect_daily()

        self.lastly()

    def lastly(self) -> None:
        self.stat.report()

    def run(self) -> None:
        loop = get_event_loop()
        loop.run_until_complete(self._run())
