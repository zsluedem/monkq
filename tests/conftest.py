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
import shutil
import tempfile
from typing import Generator
from unittest.mock import MagicMock

import pytest
from MonkTrader.config import Setting
from MonkTrader.exchange.base import BaseSimExchange  # noqa
from MonkTrader.exchange.bitmex.const import (
    INSTRUMENT_FILENAME, KLINE_FILE_NAME,
)
from tests.tools import get_resource_path


@pytest.fixture()
def settings() -> Generator[Setting, None, None]:
    yield Setting()


@pytest.fixture()
def exchange() -> Generator[MagicMock, None, None]:
    yield MagicMock(BaseSimExchange)


@pytest.fixture()
def tem_data_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(get_resource_path('test_instrument.json'), os.path.join(tmp, INSTRUMENT_FILENAME))
        shutil.copy(get_resource_path('test_table.hdf'), os.path.join(tmp, KLINE_FILE_NAME))
        yield tmp
