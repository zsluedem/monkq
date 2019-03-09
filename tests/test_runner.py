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
from MonkTrader.base_strategy import BaseStrategy
from MonkTrader.config import Setting
from MonkTrader.const import RUN_TYPE
from MonkTrader.runner import Runner
from MonkTrader.utils.timefunc import utc_datetime

from .utils import over_written_settings


class TestStrategy(BaseStrategy):
    async def handle_bar(self) -> None:
        pass


def test_runner(settings: Setting, tem_data_dir: str) -> None:
    custom_settings = {
        "STRATEGY": TestStrategy,
        "START_TIME": utc_datetime(2018, 1, 1),
        "END_TIME": utc_datetime(2018, 2, 1),
        "RUN_TYPE": RUN_TYPE.BACKTEST,
        "FREQUENCY": "1m",
        "DATA_DIR": tem_data_dir,
        "EXCHANGE": {
            "bitmex": {
                'engine': 'MonkTrader.exchange.bitmex',
                "IS_TEST": True,
                "API_KEY": '',
                "API_SECRET": '',
                "START_WALLET_BALANCE": 100000
            }
        }

    }
    with over_written_settings(settings, **custom_settings):
        runner = Runner(settings)

        runner.run()
