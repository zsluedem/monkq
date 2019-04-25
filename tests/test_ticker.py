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

import pytest
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from monkq.exception import SettingError
from monkq.ticker import FrequencyTicker

start_time = datetime.datetime(2018, 1, 1, tzinfo=tzutc())
end_time = datetime.datetime(2018, 1, 3, tzinfo=tzutc())


def test_1m_timer() -> None:
    freq = FrequencyTicker(start_time=start_time, end_time=end_time, frequency='1m')
    point = start_time
    for tick in freq.timer():
        assert tick == point
        point += relativedelta(minutes=+1)
    assert point == end_time + relativedelta(minutes=+1)


def test_1d_timer() -> None:
    freq = FrequencyTicker(start_time=start_time, end_time=end_time, frequency='1d')
    point = start_time
    for tick in freq.timer():
        assert tick == point
        point += relativedelta(days=+1)
    assert point == end_time + relativedelta(days=+1)


def test_timer_aware_timezone() -> None:
    with pytest.raises(AssertionError):
        FrequencyTicker(start_time=datetime.datetime(2018, 1, 1), end_time=datetime.datetime(2018, 1, 3),
                        frequency='1m')


def test_timer_timeexception() -> None:
    with pytest.raises(SettingError):
        FrequencyTicker(start_time=end_time, end_time=start_time, frequency='1m')
