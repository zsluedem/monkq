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
import datetime
import inspect
from importlib import import_module
from typing import Dict, Type, TypeVar, Union

from monkq.assets.account import BaseAccount
from monkq.base_strategy import BaseStrategy
from monkq.config import Setting
from monkq.const import RUN_TYPE
from monkq.exception import SettingError
from monkq.exchange.base import \
    BaseExchange  # noqa: F401 pragma: no cover
from monkq.exchange.base import \
    BaseSimExchange  # noqa: F401 pragma: no cover
from monkq.stat import Statistic
from monkq.tradecounter import TradeCounter

T_LOAD_ITEM = TypeVar("T_LOAD_ITEM")

EXCHANGE_T = Union[BaseSimExchange, BaseExchange]


class Context:
    def __init__(self, settings: Setting) -> None:
        self.settings = settings
        self.exchanges: Dict[str, EXCHANGE_T] = {}
        self.accounts: Dict[str, BaseAccount] = {}
        self.now: datetime.datetime = settings.START_TIME  # type:ignore

        self.strategy: BaseStrategy
        self.stat: Statistic
        self.trade_counter: TradeCounter

    def setup_context(self) -> None:
        self.load_statistic()
        self.load_trade_counter()
        self.load_strategy()
        self.load_exchanges()
        self.load_accounts()

    def load_statistic(self) -> None:
        statisit_model = self.settings.STATISTIC  # type:ignore
        stat_cls = self.load_target_cls(statisit_model, Statistic)
        self.stat = stat_cls(self)

    def load_trade_counter(self) -> None:
        trade_counter_model = self.settings.TRADE_COUNTER  # type:ignore
        trade_counter_cls = self.load_target_cls(trade_counter_model, TradeCounter)
        self.trade_counter = trade_counter_cls(self.stat)

    def _import_cls_from_str(self, entry: str) -> T_LOAD_ITEM:
        mod_path, _, cls_name = entry.rpartition('.')

        mod = import_module(mod_path)

        cls = getattr(mod, cls_name)
        return cls

    def load_exchanges(self) -> None:
        for name, exchange_setting in self.settings.EXCHANGES.items():  # type:ignore
            self.exchanges[name] = self._load_exchange(name, exchange_setting)

    def _load_exchange(self, name: str, exchange_setting: Dict) -> EXCHANGE_T:
        engine_cls: Union[str, Type[T_LOAD_ITEM]] = exchange_setting.get('ENGINE')  # type: ignore
        exchange_cls: Union[Type[BaseExchange], Type[BaseSimExchange]]

        if self.settings.RUN_TYPE == RUN_TYPE.REALTIME:  # type: ignore
            exchange_cls = self.load_target_cls(engine_cls, BaseExchange)
            assert not issubclass(exchange_cls, BaseSimExchange)
        elif self.settings.RUN_TYPE == RUN_TYPE.BACKTEST:  # type: ignore
            exchange_cls = self.load_target_cls(engine_cls, BaseSimExchange)
        else:
            raise SettingError("monkq only support REALTIME and BACKTEST mode.")

        return exchange_cls(self, name, exchange_setting)

    def load_strategy(self) -> None:
        strategy_model = self.settings.STRATEGY  # type: ignore
        strategy_cls = self.load_target_cls(strategy_model, BaseStrategy)
        self.strategy = strategy_cls(self)

    def load_target_cls(self, target: Union[str, Type[T_LOAD_ITEM]],
                        target_cls: Type[T_LOAD_ITEM]) -> Type[T_LOAD_ITEM]:
        if isinstance(target, str):
            loaded_cls: Type[T_LOAD_ITEM] = self._import_cls_from_str(target)
            assert issubclass(loaded_cls, target_cls)
        elif inspect.isclass(target):
            if issubclass(target, target_cls):
                loaded_cls = target
            else:
                raise SettingError(
                    "Expected target {} is subclass of {}, got {}".format(target, target_cls, type(target)))
        else:
            raise SettingError("Expected target {} is str or type {}, got {}".format(target, target_cls, type(target)))
        return loaded_cls

    def load_accounts(self) -> None:
        for account_setting in self.settings.ACCOUNTS:  # type:ignore
            self.accounts[account_setting['NAME']] = self._load_account(account_setting)

    def _load_account(self, account_setting: Dict) -> BaseAccount:
        account_model: Union[str, Type[BaseAccount]] = account_setting.get('ACCOUNT_MODEL', '')
        account_cls = self.load_target_cls(account_model, BaseAccount)
        return account_cls(exchange=self.exchanges[account_setting['EXCHANGE']],  # type:ignore
                           wallet_balance=account_setting['START_WALLET_BALANCE'],
                           position_cls=account_cls.position_cls)
