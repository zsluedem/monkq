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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
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
from MonkTrader.utils.version import PY36

import lazy_object_proxy

if PY36:
    from MonkTrader.config import default_settings36 as default_settings
else:
    from MonkTrader.config import default_settings3 as default_settings # type: ignore

# SETTINGS_ENV_VARIABLE = "SETTINGS_ENV_VARIABLE"

SETTING_FILE = 'settings'

class Setting:
    def __init__(self):
        for setting in dir(default_settings):
            if setting.isupper():
                setattr(self, setting, getattr(default_settings, setting))

        # self.SETTING_MODULE = module
        try:
            mod = __import__(SETTING_FILE)
        except ImportError:
            warnings.warn("Can not find settings.py in the current path, we are going to use the default settings.")
            return
        self._explicit_settings = set()

        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def is_overridden(self, setting):
        return setting in self._explicit_settings

def gen_settings():
    # get the current path to import settings
    base = os.getcwd()
    sys.path.insert(0, base)
    settings = Setting()
    sys.path.pop(0)
    return settings


settings = lazy_object_proxy.Proxy(gen_settings)