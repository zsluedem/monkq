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

import numpy
import pandas
from pytz import utc


def random_quote_frame(length: int, timestamp: pandas.Timestamp = pandas.Timestamp(2018, 1, 3)) -> pandas.DataFrame:
    df = pandas.DataFrame(numpy.random.uniform(1, 1000, size=(length, 4)),
                          columns=["bidSize", "bidPrice", "askPrice", "askSize"],
                          index=pandas.date_range(start=timestamp, periods=length, freq='S', tz=utc))
    return df


def random_trade_frame(length: int, timestamp: pandas.Timestamp = pandas.Timestamp(2018, 1, 3)) -> pandas.DataFrame:
    df = pandas.DataFrame(numpy.random.uniform(1, 1000, size=(length, 5)),
                          columns=["size", "price", "grossValue", "homeNotional", "foreignNotional"],
                          index=pandas.date_range(start=timestamp, periods=length, freq='S', tz=utc))
    df['side'] = pandas.Series(numpy.random.randint(1, 2),
                               index=pandas.date_range(start=timestamp, periods=length, freq='S', tz=utc))
    df['side'] = df['side'].astype(numpy.float64)
    df['tickDirection'] = pandas.Series(numpy.random.randint(1, 4),
                                        index=pandas.date_range(start=timestamp, periods=length, freq='S', tz=utc))
    df['tickDirection'] = df['tickDirection'].astype(numpy.float64)

    return df


def random_kline_data(length: int, endtime: pandas.Timestamp, freq:str='min') -> pandas.DataFrame:
    df = pandas.DataFrame(numpy.random.uniform(1, 1000, size=(length, 6)),
                          columns=["high", "low", "open", "close", "volume", "turnover"],
                          index=pandas.date_range(end=endtime, periods=length, freq=freq, tz=utc))

    return df


def random_quote_hdf(path: str, length: int = 3) -> None:
    tmp_df = random_quote_frame(length=length)
    tmp_df2 = random_quote_frame(length=length)

    tmp_df.to_hdf(path, '/XBTUSD',
                  data_columns=True, index=False, complib='blosc:blosclz',
                  complevel=9, append=True, format='table')
    tmp_df2.to_hdf(path, '/ETHUSD',
                   data_columns=True, index=False, complib='blosc:blosclz',
                   complevel=9, append=True, format='table')


def random_trade_hdf(path: str, length: int = 3) -> None:
    tmp_df = random_trade_frame(length=length)
    tmp_df2 = random_trade_frame(length=length)

    tmp_df.to_hdf(path, '/XBTUSD',
                  data_columns=True, index=False, complib='blosc:blosclz',
                  complevel=9, append=True, format='table')
    tmp_df2.to_hdf(path, '/ETHUSD',
                   data_columns=True, index=False, complib='blosc:blosclz',
                   complevel=9, append=True, format='table')
