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

from MonkTrader.__main__ import cmd_main


def test_download() -> None:
    with patch("MonkTrader.__main__.BitMexDownloader") as downloader:
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
            assert f.read() == """from MonkTrader.__main__ import cmd_main

if __name__ == '__main__':
    cmd_main()
"""

        with open(os.path.join(tem_dir, 'strategy1', 'settings.py')) as f:
            assert f.read() == """import os

from MonkTrader.const import RUN_TYPE

# Mongodb uri which is used to load data or download data in.
DATABASE_URI = "mongodb://127.0.0.1:27017"

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = 'tick'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = '2018-01-01T00:00:00Z'
END_TIME = '2018-06-01T00:00:00Z'

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

STRATEGY = "strategy.MyStrategy"

DATA_DIR = os.path.expanduser("~/.monk/data")

EXCHANGES = {  # type: ignore
    'bitmex': {
        'engine': 'MonkTrader.exchange.bitmex',
        "IS_TEST": True,
        "API_KEY": '',
        "API_SECRET": ''
    }
}
"""

        with open(os.path.join(tem_dir, 'strategy1', 'strategy.py')) as f:
            assert f.read() == """from MonkTrader.base_strategy import BaseStrategy


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
