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
import sys
import warnings
from importlib import import_module
import lazy_object_proxy
from MonkTrader.config import (  # type: ignore
    default_settings as default_settings,
)
from MonkTrader.utils.i18n import _

# SETTINGS_ENV_VARIABLE = "SETTINGS_ENV_VARIABLE"
SETTING_MODULE = "MONKTRADER_SETTING_MODULE"

DEFAULT_SETTING_MODULE = 'settings'


class Setting:
    def __init__(self) -> None:
        for setting in dir(default_settings):
            if setting.isupper():
                setattr(self, setting, getattr(default_settings, setting))

        # self.SETTING_MODULE = module
        setting_module = os.environ.get(SETTING_MODULE, DEFAULT_SETTING_MODULE)
        try:
            mod = import_module(setting_module)
        except ImportError:
            warnings.warn(_("Can not find settings.py in the current path,"
                            " we are going to use the default settings."))
            return

        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                setattr(self, setting, setting_value)


def gen_settings() -> Setting:
    # get the current path to import settings
    base = os.getcwd()
    sys.path.insert(0, base)
    settings = Setting()
    sys.path.pop(0)
    return settings


settings = lazy_object_proxy.Proxy(gen_settings)
