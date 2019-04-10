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

import pytest
import os
import shutil
import pickle
from typing import Generator, Any
from tests.tools import get_resource_path

from monkq.analyse import Analyser
from monkq.config import Setting


def _override_result_setting(setting: Setting, key: str, value: Any) -> None:
    setattr(setting, key, value)

@pytest.fixture()
def analyse_result(tem_data_dir: str) -> Generator[str, None, None]:
    with open(get_resource_path('result.pkl'), 'rb') as f:
        result = pickle.load(f)
    _override_result_setting(result['settings'], 'DATA_DIR', tem_data_dir)

    result_file = os.path.join(tem_data_dir, 'result.pkl')
    with open(result_file, 'wb') as f:
        pickle.dump(result, f)
    yield result_file


def test_analyse(analyse_result: str):
    analyser = Analyser(analyse_result)
    print(analyse_result)
