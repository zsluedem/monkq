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

import pytest
from MonkTrader.base_strategy import BaseStrategy
from MonkTrader.config import Setting
from MonkTrader.const import RUN_TYPE
from MonkTrader.context import Context
from MonkTrader.exception import SettingException
from tests.utils import add_path, over_written_settings


class Strategy(BaseStrategy):
    pass

def test_context_load_exchanges_realtime(settings: Setting) -> None:
    exchange_settings = {
        'test': {
            'engine': 'exchange_mod',
            'test': True
        }
    }
    with add_path(os.path.dirname(__file__)):
        with over_written_settings(settings, EXCHANGES=exchange_settings,
                                   RUN_TYPE=RUN_TYPE.REALTIME) as custom_settings:
            context = Context(custom_settings)
            context.load_exchanges()


def test_context_load_exchanges_backtest(settings: Setting) -> None:
    exchange_settings = {
        'test': {
            'engine': 'exchange_mod',
            'test': True
        }
    }
    with add_path(os.path.dirname(__file__)):
        with over_written_settings(settings, EXCHANGES=exchange_settings,
                                   RUN_TYPE=RUN_TYPE.BACKTEST) as custom_settings:
            context = Context(custom_settings)
            context.load_exchanges()


def test_context_load_exchanges_exception(settings: Setting) -> None:
    exchange_settings = {
        'test': {
            'engine': 'exchange_mod',
            'test': True
        }
    }
    with add_path(os.path.dirname(__file__)):
        with over_written_settings(settings, EXCHANGES=exchange_settings,
                                   RUN_TYPE="NO") as custom_settings:
            context = Context(custom_settings)
            with pytest.raises(SettingException):
                context.load_exchanges()

def test_context_load_strategy(settings: Setting) -> None:
    with add_path(os.path.dirname(__file__)):
        with over_written_settings(settings, STRATEGY="MonkTrader.base_strategy.BaseStrategy") as custom_settings:
            context = Context(custom_settings)
            context.load_strategy()

    with over_written_settings(settings, STRATEGY=Strategy) as custom_settings:
        context = Context(custom_settings)
        context.load_strategy()
