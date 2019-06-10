from collections import defaultdict
from typing import Any, Dict, List, Union

import pandas
from monkq.assets.instrument import FutureInstrument, Instrument
from monkq.context import Context
from monkq.exchange.base import BaseSimExchange
from monkq.utils.dataframe import (
    kline_1m_to_freq, kline_count_window, kline_indicator,
)

INSTRUMENT = Union[Instrument, FutureInstrument]


class Initer:
    def __init__(self, context: Context):
        self.context: Context = context
        self._cache_kline: Dict[INSTRUMENT, Dict[str, pandas.DataFrame]] = defaultdict(dict)
        self._cache_indicator: Dict[str, pandas.DataFrame] = {}

    def init_kline_freq(self, freq: str, instrument: INSTRUMENT) -> None:
        assert instrument.exchange
        exchange = self.context.exchanges[instrument.exchange.name]
        assert isinstance(exchange, BaseSimExchange)
        data = exchange.all_data(instrument)
        self._cache_kline[instrument].update({freq: kline_1m_to_freq(data, freq)})

    def init_indicator(self, freq: str, instrument: INSTRUMENT, func: str,
                       store_key: str,
                       columns: List[str], *args: Any, **kwargs: Any) -> None:
        if freq == '1min':
            assert instrument.exchange
            exchange = self.context.exchanges[instrument.exchange.name]
            assert isinstance(exchange, BaseSimExchange)
            data = exchange.all_data(instrument)
        else:
            data = self._cache_kline[instrument][freq]

        self._cache_indicator[store_key] = kline_indicator(data, func, columns, *args, **kwargs)

    def history_kline(self, freq: str, instrument: INSTRUMENT, count: int) -> pandas.DataFrame:
        frame = self._cache_kline[instrument][freq]
        return kline_count_window(frame, self.context.now, count)

    def history_indicator(self, store_key: str, count: int) -> pandas.DataFrame:
        frame = self._cache_indicator[store_key]
        return kline_count_window(frame, self.context.now, count)
