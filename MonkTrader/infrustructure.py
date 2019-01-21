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

from MonkTrader.config import CONF
from MonkTrader.const import BACKTEST, REALTIME
from MonkTrader.context import Context
from MonkTrader.interface import AbcRunner, AbcStrategy
from MonkTrader.ticker import FrequencyTicker


class BacktestRunner(AbcRunner):
    def __init__(self, strategy: AbcStrategy):
        self.strategy: AbcStrategy = strategy

    def run(self):
        pass

    def setup(self):
        pass


class RealtimeRunner(AbcRunner):
    def __init__(self, strategy: AbcStrategy):
        self.strategy: AbcStrategy = strategy

    def run(self):
        pass

    def setup(self):
        pass


class Framework():
    def __init__(self):

        if CONF.RUN_TYPE == BACKTEST:
            self.runner = BacktestRunner()
        elif CONF.RUN_TYPE == REALTIME:
            self.runner = RealtimeRunner()

        self.tick_type = CONF.TICK_TYPE

        self.strategy: AbcStrategy = None

    def load_strategy(self):
        pass

    def run_loop(self):
        pass
