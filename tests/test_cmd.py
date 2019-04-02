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
import os
import tempfile
from unittest.mock import patch

from monkq.__main__ import cmd_main


def test_download() -> None:
    with patch("monkq.__main__.BitMexDownloader") as downloader:
        with tempfile.TemporaryDirectory() as tem_dir:
            cmd_main.main(['download', '--kind', 'trade', '--dst_dir', tem_dir], standalone_mode=False)

            downloader.assert_called_with('trade', 'hdf', tem_dir)
            obj = downloader('trade', 'hdf', os.path.join(tem_dir, 'csv#trade'))
            obj.do_all.assert_called()


def test_startstrategy() -> None:
    with tempfile.TemporaryDirectory() as tem_dir:
        cmd_main.main(['startstrategy', '-n', 'strategy1', '-d', tem_dir], standalone_mode=False)

        with open(os.path.join(tem_dir, 'strategy1', '__init__.py')) as f:
            assert f.read() == ''

        with open(os.path.join(tem_dir, 'strategy1', 'manage.py')) as f:
            assert f.read() == """from monkq.strategy_cmd import cmd_main
import os

os.environ.setdefault("MONKQ_SETTING_MODULE", 'strategy1_settings')
if __name__ == '__main__':
    cmd_main()
"""

        with open(os.path.join(tem_dir, 'strategy1', 'settings.py')) as f:
            assert f.read() == """import os

from monkq.const import RUN_TYPE
from monkq.utils.timefunc import utc_datetime

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = '1m'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = utc_datetime(2018, 1, 1)
END_TIME = utc_datetime(2018, 6, 1)

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

STRATEGY = "strategy.MyStrategy"

DATA_DIR = os.path.expanduser("~/.monk/data")

EXCHANGES = {  # type: ignore
    'bitmex': {
        'ENGINE': 'monkq.exchange.bitmex',
        "IS_TEST": True,
    }
}

ACCOUNTS = [
    {
        'NAME': 'bitmex_account',
        'EXCHANGE': 'bitmex',
        "START_WALLET_BALANCE": 100000,
        'ACCOUNT_MODEL': 'monkq.assets.account.FutureAccount'
    }
]

TRADE_COUNTER = "monkq.tradecounter.TradeCounter"

STATISTIC = "monkq.stat.Statistic"

REPORT_FILE = 'result.pkl'
"""

        with open(os.path.join(tem_dir, 'strategy1', 'strategy.py')) as f:
            assert f.read() == """from monkq.base_strategy import BaseStrategy


class MyStrategy(BaseStrategy):
    def setup(self):  # type:ignore
        pass

    def on_trade(self, message):  # type:ignore
        pass

    def tick(self, message):  # type:ignore
        pass

    def handle_bar(self):  # type:ignore
        pass
"""
