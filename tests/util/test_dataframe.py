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
import random

from monkq.utils.dataframe import (
    is_datetime_not_remain, kline_1m_to_freq, kline_count_window,
    kline_indicator, kline_time_window, make_datetime_exactly,
)
from monkq.utils.timefunc import utc_datetime
from tests.tools import random_kline_data_with_start_end


def test_is_datetime_not_remain() -> None:
    assert is_datetime_not_remain(utc_datetime(2018, 1, 1, 12, 32), "T")
    assert not is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 1, 1), "T")

    assert is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 25), "5T")
    assert not is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 1, 1), "5T")

    assert is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 15), "15T")
    assert not is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 25), "15T")

    assert is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 30), "30T")
    assert not is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 25), "30T")

    assert is_datetime_not_remain(utc_datetime(2018, 1, 1, 1), "60T")
    assert not is_datetime_not_remain(utc_datetime(2018, 1, 1, 1, 25), "60T")

    assert is_datetime_not_remain(utc_datetime(2018, 1, 1), "2H")
    assert not is_datetime_not_remain(utc_datetime(2018, 1, 1, 1), "2H")


def test_make_datetime_exactly() -> None:
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "T", True) == utc_datetime(2018, 1, 1, 12, 12)
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "T", False) == utc_datetime(2018, 1, 1, 12, 11)

    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "5T", True) == utc_datetime(2018, 1, 1, 12, 15)
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "5T", False) == utc_datetime(2018, 1, 1, 12, 10)

    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "15T", True) == utc_datetime(2018, 1, 1, 12, 15)
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "15T", False) == utc_datetime(2018, 1, 1, 12, 0)

    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "30T", True) == utc_datetime(2018, 1, 1, 12, 30)
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "30T", False) == utc_datetime(2018, 1, 1, 12)

    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "60T", True) == utc_datetime(2018, 1, 1, 13)
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "60T", False) == utc_datetime(2018, 1, 1, 12)

    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "4H", False) == utc_datetime(2018, 1, 1, 12)
    assert make_datetime_exactly(utc_datetime(2018, 1, 1, 12, 11, 23), "4H", True) == utc_datetime(2018, 1, 1, 16)


def test_1m_dataframe_window() -> None:
    df = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0, 1), utc_datetime(2016, 1, 3))

    df_between = kline_count_window(df, utc_datetime(2016, 1, 2), 100)
    assert len(df_between) == 100
    assert df_between.index[-1] == utc_datetime(2016, 1, 2)

    df_not_full_count_start = kline_count_window(df, utc_datetime(2016, 1, 1, 1), 100)
    assert len(df_not_full_count_start) == 60
    assert df_not_full_count_start.index[-1] == utc_datetime(2016, 1, 1, 1)
    assert df_not_full_count_start.index[0] == utc_datetime(2016, 1, 1, 0, 1)

    df_not_full_count_end = kline_count_window(df, utc_datetime(2016, 1, 3, 0, 20), 100)
    assert len(df_not_full_count_end) == 80
    assert df_not_full_count_end.index[-1] == utc_datetime(2016, 1, 3)

    df_way_out_of_start = kline_count_window(df, utc_datetime(2015, 1, 1), 100)
    assert len(df_way_out_of_start) == 0

    df_way_out_of_end = kline_count_window(df, utc_datetime(2017, 1, 1), 100)
    assert len(df_way_out_of_end) == 0

    df_with_second_in_endtime = kline_count_window(df, utc_datetime(2016, 1, 2, 12, 13, 3), 200)
    assert len(df_with_second_in_endtime) == 200
    assert df_with_second_in_endtime.index[-1] == utc_datetime(2016, 1, 2, 12, 13)


def test_5m_dataframe_window() -> None:
    df_5min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 2, 23, 55),
                                               freq='5min')
    df_5min_between = kline_count_window(df_5min, utc_datetime(2016, 1, 2), 30)
    assert len(df_5min_between) == 30
    assert df_5min_between.index[-1] == utc_datetime(2016, 1, 2)

    df_5min_not_full_start = kline_count_window(df_5min, utc_datetime(2016, 1, 1, 1), 30)
    assert len(df_5min_not_full_start) == 13
    assert df_5min_not_full_start.index[-1] == utc_datetime(2016, 1, 1, 1)
    assert df_5min_not_full_start.index[0] == utc_datetime(2016, 1, 1)

    df_5min_not_full_count_end = kline_count_window(df_5min, utc_datetime(2016, 1, 3, 0, 20), 10)
    assert len(df_5min_not_full_count_end) == 5
    assert df_5min_not_full_count_end.index[-1] == utc_datetime(2016, 1, 2, 23, 55)

    df_5min_with_remain_in_end_time = kline_count_window(df_5min, utc_datetime(2016, 1, 2, 12, 13, 3), 30)
    assert len(df_5min_with_remain_in_end_time) == 30
    assert df_5min_with_remain_in_end_time.index[-1] == utc_datetime(2016, 1, 2, 12, 10)


