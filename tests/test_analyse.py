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
import pickle
import sys
from typing import Any, Generator

import pytest
from matplotlib.figure import Figure
from monkq.analyse import Analyser
from monkq.base_strategy import BaseStrategy
from monkq.config import Setting
from monkq.utils.timefunc import utc_datetime
from tests.tools import get_resource_path


def _override_result_setting(setting: Setting, key: str, value: Any) -> None:
    setattr(setting, key, value)


@pytest.fixture()
def strategy_module() -> Generator[None, None, None]:
    class M():
        pass

    module = M()
    setattr(module, 'TestStrategy', BaseStrategy)
    sys.modules['strategy'] = module  # type:ignore
    yield None
    sys.modules.pop('strategy')


@pytest.fixture()
def analyse_result(tem_data_dir: str, strategy_module: None) -> Generator[str, None, None]:
    with open(get_resource_path('result.pkl'), 'rb') as f:
        result = pickle.load(f)
    _override_result_setting(result['settings'], 'DATA_DIR', tem_data_dir)

    result_file = os.path.join(tem_data_dir, 'result.pkl')
    with open(result_file, 'wb') as f:
        pickle.dump(result, f)
    yield result_file


@pytest.mark.mpl_image_compare(baseline_dir='resource/images',
                               filename='account.png')
def test_analyse_plot_account(analyse_result: str) -> Figure:
    analyser = Analyser(analyse_result)
    fig, axe = analyser.plot_account()
    return fig


@pytest.mark.mpl_image_compare(baseline_dir='resource/images',
                               filename='kline.png')
def test_analyse_plot_kline(analyse_result: str) -> Figure:
    analyser = Analyser(analyse_result)
    fig, axe = analyser.plot_kline('bitmex', '60min', 'XBTZ15',
                                   utc_datetime(2015, 7, 1), utc_datetime(2015, 8, 1))
    return fig


@pytest.mark.mpl_image_compare(baseline_dir='resource/images',
                               filename='volume.png')
def test_analyse_plot_volume(analyse_result: str) -> Figure:
    analyser = Analyser(analyse_result)
    fig, axe = analyser.plot_volume('bitmex', '60min', 'XBTZ15',
                                    utc_datetime(2015, 7, 1), utc_datetime(2015, 8, 1))
    return fig


@pytest.mark.mpl_image_compare(baseline_dir='resource/images',
                               filename='indicator.png')
def test_analyse_plot_indicator(analyse_result: str) -> Figure:
    analyser = Analyser(analyse_result)
    fig, axe = analyser.plot_indicator('bitmex', '60min', 'XBTZ15', 'BBANDS',
                                       ['close'], utc_datetime(2015, 7, 1), utc_datetime(2015, 8, 1))
    return fig


@pytest.mark.mpl_image_compare(baseline_dir='resource/images',
                               filename='trade_mark.png')
def test_analyse_mark_trades(analyse_result: str) -> Figure:
    analyser = Analyser(analyse_result)
    fig, axe = analyser.plot_kline('bitmex', '4H', 'XBTZ15',
                                   utc_datetime(2015, 5, 15), utc_datetime(2015, 6, 15))
    analyser.mark_trades(axe, utc_datetime(2015, 5, 15), utc_datetime(2015, 6, 15))
    return fig


def test_analyse_trades(analyse_result: str) -> None:
    analyser = Analyser(analyse_result)
    trades = analyser.trades
    assert len(trades) == 1
    assert trades.iloc[0]['symbol'] == "XBTZ15"
