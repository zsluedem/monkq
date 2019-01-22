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
from typing import Dict
from importlib import import_module
from MonkTrader.const import RUN_TYPE
from MonkTrader.exception import SettingException


class Context:
    def __init__(self, settings):
        self._settings = settings
        self._exchanges: Dict = {}

    def load_exchanges(self):
        for name, exchange_setting in self._settings.EXCHANGES.items():
            self._exchanges[name] = self._load_exchange(name, exchange_setting)

    def _load_exchange(self, name: str,exchange_setting: Dict):
        mod = import_module(exchange_setting.get('engine'))

        if self._settings.RUN_TYPE == RUN_TYPE.REALTIME:
            exchange_cls = getattr(mod, 'default_exchange')
        elif self._settings.RUN_TYPE == RUN_TYPE.BACKTEST:
            exchange_cls = getattr(mod, 'default_sim_exchange')
        else:
            raise SettingException()

        return exchange_cls(name, exchange_setting)

