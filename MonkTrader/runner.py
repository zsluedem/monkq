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

from MonkTrader.context import Context
from MonkTrader.ticker import FrequencyTicker
from MonkTrader.stat import Statistic

class Runner():
    def __init__(self, settings):
        self.setting = settings

        self.context = Context(settings)
        self.context.load_strategy()
        self.context.load_exchanges()

        self.start_datetime = settings.START_TIME
        self.end_datetime = settings.END_TIME

        self.ticker = FrequencyTicker(self.start_datetime, self.end_datetime, '1m')

        # TODO no bitmex hard code
        self.stat = Statistic(self.context.exchanges['bitmex'].get_account(), self.context)

    async def run(self):
        for time in self.ticker.timer():
            self.context.now = time

            await self.context.strategy.handle_bar()

            for key,exchange in self.context.exchanges.items():
                await exchange.apply_trade()


            if time.minute == 0 and time.second == 0 and time.microsecond == 0:
                self.stat.collect_daily()

