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
from functools import partial
from typing import Any, List

import pandas
import talib
from dateutil.relativedelta import relativedelta
from matplotlib.axes import Axes
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from monkq.config.global_settings import KLINE_SIDE_CLOSED, KLINE_SIDE_LABEL
from talib import abstract


def _is_min_not_remain(obj: datetime.datetime) -> bool:
    return obj.second == 0 and obj.microsecond == 0


def _is_xmin_not_remain(obj: datetime.datetime, x: int) -> bool:
    return _is_min_not_remain(obj) and obj.minute % x == 0


def is_datetime_not_remain(obj: datetime.datetime, freq: str) -> bool:
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


def _get_relativedelta(period: int, minutes: int, forward: bool) -> relativedelta:
    remain = minutes % period
    if forward:
        return relativedelta(second=0, microsecond=0, minutes=period - remain)
    else:
        return relativedelta(second=0, microsecond=0, minutes=-remain)


def make_datetime_exactly(obj: datetime.datetime, freq: str, forward: bool) -> datetime.datetime:
    if is_datetime_not_remain(obj, freq):
        return obj
    else:
        if freq == 'T':
            if forward:
                relat = relativedelta(second=0, microsecond=0, minutes=+1)
            else:
                relat = relativedelta(second=0, microsecond=0)
        elif freq == '5T':
            relat = _get_relativedelta(5, obj.minute, forward)
        elif freq == '15T':
            relat = _get_relativedelta(15, obj.minute, forward)
        elif freq == '30T':
            relat = _get_relativedelta(30, obj.minute, forward)
        elif freq == '60T':
            relat = _get_relativedelta(60, obj.minute, forward)
        else:
            raise NotImplementedError()
        outcome = obj + relat
        return outcome


def kline_count_window(df: pandas.DataFrame, endtime: datetime.datetime, count: int) -> pandas.DataFrame:
    freq = df.index.freq.freqstr

    if is_datetime_not_remain(endtime, freq):
        starttime = endtime - df.index.freq.delta * (count - 1)
    else:
        starttime = endtime - df.index.freq.delta * count

    return df.loc[starttime:endtime]  # type: ignore


CONVERSION = {
    'high': 'max',
    'low': 'min',
    'open': 'first',
    'close': 'last',
    'volume': 'sum',
    'turnover': 'sum'
}


def kline_1m_to_freq(df: pandas.DataFrame, freq: str) -> pandas.DataFrame:
    result = df.resample(freq, closed=KLINE_SIDE_CLOSED, label=KLINE_SIDE_LABEL).apply(CONVERSION)
    return result


TA_FUNCTION = talib.get_functions()


def kline_indicator(df: pandas.DataFrame,
                    func: str, columns: List[str],
                    *args: Any, **kwargs: Any) -> pandas.DataFrame:
    assert func in TA_FUNCTION, "not a valid function for talib"
    func = abstract.Function(func)
    result = func(df, *args, price=columns, **kwargs)  # type:ignore
    return result


def kline_time_window(df: pandas.DataFrame, start_datetime: datetime.datetime,
                      end_datetime: datetime.datetime) -> pandas.DataFrame:
    return df.loc[start_datetime: end_datetime]  # type:ignore


def _adjust_axe_timeaxis_view(ax: Axes) -> Axes:
    locator = AutoDateLocator()
    daysFmt = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.autoscale_view()
    return ax


def plot_kline_candlestick(ax: Axes, df: pandas.DataFrame, colordown: str = 'g', colorup: str = 'r',
                           alpha: float = 1.0) -> Axes:
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown
    """

    figure: Figure = ax.figure
    f_width = figure.get_figwidth()

    bar_take_axes_size_percentage = 0.9

    bar_width = f_width * bar_take_axes_size_percentage / len(df) / ax.numCols
    offset = bar_width / 2.0

    lines = []
    patches = []
    for row in df.iterrows():
        t = date2num(row[0])
        data = row[1]
        close = data.close
        open = data.open
        high = data.high
        low = data.low
        if close >= open:
            color = colorup
            lower = open
            height = close - open
        else:
            color = colordown
            lower = close
            height = open - close

        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - offset, lower),
            width=bar_width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)

    return _adjust_axe_timeaxis_view(ax)


def plot_indicator(ax: Axes, df: pandas.DataFrame, alpha: float = 1) -> Axes:
    # line = Line2D()
    for column in df.iteritems():
        name, dataframe = column
        ax.plot(date2num(dataframe.index.to_pydatetime()), dataframe.values, label=name, alpha=alpha)
    ax.legend()
    return _adjust_axe_timeaxis_view(ax)


def plot_volume(ax: Axes, kline: pandas.DataFrame, color: str = 'b', alpha: float = 1) -> Axes:
    figure: Figure = ax.figure
    f_width = figure.get_figwidth()
    bar_take_axes_size_percentage = 0.9
    bar_width = f_width * bar_take_axes_size_percentage / len(kline) / ax.numCols
    ax.bar(date2num(kline.index.to_pydatetime()), kline['volume'].values,
           color=color, alpha=alpha, width=bar_width)
    return _adjust_axe_timeaxis_view(ax)
