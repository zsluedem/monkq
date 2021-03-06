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
from typing import IO, List, Optional, Union

import numpy as np
import pandas
from dateutil.relativedelta import relativedelta
from monkq.assets.const import SIDE
from monkq.config.global_settings import KLINE_SIDE_CLOSED, KLINE_SIDE_LABEL
from monkq.const import TICK_DIRECTION

dtypes_trades = {
    "timestamp": np.object,
    "symbol": np.str,
    "side": np.float64,
    "size": np.float64,
    "price": np.float64,
    "tickDirection": np.float64,
    "trdMatchID": np.str,
    "grossValue": np.float64,
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
    return pandas.to_datetime(one, format="%Y-%m-%dD%H:%M:%S.%f", utc=True)


def _side_converters(side: str) -> SIDE:
    if side == 'Buy':
        return np.float64(SIDE.BUY.value)
    elif side == 'Sell':
        return np.float64(SIDE.SELL.value)
    else:
        return np.float64(SIDE.UNKNOWN.value)  # pragma: no cover


def _tick_direction(tick_direction: str) -> TICK_DIRECTION:
    if tick_direction == 'MinusTick':
        return np.float64(TICK_DIRECTION.MINUS_TICK.value)
    elif tick_direction == 'PlusTick':
        return np.float64(TICK_DIRECTION.PLUS_TICK.value)
    elif tick_direction == 'ZeroMinusTick':
        return np.float64(TICK_DIRECTION.ZERO_MINUS_TICK.value)
    elif tick_direction == 'ZeroPlusTick':
        return np.float64(TICK_DIRECTION.ZERO_PLUS_TICK.value)
    else:
        return np.float64(TICK_DIRECTION.UNKNOWN.value)  # pragma: no cover


def read_trade_tar(path: Union[str, IO], with_detailed: bool = False, with_symbol: bool = True,
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


def read_quote_tar(path: Union[str, IO], with_symbol: bool = True, index: Optional[str] = None) -> pandas.DataFrame:
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


def trades_to_1m_kline(frame: pandas.DataFrame) -> pandas.DataFrame:
    re_df = frame.resample('1Min', label=KLINE_SIDE_LABEL, closed=KLINE_SIDE_CLOSED)
    kline = re_df['price'].ohlc()
    kline['volume'] = re_df['homeNotional'].sum()
    kline['turnover'] = re_df['foreignNotional'].sum()
    kline.fillna(method='ffill', inplace=True)
    return kline


def kline_from_list_of_dict(obj: List[dict]) -> pandas.DataFrame:
    """dict format
    {'timestamp': '2019-03-02T02:05:00.000Z',
    'symbol': 'XBTUSD',
    'open': 3822,
    'high': 3822,
    'low': 3822,
    'close': 3822,
    'trades': 0,
    'volume': 0,
    'vwap': None,
    'lastSize': None,
    'turnover': 0,
    'homeNotional': 0,
    'foreignNotional': 0}"""

    df = pandas.DataFrame(obj, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    df['timestamp'] = pandas.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df


def fullfill_1m_kline_with_start_end(frame: pandas.DataFrame, start: datetime.datetime,
                                     end: datetime.datetime) -> pandas.DataFrame:
    assert start.second == 0
    assert start.microsecond == 0
    assert end.second == 0
    assert end.microsecond == 0
    new = pandas.DataFrame([
        (np.nan, np.nan, np.nan, np.nan, 0., 0.),
        (np.nan, np.nan, np.nan, np.nan, 0., 0.)
    ], columns=["high", "low", "open", "close", "volume", "turnover"], index=pandas.DatetimeIndex((start, end)))

    new_df = frame.append(new, sort=False)
    resample = new_df.resample('1Min', label=KLINE_SIDE_LABEL, closed=KLINE_SIDE_CLOSED, convention="end")

    outcome = resample['close'].last()
    outcome = pandas.DataFrame(index=outcome.index)
    outcome['close'] = resample['close'].last()
    outcome['open'] = resample['open'].last()
    outcome['high'] = resample['high'].last()
    outcome['low'] = resample['low'].last()
    outcome['volume'] = resample['volume'].sum()
    outcome['turnover'] = resample['turnover'].sum()
    outcome.fillna(method='ffill', inplace=True)
    return outcome


def classify_df(df: pandas.DataFrame, column: str, delete_column: bool = True) -> pandas.DataFrame:
    out = {}
    uniques = df[column].unique()
    for one in uniques:
        new = df[df[column] == one]
        if delete_column:
            del new[column]
        out[one] = new
    return out


def check_1m_data_integrity(df: pandas.DataFrame, start: datetime.datetime, end: datetime.datetime) -> bool:
    assert start.second == 0
    assert start.microsecond == 0
    assert end.second == 0
    assert end.microsecond == 0
    start = start + relativedelta(minutes=1)
    total_date = pandas.date_range(start, end, freq='min')
    return len(df) == len(total_date) and df.index[0] == start and df.index[-1] == end
