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

import numpy as np
import pandas
from MonkTrader.exchange.bitmex.data import TRADES_DATA_F

from . import HDF_FILE_NAME

dtypes_trades = {
    "timestamp": np.object,
    "symbol": np.str,
    "side": np.bool,
    "size": np.int64,
    "price": np.float64,
    "tickDirection": np.str,
    "trdMatchID": np.str,
    "grossValue": np.int64,
    "homeNotional": np.float64,
    "foreignNotional": np.float64
}

def _date_parse(one):
    return pandas.to_datetime(one, format="%Y-%m-%dD%H:%M:%S.%f")


def _read_trade_tar(path, with_detailed=False, with_symbol=True, index=None):
    if with_detailed:
        usecols = ["timestamp", "side", "size", "price",
                   "tickDirection","trdMatchID", "grossValue",
                   "homeNotional", "foreignNotional"]
    else:
        usecols = ["timestamp", "side", "size", "price",
                   "grossValue", "homeNotional", "foreignNotional"]
    if with_symbol:
        usecols.append("symbol")
    t_frame = pandas.read_csv(path, compression='gzip',
                              parse_dates=[0],
                              infer_datetime_format=True,
                              usecols=usecols,
                              dtype=dtypes_trades,
                              false_values=['Buy'], true_values=['Sell'],
                              engine='c', low_memory=True, date_parser=_date_parse)
    if index:
        t_frame.set_index(index, inplace=True)
    return t_frame


def _trade_to_kline(frame, frequency):
    kline = frame['price'].resample(frequency).ohlc()
    kline['value'] = frame['grossValue'].resample(frequency).sum()
    return kline


def tar_to_kline(path, frequency):
    t_frame = _read_trade_tar(path)
    symbols = t_frame['symbol'].unique()
    klines = {}
    for symbol in symbols:
        obj = t_frame.loc[t_frame['symbol'] == symbol]
        klines[symbol] = _trade_to_kline(obj, frequency)

    return klines

def tarcsv2hdf(csv_file, key, output=''):
    frame = _read_trade_tar(csv_file, True)
    frame.to_hdf(os.path.join(output, HDF_FILE_NAME), key, mode='a', format='table',
                 complib='blosc')

def convert_all_trade_data2hdf(data_dir, output=''):
    base = os.path.join(data_dir, TRADES_DATA_F)
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
