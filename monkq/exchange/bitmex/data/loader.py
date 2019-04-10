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
import json
import os
from typing import TYPE_CHECKING, Dict, Optional, Type

import pandas
from logbook import Logger
from monkq.assets.instrument import (
    CallOptionInstrument, FutureInstrument, Instrument, PerpetualInstrument,
    PutOptionInstrument,
)
from monkq.exception import LoadDataError
from monkq.exchange.bitmex.const import INSTRUMENT_FILENAME, KLINE_FILE_NAME
from monkq.lazyhdf import LazyHDFTableStore
from monkq.utils.dataframe import kline_dataframe_window, make_datetime_exactly
from monkq.utils.i18n import _
from monkq.utils.timefunc import is_aware_datetime

from ..log import logger_group

if TYPE_CHECKING:
    from monkq.exchange.bitmex.exchange import BitmexSimulateExchange  # pragma: no cover  # noqa: F401

logger = Logger('exchange.bitmex.dataloader')
logger_group.add_logger(logger)

instrument_map = {
    'symbol': 'symbol',
    "rootSymbol": 'root_symbol',
    'listing': 'listing_date',
    'expiry': 'expiry_date',
    'underlying': 'underlying',
    "quoteCurrency": 'quote_currency',
    'lotSize': 'lot_size',
    'tickSize': 'tick_size',
    'makerFee': 'maker_fee',
    'takerFee': 'taker_fee',

    'initMargin': 'init_margin_rate',
    'maintMargin': 'maint_margin_rate',

    'settlementFee': 'settlement_fee',
    'settlCurrency': 'settle_currency',

    'settle': 'settle_date',
    'front': 'front_date',
    'referenceSymbol': 'reference_symbol',
    'deleverage': 'deleverage'
}


class BitmexDataloader:
    instrument_cls: Dict[str, Type[Instrument]] = {
        'OPECCS': PutOptionInstrument,  # put options
        'OCECCS': CallOptionInstrument,  # call options
        'FFCCSX': FutureInstrument,  # normal futures contracts
        'FFWCSX': PerpetualInstrument,  # perpetual  futures contracts
        'FXXXS': FutureInstrument,
        'FFICSX': FutureInstrument,
        'FMXXS': FutureInstrument
    }

    # abandon typ in Bitmex
    # https://www.onixs.biz/fix-dictionary/4.4/app_6_d.html
    # below are all index like instrument
    _abandon_instrument_type = ('MRIXXX', 'MRRXXX', 'MRCXXX')

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.instruments: Dict[str, Instrument] = dict()
        self.trade_data: Dict = dict()
        self._kline_store = LazyHDFTableStore(os.path.join(data_dir, KLINE_FILE_NAME))

    def load_instruments(self, exchange: Optional['BitmexSimulateExchange']) -> None:
        logger.debug("Now loading the instruments data.")
        instruments_file = os.path.join(self.data_dir, INSTRUMENT_FILENAME)
        with open(instruments_file) as f:
            instruments_raw = json.load(f)
        for instrument_raw in instruments_raw:
            if instrument_raw['typ'] in self._abandon_instrument_type:
                continue
            instrument_cls = self.instrument_cls.get(instrument_raw['typ'])
            if instrument_cls is None:
                raise LoadDataError(_("Unsupport instrument type {}").format(instrument_raw['typ']))
            instrument = instrument_cls.create(instrument_map, instrument_raw, exchange)
            self.instruments[instrument.symbol] = instrument
        logger.debug("Now loading the instruments data.")

    def active_instruments(self, date_time: datetime.datetime) -> Dict[str, Instrument]:
        assert is_aware_datetime(date_time)
        active = {}
        for instrument in self.instruments.values():
            if instrument.expiry_date is None:
                active[instrument.symbol] = instrument
                continue
            if instrument.listing_date is None:
                continue
            if instrument.listing_date < date_time and instrument.expiry_date > date_time:
                active[instrument.symbol] = instrument
        return active

    def get_last_price(self, symbol: str, date_time: datetime.datetime) -> float:
        assert is_aware_datetime(date_time)
        kline = self._kline_store.get(symbol)
        time_target = make_datetime_exactly(date_time, "T", forward=False)
        try:
            bar = kline.loc[time_target]
            return bar['close']
        except KeyError:
            logger.warning(_("Instrument {} on {} has no bar data., Use 0 as last price"
                             .format(symbol, date_time)))
            return 0.0

    def get_kline(self, symbol: str, date_time: datetime.datetime,
                  count: int) -> pandas.DataFrame:
        assert is_aware_datetime(date_time)
        kline_frame = self._kline_store.get(symbol)
        target_klines = kline_dataframe_window(kline_frame, date_time, count)
        return target_klines

    def all_data(self, symbol: str) -> pandas.DataFrame:
        return self._kline_store.get(symbol)
