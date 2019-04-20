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
import pickle
from importlib import import_module
from typing import Any, List, Optional, Tuple, Type

import matplotlib.pyplot as plt
import pandas
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from monkq.utils.dataframe import (
    kline_1m_to_freq, kline_indicator, kline_time_window, plot_indicator,
    plot_kline_candlestick, plot_volume,
)

DATA_LOADER_CLASS = "DataLoader"

AVAILABLE_COLORS = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')


class Analyser():
    def __init__(self, result_file: str):
        with open(result_file, 'rb') as f:
            self.result_data = pickle.load(f)
        self.settings = self.result_data['settings']
        self.start_datetime = getattr(self.settings, 'START_TIME')
        self.end_datetime = getattr(self.settings, 'END_TIME')

        self.data_dir = getattr(self.settings, 'DATA_DIR')
        self.data_loaders: dict = {}
        self._account_df: Optional[pandas.DataFrame] = None

        self.setup_data_loader()

    @property
    def accounts_info(self) -> pandas.DataFrame:
        if self._account_df is None:
            self._account_df = self._account_to_df()
        return self._account_df

    def _account_to_df(self) -> pandas.DataFrame:
        df = pandas.DataFrame(self.result_data['daily_capital'])
        df.set_index('timestamp', inplace=True)
        return df

    def setup_data_loader(self) -> None:
        exchange_settings = getattr(self.settings, 'EXCHANGES')
        for exchange_name, exchange_setting in exchange_settings.items():
            dataloader_cls = self.load_dataloader_cls(exchange_setting['ENGINE'])
            self.data_loaders[exchange_name] = dataloader_cls(self.data_dir)

    def load_dataloader_cls(self, exchange_cls_entry: str) -> Type:
        mod_path, _, cls_name = exchange_cls_entry.rpartition('.')

        mod_path = '.'.join((mod_path, 'data'))
        mod = import_module(mod_path)

        cls = getattr(mod, DATA_LOADER_CLASS)
        return cls

    def _fetch_kline(self, exchange: str, freq: str, symbol: str,
                     start: Optional[datetime.datetime] = None,
                     end: Optional[datetime.datetime] = None) -> pandas.DataFrame:
        if start is None:
            start = self.start_datetime
        if end is None:
            end = self.end_datetime
        dataloader = self.data_loaders[exchange]
        kline_df = dataloader.all_data(symbol)
        if freq != '1min':
            kline_df = kline_1m_to_freq(kline_df, freq)

        return kline_time_window(kline_df, start, end)

    def plot_kline(self, exchange: str, freq: str, symbol: str,
                   start: Optional[datetime.datetime] = None,
                   end: Optional[datetime.datetime] = None, alpha: float = 1,
                   axes: Optional[Axes] = None) -> Tuple[Figure, Axes]:

        df = self._fetch_kline(exchange, freq, symbol, start, end)
        if axes is None:
            fig, axes = plt.subplots()

        plot_kline_candlestick(axes, df, alpha=alpha)

        return (axes.figure, axes)

    def plot_indicator(self, exchange: str, freq: str, symbol: str, func: str, columns: List[str],
                       start: Optional[datetime.datetime] = None,
                       end: Optional[datetime.datetime] = None,
                       axes: Optional[Axes] = None, *args: Any,
                       **kwargs: Any) -> Tuple[Figure, Axes]:
        df = self._fetch_kline(exchange, freq, symbol, start, end)
        indicators = kline_indicator(df, func, columns, *args, **kwargs)
        if axes is None:
            fig, axes = plt.subplots()
        plot_indicator(axes, indicators)
        return (axes.figure, axes)

    def plot_volume(self, exchange: str, freq: str, symbol: str,
                    start: Optional[datetime.datetime] = None,
                    end: Optional[datetime.datetime] = None,
                    color: str = 'b', alpha: float = 1,
                    axes: Optional[Axes] = None) -> Tuple[Figure, Axes]:
        df = self._fetch_kline(exchange, freq, symbol, start, end)
        if axes is None:
            fig, axes = plt.subplots()
        plot_volume(axes, df, color, alpha)
        return (axes.figure, axes)

    def plot_account(self, axes: Optional[Axes] = None) -> Tuple[Figure, Axes]:
        if axes is None:
            fig, axes = plt.subplots()
        df = self.accounts_info
        plot_indicator(axes, df)
        return (axes.figure, axes)
