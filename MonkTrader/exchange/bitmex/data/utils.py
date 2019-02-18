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
from typing import Optional

import numpy as np
import pandas
from MonkTrader.assets.const import SIDE
from MonkTrader.const import TICK_DIRECTION

dtypes_trades = {
    "timestamp": np.object,
    "symbol": np.str,
    "side": np.int8,
    "size": np.int64,
    "price": np.float64,
    "tickDirection": np.int8,
    "trdMatchID": np.str,
    "grossValue": np.int64,
    "homeNotional": np.float64,
    "foreignNotional": np.float64
}

dtypes_quote = {
    "timestamp": np.object,
    "symbol": np.str,
    "bidSize": np.float64,
    "bidPrice": np.float64,
    "askPrice": np.float64,
    "askSize": np.float64
}


def _date_parse(one: str) -> pandas.Timestamp:
    return pandas.to_datetime(one, format="%Y-%m-%dD%H:%M:%S.%f")


def _side_converters(side: str) -> SIDE:
    if side == 'Buy':
        return SIDE.BUY.value
    elif side == 'Sell':
        return SIDE.SELL.value
    else:
        return SIDE.UNKNOWN.value


def _tick_direction(tick_direction: str) -> TICK_DIRECTION:
    if tick_direction == 'MinusTick':
        return TICK_DIRECTION.MINUS_TICK.value
    elif tick_direction == 'PlusTick':
        return TICK_DIRECTION.PLUS_TICK.value
    elif tick_direction == 'ZeroMinusTick':
        return TICK_DIRECTION.ZERO_MINUS_TICK.value
    elif tick_direction == 'ZeroPlusTick':
        return TICK_DIRECTION.ZERO_PLUS_TICK.value
    else:
        return TICK_DIRECTION.UNKNOWN.value


def read_trade_tar(path: str, with_detailed: bool = False, with_symbol: bool = True,
                   index: Optional[str] = None) -> pandas.DataFrame:
    if with_detailed:
        usecols = ["timestamp", "side", "size", "price",
                   "tickDirection", "trdMatchID", "grossValue",
                   "homeNotional", "foreignNotional"]
    else:
        usecols = ["timestamp", "side", "size", "price", "tickDirection",
                   "grossValue", "homeNotional", "foreignNotional"]
    if with_symbol:
        usecols.append("symbol")
    use_dtypes = {}
    for col in usecols:
        if col in ('side', "tickDirection"):
            continue
        use_dtypes[col] = dtypes_trades[col]
    t_frame = pandas.read_csv(path, compression='gzip',
                              parse_dates=[0],
                              infer_datetime_format=True,
                              usecols=usecols,
                              dtype=use_dtypes,
                              converters={'side': _side_converters,
                                          'tickDirection': _tick_direction},
                              engine='c', low_memory=True, date_parser=_date_parse)
    if index:
        t_frame.set_index(index, inplace=True)
    return t_frame


def read_quote_tar(path: str, with_symbol: bool = True, index: Optional[str] = None) -> pandas.DataFrame:
    usecols = ["timestamp", "bidSize", "bidPrice", "askPrice", "askSize"]
    if with_symbol:
        usecols.append("symbol")

    use_dtypes = {}
    for col in usecols:
        use_dtypes[col] = dtypes_quote[col]
    t_frame = pandas.read_csv(path, compression='gzip',
                              parse_dates=[0],
                              infer_datetime_format=True,
                              usecols=usecols,
                              dtype=use_dtypes,
                              engine='c', low_memory=True, date_parser=_date_parse)
    if index:
        t_frame.set_index(index, inplace=True)
    return t_frame


def _trade_to_kline(frame: pandas.DataFrame, frequency: str) -> pandas.DataFrame:
    kline = frame['price'].resample(frequency).ohlc()
    kline['value'] = frame['grossValue'].resample(frequency).sum()
    return kline


def trades_to_1m_kline(frame: pandas.DataFrame) -> pandas.DataFrame:
    kline = frame['price'].resample('1Min', label='right', closed='right').ohlc()
    kline['volume'] = frame['homeNotional'].resample('1Min', label='right', closed='right').sum()
    kline['turnover'] = frame['foreignNotional'].resample('1Min', label='right', closed='right').sum()
    kline.fillna(method='ffill', inplace=True)
    return kline


def classify_df(df: pandas.DataFrame, column: str, delete_column: bool = True) -> pandas.DataFrame:
    out = {}
    uniques = df[column].unique()
    for one in uniques:
        new = df[df[column] == one]
        if delete_column:
            del new[column]
        out[one] = new
    return out


def tarcsv2hdf(csv_file: str, key: str, output: str = '') -> None:
    frame = read_trade_tar(csv_file, False, False, 'timestamp')
    frame.to_hdf(os.path.join(output, 'trade.hdf'), key, mode='a',
                 format='table', data_columns=True, index=False,
                 complib='blosc:blosclz', complevel=9, append=True)


def convert_all_trade_data2hdf(data_dir: str, output: str = '') -> None:
    base = os.path.join(data_dir, '')
    directories = os.listdir(base)
    directories.sort()
    for directory in directories:
        print('date {}'.format(directory))
        date_file = os.path.join(base, directory)
        symbols_files = os.listdir(date_file)
        for path in symbols_files:
            print(path)
            symbol = path.split('.')[0]
            tarcsv2hdf(os.path.join(date_file, path), symbol, output)