def test_other_dataframe_window() -> None:
    df_15min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 3), freq='15min')
    df_15min_between = kline_count_window(df_15min, utc_datetime(2016, 1, 1, 23, 45), 10)
    assert len(df_15min_between) == 10
    assert df_15min_between.index[-1] == utc_datetime(2016, 1, 1, 23, 45)

    df_30min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 3), freq='30min')
    df_30min_between = kline_count_window(df_30min, utc_datetime(2016, 1, 1, 23, 30), 10)
    assert len(df_30min_between) == 10
    assert df_30min_between.index[-1] == utc_datetime(2016, 1, 1, 23, 30)

    df_60min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 3), freq='60min')
    df_60min_between = kline_count_window(df_60min, utc_datetime(2016, 1, 1, 23), 10)
    assert len(df_60min_between) == 10
    assert df_60min_between.index[-1] == utc_datetime(2016, 1, 1, 23)


def test_kline_1m_to_freq() -> None:
    df_1min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1), utc_datetime(2016, 1, 3), freq='1min')

    df_15min = kline_1m_to_freq(df_1min, '15min')
    assert len(df_15min) == 193
    assert df_15min.index[0] == utc_datetime(2016, 1, 1)
    assert df_15min.index[1] == utc_datetime(2016, 1, 1, 0, 15)
    assert df_15min.index[-1] == utc_datetime(2016, 1, 3)
    assert df_15min['close'][0] == df_1min['close'][0]
    assert df_15min['high'][0] == df_1min['high'][0]
    assert df_15min['low'][0] == df_1min['low'][0]
    assert df_15min['open'][0] == df_1min['open'][0]
    assert df_15min['close'][1] == df_1min.loc[utc_datetime(2016, 1, 1, 0, 15)]['close']
    assert df_15min['high'][1] == max(
        df_1min.loc[utc_datetime(2016, 1, 1, 0, 1):utc_datetime(2016, 1, 1, 0, 15)]['high'])  # type:ignore
    assert df_15min['low'][1] == min(
        df_1min.loc[utc_datetime(2016, 1, 1, 0, 1):utc_datetime(2016, 1, 1, 0, 15)]['low'])  # type:ignore
    assert df_15min['open'][1] == df_1min.loc[utc_datetime(2016, 1, 1, 0, 1)]['open']

    df_30min = kline_1m_to_freq(df_1min, '30min')
    assert len(df_30min) == 97
    assert df_30min.index[0] == utc_datetime(2016, 1, 1)
    assert df_30min.index[1] == utc_datetime(2016, 1, 1, 0, 30)
    assert df_30min.index[-1] == utc_datetime(2016, 1, 3)
    assert df_30min['close'][0] == df_1min['close'][0]
    assert df_30min['high'][0] == df_1min['high'][0]
    assert df_30min['low'][0] == df_1min['low'][0]
    assert df_30min['open'][0] == df_1min['open'][0]
    assert df_30min['close'][1] == df_1min.loc[utc_datetime(2016, 1, 1, 0, 30)]['close']
    assert df_30min['high'][1] == max(
        df_1min.loc[utc_datetime(2016, 1, 1, 0, 1):utc_datetime(2016, 1, 1, 0, 30)]['high'])  # type:ignore
    assert df_30min['low'][1] == min(
        df_1min.loc[utc_datetime(2016, 1, 1, 0, 1):utc_datetime(2016, 1, 1, 0, 30)]['low'])  # type:ignore
    assert df_30min['open'][1] == df_1min.loc[utc_datetime(2016, 1, 1, 0, 1)]['open']

    df_1h = kline_1m_to_freq(df_1min, '60min')
    assert len(df_1h) == 49
    assert df_1h.index[0] == utc_datetime(2016, 1, 1)
    assert df_1h.index[1] == utc_datetime(2016, 1, 1, 1)
    assert df_1h.index[-1] == utc_datetime(2016, 1, 3)
    assert df_1h['close'][0] == df_1min['close'][0]
    assert df_1h['high'][0] == df_1min['high'][0]
    assert df_1h['low'][0] == df_1min['low'][0]
    assert df_1h['open'][0] == df_1min['open'][0]
    assert df_1h['close'][1] == df_1min.loc[utc_datetime(2016, 1, 1, 1)]['close']
    assert df_1h['high'][1] == max(
        df_1min.loc[utc_datetime(2016, 1, 1, 0, 1):utc_datetime(2016, 1, 1, 1)]['high'])  # type:ignore
    assert df_1h['low'][1] == min(
        df_1min.loc[utc_datetime(2016, 1, 1, 0, 1):utc_datetime(2016, 1, 1, 1)]['low'])  # type:ignore
    assert df_1h['open'][1] == df_1min.loc[utc_datetime(2016, 1, 1, 0, 1)]['open']


def test_kline_indicator() -> None:
    df_1min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1), utc_datetime(2016, 1, 3), freq='1min')

    result = kline_indicator(df_1min, 'MA', ['close'], timeperiod=10)

    assert result[9] == sum(df_1min['close'][:10]) / 10


def test_kline_time_window() -> None:
    df_1min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1), utc_datetime(2016, 1, 10), freq='1min')

    result = kline_time_window(df_1min, utc_datetime(2016, 1, 2), utc_datetime(2016, 1, 9))

    assert result.index[0] == utc_datetime(2016, 1, 2)
    assert result.index[-1] == utc_datetime(2016, 1, 9)
    day = random.randint(2, 8)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    assert result.loc[utc_datetime(2016, 1, day, hour, minute)]['close'] == \
           df_1min.loc[utc_datetime(2016, 1, day, hour, minute)]['close']  # noqa:E128
