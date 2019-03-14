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

from unittest.mock import MagicMock, patch

import pytest
from MonkTrader.assets.account import FutureAccount
from MonkTrader.base_strategy import BaseStrategy
from MonkTrader.config import Setting
from MonkTrader.context import Context
from MonkTrader.exception import SettingError
from MonkTrader.exchange.bitmex.exchange import BitmexSimulateExchange
from MonkTrader.stat import Statistic
from MonkTrader.tradecounter import TradeCounter


def test_context_load_default() -> None:
    with patch("MonkTrader.exchange.bitmex.exchange.BitmexDataloader"):
        settings = Setting()
        context = Context(settings)

        context.setup_context()

        assert isinstance(context.strategy, BaseStrategy)
        assert isinstance(context.trade_counter, TradeCounter)
        assert isinstance(context.stat, Statistic)
        assert isinstance(context.accounts['bitmex_account'], FutureAccount)
        assert isinstance(context.exchanges['bitmex'], BitmexSimulateExchange)


class TestStrategy(BaseStrategy):
    pass


class TestStatistic(Statistic):
    pass


class TestTradeCounter(TradeCounter):
    pass


class TestExchange(BitmexSimulateExchange):
    pass


class TestAccount(FutureAccount):
    pass


def test_context_custom_setting() -> None:
    with patch("MonkTrader.exchange.bitmex.exchange.BitmexDataloader"):
        settings = Setting()
        settings.STRATEGY = TestStrategy  # type:ignore
        settings.TRADE_COUNTER = TestTradeCounter  # type:ignore
        settings.STATISTIC = TestStatistic  # type:ignore
        settings.ACCOUNTS[0]['ACCOUNT_MODEL'] = TestAccount  # type:ignore
        settings.EXCHANGES['bitmex']['ENGINE'] = TestExchange  # type:ignore

        context = Context(settings)
        context.setup_context()

        assert isinstance(context.strategy, TestStrategy)
        assert isinstance(context.trade_counter, TestTradeCounter)
        assert isinstance(context.stat, TestStatistic)
        assert isinstance(context.accounts, dict)
        assert isinstance(context.exchanges, dict)


def test_context_load_strategy_error() -> None:
    settings = Setting()
    settings.STRATEGY = MagicMock()  # type:ignore

    context = Context(settings)
    with pytest.raises(SettingError):
        context.load_strategy()


def test_context_load_statistic_error() -> None:
    settings = Setting()
    settings.STATISTIC = MagicMock  # type:ignore

    context = Context(settings)
    with pytest.raises(SettingError):
        context.load_statistic()


def test_context_load_trade_counter_error() -> None:
    settings = Setting()
    settings.TRADE_COUNTER = MagicMock()  # type:ignore

    context = Context(settings)
    context.load_statistic()
    with pytest.raises(SettingError):
        context.load_trade_counter()


def test_context_load_accounts_error() -> None:
    pass


def test_context_load_exchanges_error() -> None:
    pass
