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

from MonkTrader.config import Setting
from MonkTrader.context import Context
from MonkTrader.stat import Statistic
from MonkTrader.ticker import FrequencyTicker


class Runner():
    def __init__(self, settings: Setting) -> None:
        self.setting = settings

        self.context = Context(settings)
        self.context.load_strategy()
        self.context.load_exchanges()

        self.start_datetime = settings.START_TIME  # type: ignore
        self.end_datetime = settings.END_TIME  # type: ignore

        self.ticker = FrequencyTicker(self.start_datetime, self.end_datetime, '1m')

        # TODO no bitmex hard code
        self.stat = Statistic(self.context.exchanges['bitmex'].get_account(), self.context)

    async def _run(self) -> None:
        for time in self.ticker.timer():
            self.context.now = time

            await self.context.strategy.handle_bar()

            for key, exchange in self.context.exchanges.items():
                exchange.match_open_orders()

            if time.hour == 0 and time.minute == 0 and time.second == 0 and time.microsecond == 0:
                self.stat.collect_daily()

        self.lastly()

    def lastly(self) -> None:
        pass

    def run(self) -> None:
        loop = get_event_loop()
        loop.run_until_complete(self._run())
