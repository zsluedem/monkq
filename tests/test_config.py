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
import tempfile

from MonkTrader.config import Setting
from .utils import random_string, change_default_module_settings

setting_content = """
A = 123
B = 321
"""


def test_settings() -> None:
    with tempfile.TemporaryDirectory() as temp:
        name = random_string(6)
        with change_default_module_settings('{}_settings'.format(name)):
            with open(os.path.join(temp, '{}_settings.py'.format(name)), 'w') as f:
                f.write(setting_content)
            sys.path.insert(0, temp)
            setting = Setting()
            sys.path.pop(0)
            assert setting.A == 123  # type: ignore
            assert setting.B == 321  # type: ignore
