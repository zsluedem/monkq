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
import pandas
import datetime
from functools import partial


def _is_min_not_remain(obj: datetime.datetime) -> bool:
    return obj.second == 0 and obj.microsecond == 0


def _is_xmin_not_remain(obj: datetime.datetime, x: int) -> bool:
    return _is_min_not_remain(obj) and obj.minute % x == 0


def _is_datetime_not_remain(obj: datetime.datetime, freq: str) -> bool:
    if freq == 'T':
        remain_method = _is_min_not_remain
    elif freq == '5T':
        remain_method = partial(_is_xmin_not_remain, x=5)
    elif freq == '15T':
        remain_method = partial(_is_xmin_not_remain, x=15)
    elif freq == '30T':
        remain_method = partial(_is_xmin_not_remain, x=30)
    elif freq == '60T' or freq == 'H':
        remain_method = partial(_is_xmin_not_remain, x=60)
    else:
        raise NotImplementedError()

    return remain_method(obj)


def kline_dataframe_window(df: pandas.DataFrame, endtime: datetime.datetime, count: int) -> pandas.DataFrame:
    freq = df.index.freq.freqstr

    if _is_datetime_not_remain(endtime, freq):
        endtime = endtime - df.index.freq.delta
        starttime = endtime - df.index.freq.delta * (count - 1)
    else:
        endtime = endtime - df.index.freq.delta
        starttime = endtime - df.index.freq.delta * count

    return df.loc[starttime:endtime]  # type: ignore
