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
from importlib import import_module
from typing import TYPE_CHECKING, Dict, Type, TypeVar

from MonkTrader.base_strategy import BaseStrategy
from MonkTrader.config import Setting
from MonkTrader.const import RUN_TYPE
from MonkTrader.exception import SettingError

if TYPE_CHECKING:
    from MonkTrader.exchange.base import BaseExchange  # noqa: F401 pragma: no cover

T_EXCHANGE = TypeVar("T_EXCHANGE", bound="BaseExchange")


class Context:
    def __init__(self, settings: Setting) -> None:
        self.settings = settings
        self._exchanges: Dict = {}
        self.now: datetime.datetime = settings.START_TIME  # type:ignore

    def _import_cls_from_str(self, entry: str) -> Type[BaseStrategy]:
        mod_path, _, cls_name = entry.rpartition('.')

        mod = import_module(mod_path)

        cls: Type[BaseStrategy] = getattr(mod, cls_name)
        return cls

    def load_exchanges(self) -> None:
        for name, exchange_setting in self.settings.EXCHANGES.items():  # type:ignore
            self._exchanges[name] = self._load_exchange(name, exchange_setting)

    def _load_exchange(self, name: str, exchange_setting: Dict) -> T_EXCHANGE:
        mod = import_module(exchange_setting.get('engine'))  # type: ignore
        exchange_cls: Type[T_EXCHANGE]

        if self.settings.RUN_TYPE == RUN_TYPE.REALTIME:  # type: ignore
            exchange_cls = getattr(mod, 'default_exchange')
        elif self.settings.RUN_TYPE == RUN_TYPE.BACKTEST:  # type: ignore
            exchange_cls = getattr(mod, 'default_sim_exchange')
        else:
            raise SettingError()

        return exchange_cls(self, name, exchange_setting)

    def load_strategy(self) -> None:
        if isinstance(self.settings.STRATEGY, BaseStrategy):  # type: ignore
            strategy_cls = getattr(self.settings, "STRATEGY")
            self.strategy = strategy_cls(self)  # type: ignore
        elif isinstance(self.settings.STRATEGY, str):  # type: ignore
            strategy_cls = self._import_cls_from_str(self.settings.STRATEGY)  # type: ignore
            self.strategy = strategy_cls(self)  # type: ignore
