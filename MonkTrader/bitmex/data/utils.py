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

import pandas

def _date_parse(one):
    return pandas.to_datetime(one, format="%Y-%m-%dD%H:%M:%S.%f")

def tar_to_kline(path, frequency):
    t_frame = pandas.read_csv(path, compression='gzip',
                              parse_dates=[0],
                              infer_datetime_format=True,
                              usecols=["timestamp", "symbol", "side", "size", "price", "tickDirection",
                                                               "trdMatchID", "grossValue", "homeNotional", "foreignNotional"],
                              engine='c', low_memory=True, date_parser=_date_parse)
    t_frame.set_index('timestamp', inplace=True)
    symbols = t_frame['symbol'].unique()
    klines = {}
    for symbol in symbols:
        obj = t_frame.loc[t_frame['symbol'] == symbol]
        kline = obj['price'].resample(frequency).ohlc()
        kline['value'] = obj['grossValue'].resample(frequency).sum()
        klines[symbol] = kline

    return klines

