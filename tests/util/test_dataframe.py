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

from MonkTrader.utils.dataframe import (
    is_datetime_not_remain, kline_dataframe_window, make_datetime_exactly,
)
from MonkTrader.utils.timefunc import utc_datetime
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


def test_1m_dataframe_window() -> None:
    df = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0, 1), utc_datetime(2016, 1, 3))

    df_between = kline_dataframe_window(df, utc_datetime(2016, 1, 2), 100)
    assert len(df_between) == 100
    assert df_between.index[-1] == utc_datetime(2016, 1, 1, 23, 59)

    df_not_full_count_start = kline_dataframe_window(df, utc_datetime(2016, 1, 1, 1), 100)
    assert len(df_not_full_count_start) == 59
    assert df_not_full_count_start.index[-1] == utc_datetime(2016, 1, 1, 0, 59)
    assert df_not_full_count_start.index[0] == utc_datetime(2016, 1, 1, 0, 1)

    df_not_full_count_end = kline_dataframe_window(df, utc_datetime(2016, 1, 3, 0, 20), 100)
    assert len(df_not_full_count_end) == 81
    assert df_not_full_count_end.index[-1] == utc_datetime(2016, 1, 3)

    df_way_out_of_start = kline_dataframe_window(df, utc_datetime(2015, 1, 1), 100)
    assert len(df_way_out_of_start) == 0

    df_way_out_of_end = kline_dataframe_window(df, utc_datetime(2017, 1, 1), 100)
    assert len(df_way_out_of_end) == 0

    df_with_second_in_endtime = kline_dataframe_window(df, utc_datetime(2016, 1, 2, 12, 13, 3), 200)
    assert len(df_with_second_in_endtime) == 200
    assert df_with_second_in_endtime.index[-1] == utc_datetime(2016, 1, 2, 12, 12)


def test_5m_dataframe_window() -> None:
    df_5min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 2, 23, 55),
                                               freq='5min')
    df_5min_between = kline_dataframe_window(df_5min, utc_datetime(2016, 1, 2), 30)
    assert len(df_5min_between) == 30
    assert df_5min_between.index[-1] == utc_datetime(2016, 1, 1, 23, 55)

    df_5min_not_full_start = kline_dataframe_window(df_5min, utc_datetime(2016, 1, 1, 1), 30)
    assert len(df_5min_not_full_start) == 12
    assert df_5min_not_full_start.index[-1] == utc_datetime(2016, 1, 1, 0, 55)
    assert df_5min_not_full_start.index[0] == utc_datetime(2016, 1, 1)

    df_5min_not_full_count_end = kline_dataframe_window(df_5min, utc_datetime(2016, 1, 3, 0, 20), 10)
    assert len(df_5min_not_full_count_end) == 6
    assert df_5min_not_full_count_end.index[-1] == utc_datetime(2016, 1, 2, 23, 55)

    df_5min_with_remain_in_end_time = kline_dataframe_window(df_5min, utc_datetime(2016, 1, 2, 12, 13, 3), 30)
    assert len(df_5min_with_remain_in_end_time) == 30
    assert df_5min_with_remain_in_end_time.index[-1] == utc_datetime(2016, 1, 2, 12, 5)


def test_other_dataframe_window() -> None:
    df_15min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 3), freq='15min')
    df_15min_between = kline_dataframe_window(df_15min, utc_datetime(2016, 1, 2), 10)
    assert len(df_15min_between) == 10
    assert df_15min_between.index[-1] == utc_datetime(2016, 1, 1, 23, 45)

    df_30min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 3), freq='30min')
    df_30min_between = kline_dataframe_window(df_30min, utc_datetime(2016, 1, 2), 10)
    assert len(df_30min_between) == 10
    assert df_30min_between.index[-1] == utc_datetime(2016, 1, 1, 23, 30)

    df_60min = random_kline_data_with_start_end(utc_datetime(2016, 1, 1, 0), utc_datetime(2016, 1, 3), freq='60min')
    df_60min_between = kline_dataframe_window(df_60min, utc_datetime(2016, 1, 2), 10)
    assert len(df_60min_between) == 10
    assert df_60min_between.index[-1] == utc_datetime(2016, 1, 1, 23)
